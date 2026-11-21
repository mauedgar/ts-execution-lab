"""Synthetic no-Docker/no-secret security and custody tests for P2 revised candidate."""
import json
import os
import base64
import hashlib
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
        lines+=['columns|'+'b'*64,'acl|'+'c'*64,'authority|'+'e'*64,'ddl|'+'f'*64,'rls|'+'a'*64,'functions|'+'b'*64]
        if keychange is not None:
            ch=['a','a','a','b','c','e','f','a','b'][keychange]
            left,sep,right=lines[keychange].rpartition('|')
            lines[keychange]=left+sep+right.replace(ch,'d')
        return '\n'.join(lines)

    def test_original_binding(self):
        self.assertEqual(p.C_SHA,'7aef5dff689e1ceb5575084f2445caf25116cff5a22917815400693d99316852')
        self.assertEqual(p.CID,'5ce2b0833fa7ab04eac1b0c78e51ead0ed7c5e1dc2aede5621dba397b3c20d88')
        self.assertEqual(p.RUNNER_ID,'TS-RS002-P2-OBSERVER-20261119-006')

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
        self.assertEqual(len(b),9)
        self.assertEqual(p.interpret('snapshot_after',0,self.snap(),'',b),b)
        for i in range(9):
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
            with patch.object(p,'RECEIPTS',receipts),patch.object(p,'SOURCE_ROOT',Path(d)),patch.object(p,'NATIVE_CUSTODY',None),patch.object(p,'verify_prior_preflight',return_value=None),patch.object(p,'preflight',return_value=('a'*64,'b'*64)),patch.object(p.subprocess,'Popen',side_effect=OSError('deliberate synthetic spawn denied')):
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
        self.assertIn("PR62-WEBINLINE-IR007",p.REVIEW_REQUEST_PATH)
        self.assertIn("PR62-PHYSICAL-ADMISSION",p.CONTROL_GRANT_PATH)
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
                     "REFERENCES","TRIGGER","pg_policy","relrowsecurity","relforcerowsecurity",
                     "pg_get_functiondef","pg_get_function_identity_arguments","polwithcheck"):
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
            with patch.object(p,"RECEIPTS",receipts),patch.object(p,"SOURCE_ROOT",Path(d)),patch.object(p,"NATIVE_CUSTODY",None),patch.object(p,"verify_prior_preflight",return_value=None), \
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


    def test_review_rejects_duplicate_summary_headers_and_id(self):
        review,j=self.review_text()
        for addition in ("Findings: **3**", "Advisories: **2**",
                         "Verdict: **NO_RECOMMEND**",
                         "Review_ID: "+chr(96)+"old"+chr(96)):
            with self.subTest(addition=addition), self.assertRaises(RuntimeError):
                p.parse_review_admission(review+"\n"+addition,j)

    def p0_provenance_fixture(self):
        identity="11111111-1111-4111-8111-111111111111"
        denial="22222222-2222-4222-8222-222222222222"
        native={
            "protocol":"TS-RS002-P2-P0-HOST-DAC-NATIVE-v2",
            "execution_attempt":p.P0_NATIVE_ATTEMPT,
            "provider":"ORCA_NATIVE_TERMINAL",
            "status":"PASS","host":p.HOST,"distro":"Ubuntu-24.04",
            "terminal":p.P0_TERMINAL,"terminal_incarnation":p.P0_TERMINAL_INCAR,
            "container_id":p.CID,"prior_C_terminal_sha256":p.C_SHA,
            "secret_contents_exposed":False,"Product_effect":"NONE",
            "identity":{"request_id":identity,"native_pid":24501,"exit_code":0,"observed_uid":65534},
            "denial":{"request_id":denial,"native_pid":24502,"exit_code":1,"observed_uid":65534}}
        raw=json.dumps(native,sort_keys=True).encode()
        digest=hashlib.sha256(raw).hexdigest()
        begin="<!-- TS_RS002_P0_PROVIDER_REVIEW_V1_BEGIN -->"
        end="<!-- TS_RS002_P0_PROVIDER_REVIEW_V1_END -->"
        metadata="\n".join(("review_id: "+p.P0_REVIEW_ID,"verdict: RECOMMEND",
            "findings: 0","advisories: 0",
            "native_attempt: "+p.P0_NATIVE_ATTEMPT,
            "native_original_sha256: "+digest,
            "identity_request_id: "+identity,"denial_request_id: "+denial,
            "native_exits: 0,1","provider_native_observed: true"))
        review=("Review_ID: "+chr(96)+p.P0_REVIEW_ID+chr(96)+"\n"+
            "Verdict: **RECOMMEND**\nFindings: **0**\nAdvisories: **0**\n"+
            begin+"\n"+metadata+"\n"+end+"\n")
        review_bytes=review.encode()
        j={"p0_receipt_commit":"a"*40,"p0_receipt_blob":"b"*40,
           "p0_receipt_sha256":digest,
           "p0_review_commit":"c"*40,"p0_review_blob":"d"*40,
           "p0_review_sha256":hashlib.sha256(review_bytes).hexdigest()}
        return native,raw,review,j

    def test_p0_provider_native_and_distinct_review_required(self):
        native,raw,review,j=self.p0_provenance_fixture()
        original={"path":p.P0_DAC_ORIGINAL_PATH,"sha":j["p0_receipt_blob"],
                  "content":base64.b64encode(raw).decode()}
        independent={"path":p.P0_REVIEW_PATH,"sha":j["p0_review_blob"],
                     "content":base64.b64encode(review.encode()).decode()}
        with patch.object(p,"read_output",side_effect=[
             json.dumps(original),json.dumps(independent)]) as reader:
            p.verify_p0_dac(j)
        self.assertEqual(reader.call_count,2)
        p.validate_p0_native(native)
        p.validate_p0_review(review,native,hashlib.sha256(raw).hexdigest())

    def test_p0_forged_single_json_without_independent_review_denied(self):
        native,raw,review,j=self.p0_provenance_fixture()
        doc={"path":p.P0_DAC_ORIGINAL_PATH,"sha":j["p0_receipt_blob"],
             "content":base64.b64encode(raw).decode()}
        with patch.object(p,"read_output",side_effect=[
             json.dumps(doc),json.dumps({"path":p.P0_REVIEW_PATH,
             "sha":"e"*40,"content":""})]):
            with self.assertRaisesRegex(RuntimeError,"P0_INDEPENDENT_REVIEW_GIT_MISMATCH"):
                p.verify_p0_dac(j)

    def test_p0_native_identity_and_unreviewed_exit_forgeries_rejected(self):
        native,raw,review,j=self.p0_provenance_fixture()
        for changed in (
            ("denial","exit_code",0),("identity","observed_uid",0),
            ("identity","native_pid",0),
            ("denial","request_id",native["identity"]["request_id"])):
            with self.subTest(changed=changed):
                forged=json.loads(json.dumps(native))
                forged[changed[0]][changed[1]]=changed[2]
                with self.assertRaises(RuntimeError): p.validate_p0_native(forged)
        bad=review.replace("native_exits: 0,1","native_exits: 0,0")
        with self.assertRaises(RuntimeError):
            p.validate_p0_review(bad,native,hashlib.sha256(raw).hexdigest())
        with self.assertRaises(RuntimeError):
            p.validate_p0_review(review+"\nFindings: **4**",native,hashlib.sha256(raw).hexdigest())

    def test_indirect_role_attributes_in_every_role_fingerprint(self):
        self.assertIn("FROM pg_roles)",p.AUTHORITY_SNAPSHOT)
        self.assertNotIn("WHERE rolname IN",p.AUTHORITY_SNAPSHOT)
        for name in ("rolsuper","rolbypassrls","rolcreaterole",
                     "rolinherit","rolconnlimit","rolvaliduntil"):
            with self.subTest(name=name):self.assertIn(name,p.AUTHORITY_SNAPSHOT)
        before=p.interpret("snapshot_before",0,self.snap(),"",None)
        changed=p.interpret("snapshot_before",0,self.snap(5),"",None)
        self.assertEqual(before[:5],changed[:5])
        with self.assertRaisesRegex(RuntimeError,"SCHEMA_ROWS_CHANGED"):
            p.interpret("snapshot_after",0,self.snap(5),"",before)

    def test_crash_gap_is_unknown_no_replay_even_without_native_pid(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"attempt"
            self.assertEqual(p.classify_existing_attempt(root),"NONE")
            root.mkdir(mode=0o700)
            p.write_once(root/"step_intent_hba.json",{"status":"PRE_SPAWN_UNKNOWN"})
            self.assertEqual(p.classify_existing_attempt(root),"UNKNOWN_NONREPLAYABLE")
            p.write_once(root/"terminal.json",{"runner_id":p.RUNNER_ID,
                "status":"UNKNOWN","no_retry":True})
            self.assertEqual(p.classify_existing_attempt(root),"TERMINAL_UNKNOWN")

    def test_postspawn_receipt_write_error_preserves_unknown_original_pid(self):
        with tempfile.TemporaryDirectory() as d:
            receipts=Path(d)/"single"
            child=Mock()
            child.pid=66111
            original=p.write_once
            def fail_after_spawn(path,record):
                if path.name=="start_hba.json":
                    raise OSError("synthetic receipt I/O failure")
                return original(path,record)
            with (patch.object(p,"RECEIPTS",receipts),patch.object(p,"SOURCE_ROOT",Path(d)),patch.object(p,"NATIVE_CUSTODY",None),patch.object(p,"verify_prior_preflight",return_value=None),
                  patch.object(p,"preflight",return_value=("a"*64,"b"*64)),
                  patch.object(p.subprocess,"Popen",return_value=child),
                  patch.object(p,"write_once",side_effect=fail_after_spawn)):
                with self.assertRaises(SystemExit):
                    p.execute()
            terminal=json.loads((receipts/"terminal.json").read_text())
            self.assertEqual(terminal["status"],"UNKNOWN")
            self.assertEqual(terminal["possibly_unreconciled_child_pid"],66111)
            self.assertEqual(terminal["possibly_unreconciled_step"],"hba")
            self.assertTrue((receipts/"step_intent_hba.json").exists())
            self.assertFalse((receipts/"start_hba.json").exists())
            self.assertTrue(terminal["no_retry"])

    def test_stream_overflow_retains_original_child_and_no_retry(self):
        with tempfile.TemporaryDirectory() as d:
            receipts=Path(d)/"single"
            child=Mock()
            child.pid=66112
            child.poll.return_value=None
            with (patch.object(p,"RECEIPTS",receipts),patch.object(p,"SOURCE_ROOT",Path(d)),patch.object(p,"NATIVE_CUSTODY",None),patch.object(p,"verify_prior_preflight",return_value=None),
                  patch.object(p,"preflight",return_value=("a"*64,"b"*64)),
                  patch.object(p.subprocess,"Popen",return_value=child),
                  patch.object(p,"capture_bounded",side_effect=RuntimeError(
                      "NATIVE_OUTPUT_LIMIT_UNRECONCILED"))):
                with self.assertRaises(SystemExit):
                    p.execute()
            terminal=json.loads((receipts/"terminal.json").read_text())
            fail=json.loads((receipts/"failure_hba.json").read_text())
            self.assertEqual(terminal["status"],"UNKNOWN")
            self.assertEqual(terminal["possibly_unreconciled_child_pid"],66112)
            self.assertEqual(fail["pid"],66112)
            self.assertTrue(terminal["no_retry"])


    def test_native_read_output_without_prior_intent_never_spawns(self):
        with patch.object(p,"NATIVE_CUSTODY",None), \
             patch.object(p.subprocess,"Popen") as spawn:
            with self.assertRaisesRegex(RuntimeError,"NATIVE_COMMAND_OUTSIDE_DURABLE_CUSTODY"):
                p.read_output(["/usr/bin/true"])
            spawn.assert_not_called()

    def test_prespawn_native_preflight_intent_is_durable_and_nonreplayable(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"preflight"
            with (patch.object(p,"SOURCE_ROOT",Path(d)),
                  patch.object(p,"NATIVE_CUSTODY",None),
                  patch.object(p,"NATIVE_OBSERVATION_SEQ",0),
                  patch.object(p,"expected_preflight_argv",return_value=[["/usr/bin/true"]]*11),
                  patch.object(p.subprocess,"Popen",side_effect=OSError("synthetic spawn failure")) as spawn):
                p.begin_native_custody(root,"PREFLIGHT")
                with self.assertRaises(OSError):
                    p.read_output(["/usr/bin/true"])
                self.assertTrue((root/"native_intent.json").exists())
                self.assertTrue((root/"native_01_intent.json").exists())
                self.assertFalse((root/"native_01_start.json").exists())
                with self.assertRaisesRegex(RuntimeError,"NATIVE_ATTEMPT_ALREADY_EXISTS_NO_RETRY"):
                    p.begin_native_custody(root,"PREFLIGHT")
                spawn.assert_called_once()
                self.assertEqual(p.classify_existing_attempt(root),"UNKNOWN_NONREPLAYABLE")

    def test_interrupted_preflight_cannot_spawn_in_second_invocation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"preflight"
            work=Path(d)/"run"
            with (patch.object(p,"SOURCE_ROOT",Path(d)),
                  patch.object(p,"PREFLIGHT_RECEIPTS",root),
                  patch.object(p,"RECEIPTS",work),
                  patch.object(p,"NATIVE_CUSTODY",None),
                  patch.object(p,"NATIVE_OBSERVATION_SEQ",0),
                  patch.object(p,"expected_preflight_argv",return_value=[["/usr/bin/true"]]*11),
                  patch.object(p,"preflight",side_effect=lambda:p.read_output(["/usr/bin/true"])),
                  patch.object(p.subprocess,"Popen",side_effect=OSError("synthetic child failure")) as spawn):
                with self.assertRaisesRegex(RuntimeError,"NATIVE_PREFLIGHT_BLOCKED_NONREPLAYABLE"):
                    p.run_native_preflight()
                self.assertTrue((root/"native_intent.json").exists())
                self.assertTrue((root/"native_01_intent.json").exists())
                terminal=json.loads((root/"terminal.json").read_text())
                self.assertEqual(terminal["status"],"UNKNOWN")
                with self.assertRaisesRegex(RuntimeError,"NATIVE_ATTEMPT_ALREADY_EXISTS_NO_RETRY"):
                    p.run_native_preflight()
                spawn.assert_called_once()

    def test_run_requires_distinct_original_preflight_receipt(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"preflight"
            root.mkdir(mode=0o700)
            with (patch.object(p,"PREFLIGHT_RECEIPTS",root),
                  patch.object(p,"ADMISSION",Path(d)/"admission.json")):
                with self.assertRaises(Exception):p.verify_prior_preflight()
                self.assertFalse((root/"terminal.json").exists())


    def test_native_preflight_success_records_original_process_exit(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"preflight"
            with (patch.object(p,"SOURCE_ROOT",Path(d)),
                  patch.object(p,"NATIVE_CUSTODY",None),
                  patch.object(p,"NATIVE_OBSERVATION_SEQ",0),
                  patch.object(p,"expected_preflight_argv",return_value=[[sys.executable,"-c","print('synthetic_native_readonly')"]]*11)):
                p.begin_native_custody(root,"PREFLIGHT")
                result=p.read_output([sys.executable,"-c","print('synthetic_native_readonly')"])
                self.assertEqual(result,"synthetic_native_readonly")
                started=json.loads((root/"native_01_start.json").read_text())
                finished=json.loads((root/"native_01_terminal.json").read_text())
                self.assertGreater(started["pid"],0)
                self.assertEqual(finished["pid"],started["pid"])
                self.assertEqual(finished["exit_code"],0)
                self.assertEqual(finished["status"],"TERMINAL")
                self.assertEqual(finished["stdout_sha256"],hashlib.sha256(
                    b"synthetic_native_readonly\n").hexdigest())
                self.assertTrue(finished["no_retry"])


    def make_native_manifest_fixture(self,root:Path, admission:Path):
        """Eleven harmless subprocesses prove deterministic chain serialization."""
        admission.write_bytes(b'{"synthetic":true}')
        admission.chmod(0o600)
        cmd=[sys.executable,"-c","print('native_fixture')"]
        pin=patch.object(p,"expected_preflight_argv",return_value=[cmd]*11)
        pin.start()
        self.addCleanup(pin.stop)
        p.begin_native_custody(root,"PREFLIGHT")
        for _ in range(11):
            self.assertEqual(p.read_output(cmd),"native_fixture")
        manifest=p.collect_native_preflight_chain(root,11,finalized=False)
        raw=p.write_once(root/"native_manifest.json",manifest)
        terminal={
            "runner_id":p.RUNNER_ID,"status":"PASS","code":"OK",
            "no_retry":True,"source_sha256":p.sha(Path(p.__file__).read_bytes()),
            "admission_sha256":p.sha(p.safe_read(admission)),
            "container_id":p.CID,"prior_C_sha256":p.C_SHA,
            "manifest_sha256":p.sha(raw),"native_count":11,
            "root_intent_sha256":manifest["root_intent_sha256"],
            "Product_effect":"NONE"}
        p.write_once(root/"terminal.json",terminal)
        return manifest

    def test_completed_native_preflight_manifest_verified_before_run(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"preflight";adm=Path(d)/"admission.json"
            with (patch.object(p,"SOURCE_ROOT",Path(d)),
                  patch.object(p,"PREFLIGHT_RECEIPTS",root),
                  patch.object(p,"ADMISSION",adm),
                  patch.object(p,"NATIVE_CUSTODY",None),
                  patch.object(p,"NATIVE_OBSERVATION_SEQ",0)):
                m=self.make_native_manifest_fixture(root,adm)
                self.assertEqual(m["native_count"],11)
                self.assertEqual(len(m["children"]),11)
                self.assertGreater(m["children"][0]["pid"],0)
                self.assertEqual(m["children"][0]["exit_code"],0)
                with self.assertRaisesRegex(RuntimeError,"PREFLIGHT_NATIVE_PROVIDER_CUSTODY_NOT_QUALIFIED"):
                    p.verify_prior_preflight()

    def test_forged_pass_summary_without_manifest_cannot_admit_run(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"preflight";adm=Path(d)/"admission.json"
            with (patch.object(p,"SOURCE_ROOT",Path(d)),
                  patch.object(p,"PREFLIGHT_RECEIPTS",root),
                  patch.object(p,"ADMISSION",adm),
                  patch.object(p,"NATIVE_CUSTODY",None),
                  patch.object(p,"NATIVE_OBSERVATION_SEQ",0)):
                self.make_native_manifest_fixture(root,adm)
                (root/"native_manifest.json").unlink()
                with self.assertRaises(Exception): p.verify_prior_preflight()

    def test_missing_native_child_terminal_blocks_run(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"preflight";adm=Path(d)/"admission.json"
            with (patch.object(p,"SOURCE_ROOT",Path(d)),
                  patch.object(p,"PREFLIGHT_RECEIPTS",root),
                  patch.object(p,"ADMISSION",adm),
                  patch.object(p,"NATIVE_CUSTODY",None),
                  patch.object(p,"NATIVE_OBSERVATION_SEQ",0)):
                self.make_native_manifest_fixture(root,adm)
                (root/"native_01_terminal.json").unlink()
                with self.assertRaisesRegex(RuntimeError,"PREFLIGHT_NATIVE_RECEIPT_SET_INCOMPLETE_OR_EXTRA"):
                    p.verify_prior_preflight()

    def test_orphan_unknown_or_extra_native_child_blocks_run(self):
        for extra_name in ("native_12_intent.json","native_01_unknown.json","unexpected.json"):
            with self.subTest(extra=extra_name),tempfile.TemporaryDirectory() as d:
                root=Path(d)/"preflight";adm=Path(d)/"admission.json"
                with (patch.object(p,"SOURCE_ROOT",Path(d)),
                      patch.object(p,"PREFLIGHT_RECEIPTS",root),
                      patch.object(p,"ADMISSION",adm),
                      patch.object(p,"NATIVE_CUSTODY",None),
                      patch.object(p,"NATIVE_OBSERVATION_SEQ",0)):
                    self.make_native_manifest_fixture(root,adm)
                    p.write_once(root/extra_name,{"status":"UNKNOWN","no_retry":True})
                    with self.assertRaisesRegex(RuntimeError,"PREFLIGHT_NATIVE_RECEIPT_SET_INCOMPLETE_OR_EXTRA"):
                        p.verify_prior_preflight()

    def test_changed_terminal_hash_and_native_pid_break_original_chain(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"preflight";adm=Path(d)/"admission.json"
            with (patch.object(p,"SOURCE_ROOT",Path(d)),
                  patch.object(p,"PREFLIGHT_RECEIPTS",root),
                  patch.object(p,"ADMISSION",adm),
                  patch.object(p,"NATIVE_CUSTODY",None),
                  patch.object(p,"NATIVE_OBSERVATION_SEQ",0)):
                self.make_native_manifest_fixture(root,adm)
                target=root/"native_01_terminal.json"
                child=json.loads(target.read_text())
                child["pid"]=child["pid"]+1
                target.write_text(json.dumps(child)+"\n")
                with self.assertRaisesRegex(RuntimeError,"PREFLIGHT_NATIVE_TERMINAL_UNVERIFIED"):
                    p.verify_prior_preflight()

    def test_tampered_manifest_digest_or_count_cannot_admit_run(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"preflight";adm=Path(d)/"admission.json"
            with (patch.object(p,"SOURCE_ROOT",Path(d)),
                  patch.object(p,"PREFLIGHT_RECEIPTS",root),
                  patch.object(p,"ADMISSION",adm),
                  patch.object(p,"NATIVE_CUSTODY",None),
                  patch.object(p,"NATIVE_OBSERVATION_SEQ",0)):
                self.make_native_manifest_fixture(root,adm)
                t=root/"terminal.json";j=json.loads(t.read_text())
                j["native_count"]=2
                t.write_text(json.dumps(j)+"\n")
                with self.assertRaisesRegex(RuntimeError,"PREFLIGHT_NATIVE_COUNT_NOT_FIXED"):
                    p.verify_prior_preflight()
                j["native_count"]=11;j["manifest_sha256"]="0"*64
                t.write_text(json.dumps(j)+"\n")
                with self.assertRaisesRegex(RuntimeError,"PREFLIGHT_MANIFEST_DIGEST_MISMATCH"):
                    p.verify_prior_preflight()


    def test_coherent_forged_command_digest_still_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"preflight";adm=Path(d)/"admission.json"
            with (patch.object(p,"SOURCE_ROOT",Path(d)),
                  patch.object(p,"PREFLIGHT_RECEIPTS",root),
                  patch.object(p,"ADMISSION",adm),
                  patch.object(p,"NATIVE_CUSTODY",None),
                  patch.object(p,"NATIVE_OBSERVATION_SEQ",0)):
                self.make_native_manifest_fixture(root,adm)
                intent_path=root/"native_01_intent.json"
                start_path=root/"native_01_start.json"
                term_path=root/"native_01_terminal.json"
                intent=json.loads(intent_path.read_text())
                intent["command_sha256"]="f"*64
                intent_path.write_text(json.dumps(intent)+"\n")
                start=json.loads(start_path.read_text())
                start["intent_sha256"]=p.sha(intent_path.read_bytes())
                start_path.write_text(json.dumps(start)+"\n")
                term=json.loads(term_path.read_text())
                term["start_sha256"]=p.sha(start_path.read_bytes())
                term_path.write_text(json.dumps(term)+"\n")
                manifest_path=root/"native_manifest.json"
                manifest=json.loads(manifest_path.read_text())
                manifest["children"][0].update({
                    "command_sha256":"f"*64,
                    "intent_sha256":p.sha(intent_path.read_bytes()),
                    "start_sha256":p.sha(start_path.read_bytes()),
                    "terminal_sha256":p.sha(term_path.read_bytes())})
                manifest_path.write_text(json.dumps(manifest)+"\n")
                prior_path=root/"terminal.json";prior=json.loads(prior_path.read_text())
                prior["manifest_sha256"]=p.sha(manifest_path.read_bytes())
                prior_path.write_text(json.dumps(prior)+"\n")
                with self.assertRaisesRegex(RuntimeError,"PREFLIGHT_NATIVE_UNAUTHORIZED_COMMAND"):
                    p.verify_prior_preflight()

    def test_coherent_truncated_prefix_cannot_shrink_frozen_count(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"preflight";adm=Path(d)/"admission.json"
            with (patch.object(p,"SOURCE_ROOT",Path(d)),
                  patch.object(p,"PREFLIGHT_RECEIPTS",root),
                  patch.object(p,"ADMISSION",adm),
                  patch.object(p,"NATIVE_CUSTODY",None),
                  patch.object(p,"NATIVE_OBSERVATION_SEQ",0)):
                self.make_native_manifest_fixture(root,adm)
                for n in range(2,12):
                    for kind in ("intent","start","terminal"):
                        (root/f"native_{n:02d}_{kind}.json").unlink()
                manifest_path=root/"native_manifest.json"
                manifest=json.loads(manifest_path.read_text())
                manifest["native_count"]=1;manifest["children"]=manifest["children"][:1]
                manifest_path.write_text(json.dumps(manifest)+"\n")
                prior_path=root/"terminal.json";prior=json.loads(prior_path.read_text())
                prior["native_count"]=1
                prior["manifest_sha256"]=p.sha(manifest_path.read_bytes())
                prior_path.write_text(json.dumps(prior)+"\n")
                with self.assertRaisesRegex(RuntimeError,"PREFLIGHT_NATIVE_COUNT_NOT_FIXED"):
                    p.verify_prior_preflight()

    def test_unlisted_command_cannot_spawn(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"preflight"
            allowed=[sys.executable,"-c","print('approved')"]
            other=[sys.executable,"-c","print('unauthorized')"]
            with (patch.object(p,"SOURCE_ROOT",Path(d)),
                  patch.object(p,"NATIVE_CUSTODY",None),
                  patch.object(p,"NATIVE_OBSERVATION_SEQ",0),
                  patch.object(p,"expected_preflight_argv",return_value=[allowed]*11),
                  patch.object(p.subprocess,"Popen") as child):
                p.begin_native_custody(root,"PREFLIGHT")
                with self.assertRaisesRegex(RuntimeError,"NATIVE_COMMAND_NOT_IN_FROZEN_ORDER"):
                    p.read_output(other)
                child.assert_not_called()


if __name__=='__main__':unittest.main()
