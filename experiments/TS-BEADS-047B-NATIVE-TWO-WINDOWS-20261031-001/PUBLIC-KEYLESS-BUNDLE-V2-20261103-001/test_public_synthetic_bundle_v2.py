"""Permit a single fixed PUBLIC_SYNTHETIC fixture, never operational input."""
import json
from pathlib import Path
import unittest

FILE = Path(__file__).resolve().parent / "PUBLIC_SYNTHETIC_BUNDLE_V2.json"
EXPECTED = (
    b'{"schema":"TS_047B_PUBLIC_KEYLESS_V2","mode":"TEST_ONLY",'
    b'"authority":"NONE","allowEffects":false,"dataClass":"PUBLIC_SYNTHETIC",'
    b'"payload":"SECOND_FIXED_PUBLIC_ONLY_VECTOR_NO_CLIENT_DATA",'
    b'"purpose":"PORTABLE_BUNDLE_PRESERVATION"}\n'
)
ORIGINAL = (
    b'{"schema":"TS_047B_PUBLIC_SYNTHETIC_PROBE_V1","mode":"TEST_ONLY",'
    b'"authority":"NONE","allowEffects":false,"dataClass":"PUBLIC_SYNTHETIC",'
    b'"payload":"CONSTANT_PUBLIC_VECTOR_NOT_CUSTOMER_DATA"}\n'
)

class PublicSubject(unittest.TestCase):
    def test_exact_payload(self):
        self.assertEqual(FILE.read_bytes(), EXPECTED)
    def test_distinct_subject(self):
        self.assertNotEqual(EXPECTED, ORIGINAL)
    def test_no_dynamic_identity(self):
        value = json.loads(EXPECTED)
        self.assertEqual(set(value), {
            "schema", "mode", "authority", "allowEffects", "dataClass", "payload", "purpose"
        })
    def test_no_authority(self):
        value = json.loads(EXPECTED)
        self.assertEqual(value["authority"], "NONE")
        self.assertFalse(value["allowEffects"])
        self.assertEqual(value["mode"], "TEST_ONLY")
    def test_public_only(self):
        value = json.loads(EXPECTED)
        self.assertEqual(value["dataClass"], "PUBLIC_SYNTHETIC")
        self.assertEqual(value["payload"], "SECOND_FIXED_PUBLIC_ONLY_VECTOR_NO_CLIENT_DATA")
        self.assertEqual(value["purpose"], "PORTABLE_BUNDLE_PRESERVATION")
    def test_line_endings(self):
        self.assertTrue(EXPECTED.endswith(b"\n"))
        self.assertEqual(EXPECTED.count(b"\n"), 1)
        self.assertNotIn(b"\r", EXPECTED)
    def test_tampering_changes_bytes(self):
        self.assertNotEqual(EXPECTED.replace(b'"TEST_ONLY"', b'"TAMPERED_"'), EXPECTED)

if __name__ == "__main__":
    unittest.main()
