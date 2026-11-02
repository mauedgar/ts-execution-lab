# Read-only negative test: no host mutation, SQL, grant creation or network.
# Run on Windows PowerShell 7+ only after separate parser/source verification.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$module=Join-Path $PSScriptRoot '..\candidate\Security-047B-V6.psm1'
$runner=Join-Path $PSScriptRoot '..\candidate\Invoke-047B-V6-Fixture.ps1'
$launcher=Join-Path $PSScriptRoot '..\candidate\Start-047B-V6.ps1'
if(-not [IO.File]::Exists($module)){throw 'NEGATIVE_TEST_MODULE_MISSING'}
$bytes=[IO.File]::ReadAllBytes($module)
$prefix=[Text.Encoding]::ASCII.GetBytes(('blob '+$bytes.Length+[char]0))
$payload=[byte[]]::new($prefix.Length+$bytes.Length)
[Array]::Copy($prefix,0,$payload,0,$prefix.Length)
[Array]::Copy($bytes,0,$payload,$prefix.Length,$bytes.Length)
$actual=[Convert]::ToHexString([Security.Cryptography.SHA1]::HashData($payload)).ToLowerInvariant()
if($actual -cne '70f5bee86358cf48ac6cded50c619ce46fed8f42'){throw 'NEGATIVE_TEST_MODULE_BLOB_MISMATCH'}
Import-Module $module -Force
$observed=$null
try {
  # An arbitrary caller cannot provide a trusted issuer key or forge a grant.
  # No file or directory is created by this function before it fails closed.
  [void](Assert-V6Authority '__NONEXISTENT_AUTHORITY_DIR__' $runner $launcher)
} catch {
  $observed=$_.Exception.Message
}
if($observed -cne 'NO_COMPETENT_ISSUER_PIN'){
  throw ('NEGATIVE_TEST_UNEXPECTED_GATE_'+$observed)
}
[pscustomobject]@{state='PASS_NEGATIVE_SOURCE_GATE_ONLY';
  reason='UNPROVISIONED_TRUST_ANCHOR_BLOCKS_BEFORE_IO';
  sqlExecuted=$false;nativeDoltTested=$false}
