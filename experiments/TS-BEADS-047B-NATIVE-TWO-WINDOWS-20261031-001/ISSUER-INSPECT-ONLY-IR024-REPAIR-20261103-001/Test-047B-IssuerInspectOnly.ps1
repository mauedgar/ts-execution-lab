# Read-only source-only Windows CI test. Never materialize a key.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$source=Join-Path $PSScriptRoot 'Inspect-047B-IssuerEvidence.ps1'
$tokens=$null
$issues=$null
$ast=[System.Management.Automation.Language.Parser]::ParseFile($source,[ref]$tokens,[ref]$issues)
if(@($issues).Count -ne 0){throw 'INSPECT_ONLY_PARSER_FAIL'}
$names=@($ast.ParamBlock.Parameters | ForEach-Object {$_.Name.VariablePath.UserPath})
if($names.Count -ne 1 -or $names[0] -cne 'Inspect'){throw 'UNEXPECTED_PARAM_SURFACE'}
$commands=@($ast.FindAll({
  param($node)
  $node -is [System.Management.Automation.Language.CommandAst]
},$true))
$allowed=@('Set-StrictMode','Get-ChildItem','Where-Object')
foreach($command in $commands){
  $name=$command.GetCommandName()
  if($null -eq $name -or $name -cnotin $allowed){
    throw ('EFFECT_COMMAND_NOT_ALLOWED_'+$name)
  }
}
$sourceText=[IO.File]::ReadAllText($source)
$forbidden=@('New-SelfSignedCertificate','-Provision','SecurityChangeApproved',
  'SignData(','.ImportFromPem(','.GetRSAPrivateKey(','.ExportPkcs8PrivateKey(',
  'Remove-Item','Set-Content','[IO.File]::WriteAll','Start-Process')
foreach($forbiddenText in $forbidden){
  if($sourceText.IndexOf($forbiddenText,[StringComparison]::OrdinalIgnoreCase) -ge 0){
    throw ('EFFECT_SURFACE_PRESENT_'+$forbiddenText)
  }
}
foreach($expected in @('competentIssuerBound=$false','oneTimeSqlGrantPresent=$false',
  "state='NO_MATCHING_CERT_OBSERVED'","state='SINGLE_CERT_OBSERVED_UNBOUND'",
  "state='DUPLICATE_SUBJECT_NOT_TRUSTED'",'WRONG_NOTEBOOK_HOST')){
  if(-not $sourceText.Contains($expected)){throw ('FAIL_CLOSED_OUTPUT_MISSING_'+$expected)}
}
if($env:COMPUTERNAME -ceq 'DESKTOP-DJLBEQH'){throw 'TEST_MUST_NOT_RUN_ON_NOTEBOOK'}
$pwsh=(Get-Command 'pwsh' -ErrorAction Stop).Source
$wrongHost=(& $pwsh -NoLogo -NoProfile -NonInteractive -File $source -Inspect 2>&1 | Out-String)
$wrongHostExit=$LASTEXITCODE
if($wrongHostExit -eq 0 -or $wrongHost -notmatch 'WRONG_NOTEBOOK_HOST'){
  throw 'INSPECT_WRONG_HOST_DID_NOT_FAIL_CLOSED'
}
$badProvision=(& $pwsh -NoLogo -NoProfile -NonInteractive -File $source -Provision -SecurityChangeApproved 2>&1 | Out-String)
$badProvisionExit=$LASTEXITCODE
if($badProvisionExit -eq 0){throw 'UNSUPPORTED_PROVISION_FLAGS_ACCEPTED'}
[pscustomobject]@{result='ISSUER_INSPECT_ONLY_SOURCE_PASS';
  declaredParameters=$names.Count;allowedReadCommands=$commands.Count;
  provisionParameterRejected=$true;wrongHostRejected=$true;
  keyCreationSites=0;sqlExecuted=$false;providerCalls=0;productWrites=0}
