# TS-BEADS-047B: minimal native Windows XFORM materializer.
# Purpose: verify one frozen ts-mat-xform-request/v1 envelope and safely write the exact script.
# NO SQL, network, Product modifications, service startup or script execution.
# Run with PowerShell 7+. The default is validation only; -Materialize is required to write.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $RequestPath,

    [Parameter(Mandatory = $false)]
    [string] $OutputDirectory = (Join-Path $env:LOCALAPPDATA 'TS-Execution-Staging\047B'),

    [switch] $Materialize
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$expectedContract = 'ts-mat-xform-request/v1'
$expectedRequest = 'TS-BEADS-047B-PREFLIGHT-TRANSFER-001'
$expectedBatch = 'TS-BEADS-047B-HOST-PREFLIGHT-20261031-001'
$expectedArtifactId = 'native-host-preflight-ps1'
$expectedFilename = 'native-host-preflight.ps1'
$expectedGitBlob = 'af0969d7b42cff53f20cbbded376f99aa50dce8e'

function FailClosed([string] $Reason) {
    throw ('BLOCKED_PRECONDITION:' + $Reason)
}
function Get-GitBlobSha1([byte[]] $Bytes) {
    $prefix = [System.Text.Encoding]::ASCII.GetBytes(('blob ' + $Bytes.Length + "\u0060"+"0"))
    $joined = [byte[]]::new($prefix.Length + $Bytes.Length)
    [Array]::Copy($prefix, 0, $joined, 0, $prefix.Length)
    [Array]::Copy($Bytes, 0, $joined, $prefix.Length, $Bytes.Length)
    return [Convert]::ToHexString([System.Security.Cryptography.SHA1]::HashData($joined)).ToLowerInvariant()
}

if (-not (Test-Path -LiteralPath $RequestPath -PathType Leaf)) { FailClosed 'XFORM_REQUEST_MISSING' }
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) { FailClosed 'OUTPUT_DIRECTORY_MISSING' }
if (-not [System.IO.Path]::IsPathFullyQualified($OutputDirectory)) { FailClosed 'OUTPUT_DIRECTORY_NOT_ABSOLUTE' }

$raw = [System.IO.File]::ReadAllText((Resolve-Path -LiteralPath $RequestPath).ProviderPath, [System.Text.Encoding]::UTF8)
try { $doc = ConvertFrom-Json -InputObject $raw -AsHashtable -Depth 30 } catch { FailClosed 'XFORM_INVALID_JSON' }
if ($null -eq $doc -or -not ($doc -is [System.Collections.IDictionary])) { FailClosed 'XFORM_NOT_OBJECT' }
if ($doc['contract_version'] -cne $expectedContract) { FailClosed 'CONTRACT_VERSION_MISMATCH' }
if ($doc['request_id'] -cne $expectedRequest) { FailClosed 'REQUEST_ID_MISMATCH' }
if ($doc['batch_id'] -cne $expectedBatch) { FailClosed 'BATCH_ID_MISMATCH' }
if ($null -eq $doc['artifacts'] -or $doc['artifacts'].Count -ne 1) { FailClosed 'ARTIFACT_COUNT_MISMATCH' }
$item = $doc['artifacts'][0]
if (-not ($item -is [System.Collections.IDictionary])) { FailClosed 'ARTIFACT_NOT_OBJECT' }
if ($item['artifact_id'] -cne $expectedArtifactId) { FailClosed 'ARTIFACT_ID_MISMATCH' }
if ($item['relative_path'] -cne $expectedFilename) { FailClosed 'ARTIFACT_PATH_MISMATCH' }
if (-not ($item['utf8_text'] -is [string])) { FailClosed 'ARTIFACT_TEXT_MISSING' }

$contentBytes = [System.Text.Encoding]::UTF8.GetBytes($item['utf8_text'])
$gitBlob = Get-GitBlobSha1 $contentBytes
if ($gitBlob -cne $expectedGitBlob) { FailClosed 'GIT_BLOB_MISMATCH' }
$sha256 = [Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData($contentBytes)).ToLowerInvariant()
$destination = Join-Path ([System.IO.Path]::GetFullPath($OutputDirectory)) $expectedFilename
$existing = Test-Path -LiteralPath $destination
if ($existing) {
    if (-not (Test-Path -LiteralPath $destination -PathType Leaf)) { FailClosed 'OUTPUT_PATH_NOT_FILE' }
    $existingHash = Get-GitBlobSha1 ([System.IO.File]::ReadAllBytes($destination))
    if ($existingHash -cne $expectedGitBlob) { FailClosed 'EXISTING_ARTIFACT_MISMATCH' }
}

if (-not $Materialize) {
    [pscustomobject]@{
        operation = $expectedBatch
        result = 'PASS_VALIDATED_NOT_MATERIALIZED'
        git_blob = $gitBlob
        sha256 = $sha256
        output_exists_verified = [bool]$existing
        execution_started = $false
        product_effect = 'NONE'
    } | Format-List
    return
}

if ($existing) {
    $result = 'PASS_ALREADY_MATERIALIZED_VERIFIED'
} else {
    $dir = [System.IO.Path]::GetFullPath($OutputDirectory)
    if (-not (Test-Path -LiteralPath $dir)) {
        [void](New-Item -Path $dir -ItemType Directory -Force)
    }
    $tempPath = Join-Path $dir ('.' + $expectedFilename + '.' + [guid]::NewGuid().ToString('N') + '.tmp')
    try {
        [System.IO.File]::WriteAllBytes($tempPath, $contentBytes)
        if ((Get-GitBlobSha1 ([System.IO.File]::ReadAllBytes($tempPath))) -cne $expectedGitBlob) {
            FailClosed 'STAGED_ARTIFACT_MISMATCH'
        }
        [System.IO.File]::Move($tempPath, $destination)
    } finally {
        if (Test-Path -LiteralPath $tempPath -PathType Leaf) {
            Remove-Item -LiteralPath $tempPath -Force
        }
    }
    if ((Get-GitBlobSha1 ([System.IO.File]::ReadAllBytes($destination))) -cne $expectedGitBlob) {
        FailClosed 'FINAL_ARTIFACT_MISMATCH'
    }
    $result = 'PASS_MATERIALIZED_VERIFIED'
}

[pscustomobject]@{
    operation = $expectedBatch
    result = $result
    git_blob = $gitBlob
    sha256 = $sha256
    output = $destination
    script_executed = $false
    sql_started = $false
    product_effect = 'NONE'
} | Format-List
