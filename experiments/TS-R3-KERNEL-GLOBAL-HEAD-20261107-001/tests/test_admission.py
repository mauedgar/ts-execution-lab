"""Additional negative tests for exact admission and untrusted database rows."""
from __future__ import annotations
from dataclasses import replace
from copy import deepcopy
import json
import unittest
from test_bridge import FakeConn, GOLDEN, mutation, genesis
from ts_global.bridge import (EffectUnknown, StorageRejected, initialize, apply,
                              read, reconcile, _parse)


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.conn = FakeConn()
        self.scope = GOLDEN['scope']
        initialize(self.conn,self.scope,genesis())

    def test_01_non_idle_connection_denied_before_sql(self):
        self.conn.info.transaction_status.name='INTRANS'
        before=self.conn.queries
        with self.assertRaisesRegex(StorageRejected,'TRANSACTION_NOT_IDLE'):
            apply(self.conn,mutation(0))
        self.assertEqual(self.conn.queries,before)

    def test_02_invalid_autocommit_fails_before_mutate(self):
        self.conn.autocommit=False
        before=self.conn.queries
        with self.assertRaisesRegex(StorageRejected,'AUTOCOMMIT_TRUE_REQUIRED'):
            apply(self.conn,mutation(0))
        self.assertEqual(self.conn.queries,before)

    def test_03_wrong_state_revision_denied_before_sql(self):
        m=mutation(0)
        state=json.loads(m.state_bytes)
        state['revision']=42
        before=self.conn.queries
        with self.assertRaisesRegex(StorageRejected,'SNAPSHOT_REVISION_MISMATCH'):
            apply(self.conn,replace(m,state_bytes=json.dumps(state).encode()))
        self.assertEqual(before,self.conn.queries)

    def test_04_no_orphan_receipt_without_event(self):
        m=mutation(0)
        apply(self.conn,m)
        self.conn.events.clear()
        with self.assertRaisesRegex(StorageRejected,'EVENT_COUNT_MISMATCH'):
            apply(self.conn,m)

    def test_05_false_receipt_revision_detected(self):
        m=mutation(0)
        apply(self.conn,m)
        self.conn.receipts[(self.scope,m.mutation_id)]['result_revision']=2
        with self.assertRaisesRegex(StorageRejected,'RECEIPT_INCONSISTENT'):
            reconcile(self.conn,m)

    def test_06_receipt_hash_corrupted_detected(self):
        m=mutation(0)
        apply(self.conn,m)
        self.conn.receipts[(self.scope,m.mutation_id)]['event_hash']='a'*64
        with self.assertRaisesRegex(StorageRejected,'RECEIPT_INCONSISTENT'):
            reconcile(self.conn,m)

    def test_07_unsafe_json_float_denied(self):
        with self.assertRaisesRegex(StorageRejected,'UNSUPPORTED_JSON_FLOAT'):
            _parse(b'{"revision":1.5}')

    def test_08_exponent_overflow_denied(self):
        with self.assertRaisesRegex(StorageRejected,'UNSUPPORTED_JSON_FLOAT'):
            _parse(b'{"revision":1e999}')

    def test_09_duplicate_keys_denied(self):
        with self.assertRaisesRegex(StorageRejected,'DUPLICATE_JSON_KEY'):
            _parse(b'{"revision":1,"revision":2}')

    def test_10_payload_before_revision_bool_rejected(self):
        m=mutation(0)
        payload=json.loads(m.payload_bytes)
        payload['before_revision']=True
        prior=self.conn.queries
        with self.assertRaises(StorageRejected):
            apply(self.conn,replace(m,payload_bytes=json.dumps(payload).encode()))
        self.assertEqual(prior,self.conn.queries)

    def test_11_payload_after_rev_bool_rejected(self):
        m=mutation(0)
        payload=json.loads(m.payload_bytes)
        payload['after']['revision']=True
        prior=self.conn.queries
        with self.assertRaises(StorageRejected):
            apply(self.conn,replace(m,payload_bytes=json.dumps(payload).encode()))
        self.assertEqual(prior,self.conn.queries)

    def test_12_genesis_after_lost_ack_confirmed_without_reinitialize(self):
        conn=FakeConn()
        conn.failpoint='after_commit_ack'
        with self.assertRaises(EffectUnknown):
            initialize(conn,self.scope,genesis())
        self.assertEqual(read(conn,self.scope).revision,0)
        # The original attempt is terminal UNKNOWN; never call initialize again.

    def test_13_reconcile_is_readonly_and_handles_absence(self):
        m=mutation(0)
        initial=deepcopy((self.conn.heads,self.conn.events,self.conn.receipts))
        with self.assertRaises(EffectUnknown):
            reconcile(self.conn,m)
        self.assertEqual(initial,(self.conn.heads,self.conn.events,self.conn.receipts))

    def test_14_original_stream_preserved_even_when_json_object_order_differs(self):
        m=mutation(0)
        apply(self.conn,m)
        state=read(self.conn,self.scope)
        self.assertEqual(state.event_bytes,m.event_line)
        p=json.loads(m.payload_bytes)
        canonical=json.dumps(p,sort_keys=True,separators=(',',':')).encode()
        self.assertNotEqual(canonical,m.payload_bytes)

    def test_15a_event_line_with_equivalent_json_but_different_bytes_rejected(self):
        m=mutation(0)
        # Whitespace changes the line but not JSON parse. Product requires exact
        # JSON.stringify({...payload,hash}) bytes, not parse-equivalent JSON.
        equivalent=m.event_line.replace(b',"hash":"',b', "hash":"')
        before=self.conn.queries
        with self.assertRaisesRegex(StorageRejected,'EVENT_BYTES_MISMATCH'):
            apply(self.conn,replace(m,event_line=equivalent))
        self.assertEqual(before,self.conn.queries)

    def test_15b_tamper_event_line_storage_even_with_matching_stream_digest(self):
        from hashlib import sha256
        m=mutation(0)
        apply(self.conn,m)
        line=m.event_line.replace(b',"hash":"',b', "hash":"')
        self.conn.events[(self.scope,1)]['event_line']=line
        self.conn.heads[self.scope]['events_sha256']=sha256(line).hexdigest()
        with self.assertRaisesRegex(StorageRejected,'EVENT_BYTES_MISMATCH'):
            read(self.conn,self.scope)

    def test_15_read_only_snapshot_tamper_self_consistent_hash_cannot_forge_replay(self):
        m=mutation(0)
        apply(self.conn,m)
        self.conn.heads[self.scope]['state_bytes']=b'{"schema_version":"tecnotron-state-kernel/v0","revision":1,"aggregates":{"Milestone":{},"TaskCycle":{},"Operation":{},"ExecutionAttempt":{}}}'
        from hashlib import sha256
        self.conn.heads[self.scope]['state_sha256']=sha256(self.conn.heads[self.scope]['state_bytes']).hexdigest()
        with self.assertRaisesRegex(StorageRejected,'SNAPSHOT_REPLAY_MISMATCH'):
            read(self.conn,self.scope)


if __name__ == '__main__':
    unittest.main()
