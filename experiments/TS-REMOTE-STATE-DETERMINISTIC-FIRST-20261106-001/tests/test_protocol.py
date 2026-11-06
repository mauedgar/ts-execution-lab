import copy
import json
import unittest

from ts_detstate.core import (
    Command, CommitUnknown, Rejected, apply_once, canonical, digest,
    reconcile_readonly, strict_loads,
)


def wire(i=1, mutation=None, expected=0, value=1, attempt=None):
    return {
        "kind": "SyntheticState",
        "operation_id": "R3-DET-OP-20261106-001",
        "attempt_id": attempt or f"R3-DET-ATTEMPT-{i:08d}",
        "mutation_id": mutation or f"R3-DET-MUTATION-{i:08d}",
        "state_id": "R3-DET-AGGREGATE-20261106-001",
        "expected_revision": expected,
        "authority_ref": "AUTH-SYNTHETIC-R3",
        "state": {"synthetic": True, "value": value},
    }


class FakeConn:
    """A transactional SQL-contract fixture, NOT a PostgreSQL isolation simulator."""
    autocommit = True

    def __init__(self, db=None):
        self.db = db if db is not None else {"receipts": {}, "aggregate": {}, "events": {}}
        self.pending = None
        self.ack_loss = None  # None, 'before', or 'after'
        self.fail_stage = None
        self.statements = []

    def cursor(self):
        return FakeCursor(self)


