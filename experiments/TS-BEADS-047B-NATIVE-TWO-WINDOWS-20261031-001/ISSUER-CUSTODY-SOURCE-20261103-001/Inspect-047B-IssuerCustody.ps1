# TS-BEADS 047B — experimental issuer key custody SOURCE CANDIDATE.
# INSPECT is read-only. PROVISION is a LOCAL SECURITY WRITE, NOT authorized
# by publication, CI, or an unsigned manifest. Do not invoke before review.
[CmdletBinding(DefaultParameterSetName='Inspect')]
param(
  [Parameter(Mandatory,ParameterSetName='Inspect')][switch]$Inspect,
  [Parameter(Mandatory,ParameterSetName='Provision')][switch]$Provision,
  [Parameter(Mandatory,ParameterSetName='Provision')][switch]$SecurityChangeApproved
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$operation='TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001'
$expectedMachine='DESKTOP-DJLBEQH'
$issuerSubject='CN=TS-BEADS-047B-EXPERIMENTAL-ISSUER-20261103'
if([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT){throw 'WINDOWS_REQUIRED'}
if($env:COMPUTERNAME -cne $expectedMachine){throw 'WRONG_NOTEBOOK_HOST'}
if($Provision -and -not $SecurityChangeApproved){throw 'NO_EXPLICIT_KEY_CUSTODY_APPROVAL'}
$found=@(Get-ChildItem -LiteralPath 'Cert:\CurrentUser\My' -ErrorAction Stop |
  Where-Object {$_.Subject -ceq $issuerSubject})
if($found.Count -gt 1){throw 'ISSUER_CERT_DUPLICATE_BLOCKED'}
if($Provision){
  if($found.Count -ne 0){throw 'ISSUER_EXISTS_NO_REPROVISION'}
  # Writes only to Windows CurrentUser certificate and key store; future use
  # must be separately reviewed and bound to an original authorized attempt.
  $cert=New-SelfSignedCertificate -Subject $issuerSubject -CertStoreLocation 'Cert:\CurrentUser\My' -Provider 'Microsoft Software Key Storage Provider' -KeyAlgorithm RSA -KeyLength 3072 -KeyExportPolicy NonExportable -KeyUsage DigitalSignature -Type Custom -HashAlgorithm SHA256 -NotAfter ([datetime]::UtcNow.AddDays(30)) -ErrorAction Stop
  if($null -eq $cert){throw 'ISSUER_KEY_WRITE_AMBIGUOUS'}
  $found=@($cert)
}
if($found.Count -eq 0){
  [pscustomobject]@{operation=$operation;state='ISSUER_NOT_PROVISIONED';
    competentIssuerBound=$false;oneTimeSqlGrantPresent=$false;
    keyCreated=$false;sqlExecuted=$false;productEffect='NONE'}
  return
}
$certificate=$found[0]
if(-not $certificate.HasPrivateKey){throw 'ISSUER_PRIVATE_KEY_MISSING'}
if($certificate.NotAfter.ToUniversalTime() -le [datetime]::UtcNow){throw 'ISSUER_CERT_EXPIRED'}
$rsa=[System.Security.Cryptography.X509Certificates.RSACertificateExtensions]::GetRSAPublicKey($certificate)
if($null -eq $rsa){throw 'ISSUER_PUBLIC_KEY_UNAVAILABLE'}
try{
  if($rsa.KeySize -lt 3072){throw 'ISSUER_RSA_KEY_TOO_SMALL'}
  $pem=$rsa.ExportSubjectPublicKeyInfoPem()
  $raw=[Text.Encoding]::UTF8.GetBytes($pem)
  $publicFingerprint=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($raw))
  if($publicFingerprint -cnotmatch '^[A-F0-9]{64}$'){throw 'ISSUER_FINGERPRINT_INVALID'}
  # Local key possession != competent authorization. No private bytes exposed.
  [pscustomobject]@{operation=$operation;
    state=$(if($Provision){'LOCAL_KEY_CREATED_NOT_BOUND'}else{'LOCAL_KEY_PRESENT_NOT_BOUND'});
    certThumbprint=$certificate.Thumbprint;publicPemSha256Utf8=$publicFingerprint;
    keyBits=$rsa.KeySize;competentIssuerBound=$false;
    oneTimeSqlGrantPresent=$false;keyCreated=[bool]$Provision;
    sqlExecuted=$false;productEffect='NONE'}
} finally {$rsa.Dispose()}
