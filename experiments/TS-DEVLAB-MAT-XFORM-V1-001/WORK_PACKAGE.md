# TS-DEVLAB-MAT-XFORM-V1-001

Authority: NONE
Product authority: NONE
Product effect: NONE
Tecnotron effect: NONE

## Purpose

Build and qualify a JSON-first MAT-XFORM v1 mechanical text materializer.

This is a DevLab execution-mechanics experiment. It does not modify Tecnotron, does not create Product policy, and does not become a ts-exec profile in this experiment.

## Empirical inputs

Historical MAT-XFORM proved:
- deterministic extraction;
- containment;
- dry-run before write;
- byte count / SHA-256 reporting;
- fail-closed framing/path checks.

Historical stable wrapper candidate:
- branch: devlab/mat-xform-stable-invocation-001
- candidate: 807e00b1efb1b46e2af42c2a77220fc9ec898559

Use that only as mechanical evidence/oracle. Do not import Python into the mature path.

## Core direction

```text
one serialized JSON request
→ Zod trust-boundary validation
→ TypeScript trusted implementation
→ deterministic UTF-8 file materialization
→ validated JSON result
→ validated JSON receipt
```

No sentinel/Markdown transport in the v1 core.

## Owned paths

Only:
- src/mat-xform/**
- schemas/mat-xform-*.schema.json
- test/mat-xform-*.test.ts
- examples/mat-xform/**
- experiments/TS-DEVLAB-MAT-XFORM-V1-001/**

Do not edit:
- src/cli.ts
- src/registry.ts
- src/profiles/**
- existing ts-exec contracts
- package.json unless strictly necessary (Zod is already available)
- workflows
- Tecnotron

## Contracts

### MatXformRequest

contract_version = "ts-mat-xform-request/v1"

Fields:
- request_id: non-empty string
- batch_id: non-empty string
- artifacts: non-empty array

Artifact:
- artifact_id: non-empty string
- relative_path: portable relative path using "/" separators
- utf8_text: string, MAY be empty, MAY lack trailing newline, MAY contain CRLF, Unicode, old MAT-XFORM sentinels or Markdown/code

Reject:
- absolute path
- drive-qualified path
- backslash separator
- empty segment
- "." / ".."
- NUL/control chars in path
- duplicate artifact_id
- case-insensitive duplicate relative_path
- Windows reserved device segments
- path segment ending in space/dot
- characters invalid for portable Windows filename segments: < > : " | ? *

### MatXformResult

contract_version = "ts-mat-xform-result/v1"

Fields:
- request_identity: sha256:<hex> over canonical request semantics
- request_id
- batch_id
- result_status: PASS | BLOCKED | FAIL | UNAVAILABLE
- effect_state: NONE | CONFIRMED | UNKNOWN
- artifact_count
- artifacts[]: artifact_id, relative_path, bytes, sha256
- timings
- error?: structured code/message

### MatXformReceipt

contract_version = "ts-mat-xform-receipt/v1"

Fields:
- request_identity
- request_id
- batch_id
- selected_binding_ref
- started_at
- completed_at
- result_status
- effect_state
- output_root
- artifacts[]
- authority_created: false
- Product_effect: "NONE"

Use z.infer for the three portable TS types. Zod is required at request/result/receipt serialized boundaries only.

Also create matching portable JSON Schema artifacts. Do not create a schema framework/generator.

## CLI

Implement separate CLI:

```text
node src/mat-xform/cli.ts validate <request.json>
node src/mat-xform/cli.ts materialize <request.json> --out <absolute-or-relative-binding-path> [--result <path>] [--receipt <path>] [--binding <ref>]
```

The serialized request MUST NOT choose the output root.

## Write model

v1 core is CREATE-ONLY.

Preferred safe shape:

1. parse JSON
2. Zod validate
3. preflight all paths and duplicates
4. require final output root to be absent
5. create one deterministic sibling staging directory derived from request_identity
6. write every artifact there as Buffer.from(utf8_text, "utf8")
7. calculate actual bytes + SHA-256 from written bytes
8. verify all staged bytes
9. rename staging directory to final output root on same filesystem
10. post-observe final bytes/hashes
11. emit validated result + receipt

Never overwrite an existing target root.

If failure occurs before any durable target effect:
- result_status BLOCKED or FAIL as appropriate
- effect_state NONE

If final target is fully materialized and verified:
- PASS / CONFIRMED

If a failure occurs around rename/post-observation and target effect cannot be proven absent or exact:
- UNAVAILABLE / UNKNOWN

Do not infer NONE from failure alone.

Temporary staging residue is harness-local evidence, not Product effect; clean it only when effect absence is proven. Do not blind-retry.

## Canonical request identity

Deterministically canonicalize parsed request semantics and SHA-256 it.
Output root and binding MUST NOT affect request_identity.

## Tests

At minimum:
1. 50 files in one request.
2. nested paths.
3. empty file.
4. no trailing newline.
5. LF.
6. CRLF preserved exactly.
7. UTF-8 Unicode.
8. payload containing old MAT-XFORM sentinel strings succeeds.
9. duplicate id blocked.
10. case-insensitive duplicate path blocked.
11. ../ traversal blocked.
12. absolute POSIX path blocked.
13. Windows drive path blocked.
14. backslash path blocked.
15. Windows reserved device segment blocked.
16. invalid filename chars blocked.
17. existing output root blocked with effect NONE.
18. invalid JSON / invalid contract produces no output.
19. request identity unchanged when only --out / --binding change.
20. actual hashes/byte counts correspond.
21. result validates with ResultSchema.
22. receipt validates with ReceiptSchema.
23. post-materialization root contains exactly the requested members.
24. regression fixture matching one historical MAT-XFORM batch produces the same file bytes/hashes as the historical oracle fixture (do not require TAR/sentinel identity).

## Qualification artifacts

Under experiments/TS-DEVLAB-MAT-XFORM-V1-001 produce:
- WORKER_RESULT.json
- RESULT-DRAFT.md
- fixtures/oracle-request.json or equivalent
- any bounded evidence needed

Do not claim Product adoption.
Do not merge.
