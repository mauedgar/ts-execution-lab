# TS-BEADS 047B PROPOSAL — NO EXECUTION GRANT. New reviewed/pinned revision
# and original one-time receipt required before any local key-creation effect.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$operation='TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001'
$attempt='TS-BEADS-047B-ISSUER-COMMISSION-20261103-001'
$hostName='DESKTOP-DJLBEQH'
$subject='CN=TS-BEADS-047B-EXPERIMENTAL-ISSUER-20261103'
$trustedAuthorityPemSha256=('0'*64)
# No caller switch, private key, JSON assertion or external parameter can bypass.
if($trustedAuthorityPemSha256 -ceq ('0'*64)){throw 'COMPETENT_AUTHORITY_ANCHOR_NOT_BOUND'}
if([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT){throw 'WINDOWS_REQUIRED'}
if([Environment]::MachineName -cne $hostName -or $env:COMPUTERNAME -cne $hostName){throw 'WRONG_HOST'}
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
if($null -eq $identity -or $null -eq $identity.User){throw 'USER_SID_UNAVAILABLE'}
$ownerSid=$identity.User.Value
$local=[Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)
if([string]::IsNullOrWhiteSpace($local)){throw 'LOCALAPPDATA_MISSING'}
if([IO.Path]::GetFullPath($local).TrimEnd('\') -cne [IO.Path]::GetFullPath($env:LOCALAPPDATA).TrimEnd('\')){throw 'LOCALAPPDATA_ENV_MISMATCH'}
$root=[IO.Path]::Combine($local,'TS-BEADS-047B','issuer-commission-v1')
$grantPath=[IO.Path]::Combine($root,'authority','grant.json')
$sigPath=[IO.Path]::Combine($root,'authority','grant.sig')
$keyPath=[IO.Path]::Combine($root,'authority','authority.pem')
$claimPath=[IO.Path]::Combine($root,'original-attempt.jsonl')
# Pre-materialized source/authority material, never created by this runner.
if(-not [IO.Directory]::Exists($root)){throw 'PROTECTED_ROOT_NOT_MATERIALIZED'}
$walk=$root
while($true){
  if([IO.File]::Exists($walk) -or [IO.Directory]::Exists($walk)){
    if(([IO.File]::GetAttributes($walk) -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'REPARSE_ANCESTOR'}
  }
  $parent=[IO.Directory]::GetParent($walk)
  if($null -eq $parent){break}
  $walk=$parent.FullName
}
foreach($p in @($root,[IO.Path]::GetDirectoryName($grantPath),$grantPath,$sigPath,$keyPath)){
  if(-not (Test-Path -LiteralPath $p)){throw 'AUTHORITY_MATERIAL_MISSING'}
  if(([IO.File]::GetAttributes($p) -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'REPARSE_AUTHORITY_PATH'}
}
$acl=Get-Acl -LiteralPath $root -ErrorAction Stop
if($acl.GetOwner([Security.Principal.SecurityIdentifier]).Value -cne $ownerSid -or -not $acl.AreAccessRulesProtected){throw 'ROOT_OWNER_OR_DACL_UNSAFE'}
foreach($ace in $acl.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier])){
  if($ace.AccessControlType -eq [Security.AccessControl.AccessControlType]::Allow -and $ace.IdentityReference.Value -cnotin @($ownerSid,'S-1-5-18')){throw 'ROOT_ACL_EXCESS_ACCESS'}
}
if([IO.File]::Exists($claimPath)){throw 'PREEXISTING_ATTEMPT_NO_RETRY'}
$pemBytes=[IO.File]::ReadAllBytes($keyPath)
$pemHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($pemBytes))
if($pemHash -cne $trustedAuthorityPemSha256){throw 'UNTRUSTED_AUTHORITY_KEY'}
$grantBytes=[IO.File]::ReadAllBytes($grantPath)
$sigText=[IO.File]::ReadAllText($sigPath,[Text.Encoding]::ASCII).Trim()
if($sigText -cnotmatch '^[A-Za-z0-9+/=]+$'){throw 'INVALID_SIGNATURE_ENCODING'}
$sig=[Convert]::FromBase64String($sigText)
$authorityRsa=[Security.Cryptography.RSA]::Create()
try{
  $authorityRsa.ImportFromPem([Text.Encoding]::UTF8.GetString($pemBytes))
  if($authorityRsa.KeySize -lt 3072){throw 'AUTHORITY_RSA_TOO_SMALL'}
  if(-not $authorityRsa.VerifyData($grantBytes,$sig,[Security.Cryptography.HashAlgorithmName]::SHA256,[Security.Cryptography.RSASignaturePadding]::Pss)){throw 'GRANT_SIGNATURE_INVALID'}
}finally{$authorityRsa.Dispose();[Array]::Clear($pemBytes,0,$pemBytes.Length)}
$g=[Text.Encoding]::UTF8.GetString($grantBytes)|ConvertFrom-Json -AsHashtable -Depth 12
if($g -isnot [hashtable]){throw 'SIGNED_GRANT_SCHEMA'}
if($g.operation -cne $operation -or $g.attempt -cne $attempt -or $g.host -cne $hostName -or $g.windowsSid -cne $ownerSid -or $g.scope -cne 'LOCAL_EXPERIMENTAL_UNBOUND_ISSUER_KEY_ONLY' -or $g.allowKeyCreation -cne $true -or $g.subject -cne $subject){throw 'GRANT_SCOPE_OR_PRINCIPAL_MISMATCH'}
if($g.issuerRole -cne 'COMPETENT_EXPERIMENTAL_CONTROL' -or $g.exclusiveClaimReceiptSha256 -cnotmatch '^[A-F0-9]{64}$' -or $g.exclusiveClaimRef -cnotmatch '^[A-Za-z0-9_.:/@-]{20,300}$'){throw 'GRANT_CLAIM_PROVENANCE_MISSING'}
# Signed claim references are NOT proof; independent external join is mandatory.
if($g.sourceCommit -cnotmatch '^[a-f0-9]{40}$' -or $g.subjectBlob -cnotmatch '^[a-f0-9]{40}$' -or $g.claimNonce -cnotmatch '^[a-f0-9]{64}$'){throw 'GRANT_SOURCE_AND_CLAIM_INVALID'}
$git=(Get-Command 'git.exe' -ErrorAction Stop).Source
$checkoutHead=(& $git -C $PSScriptRoot rev-parse HEAD 2>$null | Out-String).Trim()
if($LASTEXITCODE -ne 0 -or $checkoutHead -cne $g.sourceCommit){throw 'SIGNED_COMMIT_MISMATCH'}
$actualBlob=(& $git -C $PSScriptRoot hash-object -- $PSCommandPath 2>$null | Out-String).Trim()
if($LASTEXITCODE -ne 0 -or $actualBlob -cne $g.subjectBlob){throw 'SIGNED_SOURCE_BLOB_MISMATCH'}
$expires=[datetimeoffset]::Parse($g.expiresUtc,[Globalization.CultureInfo]::InvariantCulture)
if($expires -le [datetimeoffset]::UtcNow -or $expires -gt [datetimeoffset]::UtcNow.AddMinutes(20)){throw 'GRANT_EXPIRED_OR_OVERLONG'}
$existing=@(Get-ChildItem -Path 'Cert:\CurrentUser\My' -ErrorAction Stop|Where-Object{$_.Subject -ceq $subject})
if($existing.Count -ne 0){throw 'ISSUER_SUBJECT_ALREADY_PRESENT'}
# Atomic CreateNew and exclusive FileShare.None on one stable path across calls.
# STARTED and terminal lines flushed to durable file; never delete/overwrite.
$fs=[IO.FileStream]::new($claimPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
$writer=$null
try{
  $writer=[IO.StreamWriter]::new($fs,[Text.UTF8Encoding]::new($false),1024,$true)
  $start=[ordered]@{attempt=$attempt;state='STARTED_BEFORE_KEY_EFFECT';operation=$operation;sourceCommit=$g.sourceCommit;grantSha256=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($grantBytes));timeUtc=[datetimeoffset]::UtcNow.ToString('o')}
  $writer.WriteLine(($start|ConvertTo-Json -Compress))
  $writer.Flush();$fs.Flush($true)
  # An exception after this point leaves an ambiguous effect; NO AUTO RETRY.
  $cert=New-SelfSignedCertificate -Subject $subject -Type Custom -CertStoreLocation 'Cert:\CurrentUser\My' -Provider 'Microsoft Software Key Storage Provider' -KeyAlgorithm RSA -KeyLength 3072 -KeyExportPolicy NonExportable -KeyUsage DigitalSignature -HashAlgorithm SHA256 -NotAfter ([DateTime]::UtcNow.AddDays(30)) -ErrorAction Stop
  if($null -eq $cert){throw 'KEY_EFFECT_UNKNOWN'}
  $after=@(Get-ChildItem -Path 'Cert:\CurrentUser\My' -ErrorAction Stop|Where-Object{$_.Subject -ceq $subject})
  if($after.Count -ne 1 -or $after[0].Thumbprint -cne $cert.Thumbprint){throw 'KEY_EFFECT_AMBIGUOUS'}
  if(-not $cert.HasPrivateKey){throw 'PRIVATE_KEY_NOT_PRESENT'}
  $publicRsa=[System.Security.Cryptography.X509Certificates.RSACertificateExtensions]::GetRSAPublicKey($cert)
  if($null -eq $publicRsa){throw 'PUBLIC_KEY_UNAVAILABLE'}
  try{
    if($publicRsa.KeySize -ne 3072){throw 'WRONG_KEY_BITS'}
    $publicPem=[Text.Encoding]::UTF8.GetBytes($publicRsa.ExportSubjectPublicKeyInfoPem())
    $publicDigest=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($publicPem))
  }finally{$publicRsa.Dispose()}
  $result=[ordered]@{attempt=$attempt;state='LOCAL_KEY_CREATED_UNBOUND_POLICY_NOT_ATTESTED';certThumbprint=$cert.Thumbprint;publicPemSha256Utf8=$publicDigest;timeUtc=[datetimeoffset]::UtcNow.ToString('o');competentIssuerBound=$false;oneTimeSqlGrantPresent=$false;sqlExecuted=$false;productEffect='NONE'}
  $writer.WriteLine(($result|ConvertTo-Json -Compress));$writer.Flush();$fs.Flush($true)
  [pscustomobject]$result
}catch{
  # Never print provider error or secrets. Claim remains, even if empty.
  try{if($null -ne $writer){$writer.WriteLine('{"state":"UNKNOWN_EFFECT_RECONCILE_BEFORE_RETRY"}');$writer.Flush();$fs.Flush($true)}}catch{}
  throw 'KEY_COMMISSION_FAILED_OR_UNKNOWN_NO_RETRY'
}finally{if($null -ne $writer){$writer.Dispose()};$fs.Dispose()}
