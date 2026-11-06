"""Compare exact Python canonical bytes to independent Node22 golden vectors."""
from __future__ import annotations

import hashlib
import json
import pathlib
import unittest

from ts_detstate.core import Rejected, canonical, digest


FIXTURE = pathlib.Path(__file__).with_name("canonical-vectors.json")


class CanonicalVectorsTests(unittest.TestCase):
    def test_python_matches_all_frozen_vectors(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(fixture["schema"], "ts-detfirst-canonical-v0-vectors")
        self.assertEqual(len(fixture["cases"]), 5)
        for case in fixture["cases"]:
            with self.subTest(name=case["name"]):
                encoded = canonical(case["value"])
                self.assertEqual(encoded, case["canonical"])
                self.assertEqual(hashlib.sha256(encoded.encode("utf-8")).hexdigest(), case["sha256"])
                self.assertEqual(digest(case["value"]), case["sha256"])

    def test_nonascii_keys_rejected_before_hash(self):
        for key in ("é", "😀", "a b", "__proto__", "constructor", ""):
            with self.subTest(key=key):
                with self.assertRaisesRegex(Rejected, "JSON_UNSAFE_KEY"):
                    canonical({key: "value"})

    def test_limits_are_not_silently_rounded(self):
        for n in (9007199254740992, -9007199254740992):
            with self.subTest(n=n):
                with self.assertRaisesRegex(Rejected, "JSON_INTEGER_RANGE"):
                    canonical({"counter": n})


if __name__ == "__main__":
    unittest.main()
