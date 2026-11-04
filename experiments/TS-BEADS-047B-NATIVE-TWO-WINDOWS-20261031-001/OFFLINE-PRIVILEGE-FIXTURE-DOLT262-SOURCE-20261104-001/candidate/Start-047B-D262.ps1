# TS-BEADS 047B Dolt 2.6.2 source-only launcher. NO SIGNER/SQL GRANT.
[CmdletBinding(DefaultParameterSetName='Preflight')]
param(
  [Parameter(Mandatory,ParameterSetName='Preflight')][switch]$Preflight,
  [Parameter(Mandatory,ParameterSetName='Effect')][switch]$Effect,
  [Parameter(Mandatory,ParameterSetName='Effect')][string]$AuthorityDirectory
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$runner=Join-Path $PSScriptRoot 'Invoke-047B-D262-Fixture.ps1'
$module=Join-Path $PSScriptRoot 'Security-047B-D262.psm1'
function Get-GitBlobSha1([string]$Path) {
  $bytes=[IO.File]::ReadAllBytes($Path)
  $prefix=[Text.Encoding]::ASCII.GetBytes(('blob '+$bytes.Length+[char]0))
  $combined=[byte[]]::new($prefix.Length+$bytes.Length)
  [Array]::Copy($prefix,0,$combined,0,$prefix.Length)
  [Array]::Copy($bytes,0,$combined,$prefix.Length,$bytes.Length)
  [Convert]::ToHexString([Security.Cryptography.SHA1]::HashData($combined)).ToLowerInvariant()
}
try {
  if(-not [IO.File]::Exists($runner) -or -not [IO.File]::Exists($module)){throw 'SOURCE_MISSING'}
  if((Get-GitBlobSha1 $runner) -cne 'a3172799ca62885dc02378d359c6f7e52203ac2b'){throw 'RUNNER_BLOB_MISMATCH'}
  if((Get-GitBlobSha1 $module) -cne 'ffb95bfff24ca75db8c750953f414873f34d71bd'){throw 'SECURITY_MODULE_MISMATCH'}
  if($Preflight){
    & $runner -Preflight
  } else {
    # Even direct runner invocation repeats signed-grant verification; the
    # launcher does not provide a bypass, hash or caller-declared issuer.
    & $runner -Effect -AuthorityDirectory $AuthorityDirectory -LauncherPath $PSCommandPath
  }
} catch {
  # An exceptional effect invocation cannot be classified as no effect from here.
  $classification=if($Effect){'UNKNOWN_EFFECT'}else{'BLOCKED_PRECONDITION'}
  [pscustomobject]@{operation='TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001';
    state=$classification;reason='LAUNCHER_ERROR_RECONCILE_ORIGINAL_EFFECT';sqlEffect='NOT_RETRYABLE_WITHOUT_ORIGINAL_RECEIPT'}
}
