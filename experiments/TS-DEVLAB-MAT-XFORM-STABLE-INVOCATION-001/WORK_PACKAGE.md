# TS-DEVLAB-MAT-XFORM-STABLE-INVOCATION-001

Authority: NONE
Product effect: NONE
Tecnotron effect: NONE

## Concrete question

Can the already-proven MAT-XFORM transport/extractor mechanics be wrapped as one bounded stable invocation so ChatGPT can materialize many text files with one request instead of one remote write/tool call per file?

## Reuse boundary

Historical source is already present under:

experiments/TS-DEVLAB-MAT-XFORM-STABLE-INVOCATION-001/historical-source/

It was reconstructed from the indexed Library text bundle and is NOT claimed byte-identical to the original historical local file. Reuse its protocol/behavior; do not redesign MAT-XFORM.

## Required implementation

Owned paths only:

experiments/TS-DEVLAB-MAT-XFORM-STABLE-INVOCATION-001/**

Implement:

1. stable_materialize.py
2. test_stable_materialize.py
3. README.md
4. RESULT-DRAFT.md only if useful; do not claim terminal PASS before external qualification.

### Modes

A. from-transport
- inputs: existing MAT-XFORM transport file, manifest file, output staging root, receipt path.
- run historical extractor dry-run first.
- require dry-run PASS.
- then perform real extraction.
- compute actual bytes + sha256 for every output.
- emit compact JSON receipt.

B. from-inline
- input: ONE JSON request containing:
  - schema = ts-devlab-text-materialization-request/v0
  - batch_id
  - artifacts[] with id, relative_path, utf8_text
- deterministically create a compatible MAT-XFORM transport+manifest in an internal temporary area.
- invoke the SAME from-transport path.
- do not implement a second extraction algorithm.

## Safety / scope

- UTF-8 text only.
- create-only staging: target output must be absent or empty.
- no overwrite/edit of existing files.
- reject absolute paths, drive-qualified paths, empty segments and ..
- reject duplicate ids and case-insensitive duplicate paths.
- fail closed on reserved sentinel collisions.
- no symlink/path redirection escape.
- do not execute payloads.
- no Product semantics.
- no generic file-management framework.
- no ts-exec registry/profile changes.
- no Commander/Orca logic.
- no Git mutation logic.

## Receipt

Minimum:
- schema
- batch_id
- input_mode
- artifact_count
- output_root
- per artifact: id/path/bytes/sha256
- transport_sha256
- manifest_sha256
- dry_run PASS
- extraction PASS
- effect_state CONFIRMED (mechanical local file creation only)
- authority_created false
- Product_effect NONE

## Tests

Include positive and negative tests for:
- many files in one request
- nested relative paths
- UTF-8 unicode
- CRLF preservation
- duplicate path
- traversal
- absolute Windows path
- existing non-empty output rejection
- sentinel collision
- dry-run failure prevents real writes
- from-inline and equivalent from-transport produce same materialized bytes
- receipt hashes match actual bytes

Run tests locally. Commit/push this branch only. Do not merge.
