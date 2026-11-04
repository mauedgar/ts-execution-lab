# TS-BEADS 047B — Dolt 2.6.2 source-only derived V6P1 candidate.
# Distinct attempt; NOT DISPATCHABLE. Original V6P1 stays immutable.
# NO GRANT OR SQL EFFECT IS IMPLIED.
Set-StrictMode -Version Latest
$script:V6Operation='TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001'
$script:V6Host='DESKTOP-DJLBEQH'
$script:V6Attempt='TS-BEADS-047B-DOLT262-OFFLINE-FIXTURE-20261104-001'
$script:V6Scope='OFFLINE_DOLT_PRIVILEGE_PERSISTENCE_ONLY'
# Deliberately UNPROVISIONED. Only a new independently reviewed immutable source
# revision may pin a real competent issuer key. A caller-supplied hash is NEVER trust.
$script:V6TrustedKeySha256=('0' * 64)
$script:V6DoltSha256='DF49F737CB80FC0F32B02220C701F476D378F322FA1BB51D696728FDAE825B91'
function Assert-V6([bool]$Condition,[string]$Code) {
  if(-not $Condition){throw [System.InvalidOperationException]::new($Code)}
}
function Get-V6Root {
  Assert-V6 ([Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT) 'WINDOWS_REQUIRED'
  $local=[Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)
  Assert-V6 (-not [string]::IsNullOrWhiteSpace($local)) 'LOCALAPPDATA_UNRESOLVED'
  $base=[IO.Path]::GetFullPath($local).TrimEnd('\')
  Assert-V6 ($base -eq [IO.Path]::GetFullPath($env:LOCALAPPDATA).TrimEnd('\')) 'LOCALAPPDATA_ENV_MISMATCH'
  $userProfilePath=[Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
  Assert-V6 ($base.StartsWith(([IO.Path]::GetFullPath($userProfilePath).TrimEnd('\')+'\'),[StringComparison]::OrdinalIgnoreCase)) 'LOCALAPPDATA_NOT_UNDER_PROFILE'
  $parent=[IO.Path]::Combine($base,'TS047B-Offline-V6')
  [pscustomobject]@{Base=$base;Parent=$parent;Root=[IO.Path]::Combine($parent,$script:V6Attempt);
    Receipt=[IO.Path]::Combine($parent,($script:V6Attempt+'.jsonl'))}
}
function Assert-V6NoReparse([string]$Path) {
  $p=[IO.Path]::GetFullPath($Path)
  while($true){
    if([IO.File]::Exists($p) -or [IO.Directory]::Exists($p)){
      $a=[IO.File]::GetAttributes($p)
      Assert-V6 (($a -band [IO.FileAttributes]::ReparsePoint) -eq 0) 'REPARSE_ANCESTOR'
    }
    $parent=[IO.Directory]::GetParent($p)
    if($null -eq $parent){break}
    $p=$parent.FullName
  }
}
function Assert-V6PrivateAcl([string]$Path,[bool]$InheritFromPrivateParent=$false) {
  Assert-V6 (-not ([IO.File]::GetAttributes($Path) -band [IO.FileAttributes]::ReparsePoint)) 'REPARSE_ITEM'
  $acl=Get-Acl -LiteralPath $Path -ErrorAction Stop
  $current=[Security.Principal.WindowsIdentity]::GetCurrent().User.Value
  $owner=$acl.GetOwner([Security.Principal.SecurityIdentifier]).Value
  Assert-V6 ($owner -eq $current) 'ACL_OWNER'
  if($InheritFromPrivateParent) {
    Assert-V6 ([IO.File]::Exists($Path)) 'INHERITED_ACL_ONLY_FOR_FILE'
    Assert-V6PrivateAcl ([IO.Path]::GetDirectoryName($Path)) $false
  } else { Assert-V6 ($acl.AreAccessRulesProtected) 'ACL_NOT_PROTECTED' }
  $allowed=@($current,'S-1-5-18')
  foreach($ace in $acl.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier])){
    if($ace.AccessControlType -eq [Security.AccessControl.AccessControlType]::Allow){
      Assert-V6 ($ace.IdentityReference.Value -in $allowed) 'ACL_UNTRUSTED_ALLOW'
    }
  }
  Assert-V6 ($acl.Access.Count -gt 0) 'ACL_EMPTY'
}
function New-V6AtomicPrivateDirectory([string]$Path) {
  # Win32 CreateDirectoryW receives a protected security descriptor AT CREATION.
  # No create-then-Set-Acl window. An existing directory is never adopted here.
  Assert-V6 (-not (Test-Path -LiteralPath $Path)) 'DIRECTORY_ALREADY_EXISTS'
  Assert-V6NoReparse (Split-Path -Parent $Path)
  if(-not ('V6NativeAcl' -as [type])){
    Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
public static class V6NativeAcl {
 [StructLayout(LayoutKind.Sequential)] public struct SA {
  public int nLength; public IntPtr lpSecurityDescriptor;
  [MarshalAs(UnmanagedType.Bool)] public bool bInheritHandle;
 }
 [DllImport("advapi32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
 [return:MarshalAs(UnmanagedType.Bool)]
 static extern bool ConvertStringSecurityDescriptorToSecurityDescriptorW(
  string sddl, uint revision, out IntPtr descriptor, out uint size);
 [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
 [return:MarshalAs(UnmanagedType.Bool)]
 static extern bool CreateDirectoryW(string path, ref SA security);
 [DllImport("kernel32.dll")] static extern IntPtr LocalFree(IntPtr mem);
 public static void Create(string path,string userSid){
  IntPtr sd=IntPtr.Zero; uint size=0;
  string sddl="O:"+userSid+"G:"+userSid+"D:P(A;OICI;FA;;;"+userSid+")(A;OICI;FA;;;SY)";
  if(!ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl,1,out sd,out size))
   throw new Win32Exception(Marshal.GetLastWin32Error());
  try {
   SA a=new SA{nLength=Marshal.SizeOf<SA>(),lpSecurityDescriptor=sd,bInheritHandle=false};
   if(!CreateDirectoryW(path,ref a))throw new Win32Exception(Marshal.GetLastWin32Error());
  } finally {LocalFree(sd);}
 }
}
'@ -ErrorAction Stop
  }
  $sid=[Security.Principal.WindowsIdentity]::GetCurrent().User.Value
  [V6NativeAcl]::Create($Path,$sid)
  Assert-V6NoReparse $Path
  Assert-V6PrivateAcl $Path
}
# CreateNew + protected descriptor in ONE Win32 CreateFileW call.
function New-V6AtomicPrivateFile([string]$Path) {
  Assert-V6 (-not (Test-Path -LiteralPath $Path)) 'RECEIPT_ALREADY_EXISTS'
  Assert-V6NoReparse (Split-Path -Parent $Path)
  Assert-V6PrivateAcl (Split-Path -Parent $Path) $false
  if(-not ('V6NativePrivateFile' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.IO;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;
public static class V6NativePrivateFile {
 [StructLayout(LayoutKind.Sequential)] public struct SA {
  public int nLength; public IntPtr lpSecurityDescriptor;
  [MarshalAs(UnmanagedType.Bool)] public bool bInheritHandle;
 }
 [DllImport("advapi32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
 [return:MarshalAs(UnmanagedType.Bool)]
 static extern bool ConvertStringSecurityDescriptorToSecurityDescriptorW(
  string sddl, uint revision, out IntPtr descriptor, out uint size);
 [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
 static extern SafeFileHandle CreateFileW(string path, uint access, uint share,
  ref SA sec, uint creation, uint flags, IntPtr template);
 [DllImport("kernel32.dll")] static extern IntPtr LocalFree(IntPtr mem);
 public static FileStream Create(string path,string userSid){
  IntPtr sd=IntPtr.Zero; uint size=0;
  string sddl="O:"+userSid+"G:"+userSid+"D:P(A;;FA;;;"+userSid+")(A;;FA;;;SY)";
  if(!ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl,1,out sd,out size))
    throw new Win32Exception(Marshal.GetLastWin32Error());
  try {
    SA a=new SA{nLength=Marshal.SizeOf<SA>(),lpSecurityDescriptor=sd,bInheritHandle=false};
    SafeFileHandle h=CreateFileW(path,0x40000000,0,ref a,1,0x80000000,IntPtr.Zero);
    if(h.IsInvalid){int code=Marshal.GetLastWin32Error();h.Dispose();throw new Win32Exception(code);}
    return new FileStream(h,FileAccess.Write,4096,false);
  } finally {LocalFree(sd);}
 }
}
'@ -ErrorAction Stop
  }
  $stream=[V6NativePrivateFile]::Create($Path,[Security.Principal.WindowsIdentity]::GetCurrent().User.Value)
  try {
    Assert-V6NoReparse $Path
    Assert-V6PrivateAcl $Path $false
    return $stream
  } catch {$stream.Dispose();throw}
}
function Assert-V6TrustedDocument([string]$BodyPath,[string]$SignaturePath,[string]$PublicKeyPath) {
  Assert-V6 ($script:V6TrustedKeySha256 -ne ('0' * 64)) 'ISSUER_TRUST_ANCHOR_UNPROVISIONED'
  foreach($p in @($BodyPath,$SignaturePath,$PublicKeyPath)){
    Assert-V6 ([IO.File]::Exists($p)) 'SIGNED_DOCUMENT_MISSING'
    Assert-V6NoReparse $p
  }
  $key=[IO.File]::ReadAllBytes($PublicKeyPath)
  $keyHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($key))
  Assert-V6 ($keyHash -ceq $script:V6TrustedKeySha256) 'UNTRUSTED_ISSUER_KEY'
  $sigText=[IO.File]::ReadAllText($SignaturePath,[Text.Encoding]::ASCII).Trim()
  Assert-V6 ($sigText -match '^[A-Za-z0-9+/=]+$') 'SIGNATURE_ENCODING'
  $signature=[Convert]::FromBase64String($sigText)
  $body=[IO.File]::ReadAllBytes($BodyPath)
  $rsa=[Security.Cryptography.RSA]::Create()
  try {
    $rsa.ImportFromPem([Text.Encoding]::UTF8.GetString($key))
    Assert-V6 ($rsa.KeySize -ge 3072) 'ISSUER_KEY_TOO_SMALL'
    Assert-V6 ($rsa.VerifyData($body,$signature,
      [Security.Cryptography.HashAlgorithmName]::SHA256,
      [Security.Cryptography.RSASignaturePadding]::Pss)) 'INVALID_SIGNATURE'
  } finally {$rsa.Dispose();[Array]::Clear($key,0,$key.Length)}
  $json=[Text.Encoding]::UTF8.GetString($body)|ConvertFrom-Json -AsHashtable -Depth 16
  Assert-V6 ($json -is [hashtable]) 'SIGNED_DOCUMENT_SCHEMA'
  return $json
}
function Get-V6GitBlob([string]$Path) {
  $data=[IO.File]::ReadAllBytes($Path)
  try {
    $prefix=[Text.Encoding]::ASCII.GetBytes(('blob '+$data.Length+[char]0))
    $payload=[byte[]]::new($prefix.Length+$data.Length)
    [Array]::Copy($prefix,0,$payload,0,$prefix.Length)
    [Array]::Copy($data,0,$payload,$prefix.Length,$data.Length)
    return [Convert]::ToHexString([Security.Cryptography.SHA1]::HashData($payload)).ToLowerInvariant()
  } finally { [Array]::Clear($data,0,$data.Length) }
}
function Assert-V6Authority([string]$AuthorityDirectory,[string]$RunnerPath,[string]$LauncherPath) {
  # Two distinct signed documents: grant and original-operation reconciliation.
  # A JSON field claiming issuer/authority without the pinned signature is worthless.
  Assert-V6 ($script:V6TrustedKeySha256 -ne ('0' * 64)) 'NO_COMPETENT_ISSUER_PIN'
  $pub=Join-Path $AuthorityDirectory 'issuer.pem'
  $g=Assert-V6TrustedDocument (Join-Path $AuthorityDirectory 'grant.json') (Join-Path $AuthorityDirectory 'grant.sig') $pub
  $r=Assert-V6TrustedDocument (Join-Path $AuthorityDirectory 'reconciliation.json') (Join-Path $AuthorityDirectory 'reconciliation.sig') $pub
  Assert-V6 ($r.sourceCommit -ceq $g.sourceCommit) 'GRANT_RECONCILIATION_SOURCE_MISMATCH'
  Assert-V6 ($r.subjectBlob -ceq $g.subjectBlob) 'RECONCILIATION_SUBJECT_MISMATCH'
  foreach($d in @($g,$r)){
    Assert-V6 ($d.operation -ceq $script:V6Operation) 'OPERATION_MISMATCH'
    Assert-V6 ($d.attempt -ceq $script:V6Attempt) 'ATTEMPT_MISMATCH'
    Assert-V6 ($d.host -ceq $script:V6Host) 'HOST_MISMATCH'
    Assert-V6 ($d.issuer -ceq 'COMPETENT_EXPERIMENTAL_CONTROL') 'ISSUER_MISMATCH'
  }
  Assert-V6 ($g.scope -ceq $script:V6Scope -and $g.allowSqlEffect -ceq $true) 'SCOPE_OR_GRANT'
  Assert-V6 ($g.sourceCommit -match '^[a-f0-9]{40}$') 'SOURCE_COMMIT_INVALID'
  Assert-V6 ($g.subjectBlob -ceq (Get-V6GitBlob $RunnerPath)) 'SIGNED_SUBJECT_BLOB_MISMATCH'
  # Independently granted signed commit must equal the actual Git checkout HEAD.
  # This is source identity only, NOT an external provider claim or Product authority.
  $git=(Get-Command 'git.exe' -ErrorAction Stop).Source
  $checkedOutHead=(& $git -C $PSScriptRoot rev-parse HEAD 2>$null | Out-String).Trim()
  Assert-V6 ($LASTEXITCODE -eq 0 -and $checkedOutHead -ceq $g.sourceCommit) 'SIGNED_COMMIT_NOT_CHECKED_OUT'
  Assert-V6 ($g.runnerSha256 -ceq (Get-FileHash -LiteralPath $RunnerPath -Algorithm SHA256).Hash) 'RUNNER_HASH_MISMATCH'
  Assert-V6 ($g.launcherSha256 -ceq (Get-FileHash -LiteralPath $LauncherPath -Algorithm SHA256).Hash) 'LAUNCHER_HASH_MISMATCH'
  Assert-V6 ($g.subjectBlob -match '^[a-f0-9]{40}$') 'SOURCE_BLOB_INVALID'
  $now=[datetimeoffset]::UtcNow
  $expiry=[datetimeoffset]::Parse($g.expiresUtc,[Globalization.CultureInfo]::InvariantCulture)
  Assert-V6 ($expiry -gt $now -and $expiry -lt $now.AddHours(24)) 'GRANT_EXPIRED_OR_TOO_WIDE'
  Assert-V6 ($r.priorEffectsReconciled -ceq $true -and $r.unknownCount -ceq 0) 'ORIGINAL_EFFECTS_UNRECONCILED'
  Assert-V6 ($r.exclusiveClaim -ceq 'CLAIMED_BY_COMPETENT_CONTROL') 'EXCLUSIVE_CLAIM_ABSENT'
  Assert-V6 ($r.claimGitCommit -match '^[a-f0-9]{40}$' -and $r.claimBlob -match '^[a-f0-9]{40}$') 'CLAIM_PROVENANCE_MISSING'
  Assert-V6 ($r.registryObservationVerified -ceq $true) 'OFFHOST_CAS_OBSERVATION_ABSENT'
  Assert-V6 ($r.originalProviderReceiptsJoined -ceq $true) 'ORIGINAL_PROVIDER_RECEIPTS_UNJOINED'
  Assert-V6 ($r.sourceCommit -ceq $g.sourceCommit) 'GRANT_RECONCILIATION_SOURCE_MISMATCH'
  Assert-V6 ($r.claimNonce -ceq $g.claimNonce -and $g.claimNonce -match '^[a-f0-9]{64}$') 'CLAIM_NONCE_MISMATCH'
  return [pscustomobject]@{Grant=$g;Reconciliation=$r}
}
function Assert-V6NoNetworkExposure {
  # This offline CLI fixture NEVER starts a SQL listener. Refuse even a possible
  # 3307 listener, unknown Tailscale CLI/schema, Serve or Funnel configuration.
  $connections=@(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object {$_.LocalPort -eq 3307})
  Assert-V6 ($connections.Count -eq 0) 'SQL_PORT_OCCUPIED'
  $ts=Get-Command 'tailscale.exe' -ErrorAction Stop
  foreach($mode in @('serve','funnel')){
    $raw=(& $ts.Source $mode status --json 2>$null | Out-String).Trim()
    Assert-V6 ($LASTEXITCODE -eq 0) ('TAILSCALE_'+$mode+'_UNKNOWN')
    # Strict empty-object schema only. New keys, null, empty, warnings all block.
    Assert-V6 ($raw -ceq '{}') ('TAILSCALE_'+$mode+'_CONFIG_PRESENT_OR_UNKNOWN')
  }
}
Export-ModuleMember -Function Assert-V6,Get-V6Root,Assert-V6NoReparse,Assert-V6PrivateAcl,New-V6AtomicPrivateDirectory,New-V6AtomicPrivateFile,Get-V6GitBlob,Assert-V6Authority,Assert-V6NoNetworkExposure
