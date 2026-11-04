# One-shot mechanical Windows wrapper for an already-resident WSL R1 runner.
# Do not use Commander to materialize sources, discover repositories, or run OpenCode semantics.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$RunnerPathWSL,
    [Parameter(Mandatory=$true)][string]$LabPathWSL,
    [Parameter(Mandatory=$true)][string]$ProductPathWSL,
    [Parameter(Mandatory=$true)][string]$ExpectedLabSHA,
    [Parameter(Mandatory=$true)][string]$ResultRootWSL,
    [Parameter(Mandatory=$true)][string]$AttemptID,
    [string]$Distro = 'Ubuntu'
)
$ErrorActionPreference = 'Stop'
if ($ExpectedLabSHA -cnotmatch '^[a-f0-9]{40}$' -or $AttemptID -cnotmatch '^[A-Za-z0-9_-]{1,50}$') {
    throw 'BLOCKED_PRECONDITION|invalid-subject-or-attempt-identity'
}
foreach ($p in @($RunnerPathWSL, $LabPathWSL, $ProductPathWSL, $ResultRootWSL)) {
    if (-not $p.StartsWith('/') -or $p.Contains([char]0)) {
        throw 'BLOCKED_PRECONDITION|absolute-wsl-path-required'
    }
}
if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    throw 'BLOCKED_PRECONDITION|wsl-exe-unavailable'
}
# The Linux runner owns the strict Git identity check, immutable attempt reservation,
# Docker readiness, execution, receipt, and cleanup. No git/gh/opencode here.
& wsl.exe -d $Distro -- bash $RunnerPathWSL $LabPathWSL $ProductPathWSL $ExpectedLabSHA $ResultRootWSL $AttemptID
$rc = $LASTEXITCODE
if ($null -eq $rc) { throw 'UNKNOWN|wsl-returned-no-exit-code' }
if ($rc -ne 0) {
    Write-Output "BLOCKED_OR_FAILED|exit=$rc|subject=$ExpectedLabSHA|attempt=$AttemptID"
    exit $rc
}
Write-Output "PASS|WINDOWS_WRAPPER|subject=$ExpectedLabSHA|attempt=$AttemptID|verify_linux_terminal_receipt=true"
exit 0
