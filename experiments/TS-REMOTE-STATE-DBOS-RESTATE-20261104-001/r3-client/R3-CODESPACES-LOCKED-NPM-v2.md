# TS R3 — Codespaces credential-free locked npm qualification v2

Owner: TS_EXECUTION_ENGINEERING. Experimental only, no Product/Neon authority. This version repairs independent IR001 F001–F003 of the earlier Codespaces npm runner; reviewed predecessor `mauedgar/ts-execution-lab@f075f0eb47074a0114c38698e7d2d4f767d5266b` remains frozen and unexecuted.

## One-shot execution envelope

Target only original Codespace `reimagined-zebra-pwj5g6wpg4ghrqr6` (2-core). Do not create or rerun resources. Use an exact GitHub-origin, Control-verified single-commit branch whose immediate parent is `f075f0eb47074a0114c38698e7d2d4f767d5266b` and whose entire diff adds only this runner, its tests and this notes file. The authoritative exact final commit SHA/tree and code blobs must be frozen in a separate GitHub Transport request before any execution. Checkout on Codespace must be exclusive, clean, and provider-bound; local Git checks cannot cryptographically attest remote provider identity. The runner checks the parent anchor and allowed three-file diff plus own Git tree blob, no untracked or modified files, and repeats git identity and tracked/untracked status post-install.

Invoke one time with fixed attempt ID:

`node r3-codespaces-locked-npm-v2.cjs TS-R3-CS-NATIVE-20261106-002-A01 <frozen-exact-commit> <frozen-exact-tree>`

The shell / caller must verify the exact commit/tree with GitHub authenticated connector before dispatch, bind the native provider resource ID and original run receipt, and invoke only the frozen script at that commit. Arbitrary commit/tree inputs are rejected if they do not have the pinned parent anchor, exact three-file change-set and source git-blob identity. No Product or provider acceptance is conferred by hashes alone.

## Precondition and side effect

- Node v22.x required; fixed `r2-node/package.json` blob `fa733e5bc20c5c257a042df9bfbea5377a6c7018`, lock blob `8241c9d02d2da25a11b2d6c16e0c6fc64aaf2835`, existing native portable preflight blob `044c517c631f225e2c476046b163f53ad6b11a21`, and durable claim helper blob `c031704445f08ce04de3d61a96fc7d9da423d03f`.
- 18 lock entries, each with exact `https://registry.npmjs.org` host, canonical SHA-512/64-byte digest, name and version matching the final installed package metadata. `npm ci` itself validates registry tarballs per lockfile, but this adapter **does not independently hash installed executable bytes**; success is deliberately `PASS_NPM_LOCK_INSTALL_METADATA`, not full source attestation.
- Strip all child environment variables except bounded `PATH`, default locale and fixed flags. Child npm runs with new isolated `$HOME`, `$TMPDIR` and npm cache, config paths `/dev/null`, fixed public registry, strict TLS and no proxy env; forbid project-local `.npmrc`, direct database URL, or inherited NPM token. No lifecycle scripts (`--ignore-scripts`), audits, funds, GitHub Actions or SQL.
- Before any npm install, create-only unique attempt directory at `$HOME/.ts-r3-codespaces-attempts/TS-R3-CS-NATIVE-20261106-002-A01`, fsync parent and `claim.json` using independently reviewed durable helper. Any existing attempt directory, even partial, blocks replay. `npm ci` executes **once**. Subsequent `npm ls` and read-only preflight are bounded. Child error, timeout, signal and package mismatch yield conservative BLOCKED/UNKNOWN classes, not auto-retry.
- Create-only fsync'ed `receipt.json` after outcome; never unlink partial artifacts. Local hashes and JSON receipts are not signed native provider attestation. Provider filesystem durability, exclusive checkout, OS sandbox, post-crash recovery and credential custody remain separate gates.

## Qualification limitations

Native ChatGPT-local Node v22.16.0 **29/29 PASS** in synthetic isolated fixtures: npm/git/preflight process mocked, durable helper test shim. This proves source control flow only, not actual `npm ci`, network trust, existing Codespace, Windows/Linux filesystem power loss, TLS, real Neon DB, host A/B P01–P10 or autonomous no-notebook execution. Original IR001 NO_RECOMMEND remains historical; this new candidate requires distinct independent IR002 before remote dispatch. A001–A004 external proof (native package integrity, provider attestation, workspace isolation/durability and real physical continuity) are NOT waived.

Cost guard: Codespace original was observed `Shutdown` by provider-native GitHub CLI; only permitted included quota, 2 cores. Stop the same Codespace after terminal outcome; never create another/replay original GitHub Actions denied workflow. No Product integration, migration, phase 2 or State Kernel retirement.
