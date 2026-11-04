# TS047B Dolt262 hosted-Windows no-effect security negative tests.
# Imports source module and exercises only rejecting paths. No SQL or Tailscale actions.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if($env:GITHUB_ACTIONS -cne 'true' -or $env:RUNNER_ENVIRONMENT -cne 'github-hosted' -or $env:GITHUB_RUN_ATTEMPT -cne '1') {
  throw 'HOSTED_CI_FIRST_ATTEMPT_ONLY'
}
if($env:COMPUTERNAME -ceq 'DESKTOP-DJLBEQH') { throw 'FROZEN_NOTEBOOK_HOST_COLLISION' }
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$candidate=Join-Path $root 'candidate'
$module=Join-Path $candidate 'Security-047B-D262.psm1'
$runner=Join-Path $candidate 'Invoke-047B-D262-Fixture.ps1'
$launcher=Join-Path $candidate 'Start-047B-D262.ps1'
$expected=@{
  'Security-047B-D262.psm1'='ffb95bfff24ca75db8c750953f414873f34d71bd'
  'Invoke-047B-D262-Fixture.ps1'='a3172799ca62885dc02378d359c6f7e52203ac2b'
  'Start-047B-D262.ps1'='bad08eda0165d18c6227eb35f19f6ea95fef7e17'
}
foreach($file in @($module,$runner,$launcher)){
  $base=[IO.Path]::GetFileName($file)
  if(-not [IO.File]::Exists($file)) { throw ('MISSING_FROZEN_FILE_'+$base) }
  $actual=(& git.exe hash-object --no-filters -- $file | Out-String).Trim()
  if($LASTEXITCODE -ne 0 -or $actual -cne $expected[$base]) { throw ('EXACT_GIT_BLOB_MISMATCH_'+$base) }
}
'PINNED_THREE_SOURCE_BLOBS_PASS'
Import-Module -Name $module -Force -ErrorAction Stop
function Assert-Rejected([scriptblock]$Action,[string]$Expected){
  $rejected=$false
  try { & $Action | Out-Null } catch {
    if($_.Exception.Message -cne $Expected){ throw ('WRONG_REJECTION_'+$Expected) }
    $rejected=$true
  }
  if(-not $rejected){throw ('ACCEPTED_INVALID_CASE_'+$Expected)}
}
# These functions reject BEFORE file reads, Git operations, signed-JSON parsing or SQL.
$missing=Join-Path $env:RUNNER_TEMP 'ts047b-d262-missing-not-created'
if(Test-Path -LiteralPath $missing){throw 'NEGATIVE_PLACEHOLDER_EXISTS'}
Assert-Rejected { Assert-V6Authority $missing $runner $launcher } 'NO_COMPETENT_ISSUER_PIN'
'UNPROVISIONED_COMPETENT_ISSUER_REJECTED=PASS'
Assert-Rejected { Assert-V6TrustedDocument $missing $missing $missing } 'ISSUER_TRUST_ANCHOR_UNPROVISIONED'
'FORGED_SIGNED_DOCUMENT_REJECTED_BEFORE_IO=PASS'
# Actual direct runner entrypoint with -Effect on an unrelated ephemeral host.
# The fixed physical owner check must fail BEFORE ANY local directory or SQL effect.
$direct=@(& $runner -Effect -AuthorityDirectory $missing -LauncherPath $launcher)
if($direct.Count -ne 1 -or $direct[0].state -cne 'BLOCKED_PRECONDITION' -or $direct[0].reason -cne 'NO_SQL_EFFECT'){
  throw 'DIRECT_RUNNER_WRONG_HOST_DID_NOT_FAIL_CLOSED'
}
if(Test-Path -LiteralPath $missing){throw 'DIRECT_RUNNER_CREATED_PLACEHOLDER'}
'DIRECT_RUNNER_WRONG_HOST_BLOCKED=PASS'
# The launcher must preserve this denial; no caller-provided path can grant authority.
$viaLauncher=@(& $launcher -Effect -AuthorityDirectory $missing)
if($viaLauncher.Count -ne 1 -or $viaLauncher[0].state -cne 'BLOCKED_PRECONDITION' -or $viaLauncher[0].reason -cne 'NO_SQL_EFFECT'){
  throw 'LAUNCHER_WRONG_HOST_DID_NOT_FAIL_CLOSED'
}
if(Test-Path -LiteralPath $missing){throw 'LAUNCHER_CREATED_PLACEHOLDER'}
'LAUNCHER_WRONG_HOST_BLOCKED=PASS'
'HOSTED_NEGATIVE_SECURITY_NO_EFFECT_PASS'
'SQL_EXECUTED=FALSE'
'TAILSCALE_CONFIGURATION_CHANGED=FALSE'
