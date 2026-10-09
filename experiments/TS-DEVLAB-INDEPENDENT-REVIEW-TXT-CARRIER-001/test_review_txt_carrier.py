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
                    archive.addfile(info)
                else:
                    info.size = len(payload)
                    archive.addfile(info, io.BytesIO(payload))

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

    def test_non_utf8_and_links_are_rejected(self) -> None:
        with self._temp_dir() as root:
            non_utf8, symlink, hardlink = root / "non-utf8.tar", root / "symlink.tar", root / "hardlink.tar"
            self.make_tar(non_utf8, [("bad.txt", b"\xff", None)])
            self.make_tar(symlink, [("link", b"", tarfile.SYMTYPE)])
            self.make_tar(hardlink, [("link", b"", tarfile.LNKTYPE)])
            for source, expected in ((non_utf8, "UTF-8"), (symlink, "non-regular"), (hardlink, "non-regular")):
                with self.assertRaisesRegex(carrier.CarrierError, expected):
                    carrier.project(source, root / "bundle.txt", root / "report.json")

    def _temp_dir(self):
        class PathTemporaryDirectory(tempfile.TemporaryDirectory):
            def __enter__(self):
                return Path(super().__enter__())

        return PathTemporaryDirectory()


if __name__ == "__main__":
    unittest.main()
