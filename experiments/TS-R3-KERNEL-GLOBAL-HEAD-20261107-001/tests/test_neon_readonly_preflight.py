"""A001 safe DSN metadata validation tests; strictly no network or credentials."""
from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "runners" / "neon_readonly_preflight.py"
SPEC = importlib.util.spec_from_file_location("a001_readonly_preflight", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class NeonMetadataPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = (
            "postgresql://tsr3_host_a_rw:"
            "encoded%40with%3Acolons%2Fslash%25percent@"
            "ep-lucky-waterfall-b6244mdy.c-2.sa-east-1.aws.neon.tech/"
            "ts_remote_r3"
        )
        self.good = self.base + "?sslmode=require&channel_binding=require"

    def test_valid_pinned_metadata_and_encoded_password(self) -> None:
        mod.validate_dsn(self.good)
        mod.validate_dsn(
            self.base + "?sslmode=verify-full&channel_binding=require")
        mod.validate_dsn(
            self.base + "?sslmode=verify-ca&channel_binding=require")

    def test_missing_channel_binding_is_never_defaulted(self) -> None:
        for suffix in (
            "?sslmode=require", "?sslmode=verify-ca",
            "?sslmode=verify-full", "?sslmode=require&channel_binding=",
            "?sslmode=require&channel_binding=prefer",
            "?sslmode=require&channel_binding=disable",
            "?sslmode=require&channel_binding=verify",
            "?sslmode=require&channel_binding=require&channel_binding=prefer",
        ):
            with self.subTest(suffix=suffix):
                with self.assertRaises((mod.BlockedPrecondition, ValueError)):
                    mod.validate_dsn(self.base + suffix)

    def test_rejects_unknown_or_downgraded_transport(self) -> None:
        for suffix in (
            "?sslmode=disable&channel_binding=require",
            "?sslmode=allow&channel_binding=require",
            "?sslmode=prefer&channel_binding=require",
            "?sslmode=require&sslmode=disable&channel_binding=require",
            "?sslmode=require&channel_binding=require&options=superuser",
            "?sslmode=require&channel_binding=require&host=other",
            "?sslmode=require&channel_binding=require&sslnegotiation=direct",
            "?sslmode=require&channel_binding=require&connect_timeout=60",
            "?sslmode=require&channel_binding=require&application_name=other",
        ):
            with self.subTest(suffix=suffix):
                with self.assertRaises((mod.BlockedPrecondition, ValueError)):
                    mod.validate_dsn(self.base + suffix)

    def test_rejects_wrong_host_role_database_pooler_or_port(self) -> None:
        forbidden = (
            self.good.replace("tsr3_host_a_rw", "tsr3_owner", 1),
            self.good.replace("ts_remote_r3", "postgres", 1),
            self.good.replace("ep-lucky-waterfall-", "ep-other-waterfall-", 1),
            self.good.replace(".c-2.sa-east-1", "-pooler.c-2.sa-east-1", 1),
            self.good.replace(".neon.tech/", ".neon.tech:6432/", 1),
            self.good.replace("postgresql://", "postgres://", 1),
        )
        for case in forbidden:
            with self.subTest(case="bad metadata"):
                with self.assertRaises((mod.BlockedPrecondition, ValueError)):
                    mod.validate_dsn(case)

    def test_rejects_broken_percent_escape_nul_and_missing_password(self) -> None:
        for passpart in ("broken%escape", "%", "%0", "%GG", "%00", ""):
            candidate = self.good.replace(
                "encoded%40with%3Acolons%2Fslash%25percent", passpart)
            with self.subTest(password_format=passpart):
                with self.assertRaises((mod.BlockedPrecondition, ValueError)):
                    mod.validate_dsn(candidate)

    def test_secret_never_appears_in_rejection(self) -> None:
        secret = "PRIVATE_NEVER_PRINT_THIS_DSN_PASSWORD"
        invalid = self.good.replace(
            "encoded%40with%3Acolons%2Fslash%25percent", secret
        ).replace("ep-lucky-waterfall-", "ep-mismatched-waterfall-", 1)
        with self.assertRaises(mod.BlockedPrecondition) as cm:
            mod.validate_dsn(invalid)
        self.assertNotIn(secret, str(cm.exception))

    def test_selftest_and_unknown_argument_without_network(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(mod.main(["--self-test"]), 0)
        self.assertIn("PASS_DSN_METADATA_SELFTEST", out.getvalue())
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(mod.main(["--not-approved"]), 2)
        self.assertIn("BLOCKED_UNEXPECTED_ARGUMENTS", out.getvalue())

    def test_no_secret_fails_closed_without_importing_psycopg(self) -> None:
        out = io.StringIO()
        with mock.patch.dict(mod.os.environ, {mod.SECRET_ENV: ""}):
            with redirect_stdout(out):
                self.assertEqual(mod.main([]), 2)
        self.assertIn("BLOCKED_PRECONDITION", out.getvalue())
        self.assertNotIn("tsr3_host_a_rw:", out.getvalue())


if __name__ == "__main__":
    unittest.main()
