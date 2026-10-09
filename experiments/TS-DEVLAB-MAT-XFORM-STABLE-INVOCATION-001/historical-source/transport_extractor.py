from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

OUTER_BEGIN = "@@TECNOTRON_BATCH_RESULT_V1_BEGIN@@"
OUTER_END = "@@TECNOTRON_BATCH_RESULT_V1_END@@"
TRANSPORT_METADATA_BEGIN = "@@TRANSPORT_METADATA_BEGIN@@"
TRANSPORT_METADATA_END = "@@TRANSPORT_METADATA_END@@"
BATCH_METADATA_BEGIN = "@@BATCH_RESULT_METADATA_BEGIN@@"
BATCH_METADATA_END = "@@BATCH_RESULT_METADATA_END@@"
ARTIFACT_BEGIN_RE = re.compile(r"^@@ARTIFACT_BEGIN:(.+)@@$")
ARTIFACT_END_RE = re.compile(r"^@@ARTIFACT_END:(.+)@@$")
RESERVED_PREFIXES = (
    "@@TECNOTRON_",
    "@@TRANSPORT_METADATA_",
    "@@ARTIFACT_",
    "@@BATCH_RESULT_METADATA_",
)
REPORT_FILENAME = "extraction-report.json"
SOURCE_DOCUMENT = "CHATGPT_DOCUMENT_BLOCK_MARKDOWN_EXPORT"
SOURCE_WRAPPED = "WRAPPED_MARKDOWN_WITH_LITERAL_SENTINELS"


