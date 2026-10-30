#!/usr/bin/env python3
"""Independent six-case native-process crash/ACK-loss acceptance runner."""
import json,os,pathlib,subprocess,sys,unittest
LAB=pathlib.Path(os.environ['LAB046_ROOT']).resolve()
APP=pathlib.Path(os.environ['LAB046_SCRIPT']).resolve()
class NativeCrashTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):LAB.mkdir(parents=True,exist_ok=False)
    def setUp(self):
        self.root=LAB/self._testMethodName
        self.key=('--attempt',self._testMethodName,'--subject','synthetic@frozen046','--owner','TS_EE_046')
        self.call('init');self.call('intent',*self.key)
    def call(self,op,*args,expect=0):
        p=subprocess.run([sys.executable,str(APP),op,'--root',str(self.root),*args],
                         text=True,capture_output=True,timeout=20)
        self.assertEqual(p.returncode,expect,(op,p.stdout,p.stderr))
        if expect in (73,74):
            self.assertEqual(p.stdout,'')
            return None
        return json.loads(p.stdout.strip().splitlines()[-1])
    def inspect(self):
        x=self.call('inspect')
        self.assertEqual(x['integrity'],['ok','ok'])
        return x
    def test_01_commit_survives_actual_process_crash_before_ack(self):
        self.call('apply',*self.key,'--fault','after_commit_before_ack',expect=73)
        self.assertEqual(self.call('reconcile',*self.key,'--provider-available','no')['phase'],'RECONCILE_UNKNOWN')
        receipt=self.call('probe',*self.key)
        self.assertEqual(receipt['phase'],'PROVIDER_CONFIRMED')
        self.assertEqual(receipt['units'],1)
        x=self.call('reconcile',*self.key)
        self.assertEqual(x['phase'],'NO_RETRY_CONFIRMED')
        self.assertEqual(x['receipt'],receipt['receipt'])
        data=self.inspect()
        self.assertEqual(len(data['effects']),1)
        self.assertEqual(data['effects'][0][4],1)
        self.assertEqual([r[4] for r in data['journal']],['INTENT','RECONCILE_UNKNOWN','NO_RETRY_CONFIRMED'])
    def test_02_crash_before_commit_never_authorizes_blind_retry(self):
        self.call('apply',*self.key,'--fault','before_commit',expect=74)
        self.assertEqual(self.call('reconcile',*self.key,'--provider-available','no')['phase'],'RECONCILE_UNKNOWN')
        self.assertEqual(self.call('probe',*self.key)['phase'],'PROVIDER_AUTHORITATIVE_ABSENT')
        self.assertEqual(self.call('reconcile',*self.key)['phase'],'ABSENT_REQUIRES_AUTHORITY')
        self.assertEqual(self.inspect()['effects'],[])
    def test_03_lost_client_ack_recovered_by_new_process(self):
        ack=self.call('apply',*self.key)
        self.assertEqual(ack['phase'],'APPLIED_ACK')
        # Deliberately do not save ACK in consumer journal; restart CLI.
        result=self.call('reconcile',*self.key)
        self.assertEqual(result['phase'],'NO_RETRY_CONFIRMED')
        self.assertEqual(result['receipt'],ack['receipt'])
        self.assertEqual(len(self.inspect()['effects']),1)
    def test_04_collision_of_owner_blocks_without_effect_duplication(self):
        ack=self.call('apply',*self.key)
        args=list(self.key);args[5]='DIFFERENT_OWNER'
        self.assertEqual(self.call('apply',*args,expect=77)['phase'],'BLOCK_IDENTITY')
        self.assertEqual(self.call('probe',*args)['phase'],'BLOCK_IDENTITY')
        self.assertEqual(self.call('reconcile',*args,expect=78)['phase'],'BLOCK_IDENTITY_OR_NO_INTENT')
        rows=self.inspect()['effects'];self.assertEqual(len(rows),1)
        self.assertEqual(rows[0][3],ack['receipt'])
    def test_05_injected_duplicate_request_idempotently_rejected(self):
        # Intentional adversarial duplicate submission, not blind retry after UNKNOWN.
        one=self.call('apply',*self.key);two=self.call('apply',*self.key)
        self.assertEqual((one['phase'],two['phase']),('APPLIED_ACK','ALREADY_CONFIRMED'))
        self.assertEqual(one['receipt'],two['receipt'])
        self.assertEqual(len(self.inspect()['effects']),1)
    def test_06_concurrent_workers_only_one_effect(self):
        cmd=[sys.executable,str(APP),'apply','--root',str(self.root),*self.key]
        a=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        b=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        got=[]
        for p in (a,b):
            out,err=p.communicate(timeout=20)
            self.assertEqual(p.returncode,0,err)
            got.append(json.loads(out))
        self.assertEqual(sorted(x['phase'] for x in got),['ALREADY_CONFIRMED','APPLIED_ACK'])
        self.assertEqual(got[0]['receipt'],got[1]['receipt'])
        self.assertEqual(len(self.inspect()['effects']),1)
if __name__=='__main__':
    out=pathlib.Path(os.environ['LAB046_RESULT']).resolve()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(NativeCrashTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    summary={'experiment':'TS-EE-LLM-046-CRASH-ACK-LOSS-20261030-001',
             'attempt':'TS-EE-LLM-046-ATTEMPT-001',
             'authority':'EXPERIMENTAL_CONTROL_ONLY','product_effect':'NONE',
             'provider':'SYNTHETIC_LOCAL_SQLITE_NOT_REMOTE',
             'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
             'success':result.wasSuccessful(),
             'scenario_directories':sorted(x.name for x in LAB.iterdir())}
    out.write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print('LLM046_TERMINAL='+('PASS_BOUNDED_NATIVE_CRASH_RECONCILIATION' if result.wasSuccessful() else 'FAIL_CLOSED')+';tests='+str(result.testsRun)+';failed='+str(len(result.failures)+len(result.errors))+';Product=NONE',flush=True)
    sys.exit(not result.wasSuccessful())