class FakeCursor:
    def __init__(self, conn):
        self.c = conn
        self._rows = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def fetchone(self):
        return self._rows.pop(0) if self._rows else None

    def fetchall(self):
        return self._rows[:]

    def execute(self, sql, params=None):
        self.c.statements.append(sql)
        self._rows = []
        if sql.startswith('BEGIN'):
            if self.c.pending is not None:
                raise Exception('nested transaction')
            self.c.pending = copy.deepcopy(self.c.db)
            return
        if sql == 'ROLLBACK':
            self.c.pending = None
            return
        if sql == 'COMMIT':
            if self.c.ack_loss == 'before':
                self.c.pending = None
                raise ConnectionError('simulated before COMMIT persisted')
            self.c.db.clear()
            self.c.db.update(self.c.pending)
            self.c.pending = None
            if self.c.ack_loss == 'after':
                raise ConnectionError('simulated ack loss AFTER persisted COMMIT')
            return
        if self.c.pending is None:
            raise Exception('no transaction')
        if self.c.fail_stage and self.c.fail_stage in sql:
            raise ConnectionError('synthetic precommit failure')
        store = self.c.pending
        if sql.startswith('INSERT INTO') and '.receipts' in sql:
            mutation, fingerprint, rev, raw = params
            if mutation not in store['receipts']:
                store['receipts'][mutation] = {'mutation_id': mutation,
                    'command_fingerprint': fingerprint, 'original_revision': rev,
                    'result': json.loads(raw)}
                self._rows = [{'mutation_id': mutation}]
        elif sql.startswith('SELECT') and '.receipts' in sql:
            row = store['receipts'].get(params[0])
            self._rows = [copy.deepcopy(row)] if row else []
        elif sql.startswith('SELECT') and '.aggregate_state' in sql:
            row = store['aggregate'].get(params[0])
            self._rows = [copy.deepcopy(row)] if row else []
        elif sql.startswith('SELECT') and '.events' in sql:
            rows = [copy.deepcopy(r) for r in store['events'].values() if r['id'] == params[0]]
            self._rows = sorted(rows, key=lambda x: x['sequence'])[:1001]
        elif sql.startswith('INSERT INTO') and '.aggregate_state' in sql:
            state_id, rev, st, event_hash = params
            if state_id in store['aggregate']:
                raise Exception('PK conflict')
            store['aggregate'][state_id] = {'revision': rev, 'state': json.loads(st),
                'last_event_sha256': event_hash}
        elif sql.startswith('UPDATE') and '.aggregate_state' in sql:
            rev, st, event_hash, state_id, old_rev = params
            row = store['aggregate'].get(state_id)
            if row and row['revision'] == old_rev:
                row.update(revision=rev, state=json.loads(st), last_event_sha256=event_hash)
                self._rows = [{'revision': rev}]
        elif sql.startswith('INSERT INTO') and '.events' in sql:
            event_id, state_id, seq, prev, event_hash, payload = params
            if event_id in store['events']:
                raise Exception('PK conflict')
            store['events'][event_id] = dict(event_id=event_id, id=state_id,
                sequence=seq, previous_hash=prev, event_hash=event_hash,
                payload=json.loads(payload))
        elif sql.startswith('UPDATE') and '.receipts' in sql:
            raw, mutation, fingerprint = params
            row = store['receipts'].get(mutation)
            if row and row['command_fingerprint'] == fingerprint:
                row['result'] = json.loads(raw)
                self._rows = [{'mutation_id': mutation}]
        else:
            raise AssertionError(f'Unexpected SQL: {sql[:90]}')


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.db = {'receipts': {}, 'aggregate': {}, 'events': {}}
        self.conn = FakeConn(self.db)
        self.a = Command.from_dict(wire())

    def test_direct_unvalidated_constructor_forbidden(self):
        with self.assertRaises(TypeError):
            Command(**{k: wire()[k] for k in ('operation_id', 'attempt_id',
                            'mutation_id', 'state_id', 'expected_revision', 'state')})

    def test_cannot_mutate_validated_snapshot(self):
        raw = wire()
        cmd = Command.from_dict(raw)
        fingerprint = cmd.fingerprint()
        raw['state']['value'] = 999
        cmd.state['value'] = 999
        self.assertEqual(cmd.fingerprint(), fingerprint)
        self.assertEqual(cmd.state['value'], 1)

    def test_unvalidated_object_rejected_before_begin(self):
        bad = object.__new__(Command)
        with self.assertRaisesRegex(Rejected, 'COMMAND_NOT_VALIDATED'):
            apply_once(self.conn, bad)
        self.assertEqual(self.conn.statements, [])

    def test_tampered_authority_even_with_rehashed_chain_rejected(self):
        apply_once(self.conn, self.a)
        event = self.db['events'][self.a.event_id()]
        event['payload']['authority_ref'] = 'UNTRUSTED-SYNTHETIC'
        event['event_hash'] = digest(event['payload'])
        self.db['aggregate'][self.a.state_id]['last_event_sha256'] = event['event_hash']
        with self.assertRaisesRegex(Rejected, 'CHAIN_HASH_MISMATCH'):
            reconcile_readonly(FakeConn(self.db), self.a)

    def test_genesis_one_receipt_one_event(self):
        out = apply_once(self.conn, self.a)
        self.assertEqual((out['disposition'], out['effect'], out['revision']), ('COMMITTED', 'CONFIRMED', 1))
        self.assertEqual(tuple(len(self.db[x]) for x in ('aggregate', 'events', 'receipts')), (1, 1, 1))
        self.assertEqual(self.db['receipts'][self.a.mutation_id]['result']['event_hash'], out['event_hash'])

    def test_exact_replay_no_second_effect(self):
        apply_once(self.conn, self.a)
        result = apply_once(self.conn, self.a)
        self.assertEqual(result['disposition'], 'RECONCILED')
        self.assertEqual(tuple(len(self.db[x]) for x in ('aggregate', 'events', 'receipts')), (1, 1, 1))

    def test_changed_payload_same_mutation_is_collision(self):
        apply_once(self.conn, self.a)
        modified = Command.from_dict(wire(value=99))
        with self.assertRaisesRegex(Rejected, 'MUTATION_IDENTITY_COLLISION'):
            apply_once(self.conn, modified)
        self.assertEqual(len(self.db['receipts']), 1)

    def test_changed_authority_rejected_at_parser(self):
        raw = wire(); raw['authority_ref'] = 'AUTH-UNRELATED'
        with self.assertRaisesRegex(Rejected, 'NON_SYNTHETIC'):
            Command.from_dict(raw)

    def test_changed_attempt_same_mutation_is_collision(self):
        apply_once(self.conn, self.a)
        changed = Command.from_dict(wire(attempt='R3-DET-ATTEMPT-CHANGED-2026'))
        with self.assertRaisesRegex(Rejected, 'MUTATION_IDENTITY_COLLISION'):
            reconcile_readonly(FakeConn(self.db), changed)

    def test_stale_revision_cannot_commit(self):
        apply_once(self.conn, self.a)
        stale = Command.from_dict(wire(2, expected=0))
        with self.assertRaisesRegex(Rejected, 'STALE_REVISION'):
            apply_once(self.conn, stale)
        self.assertEqual(len(self.db['receipts']), 1)

    def test_second_revision_and_replay_first(self):
        first = apply_once(self.conn, self.a)
        second_cmd = Command.from_dict(wire(2, expected=1, value=2))
        second = apply_once(self.conn, second_cmd)
        self.assertEqual(second['revision'], 2)
        self.assertEqual(self.db['events'][second_cmd.event_id()]['previous_hash'], first['event_hash'])
        self.assertEqual(reconcile_readonly(FakeConn(self.db), self.a)['revision'], 1)
        self.assertEqual(apply_once(self.conn, self.a)['revision'], 1)
        self.assertEqual(len(self.db['events']), 2)

    def test_readonly_missing_receipt_unknown_no_insert(self):
        out = reconcile_readonly(FakeConn(self.db), self.a)
        self.assertEqual((out['effect'], out['retry_authorized']), ('UNKNOWN', False))
        self.assertEqual(len(self.db['receipts']), 0)

    def test_readonly_existing_receipt(self):
        apply_once(self.conn, self.a)
        reader = FakeConn(self.db)
        out = reconcile_readonly(reader, self.a)
        self.assertEqual(out['effect'], 'CONFIRMED')
        self.assertTrue(all(not s.startswith(('INSERT', 'UPDATE', 'DELETE', 'SELECT FOR UPDATE')) for s in reader.statements))
        self.assertIn('BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY', reader.statements)

    def test_commit_ack_lost_after_persist(self):
        self.conn.ack_loss = 'after'
        with self.assertRaises(CommitUnknown) as raised:
            apply_once(self.conn, self.a)
        self.assertFalse(raised.exception.retry_authorized)
        self.assertEqual(len(self.db['receipts']), 1)
        out = reconcile_readonly(FakeConn(self.db), self.a)
        self.assertEqual(out['effect'], 'CONFIRMED')

    def test_commit_lost_before_persist_is_unknown_not_retry(self):
        self.conn.ack_loss = 'before'
        with self.assertRaises(CommitUnknown):
            apply_once(self.conn, self.a)
        self.assertEqual(len(self.db['receipts']), 0)
        out = reconcile_readonly(FakeConn(self.db), self.a)
        self.assertEqual((out['effect'], out['retry_authorized']), ('UNKNOWN', False))

    def test_precommit_error_rollback(self):
        self.conn.fail_stage = '.events'
        with self.assertRaisesRegex(Rejected, 'PRECOMMIT_FAILED_RECONCILE_FIRST'):
            apply_once(self.conn, self.a)
        self.assertEqual(tuple(len(self.db[x]) for x in ('aggregate', 'events', 'receipts')), (0, 0, 0))

    def test_missing_aggregate_is_detected(self):
        apply_once(self.conn, self.a)
        self.db['aggregate'].clear()
        with self.assertRaises(Rejected):
            reconcile_readonly(FakeConn(self.db), self.a)

    def test_tampered_event_hash_detected(self):
        apply_once(self.conn, self.a)
        self.db['events'][self.a.event_id()]['event_hash'] = '0' * 64
        with self.assertRaisesRegex(Rejected, 'CHAIN_HASH_MISMATCH'):
            reconcile_readonly(FakeConn(self.db), self.a)

    def test_no_autocommit_fail_closed(self):
        self.conn.autocommit = False
        with self.assertRaisesRegex(Rejected, 'AUTOCOMMIT_REQUIRED'):
            apply_once(self.conn, self.a)
        self.assertEqual(self.conn.statements, [])

    def test_sql_has_only_static_identifiers_and_bind_params(self):
        apply_once(self.conn, self.a)
        sql = '\n'.join(self.conn.statements)
        self.assertIn('ts_r3_synthetic_20261105_001.', sql)
        self.assertIn('%s', sql)
        self.assertNotIn(self.a.mutation_id, sql)
        self.assertNotIn(self.a.state_id, sql)


