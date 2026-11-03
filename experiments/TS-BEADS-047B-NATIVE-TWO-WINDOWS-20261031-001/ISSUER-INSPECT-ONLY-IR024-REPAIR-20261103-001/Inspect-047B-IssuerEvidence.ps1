# TS-BEADS 047B — strictly observational issuer certificate inventory.
# NO key creation, signing, credentials, network, SQL or Product effects.
# All outcomes are UNBOUND observations, never an authority decision.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][switch]$Inspect)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$operation='TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001'
$expectedMachine='DESKTOP-DJLBEQH'
$subject='CN=TS-BEADS-047B-EXPERIMENTAL-ISSUER-20261103'
if([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT){throw 'WINDOWS_REQUIRED'}
if($env:COMPUTERNAME -cne $expectedMachine){throw 'WRONG_NOTEBOOK_HOST'}
# The environment name is a weak observation and is NOT host attestation.
$existing=@(Get-ChildItem -Path 'Cert:\CurrentUser\My' -ErrorAction Stop |
  Where-Object {$_.Subject -ceq $subject})
if($existing.Count -eq 0){
  [pscustomobject]@{operation=$operation;state='NO_MATCHING_CERT_OBSERVED';
    scope='READ_ONLY_UNBOUND';subjectMatches=0;
    competentIssuerBound=$false;oneTimeSqlGrantPresent=$false;
    keyCreated=$false;sqlExecuted=$false;productEffect='NONE'}
  return
}
if($existing.Count -ne 1){
  [pscustomobject]@{operation=$operation;state='DUPLICATE_SUBJECT_NOT_TRUSTED';
    scope='READ_ONLY_UNBOUND';subjectMatches=$existing.Count;
    competentIssuerBound=$false;oneTimeSqlGrantPresent=$false;
    keyCreated=$false;sqlExecuted=$false;productEffect='NONE'}
  return
}
$cert=$existing[0]
# Presence and public-key fingerprint are NOT custody, signer competence,
# private key nonexportability, ACL, SID attestation or signing-use proof.
$rsa=[System.Security.Cryptography.X509Certificates.RSACertificateExtensions]::GetRSAPublicKey($cert)
if($null -eq $rsa){throw 'UNSUPPORTED_CERT_PUBLIC_KEY'}
try{
  $pem=$rsa.ExportSubjectPublicKeyInfoPem()
  $bytes=[Text.Encoding]::UTF8.GetBytes($pem)
  $publicDigest=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes))
  [pscustomobject]@{operation=$operation;state='SINGLE_CERT_OBSERVED_UNBOUND';
    scope='READ_ONLY_UNBOUND';subjectMatches=1;
    certThumbprint=$cert.Thumbprint;publicPemSha256Utf8=$publicDigest;
    publicKeyBits=$rsa.KeySize;certNotAfterUtc=$cert.NotAfter.ToUniversalTime().ToString('o');
    privateKeyPresenceClaim=[bool]$cert.HasPrivateKey;
    competentIssuerBound=$false;oneTimeSqlGrantPresent=$false;
    keyCreated=$false;sqlExecuted=$false;productEffect='NONE'}
}finally{$rsa.Dispose()}
