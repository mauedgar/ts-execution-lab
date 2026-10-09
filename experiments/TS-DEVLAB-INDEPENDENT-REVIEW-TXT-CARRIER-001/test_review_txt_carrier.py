import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

import review_txt_carrier as carrier


class ReviewTxtCarrierTests(unittest.TestCase):
    def make_tar(self, path: Path, entries: list[tuple[str, bytes, bytes | None]]) -> None:
        with tarfile.open(path, "w") as archive:
            for name, payload, kind in entries:
                info = tarfile.TarInfo(name)
                if kind is not None:
                    info.type = kind
                    info.linkname = "target"
                    info.size = len(payload)
                    archive.addfile(info, io.BytesIO(payload))
                else:
                    info.size = len(payload)
                    archive.addfile(info, io.BytesIO(payload))

    def tar_bytes(self, entries: list[tuple[str, bytes, bytes | None]]) -> bytes:
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode="w") as archive:
            for name, payload, kind in entries:
                info = tarfile.TarInfo(name)
                if kind is not None:
                    info.type = kind
                    info.linkname = "target"
                    info.size = len(payload)
                    archive.addfile(info, io.BytesIO(payload))
                else:
                    info.size = len(payload)
                    archive.addfile(info, io.BytesIO(payload))
        return output.getvalue()

    def test_project_extracts_exact_text_payloads_deterministically(self) -> None:
        with self.subTest("projection and extraction"):
            with self._temp_dir() as root:
                source = root / "source.tar"
                entries = [("z/no-newline.txt", b"no trailing newline", None), ("a/lf.txt", b"one\ntwo\n", None), ("b/crlf.txt", b"one\r\ntwo\r\n", None), ("c/unicode.txt", "cafe \u2615\n".encode(), None)]
                self.make_tar(source, entries)
                first, second = root / "first.txt", root / "second.txt"
                carrier.project(source, first, root / "project.json")
                carrier.project(source, second, root / "project2.json")
                self.assertEqual(first.read_bytes(), second.read_bytes())
                first.read_bytes().decode("utf-8")
                carrier.verify(first, root / "verify.json")
                destination = root / "output"
                carrier.extract(first, destination, root / "extract.json")
                self.assertEqual({name: (destination / name).read_bytes() for name, _, _ in entries}, {name: payload for name, payload, _ in entries})
                report = json.loads((root / "verify.json").read_text())
                self.assertEqual(report["member_payload_equivalence"], "PASS")
                self.assertTrue(report["source_archive_identity_preserved_as_metadata"])
                self.assertEqual(report["source_archive_byte_reconstruction"], "NOT_CLAIMED")

    def test_tampered_payload_is_detected(self) -> None:
        with self._temp_dir() as root:
            source, bundle = root / "source.tar", root / "bundle.txt"
            self.make_tar(source, [("text.txt", b"original\n", None)])
            carrier.project(source, bundle, root / "report.json")
            bundle.write_bytes(bundle.read_bytes().replace(b"original", b"tampered", 1))
            with self.assertRaisesRegex(carrier.CarrierError, "hash mismatch"):
                carrier.verify(bundle, root / "verify.json")

    def test_duplicate_and_traversal_paths_are_rejected(self) -> None:
        with self._temp_dir() as root:
            duplicate, traversal = root / "duplicate.tar", root / "traversal.tar"
            self.make_tar(duplicate, [("same.txt", b"one", None), ("same.txt", b"two", None)])
            self.make_tar(traversal, [("C:/outside.txt", b"no", None)])
            with self.assertRaisesRegex(carrier.CarrierError, "duplicate"):
                carrier.project(duplicate, root / "duplicate.txt", root / "report.json")
            with self.assertRaisesRegex(carrier.CarrierError, "unsafe"):
                carrier.project(traversal, root / "traversal.txt", root / "report.json")

    def test_portable_paths_and_case_insensitive_duplicates_are_rejected(self) -> None:
        with self._temp_dir() as root:
            cases = {
                "duplicate": [("Readme.txt", b"one", None), ("README.TXT", b"two", None)],
                "reserved": [("CON.txt", b"no", None)],
                "trailing": [("report. ", b"no", None)],
            }
            for label, entries in cases.items():
                with self.subTest(label=label):
                    source = root / f"{label}.tar"
                    self.make_tar(source, entries)
                    with self.assertRaisesRegex(carrier.CarrierError, "duplicate|unsafe"):
                        carrier.project(source, root / f"{label}.txt", root / f"{label}.json")

    def test_non_utf8_and_links_are_rejected(self) -> None:
        with self._temp_dir() as root:
            non_utf8, symlink, hardlink = root / "non-utf8.tar", root / "symlink.tar", root / "hardlink.tar"
            self.make_tar(non_utf8, [("bad.txt", b"\xff", None)])
            self.make_tar(symlink, [("link", b"", tarfile.SYMTYPE)])
            self.make_tar(hardlink, [("link", b"", tarfile.LNKTYPE)])
            for source, expected in ((non_utf8, "UTF-8"), (symlink, "non-regular"), (hardlink, "non-regular")):
                with self.assertRaisesRegex(carrier.CarrierError, expected):
                    carrier.project(source, root / "bundle.txt", root / "report.json")

    def test_readable_projection_recurses_and_preserves_provenance(self) -> None:
        with self._temp_dir() as root:
            child = self.tar_bytes([("deep.txt", b"deep\n", None)])
            history = self.tar_bytes([("safe-dir", b"", tarfile.DIRTYPE), ("child.tar", child, None), ("history.txt", b"history\n", None)])
            source = root / "source.tar"
            self.make_tar(source, [("root.txt", b"root\n", None), ("evidence/history.tar", history, None)])
            first, second = root / "first.txt", root / "second.txt"
            carrier.project_readable(source, first, root / "project.json")
            carrier.project_readable(source, second, root / "project2.json")
            self.assertEqual(first.read_bytes(), second.read_bytes())
            carrier.verify_readable(first, root / "verify.json")
            manifest, leaves = carrier._parse_readable_bundle(first)
            self.assertEqual(len(manifest["archives"]), 3)
            self.assertEqual([(metadata["archive_chain"], metadata["path"], payload) for metadata, payload in leaves], [([], "root.txt", b"root\n"), (["evidence/history.tar"], "history.txt", b"history\n"), (["evidence/history.tar", "child.tar"], "deep.txt", b"deep\n")])
            report = json.loads((root / "verify.json").read_text())
            self.assertEqual(report["archive_count"], 3)
            self.assertEqual(report["max_archive_depth"], 2)
            self.assertEqual(report["review_leaf_payload_equivalence"], "PASS")
            self.assertTrue(report["all_leaf_payloads_utf8"])

    def test_readable_projection_rejects_nested_unsafe_content_and_tampering(self) -> None:
        with self._temp_dir() as root:
            for kind in (tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.CHRTYPE, tarfile.BLKTYPE, tarfile.FIFOTYPE):
                with self.subTest(kind=kind):
                    source = root / f"{kind.decode()}.tar"
                    self.make_tar(source, [("nested.tar", self.tar_bytes([("unsafe", b"x", kind)]), None)])
                    with self.assertRaisesRegex(carrier.CarrierError, "non-regular"):
                        carrier.project_readable(source, root / "bundle.txt", root / "report.json")
            source = root / "non-utf8.tar"
            self.make_tar(source, [("nested.tar", self.tar_bytes([("bad.txt", b"\xff", None)]), None)])
            with self.assertRaisesRegex(carrier.CarrierError, "UTF-8"):
                carrier.project_readable(source, root / "bundle.txt", root / "report.json")
            self.make_tar(source, [("nested.tar", self.tar_bytes([("good.txt", b"original", None)]), None)])
            bundle = root / "bundle.txt"
            carrier.project_readable(source, bundle, root / "report.json")
            bundle.write_bytes(bundle.read_bytes().replace(b"original", b"tampered", 1))
            with self.assertRaisesRegex(carrier.CarrierError, "hash mismatch"):
                carrier.verify_readable(bundle, root / "verify.json")

    def test_readable_projection_rejects_ambiguous_and_non_printable_leaves(self) -> None:
        with self._temp_dir() as root:
            duplicate = root / "duplicate.tar"
            self.make_tar(duplicate, [("Readme.txt", b"one", None), ("README.TXT", b"two", None)])
            with self.assertRaisesRegex(carrier.CarrierError, "duplicate"):
                carrier.project_readable(duplicate, root / "duplicate.txt", root / "duplicate.json")
            for label, payload in (("nul", b"safe\x00text"), ("control", b"safe\x1ftext")):
                with self.subTest(label=label):
                    source = root / f"{label}.tar"
                    self.make_tar(source, [("leaf.txt", payload, None)])
                    with self.assertRaisesRegex(carrier.CarrierError, "reviewer-readable"):
                        carrier.project_readable(source, root / f"{label}.txt", root / f"{label}.json")

    def test_verification_rejects_case_insensitive_duplicate_provenance(self) -> None:
        with self._temp_dir() as root:
            exact_metadata = [
                {"path": "README.TXT", "byte_length": 3, "sha256": carrier._sha256(b"two")},
                {"path": "Readme.txt", "byte_length": 3, "sha256": carrier._sha256(b"one")},
            ]
            exact_manifest = {"format": "IR-TXT-CARRIER/1", "source_archive": {"sha256": "0" * 64, "size": 0, "entry_count": 2}, "members": exact_metadata}
            exact_bundle = root / "exact.txt"
            exact_bundle.write_bytes(carrier._encode_bundle(exact_manifest, list(zip(exact_metadata, [b"two", b"one"]))))
            with self.assertRaisesRegex(carrier.CarrierError, "duplicate"):
                carrier.verify(exact_bundle, root / "exact-report.json")

            readable_metadata = [
                {"archive_chain": [], "path": "README.TXT", "byte_length": 3, "sha256": carrier._sha256(b"two")},
                {"archive_chain": [], "path": "Readme.txt", "byte_length": 3, "sha256": carrier._sha256(b"one")},
            ]
            archive = {"archive_chain": [], "source_member_path": None, "sha256": "0" * 64, "byte_length": 0, "entry_count": 2, "depth": 0}
            manifest = {"format": "IR-TXT-REVIEW-PROJECTION/1", "source_archive": {"sha256": "0" * 64, "size": 0, "entry_count": 2}, "archives": [archive], "leaves": readable_metadata}
            bundle = root / "bundle.txt"
            bundle.write_bytes(carrier._encode_readable_bundle(manifest, list(zip(readable_metadata, [b"two", b"one"]))))
            with self.assertRaisesRegex(carrier.CarrierError, "invalid leaf ordering"):
                carrier.verify_readable(bundle, root / "report.json")

    def test_readable_projection_depth_limit_fails_closed(self) -> None:
        with self._temp_dir() as root:
            payload = self.tar_bytes([("leaf.txt", b"text\n", None)])
            for depth in range(9):
                payload = self.tar_bytes([(f"level-{depth}.tar", payload, None)])
            source = root / "deep.tar"
            source.write_bytes(payload)
            with self.assertRaisesRegex(carrier.CarrierError, "maximum archive depth"):
                carrier.project_readable(source, root / "bundle.txt", root / "report.json")

    def _temp_dir(self):
        class PathTemporaryDirectory(tempfile.TemporaryDirectory):
            def __enter__(self):
                return Path(super().__enter__())

        return PathTemporaryDirectory()


if __name__ == "__main__":
    unittest.main()
