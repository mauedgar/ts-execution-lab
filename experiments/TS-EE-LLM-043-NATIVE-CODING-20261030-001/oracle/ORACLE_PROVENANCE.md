# LLM 043 — Independent validation oracle

Authority: experimental only. **Not visible to coding models**, because role permissions authorize reads only under each role's local source/test/package files. The oracle lives in a separate Git branch and is run in a fresh GitHub Actions environment after model attempts terminate.

Source of requirements: the user-authorized `TS-EE-LLM-042` frozen work package and `TS-EE-LLM-043/DOD.md`. Tests check previously specified six-decimal rounding, exact error classes, duplicate validity, deterministic grouping, tie handling and UNKNOWN preservation.

There are four oracle tests per responsibility, independent of the nine published task tests. This oracle was authored after observing 2 preliminary patches, so it is **not a prospective double-blind benchmark**; do not imply otherwise. It is a separately executed semantic contract check, with no model writing test files or editing validation code.

CI may produce a red oracle for a candidate; this is a valid, preserved result. Never merge or auto-correct model candidates to erase failures.
