# TS R3 experimental Codespaces locked-install qualification v1

Owner: TS_EXECUTION_ENGINEERING. Product authority/effect: NONE. The provider is GitHub Codespaces; this is a bounded qualification, not a new Product actor, scheduler, TaskCycle or migration.

## Scope / authority

The runner is for exactly one original execution attempt of a **credential-free** native Node22 and locked `pg` installation on a GitHub Codespace. It never runs Neon, uses no PostgreSQL URLs, does not change Product, and does not authorize physical A/B continuity.

Target is the **existing** 2-core Codespace `reimagined-zebra-pwj5g6wpg4ghrqr6`, repository `mauedgar/ts-execution-lab`. This is not permission to create another Codespace. The source is in isolated new Git branch `ee/ts-r3-codespaces-locked-npm-v1-20261106-001`, created from experimental commit `f0827f52b6a1795bcce3cdc90edc1c633193da77` (tree `81eb12bfa0b9b7f50be24239c167a7b3452c441a`). Its source commit/tree must be read from GitHub after publication and remain pinned at execution.

Node CLI arguments: `node r3-codespaces-locked-npm-v1.cjs TS-R3-CS-NATIVE-20261106-001-A01 <exact-frozen-commit> <exact-frozen-tree>`. These are authenticated only through a separate provider-bound execution receipt, NOT by the JSON produced locally.

## Preconditions

- OS Linux; native Node v22.x and Git available; no `TS_R3_DATABASE_URL` in environment. Uses only a fixed public npm registry and strips auth-bearing variables before running npm. No project-local `.npmrc`.
- Trusted private workspace with checkout pinned to frozen candidate, clean tracked files, and immutable/exclusive access during the attempt. Git HEAD, tree and pinned Git blobs validated before any install.
- Fixed `r2-node/package-lock.json` Git blob `8241c9d02d2da25a11b2d6c16e0c6fc64aaf2835`, `package.json` blob `fa733e5bc20c5c257a042df9bfbea5377a6c7018`, portable preflight blob `044c517c631f225e2c476046b163f53ad6b11a21`, existing durable attempt module blob `c031704445f08ce04de3d61a96fc7d9da423d03f`. Exactly 18 npm packages pinned to `registry.npmjs.org` with SHA512 integrity metadata.
- No same attempt directory exists at `$HOME/.ts-r3-codespaces-attempts/TS-R3-CS-NATIVE-20261106-001-A01`; if it does, stop without re-dispatch even if receipt is partial.

## One-shot mechanics

After read-only preconditions, the runner makes its exclusive attempt directory and fsyncs its parent, creates a claim/receipt via the existing verified `durableCreate` helper (create-only, full write, fsync file + directory, verified readback). The claim is durably established BEFORE `npm ci`; a crash, ambiguous exit, or partial artifact prohibits retry under the same ID. It executes once, via `spawnSync` without shell, `npm ci --ignore-scripts --no-audit --no-fund`, then checks installed package.json name/version of the 18 lockfile entries, runs once `npm ls --all --depth=20`, and runs the unchanged Node22 read-only portable preflight. No package scripts, SQL, secrets, browser automation or GitHub Actions. Bounded time/output.

Original compact stdout records outcome, attempt ID, SHA256 receipt, installed package count and failure class. Local `claim.json` / `receipt.json` in Codespace is NOT a GitHub-signed native provider receipt and MUST be independently transported with provider binding before durable evidence is claimed. Manual stdout/readback cannot prove cryptographic GitHub device attestation or physical persistence. On error/UNKNOWN preserve artifact and refrain from retry. Codespaces stopped state saves storage while preventing further compute costs; it does not guarantee immutable checkout or indefinitely durable receipts.

## Test ceiling and deferred gates

Native local synthetic fixture suite 22/22 PASS on Node v22.16.0. This test uses a deliberately isolated shim of previously independent-reviewed `r3-offline-attempt-v1.cjs` and a stubbed `npm` child; it proves only this runner's control logic. Actual Codespaces Linux + real npm clean install and original native provider run NOT_RUN at publication. Windows native, actual pg import/real DB/TLS, separate host credentials, P01–P10 A/B recovery, real lost ACK, and autonomous running when notebook is off remain NOT_RUN. External A001–A004 are NOT closed by these synthetic tests.

Cost guard: existing verified Codespace is Shutdown at last provider-native observation; only user-authorized free included use. Stop same instance after terminal result; do not create/retry resources. Previously denied GitHub Actions workflow-creation effect is still DENIED and never routed via another provider.
