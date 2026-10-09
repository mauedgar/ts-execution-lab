from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import sys

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
SPEC = importlib.util.spec_from_file_location("stable_materialize", ROOT / "stable_materialize.py")
assert SPEC and SPEC.loader
stable = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stable)


def request(*artifacts):
    return {"schema": stable.SCHEMA, "batch_id": "BATCH-1", "artifacts": list(artifacts)}


def artifact(artifact_id, path, text):
    return {"id": artifact_id, "relative_path": path, "utf8_text": text}


class StableMaterializeTests(unittest.TestCase):
    def test_inline_many_nested_unicode_and_crlf(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            out = tmp_path / "out"
            receipt_path = tmp_path / "receipt.json"
            stable.materialize_from_inline(request(artifact("one", "nested/one.txt", "café\r\n"), artifact("two", "two.txt", "第二\r\n")), out, receipt_path)
            self.assertEqual((out / "nested/one.txt").read_bytes(), "café\r\n".encode())
            self.assertEqual((out / "two.txt").read_bytes(), "第二\r\n".encode())
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            for item in receipt["artifacts"]:
                data = (out / item["path"]).read_bytes()
                self.assertEqual(item["bytes"], len(data))
                self.assertEqual(item["sha256"], hashlib.sha256(data).hexdigest())


    def test_rejects_duplicate_traversal_absolute_and_existing(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            for req in (request(artifact("a", "x.txt", "x\n"), artifact("b", "X.TXT", "y\n")), request(artifact("a", "../x.txt", "x\n")), request(artifact("a", "C:/x.txt", "x\n"))):
                with self.assertRaises(stable.TransportError):
                    stable.materialize_from_inline(req, tmp_path / "out", tmp_path / "r.json")
            out = tmp_path / "existing"
            out.mkdir()
            (out / "old").write_text("old")
            with self.assertRaises(stable.TransportError):
                stable.materialize_from_inline(request(artifact("a", "x.txt", "x\n")), out, tmp_path / "r.json")


    def test_rejects_sentinel_and_dry_run_failure_writes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            with self.assertRaises(stable.TransportError):
                stable.materialize_from_inline(request(artifact("a", "x.txt", "@@ARTIFACT_END:x@@\n")), tmp_path / "out", tmp_path / "r.json")
            out = tmp_path / "out"
            with patch.object(stable, "extract_transport", side_effect=stable.TransportError("DRY_RUN_FAILED", "test")):
                with self.assertRaises(stable.TransportError):
                    stable.materialize_from_inline(request(artifact("a", "x.txt", "x\n")), out, tmp_path / "r.json")
            self.assertFalse(out.exists())


    def test_inline_and_transport_have_same_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            req = request(artifact("a", "nested/x.txt", "hello\r\n"))
            inline_out = tmp_path / "inline"
            stable.materialize_from_inline(req, inline_out, tmp_path / "inline-receipt.json")
            transport_out = tmp_path / "transport"
            source = tmp_path / "source.md"
            manifest = tmp_path / "manifest.json"
            source.write_bytes(("@@TECNOTRON_BATCH_RESULT_V1_BEGIN@@\n@@TRANSPORT_METADATA_BEGIN@@\ntransport_id: BATCH-1\nbatch: BATCH-1\ndocument_title: BATCH-1\nexpected_download_filename: source.md\n@@TRANSPORT_METADATA_END@@\n@@ARTIFACT_BEGIN:a@@\nhello\r\n@@ARTIFACT_END:a@@\n@@BATCH_RESULT_METADATA_BEGIN@@\nx: y\n@@BATCH_RESULT_METADATA_END@@\n@@TECNOTRON_BATCH_RESULT_V1_END@@\n").encode())
            manifest.write_text(json.dumps({"batch": "BATCH-1", "transport": {"document_title": "BATCH-1", "expected_download_filename": "source.md"}, "artifacts": [{"id": "a", "filename": "nested/x.txt"}]}))
            stable.materialize_from_transport(source, manifest, transport_out, tmp_path / "transport-receipt.json")
            self.assertEqual((inline_out / "nested/x.txt").read_bytes(), (transport_out / "nested/x.txt").read_bytes())


if __name__ == "__main__":
    unittest.main()
