"""Synthetic no-Docker/no-secret security and custody tests for P2 revised candidate."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

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
        lines+=['columns|'+'b'*64,'acl|'+'c'*64,'authority|'+'e'*64,'ddl|'+'f'*64]
        if keychange is not None:
            ch=['a','a','a','b','c','e','f'][keychange]
            left,sep,right=lines[keychange].rpartition('|')
            lines[keychange]=left+sep+right.replace(ch,'d')
        return '\n'.join(lines)

    def test_original_binding(self):
        self.assertEqual(p.C_SHA,'7aef5dff689e1ceb5575084f2445caf25116cff5a22917815400693d99316852')
        self.assertEqual(p.CID,'5ce2b0833fa7ab04eac1b0c78e51ead0ed7c5e1dc2aede5621dba397b3c20d88')
        self.assertEqual(p.RUNNER_ID,'TS-RS002-P2-OBSERVER-20261118-003')

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
        self.assertEqual(len(b),7)
        self.assertEqual(p.interpret('snapshot_after',0,self.snap(),'',b),b)
        for i in range(7):
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


    def review_text(self, *, verdict="RECOMMEND", findings=0, advisories=0, duplicate=False):
        j={"source_commit":"a"*40,"source_blob":"b"*40}
        begin="<!-- TS_RS002_P2_REVIEW_ADMISSION_V1_BEGIN -->"
        end="<!-- TS_RS002_P2_REVIEW_ADMISSION_V1_END -->"
        block="\n".join((begin,"review_id: "+p.REVIEW_ID,"verdict: RECOMMEND",
            "findings: 0","advisories: 0",
            "source_head: "+j["source_commit"],"source_blob: "+j["source_blob"],end))
        header=("Review_ID: "+chr(96)+p.REVIEW_ID+chr(96)+"\n" +
            "Verdict: **"+verdict+"**\nFindings: **"+str(findings)+"**\n" +
            "Advisories: **"+str(advisories)+"**\n")
        return header+block+("\n"+block if duplicate else ""),j

    def test_review_admission_exact_unique_and_provenance(self):
        review,j=self.review_text()
        p.parse_review_admission(review,j)
        self.assertIn("PR59-WEBINLINE-IR003",p.REVIEW_REQUEST_PATH)
        self.assertIn("PR59-PHYSICAL-ADMISSION",p.CONTROL_GRANT_PATH)
        self.assertNotIn("PR56",p.REVIEW_REQUEST_PATH+p.CONTROL_GRANT_PATH)

    def test_review_admission_rejects_duplicates_and_no_recommend(self):
        for opts in ({"duplicate":True},{"verdict":"NO_RECOMMEND"},
                     {"findings":1},{"advisories":1}):
            review,j=self.review_text(**opts)
            with self.subTest(opts=opts),self.assertRaises(RuntimeError):
                p.parse_review_admission(review,j)

    def test_review_admission_rejects_forged_subject(self):
        review,j=self.review_text()
        for bad in ({"source_commit":"c"*40,"source_blob":j["source_blob"]},
                    {"source_commit":j["source_commit"],"source_blob":"d"*40}):
            with self.subTest(bad=bad),self.assertRaises(RuntimeError):
                p.parse_review_admission(review,bad)

    def test_full_authority_and_ddl_fingerprints_in_readonly_snapshot(self):
        for name in ("pg_auth_members","rolsuper","rolbypassrls","rolcreaterole",
                     "has_database_privilege","has_schema_privilege",
                     "pg_get_constraintdef","pg_indexes","pg_get_triggerdef",
                     "REFERENCES","TRIGGER"):
            with self.subTest(name=name):
                self.assertIn(name,p.SNAPSHOT)
        self.assertIn("REPEATABLE READ READ ONLY",p.SNAPSHOT)
        self.assertEqual(p.SNAPSHOT.count("COMMIT;"),1)

    def test_timeout_preserves_original_pid_and_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            receipts=Path(d)/"original"
            fake=Mock()
            fake.pid=9988
            fake.poll.return_value=None
            with patch.object(p,"RECEIPTS",receipts), \
                 patch.object(p,"preflight",return_value=("a"*64,"b"*64)), \
                 patch.object(p.subprocess,"Popen",return_value=fake), \
                 patch.object(p,"capture_bounded",side_effect=RuntimeError(
                     "NATIVE_CHILD_TIMEOUT_UNRECONCILED")):
                with self.assertRaises(SystemExit):
                    p.execute()
            before=json.loads((receipts/"step_intent_hba.json").read_text())
            running=json.loads((receipts/"start_hba.json").read_text())
            failure=json.loads((receipts/"failure_hba.json").read_text())
            terminal=json.loads((receipts/"terminal.json").read_text())
            self.assertEqual(before["status"],"PRE_SPAWN_UNKNOWN")
            self.assertEqual(running["pid"],9988)
            self.assertEqual(failure["pid"],9988)
            self.assertEqual(failure["status"],"UNKNOWN")
            self.assertEqual(terminal["status"],"UNKNOWN")
            self.assertTrue(terminal["no_retry"])

    def test_source_only_separate_host_dac_dependency(self):
        self.assertIn("other-UID host-DAC negative",Path(p.__file__).read_text())
        self.assertIn("CONTAINER_PGDATA_DRIFT",Path(p.__file__).read_text())
        self.assertIn("ORIGINAL_READONLY_BIND_INVENTORY_DRIFT",Path(p.__file__).read_text())


if __name__=='__main__':unittest.main()
