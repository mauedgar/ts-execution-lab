"""Offline exhaustive source tests: NEVER invokes live Neon or imports psycopg.

The FakeConn simulates atomic commit/rollback and a lost terminal ACK. PostgreSQL
native isolation, credential custody and lost network packet require separate gates.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import base64
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from ts_global.bridge import (EffectUnknown, Mutation, StorageRejected, apply,
                              initialize, read, reconcile, _preflight_mutation)

GOLDEN = json.loads((Path(__file__).parent.parent / "oracle" / "golden.json").read_text(encoding="utf8"))


def mutation(i):
    item = GOLDEN["mutations"][i]
    return Mutation(GOLDEN["scope"], item["mutation_id"], item["expected_revision"],
                    item["previous_event_hash"],base64.b64decode(item["payload_b64"]),
                    base64.b64decode(item["line_b64"]),base64.b64decode(item["state_b64"]),
                    item["authority_fingerprint"])


def genesis():
    return base64.b64decode(GOLDEN["genesis_b64"])


class FakeConn:
    autocommit = True

    def __init__(self):
        self.info = SimpleNamespace(transaction_status=SimpleNamespace(name="IDLE"))
        self.heads = {}
        self.events = {}
        self.receipts = {}
        self.queries = 0
        self.statements = []
        self.failpoint = None
        self._transaction = False

    @contextmanager
    def transaction(self):
        assert not self._transaction
        self._transaction = True
        pre = deepcopy((self.heads, self.events, self.receipts))
        try:
            yield self
        except Exception:
            self.heads, self.events, self.receipts = pre
            raise
        else:
            if self.failpoint == "before_commit":
                self.failpoint = None
                self.heads, self.events, self.receipts = pre
                raise ConnectionError("lost before DB commit")
            if self.failpoint == "after_commit_ack":
                self.failpoint = None
                raise ConnectionError("lost after DB commit ACK")
        finally:
            self._transaction = False

    @contextmanager
    def cursor(self):
        yield FakeCursor(self)


class FakeCursor:
    def __init__(self, db):
        self.db = db
        self.result = None

    def execute(self, sql, values=()):
        self.db.queries += 1
        self.db.statements.append(sql)
        self.result = None
        if sql == "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY":
            return
        if sql.startswith("SELECT revision,state_bytes,state_sha256,events_sha256,last_event_hash FROM"):
            scope = values[0]
            self.result = [deepcopy(self.db.heads[scope])] if scope in self.db.heads else []
        elif sql.startswith("SELECT revision,event_hash,previous_event_hash,payload_bytes,event_line FROM"):
            scope = values[0]
            self.result = [deepcopy(v) for (sc,_),v in sorted(self.db.events.items()) if sc == scope]
        elif sql.startswith("SELECT event_hash FROM"):
            scope,rev=values
            self.result = [{"event_hash":self.db.events[(scope,rev)]["event_hash"]}] if (scope,rev) in self.db.events else []
        elif sql.startswith("SELECT command_fingerprint,result_revision,event_hash FROM"):
            self.result = [deepcopy(self.db.receipts[(values[0], values[1])])] if (values[0], values[1]) in self.db.receipts else []
        elif sql.startswith("INSERT INTO") and ".head(" in sql:
            scope, state_bytes, state_hash, event_hash = values
            if scope not in self.db.heads:
                self.db.heads[scope] = dict(revision=0,state_bytes=state_bytes,state_sha256=state_hash,
                                            events_sha256=event_hash,last_event_hash=None)
                self.result = [{"revision":0}]
            else:
                self.result = []
        elif sql.startswith("UPDATE") and ".head SET" in sql:
            rev, state_bytes, state_hash, events_hash, event_hash, scope, expected_rev, prev = values
            row = self.db.heads[scope]
            if row["revision"] == expected_rev and row["last_event_hash"] == prev:
                row.update(revision=rev,state_bytes=state_bytes,state_sha256=state_hash,
                           events_sha256=events_hash,last_event_hash=event_hash)
                self.result = [{"revision":rev}]
            else: self.result = []
        elif sql.startswith("INSERT INTO") and ".events(" in sql:
            scope, revision, event_hash, prev, payload_bytes, line = values
            assert (scope,revision) not in self.db.events
            self.db.events[(scope,revision)] = dict(revision=revision,event_hash=event_hash,
                previous_event_hash=prev,payload_bytes=payload_bytes,event_line=line)
            self.result = []
        elif sql.startswith("INSERT INTO") and ".receipts(" in sql:
            scope, mid, fp, expected, revision, event_hash, auth = values
            assert (scope,mid) not in self.db.receipts
            self.db.receipts[(scope,mid)] = dict(command_fingerprint=fp,result_revision=revision,event_hash=event_hash)
            self.result = []
        else:
            raise AssertionError("unexpected SQL statement: " + sql)

    def fetchone(self):
        return self.result.pop(0) if self.result else None

    def fetchall(self):
        return self.result if self.result is not None else []


class GlobalBridgeTests(unittest.TestCase):
    def setUp(self):
        self.db = FakeConn()
        self.scope = GOLDEN["scope"]
        self.view = initialize(self.db, self.scope, genesis())

    def test_01_genesis_preserves_exact_js_bytes(self):
        self.assertEqual(self.view.revision,0)
        self.assertEqual(self.view.state_bytes,genesis())
        self.assertEqual(self.view.event_bytes,b"")
        self.assertEqual(self.view.events_sha256,sha256(b"").hexdigest())

    def test_02_genesis_repeated_fails_no_mutation(self):
        before=deepcopy(self.db.heads)
        with self.assertRaisesRegex(StorageRejected,"ALREADY_INITIALIZED"):
            initialize(self.db,self.scope,genesis())
        self.assertEqual(before,self.db.heads)

    def test_03_four_kind_and_unknown_replay_byte_identical(self):
        events=[]
        for i in range(len(GOLDEN["mutations"])):
            m=mutation(i)
            rec=apply(self.db,m)
            self.assertEqual((rec.disposition,rec.revision,rec.replay),("CONFIRMED",i+1,False))
            events.append(m.event_line)
            view=read(self.db,self.scope)
            self.assertEqual(view.revision,i+1)
            self.assertEqual(view.event_bytes,b"".join(events))
            self.assertEqual(view.state_bytes,m.state_bytes)
        s=json.loads(view.state_bytes)
        self.assertEqual({k:len(v) for k,v in s["aggregates"].items()},
                         {"Milestone":1,"TaskCycle":2,"Operation":1,"ExecutionAttempt":1})
        self.assertEqual(s["aggregates"]["TaskCycle"]["TC-SYNTHETIC"]["state"],"CLOSED")
        self.assertEqual(s["aggregates"]["TaskCycle"]["TC-SYNTHETIC-IMPORTED"]["state"],"READY")
        self.assertEqual(s["aggregates"]["ExecutionAttempt"]["AT-SYNTHETIC"]["state"],"FAILED")
        self.assertFalse(s["aggregates"]["ExecutionAttempt"]["AT-SYNTHETIC"]["reconciliation_required"])

    def test_04_replay_is_read_only(self):
        m=mutation(0)
        apply(self.db,m)
        before=(deepcopy(self.db.heads),deepcopy(self.db.events),deepcopy(self.db.receipts))
        result=apply(self.db,m)
        self.assertEqual((result.disposition,result.replay),('CONFIRMED',True))
        self.assertEqual(before,(self.db.heads,self.db.events,self.db.receipts))

    def test_05_stale_revision_fenced(self):
        apply(self.db,mutation(0))
        m=replace(mutation(0),mutation_id="MUT-STALE-DIFFERENT")
        before=(deepcopy(self.db.heads),deepcopy(self.db.events),deepcopy(self.db.receipts))
        with self.assertRaisesRegex(StorageRejected,"STALE_REVISION"):
            apply(self.db,m)
        self.assertEqual(before,(self.db.heads,self.db.events,self.db.receipts))

    def test_06_mutation_collision_fails_closed(self):
        m=mutation(0)
        apply(self.db,m)
        with self.assertRaisesRegex(StorageRejected,"MUTATION_COLLISION"):
            apply(self.db,replace(m,authority_fingerprint="c"*64))

    def test_07_commit_ack_lost_after_persist_read_only_reconcile(self):
        m=mutation(0)
        self.db.failpoint="after_commit_ack"
        with self.assertRaises(EffectUnknown):
            apply(self.db,m)
        self.assertEqual(read(self.db,self.scope).revision,1)
        result=reconcile(self.db,m)
        self.assertEqual((result.disposition,result.replay),('CONFIRMED',True))

    def test_08_commit_ack_lost_before_commit_unknown_no_retry(self):
        m=mutation(0)
        self.db.failpoint="before_commit"
        with self.assertRaises(EffectUnknown):
            apply(self.db,m)
        self.assertEqual(read(self.db,self.scope).revision,0)
        with self.assertRaises(EffectUnknown):
            reconcile(self.db,m)

    def test_09_rollback_on_receipt_insert_failure(self):
        m=mutation(0)
        # Monkey patch cursor to fail only after head & event writes.
        real=self.db.cursor
        @contextmanager
        def broken():
            with real() as c:
                execute=c.execute
                def fail_on_receipt(sql, params=()):
                    if '.receipts(' in sql:
                        raise ValueError('injected constraint')
                    return execute(sql,params)
                c.execute=fail_on_receipt
                yield c
        self.db.cursor=broken
        with self.assertRaises(EffectUnknown):
            apply(self.db,m)
        self.db.cursor=real
        self.assertEqual(read(self.db,self.scope).revision,0)
        self.assertEqual(self.db.events,{})
        self.assertEqual(self.db.receipts,{})

    def test_10_tamper_snapshot_hash_denied(self):
        apply(self.db,mutation(0))
        self.db.heads[self.scope]["state_bytes"]=b'{}'
        with self.assertRaisesRegex(StorageRejected,"SNAPSHOT_TAMPERED"):
            read(self.db,self.scope)

    def test_11_tamper_event_bytes_denied(self):
        apply(self.db,mutation(0))
        self.db.events[(self.scope,1)]["payload_bytes"]+=b' '
        with self.assertRaisesRegex(StorageRejected,"PAYLOAD_FRAMING"):
            read(self.db,self.scope)

    def test_12_tamper_chain_head_denied(self):
        apply(self.db,mutation(0))
        self.db.heads[self.scope]["last_event_hash"]='f'*64
        with self.assertRaisesRegex(StorageRejected,"HEAD_EVENT_MISMATCH"):
            read(self.db,self.scope)

    def test_13_tamper_stream_digest_denied(self):
        apply(self.db,mutation(0))
        self.db.heads[self.scope]["events_sha256"]='e'*64
        with self.assertRaisesRegex(StorageRejected,"EVENT_STREAM_TAMPERED"):
            read(self.db,self.scope)

    def test_14_tamper_event_count_denied(self):
        apply(self.db,mutation(0))
        self.db.events.clear()
        with self.assertRaisesRegex(StorageRejected,"EVENT_COUNT_MISMATCH"):
            read(self.db,self.scope)

    def test_15_unsafe_json_integer_preflight_no_sql(self):
        m=mutation(0)
        p=m.payload_bytes.replace(b'"sequence":1',b'"sequence":9007199254740992')
        before=self.db.queries
        with self.assertRaises(StorageRejected):
            apply(self.db,replace(m,payload_bytes=p))
        self.assertEqual(before,self.db.queries)

    def test_16_invalid_utf8_preflight_no_sql(self):
        m=mutation(0)
        before=self.db.queries
        with self.assertRaisesRegex(StorageRejected,"INVALID_JSON"):
            apply(self.db,replace(m,payload_bytes=b'\xff'))
        self.assertEqual(before,self.db.queries)

    def test_17_event_line_hash_forgery_rejected(self):
        m=mutation(0)
        x=m.event_line.replace(m.event_line[-66:-2],b'f'*64)
        with self.assertRaises(StorageRejected):
            apply(self.db,replace(m,event_line=x))

    def test_18_state_or_event_substitution_rejected(self):
        m=mutation(0)
        alt=mutation(1)
        with self.assertRaises(StorageRejected):
            apply(self.db,replace(m,state_bytes=alt.state_bytes))

    def test_19_strict_dict_row_required(self):
        self.db.heads[self.scope]['extra']=123
        with self.assertRaisesRegex(StorageRejected,'DB_ROW_INVALID'):
            read(self.db,self.scope)

    def test_20_autocommit_guard(self):
        self.db.autocommit=False
        with self.assertRaisesRegex(StorageRejected,'AUTOCOMMIT_TRUE_REQUIRED'):
            read(self.db,self.scope)

    def test_21_reconcile_wrong_fingerprint_rejected(self):
        m=mutation(0)
        apply(self.db,m)
        with self.assertRaisesRegex(StorageRejected,'RECEIPT_INCONSISTENT'):
            reconcile(self.db,replace(m,authority_fingerprint='f'*64))

    def test_22_empty_receipt_after_stale_effect_stays_unknown(self):
        m=mutation(0)
        apply(self.db,m)
        m2=mutation(1)
        with self.assertRaises(EffectUnknown):
            reconcile(self.db,m2)

    def test_23_read_does_not_modify_database(self):
        apply(self.db,mutation(0))
        before=deepcopy((self.db.heads,self.db.events,self.db.receipts))
        self.assertEqual(read(self.db,self.scope).revision,1)
        self.assertEqual(before,(self.db.heads,self.db.events,self.db.receipts))

    def test_24_genesis_commit_unknown_reconciled_by_read(self):
        db=FakeConn()
        db.failpoint="after_commit_ack"
        with self.assertRaises(EffectUnknown):
            initialize(db,self.scope,genesis())
        self.assertEqual(read(db,self.scope).revision,0)

    def test_25_same_mutation_across_scopes_not_colliding(self):
        m=mutation(0)
        apply(self.db,m)
        other="scope-other-20261107"
        initialize(self.db,other,genesis())
        self.assertEqual(apply(self.db,replace(m,scope=other)).revision,1)

    def test_26_original_payload_sha_matches_js_golden(self):
        for idx,x in enumerate(GOLDEN['mutations']):
            self.assertEqual(sha256(mutation(idx).payload_bytes).hexdigest(),x['event_hash'])

    def test_27_malformed_doubled_newline_rejected(self):
        m=mutation(0)
        with self.assertRaisesRegex(StorageRejected,'EVENT_LINE_FRAMING'):
            apply(self.db,replace(m,event_line=m.event_line+b'\n'))

    def test_28_no_implicit_db_schema_changes(self):
        for i in range(3):
            apply(self.db,mutation(i))
        self.assertFalse(any('CREATE ' in q or 'DROP ' in q or 'ALTER ' in q
                             for q in self.db.statements))


if __name__ == '__main__':
    unittest.main()
