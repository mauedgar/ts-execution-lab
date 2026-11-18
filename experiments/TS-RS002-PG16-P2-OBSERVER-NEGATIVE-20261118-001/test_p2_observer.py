"""No-Docker, no-secret synthetic checks of frozen P2 observer behavior."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import p2_observer as p


class P2SourceContractTests(unittest.TestCase):
    def test_exact_host_container_and_prior_C(self):
        self.assertEqual(p.CID, "5ce2b0833fa7ab04eac1b0c78e51ead0ed7c5e1dc2aede5621dba397b3c20d88")
        self.assertEqual(p.C_SHA, "7aef5dff689e1ceb5575084f2445caf25116cff5a22917815400693d99316852")
        self.assertEqual(p.RUNNER_ID, "TS-RS002-P2-OBSERVER-20261118-001")

    def test_known_no_shell_on_host(self):
        argv = p.cmd_for(p.POSITIVE, True)
        self.assertEqual(argv[:6], [p.DOCKER, "exec", "--user", "postgres", p.CID, "sh"])
        self.assertEqual(argv[-1], p.POSITIVE)
        self.assertNotIn("PGPASSWORD=", " ".join(argv[:5]))
        self.assertIn("cat /run/secrets/observer.pass", argv[7])
        self.assertNotIn("password", p.POSITIVE.lower())
        self.assertEqual(p.cmd_for(p.SNAPSHOT, False)[5], "psql")

    def test_real_TCP_credential_binding(self):
        self.assertIn("-h 127.0.0.1", p.OBSERVER_WRAPPER)
        self.assertIn("-U ts_rs002_observer", p.OBSERVER_WRAPPER)
        self.assertIn("export PGPASSWORD", p.OBSERVER_WRAPPER)
        self.assertIn("auth_method='scram-sha-256'", p.HBA)

    def test_positive_sql_has_explicit_read_only(self):
        self.assertIn("REPEATABLE READ READ ONLY", p.POSITIVE)
        self.assertIn("session_user,current_user", p.POSITIVE)
        self.assertEqual(p.interpret("observer_read", 0,
            "ts_rs002_observer|ts_rs002_observer|ts_rs002_a02_lab|on|on\n9\n", "", None),
            ["ts_rs002_observer|ts_rs002_observer|ts_rs002_a02_lab|on|on", "9"])

    def test_observer_wrong_identity_blocked(self):
        with self.assertRaisesRegex(RuntimeError, "OBSERVER_TCP_READ_NOT_PROVEN"):
            p.interpret("observer_read", 0, "ts_rs002_admin|ts_rs002_admin|ts_rs002_a02_lab|on|on\n0", "", None)

    def test_hba_scram_accept_and_denial(self):
        self.assertEqual(p.interpret("hba", 0, "0|2|0", "", None), ["0|2|0"])
        for row in ("1|2|0", "0|0|0", "0|2|1", "some invalid string"):
            with self.subTest(row=row), self.assertRaisesRegex(RuntimeError, "HOST_SCRAM_HBA_NOT_ATTESTED"):
                p.interpret("hba", 0, row, "", None)

    def test_snapshot_match_and_drift_block(self):
        before = p.interpret("snapshot_before", 0, "1|2|3", "", None)
        self.assertEqual(p.interpret("snapshot_after", 0, "1|2|3", "", before), before)
        with self.assertRaisesRegex(RuntimeError, "SCHEMA_ROWS_CHANGED"):
            p.interpret("snapshot_after", 0, "2|2|3", "", before)

    def test_delete_only_no_rows_and_rollback(self):
        self.assertIn("READ WRITE", p.DENY_DELETE)
        self.assertIn("WHERE FALSE", p.DENY_DELETE)
        self.assertIn("ROLLBACK;", p.DENY_DELETE)
        self.assertEqual(p.interpret("deny_delete", 3, "", "ERROR: permission denied for table head", None),
                         ["ERROR: permission denied for table head"])
        with self.assertRaisesRegex(RuntimeError, "OBSERVER_NEGATIVE_FAILED_DENY_DELETE"):
            p.interpret("deny_delete", 0, "DELETE 0", "", None)

    def test_readonly_does_not_mask_acl_probe(self):
        with self.assertRaisesRegex(RuntimeError, "OBSERVER_NEGATIVE_FAILED_DENY_DELETE"):
            p.interpret("deny_delete", 3, "", "ERROR: cannot execute DELETE in a read-only transaction", None)

    def test_temp_denial_and_safe_rollback(self):
        self.assertIn("CREATE TEMP TABLE", p.DENY_TEMP)
        self.assertIn("ROLLBACK;", p.DENY_TEMP)
        self.assertEqual(p.interpret("deny_temp", 3, "", "ERROR: permission denied to create temporary tables", None),
                         ["ERROR: permission denied to create temporary tables"])
        with self.assertRaisesRegex(RuntimeError, "OBSERVER_NEGATIVE_FAILED_DENY_TEMP"):
            p.interpret("deny_temp", 0, "", "", None)

    def test_role_escalation_denied(self):
        self.assertIn("SET ROLE ts_rs002_owner", p.DENY_ROLE)
        self.assertEqual(p.interpret("deny_role", 3, "", "ERROR: permission denied to set role", None),
                         ["ERROR: permission denied to set role"])
        with self.assertRaisesRegex(RuntimeError, "OBSERVER_NEGATIVE_FAILED_DENY_ROLE"):
            p.interpret("deny_role", 0, "", "", None)

    def test_no_dynamic_sql_and_frozen_step_order(self):
        self.assertEqual(tuple(s[0] for s in p.STEPS),
            ("hba", "snapshot_before", "observer_read", "deny_delete", "deny_temp", "deny_role", "snapshot_after"))
        for _,sql,_ in p.STEPS:
            self.assertTrue(sql.endswith("COMMIT;") or sql.endswith("ROLLBACK;"))
        self.assertNotIn("PGPASSWORD", " ".join(x[1] for x in p.STEPS))


if __name__ == "__main__":
    unittest.main()
