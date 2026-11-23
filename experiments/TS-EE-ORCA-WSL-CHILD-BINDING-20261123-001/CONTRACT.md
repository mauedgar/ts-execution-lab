# Orca/Windows/WSL direct leaf source experiment, TS EE 004

status: SOURCE_ONLY_UNREVIEWED
authority: TS_EXECUTION_ENGINEERING_NONPRODUCT_ONLY
Product_authority: NONE
Product_effect: NONE

The previous E1 attempt remains terminal PARTIAL. A new native E2 negative
exit1 test had original Orca exitCode=1 and exact close but did not retain Linux
PID/UID/namespace/exit original. The next nested /bin/sh -c marker attempt
ended native invalid_argument with effect NONE; it MUST NOT be retried.

This candidate uses one bounded PowerShell 7 -File runner with explicit
ProcessStartInfo.ArgumentList and fixed Linux Python /usr/bin/python3 -I -c
argv, instead of building nested Orca, PowerShell and Bash quoting.
SelfTest is source-only, executes six negatives, and never starts WSL or Orca.
Native execution is NOT authorized by CI. It would need:
- separate source review and stable reviewed runner SHA
- original current authenticated Orca runtime, visible owned terminal, worktree,
  host and incarnation bound to one native ExecutionAttempt
- create-only materialization at the exact isolated approved host path using
  an already installed and hash-verified XForm extractor with a qualified
  UTF8 TXT envelope (TS-EXB); no arbitrary Commander file edits or script builds
- exact native runner invocation via pwsh.exe -NoLogo -NoProfile
  -NonInteractive -ExecutionPolicy Bypass -File followed by the isolated script,
  Mode Native and caller-pinned SHA256, with source hash and mode checked
- provider-native original WSL/Windows PID, terminal exit and result byte
  readback, then exact owned terminal close and independent nonProduct IR.

The Linux marker prints PID/PPID/UID/pid namespace from /proc and Linux
process APIs, but this is still carried through Windows/WSL stdout and
not cryptographic cross-kernel PID attestation. Output is a create-only
source-limited local receipt; the caller must independently join Orca native
runtime/host/handle and original source digest. Any missing evidence is
PARTIAL, BLOCKED_PRECONDITION or UNKNOWN, never assumed success.

Source CI on disposable Windows Actions executes SelfTest ONLY; it does
not access user's notebook, Orca, WSL or Product. No canonical Product effect.
