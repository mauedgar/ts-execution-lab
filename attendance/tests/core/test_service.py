import concurrent.futures
import json
from contextlib import closing
import sqlite3
import multiprocessing
from pathlib import Path
import tempfile
import unittest

from attendance.core.service import AttendanceError, AttendanceService

T0 = '2026-11-01T10:00:00Z'
T1 = '2026-11-01T11:00:00Z'
T2 = '2026-11-01T12:00:00Z'
T3 = '2026-11-01T13:00:00Z'


def concurrent_checkin(db, instant, gate):
    service = AttendanceService(db)
    gate.wait()
    try:
        service.checkIn({'subject_id':'s1','occurred_at':instant})
        return 'PASS'
    except AttendanceError as e:
        return e.code


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / 'attendance.sqlite')
        self.s = AttendanceService(self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def inp(self, t=T0, **kw):
        return {'subject_id':'s1', 'occurred_at':t, **kw}

    def must_fail(self, code, func, payload):
        with self.assertRaises(AttendanceError) as cm:
            func(payload)
        self.assertEqual(cm.exception.code, code)

    def test_transitions_and_successive_intervals(self):
        self.must_fail('NO_OPEN_SESSION', self.s.checkOut, self.inp())
        a = self.s.checkIn(self.inp())
        self.assertTrue(self.s.getState({'subject_id':'s1'})['active'])
        self.must_fail('ALREADY_OPEN', self.s.checkIn, self.inp(T1))
        self.must_fail('NON_MONOTONIC_TIME', self.s.checkOut, self.inp(T0))
        x = self.s.checkOut(self.inp(T1))
        self.assertEqual(a['session_id'],x['session_id'])
        self.must_fail('NO_OPEN_SESSION', self.s.checkOut, self.inp(T2))
        self.must_fail('NON_MONOTONIC_TIME', self.s.checkIn, self.inp(T1))
        b = self.s.checkIn(self.inp(T2))
        self.assertNotEqual(a['session_id'],b['session_id'])
        self.s.checkOut(self.inp(T3))
        ls = self.s.listSessions({'subject_id':'s1','from':T0,'to':'2026-11-02T00:00:00Z'})
        self.assertEqual([a['session_id'],b['session_id']], [v['session_id'] for v in ls])
        self.assertFalse(self.s.getState({'subject_id':'s1'})['active'])
        self.assertEqual([a['session_id']], [v['session_id'] for v in self.s.listSessions({'subject_id':'s1','from':T0,'to':T2})])

    def test_idempotency_and_request_conflict_across_restart(self):
        original = self.s.checkIn(self.inp(request_id='req1'))
        self.assertEqual(original, self.s.checkIn(self.inp(request_id='req1')))
        self.must_fail('REQUEST_CONFLICT', self.s.checkIn, self.inp(T1, request_id='req1'))
        self.must_fail('REQUEST_CONFLICT', self.s.checkOut, self.inp(request_id='req1'))
        done = self.s.checkOut(self.inp(T1, request_id='req2'))
        other = AttendanceService(self.db)
        self.assertEqual(done, other.checkOut(self.inp(T1, request_id='req2')))
        self.assertEqual(original, other.checkIn(self.inp(request_id='req1')))
        self.assertFalse(other.getState({'subject_id':'s1'})['active'])
        self.assertEqual(len(other.listSessions({'subject_id':'s1','from':T0,'to':T3})),1)

    def test_validation_unknown_and_boundaries(self):
        self.must_fail('NOT_FOUND', self.s.getState, {'subject_id':'missing'})
        self.must_fail('NOT_FOUND', self.s.listSessions, {'subject_id':'missing','from':T0,'to':T2})
        self.must_fail('INVALID_ARGUMENT', self.s.checkIn, self.inp('2026-11-01T10:00:00'))
        self.must_fail('INVALID_ARGUMENT', self.s.checkIn, self.inp('2026-13-01T10:00:00Z'))
        self.must_fail('INVALID_ARGUMENT', self.s.checkIn, self.inp(subject_id='s 1'))
        self.must_fail('INVALID_ARGUMENT', self.s.checkIn, self.inp(request_id='?'))
        self.must_fail('INVALID_ARGUMENT', self.s.listSessions, {'subject_id':'s1','from':T2,'to':T0})
        self.must_fail('INVALID_ARGUMENT', self.s.checkIn, {'subject_id':'s1','occurred_at':T0,'other':3})
        self.s.checkIn({'subject_id':'s1','occurred_at':'2026-11-01T12:00:00+02:00'})
        self.assertEqual(self.s.getState({'subject_id':'s1'})['active_session']['checked_in_at'], '2026-11-01T10:00:00.000000Z')

    def test_rfc3339_unrestricted_fraction_and_lowercase_rfc3339(self):
        raw = '2026-11-02t10:00:00.1234567000001z'
        opened = self.s.checkIn(self.inp(raw))
        self.assertEqual(opened['checked_in_at'], '2026-11-02T10:00:00.1234567000001Z')
        # Strictly greater time at far more than six decimal places.
        after = '2026-11-02T10:00:00.1234567000002Z'
        closed = self.s.checkOut(self.inp(after))
        self.assertEqual(closed['checked_out_at'], after)
        self.assertEqual([opened['session_id']], [s['session_id'] for s in
                         self.s.listSessions({'subject_id':'s1',
                            'from':'2026-11-02T10:00:00.1234567000000Z',
                            'to':'2026-11-02T10:00:00.1234567000002Z'})])

    def test_fraction_boundary_order_exact_query_edges(self):
        a = self.s.checkIn(self.inp('2026-11-01T10:00:00.123456Z'))
        self.s.checkOut(self.inp('2026-11-01T10:00:00.1234567Z'))
        self.s.checkIn(self.inp('2026-11-01T10:00:00.12345671Z'))
        self.assertEqual(len(self.s.listSessions({'subject_id': 's1',
                       'from': '2026-11-01T10:00:00.123456Z',
                       'to': '2026-11-01T10:00:00.12345671Z'})), 1)
        self.assertEqual(self.s.getState({'subject_id':'s1'})['active_session']['session_id'] != a['session_id'], True)

    def test_overflow_is_typed_invalid_argument(self):
        for ts in ('0001-01-01T00:00:00+01:00',
                   '9999-12-31T23:59:59-01:00'):
            with self.subTest(ts=ts):
                self.must_fail('INVALID_ARGUMENT', self.s.checkIn, self.inp(ts))
        self.must_fail('NOT_FOUND', self.s.getState, {'subject_id':'s1'})

    def test_request_id_compares_literal_original_arguments(self):
        opened = self.s.checkIn(self.inp('2026-11-01T10:00:00Z',request_id='same'))
        self.assertEqual(opened,self.s.checkIn(self.inp('2026-11-01T10:00:00Z',request_id='same')))
        # A distinct textual timestamp is not identical caller arguments.
        self.must_fail('REQUEST_CONFLICT', self.s.checkIn,
                       self.inp('2026-11-01T12:00:00+02:00',request_id='same'))
        self.must_fail('REQUEST_CONFLICT', self.s.checkIn,
                       self.inp('2026-11-01t10:00:00z',request_id='same'))

    def test_future_schema_version_fail_closed_preserve_original(self):
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('PRAGMA user_version=999')
            conn.commit()
        with self.assertRaises(AttendanceError) as cm:
            AttendanceService(self.db)
        self.assertEqual(cm.exception.code,'STORAGE_ERROR')
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute('PRAGMA user_version').fetchone()[0],999)

    def test_old_database_version_migrates_without_losing_records(self):
        self.s.checkIn(self.inp())
        self.s.checkOut(self.inp(T1))
        with closing(sqlite3.connect(self.db)) as conn:
            # v1 used .000000Z, so construct its actual legacy representation.
            conn.execute('UPDATE sessions SET checked_in_at="2026-11-01T10:00:00.000000Z", checked_out_at="2026-11-01T11:00:00.000000Z"')
            conn.execute('PRAGMA user_version=1')
            conn.commit()
        restored = AttendanceService(self.db)
        data=restored.listSessions({'subject_id':'s1','from':T0,'to':T3})
        self.assertEqual(len(data),1)
        self.assertEqual(data[0]['checked_in_at'],'2026-11-01T10:00:00.000000Z')
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute('PRAGMA user_version').fetchone()[0],2)
        AttendanceService(self.db)  # repeat setup must not mutate anything

    def test_invalid_offset_minutes_hours_are_typed(self):
        for offset in ('+00:60','+01:99','-01:99','+24:00'):
            with self.subTest(offset=offset):
                self.must_fail('INVALID_ARGUMENT', self.s.checkIn,
                               self.inp('2026-11-01T10:00:00' + offset))

    def test_known_leap_second_utc_and_local_offset(self):
        s=self.s.checkIn(self.inp('2016-12-31T23:59:60Z'))
        self.assertEqual(s['checked_in_at'],'2016-12-31T23:59:60.000000Z')
        self.s.checkOut(self.inp('2017-01-01T00:00:00.0000001Z'))
        self.assertEqual(len(self.s.listSessions({'subject_id':'s1',
                          'from':'2016-12-31T23:59:59Z',
                          'to':'2017-01-01T00:00:00Z'})),1)
        other=AttendanceService(str(Path(self.tmp.name)/'another.sqlite'))
        v=other.checkIn({'subject_id':'x','occurred_at':'2017-01-01T00:59:60+01:00'})
        self.assertEqual(v['checked_in_at'],'2016-12-31T23:59:60.000000Z')
        self.must_fail('INVALID_ARGUMENT',other.checkIn,
                       {'subject_id':'y','occurred_at':'2017-12-31T23:59:60Z'})

    def test_migrate_genuine_v1_persisted_idempotency_signature(self):
        stamp='2026-11-01T10:00:00Z'
        original=self.s.checkIn(self.inp(stamp,request_id='legacy'))
        # Reconstruct actual v1 persisted signature and session timestamp.
        with closing(sqlite3.connect(self.db)) as conn:
            legacy_sig=json.dumps({'operation':'checkIn',
                        'occurred_at':'2026-11-01T10:00:00.000000Z'},sort_keys=True,separators=(',',':'))
            conn.execute('UPDATE requests SET payload=? WHERE request_id="legacy"',(legacy_sig,))
            conn.execute('UPDATE sessions SET checked_in_at="2026-11-01T10:00:00.000000Z"')
            conn.execute('PRAGMA user_version=1')
            conn.commit()
        migrated=AttendanceService(self.db)
        self.assertEqual(migrated.checkIn(self.inp(stamp,request_id='legacy')),original)
        # Legacy keys retain their canonical UTC replay semantics as v1 did.
        self.assertEqual(migrated.checkIn(self.inp('2026-11-01T12:00:00+02:00',request_id='legacy')),original)
        self.must_fail('REQUEST_CONFLICT',migrated.checkIn,self.inp(T1,request_id='legacy'))
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute('PRAGMA user_version').fetchone()[0],2)
            sig=json.loads(conn.execute('SELECT payload FROM requests WHERE request_id="legacy"').fetchone()[0])
            self.assertEqual(sig['signature_version'],1)
        # Newly issued v2 keys obey original *literal* payload identity.
        migrated.checkOut(self.inp(T1,request_id='new'))
        self.must_fail('REQUEST_CONFLICT',migrated.checkOut,
                       self.inp('2026-11-01T13:00:00+02:00',request_id='new'))

    def test_setup_idempotence_and_concurrent_connections(self):
        for _ in range(3):
            AttendanceService(self.db)
        with multiprocessing.Manager() as manager:
            gate = manager.Event()
            with concurrent.futures.ProcessPoolExecutor(max_workers=2) as ex:
                first = ex.submit(concurrent_checkin, self.db, T0, gate)
                second = ex.submit(concurrent_checkin, self.db, T0, gate)
                gate.set()
                answers = [first.result(timeout=25),second.result(timeout=25)]
        self.assertEqual(sorted(answers), ['ALREADY_OPEN','PASS'])
        self.assertEqual(len(self.s.listSessions({'subject_id':'s1','from':T0,'to':T3})),1)


if __name__ == '__main__':
    unittest.main()
