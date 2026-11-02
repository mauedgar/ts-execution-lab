# Read-only negative test: no host mutation, SQL, grant creation or network.
# Run on Windows PowerShell 7+ only after separate parser/source verification.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$module=Join-Path $PSScriptRoot '..\candidate\Security-047B-V3.psm1'
$runner=Join-Path $PSScriptRoot '..\candidate\Invoke-047B-V3-Fixture.ps1'
$launcher=Join-Path $PSScriptRoot '..\candidate\Start-047B-V3.ps1'
if((Get-FileHash -LiteralPath $module -Algorithm SHA256).Hash -cne '3B1CC29B539A04DB05223CE1D50785F8736646EAE71378E855F3CF6FE9291B26'){
  throw 'NEGATIVE_TEST_MODULE_HASH_MISMATCH'
}
Import-Module $module -Force
$observed=$null
try {
  # An arbitrary caller cannot provide a trusted issuer key or forge a grant.
  # No file or directory is created by this function before it fails closed.
  [void](Assert-V3Authority '__NONEXISTENT_AUTHORITY_DIR__' $runner $launcher)
} catch {
  $observed=$_.Exception.Message
}
if($observed -cne 'NO_COMPETENT_ISSUER_PIN'){
  throw ('NEGATIVE_TEST_UNEXPECTED_GATE_'+$observed)
}
[pscustomobject]@{state='PASS_NEGATIVE_SOURCE_GATE_ONLY';
  reason='UNPROVISIONED_TRUST_ANCHOR_BLOCKS_BEFORE_IO';
  sqlExecuted=$false;nativeDoltTested=$false}
