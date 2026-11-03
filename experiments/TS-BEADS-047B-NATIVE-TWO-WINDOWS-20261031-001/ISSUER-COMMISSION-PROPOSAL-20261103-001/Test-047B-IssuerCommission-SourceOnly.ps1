# STRICT SOURCE-ONLY. Never create a certificate or a root/claim file in CI.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$source=Join-Path $PSScriptRoot 'Invoke-047B-IssuerCommission.ps1'
$token=$null;$err=$null
$ast=[System.Management.Automation.Language.Parser]::ParseFile($source,[ref]$token,[ref]$err)
if(@($err).Count -ne 0){throw 'ISSUER_COMMISSION_PARSER_FAIL'}
if(@($ast.ParamBlock.Parameters).Count -ne 0){throw 'UNEXPECTED_CALLER_PARAMETERS'}
$code=[IO.File]::ReadAllText($source)
$must=@("('0'*64)","COMPETENT_AUTHORITY_ANCHOR_NOT_BOUND",
 'Get-CurrentUserSid','NONEXISTENT_SENTINEL_PLACEHOLDER')
# Two generic placeholder strings above are NOT used: test concrete expectations.
$must=@(
 'COMPETENT_AUTHORITY_ANCHOR_NOT_BOUND','New-SelfSignedCertificate',
 'Security.Cryptography.RSASignaturePadding]::Pss',
 'SIGNED_SOURCE_BLOB_MISMATCH','SIGNED_COMMIT_MISMATCH',
 'GRANT_SCOPE_OR_PRINCIPAL_MISMATCH','ROOT_OWNER_OR_DACL_UNSAFE',
 'PREEXISTING_ATTEMPT_NO_RETRY','FileMode]::CreateNew',
 'FileShare]::None','STARTED_BEFORE_KEY_EFFECT',
 'UNKNOWN_EFFECT_RECONCILE_BEFORE_RETRY','NonExportable',
 'LOCAL_KEY_CREATED_UNBOUND_POLICY_NOT_ATTESTED',
 'competentIssuerBound=$false','oneTimeSqlGrantPresent=$false')
foreach($item in $must){if(-not $code.Contains($item)){throw ('EXPECTED_GUARD_MISSING_'+$item)}}
$cmds=@($ast.FindAll({param($x)$x -is [System.Management.Automation.Language.CommandAst]},$true))
$create=@($cmds|Where-Object{$_.GetCommandName() -ceq 'New-SelfSignedCertificate'})
if($create.Count -ne 1){throw 'EXPECTED_ONE_CREATION_SITE'}
$blocked=@('dolt','bd','tailscale','Remove-Item','Invoke-RestMethod','Invoke-WebRequest',
 'Start-Process','Set-Content','Out-File','Clear-Content','Remove-ItemProperty')
foreach($cmd in $cmds){if($cmd.GetCommandName() -cin $blocked){throw ('UNEXPECTED_EFFECT_COMMAND_'+$cmd.GetCommandName())}}
$anchor=[regex]::Match($code,[regex]::Escape("if("+'$trustedAuthorityPemSha256')+'.*COMPETENT_AUTHORITY_ANCHOR_NOT_BOUND')
if(-not $anchor.Success){throw 'NO_PERMANENT_FAIL_CLOSED_ANCHOR'}
if($anchor.Index -ge $code.IndexOf('New-SelfSignedCertificate -Subject')){throw 'KEY_CREATION_BEFORE_TRUST_CHECK'}
# Execute ONLY unprovisioned trust-anchor denial on the ephemeral CI host.
$pwsh=(Get-Command 'pwsh' -ErrorAction Stop).Source
$observed=(& $pwsh -NoLogo -NoProfile -NonInteractive -File $source 2>&1 | Out-String)
$exit=$LASTEXITCODE
if($exit -eq 0 -or $observed -notmatch 'COMPETENT_AUTHORITY_ANCHOR_NOT_BOUND'){
 throw 'UNPROVISIONED_TRUST_ANCHOR_NOT_REJECTED'
}
[pscustomobject]@{result='COMMISSION_SOURCE_UNBOUND_NO_EFFECT_PASS';guards=$must.Count;
 parameters=0;sourceCreationSites=$create.Count;actualKeyCreates=0;
 sqlExecuted=$false;externalProviderCalls=0;productWrites=0}
