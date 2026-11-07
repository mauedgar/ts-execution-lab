"""A005: Product ISO timestamp predicate versus conservative Python V0 mirror.

This exercises native Node Date behavior, not Zod integration; pinned Zod 4.6.7
regex source permits year 0000. Full Product runtime differential remains OPEN.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import unittest

from ts_global import legacy_v0

SCRIPT = Path(__file__).parent.parent / "oracle" / "js_iso_parity.cjs"
SAMPLES = [
    "0000-01-01T00:00:00.000Z",
    "0000-02-29T23:59:59.999Z",
    "0000-02-30T00:00:00.000Z",
    "0000-03-01T00:00:00.000Z",
    "0001-01-01T00:00:00.000Z",
    "0100-01-01T00:00:00.000Z",
    "1900-02-29T00:00:00.000Z",
    "2000-02-29T00:00:00.000Z",
    "2026-11-07T23:59:59.000Z",
    "2026-11-07T24:00:00.000Z",
    "2026-11-07T23:60:00.000Z",
    "2026-11-07T23:59:60.000Z",
    "2026-02-29T00:00:00.000Z",
    "2024-02-29T00:00:00.000Z",
    "9999-12-31T23:59:59.999Z",
    "2026-11-07T00:00:00.000+00:00",
    "2026-11-07T00:00:00Z",
    "2026-11-07T00:00:00.000z",
    "٢٠٢٦-11-07T00:00:00.000Z",
]


class IsoParityTests(unittest.TestCase):
    def test_python_expected_timestamp_boundaries(self):
        expected = {0: True, 1: True, 2: False, 6: False, 7: True,
                    9: False, 10: False, 11: False, 12: False, 13: True,
                    15: False, 16: False, 17: False, 18: False}
        for i, outcome in expected.items():
            with self.subTest(date=SAMPLES[i]):
                self.assertIs(legacy_v0.iso(SAMPLES[i]), outcome)

    @unittest.skipUnless(shutil.which("node"), "Native Node unavailable")
    def test_js_date_toiso_predicate_matches_python_on_canonical_subset(self):
        result = subprocess.run(
            ["node", str(SCRIPT)], input=json.dumps(SAMPLES),
            capture_output=True, text=True, check=True, timeout=15,
        )
        js = json.loads(result.stdout)
        self.assertEqual([item["input"] for item in js], SAMPLES)
        for item in js:
            with self.subTest(date=item["input"]):
                self.assertIs(legacy_v0.iso(item["input"]), item["valid"])


if __name__ == "__main__":
    unittest.main()
