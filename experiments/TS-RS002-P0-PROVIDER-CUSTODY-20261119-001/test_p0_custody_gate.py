"""Adversarial negative and no-dispatch synthetic tests for the P0 source-only gate."""
from dataclasses import replace
import unittest
import p0_custody_gate as p


SHA = "a" * 64


def fixture():
    ids = {"metadata": "native-req-meta-001", "identity": "native-req-identity-001", "denial": "native-req-denial-001"}
    f = p.Frozen(p.ATTEMPT, p.HOST, p.DISTRO, p.TERMINAL, p.INCARNATION, SHA, ids)
    meta = (
        p.StatEntry(p.ROOT_PATH, "directory", 1000, 0o700, 10, 1, 2, False),
        p.StatEntry(p.TARGET_PARENT, "directory", 1000, 0o700, 11, 1, 2, False),
        p.StatEntry(p.SECRET_PATH, "regular", 1000, 0o600, 12, 1, 1, False),
    )
    items = {}
    for index, name in enumerate(("metadata", "identity", "denial")):
        argv = () if name == "metadata" else p.expected_argv(name)
        items[name] = p.NativeReceipt(
            stage=name, request_id=ids[name], attempt=p.ATTEMPT, provider=p.NATIVE_PROVIDER,
            provider_original_ref=f"provider-original-{name}-001", provider_original_sha256=SHA,
            host=p.HOST, distro=p.DISTRO, terminal=p.TERMINAL, incarnation=p.INCARNATION,
            adapter_sha256=SHA, argv=argv, argv_sha256=p.digest(list(argv)),
            native_windows_pid=100 + index, linux_pid=200 + index,
            linux_pid_namespace="wsl-native-namespace-001", linux_uid=1000 if name == "metadata" else 65534,
            native_completed=True, exit_code=1 if name == "denial" else 0,
            stdout="65534\n" if name == "identity" else "", metadata=meta if name == "metadata" else (),
        )
    return f, items


