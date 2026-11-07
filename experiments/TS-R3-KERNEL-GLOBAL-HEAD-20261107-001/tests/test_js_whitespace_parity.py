"""A005: deterministic JS/Python whitespace differential, offline/no DB.

This compares the EXACT Product contracts.js string() predicate with native
Node String.prototype.trim(), not the full Zod/state-kernel runtime.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import unittest

from ts_global import legacy_v0

ORACLE_BLOB = "5d2d3a8a24ebc17339675e0c801595956e0cd353"
SCRIPT = Path(__file__).parent.parent / "oracle" / "js_string_parity.cjs"
# All ECMAScript trim points plus Python-only whitespace and boundary cases.
CODEPOINTS = [
    0x0009, 0x000A, 0x000B, 0x000C, 0x000D, 0x001C, 0x001D,
    0x001E, 0x001F, 0x0020, 0x0041, 0x0085, 0x00A0, 0x1680,
    0x180E, 0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005,
    0x2006, 0x2007, 0x2008, 0x2009, 0x200A, 0x200B, 0x2028,
    0x2029, 0x202F, 0x205F, 0x3000, 0xFEFF,
]


class JsStringParityTests(unittest.TestCase):
    def test_python_boundary_cases(self):
        for codepoint, expected in ((0x85, True), (0xFEFF, False),
                                    (0x1C, True), (0x200B, True),
                                    (0x00A0, False), (0x2028, False)):
            with self.subTest(codepoint=hex(codepoint)):
                self.assertIs(legacy_v0.string(chr(codepoint)), expected)

    def test_reference_validation_uses_product_trim(self):
        for text, should_pass in (("\u0085", True), ("\ufeff", False),
                                  ("\u001c", True), ("\u00a0", False)):
            with self.subTest(text=repr(text)):
                ref = {"kind": "AUTHORITY", "id": text}
                if should_pass:
                    legacy_v0.refs([ref])
                else:
                    with self.assertRaisesRegex(ValueError, "PRODUCT_V0_CONTRACT_MISMATCH"):
                        legacy_v0.refs([ref])

    @unittest.skipUnless(shutil.which("node"), "Native Node not installed")
    def test_native_node_string_predicate_matches_python_mirror(self):
        # Node is a separate runtime, but this is a narrowed literal predicate
        # copied from the frozen Product contract. Full Zod tests remain OPEN.
        completed = subprocess.run(
            ["node", str(SCRIPT)],
            input=json.dumps(CODEPOINTS), text=True,
            capture_output=True, check=True, timeout=15,
        )
        observations = json.loads(completed.stdout)
        self.assertEqual([item["cp"] for item in observations], CODEPOINTS)
        for item in observations:
            with self.subTest(codepoint=hex(item["cp"])):
                self.assertIs(legacy_v0.string(chr(item["cp"])), item["valid"])


if __name__ == "__main__":
    unittest.main()
