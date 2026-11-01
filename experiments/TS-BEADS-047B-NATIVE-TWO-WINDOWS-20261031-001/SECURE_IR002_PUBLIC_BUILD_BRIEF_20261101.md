# TS-BEADS 047B — self-contained public build brief after private-carrier access failure

**Authority** EXPERIMENTAL_CONTROL_ONLY. Same TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001 operation, user authorizes continuation and repair; Product authority NONE. This source is deliberately PUBLIC and contains NO credentials or private addresses. Orca is already restored; notebook host is the sole candidate Dolt writer; desktop a client.

**Source and limits:** this file and the following files in the same PUBLIC repository are the complete inputs for the next implementation worker:
- experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/DOD.md at e02c611dec74ce5d2ddcd5c169f407543ef2e3c4, Git blob 26388665fc0782fd10b24adca96a7dfa47c6a952
- experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/SECURE_HOST_PROVISIONING_REQUEST_20261101.md at f88e30cdce5a092b4a84c7a75987dba47063f00d, blob 7ebec00133736a74431516171deee614f3dbaed1
- experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/SECURE_PROVISIONING_IR002_IMPLEMENTATION_CORRECTION_20261101.md at 2e29b7206d6b8a9c8cea11ddc8b08c3c9593c50d, blob 865b1699ea362a4d7dc4939bbd98d147b5634d5e.

## Why this public self-contained brief is necessary

Private repo mauedgar/ts-execution-transport is not anonymously fetchable to the Orca OpenCode web source. The last one-shot agent 047B IR002-REPAIR-001 stopped after GitHub HTTP 404 on its private carrier, not because the pinned source was missing. It produced no verified candidate. Its original terminal is terminal; do not retry it. This new brief can be read without granting OpenCode new private repository credentials or exposing tokens.

The prior independently reviewed GPT candidate, though reported static tests 14/14, only contained a ~50-line Test-StaticPlan function which consumed a schema fixture and all-true booleans. That did not implement the secure SQL workflow. The independent IR002 security findings requiring correction are:
- F001: no actual code to generate/protect secrets, enforce ACL, start loopback SQL, harden passwordless default root, scope writer/reader, prove auth.
- F002: host/root/port/Serve/ACL/UNKNOWN “checks” were injected all-true fixture booleans, not actual native provider checks.
- F003: 14 pure-boolean tests were not provider-mocked SQL state transitions; no secure SQL client or denial tests.
- F004: grammar strings suggested wildcard principals, blanket ALL and DROP root without independently verified secure admin recovery.
A new static-only validator is NOT a repair.

## What to implement on native Windows via OpenCode2 / OpenAI GPT

Use only the public frozen files above and official documentation to implement a new secure bootstrap CODE candidate, plus mocked provider test harness, receipt and procedure. This attempt MUST NOT execute SQL, start Dolt, start Serve, create live secrets, mutate Beads or Product, or run older attempts.

Future conditional effect runner must contain:
1. Distinct future effect attempt and immutable source/owner/host grant checks. Stage Preflight is always read-only and checks actual Windows host ID, owner, pinned Dolt 2.2.0 and Beads 1.3.1 binaries, Tailscale peer/ACL, absent SQL/Serve/public forwarding, port 3307, no previous/UNKNOWN provider writes; checks exact canonical isolated %LOCALAPPDATA%\TS-BEADS-047B path, reparse/symlink/collision/ACL. Missing evidence blocks.
2. Windows CSPRNG independent admin/writer/reader secrets and a real user-scoped DPAPI or Credential Manager implementation with restricted ACL. Secrets never appear in public Git, arguments, child process list, environment output, logs, PowerShell transcript, stdout/stderr, or portable receipts. If no secure in-memory MySQL/Dolt client adapter can be implemented with verified dependencies, stop BLOCKED_SECURE_SQL_CLIENT_UNAVAILABLE. Do NOT pass plaintext SQL commands with credentials via a shell process.
3. Separate no-secret Dolt SQL YAML config explicitly binding 127.0.0.1:3307 with isolated data_dir, cfg_dir and privilege_file. Local OS filesystem users with access to dolt sql can bypass SQL grants: protect the directory and never claim SQL read-only user bars privileged local CLI.
4. Correct first-boot passwordless root@localhost handling: ensure Serve remains DISABLED; create and authenticate a secured recovery admin before removing the passwordless root. Standard CREATE USER / DROP USER / GRANT are supported; ALTER USER and SET PASSWORD are listed NOT SUPPORTED in current official access-management docs. Confirm the pinned native 2.2.0 behavior before actual effects. Restrict principal host patterns; no public root@%, no destructive drop of last admin; local read-only/incorrect-password/anonymous tests must be real future postconditions.
5. One attempt, one process, explicitly fenced and journaled sequence: integrity/parser, host/provider preconditions, conditioned SQL start, immediate root hardening/admin/writer/reader setup, tests of auth, grants and lack of network exposure, compact sanitized original terminal receipt. If any partial/UNKNOWN effect occurs, preserve state and do not retry/rollback/cleanup automatically. Future tailnet ingress is a separate step after hardened local SQL and access review; never Funnel or public listener.
6. Include working tests with injected providers that simulate each security step and assert EXACT expected failure reasons and that no later effect executes after a block. Tests for wrong host/device, binary/grammar, existing lab root/reparse/ACL, port occupied, unexpected Serve, prior UNKNOWN, CSPRNG/DPAPI failure, SQL connector unavailable, root credential not hardened, bad writer privileges, reader mutation, invalid credentials, crash/recovery and receipt. No all-true runtime implementation; pure mocks only in test mode.

**Reviewability:** produce code that can actually implement the future effect if its dependencies are present; no 50-line documentation-only stub. Provide source, tests, provider-contract and operator procedure, original mock results, parser/integrity hashes. If not feasible, produce precise BLOCKED evidence specifying missing native Dolt 2.2.0 support or SQL library, not false PASS.

## Source access and publication

Public repo is mauedgar/ts-execution-lab, experimental branch experiment/beads-047b-native-two-windows-20261031-001. Use pinned GitHub raw public URLs or local Git checkout after verifying commit. Do not attempt private Transport as first input, do not scan unrelated worktrees, do not use WSL/bash/Unix ls -la/head/grep on Windows.

Publish nonsecret candidate and receipts into the PUBLIC experiment directory under unique IR002 public-build attempt identity, never modifying frozen previous candidate and never committing Product or secrets. If Git auth to lab is insufficient, preserve locally with original hashes and report precise BLOCKED; do not build a parallel publisher or retry. ChatGPT Web independent review will validate and can mirror a sanitized result to private Transport via its connector.

**Dolt reference sources:** https://www.dolthub.com/docs/sql-reference/server/access-management/ ; https://www.dolthub.com/docs/sql-reference/server/configuration/ ; https://www.dolthub.com/blog/2025-02-05-sql-server-removes-user-pass-args/ . Verify native 2.2.0 before effects; no assumption that modern documentation is exact for local binary.

**Overall verdict remains:** HOST_INDEPENDENCE_INCOMPLETE until secure SQL, two-host Beads graph continuity, failure/recovery and backup are empirically tested under later grants.
