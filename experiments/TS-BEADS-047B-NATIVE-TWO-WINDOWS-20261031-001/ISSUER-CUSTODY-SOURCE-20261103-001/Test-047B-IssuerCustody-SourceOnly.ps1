# Source-only negative test. No -Provision, SQL, credentials or service changes.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$source=Join-Path $PSScriptRoot 'Inspect-047B-IssuerCustody.ps1'
$tokens=$null
$issues=$null
$ast=[System.Management.Automation.Language.Parser]::ParseFile($source,[ref]$tokens,[ref]$issues)
if(@($issues).Count -ne 0){throw 'ISSUER_SCRIPT_PARSER_FAIL'}
$code=[IO.File]::ReadAllText($source)
$required=@('WRONG_NOTEBOOK_HOST','SecurityChangeApproved','Cert:\CurrentUser\My',
  'NonExportable','ISSUER_EXISTS_NO_REPROVISION','ISSUER_CERT_DUPLICATE_BLOCKED',
  'LOCAL_KEY_CREATED_NOT_BOUND','LOCAL_KEY_PRESENT_NOT_BOUND',
  'competentIssuerBound=$false','oneTimeSqlGrantPresent=$false',
  'ExportSubjectPublicKeyInfoPem','SHA256','3072')
foreach($needle in $required){
  if(-not $code.Contains($needle)){throw ('ISSUER_MISSING_GUARD_'+$needle)}
}
$blockedCommands=@('dolt','bd','tailscale','Invoke-RestMethod','Invoke-WebRequest',
  'Start-Process','Remove-Item','Set-Content','Out-File')
$calls=@($ast.FindAll({
  param($node)
  $node -is [System.Management.Automation.Language.CommandAst]
},$true))
foreach($call in $calls){
  if($call.GetCommandName() -in $blockedCommands){
    throw ('ISSUER_UNEXPECTED_COMMAND_'+$call.GetCommandName())
  }
}
$provisionCalls=@($calls|Where-Object{$_.GetCommandName() -ceq 'New-SelfSignedCertificate'})
if($provisionCalls.Count -ne 1){throw 'ISSUER_EXPECTED_ONE_KEY_CREATION_SITE'}
if($env:COMPUTERNAME -ceq 'DESKTOP-DJLBEQH'){throw 'CI_HOST_IS_NOTEBOOK_STOP'}
$pwsh=(Get-Command 'pwsh' -ErrorAction Stop).Source
$observed=(& $pwsh -NoLogo -NoProfile -NonInteractive -File $source -Inspect 2>&1 | Out-String)
$exit=$LASTEXITCODE
if($exit -eq 0 -or $observed -notmatch 'WRONG_NOTEBOOK_HOST'){
  throw 'WRONG_HOST_DID_NOT_FAIL_CLOSED'
}
[pscustomobject]@{result='ISSUER_SOURCE_ONLY_PASS';guardStrings=$required.Count;
  keyCreationSites=$provisionCalls.Count;keyCreationExecuted=$false;
  sqlExecuted=$false;providerCalls=0;competentIssuerBound=$false}
