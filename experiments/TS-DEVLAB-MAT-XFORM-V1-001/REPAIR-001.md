# MAT-XFORM v1 — Repair 001

Preserve candidate 8d1f40b41d342aad62e25fd085e42780681d7ea6. Apply only these findings.

1. WORKER_RESULT must not claim QUALIFIED before independent Web qualification.
   - use CANDIDATE_READY_FOR_QUALIFICATION or equivalent.

2. Staging residue safety:
   - deterministic staging path may already exist from an earlier attempt.
   - pre-existing staging MUST be BLOCKED/NONE before writes.
   - never delete a staging directory unless this invocation itself created it.
   - add a test proving a pre-existing staging directory and its contents are preserved.

3. Result/receipt publication is create-only:
   - never overwrite an existing --result or --receipt file.
   - preflight publication paths before materialization so a known conflict blocks with effect NONE.
   - add tests.

4. Historical MAT-XFORM compatibility oracle:
   - add one static oracle fixture representing a batch valid under the historical MAT-XFORM protocol.
   - prove v1 emits the exact same requested file bytes and SHA-256 values for that batch.
   - member-byte equivalence only; do not claim transport/framing identity.
   - oracle artifacts:
       artifact_id: oracle-a
       relative_path: nested/a.txt
       utf8_text: "alpha\n"
       expected_bytes: 6
       expected_sha256: sha256:b6a98d9ce9a2d9149288fa3df42d377c3e42737afdcdaf714e33c0a100b51060
     and:
       artifact_id: oracle-b
       relative_path: b.txt
       utf8_text: "café\r\n"
       expected_bytes: 7
       expected_sha256: sha256:7f2adbdb77890209f13a322e75d8aa13b9169722e702a2e367250125d33e8832
   - mark fixture source as HISTORICAL_PROTOCOL_COMPATIBILITY_ORACLE, authority NONE.

5. Keep JSON + TypeScript + Zod boundary and separate utility.
   - no ts-exec registry/profile change
   - no workflow changes
   - no Tecnotron edits

Run focused tests. Commit/push branch. Do not merge.
