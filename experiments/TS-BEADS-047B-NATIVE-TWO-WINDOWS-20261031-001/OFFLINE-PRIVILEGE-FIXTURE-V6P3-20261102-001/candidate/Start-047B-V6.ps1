# TS-BEADS 047B V6P3 launcher. Source-only; no grant, no SQL authorization.
[CmdletBinding(DefaultParameterSetName='Preflight')]
param(
  [Parameter(Mandatory,ParameterSetName='Preflight')][switch]$Preflight,
  [Parameter(Mandatory,ParameterSetName='Effect')][switch]$Effect,
  [Parameter(Mandatory,ParameterSetName='Effect')][string]$AuthorityDirectory
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$runner=Join-Path $PSScriptRoot 'Invoke-047B-V6-Fixture.ps1'
$module=Join-Path $PSScriptRoot 'Security-047B-V6.psm1'
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
  if((Get-GitBlobSha1 $runner) -cne 'e32375735698032d2bb465ce7072600aa0348d91'){throw 'RUNNER_BLOB_MISMATCH'}
  if((Get-GitBlobSha1 $module) -cne '70f5bee86358cf48ac6cded50c619ce46fed8f42'){throw 'SECURITY_MODULE_MISMATCH'}
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
