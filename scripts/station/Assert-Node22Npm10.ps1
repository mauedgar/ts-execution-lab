# TS Dev UX: non-Product, read-only Windows Node/npm selector qualification.
# Example: pwsh -NoProfile -File scripts/station/Assert-Node22Npm10.ps1
# Does not modify PATH, install software, or execute npm lifecycle commands.
[CmdletBinding()]
param(
    [string]$NodeVersion = '22.23.3',
    [string]$NpmVersion = '10.9.9'
)

$ErrorActionPreference = 'Stop'
$fnmRoot = if ($env:FNM_DIR) { $env:FNM_DIR } else {
    Join-Path $env:APPDATA 'fnm'
}
$installation = Join-Path $fnmRoot ("node-versions/v{0}/installation" -f $NodeVersion)
$node = Join-Path $installation 'node.exe'
$npmCli = Join-Path $installation 'node_modules/npm/bin/npm-cli.js'

if (-not (Test-Path -LiteralPath $node -PathType Leaf)) {
    throw "NODE_SELECTOR_MISSING version=$NodeVersion path=$node"
}
if (-not (Test-Path -LiteralPath $npmCli -PathType Leaf)) {
    throw "NPM_SELECTOR_MISSING path=$npmCli"
}
$actualNode = (& $node --version | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $actualNode -ne "v$NodeVersion") {
    throw "NODE_SELECTOR_MISMATCH expected=v$NodeVersion observed=$actualNode"
}
$actualNpm = (& $node $npmCli --version | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $actualNpm -ne $NpmVersion) {
    throw "NPM_SELECTOR_MISMATCH expected=$NpmVersion observed=$actualNpm"
}
Write-Output "NODE_NPM_EXACT_BINDING_PASS node=$actualNode npm=$actualNpm"
Write-Output "NODE_EXE=$node"
Write-Output "NPM_CLI=$npmCli"
