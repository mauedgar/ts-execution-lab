# TS-BEADS 047B V2 launcher. Source-only; no grant, no SQL authorization.
[CmdletBinding(DefaultParameterSetName='Preflight')]
param(
  [Parameter(Mandatory,ParameterSetName='Preflight')][switch]$Preflight,
  [Parameter(Mandatory,ParameterSetName='Effect')][switch]$Effect,
  [Parameter(Mandatory,ParameterSetName='Effect')][string]$AuthorityDirectory
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$runner=Join-Path $PSScriptRoot 'Invoke-047B-V2-Fixture.ps1'
$module=Join-Path $PSScriptRoot 'Security-047B-V2.psm1'
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
  if((Get-GitBlobSha1 $runner) -cne '8f9b66ada9b52e2d793a3aef3d8fea96c1d90291'){throw 'RUNNER_BLOB_MISMATCH'}
  if((Get-FileHash -LiteralPath $module -Algorithm SHA256).Hash -cne '101D9737C198DA7FD6070F9F8C961BF900499EA05857314E4F97701777239F77'){throw 'SECURITY_MODULE_MISMATCH'}
  if($Preflight){
    & $runner -Preflight
  } else {
    # Even direct runner invocation repeats signed-grant verification; the
    # launcher does not provide a bypass, hash or caller-declared issuer.
    & $runner -Effect -AuthorityDirectory $AuthorityDirectory -LauncherPath $PSCommandPath
  }
} catch {
  [pscustomobject]@{operation='TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001';
    state='BLOCKED_PRECONDITION';reason='SOURCE_OR_LAUNCHER_PRECONDITION_FAILED';sqlEffect='NOT_AUTHORIZED'}
}
