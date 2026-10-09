# TS-DEVLAB-MAT-XFORM-V1-001 — Repair 001

Preserve candidate 8d1f40b41d342aad62e25fd085e42780681d7ea6. Apply only these review findings. Stay inside existing owned paths. Run focused tests, commit and push branch, then stop.

## R001 — qualification claim is premature

WORKER_RESULT.json must NOT say QUALIFIED before external Web qualification.
Use:
- status: CANDIDATE
- qualification: PENDING_EXTERNAL_RECONCILIATION

RESULT-DRAFT remains a draft.

## R002 — preexisting staging must not be silently deleted

The deterministic staging path is evidence from this request identity.

Before mkdir/write:
- if staging path already exists, return BLOCKED / NONE with code STAGING_EXISTS.
- do not delete it.
- no blind cleanup/retry.

Only clean staging created by the current invocation when the current invocation has mechanically proven final target absent and owns that staging effect.

Add a test proving a preexisting deterministic staging directory remains untouched and final output is absent.

## R003 — publication paths are create-only too

Before materializing:
- if --result or --receipt path already exists, block with NONE before target write.
- if result and receipt resolve to the same path, block with NONE.
- do not overwrite publication files.
- actual writes use create-only semantics (wx or equivalent).

If a publication write nevertheless fails after materialization is already CONFIRMED:
- do not change the materialization result/effect to NONE;
- emit the materialization result to stdout and a clear publication failure to stderr / nonzero exit so the caller can reconcile.
Do not invent Product semantics.

Add tests for preexisting result/receipt and same-path publication guards.

## R004 — error observations/timings

For BLOCKED before any artifact write:
- artifact_count must represent verified/materialized artifacts (0).

For materialization failure:
- total_ms/materialization_ms must reflect elapsed execution rather than validation_ms only.

Keep result/effect separation.

## R005 — historical MAT-XFORM oracle fixture

The WP required a historical regression oracle.

Add a bounded fixture under:
experiments/TS-DEVLAB-MAT-XFORM-V1-001/fixtures/

Use this exact logical batch:
- artifact one, path nested/one.txt, text café\r\n
- artifact two, path two.txt, text 第二\r\n
- artifact three, path no-newline.txt, text no trailing newline

Record expected UTF-8 byte lengths and SHA-256 values in a separate oracle JSON.

The oracle represents expected MATERIALIZED FILE BYTES only. It does not claim sentinel transport equivalence.

Add a test that v1 materializes exactly those expected bytes/hashes.

Do not derive expected hashes inside the assertion from the v1 result itself.

## R006 — validate output boundary

The validate command's emitted result must itself pass MatXformResultSchema before serialization.

## Stop

Do not merge.
Do not edit ts-exec registry/profile files.
Do not touch Tecnotron.
Do not claim Product adoption.
