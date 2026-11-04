# TS-BEADS 047B IR001 source repair. This file is deliberately NON-EFFECTFUL.
# No source, grant JSON, command-line digest or caller assertion can admit SQL.
# The original effectful candidate is immutable at 404c358cb9717dd5446deae154afd576ede543ba.
[CmdletBinding()]
param(
    [ValidateSet('Inspect','Execute')][string]$Mode = 'Inspect'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$attempt = 'TS047B_NOTEBOOK_OFFLINE_BOOTSTRAP_20261103_001'
$ownerHost = 'DESKTOP-DJLBEQH'
$doltSha256 = 'DF49F737CB80FC0F32B02220C701F476D378F322FA1BB51D696728FDAE825B91'
$bdSha256 = '280517091DDA13CB195A39F991144771117B2BC26A4D472612F8FC9FD80F46E2'

# F001/F004: an unadmitted effect cannot be made safe by caller-chosen hashes.
# Always deny BEFORE querying host or creating any local object. No replay path.
if ($Mode -ceq 'Execute') {
    'BLOCKED_UNADMITTED_EFFECT_NO_TRUSTED_ORIGINAL_RECEIPT'
    'NO_SQL_OR_TAILSCALE_EFFECT'
    exit 41
}

function Assert-ExactBinary {
    param([string]$Path,[string]$Sha256,[string]$Name)
    if (-not [IO.File]::Exists($Path)) { throw ('BLOCKED_'+$Name+'_ABSENT') }
    $actual = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
    if ($actual -cne $Sha256) { throw ('BLOCKED_'+$Name+'_HASH') }
}
function Assert-NoReparseAncestor {
    param([string]$Path)
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
function Assert-NoProxy {
    param([string]$Tailscale,[string]$Kind)
    # Neither tailnet addresses nor raw output may be printed to a receipt.
    $raw = (& $Tailscale $Kind status --json 2>$null | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($raw)) {
        throw 'BLOCKED_PROXY_UNAVAILABLE'
    }
    $json = ConvertFrom-Json -InputObject $raw -AsHashtable -ErrorAction Stop
    if ($null -eq $json -or $json -isnot [System.Collections.IDictionary] -or $json.Count -ne 0) {
        throw 'BLOCKED_PROXY_ACTIVE_OR_UNVERIFIED'
    }
}
try {
    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT -or
        [Environment]::MachineName -cne $ownerHost) { throw 'BLOCKED_HOST' }
    $winId = [Security.Principal.WindowsIdentity]::GetCurrent()
    if ($null -eq $winId -or $null -eq $winId.User -or
        $winId.User.Value -notmatch '^S-1-5-21-') { throw 'BLOCKED_WINDOWS_SID' }

    $dolt = 'C:\Program Files\Dolt\bin\dolt.exe'
    $bd = Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages\GasTownHall.Beads_Microsoft.Winget.Source_8wekyb3d8bbwe\bd.exe'
    Assert-ExactBinary $dolt $doltSha256 'DOLT'
    Assert-ExactBinary $bd $bdSha256 'BEADS'
    $dv = ((& $dolt version 2>&1 | Select-Object -First 1) | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $dv -notmatch 'dolt version 2[.]6[.]2') {
        throw 'BLOCKED_DOLT_VERSION'
    }
    $bv = ((& $bd version 2>&1 | Select-Object -First 1) | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $bv -notmatch 'bd version 1[.]3[.]2') {
        throw 'BLOCKED_BEADS_VERSION'
    }
    if (@(Get-Process -Name dolt -ErrorAction SilentlyContinue).Count -ne 0) {
        throw 'BLOCKED_DOLT_PROCESS'
    }
    $listeners = @(Get-NetTCPConnection -State Listen -ErrorAction Stop |
        Where-Object { $_.LocalPort -in @(3306,3307,3308,14337) })
    if ($listeners.Count -ne 0) { throw 'BLOCKED_POSSIBLE_SQL_LISTENER' }

    $ts = (Get-Command tailscale -ErrorAction Stop).Source
    $rawStatus = (& $ts status --json 2>$null | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($rawStatus)) {
        throw 'BLOCKED_TAILSCALE_STATUS'
    }
    $status = ConvertFrom-Json -InputObject $rawStatus -AsHashtable -ErrorAction Stop
    if ($status.BackendState -cne 'Running' -or $status.Self.Online -ne $true) {
        throw 'BLOCKED_TAILSCALE_NOT_RUNNING_OR_NOT_ONLINE'
    }
    Assert-NoProxy $ts 'serve'
    Assert-NoProxy $ts 'funnel'

    $base = [IO.Path]::GetFullPath($env:LOCALAPPDATA).TrimEnd('\')
    Assert-NoReparseAncestor $base
    $root = [IO.Path]::GetFullPath((Join-Path $base 'TS-BEADS-047B'))
    if (-not $root.StartsWith($base+'\',[StringComparison]::OrdinalIgnoreCase)) {
        throw 'BLOCKED_ROOT_CONTAINMENT'
    }
    if (Test-Path -LiteralPath $root) { throw 'BLOCKED_EXISTING_ATTEMPT_OR_DATA' }

    # Observation only. Sid/peer/privileges/receipt are NOT qualified here.
    'READONLY_HOST_PRECONDITIONS_OBSERVED'
    'SID_PIN_AND_PEER_IDENTITY_UNVERIFIED'
    'ORIGINAL_PROVIDER_RECEIPT_UNVERIFIED'
    'SQL_ACCOUNT_ACL_DPAPI_AND_RESTORE_UNVERIFIED'
    'NO_SQL_OR_TAILSCALE_EFFECT'
    exit 0
} catch {
    # Fail closed; do not expose exception messages (may contain identity/paths).
    'BLOCKED_READONLY_PREFLIGHT'
    'NO_SQL_OR_TAILSCALE_EFFECT'
    exit 11
}
