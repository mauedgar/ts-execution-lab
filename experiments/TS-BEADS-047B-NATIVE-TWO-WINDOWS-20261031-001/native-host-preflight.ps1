# TS-BEADS-047B / read-only native Windows host preflight.
# No SQL startup, no file writes, no secrets, no public endpoint, no Product.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('NotebookServer', 'DesktopClient')]
    [string] $Role,
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $PeerHostname
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
function Assert-Condition([bool]$Condition, [string]$Label) {
    if (-not $Condition) {
        throw ('BLOCKED_PRECONDITION:' + $Label)
    }
}
function CmdPath([string]$CommandName) {
    $cmd = Get-Command $CommandName -ErrorAction SilentlyContinue
    Assert-Condition ($null -ne $cmd) ('MISSING_TOOL_' + $CommandName)
    return $cmd.Source
}
Assert-Condition ($env:OS -eq 'Windows_NT') 'WINDOWS_ONLY'
Assert-Condition (-not [string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) 'LOCALAPPDATA_MISSING'
$tsPath = 'C:\Program Files\Tailscale\tailscale.exe'
Assert-Condition (Test-Path -LiteralPath $tsPath -PathType Leaf) 'TAILSCALE_CLI_MISSING'
$statusText = (& $tsPath status --json | Out-String)
Assert-Condition ($LASTEXITCODE -eq 0) 'TAILSCALE_STATUS_ERROR'
$status = $statusText | ConvertFrom-Json
Assert-Condition ($status.BackendState -eq 'Running' -and $status.Self.Online -eq $true) 'TAILNET_OFFLINE'
$peers = @($status.Peer.PSObject.Properties | ForEach-Object { $_.Value } | Where-Object {
    $_.HostName -eq $PeerHostname -and $_.Online -eq $true
})
Assert-Condition ($peers.Count -eq 1) 'PEER_NOT_ONLINE_UNIQUE'
$pingOutput = @(& $tsPath ping --c=1 $peers[0].TailscaleIPs[0] 2>&1)
Assert-Condition ($LASTEXITCODE -eq 0) 'PRIVATE_PEER_PING_ERROR'
Assert-Condition ((($pingOutput | Out-String) -match '(?i)pong')) 'PRIVATE_PEER_UNREACHABLE'
$env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
            [Environment]::GetEnvironmentVariable('Path', 'User')
$bdPath = CmdPath 'bd'
$bdVersion = (& $bdPath --version | Out-String)
Assert-Condition ($LASTEXITCODE -eq 0 -and $bdVersion.Contains('1.3.1')) 'BEADS_VERSION_NOT_PINNED'
$labRoot = Join-Path $env:LOCALAPPDATA 'TS-BEADS-047B'
Assert-Condition (-not (Test-Path -LiteralPath $labRoot)) 'LAB_ROOT_ALREADY_EXISTS_RECONCILE'
if ($Role -eq 'NotebookServer') {
    $doltPath = CmdPath 'dolt'
    $doltVersion = (& $doltPath version | Out-String)
    Assert-Condition ($LASTEXITCODE -eq 0 -and $doltVersion.Contains('2.2.0')) 'DOLT_VERSION_NOT_PINNED'
    $occupant = @(Get-NetTCPConnection -LocalPort 3307 -ErrorAction SilentlyContinue)
    Assert-Condition ($occupant.Count -eq 0) 'SQL_PORT_ALREADY_OCCUPIED_RECONCILE'
}
[pscustomobject]@{
    operation = 'TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001'
    authority = 'EXPERIMENTAL_CONTROL_ONLY'
    product_effect = 'NONE'
    role = $Role
    result = 'PASS_READ_ONLY_HOST_PREFLIGHT'
    tailnet_running = $true
    peer_online = $true
    private_ping = 'PASS'
    native_beads_version = '1.3.1'
    native_dolt_server_version = $(if ($Role -eq 'NotebookServer') { '2.2.0' } else { 'NOT_REQUIRED' })
    live_sql_execution_started = $false
    notebook_primary_sql_started = $false
} | Format-List
