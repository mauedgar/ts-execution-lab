# TS-BEADS 047B - V6P2 test-source and LF checkout correction

This is a NEW experimental source-only candidate. Frozen V6P1 is immutable: mauedgar/ts-execution-lab@0118028c2508c2ce274fd42240f847adf7ff2187.

Executable PowerShell bytes in candidate/ and both PowerShell test files are exactly reused from V6P1. The sole source test fix is in tests/test_source_contract.py: setUpClass now uses cls.runner_source instead of shadowing unittest.TestCase.run, with all references updated accordingly. This correction was proven on a temporary copy in native Windows Actions run 41386952103, attempt 1, original receipt artifact 13116000934.

This directory contains a local .gitattributes that pins LF endings for PS1/PSM1/PY/MD/JSON independent of Windows core.autocrlf. CI must additionally pin Git core.autocrlf=false before checkout and verify raw byte-length, SHA256, Git blob, no CR, no BOM. Never normalize a failing hash in place.

Not dispatchable. SourceOnly=true. No trusted issuer provisioned, no competent SQL grant, no real off-host CAS, no host independence proof, no Product authority, no TaskCycle, no Kernel migration. Require independent review of this new exact candidate, then a distinct bounded native proof if authorized.
