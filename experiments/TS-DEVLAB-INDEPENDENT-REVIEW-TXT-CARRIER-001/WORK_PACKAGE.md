# TS-DEVLAB-INDEPENDENT-REVIEW-TXT-CARRIER-001

Authority: NONE
Product effect: NONE
Tecnotron effect: NONE
Independent Review effect: NONE

## Concrete question

For a frozen Independent Review interface whose TAR contains only safe regular UTF-8 text members, can one deterministic .txt carrier preserve the exact member set and member bytes/hashes while being directly readable by ChatGPT, without requiring a binary TAR attachment?

This experiment does NOT redefine the Product review-interface Recipe.

## Owned paths only

experiments/TS-DEVLAB-INDEPENDENT-REVIEW-TXT-CARRIER-001/**

Implement:
1. review_txt_carrier.py
2. test_review_txt_carrier.py
3. README.md
4. RESULT-DRAFT.md only if useful.

## Required projection contract

CLI should support:
- project <source.tar> --out <bundle.txt> --report <report.json>
- verify <bundle.txt> --report <report.json>
- extract <bundle.txt> --out <empty-dir> --report <report.json>

Projection requirements:
- compute source TAR sha256, size and entry count.
- accept regular files only.
- reject symlink, hardlink, device, FIFO, absolute paths, path traversal.
- require every payload to be valid UTF-8.
- preserve each member payload BYTES exactly.
- deterministic member ordering.
- bundle itself must be UTF-8 text and reasonably human/LLM-readable.
- framing must be deterministic and parseable without Markdown interpretation.
- use byte length and sha256 per member so payload does not depend on sentinel uniqueness.
- verifier validates bundle framing, member path safety, byte length/hash, duplicate paths and bundle manifest.
- extractor writes members only inside an absent/empty output directory.
- no normalization of line endings.
- no semantic review.

## Important non-claim

The TXT projection does NOT need to reconstruct the original TAR byte-for-byte.

It must explicitly report:
- member_payload_equivalence: PASS/FAIL
- source_archive_identity_preserved_as_metadata: true
- source_archive_byte_reconstruction: NOT_CLAIMED

The architectural/Product question "may TXT replace TAR canonically?" remains external.

## Tests

Synthetic TAR tests must include:
- LF text
- CRLF text
- UTF-8 Unicode
- text with no trailing newline
- deterministic projection
- projection -> extraction exact member bytes
- tampered payload detected
- duplicate/path traversal rejected
- non-UTF8 member rejected
- symlink/hardlink rejected

Commit/push branch only. Do not touch main or Tecnotron.
