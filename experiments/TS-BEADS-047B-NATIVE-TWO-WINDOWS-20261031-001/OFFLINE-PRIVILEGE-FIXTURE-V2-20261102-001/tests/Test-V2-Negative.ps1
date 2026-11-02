# Read-only negative test: no host mutation, SQL, grant creation or network.
# Run on Windows PowerShell 7+ only after separate parser/source verification.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$module=Join-Path $PSScriptRoot '..\candidate\Security-047B-V2.psm1'
$runner=Join-Path $PSScriptRoot '..\candidate\Invoke-047B-V2-Fixture.ps1'
$launcher=Join-Path $PSScriptRoot '..\candidate\Start-047B-V2.ps1'
if((Get-FileHash -LiteralPath $module -Algorithm SHA256).Hash -cne '101D9737C198DA7FD6070F9F8C961BF900499EA05857314E4F97701777239F77'){
  throw 'NEGATIVE_TEST_MODULE_HASH_MISMATCH'
}
Import-Module $module -Force
$observed=$null
try {
  # An arbitrary caller cannot provide a trusted issuer key or forge a grant.
  # No file or directory is created by this function before it fails closed.
  [void](Assert-V2Authority '__NONEXISTENT_AUTHORITY_DIR__' $runner $launcher)
} catch {
  $observed=$_.Exception.Message
}
if($observed -cne 'NO_COMPETENT_ISSUER_PIN'){
  throw ('NEGATIVE_TEST_UNEXPECTED_GATE_'+$observed)
}
[pscustomobject]@{state='PASS_NEGATIVE_SOURCE_GATE_ONLY';
  reason='UNPROVISIONED_TRUST_ANCHOR_BLOCKS_BEFORE_IO';
  sqlExecuted=$false;nativeDoltTested=$false}