class GateTests(unittest.TestCase):
    def assert_reject(self, items=None, frozen=None):
        f, r = fixture()
        with self.assertRaises(p.BlockedPrecondition):
            p.evaluate_untrusted_originals(f if frozen is None else frozen, r if items is None else items)

    def test_synthetic_consistent_is_explicitly_untrusted(self):
        f, r = fixture()
        self.assertEqual(p.evaluate_untrusted_originals(f, r), "SOURCE_FIELDS_CONSISTENT_UNTRUSTED_NO_DISPATCH")

    def test_provider_preflight_never_calls_unqualified_provider(self):
        f, _ = fixture()
        class Trap:
            def read_original(self, key):
                raise AssertionError("MUST_NOT_CALL_PROVIDER")
        with self.assertRaisesRegex(p.BlockedPrecondition, "CUSTODY_NOT_QUALIFIED"):
            p.qualify_provider_and_physical(f, Trap())

    def test_denial_on_nonexistent_path_not_pass(self):
        _, r = fixture()
        r["metadata"] = replace(r["metadata"], metadata=r["metadata"].metadata[:2])
        self.assert_reject(r)

    def test_secret_symlink_rejected(self):
        _, r = fixture()
        m = r["metadata"].metadata
        r["metadata"] = replace(r["metadata"], metadata=(*m[:2], replace(m[2], is_symlink=True)))
        self.assert_reject(r)

    def test_secret_insecure_mode_rejected(self):
        _, r = fixture()
        m = r["metadata"].metadata
        r["metadata"] = replace(r["metadata"], metadata=(*m[:2], replace(m[2], mode=0o644)))
        self.assert_reject(r)

    def test_secret_nonregular_rejected(self):
        _, r = fixture()
        m = r["metadata"].metadata
        r["metadata"] = replace(r["metadata"], metadata=(*m[:2], replace(m[2], kind="directory")))
        self.assert_reject(r)

    def test_parent_insecure_rejected(self):
        _, r = fixture()
        m = r["metadata"].metadata
        r["metadata"] = replace(r["metadata"], metadata=(replace(m[0], mode=0o755), *m[1:]))
        self.assert_reject(r)

    def test_wrong_secret_owner_rejected(self):
        _, r = fixture()
        m = r["metadata"].metadata
        r["metadata"] = replace(r["metadata"], metadata=(*m[:2], replace(m[2], uid=0)))
        self.assert_reject(r)

    def test_duplicate_request_ids_rejected(self):
        f, _ = fixture()
        ids = dict(f.request_ids); ids["denial"] = ids["identity"]
        self.assert_reject(frozen=replace(f, request_ids=ids))

    def test_missing_original_rejected(self):
        _, r = fixture(); del r["metadata"]
        self.assert_reject(r)

    def test_reused_provider_receipt_reference_rejected(self):
        _, r = fixture()
        r["denial"] = replace(r["denial"], provider_original_ref=r["identity"].provider_original_ref)
        self.assert_reject(r)

    def test_stale_terminal_incarnation_rejected(self):
        _, r = fixture()
        r["denial"] = replace(r["denial"], incarnation="stale-incarnation-001")
        self.assert_reject(r)

    def test_spoofed_uid_output_rejected(self):
        _, r = fixture()
        r["identity"] = replace(r["identity"], linux_uid=1000)
        self.assert_reject(r)

    def test_exit_one_from_wrong_user_rejected(self):
        _, r = fixture()
        r["denial"] = replace(r["denial"], linux_uid=1000)
        self.assert_reject(r)

    def test_native_send_ack_without_completion_rejected(self):
        _, r = fixture()
        r["denial"] = replace(r["denial"], native_completed=False)
        self.assert_reject(r)

    def test_windows_pid_cannot_stand_in_for_missing_linux_pid(self):
        _, r = fixture()
        r["denial"] = replace(r["denial"], linux_pid=0)
        self.assert_reject(r)

    def test_unqualified_linux_namespace_rejected(self):
        _, r = fixture()
        r["denial"] = replace(r["denial"], linux_pid_namespace="")
        self.assert_reject(r)

    def test_wrong_argv_even_with_matching_digest_rejected(self):
        _, r = fixture()
        new = (*r["denial"].argv[:-1], "/tmp/nonexistent-file")
        r["denial"] = replace(r["denial"], argv=new, argv_sha256=p.digest(list(new)))
        self.assert_reject(r)

    def test_forged_digest_rejected(self):
        _, r = fixture()
        r["identity"] = replace(r["identity"], argv_sha256="b" * 64)
        self.assert_reject(r)

    def test_exit_zero_readable_secret_is_failure(self):
        _, r = fixture()
        r["denial"] = replace(r["denial"], exit_code=0)
        self.assert_reject(r)

    def test_crash_or_missing_terminal_exit_rejected(self):
        _, r = fixture()
        r["denial"] = replace(r["denial"], exit_code=None)
        self.assert_reject(r)

    def test_stdout_leak_rejected(self):
        _, r = fixture()
        r["denial"] = replace(r["denial"], stdout="secret-token")
        self.assert_reject(r)

    def test_tampered_adapter_hash_rejected(self):
        _, r = fixture()
        r["denial"] = replace(r["denial"], adapter_sha256="b" * 64)
        self.assert_reject(r)

    def test_changed_path_order_rejected(self):
        _, r = fixture()
        r["metadata"] = replace(r["metadata"], metadata=tuple(reversed(r["metadata"].metadata)))
        self.assert_reject(r)

    def test_duplicate_linux_pid_rejected(self):
        _, r = fixture()
        r["denial"] = replace(r["denial"], linux_pid=r["identity"].linux_pid)
        self.assert_reject(r)

    def test_extra_original_is_not_silently_ignored(self):
        _, r = fixture(); r["unknown"] = r["denial"]
        self.assert_reject(r)

    def test_no_qualified_metadata_argv(self):
        with self.assertRaisesRegex(p.BlockedPrecondition, "NOT_QUALIFIED"):
            p.expected_argv("metadata")


if __name__ == "__main__":
    unittest.main()
