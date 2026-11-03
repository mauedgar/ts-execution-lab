"""Strict allowlist for a public Sigstore demo. No real operational/customer input."""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
FILE = ROOT / "PUBLIC_SYNTHETIC_PROBE.json"
EXPECTED_BYTES = (
    b'{"schema":"TS_047B_PUBLIC_SYNTHETIC_PROBE_V1","mode":"TEST_ONLY",'
    b'"authority":"NONE","allowEffects":false,"dataClass":"PUBLIC_SYNTHETIC",'
    b'"payload":"CONSTANT_PUBLIC_VECTOR_NOT_CUSTOMER_DATA"}\n'
)
EXPECTED_KEYS = frozenset({
    "schema", "mode", "authority", "allowEffects", "dataClass", "payload"
})


class PublicFixtureContract(unittest.TestCase):
    def test_exact_bytes_only(self):
        self.assertEqual(FILE.read_bytes(), EXPECTED_BYTES)

    def test_canonical_no_dynamic_input(self):
        self.assertTrue(EXPECTED_BYTES.endswith(b"\n"))
        self.assertEqual(EXPECTED_BYTES.count(b"\n"), 1)
        self.assertNotIn(b"\r", EXPECTED_BYTES)

    def test_exact_public_schema(self):
        value = json.loads(EXPECTED_BYTES)
        self.assertEqual(set(value), EXPECTED_KEYS)
        self.assertEqual(value["dataClass"], "PUBLIC_SYNTHETIC")

    def test_explicit_non_authorizing(self):
        value = json.loads(EXPECTED_BYTES)
        self.assertEqual(value["mode"], "TEST_ONLY")
        self.assertEqual(value["authority"], "NONE")
        self.assertIs(value["allowEffects"], False)

    def test_constant_test_payload(self):
        value = json.loads(EXPECTED_BYTES)
        self.assertEqual(value["payload"], "CONSTANT_PUBLIC_VECTOR_NOT_CUSTOMER_DATA")

    def test_modified_fixture_rejected(self):
        modified = EXPECTED_BYTES.replace(b"TEST_ONLY", b"LIVE_RUN__")
        self.assertNotEqual(modified, EXPECTED_BYTES)

    def test_no_external_identifiers_or_dynamic_fields(self):
        value = json.loads(EXPECTED_BYTES)
        self.assertTrue(EXPECTED_KEYS.isdisjoint({
            "email", "name", "userId", "customerId", "tenantId", "payloadHash",
            "secret", "token", "address", "sourceUrl", "executionAttempt",
            "providerReceipt", "patientId", "personalData",
        }))


if __name__ == "__main__":
    unittest.main()
