import io
import json
import unittest

from attendance.operator.cli import main


class MockError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


class MockService:
    def __init__(self, path):
        self.path = path
        self.calls = []
        self.error = None

    def perform(self, op, payload):
        self.calls.append((op, payload))
        if self.error:
            raise MockError(self.error)
        return {'op':op,'payload':payload}

    def checkIn(self, p): return self.perform('checkIn',p)
    def checkOut(self, p): return self.perform('checkOut',p)
    def getState(self, p): return self.perform('getState',p)
    def listSessions(self, p): return self.perform('listSessions',p)


class OperatorTests(unittest.TestCase):
    def setUp(self):
        self.service = MockService('dummy')
        self.out = io.StringIO()
        self.err = io.StringIO()

    def run_cli(self, *args):
        code = main(['--db','mock.sqlite',*args], service_factory=lambda p:self.service, out=self.out, err=self.err)
        data = json.loads(self.out.getvalue() or self.err.getvalue())
        return code,data

    def test_four_commands_using_service_interface(self):
        stamp='2026-11-02T00:00:00Z'
        cases=[
            (('check-in','--subject-id','s1','--occurred-at',stamp,'--request-id','r1'),'checkIn',{'subject_id':'s1','occurred_at':stamp,'request_id':'r1'}),
            (('check-out','--subject-id','s1','--occurred-at',stamp),'checkOut',{'subject_id':'s1','occurred_at':stamp}),
            (('state','--subject-id','s1'),'getState',{'subject_id':'s1'}),
            (('list','--subject-id','s1','--from',stamp,'--to','2026-11-03T00:00:00Z'),'listSessions',{'subject_id':'s1','from':stamp,'to':'2026-11-03T00:00:00Z'})
        ]
        for args,expected,payload in cases:
            with self.subTest(expected):
                self.out=io.StringIO()
                code,response=self.run_cli(*args)
                self.assertEqual(code,0)
                self.assertTrue(response['ok'])
                self.assertEqual(self.service.calls[-1],(expected,payload))

    def test_typed_error_is_reported_without_masking(self):
        for err in ('NOT_FOUND','INVALID_ARGUMENT','NO_OPEN_SESSION','REQUEST_CONFLICT','ALREADY_OPEN'):
            with self.subTest(err):
                self.err=io.StringIO()
                self.service.error=err
                code,response=self.run_cli('state','--subject-id','missing')
                self.assertEqual(code,1)
                self.assertFalse(response['ok'])
                self.assertEqual(response['error']['code'],err)

    def test_no_database_or_schema_access(self):
        from pathlib import Path
        text=Path(__file__).parents[2].joinpath('operator','cli.py').read_text()
        self.assertNotIn('import sqlite3',text)
        self.assertNotIn('sqlite_store',text)
        self.assertNotIn('CREATE TABLE',text)


if __name__ == '__main__':
    unittest.main()
