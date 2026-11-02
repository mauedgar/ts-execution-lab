import concurrent.futures
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
