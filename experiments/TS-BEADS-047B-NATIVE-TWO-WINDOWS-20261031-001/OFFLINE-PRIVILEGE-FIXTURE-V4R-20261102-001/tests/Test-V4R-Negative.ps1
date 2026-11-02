# Read-only negative test: no host mutation, SQL, grant creation or network.
# Run on Windows PowerShell 7+ only after separate parser/source verification.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$module=Join-Path $PSScriptRoot '..\candidate\Security-047B-V4R.psm1'
$runner=Join-Path $PSScriptRoot '..\candidate\Invoke-047B-V4R-Fixture.ps1'
$launcher=Join-Path $PSScriptRoot '..\candidate\Start-047B-V4R.ps1'
if(-not (Test-Path -LiteralPath $module)){
  throw 'NEGATIVE_TEST_MODULE_MISSING'
}
Import-Module $module -Force
$observed=$null
try {
  # An arbitrary caller cannot provide a trusted issuer key or forge a grant.
  # No file or directory is created by this function before it fails closed.
  [void](Assert-V4RAuthority '__NONEXISTENT_AUTHORITY_DIR__' $runner $launcher)
} catch {
  $observed=$_.Exception.Message
}
if($observed -cne 'NO_COMPETENT_ISSUER_PIN'){
  throw ('NEGATIVE_TEST_UNEXPECTED_GATE_'+$observed)
}
[pscustomobject]@{state='PASS_NEGATIVE_SOURCE_GATE_ONLY';
  reason='UNPROVISIONED_TRUST_ANCHOR_BLOCKS_BEFORE_IO';
  sqlExecuted=$false;nativeDoltTested=$false}
