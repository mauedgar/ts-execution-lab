"""B004 actual Playwright negative fault qualifications, not Product/browser certification.

Each case uses a new isolated local HTTP server and Playwright context; no remote
requests escape: external-success fault is satisfied by route.fulfill, not network.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

BASE=Path(__file__).resolve().parents[2]
SCRIPT=BASE/"TS-EE-E2-BROWSER-QA-20261119-001"/"e2_browser_qa.py"
ROOT=Path("e2-fault-evidence")

class BrowserNegativeFaults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if ROOT.exists():
            raise RuntimeError("BLOCKED_EXISTING_RUNTIME_FAULT_RESULTS")
        ROOT.mkdir(parents=True)

    def run_fault(self,mode,expected_exit):
        output=ROOT/mode
        env=dict(os.environ,TS_EE_E2_FAULT=mode)
        proc=subprocess.run(
            [sys.executable,str(SCRIPT),"--output",str(output)],
            cwd=Path.cwd(),env=env,capture_output=True,text=True,
            timeout=90,check=False
        )
        (ROOT/(mode+".stdout.txt")).write_text(proc.stdout,encoding="utf8")
        (ROOT/(mode+".stderr.txt")).write_text(proc.stderr,encoding="utf8")
        self.assertEqual(proc.returncode,expected_exit,
                         (mode,proc.stdout[-1200:],proc.stderr[-1200:]))
        return output,proc

    def test_keyboard_positive_enter_blocked_detected(self):
        p,_=self.run_fault("keyboard_block_positive",1)
        receipt=json.loads((p/"RESULT.json").read_text())
        self.assertIs(receipt["pass"],False)
        self.assertIn("KEYBOARD_ACTIVATION",receipt["variants"]["good"]["detected"])
        self.assertIn("KEYBOARD_ACTIVATION",receipt["variants"]["bad"]["detected"])
        self.assertEqual(len(receipt["variants"]["good"]["rows"]),4)
        self.assertFalse((p/"TERMINAL_FAILURE.json").exists())

    def test_external_success_simulated_locally_detected(self):
        p,_=self.run_fault("external_fulfill_simulated",1)
        receipt=json.loads((p/"RESULT.json").read_text())
        self.assertIs(receipt["pass"],False)
        self.assertIn("EXTERNAL_NOT_BLOCKED",receipt["variants"]["good"]["detected"])
        self.assertIn("EXTERNAL_NOT_BLOCKED",receipt["variants"]["bad"]["detected"])
        self.assertTrue(all(row["external_navigation_rejected"] is False
                            for row in receipt["variants"]["good"]["rows"]))
        for variant in ("good","bad"):
            for row in receipt["variants"][variant]["rows"]:
                self.assertIs(row["external_fulfill_returned"],True)
                self.assertEqual(row["external_response_status"],200)
                self.assertTrue(row["external_fault_injection_proven"])
                self.assertIn("https://wa.me/",row["external_navigation_final_url"])
            self.assertNotIn("FAULT_INJECTION_UNPROVEN",
                             receipt["variants"][variant]["detected"])
        self.assertFalse((p/"TERMINAL_FAILURE.json").exists())

    def test_unexpected_runtime_exception_generates_terminal_failure(self):
        p,proc=self.run_fault("runtime_exception",2)
        self.assertTrue((p/"TERMINAL_FAILURE.json").is_file())
        self.assertFalse((p/"RESULT.json").exists())
        receipt=json.loads((p/"TERMINAL_FAILURE.json").read_text())
        self.assertEqual(receipt["status"],"FAIL")
        self.assertEqual(receipt["exception_type"],"RuntimeError")
        self.assertEqual(receipt["reason_code"],"SYNTHETIC_RUNTIME_EXCEPTION")
        self.assertFalse(receipt["provider_native_verified"])
        self.assertEqual(receipt["source_sha256"],
                         hashlib.sha256(SCRIPT.read_bytes()).hexdigest())
        self.assertIn('"failure_receipt_created": true',proc.stdout.lower())

if __name__=="__main__":
    unittest.main()
