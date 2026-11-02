import concurrent.futures
import json
from contextlib import closing
import sqlite3
import multiprocessing
import uuid
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

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
            conn.execute('DROP TABLE IF EXISTS v1_provenance')
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

    def test_migrate_reconstructed_v1_persisted_idempotency_signature(self):
        stamp='2026-11-01T10:00:00Z'
        original=self.s.checkIn(self.inp(stamp,request_id='legacy'))
        # Reconstruct actual v1 persisted signature and session timestamp.
        with closing(sqlite3.connect(self.db)) as conn:
            legacy_sig=json.dumps({'operation':'checkIn',
                        'occurred_at':'2026-11-01T10:00:00.000000Z'},sort_keys=True,separators=(',',':'))
            conn.execute('UPDATE requests SET payload=? WHERE request_id="legacy"',(legacy_sig,))
            conn.execute('UPDATE sessions SET checked_in_at="2026-11-01T10:00:00.000000Z"')
            conn.execute('DROP TABLE IF EXISTS v1_provenance')
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

    def test_invalid_sqlite_paths_report_typed_argument_errors(self):
        for path in ('bad\x00path.sqlite', 'bad\ud800path.sqlite', ':memory:', ''):
            with self.subTest(path=repr(path)):
                with self.assertRaises(AttendanceError) as caught:
                    AttendanceService(path)
                self.assertEqual(caught.exception.code, 'INVALID_ARGUMENT')

    def test_invalid_stored_request_response_fail_closed(self):
        self.s.checkIn(self.inp(request_id='abc'))
        for field in ('payload', 'response'):
            with self.subTest(field=field):
                with closing(sqlite3.connect(self.db)) as conn:
                    old = conn.execute('SELECT '+field+' FROM requests WHERE request_id=?', ('abc',)).fetchone()[0]
                    conn.execute('UPDATE requests SET '+field+'=? WHERE request_id=?', ('{broken-json', 'abc'))
                    conn.commit()
                try:
                    self.must_fail('STORAGE_ERROR', self.s.checkIn, self.inp(request_id='abc'))
                finally:
                    with closing(sqlite3.connect(self.db)) as conn:
                        conn.execute('UPDATE requests SET '+field+'=? WHERE request_id=?', (old, 'abc'))
                        conn.commit()

    def test_corrupt_legacy_request_rolls_back_entire_migration(self):
        self.s.checkIn(self.inp(request_id='aa'))
        self.s.checkOut(self.inp(T1, request_id='zz'))
        with closing(sqlite3.connect(self.db)) as conn:
            for request_id in ('aa','zz'):
                operation = 'checkIn' if request_id == 'aa' else 'checkOut'
                stamp = T0 if request_id == 'aa' else T1
                original = json.dumps({'operation':operation,'occurred_at':stamp.replace('Z','.000000Z')},
                                      sort_keys=True,separators=(',',':'))
                conn.execute('UPDATE requests SET payload=? WHERE request_id=?', (original,request_id))
            conn.execute('UPDATE requests SET payload=? WHERE request_id=?', ('{malformed', 'zz'))
            conn.execute('UPDATE sessions SET checked_in_at=?,checked_out_at=?',
                         ('2026-11-01T10:00:00.000000Z','2026-11-01T11:00:00.000000Z'))
            conn.execute('DROP TABLE IF EXISTS v1_provenance')
            conn.execute('PRAGMA user_version=1')
            conn.commit()
        self.must_fail('STORAGE_ERROR', lambda _: AttendanceService(self.db), None)
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute('PRAGMA user_version').fetchone()[0],1)
            self.assertEqual(conn.execute('SELECT checked_in_at FROM sessions').fetchone()[0],
                             '2026-11-01T10:00:00.000000Z')

    def test_leap_second_edges_and_offsets(self):
        self.must_fail('INVALID_ARGUMENT',self.s.checkIn,self.inp('2016-12-31T23:58:60Z'))
        self.must_fail('INVALID_ARGUMENT',self.s.checkIn,self.inp('2016-12-31T23:59:60+01:00'))
        self.must_fail('INVALID_ARGUMENT',self.s.checkIn,self.inp('2026-11-01T00:00:60Z'))
        self.s.checkIn(self.inp('2016-12-31T23:59:59.99999999Z'))
        self.s.checkOut(self.inp('2016-12-31T23:59:60Z'))
        self.s.checkIn(self.inp('2017-01-01T00:00:00Z'))
        records = self.s.listSessions({'subject_id':'s1',
                                      'from':'2016-12-31T23:59:59Z',
                                      'to':'2017-01-01T00:00:00.5Z'})
        self.assertEqual(len(records),2)
        self.assertLess(records[0]['checked_out_at'],records[1]['checked_in_at'])

    def test_legacy_migration_many_rows_uses_bounded_batches(self):
        with closing(sqlite3.connect(self.db)) as conn:
            for index in range(260):
                sid=f's{index:04d}'
                session=uuid.uuid4().hex
                conn.execute('INSERT INTO subjects(subject_id) VALUES(?)',(sid,))
                conn.execute('INSERT INTO sessions(session_id,subject_id,checked_in_at,checked_out_at) '
                             'VALUES(?,?,?,?)',(session,sid,'2026-11-01T10:00:00.000000Z','2026-11-01T11:00:00.000000Z'))
                response=json.dumps({'session_id':session,'subject_id':sid,
                    'checked_in_at':'2026-11-01T10:00:00.000000Z','checked_out_at':None})
                signature=json.dumps({'operation':'checkIn','occurred_at':'2026-11-01T10:00:00.000000Z'},
                                     sort_keys=True,separators=(',',':'))
                conn.execute('INSERT INTO requests(subject_id,request_id,operation,payload,response) '
                             'VALUES(?,?,?,?,?)',(sid,'req','checkIn',signature,response))
            conn.execute('DROP TABLE IF EXISTS v1_provenance')
            conn.execute('PRAGMA user_version=1')
            conn.commit()
        migrated=AttendanceService(self.db)
        self.assertEqual(len(migrated.listSessions({'subject_id':'s0259',
             'from':T0,'to':T3})),1)
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute('PRAGMA user_version').fetchone()[0],2)
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM sessions').fetchone()[0],260)
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM requests WHERE payload LIKE ?',
                            ('%signature_version%',)).fetchone()[0],260)

    def test_sqlite_trigger_fault_rolls_back_v1_migration(self):
        self.s.checkIn(self.inp())
        self.s.checkOut(self.inp(T1))
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('UPDATE sessions SET checked_in_at=?,checked_out_at=?',
                         ('2026-11-01T10:00:00.000000Z', '2026-11-01T11:00:00.000000Z'))
            conn.execute('CREATE TRIGGER fail_migration BEFORE UPDATE ON sessions '
                         "BEGIN SELECT RAISE(ABORT, 'synthetic disk transaction fault'); END")
            conn.execute('DROP TABLE IF EXISTS v1_provenance')
            conn.execute('PRAGMA user_version=1')
            conn.commit()
        with self.assertRaises(AttendanceError) as caught:
            AttendanceService(self.db)
        self.assertEqual(caught.exception.code, 'STORAGE_ERROR')
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute('PRAGMA user_version').fetchone()[0],1)
            self.assertEqual(conn.execute('SELECT checked_in_at FROM sessions').fetchone()[0],
                             '2026-11-01T10:00:00.000000Z')
            conn.execute('DROP TRIGGER fail_migration')
            conn.commit()
        self.assertEqual(len(AttendanceService(self.db).listSessions(
            {'subject_id':'s1','from':T0,'to':T3})),1)

    def test_long_fraction_no_silent_loss(self):
        digits='1234567890'*500
        opened=self.s.checkIn(self.inp('2026-11-01T10:00:00.'+digits+'Z'))
        self.assertEqual(opened['checked_in_at'],'2026-11-01T10:00:00.'+digits.rstrip('0')+'Z')
        self.s.checkOut(self.inp(T1))
        self.assertEqual(len(self.s.listSessions({'subject_id':'s1',
             'from':T0,'to':T2})),1)

    def test_v1_provenance_and_invalid_history_fail_closed(self):
        self.s.checkIn(self.inp(request_id='r'))
        with closing(sqlite3.connect(self.db)) as conn:
            session = conn.execute('SELECT session_id FROM sessions').fetchone()[0]
            signature=json.dumps({'operation':'checkIn','occurred_at':'2026-11-01T10:00:00.000000Z'},
                                 sort_keys=True,separators=(',',':'))
            response=json.dumps({'session_id':session,'subject_id':'s1',
                                 'checked_in_at':'2026-11-01T10:00:00.000000Z','checked_out_at':None})
            conn.execute('UPDATE requests SET payload=?,response=?,operation=? WHERE request_id=?',
                         (signature,response,'checkOut','r'))
            conn.execute('UPDATE sessions SET checked_in_at=?',
                         ('2026-11-01T10:00:00.000000Z',))
            conn.execute('DROP TABLE IF EXISTS v1_provenance')
            conn.execute('PRAGMA user_version=1')
            conn.commit()
        self.must_fail('STORAGE_ERROR',lambda _: AttendanceService(self.db),None)
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute('PRAGMA user_version').fetchone()[0],1)

    def test_v1_malformed_session_timestamp_fails_storage_error(self):
        self.s.checkIn(self.inp())
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('UPDATE sessions SET checked_in_at=?',('garbage-time',))
            conn.execute('DROP TABLE IF EXISTS v1_provenance')
            conn.execute('PRAGMA user_version=1')
            conn.commit()
        self.must_fail('STORAGE_ERROR',lambda _: AttendanceService(self.db),None)
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute('PRAGMA user_version').fetchone()[0],1)

    def test_v1_empty_session_id_must_not_be_skipped(self):
        self.s.checkIn(self.inp())
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('UPDATE sessions SET session_id=?,checked_in_at=?',
                         ('','2026-11-01T10:00:00.000000Z'))
            conn.execute('DROP TABLE IF EXISTS v1_provenance')
            conn.execute('PRAGMA user_version=1')
            conn.commit()
        self.must_fail('STORAGE_ERROR',lambda _: AttendanceService(self.db),None)

    def test_v1_response_type_shape_must_match_persisted_session(self):
        self.s.checkIn(self.inp(request_id='r'))
        with closing(sqlite3.connect(self.db)) as conn:
            signature=json.dumps({'operation':'checkIn','occurred_at':'2026-11-01T10:00:00.000000Z'},
                                 sort_keys=True,separators=(',',':'))
            conn.execute('UPDATE sessions SET checked_in_at=?',
                         ('2026-11-01T10:00:00.000000Z',))
            conn.execute('UPDATE requests SET payload=?,response=? WHERE request_id=?',
                         (signature, json.dumps({'session_id':None,'subject_id':'s1',
                          'checked_in_at':False,'checked_out_at':{}}),'r'))
            conn.execute('DROP TABLE IF EXISTS v1_provenance')
            conn.execute('PRAGMA user_version=1')
            conn.commit()
        self.must_fail('STORAGE_ERROR',lambda _: AttendanceService(self.db),None)

    def test_legacy_schema_must_retain_request_unique_constraint(self):
        self.s.checkIn(self.inp())
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('DROP TABLE requests')
            conn.execute('CREATE TABLE requests (subject_id TEXT, request_id TEXT, '
                         'operation TEXT, payload TEXT, response TEXT)')
            conn.execute('DROP TABLE IF EXISTS v1_provenance')
            conn.execute('PRAGMA user_version=1')
            conn.commit()
        self.must_fail('STORAGE_ERROR', lambda _: AttendanceService(self.db), None)

    def test_v1_overlap_rejected_atomically(self):
        self.s.checkIn(self.inp())
        self.s.checkOut(self.inp(T2))
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('UPDATE sessions SET checked_in_at=?,checked_out_at=?',
                         ('2026-11-01T10:00:00.000000Z','2026-11-01T12:00:00.000000Z'))
            conn.execute('INSERT INTO sessions(session_id,subject_id,checked_in_at,checked_out_at) '
                         'VALUES(?,?,?,?)',
                         (uuid.uuid4().hex,'s1','2026-11-01T11:00:00.000000Z',
                          '2026-11-01T13:00:00.000000Z'))
            conn.execute('DROP TABLE IF EXISTS v1_provenance')
            conn.execute('PRAGMA user_version=1')
            conn.commit()
        self.must_fail('STORAGE_ERROR',lambda _: AttendanceService(self.db),None)
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute('PRAGMA user_version').fetchone()[0],1)

    def test_v2_corrupt_valid_json_response_fail_closed(self):
        self.s.checkIn(self.inp(request_id='req1'))
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('UPDATE requests SET response=? WHERE request_id=?',
                         (json.dumps({'session_id':None,'subject_id':'s1',
                          'checked_in_at':False,'checked_out_at':{}}),'req1'))
            conn.commit()
        self.must_fail('STORAGE_ERROR',self.s.checkIn,self.inp(request_id='req1'))

    def test_v2_boolean_legacy_marker_does_not_grant_grandfather(self):
        self.s.checkIn(self.inp(request_id='req1'))
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('UPDATE requests SET payload=? WHERE request_id=?',
                         (json.dumps({'signature_version':True,'operation':'checkIn',
                         'utc_occurred_at':'2026-11-01T10:00:00'}),'req1'))
            conn.commit()
        self.must_fail('STORAGE_ERROR',self.s.checkIn,self.inp(request_id='req1'))

    def test_v1_orphan_subject_must_not_survive_migration(self):
        self.s.checkIn(self.inp())
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('INSERT INTO subjects(subject_id) VALUES(?)',('orphan',))
            conn.execute('UPDATE sessions SET checked_in_at=?',
                         ('2026-11-01T10:00:00.000000Z',))
            conn.execute('DROP TABLE IF EXISTS v1_provenance')
            conn.execute('PRAGMA user_version=1')
            conn.commit()
        self.must_fail('STORAGE_ERROR',lambda _: AttendanceService(self.db),None)

    def test_unversioned_existing_schema_must_not_be_adopted(self):
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('PRAGMA user_version=0')
            conn.commit()
        self.must_fail('STORAGE_ERROR',lambda _: AttendanceService(self.db),None)

    def test_sessions_many_rows_return_all_results(self):
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('INSERT INTO subjects(subject_id) VALUES(?)',('s1',))
            for i in range(260):
                minute=i*2
                hh=minute//60
                mm=minute%60
                hh2=(minute+1)//60
                mm2=(minute+1)%60
                entered=f'2026-11-01T{hh:02d}:{mm:02d}:00'
                finished=f'2026-11-01T{hh2:02d}:{mm2:02d}:00'
                conn.execute('INSERT INTO sessions(session_id,subject_id,checked_in_at,checked_out_at) '
                             'VALUES(?,?,?,?)',(uuid.uuid4().hex,'s1',entered,finished))
            conn.commit()
        results=self.s.listSessions({'subject_id':'s1',
            'from':'2026-11-01T00:00:00Z','to':'2026-11-02T00:00:00Z'})
        self.assertEqual(len(results),260)

    def test_v1_partial_unique_index_with_false_predicate_rejected(self):
        self.s.checkIn(self.inp())
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('DROP INDEX one_open_session')
            conn.execute('CREATE UNIQUE INDEX one_open_session ON sessions(subject_id) '
                         'WHERE checked_out_at IS NULL AND 1=0')
            conn.execute('UPDATE sessions SET checked_in_at=?',
                         ('2026-11-01T10:00:00.000000Z',))
            conn.execute('DROP TABLE IF EXISTS v1_provenance')
            conn.execute('PRAGMA user_version=1')
            conn.commit()
        self.must_fail('STORAGE_ERROR',lambda _: AttendanceService(self.db),None)
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute('PRAGMA user_version').fetchone()[0],1)

    def test_v2_forged_historical_signature_without_ledger_rejected(self):
        self.s.checkIn(self.inp(request_id='req1'))
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('UPDATE requests SET payload=? WHERE request_id=?',
                         (json.dumps({'signature_version':1,'operation':'checkIn',
                           'utc_occurred_at':'2026-11-01T10:00:00'},
                           sort_keys=True,separators=(',',':')),'req1'))
            conn.commit()
        self.must_fail('STORAGE_ERROR',self.s.checkIn,self.inp(request_id='req1'))

    def test_get_state_and_list_sessions_reject_corrupt_v2_timestamp(self):
        self.s.checkIn(self.inp())
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('UPDATE sessions SET checked_in_at=?',
                         ('2026-11-01T10:00:00invalid',))
            conn.commit()
        self.must_fail('STORAGE_ERROR', self.s.getState, {'subject_id':'s1'})
        self.must_fail('STORAGE_ERROR', self.s.listSessions,
                       {'subject_id':'s1','from':T0,'to':T3})

    def test_v1_additional_unique_index_and_trigger_rejected(self):
        for extra_sql in (
            'CREATE UNIQUE INDEX untrusted_unique ON sessions(subject_id)',
            'CREATE TRIGGER untrusted_drop BEFORE INSERT ON sessions '
            "BEGIN SELECT RAISE(IGNORE); END"
        ):
            with self.subTest(extra_sql=extra_sql):
                with tempfile.TemporaryDirectory() as tempdir:
                    path=str(Path(tempdir)/'legacy.sqlite')
                    AttendanceService(path).checkIn(self.inp())
                    with closing(sqlite3.connect(path)) as conn:
                        conn.execute('UPDATE sessions SET checked_in_at=?',
                                     ('2026-11-01T10:00:00.000000Z',))
                        conn.execute(extra_sql)
                        conn.execute('DROP TABLE IF EXISTS v1_provenance')
                        conn.execute('PRAGMA user_version=1')
                        conn.commit()
                    self.must_fail('STORAGE_ERROR',lambda _: AttendanceService(path),None)
                    with closing(sqlite3.connect(path)) as conn:
                        self.assertEqual(conn.execute('PRAGMA user_version').fetchone()[0],1)

    def test_v2_altered_partial_index_rejected(self):
        self.s.checkIn(self.inp())
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('DROP INDEX one_open_session')
            conn.execute('CREATE UNIQUE INDEX one_open_session ON sessions(subject_id) '
                         'WHERE checked_out_at IS NULL AND 1=0')
            conn.commit()
        self.must_fail('STORAGE_ERROR',lambda _: AttendanceService(self.db),None)

    def test_fraction_over_budget_rejected_before_regex(self):
        from attendance.core.service import utc
        oversized = '2026-11-01T11:00:00.' + '1' * 8193 + 'Z'
        self.assertLessEqual(len(oversized), 8218)
        with patch('attendance.core.service._RFC3339') as pattern:
            with self.assertRaises(AttendanceError) as caught:
                utc(oversized)
            self.assertEqual(caught.exception.code, 'INVALID_ARGUMENT')
            pattern.fullmatch.assert_not_called()
        # Both ceiling and supported input remain precise, not truncated.
        valid = '2026-11-01T10:00:00.' + '1' * 8192 + 'Z'
        self.assertEqual(len(utc(valid).split('.', 1)[1]), 8192)

    def test_fraction_resource_budget_exact(self):
        digits='1'*8192
        self.s.checkIn(self.inp('2026-11-01T10:00:00.'+digits+'Z'))
        self.must_fail('INVALID_ARGUMENT', self.s.checkOut,
                       self.inp('2026-11-01T11:00:00.'+digits+'1Z'))
        self.s.checkOut(self.inp(T1))

    def test_list_sessions_full_result_or_typed_budget(self):
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('INSERT INTO subjects(subject_id) VALUES(?)',('s1',))
            data=[]
            for index in range(10000):
                # Distinct, non-overlapping, strictly monotone intervals in
                # canonical UTC precision, within a single query window.
                def stamp(microseconds):
                    digits = f'{microseconds:06d}'.rstrip('0')
                    return '2026-11-01T10:00:00' + ('.' + digits if digits else '')
                entered, exited = stamp(index * 2), stamp(index * 2 + 1)
                data.append((uuid.uuid4().hex,'s1',entered,exited))
            self.assertTrue(all(data[i][3] < data[i+1][2] for i in range(len(data)-1)))
            conn.executemany('INSERT INTO sessions(session_id,subject_id,checked_in_at,checked_out_at) '
                             'VALUES(?,?,?,?)',data)
            conn.commit()
        self.assertEqual(len(self.s.listSessions({'subject_id':'s1','from':T0,'to':T2})),10000)
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('INSERT INTO sessions(session_id,subject_id,checked_in_at,checked_out_at) '
                         'VALUES(?,?,?,?)',
                         (uuid.uuid4().hex,'s1','2026-11-01T10:00:00.02','2026-11-01T10:00:00.020001'))
            conn.commit()
        self.must_fail('INVALID_ARGUMENT',self.s.listSessions,
                       {'subject_id':'s1','from':T0,'to':T2})

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
