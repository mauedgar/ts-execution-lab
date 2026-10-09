"""Deterministic, text-only projection for safe UTF-8 TAR members."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import sys
import tarfile
from typing import Any


MAGIC = b"IR-TXT-CARRIER/1\n"
END_MEMBER = b"\nEND-MEMBER\n"
END_BUNDLE = b"END-BUNDLE\n"


class CarrierError(ValueError):
    pass


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _safe_path(name: str) -> None:
    path = PurePosixPath(name)
    windows_path = PureWindowsPath(name)
    if (
        not name
        or "\\" in name
        or path.is_absolute()
        or windows_path.is_absolute()
        or windows_path.drive
        or any(part in ("", ".", "..") for part in path.parts)
    ):
        raise CarrierError(f"unsafe member path: {name!r}")


def _read_tar(source: Path) -> tuple[dict[str, Any], list[tuple[dict[str, Any], bytes]]]:
    source_bytes = source.read_bytes()
    try:
        archive = tarfile.open(fileobj=io.BytesIO(source_bytes), mode="r:")
    except tarfile.TarError as error:
        raise CarrierError(f"invalid TAR: {error}") from error
    with archive:
        entries = archive.getmembers()
        members: list[tuple[dict[str, Any], bytes]] = []
        paths: set[str] = set()
        for entry in entries:
            _safe_path(entry.name)
            if not entry.isfile():
                raise CarrierError(f"non-regular TAR member: {entry.name!r}")
            if entry.name in paths:
                raise CarrierError(f"duplicate TAR member path: {entry.name!r}")
            paths.add(entry.name)
            payload_file = archive.extractfile(entry)
            if payload_file is None:
                raise CarrierError(f"cannot read TAR member: {entry.name!r}")
            payload = payload_file.read()
            try:
                payload.decode("utf-8")
            except UnicodeDecodeError as error:
                raise CarrierError(f"member is not valid UTF-8: {entry.name!r}") from error
            members.append(({"path": entry.name, "byte_length": len(payload), "sha256": _sha256(payload)}, payload))

    members.sort(key=lambda item: item[0]["path"])
    manifest = {
        "format": "IR-TXT-CARRIER/1",
        "source_archive": {"sha256": _sha256(source_bytes), "size": len(source_bytes), "entry_count": len(entries)},
        "members": [metadata for metadata, _ in members],
    }
    return manifest, members


def _encode_bundle(manifest: dict[str, Any], members: list[tuple[dict[str, Any], bytes]]) -> bytes:
    manifest_bytes = _canonical_json(manifest)
    output = bytearray(MAGIC)
    output.extend(f"MANIFEST-SHA256 {_sha256(manifest_bytes)}\n".encode("ascii"))
    output.extend(f"MANIFEST-BYTES {len(manifest_bytes)}\n".encode("ascii"))
    output.extend(manifest_bytes)
    output.extend(b"\n")
    for metadata, payload in members:
        output.extend(b"MEMBER ")
        output.extend(_canonical_json(metadata))
        output.extend(b"\n")
        output.extend(payload)
        output.extend(END_MEMBER)
    output.extend(END_BUNDLE)
    return bytes(output)


def _line(data: bytes, cursor: int) -> tuple[bytes, int]:
    end = data.find(b"\n", cursor)
    if end < 0:
        raise CarrierError("truncated framing line")
    return data[cursor:end], end + 1


def _parse_json(value: bytes, label: str) -> Any:
    try:
        return json.loads(value.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CarrierError(f"invalid {label} JSON") from error


def _parse_bundle(bundle: Path) -> tuple[dict[str, Any], list[tuple[dict[str, Any], bytes]]]:
    data = bundle.read_bytes()
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise CarrierError("bundle is not valid UTF-8 text") from error
    if not data.startswith(MAGIC):
        raise CarrierError("invalid bundle magic")
    cursor = len(MAGIC)
    manifest_hash_line, cursor = _line(data, cursor)
    if not manifest_hash_line.startswith(b"MANIFEST-SHA256 "):
        raise CarrierError("missing manifest hash")
    try:
        expected_manifest_hash = manifest_hash_line.removeprefix(b"MANIFEST-SHA256 ").decode("ascii", "strict")
    except UnicodeDecodeError as error:
        raise CarrierError("invalid manifest hash") from error
    if len(expected_manifest_hash) != 64 or any(char not in "0123456789abcdef" for char in expected_manifest_hash):
        raise CarrierError("invalid manifest hash")
    size_line, cursor = _line(data, cursor)
    if not size_line.startswith(b"MANIFEST-BYTES "):
        raise CarrierError("missing manifest byte length")
    try:
        manifest_size = int(size_line.removeprefix(b"MANIFEST-BYTES "))
    except ValueError as error:
        raise CarrierError("invalid manifest byte length") from error
    if manifest_size < 0 or cursor + manifest_size >= len(data):
        raise CarrierError("truncated manifest")
    manifest_bytes = data[cursor : cursor + manifest_size]
    cursor += manifest_size
    if data[cursor : cursor + 1] != b"\n":
        raise CarrierError("missing manifest terminator")
    cursor += 1
    if _sha256(manifest_bytes) != expected_manifest_hash:
        raise CarrierError("manifest hash mismatch")
    manifest = _parse_json(manifest_bytes, "manifest")
    if _canonical_json(manifest) != manifest_bytes:
        raise CarrierError("manifest is not canonical")
    if (
        not isinstance(manifest, dict)
        or set(manifest) != {"format", "source_archive", "members"}
        or manifest.get("format") != "IR-TXT-CARRIER/1"
        or not isinstance(manifest["members"], list)
    ):
        raise CarrierError("invalid manifest")

    members: list[tuple[dict[str, Any], bytes]] = []
    while not data.startswith(END_BUNDLE, cursor):
        member_line, cursor = _line(data, cursor)
        if not member_line.startswith(b"MEMBER "):
            raise CarrierError("missing member header")
        metadata = _parse_json(member_line.removeprefix(b"MEMBER "), "member header")
        if not isinstance(metadata, dict) or set(metadata) != {"path", "byte_length", "sha256"}:
            raise CarrierError("invalid member header")
        path, length, digest = metadata["path"], metadata["byte_length"], metadata["sha256"]
        if not isinstance(path, str) or not isinstance(length, int) or isinstance(length, bool) or length < 0 or not isinstance(digest, str):
            raise CarrierError("invalid member metadata")
        _safe_path(path)
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise CarrierError("invalid member hash")
        if cursor + length + len(END_MEMBER) > len(data):
            raise CarrierError("truncated member payload")
        payload = data[cursor : cursor + length]
        cursor += length
        if data[cursor : cursor + len(END_MEMBER)] != END_MEMBER:
            raise CarrierError("invalid member terminator")
        cursor += len(END_MEMBER)
        if _sha256(payload) != digest:
            raise CarrierError(f"member hash mismatch: {path!r}")
        members.append((metadata, payload))
    cursor += len(END_BUNDLE)
    if cursor != len(data):
        raise CarrierError("trailing data after bundle")
    paths = [metadata["path"] for metadata, _ in members]
    if len(paths) != len(set(paths)):
        raise CarrierError("duplicate member path")
    if paths != sorted(paths):
        raise CarrierError("members are not sorted")
    if manifest.get("members") != [metadata for metadata, _ in members]:
        raise CarrierError("manifest member list mismatch")
    source = manifest.get("source_archive")
    if not isinstance(source, dict) or set(source) != {"sha256", "size", "entry_count"}:
        raise CarrierError("invalid source archive metadata")
    source_hash, source_size, entry_count = source["sha256"], source["size"], source["entry_count"]
    if (
        not isinstance(source_hash, str)
        or len(source_hash) != 64
        or any(char not in "0123456789abcdef" for char in source_hash)
        or not isinstance(source_size, int)
        or isinstance(source_size, bool)
        or source_size < 0
        or not isinstance(entry_count, int)
        or isinstance(entry_count, bool)
        or entry_count != len(members)
    ):
        raise CarrierError("invalid source archive metadata")
    return manifest, members


def _report(manifest: dict[str, Any], status: str) -> dict[str, Any]:
    return {
        "status": status,
        "source_archive": manifest["source_archive"],
        "member_count": len(manifest["members"]),
        "member_payload_equivalence": "PASS" if status == "PASS" else "FAIL",
        "source_archive_identity_preserved_as_metadata": True,
        "source_archive_byte_reconstruction": "NOT_CLAIMED",
    }


def _write_report(report_path: Path, report: dict[str, Any]) -> None:
    report_path.write_bytes(_canonical_json(report) + b"\n")


def project(source: Path, output: Path, report_path: Path) -> None:
    manifest, members = _read_tar(source)
    output.write_bytes(_encode_bundle(manifest, members))
    _write_report(report_path, _report(manifest, "PASS"))


def verify(bundle: Path, report_path: Path) -> None:
    manifest, _ = _parse_bundle(bundle)
    _write_report(report_path, _report(manifest, "PASS"))


def extract(bundle: Path, output: Path, report_path: Path) -> None:
    if output.is_symlink() or (output.exists() and (not output.is_dir() or any(output.iterdir()))):
        raise CarrierError("output directory must be absent or empty")
    manifest, members = _parse_bundle(bundle)
    output.mkdir(parents=True, exist_ok=True)
    for metadata, payload in members:
        destination = output.joinpath(*PurePosixPath(metadata["path"]).parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
    _write_report(report_path, _report(manifest, "PASS"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    project_parser = commands.add_parser("project")
    project_parser.add_argument("source", type=Path)
    project_parser.add_argument("--out", required=True, type=Path)
    project_parser.add_argument("--report", required=True, type=Path)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("bundle", type=Path)
    verify_parser.add_argument("--report", required=True, type=Path)
    extract_parser = commands.add_parser("extract")
    extract_parser.add_argument("bundle", type=Path)
    extract_parser.add_argument("--out", required=True, type=Path)
    extract_parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "project":
            project(args.source, args.out, args.report)
        elif args.command == "verify":
            verify(args.bundle, args.report)
        else:
            extract(args.bundle, args.out, args.report)
    except (CarrierError, OSError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    sys.exit(main())
