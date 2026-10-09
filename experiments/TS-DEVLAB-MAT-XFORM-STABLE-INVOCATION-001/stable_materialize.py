from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

_HISTORICAL_PATH = Path(__file__).parent / "historical-source" / "transport_extractor.py"
_HISTORICAL_SPEC = importlib.util.spec_from_file_location("mat_xform_historical", _HISTORICAL_PATH)
if _HISTORICAL_SPEC is None or _HISTORICAL_SPEC.loader is None:
    raise ImportError(f"cannot load historical extractor: {_HISTORICAL_PATH}")
_HISTORICAL = importlib.util.module_from_spec(_HISTORICAL_SPEC)
sys.modules[_HISTORICAL_SPEC.name] = _HISTORICAL
_HISTORICAL_SPEC.loader.exec_module(_HISTORICAL)
TransportError = _HISTORICAL.TransportError
extract_transport = _HISTORICAL.extract_transport

SCHEMA = "ts-devlab-text-materialization-request/v0"
RESERVED_SENTINEL = re.compile(r"^@@(?:TECNOTRON_|TRANSPORT_METADATA_|ARTIFACT_|BATCH_RESULT_METADATA_)")


def _error(message: str) -> TransportError:
    return TransportError("INVALID_REQUEST", message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_inline(request: Any) -> tuple[str, list[dict[str, str]]]:
    if not isinstance(request, dict) or request.get("schema") != SCHEMA:
        raise _error(f"schema must be {SCHEMA!r}")
    batch_id = request.get("batch_id")
    if not isinstance(batch_id, str) or not batch_id or "\n" in batch_id or "\r" in batch_id:
        raise _error("batch_id must be a non-empty single-line string")
    artifacts = request.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise _error("artifacts must be a non-empty array")
    result: list[dict[str, str]] = []
    ids: set[str] = set()
    paths: set[str] = set()
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            raise _error(f"artifacts[{index}] must be an object")
        artifact_id = artifact.get("id")
        filename = artifact.get("relative_path")
        text = artifact.get("utf8_text")
        if not isinstance(artifact_id, str) or not artifact_id or "@@" in artifact_id:
            raise _error(f"artifacts[{index}].id is invalid")
        if not isinstance(filename, str) or not filename:
            raise _error(f"artifacts[{index}].relative_path is invalid")
        if not isinstance(text, str):
            raise _error(f"artifacts[{index}].utf8_text must be a string")
        if not text or not text.endswith(("\n", "\r")):
            raise _error(f"artifacts[{index}].utf8_text must be non-empty and end with a line ending")
        if any(RESERVED_SENTINEL.match(line.rstrip("\r\n")) for line in text.splitlines(keepends=True)):
            raise _error(f"artifacts[{index}].utf8_text contains a reserved sentinel")
        normalized = filename.replace("\\", "/")
        parts = normalized.split("/")
        if normalized.startswith(("/", "//")) or re.match(r"^[A-Za-z]:", normalized):
            raise _error(f"artifacts[{index}].relative_path must be relative")
        if any(part in ("", ".", "..") for part in parts):
            raise _error(f"artifacts[{index}].relative_path contains an unsafe segment")
        key = normalized.casefold()
        if artifact_id in ids:
            raise _error(f"duplicate artifact id: {artifact_id}")
        if key in paths:
            raise _error(f"duplicate artifact path: {filename}")
        ids.add(artifact_id)
        paths.add(key)
        result.append({"id": artifact_id, "filename": filename, "text": text})
    return batch_id, result


def _receipt(
    mode: str,
    batch_id: str,
    output_root: Path,
    artifacts: list[dict[str, str]],
    transport: Path,
    manifest: Path,
) -> dict[str, Any]:
    outputs = []
    for artifact in artifacts:
        path = output_root.joinpath(*artifact["filename"].replace("\\", "/").split("/"))
        data = path.read_bytes()
        outputs.append({"id": artifact["id"], "path": artifact["filename"], "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    return {
        "schema": "ts-devlab-stable-materialization-receipt/v0",
        "batch_id": batch_id,
        "input_mode": mode,
        "artifact_count": len(outputs),
        "output_root": str(output_root),
        "artifacts": outputs,
        "transport_sha256": _sha256(transport),
        "manifest_sha256": _sha256(manifest),
        "dry_run": "PASS",
        "extraction": "PASS",
        "effect_state": "CONFIRMED",
        "authority_created": False,
        "Product_effect": "NONE",
    }


def materialize_from_transport(source: Path, manifest: Path, output: Path, receipt: Path) -> dict[str, Any]:
    report = extract_transport(source, manifest, output, dry_run=True)
    if report.get("result") != "PASS":
        raise _error("historical extractor dry-run did not pass")
    extract_transport(source, manifest, output, dry_run=False)
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    artifacts = [{"id": item["id"], "filename": item["filename"]} for item in manifest_data["artifacts"]]
    result = _receipt("from-transport", manifest_data["batch"], output, artifacts, source, manifest)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return result


def materialize_from_inline(request: Any, output: Path, receipt: Path) -> dict[str, Any]:
    batch_id, artifacts = _validate_inline(request)
    with tempfile.TemporaryDirectory(prefix="ts-devlab-mat-xform-") as temporary:
        root = Path(temporary)
        source = root / f"{batch_id}.md"
        manifest = root / "manifest.json"
        chunks = ["@@TECNOTRON_BATCH_RESULT_V1_BEGIN@@\n", "@@TRANSPORT_METADATA_BEGIN@@\n", f"transport_id: {batch_id}\n", f"batch: {batch_id}\n", f"document_title: {batch_id}\n", f"expected_download_filename: {source.name}\n", "@@TRANSPORT_METADATA_END@@\n"]
        for artifact in artifacts:
            chunks.extend([f"@@ARTIFACT_BEGIN:{artifact['id']}@@\n", artifact["text"], f"@@ARTIFACT_END:{artifact['id']}@@\n"])
        chunks.extend(["@@BATCH_RESULT_METADATA_BEGIN@@\n", "generated_by: stable_materialize\n", "@@BATCH_RESULT_METADATA_END@@\n", "@@TECNOTRON_BATCH_RESULT_V1_END@@\n"])
        source.write_text("".join(chunks), encoding="utf-8", newline="")
        manifest.write_text(json.dumps({"batch": batch_id, "transport": {"document_title": batch_id, "expected_download_filename": source.name}, "artifacts": [{"id": a["id"], "filename": a["filename"]} for a in artifacts]}), encoding="utf-8", newline="\n")
        result = materialize_from_transport(source, manifest, output, receipt)
        result["input_mode"] = "from-inline"
        receipt.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="mode", required=True)
    transport = subparsers.add_parser("from-transport")
    transport.add_argument("source", type=Path)
    transport.add_argument("--manifest", required=True, type=Path)
    transport.add_argument("--output", required=True, type=Path)
    transport.add_argument("--receipt", required=True, type=Path)
    inline = subparsers.add_parser("from-inline")
    inline.add_argument("request", type=Path)
    inline.add_argument("--output", required=True, type=Path)
    inline.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.mode == "from-transport":
            result = materialize_from_transport(args.source, args.manifest, args.output, args.receipt)
        else:
            result = materialize_from_inline(json.loads(args.request.read_text(encoding="utf-8")), args.output, args.receipt)
    except (OSError, json.JSONDecodeError, TransportError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
