# TS-BEADS 047B: IR002 advisory repair, source-only OS observation.
# NO SQL, NO external CLI invocation, NO privileged mutation, NO Product effects.
# Original IR001/IR002 candidate and ExecutionAttempt identities are immutable.
[CmdletBinding()]
param(
    [ValidateSet('Inspect','Execute')][string]$Mode = 'Inspect'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ownerHost = 'DESKTOP-DJLBEQH'
$doltSha256 = 'DF49F737CB80FC0F32B02220C701F476D378F322FA1BB51D696728FDAE825B91'
$bdSha256 = '280517091DDA13CB195A39F991144771117B2BC26A4D472612F8FC9FD80F46E2'

# All effects are denied before host inspection, argument use or OS APIs.
if ($Mode -ceq 'Execute') {
    'BLOCKED_UNADMITTED_EFFECT_NO_TRUSTED_ORIGINAL_RECEIPT'
    'NO_SQL_OR_TAILSCALE_EFFECT'
    exit 41
}
function Assert-NoReparseAncestor {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path) -or
        -not [IO.Path]::IsPathFullyQualified($Path)) { throw 'BLOCKED_INVALID_PATH' }
    $cursor = [IO.Path]::GetFullPath($Path)
    while ($true) {
        if (-not [IO.Directory]::Exists($cursor)) { throw 'BLOCKED_ANCESTOR_MISSING' }
        $attrs = [IO.File]::GetAttributes($cursor)
        if (($attrs -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw 'BLOCKED_REPARSE_ANCESTOR'
        }
        $parent = [IO.Directory]::GetParent($cursor)
        if ($null -eq $parent) { break }
        $cursor = $parent.FullName
    }
}
# Path-guard regression fixtures are isolated in hosted Windows tests only.
function Assert-ExactBinary {
    param([string]$Path,[string]$Sha256)
    if (-not [IO.File]::Exists($Path)) { throw 'BLOCKED_BINARY_ABSENT' }
    if ((Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash -cne $Sha256) {
        throw 'BLOCKED_BINARY_IDENTITY'
    }
}
try {
    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT -or
        [Environment]::MachineName -cne $ownerHost) { throw 'BLOCKED_HOST' }
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    if ($null -eq $identity -or $null -eq $identity.User -or
        $identity.User.Value -notmatch '^S-1-5-21-') { throw 'BLOCKED_SID_FORMAT' }

    # Hash binary bytes but do not invoke unqualified third-party CLIs.
    # Versions and Tailscale status/Serve/Funnel must be observed in a later
    # separately-qualified, exact-hash, read-only mechanical stage.
    $dolt = 'C:\Program Files\Dolt\bin\dolt.exe'
    $bd = Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages\GasTownHall.Beads_Microsoft.Winget.Source_8wekyb3d8bbwe\bd.exe'
    Assert-ExactBinary $dolt $doltSha256
    Assert-ExactBinary $bd $bdSha256

    if (@(Get-Process -Name dolt -ErrorAction SilentlyContinue).Count -ne 0) {
        throw 'BLOCKED_DOLT_PROCESS'
    }
    # Only known likely service ports can be screened without a service
    # inventory and provider reconciliation; alternate listeners UNKNOWN.
    $listeners = @(Get-NetTCPConnection -State Listen -ErrorAction Stop |
        Where-Object { $_.LocalPort -in @(3306,3307,3308,14337) })
    if ($listeners.Count -ne 0) { throw 'BLOCKED_POSSIBLE_SQL_LISTENER' }

    $base = [IO.Path]::GetFullPath($env:LOCALAPPDATA).TrimEnd('\')
    Assert-NoReparseAncestor $base
    $root = [IO.Path]::GetFullPath((Join-Path $base 'TS-BEADS-047B'))
    if (-not $root.StartsWith($base+'\',[StringComparison]::OrdinalIgnoreCase)) {
        throw 'BLOCKED_ROOT_CONTAINMENT'
    }
    if (Test-Path -LiteralPath $root) { throw 'BLOCKED_EXISTING_ATTEMPT_OR_DATA' }

    'READONLY_OS_OBSERVATION_PARTIAL'
    'BINARY_HASH_ONLY_VERSION_UNVERIFIED'
    'TAILSCALE_AND_PEER_STATE_UNVERIFIED'
    'ALTERNATE_SQL_LISTENERS_UNVERIFIED'
    'SID_PIN_AND_ACL_UNVERIFIED'
    'REPARSE_SNAPSHOT_NOT_ATOMIC'
    'PROVIDER_ORIGINAL_ATTEMPT_UNVERIFIED'
    'SQL_DPAPI_BACKUP_RESTORE_UNVERIFIED'
    'NO_SQL_OR_TAILSCALE_EFFECT'
    exit 0
} catch {
    # No system paths, usernames, tailnet names or stack traces in receipts.
    'BLOCKED_READONLY_OS_OBSERVATION'
    'NO_SQL_OR_TAILSCALE_EFFECT'
    exit 11
}
