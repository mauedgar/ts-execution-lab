# TS EE E3 — Controlled context/coverage comparison
Responsibility: TS-EE-E3-WEBINLINE-COVERAGE-20261119-001.
Authority: EE_NONPRODUCT_ONLY. Product_effect: NONE.
Candidate: same immutable fixture at frozen commit, with 13 source modules + 3 tests + one contract.
Two separate-context reviewer arms with distinct Review_IDs:
A = historical-style plain path listing + Git refs; B = bounded, byte-complete multi-file review packets + explicit per-file evidence contract.
Do not expose control/ORACLE_PRIVATE_DO_NOT_SEND_TO_REVIEWERS.json to reviewers.
Two arms must inspect identical primary source bytes, same requirements, same verdict schema, and no product changes.
Metrics: #FULL_READ (verified by per-file evidence and exact blob), omitted, 8 seeded defects recalled, false positives in two benign modules, 4 cross-file checks, original transport, observed time and tool calls (where measurable). No fabricated tokens or performance deltas.
Critical invariants: independent contexts, no duplicate run, no reuse of historical IR findings as new model output; CI good does not imply FULL_READ. Control-only oracle may be opened after terminal originals have been frozen.
Decisions: RECOMMEND_METHOD only with evidence; no Tecnotron adoption before competent disposition.
