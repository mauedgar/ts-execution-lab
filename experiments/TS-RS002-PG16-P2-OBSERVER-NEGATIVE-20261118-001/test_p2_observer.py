"""Synthetic no-Docker/no-secret security and custody tests for P2 revised candidate."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).parent))
import p2_observer as p


class P2SourceContractTests(unittest.TestCase):
    def hba_rule(self,n=1,**kw):
        o={"rule_number":n,"file_name":"/fake/pg_hba.conf","line_number":n,
           "type":"host","database":["all"],"user_name":["all"],
           "address":"127.0.0.1","netmask":"255.255.255.255",
           "auth_method":"scram-sha-256","error":None}
        o.update(kw)
        return json.dumps(o)

    def snap(self,keychange=None):
        lines=[f'{n}|1|'+('a'*64) for n in ('head','events','receipts')]
        lines+=['columns|'+'b'*64,'acl|'+'c'*64]
        if keychange is not None:
            ch='a' if keychange<3 else ('b' if keychange==3 else 'c')
            left,sep,right=lines[keychange].rpartition('|')
            lines[keychange]=left+sep+right.replace(ch,'d')
        return '\n'.join(lines)

    def test_original_binding(self):
        self.assertEqual(p.C_SHA,'7aef5dff689e1ceb5575084f2445caf25116cff5a22917815400693d99316852')
        self.assertEqual(p.CID,'5ce2b0833fa7ab04eac1b0c78e51ead0ed7c5e1dc2aede5621dba397b3c20d88')
        self.assertEqual(p.RUNNER_ID,'TS-RS002-P2-OBSERVER-20261118-002')

    def test_host_fixed_mechanical_argv_and_password_inside_container(self):
        argv=p.cmd_for(p.POSITIVE,True)
        self.assertEqual(argv[:6],[p.DOCKER,'exec','--user','postgres',p.CID,'sh'])
        self.assertEqual(argv[-1],p.POSITIVE)
        self.assertIn('cat /run/secrets/observer.pass',argv[7])
        self.assertIn('PGSSLMODE=disable',argv[7])
        self.assertIn('PGGSSENCMODE=disable',argv[7])
        self.assertNotIn('PGPASSWORD=',str(argv[:5]))
        self.assertEqual(p.cmd_for(p.SNAPSHOT,False)[5],'psql')

    def test_effective_hba_first_ipv4_scram_selected(self):
        self.assertEqual(p.effective_scram(['t',self.hba_rule(1)]),'rule=1|scram-sha-256')
        self.assertEqual(p.effective_scram(['t',self.hba_rule(1,address='10.0.0.0',netmask='255.0.0.0'),self.hba_rule(2)]),'rule=2|scram-sha-256')

    def test_effective_hba_earlier_reject_blocks(self):
        with self.assertRaisesRegex(RuntimeError,'HBA_FIRST_RULE_NOT_SCRAM'):
            p.effective_scram(['t',self.hba_rule(1,auth_method='reject'),self.hba_rule(2)])

    def test_effective_hba_wrong_role_or_database_not_evidence(self):
        with self.assertRaisesRegex(RuntimeError,'HBA_NO_EFFECTIVE_RULE'):
            p.effective_scram(['t',self.hba_rule(1,database=['otherdb']),self.hba_rule(2,user_name=['otheruser'])])

    def test_effective_hba_order_and_error(self):
        for data in (['f',self.hba_rule()],['t',self.hba_rule(2),self.hba_rule(1)],['t',self.hba_rule(1,error='broken')],['t',self.hba_rule(1,rule_number=None)]):
            with self.subTest(data=data),self.assertRaises(RuntimeError):p.effective_scram(data)

    def test_effective_hba_cidr_matching_and_unresolved_patterns(self):
        self.assertEqual(p.effective_scram(['t',self.hba_rule(1,address='127.0.0.0',netmask='255.0.0.0')]),'rule=1|scram-sha-256')
        for changes in ({'address':'localhost'},{'address':'samehost'},{'user_name':['+admins']},{'database':['/^ts_/']},{'auth_method':'trust'}):
            with self.subTest(changes=changes),self.assertRaises(RuntimeError):p.effective_scram(['t',self.hba_rule(1,**changes)])

    def test_hba_sql_checks_load_and_order(self):
        self.assertIn('pg_conf_load_time()',p.HBA)
        self.assertIn('pg_stat_file(file_name)',p.HBA)
        self.assertIn('ORDER BY rule_number',p.HBA)
        self.assertEqual(p.interpret('hba',0,'t\n'+self.hba_rule(),'',None),['rule=1|scram-sha-256'])

    def test_snapshot_stable_complete_fingerprints(self):
        b=p.interpret('snapshot_before',0,self.snap(),'',None)
        self.assertEqual(len(b),5)
        self.assertEqual(p.interpret('snapshot_after',0,self.snap(),'',b),b)
        for i in range(5):
            with self.subTest(i=i),self.assertRaisesRegex(RuntimeError,'SCHEMA_ROWS_CHANGED'):
                p.interpret('snapshot_after',0,self.snap(i),'',b)

    def test_snapshot_invalid_and_non_count_sensitivity(self):
        self.assertIn('to_jsonb(t)',p.SNAPSHOT)
        self.assertIn('sha256(convert_to',p.SNAPSHOT)
        self.assertIn('has_table_privilege',p.SNAPSHOT)
        with self.assertRaisesRegex(RuntimeError,'SNAPSHOT_INVALID'):p.interpret('snapshot_before',0,'1|2|3','',None)

    def test_positive_true_observer_and_endpoint(self):
        self.assertIn('REPEATABLE READ READ ONLY',p.POSITIVE)
        s='ts_rs002_observer|ts_rs002_observer|ts_rs002_a02_lab|on|on|127.0.0.1|f\n2'
        self.assertEqual(len(p.interpret('observer_read',0,s,'',None)),2)
        with self.assertRaisesRegex(RuntimeError,'OBSERVER_TCP_READ_NOT_PROVEN'):
            p.interpret('observer_read',0,s.replace('ts_rs002_observer','ts_rs002_admin'),'',None)

    def test_negative_delete_acl_does_not_hide_behind_readonly(self):
        self.assertIn('READ WRITE',p.DENY_DELETE)
        self.assertIn('WHERE FALSE',p.DENY_DELETE)
        self.assertIn('ROLLBACK',p.DENY_DELETE)
        self.assertEqual(p.interpret('deny_delete',3,'','ERROR: permission denied for table head',None),['ERROR: permission denied for table head'])
        for code,err in ((0,''),(3,'cannot execute DELETE in a read-only transaction')):
            with self.assertRaises(RuntimeError):p.interpret('deny_delete',code,'',err,None)

    def test_temp_and_set_role_denial(self):
        self.assertEqual(p.interpret('deny_temp',3,'','ERROR: permission denied to create temporary tables',None),['ERROR: permission denied to create temporary tables'])
        self.assertEqual(p.interpret('deny_role',3,'','ERROR: permission denied to set role',None),['ERROR: permission denied to set role'])
        for step in ('deny_temp','deny_role'):
            with self.assertRaises(RuntimeError):p.interpret(step,0,'','',None)

    def test_external_control_grant_exact_schema_and_git_root(self):
        self.assertIn('GRANT.json',p.CONTROL_GRANT_PATH)
        self.assertIn('ORIGINAL.md',p.REVIEW_REQUEST_PATH)
        self.assertIn('SOURCE_COMMIT_BLOB_MISMATCH',Path(p.__file__).read_text())
        self.assertIn('CONTROL_GRANT_GIT_ORIGIN_MISMATCH',Path(p.__file__).read_text())

    def test_forged_admission_rejected_before_git(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'admission.json'
            f.write_text('{}')
            with patch.object(p,'ADMISSION',f):
                with self.assertRaisesRegex(RuntimeError,'P2_ADMISSION_SCHEMA'):p.admittance()

    def test_safe_read_symlink_and_other_uid(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'a';b=Path(d)/'b';a.write_text('test');a.chmod(0o600);b.symlink_to(a)
            self.assertEqual(p.safe_read(a),b'test')
            with self.assertRaises(RuntimeError):p.safe_read(b)
            a.chmod(0o666)
            with self.assertRaises(RuntimeError):p.safe_read(a)

    def test_create_only_receipt_collision(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'receipt.json'
            p.write_once(f,{'one':1})
            with self.assertRaises(FileExistsError):p.write_once(f,{'two':2})

    def test_original_step_prespawn_intent_before_any_docker_child(self):
        with tempfile.TemporaryDirectory() as d:
            receipts=Path(d)/'isolated'
            with patch.object(p,'RECEIPTS',receipts),patch.object(p,'preflight',return_value=('a'*64,'b'*64)),patch.object(p.subprocess,'Popen',side_effect=OSError('deliberate synthetic spawn denied')):
                with self.assertRaises(SystemExit):p.execute()
            self.assertTrue((receipts/'step_intent_hba.json').exists())
            self.assertFalse((receipts/'start_hba.json').exists())
            terminal=json.loads((receipts/'terminal.json').read_text())
            self.assertEqual(terminal['status'],'UNKNOWN')
            self.assertTrue(terminal['no_retry'])

    def test_bounded_child_streams(self):
        child=subprocess.Popen([sys.executable,'-c','import sys;sys.stdout.write("ok");sys.stderr.write("x")'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out,err=p.capture_bounded(child,timeout=5,limit=10)
        self.assertEqual((out,err),('ok','x'))
        child.wait(timeout=5)
        child.stdout.close(); child.stderr.close()

    def test_exact_step_sequence(self):
        self.assertEqual(tuple(s[0] for s in p.STEPS),('hba','snapshot_before','observer_read','deny_delete','deny_temp','deny_role','snapshot_after'))
        for _,sql,_ in p.STEPS:self.assertTrue(sql.endswith('COMMIT;') or sql.endswith('ROLLBACK;'))
        self.assertNotIn('PGPASSWORD',' '.join(s[1] for s in p.STEPS))


if __name__=='__main__':unittest.main()
