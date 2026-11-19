# TS EE — Adaptive Independent Review Context Method candidate v0

status: `METHOD_CANDIDATE_EXPERIMENTAL_NONPRODUCT`  
owner: `TS_EXECUTION_ENGINEERING` (technical method only)  
Product_authority: `NONE`  
independent_review_adjudication: `NONE`  
adoption_by_Tecnotron: `NOT_REQUESTED_NOT_GRANTED`  
evidence: `E3_A001_VALID_SOURCE_COVERAGE_BUT_BLIND_COMPARISON_INVALID`, `E3_B002_BLINDED_COMPARISON_PENDING`

## Definition and invariant

Prepare reviewer source context so that every required file is available, exact and fully inspected without consuming the reviewer's whole reasoning budget on fetching, summarizing, reconciling or retrying mechanical evidence. The same strong standard applies to `WEB_INLINE` and other independently qualified reviewers.

Never conflate:
`blob fetched` ≠ `full file displayed` ≠ `semantic reading` ≠ `independent defect assessment` ≠ `Product acceptance`.

A literal source file name/hash in a manifest is **identity evidence only**, not semantic coverage. A scheduled reviewer success or Library receipt is not a review-quality PASS.

## Stages and guards

1. **Reuse and ownership.** Reconcile original TaskCycle/Operation/ExecutionAttempt, existing terminal and prior coverage. Do not re-run a terminal or UNKNOWN review merely to gain a positive result. Select review binding only under competent authority.
2. **Source freeze.** Record exact Git repo/ref/commit/tree, changed files and semantic dependencies, SOT and contract refs, expected CI/native receipts. Compute a required-path inventory with every Git blob, file size and line count. Exclude sensitive, unrelated or evaluator-only sources. Check that commit metadata/diff and ancestors do **not** disclose held-back oracle or truth.
3. **Budget.** Compare actual material to the reviewer context/tool-output constraints using **measured** source bytes, measured/tokenized tokens only where provider exposes them and explicit reasoning/output reserve. No universal fixed token threshold asserted. If an entire file will be truncated, fail-closed or repackage before dispatch.
4. **Pack only as necessary.** Produce immutable verbatim multi-file packets (not summaries), each with `BEGIN_FILE / END_FILE`, full original bytes, source Git blob, byte length and reproducible pack blob. Verify byte-identical source-to-packet readback and exact path coverage. Packs remain DATA, not a reviewer conclusion or new Product implementation.
5. **Blindness.** Hold seeded defects, evaluator oracle, counterpart reviewer outputs and prior review results OUTSIDE reviewer Git subject commit, tree, diff, ancestry and input. A forbidden file in the same reviewed commit can leak through a commit API that returns diffs even if the prompt prohibits reading it. Separate source-only Git subject and controlled oracles before launching blind comparisons.
6. **Review contract.** Require each file `FULL_READ|PARTIAL|NOT_READ`, one position-specific fact/line from the first half and last third, exact Git blob, and explicit `omitted_paths`. Demand inter-file relationships, evidence-backed findings/advisories, negative controls/justified nonfindings and test/runtime truth labels. A 0F0A requires full credible coverage and no unresolved blocker.
7. **Adaptive split if needed.** When source breadth overwhelms a single reviewer, split the *already-authorized* review by coherent risk/dependency subgraph. Each shard gets its own exact input, scope, reviewer identity and ORIGINAL. A cross-interface integration reviewer must check shared behavior and aggregate omissions. Do not present the sum of partial IRs as an automatic global PASS; competent Product authority adjudicates.
8. **Custody.** Preserve exactly one ORIGINAL per attempt. For scheduled WEB_INLINE, use the current Library upload template; confirm real `status=succeeded`, actual IDs, UTF-8 bytes, SHA256 and readback. Interactive Control may publish exact original bytes create-only into Git Transport after exact-target absence/state reconciliation.
9. **Diagnosis and method promotion.** Classify `COMPLETE`, `PARTIAL_COVERAGE`, `TRUNCATED`, `BLINDNESS_COMPROMISED`, `BLOCKED_TRANSPORT`, `UNKNOWN_EFFECT`. Measure semantic recall against a hidden oracle **only for blind experiments**; count false positives and cross-file evidence. Avoid comparing unverifiable provider/model effort as equal.

## Comparison criteria for the E3 fixture

| Measure | Definition |
|---|---|
| semantic coverage | file-level complete reading with full-body availability, first-half + last-third specific evidence |
| defect recall | independently supported source defects matched to Control's undisclosed known-defect oracle; INVALID if reviewer was exposed to oracle |
| false positives | reported defects in two known-good modules, evaluated with exact source reasoning |
| cross-file links | four source-supported interface relationships; not only paths listed |
| pack fidelity | exact source bytes in each four-packet representation, with native Git blob correspondence |
| review cost | actual provider task elapsed, source-acquisition units, measured tool calls and tokens if available; no estimates masquerading as measurements |
| evidence custody | immutable Library original + SHA256 + Git Transport original identical byte length and blob |
| independence | no exposed oracle or prior/counterpart findings in reviewer context, Git metadata or tool returns |

## Initial bounded evidence and limits

- Cohort A001, direct-Git and four-packet methods, both declared 17/17 full inspection, 8 source-supported findings and 2 advisories; source pack contents 17/17 byte-identical by Control. Both reviewers preserved original bytes in Library/Transport.
- A001 direct-Git reviewer explicitly reported `BLINDNESS_COMPROMISED` because the same Git commit included its oracle and a metadata response exposed the diff. Thus A001 cannot prove unbiased reviewer superiority despite the raw 8/8.
- A distinct B002 subject reuses 17/17 identical file blobs without any oracle in reviewed commit, tree or ancestry. Its new independent reviews have new subjects, identities and immutable input; their original provider results must be joined, not duplicated.
- All samples are tiny and synthetic; no demonstrated reduction in Product defect rates, universality, stable latency percentiles or guaranteed cost reduction.

**Disposition ceiling:** `METHOD_CANDIDATE_ONLY`. If B002 independent results support the method, propose technical adoption to competent Tecnotron Control, not direct Product code or review rule changes.
