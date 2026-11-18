# R007 B1 — bounded Orca-owned Git ref admission, NONPRODUCT.
# Single exact mechanical attempt R007-B1-FETCH-A001; no inference or Product changes.
$ErrorActionPreference = 'Stop'
$expectedRoot = 'C:\Users\Mauri\orca\workspaces\ts-ee-llm040-source-20261030-001\ts-ee-oc2-notebook-free-native-20261113-001'
$oldHead = 'ad73a7df0593f9d6606959dbc97383a74d2faeb7'
$newHead = $env:TS_EE_R007_EXPECTED_BRANCH_HEAD
if ($newHead -cnotmatch '^[0-9a-f]{40}
$ref = 'refs/remotes/origin/experiment/ts-ee-oc2-notebook-free-native-20261113-001'
Write-Output 'R007_B1_FETCH_A001_PREFLIGHT'
if ((Get-Location).ProviderPath.TrimEnd('\') -ine $expectedRoot.TrimEnd('\')) { throw 'BLOCKED_ORCA_WORKTREE_ROOT' }
$before = (& git rev-parse --verify HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $before -cne $oldHead) { throw 'BLOCKED_HISTORICAL_CHECKOUT_CHANGED' }
$origin = (& git remote get-url origin).Trim()
if ($LASTEXITCODE -ne 0 -or $origin -notmatch '(?i)(github[.]com[:/]mauedgar/ts-execution-lab(?:[.]git)?)$') { throw 'BLOCKED_REMOTE_IDENTITY' }
$current = (& git rev-parse --verify $ref 2>$null)
$already = ($LASTEXITCODE -eq 0 -and $current.Trim() -ceq $newHead)
if (-not $already) {
  $env:GIT_TERMINAL_PROMPT = '0'
  try {
    & git -c core.hooksPath=NUL fetch --no-tags --no-write-fetch-head origin 'refs/heads/experiment/ts-ee-oc2-notebook-free-native-20261113-001:refs/remotes/origin/experiment/ts-ee-oc2-notebook-free-native-20261113-001' | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'BLOCKED_FETCH_NATIVE_EXIT' }
  } finally {
    Remove-Item Env:GIT_TERMINAL_PROMPT -ErrorAction SilentlyContinue
  }
}
$afterRef = (& git rev-parse --verify $ref).Trim()
$afterHead = (& git rev-parse --verify HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $afterRef -cne $newHead -or $afterHead -cne $oldHead) { throw 'BLOCKED_FETCH_POSTCONDITION_UNKNOWN' }
Write-Output ('R007_B1_FETCH_A001_PASS;REUSED=' + $already + ';REF=' + $afterRef + ';CHECKOUT_UNCHANGED=' + ($afterHead -ceq $oldHead))
) { throw 'BLOCKED_UNBOUND_IMMUTABLE_TARGET' }
$ref = 'refs/remotes/origin/experiment/ts-ee-oc2-notebook-free-native-20261113-001'
Write-Output 'R007_B1_FETCH_A001_PREFLIGHT'
if ((Get-Location).ProviderPath.TrimEnd('\') -ine $expectedRoot.TrimEnd('\')) { throw 'BLOCKED_ORCA_WORKTREE_ROOT' }
$before = (& git rev-parse --verify HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $before -cne $oldHead) { throw 'BLOCKED_HISTORICAL_CHECKOUT_CHANGED' }
$origin = (& git remote get-url origin).Trim()
if ($LASTEXITCODE -ne 0 -or $origin -notmatch '(?i)(github[.]com[:/]mauedgar/ts-execution-lab(?:[.]git)?)$') { throw 'BLOCKED_REMOTE_IDENTITY' }
$current = (& git rev-parse --verify $ref 2>$null)
$already = ($LASTEXITCODE -eq 0 -and $current.Trim() -ceq $newHead)
if (-not $already) {
  $env:GIT_TERMINAL_PROMPT = '0'
  try {
    & git -c core.hooksPath=NUL fetch --no-tags --no-write-fetch-head origin 'refs/heads/experiment/ts-ee-oc2-notebook-free-native-20261113-001:refs/remotes/origin/experiment/ts-ee-oc2-notebook-free-native-20261113-001' | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'BLOCKED_FETCH_NATIVE_EXIT' }
  } finally {
    Remove-Item Env:GIT_TERMINAL_PROMPT -ErrorAction SilentlyContinue
  }
}
$afterRef = (& git rev-parse --verify $ref).Trim()
$afterHead = (& git rev-parse --verify HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $afterRef -cne $newHead -or $afterHead -cne $oldHead) { throw 'BLOCKED_FETCH_POSTCONDITION_UNKNOWN' }
Write-Output ('R007_B1_FETCH_A001_PASS;REUSED=' + $already + ';REF=' + $afterRef + ';CHECKOUT_UNCHANGED=' + ($afterHead -ceq $oldHead))
