"""A005: exact well-formed ECMAScript JSON.stringify surrogate parity.

These are bounded synthetic native Node 22 vs Python source differential
tests, not execution of Tecnotron Product JS/Zod and not a Product grant.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import unittest

from ts_global import legacy_v0

ORACLE = Path(__file__).parent.parent / "oracle" / "js_surrogate_parity.cjs"
SAMPLES = (
    r'{"title":"\ud800"}',
    r'{"title":"\udc00"}',
    r'{"title":"\ud83d\ude00"}',
    r'{"title":"hello \ud800 world"}',
    r'{"title":"\ud83d\ude00\ud800"}',
    r'{"title":"\u2028/\u2029"}',
    r'{"10":"\ud800","2":"\udc00","4294967295":"outside"}',
    r'{"a":"\ud800","b":"\\ud800"}',
    r'{"emoji":"\ud83d\udc9a"}',
    r'{"title":"\ud800\udc00"}',
    r'{"\ud800":"\udc00"}',
)


class JsonSurrogateParityTests(unittest.TestCase):
    def test_01_exact_unpaired_and_paired_utf16_output(self):
        raw = legacy_v0.exact_js_event_payload({"title": "\ud800"})
        self.assertEqual(raw, b'{"title":"\\ud800"}')
        paired = legacy_v0.exact_js_event_payload(
            {"title": "\ud83d\ude00"}
        )
        self.assertEqual(paired, '{"title":"😀"}'.encode("utf-8"))
        self.assertEqual(
            legacy_v0.exact_js_event_payload({"title": "😀"}), paired
        )

    def test_02_existing_string_escape_is_not_double_interpreted(self):
        self.assertEqual(
            legacy_v0.exact_js_event_payload({"title": "\\ud800"}),
            b'{"title":"\\\\ud800"}',
        )

    def test_03_malformed_keys_cannot_silently_collide(self):
        with self.assertRaisesRegex(ValueError, "PRODUCT_V0_ENCODING_UNSUPPORTED"):
            legacy_v0.exact_js_event_payload(
                {"😀": 1, "\ud83d\ude00": 2}
            )

    @unittest.skipUnless(shutil.which("node"), "Native Node unavailable")
    def test_04_node_bytes_equal_python_for_compact_and_pretty(self):
        observed = subprocess.run(
            ["node", str(ORACLE)],
            input=json.dumps(SAMPLES),
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        )
        rows = json.loads(observed.stdout)
        self.assertEqual(len(rows), len(SAMPLES))
        for sample, pair in zip(SAMPLES, rows, strict=True):
            with self.subTest(sample=sample):
                payload = json.loads(sample)
                self.assertEqual(
                    legacy_v0.exact_js_event_payload(payload).hex(),
                    pair["compact_hex"],
                )
                self.assertEqual(
                    legacy_v0.exact_js_snapshot(payload).hex(),
                    pair["pretty_hex"],
                )


if __name__ == "__main__":
    unittest.main()
