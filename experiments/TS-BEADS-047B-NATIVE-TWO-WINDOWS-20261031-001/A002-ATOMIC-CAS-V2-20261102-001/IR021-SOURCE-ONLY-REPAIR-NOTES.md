# TS-BEADS 047B A002 — IR021 source-only follow-up (experimental)

Parent source `mauedgar/ts-execution-lab@d44c1b50808c7607364eec6c33113786b2582105`, exact tree `bcb600ca4e174fc135ff7edc6747c08c15059f0b`.
Frozen independent IR021 original `libfile_63bca8d0d3b0819189360bfdaa8c9612` / SHA256 `52e45bc41439a4d153b470a60caef86072900157a89f517f3e853c3784df8152`.
Control disposition `mauedgar/ts-execution-transport@db0df3d155b185d1379f49ab92d440e55b1bc17f:results/TS-BEADS-047B-A002-V2-IR021-20261103-001/CONTROL_POST_REVIEW_DISPOSITION.md`.

**Changes limited to source and synthetic tests.**
- A02: remove 400-character truncation before classifier; original bounded decoded response is still captured before parse.
- A06: reject mixed success/data and errors; reject malformed top-level/error objects; add HTTP 401 and malformed synthetic negatives, plus pure helper body/hash/sensitive/oversize tests.
- A03: accurately label the response.Content bytes as decoded content re-encoded to UTF-8, not byte-identical HTTP wire bytes. Expand conservative secret recognition; suspicious or >65536-byte content becomes UNKNOWN without body bytes in journal.
- A01: assumed GitHub error code/message taxonomy remains unresolved and can only fail closed. No synthetic PASS establishes real provider behavior.
- A04: off-host journal upload, crash recovery and receipt retention remain blocked by F03-02/F04.
- A05: no durable multi-dispatch fence, no two-host CAS, no host-independence proof. Historical UNKNOWNs must not be retried.
- No modification to G0/ALPHA/BETA or target ref, no effects workflow, no Product, Beads or Dolt action.

**Safety:** the test extracts two pure functions with PowerShell AST, never dot-sources the top-level effect runner. The source-only CI has `contents: read`, no GH_TOKEN, no write/API mutation. Its PASS, if observed, is only a source-test result. New candidate requires independent IR before any wider recommendation.

**Disposition at candidate creation:** `SOURCE_ONLY_CANDIDATE_UNREVIEWED / F03-02_BLOCKED / F04_BLOCKED / NO_GO_CAS_MUTATION`.
