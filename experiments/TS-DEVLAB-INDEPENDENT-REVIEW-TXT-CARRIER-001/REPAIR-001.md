# TS-DEVLAB-INDEPENDENT-REVIEW-TXT-CARRIER-001 — Repair 001

Preserve the existing exact-member carrier mode and its tests. Add only a recursive reviewer-facing projection mode based on the real Branch-A finding.

Authority: NONE
Product effect: NONE
Independent Review effect: NONE

## Empirical trigger

Real frozen review:
- outer TAR sha256: b887750e9f5a3eb3bbaa9f7dff95cd8aaa7fa8a4072b8679cad5fe6a43fe6ff2
- outer bytes: 314880
- outer entries: 12
- exact-member TXT projection PASS, but one outer member is evidence/history.tar (204800 bytes)
- recursive characterization found:
  - archive_count: 4
  - max_archive_depth: 2
  - leaf_count: 47
  - all leaf payloads UTF-8
  - only non-regular entries observed were safe directory entries inside a nested frozen.tar
  - nested TAR identities:
    - evidence/history.tar sha256 04e61e07b271def968d0d3e99f8cac7bb69e56d6ba79c3bfeb5b4ded8f3929e0
    - child frozen.tar sha256 1597238ac1163c6784ba5dd9d9660f49bb9757cb63e785a2490ea9bcb250eff3
    - parent frozen.tar sha256 f037a19f90ccee7e2503a4a492cc631575019dd9671ad89e40f0e87aab7d4c91

The current exact-member TXT is technically valid but not fully reviewer-readable because nested TAR bytes remain opaque.

## Add new commands

- project-readable <source.tar> --out <bundle.txt> --report <report.json>
- verify-readable <bundle.txt> --report <report.json>

Do not change existing project/verify/extract behavior.

## New format

Magic/version:
IR-TXT-REVIEW-PROJECTION/1

Purpose:
A reviewer-facing UTF-8 projection, not archive reconstruction.

Recursively traverse TAR containers.

Archive handling:
- root TAR is archive depth 0.
- a regular member whose name ends in .tar and whose payload parses as a TAR is treated as a nested archive.
- record every archive container with:
  - archive_chain: array of containing TAR member names; root uses []
  - source_member_path: null for root, member path for nested archive
  - sha256
  - byte_length
  - entry_count
  - depth
- safe directory entries may be accepted as structure only and carry no payload.
- reject symlink, hardlink, char/block device, FIFO, absolute/traversal/unsafe paths.
- regular non-container leaf payloads must be valid UTF-8.
- nested archives may recurse to a bounded maximum depth of 8; exceeding it fails closed.

Leaf handling:
- each leaf record:
  - archive_chain: array of nested TAR member paths from root to containing archive
  - path: member path inside containing archive
  - byte_length
  - sha256
- preserve leaf payload bytes exactly.
- deterministic ordering by canonical archive_chain then path.
- length framing, not sentinel framing.
- entire bundle must be valid UTF-8.

## Report

Minimum:
- status
- format
- source_archive {sha256,size,entry_count}
- archive_count
- leaf_count
- max_archive_depth
- review_leaf_payload_equivalence: PASS/FAIL
- archive_container_identity_preserved_as_metadata: true
- source_archive_byte_reconstruction: NOT_CLAIMED
- nested_archive_byte_reconstruction: NOT_CLAIMED
- all_leaf_payloads_utf8: true on PASS
- Product_effect: NONE
- Independent_Review_effect: NONE

The projection does NOT claim the original TAR or nested TAR bytes can be reconstructed from the TXT.

## Tests

Add focused tests without weakening existing exact mode:
1. nested TAR depth 2 with UTF-8 leaves.
2. safe directory entries are accepted as structure.
3. nested symlink/hardlink/device/FIFO rejected.
4. nested non-UTF8 leaf rejected.
5. recursive projection deterministic.
6. tampered leaf detected by verifier.
7. archive-chain/path provenance preserved.
8. depth limit fails closed.
9. existing exact-member mode tests still PASS.

Do not touch main.
Do not touch Tecnotron.
Do not change Product review semantics.
Do not claim TAR replacement.
Commit/push this branch only, then stop.