class TransportError(Exception):
    """Deterministic, fail-closed transport validation error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class ManifestArtifact:
    artifact_id: str
    filename: str
    parts: tuple[str, ...]


@dataclass(frozen=True)
class TransportManifest:
    batch: str
    document_title: str
    expected_download_filename: str
    artifacts: tuple[ManifestArtifact, ...]


@dataclass(frozen=True)
class ParsedArtifact:
    artifact_id: str
    payload: str


def _line_body(line: str) -> str:
    if line.endswith("\r\n"):
        return line[:-2]
    if line.endswith("\n") or line.endswith("\r"):
        return line[:-1]
    return line


def _is_reserved_sentinel(body: str) -> bool:
    return body.startswith(RESERVED_PREFIXES)


def _require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise TransportError(
            "INVALID_MANIFEST",
            f"{field} must be a non-empty string",
        )
    if "\r" in value or "\n" in value:
        raise TransportError(
            "INVALID_MANIFEST",
            f"{field} must not contain line breaks",
        )
    return value


def _validate_artifact_id(value: Any, field: str) -> str:
    artifact_id = _require_nonempty_string(value, field)
    if "@@" in artifact_id:
        raise TransportError(
            "INVALID_MANIFEST",
            f"{field} must not contain '@@'",
        )
    return artifact_id


def _safe_relative_parts(filename: str) -> tuple[str, ...]:
    if "\x00" in filename:
        raise TransportError(
            "UNSAFE_ARTIFACT_PATH",
            f"NUL byte in artifact filename: {filename!r}",
        )

    normalized = filename.replace("\\", "/")

    if normalized.startswith("/") or normalized.startswith("//"):
        raise TransportError(
            "ABSOLUTE_ARTIFACT_PATH",
            f"absolute artifact path is forbidden: {filename!r}",
        )

    if re.match(r"^[A-Za-z]:", normalized):
        raise TransportError(
            "ABSOLUTE_ARTIFACT_PATH",
            f"drive-qualified artifact path is forbidden: {filename!r}",
        )

    parts = tuple(normalized.split("/"))

    if not parts or any(part in ("", ".", "..") for part in parts):
        if ".." in parts:
            raise TransportError(
                "PATH_TRAVERSAL",
                f"path traversal is forbidden: {filename!r}",
            )
        raise TransportError(
            "UNSAFE_ARTIFACT_PATH",
            f"invalid artifact filename: {filename!r}",
        )

    return parts


def load_manifest(path: Path) -> TransportManifest:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise TransportError("MANIFEST_READ_FAILED", str(exc)) from exc

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TransportError("MANIFEST_NOT_UTF8", str(exc)) from exc

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise TransportError("INVALID_MANIFEST_JSON", str(exc)) from exc

    if not isinstance(data, dict):
        raise TransportError(
            "INVALID_MANIFEST",
            "manifest root must be a JSON object",
        )

    batch = _require_nonempty_string(data.get("batch"), "batch")

    transport = data.get("transport")
    if not isinstance(transport, dict):
        raise TransportError(
            "INVALID_MANIFEST",
            "transport must be a JSON object",
        )

    document_title = _require_nonempty_string(
        transport.get("document_title"),
        "transport.document_title",
    )
    expected_download_filename = _require_nonempty_string(
        transport.get("expected_download_filename"),
        "transport.expected_download_filename",
    )

    artifact_values = data.get("artifacts")
    if not isinstance(artifact_values, list) or not artifact_values:
        raise TransportError(
            "INVALID_MANIFEST",
            "artifacts must be a non-empty JSON array",
        )

    artifacts: list[ManifestArtifact] = []
    seen_ids: set[str] = set()
    seen_filenames: set[str] = set()

    for index, value in enumerate(artifact_values):
        if not isinstance(value, dict):
            raise TransportError(
                "INVALID_MANIFEST",
                f"artifacts[{index}] must be an object",
            )

        artifact_id = _validate_artifact_id(
            value.get("id"),
            f"artifacts[{index}].id",
        )
        filename = _require_nonempty_string(
            value.get("filename"),
            f"artifacts[{index}].filename",
        )
        parts = _safe_relative_parts(filename)

        if artifact_id in seen_ids:
            raise TransportError(
                "DUPLICATE_MANIFEST_ARTIFACT_ID",
                artifact_id,
            )
        seen_ids.add(artifact_id)

        filename_key = "/".join(parts).casefold()

        if filename_key == REPORT_FILENAME.casefold():
            raise TransportError(
                "RESERVED_OUTPUT_FILENAME",
                filename,
            )

        if filename_key in seen_filenames:
            raise TransportError(
                "DUPLICATE_MANIFEST_FILENAME",
                filename,
            )
        seen_filenames.add(filename_key)

        artifacts.append(
            ManifestArtifact(
                artifact_id,
                filename,
                parts,
            )
        )

    return TransportManifest(
        batch,
        document_title,
        expected_download_filename,
        tuple(artifacts),
    )


def _read_utf8_source(path: Path) -> str:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise TransportError("SOURCE_READ_FAILED", str(exc)) from exc

    if raw.startswith(b"\xef\xbb\xbf"):
        raise TransportError(
            "UTF8_BOM_FORBIDDEN",
            (
                "source must begin with the literal batch sentinel, "
                "not a UTF-8 BOM"
            ),
        )

    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TransportError("SOURCE_NOT_UTF8", str(exc)) from exc


def _exact_line_indexes(
    lines: list[str],
    sentinel: str,
) -> list[int]:
    return [
        index
        for index, line in enumerate(lines)
        if _line_body(line) == sentinel
    ]


def _only_whitespace(lines: Iterable[str]) -> bool:
    return all(not line.strip() for line in lines)


def _parse_transport_metadata(
    lines: list[str],
) -> dict[str, str]:
    metadata: dict[str, str] = {}

    for line in lines:
        body = _line_body(line)

        if not body.strip():
            continue

        if _is_reserved_sentinel(body):
            raise TransportError(
                "RESERVED_SENTINEL_COLLISION",
                (
                    "reserved sentinel inside transport metadata: "
                    f"{body!r}"
                ),
            )

        if ":" not in body:
            raise TransportError(
                "INVALID_TRANSPORT_METADATA",                f"expected 'key: value', got {body!r}",
            )

        key, value = body.split(":", 1)
        key = key.strip()
        value = value.strip()

        if not key or not value:
            raise TransportError(
                "INVALID_TRANSPORT_METADATA",
                f"empty metadata key/value in {body!r}",
            )

        if key in metadata:
            raise TransportError(
                "DUPLICATE_TRANSPORT_METADATA_KEY",
                key,
            )

        metadata[key] = value

    required = (
        "transport_id",
        "batch",
        "document_title",
        "expected_download_filename",
    )
    missing = [
        key
        for key in required
        if key not in metadata
    ]

    if missing:
        raise TransportError(
            "MISSING_TRANSPORT_METADATA",
            ", ".join(missing),
        )

    return metadata


def _consume_whitespace(
    lines: list[str],
    index: int,
    stop: int,
) -> int:
    while index < stop and not _line_body(lines[index]).strip():
        index += 1
    return index


def parse_transport(
    text: str,
    manifest: TransportManifest,
    strict_wrapper: bool,
) -> tuple[
    str,
    dict[str, str],
    tuple[ParsedArtifact, ...],
]:
    lines = text.splitlines(keepends=True)

    if not lines:
        raise TransportError(
            "EMPTY_SOURCE",
            "source file is empty",
        )

    begin_indexes = _exact_line_indexes(
        lines,
        OUTER_BEGIN,
    )
    end_indexes = _exact_line_indexes(
        lines,
        OUTER_END,
    )

    if len(begin_indexes) != 1 or len(end_indexes) != 1:
        raise TransportError(
            "BATCH_SENTINEL_COUNT",
            (
                "expected exactly one batch BEGIN and END, "
                f"found BEGIN={len(begin_indexes)} "
                f"END={len(end_indexes)}"
            ),
        )

    begin_index = begin_indexes[0]
    end_index = end_indexes[0]

    if begin_index >= end_index:
        raise TransportError(
            "BATCH_SENTINEL_ORDER",
            "batch END must follow batch BEGIN",
        )

    prefix = lines[:begin_index]
    suffix = lines[end_index + 1 :]

    wrapper_is_clean = (
        _only_whitespace(prefix)
        and _only_whitespace(suffix)
    )

    if strict_wrapper and not wrapper_is_clean:
        raise TransportError(
            "STRICT_WRAPPER_REJECTED",
            (
                "non-whitespace content exists outside "
                "the batch wrapper"
            ),
        )

    source_transport = (
        SOURCE_DOCUMENT
        if wrapper_is_clean
        else SOURCE_WRAPPED
    )

    index = begin_index + 1
    index = _consume_whitespace(
        lines,
        index,
        end_index,
    )

    if (
        index >= end_index
        or _line_body(lines[index])
        != TRANSPORT_METADATA_BEGIN
    ):
        raise TransportError(
            "MISSING_TRANSPORT_METADATA",
            (
                "transport metadata section must be "
                "first inside the batch"
            ),
        )

    metadata_begin = index
    metadata_end_candidates = [
        candidate
        for candidate in range(
            metadata_begin + 1,
            end_index,
        )
        if _line_body(lines[candidate])
        == TRANSPORT_METADATA_END
    ]

    if len(metadata_end_candidates) != 1:
        raise TransportError(
            "TRANSPORT_METADATA_SENTINEL_COUNT",
            (
                "expected one transport metadata END, "
                f"found {len(metadata_end_candidates)}"
            ),
        )

    metadata_end = metadata_end_candidates[0]
    metadata = _parse_transport_metadata(
        lines[metadata_begin + 1 : metadata_end]
    )

    if metadata["batch"] != manifest.batch:
        raise TransportError(
            "BATCH_MISMATCH",
            (
                f"document batch {metadata['batch']!r} "
                f"!= manifest batch {manifest.batch!r}"
            ),
        )

    if metadata["document_title"] != manifest.document_title:
        raise TransportError(
            "DOCUMENT_TITLE_MISMATCH",
            (
                "document title "
                f"{metadata['document_title']!r} "
                "!= manifest title "
                f"{manifest.document_title!r}"
            ),
        )

    if (
        metadata["expected_download_filename"]
        != manifest.expected_download_filename
    ):
        raise TransportError(
            "EXPECTED_FILENAME_METADATA_MISMATCH",
            (
                "document expected_download_filename "
                "does not match manifest"
            ),
        )

    index = metadata_end + 1
    parsed: list[ParsedArtifact] = []
    seen_ids: set[str] = set()
    batch_metadata_seen = False

    while True:
        index = _consume_whitespace(
            lines,
            index,
            end_index,
        )

        if index >= end_index:
            break

        body = _line_body(lines[index])

        if body == BATCH_METADATA_BEGIN:
            if batch_metadata_seen:
                raise TransportError(
                    "DUPLICATE_BATCH_RESULT_METADATA",
                    "batch result metadata section repeated",
                )

            batch_metadata_seen = True

            metadata_end_candidates = [
                candidate
                for candidate in range(
                    index + 1,
                    end_index,
                )
                if _line_body(lines[candidate])
                == BATCH_METADATA_END
            ]

            if len(metadata_end_candidates) != 1:
                raise TransportError(
                    "BATCH_RESULT_METADATA_SENTINEL_COUNT",
                    (
                        "expected one batch result metadata END, "
                        f"found {len(metadata_end_candidates)}"
                    ),
                )

            batch_metadata_end = metadata_end_candidates[0]

            for inner in lines[
                index + 1 : batch_metadata_end
            ]:
                inner_body = _line_body(inner)

                if _is_reserved_sentinel(inner_body):
                    raise TransportError(
                        "RESERVED_SENTINEL_COLLISION",
                        (
                            "reserved sentinel inside "
                            "batch result metadata: "
                            f"{inner_body!r}"
                        ),
                    )

            index = batch_metadata_end + 1
            index = _consume_whitespace(
                lines,
                index,
                end_index,
            )

            if index != end_index:
                raise TransportError(
                    "INTERSTITIAL_CONTENT",
                    (
                        "non-whitespace content appears "
                        "after batch result metadata and "
                        "before batch END"
                    ),
                )

            break

        match = ARTIFACT_BEGIN_RE.fullmatch(body)

        if not match:
            raise TransportError(
                "INTERSTITIAL_CONTENT",
                (
                    "unexpected non-whitespace content "
                    "between transport sections: "
                    f"{body!r}"
                ),
            )

        artifact_id = match.group(1)

        if artifact_id in seen_ids:
            raise TransportError(
                "DUPLICATE_ARTIFACT_ID",
                artifact_id,
            )

        seen_ids.add(artifact_id)
        payload_start = index + 1
        cursor = payload_start
        expected_end = (
            f"@@ARTIFACT_END:{artifact_id}@@"
        )

        while cursor < end_index:
            candidate = _line_body(lines[cursor])

            if candidate == expected_end:
                break

            end_match = ARTIFACT_END_RE.fullmatch(
                candidate
            )

            if end_match:
                raise TransportError(
                    "MISMATCHED_ARTIFACT_END",
                    (
                        f"artifact {artifact_id!r} "
                        "closed by "
                        f"{end_match.group(1)!r}"
                    ),
                )

            if (
                ARTIFACT_BEGIN_RE.fullmatch(candidate)
                or candidate
                in (
                    BATCH_METADATA_BEGIN,
                    BATCH_METADATA_END,
                    OUTER_END,
                )
            ):
                raise TransportError(
                    "MISSING_ARTIFACT_END",
                    artifact_id,
                )

            if _is_reserved_sentinel(candidate):
                raise TransportError(
                    "RESERVED_SENTINEL_COLLISION",
                    (
                        "reserved sentinel inside artifact "
                        f"{artifact_id!r}: {candidate!r}"
                    ),
                )

            cursor += 1

        if cursor >= end_index:
            raise TransportError(
                "MISSING_ARTIFACT_END",
                artifact_id,
            )

        payload = "".join(
            lines[payload_start:cursor]
        )

        if not payload or not payload.strip():
            raise TransportError(
                "EMPTY_ARTIFACT_PAYLOAD",
                artifact_id,
            )

        parsed.append(
            ParsedArtifact(
                artifact_id,
                payload,
            )
        )
        index = cursor + 1

    if not batch_metadata_seen:
        raise TransportError(
            "MISSING_BATCH_RESULT_METADATA",
            "batch result metadata section is required",
        )

    expected_ids = [
        artifact.artifact_id
        for artifact in manifest.artifacts
    ]
    expected_set = set(expected_ids)

    parsed_ids = [
        artifact.artifact_id
        for artifact in parsed
    ]
    parsed_set = set(parsed_ids)

    unexpected = [
        artifact_id
        for artifact_id in parsed_ids
        if artifact_id not in expected_set
    ]

    if unexpected:
        raise TransportError(
            "UNEXPECTED_ARTIFACT",
            ", ".join(unexpected),
        )

    missing = [
        artifact_id
        for artifact_id in expected_ids
        if artifact_id not in parsed_set
    ]

    if missing:
        raise TransportError(
            "MISSING_EXPECTED_ARTIFACT",
            ", ".join(missing),
        )

    if len(parsed_ids) != len(expected_ids):
        raise TransportError(
            "ARTIFACT_COUNT_MISMATCH",
            "artifact count differs from manifest",
        )

    return (
        source_transport,
        metadata,
        tuple(parsed),
    )


def _validate_output_root(
    output_root: Path,
) -> None:
    if output_root.exists():
        if not output_root.is_dir():
            raise TransportError(
                "OUTPUT_NOT_DIRECTORY",
                str(output_root),
            )

        try:
            if any(output_root.iterdir()):
                raise TransportError(
                    "OUTPUT_NOT_EMPTY",
                    str(output_root),
                )
        except OSError as exc:
            raise TransportError(
                "OUTPUT_INSPECTION_FAILED",
                str(exc),
            ) from exc


def _safe_output_path(
    output_root: Path,
    parts: tuple[str, ...],
) -> Path:
    root_resolved = output_root.resolve(
        strict=False
    )
    candidate = output_root.joinpath(*parts)
    candidate_resolved = candidate.resolve(
        strict=False
    )

    try:
        common = os.path.commonpath(
            (
                str(root_resolved),
                str(candidate_resolved),
            )
        )
    except ValueError as exc:
        raise TransportError(
            "WRITE_OUTSIDE_STAGING",
            str(candidate),
        ) from exc

    if (
        os.path.normcase(common)
        != os.path.normcase(str(root_resolved))
    ):
        raise TransportError(
            "WRITE_OUTSIDE_STAGING",
            str(candidate),
        )

    return candidate


def extract_transport(
    source_path: Path,
    manifest_path: Path,
    output_root: Path,
    *,
    dry_run: bool = False,
    strict_wrapper: bool = False,
) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    _validate_output_root(output_root)

    text = _read_utf8_source(source_path)

    (
        source_transport,
        metadata,
        parsed,
    ) = parse_transport(
        text,
        manifest,
        strict_wrapper,
    )

    parsed_by_id = {
        artifact.artifact_id: artifact
        for artifact in parsed
    }

    artifact_reports: list[
        dict[str, Any]
    ] = []
    writes: list[
        tuple[Path, bytes]
    ] = []

    for artifact in manifest.artifacts:
        parsed_artifact = parsed_by_id[
            artifact.artifact_id
        ]
        payload_bytes = (
            parsed_artifact.payload.encode("utf-8")
        )
        output_path = _safe_output_path(
            output_root,
            artifact.parts,
        )

        writes.append(
            (
                output_path,
                payload_bytes,
            )
        )

        artifact_reports.append(
            {
                "id": artifact.artifact_id,
                "filename": artifact.filename,
                "byte_count": len(payload_bytes),
                "sha256": hashlib.sha256(
                    payload_bytes
                ).hexdigest(),
            }
        )

    source_basename = source_path.name
    filename_match = (
        source_basename
        == manifest.expected_download_filename
    )

    warnings: list[str] = []

    if not filename_match:
        warnings.append(
            "SOURCE_BASENAME_MISMATCH"
        )

    report: dict[str, Any] = {
        "batch": manifest.batch,
        "transport_id": metadata["transport_id"],
        "source_transport": source_transport,
        "source_basename": source_basename,
        "document_title": manifest.document_title,
        "expected_download_filename":
            manifest.expected_download_filename,
        "filename_match": filename_match,
        "artifacts": artifact_reports,
        "warnings": warnings,
        "dry_run": dry_run,
        "result": "PASS",
    }

    if dry_run:
        return report

    try:
        output_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        for output_path, payload_bytes in writes:
            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            output_path.write_bytes(
                payload_bytes
            )
        report_path = _safe_output_path(
            output_root,
            (REPORT_FILENAME,),
        )

        report_path.write_text(
            (
                json.dumps(
                    report,
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n"
            ),
            encoding="utf-8",
            newline="\n",
        )

    except OSError as exc:
        raise TransportError(
            "WRITE_FAILED",
            str(exc),
        ) from exc

    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Deterministically extract "
            "manifest-declared artifacts "
            "from ChatGPT Markdown transport."
        )
    )

    parser.add_argument(
        "downloaded_markdown",
        type=Path,
        help=(
            "Downloaded ChatGPT document "
            "Markdown export"
        ),
    )

    parser.add_argument(
        "--manifest",
        required=True,
        type=Path,
        help="Transport manifest JSON",
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Absent or empty staging directory",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Validate and report "
            "without writing files"
        ),
    )

    parser.add_argument(
        "--strict-wrapper",
        action="store_true",
        help=(
            "Reject non-whitespace content "
            "before or after the outer "
            "batch wrapper"
        ),
    )

    return parser


def main(
    argv: list[str] | None = None,
) -> int:
    args = _build_parser().parse_args(argv)

    try:
        report = extract_transport(
            args.downloaded_markdown,
            args.manifest,
            args.output,
            dry_run=args.dry_run,
            strict_wrapper=args.strict_wrapper,
        )
    except TransportError as exc:
        print(
            f"ERROR {exc.code}: {exc.message}",
            file=sys.stderr,
        )
        return 2

    print(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