class ValidationTests(unittest.TestCase):
    def test_canonical_order_and_digest(self):
        a, b = {'b': 2, 'a': [True, None]}, {'a': [True, None], 'b': 2}
        self.assertEqual(canonical(a), canonical(b))
        self.assertEqual(digest(a), digest(b))

    def test_reject_float(self):
        with self.assertRaisesRegex(Rejected, 'JSON_FLOAT_FORBIDDEN'):
            strict_loads('{"v":1.1}')

    def test_reject_duplicate_object_keys(self):
        with self.assertRaisesRegex(Rejected, 'JSON_DUPLICATE_KEY'):
            strict_loads('{"v":1,"v":2}')

    def test_reject_nan(self):
        with self.assertRaisesRegex(Rejected, 'JSON_NONFINITE_FORBIDDEN'):
            strict_loads('{"v":NaN}')

    def test_reject_unicode_non_nfc(self):
        with self.assertRaisesRegex(Rejected, 'JSON_UNSAFE_TEXT'):
            canonical({'x':'e\u0301'})

    def test_reject_exotic_json_values(self):
        with self.assertRaisesRegex(Rejected, 'JSON_UNSUPPORTED_TYPE'):
            canonical({'x': {1,2}})

    def test_reject_overly_deep(self):
        v = 0
        for _ in range(20):
            v = [v]
        with self.assertRaisesRegex(Rejected, 'JSON_DEPTH'):
            canonical(v)

    def test_reject_out_of_bounds_int(self):
        with self.assertRaisesRegex(Rejected, 'JSON_INTEGER_RANGE'):
            canonical({'x': 2**60})

    def test_reject_extra_command_fields(self):
        raw = wire(); raw['ignored'] = 2
        with self.assertRaisesRegex(Rejected, 'COMMAND_SHAPE'):
            Command.from_dict(raw)

    def test_reject_product_like_id(self):
        raw = wire(); raw['state_id'] = 'TASKCYCLE-REAL-001'
        with self.assertRaisesRegex(Rejected, 'COMMAND_IDENTITY'):
            Command.from_dict(raw)

    def test_reject_expected_revision_bool(self):
        raw = wire(); raw['expected_revision'] = True
        with self.assertRaisesRegex(Rejected, 'EXPECTED_REVISION'):
            Command.from_dict(raw)

    def test_reject_non_synthetic_state(self):
        raw = wire(); raw['state']['synthetic'] = False
        with self.assertRaisesRegex(Rejected, 'NON_SYNTHETIC_STATE'):
            Command.from_dict(raw)


if __name__ == '__main__':
    unittest.main()
