"""Prospective Parent H6 E2E: actual operator process talking to SQLite domain."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = str(Path(__file__).resolve().parents[3])


class ParentE2E(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / 'attendance.db')

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *args):
        env = dict(os.environ, PYTHONPATH=ROOT)
        p = subprocess.run([sys.executable,'-m','attendance.operator.cli','--db',self.db,*args],capture_output=True,text=True,env=env,timeout=10)
        return p.returncode, json.loads(p.stdout or p.stderr)

    def test_real_2_processes_and_persistence(self):
        t0='2026-11-01T10:00:00Z'
        t1='2026-11-01T10:30:00Z'
        t2='2026-11-01T11:00:00Z'
        start=('check-in','--subject-id','p1','--occurred-at',t0,'--request-id','original')
        n,a=self.cli(*start)
        self.assertEqual(n,0,a)
        n,b=self.cli(*start)
        self.assertEqual(n,0,b)
        self.assertEqual(a['data'],b['data'])
        n,state=self.cli('state','--subject-id','p1')
        self.assertEqual(n,0,state)
        self.assertTrue(state['data']['active'])
        n,e=self.cli('check-in','--subject-id','p1','--occurred-at',t1)
        self.assertEqual(n,1,e)
        self.assertEqual(e['error']['code'],'ALREADY_OPEN')
        n,end=self.cli('check-out','--subject-id','p1','--occurred-at',t1)
        self.assertEqual(n,0,end)
        n,ls=self.cli('list','--subject-id','p1','--from',t0,'--to',t2)
        self.assertEqual(n,0,ls)
        self.assertEqual(len(ls['data']),1)
        self.assertEqual(ls['data'][0]['session_id'],a['data']['session_id'])
        n,unknown=self.cli('state','--subject-id','missing')
        self.assertEqual(n,1,unknown)
        self.assertEqual(unknown['error']['code'],'NOT_FOUND')


if __name__ == '__main__':
    unittest.main()
