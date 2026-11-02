# TS-BEADS 047B V4. EXPERIMENTAL SOURCE ONLY; NO GRANT OR SQL EFFECT IS IMPLIED.
Set-StrictMode -Version Latest
$script:V4Operation='TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001'
$script:V4Host='DESKTOP-DJLBEQH'
$script:V4Attempt='TS-BEADS-047B-DOLT-FIXTURE-V4-20261102-001'
$script:V4Scope='OFFLINE_DOLT_PRIVILEGE_PERSISTENCE_ONLY'
# Deliberately UNPROVISIONED. Only a new independently reviewed immutable source
# revision may pin a real competent issuer key. A caller-supplied hash is NEVER trust.
$script:V4TrustedKeySha256=('0' * 64)
$script:V4DoltSha256='BED880C0E6B522498A563FCD1F0FC1E25527BA07E66C1E0A85C2242B64DFD967'
function Assert-V4([bool]$Condition,[string]$Code) {
  if(-not $Condition){throw [System.InvalidOperationException]::new($Code)}
}
function Get-V4Root {
  Assert-V4 ([Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT) 'WINDOWS_REQUIRED'
  $local=[Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)
  Assert-V4 (-not [string]::IsNullOrWhiteSpace($local)) 'LOCALAPPDATA_UNRESOLVED'
  $base=[IO.Path]::GetFullPath($local).TrimEnd('\')
  Assert-V4 ($base -eq [IO.Path]::GetFullPath($env:LOCALAPPDATA).TrimEnd('\')) 'LOCALAPPDATA_ENV_MISMATCH'
  $home=[Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
  Assert-V4 ($base.StartsWith(([IO.Path]::GetFullPath($home).TrimEnd('\')+'\'),[StringComparison]::OrdinalIgnoreCase)) 'LOCALAPPDATA_NOT_UNDER_PROFILE'
  $parent=[IO.Path]::Combine($base,'TS047B-Offline-V4')
  [pscustomobject]@{Base=$base;Parent=$parent;Root=[IO.Path]::Combine($parent,$script:V4Attempt);
    Receipt=[IO.Path]::Combine($parent,($script:V4Attempt+'.jsonl'))}
}
function Assert-V4NoReparse([string]$Path) {
  $p=[IO.Path]::GetFullPath($Path)
  while($true){
    if([IO.File]::Exists($p) -or [IO.Directory]::Exists($p)){
      $a=[IO.File]::GetAttributes($p)
      Assert-V4 (($a -band [IO.FileAttributes]::ReparsePoint) -eq 0) 'REPARSE_ANCESTOR'
    }
    $parent=[IO.Directory]::GetParent($p)
    if($null -eq $parent){break}
    $p=$parent.FullName
  }
}
function Assert-V4PrivateAcl([string]$Path,[bool]$InheritFromPrivateParent=$false) {
  Assert-V4 (-not ([IO.File]::GetAttributes($Path) -band [IO.FileAttributes]::ReparsePoint)) 'REPARSE_ITEM'
  $acl=Get-Acl -LiteralPath $Path -ErrorAction Stop
  $current=[Security.Principal.WindowsIdentity]::GetCurrent().User.Value
  $owner=$acl.GetOwner([Security.Principal.SecurityIdentifier]).Value
  Assert-V4 ($owner -eq $current) 'ACL_OWNER'
  if($InheritFromPrivateParent) {
    Assert-V4 ([IO.File]::Exists($Path)) 'INHERITED_ACL_ONLY_FOR_FILE'
    Assert-V4PrivateAcl ([IO.Path]::GetDirectoryName($Path)) $false
  } else { Assert-V4 ($acl.AreAccessRulesProtected) 'ACL_NOT_PROTECTED' }
  $allowed=@($current,'S-1-5-18')
  foreach($ace in $acl.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier])){
    if($ace.AccessControlType -eq [Security.AccessControl.AccessControlType]::Allow){
      Assert-V4 ($ace.IdentityReference.Value -in $allowed) 'ACL_UNTRUSTED_ALLOW'
    }
  }
  Assert-V4 ($acl.Access.Count -gt 0) 'ACL_EMPTY'
}
function New-V4AtomicPrivateDirectory([string]$Path) {
  # Win32 CreateDirectoryW receives a protected security descriptor AT CREATION.
  # No create-then-Set-Acl window. An existing directory is never adopted here.
  Assert-V4 (-not (Test-Path -LiteralPath $Path)) 'DIRECTORY_ALREADY_EXISTS'
  Assert-V4NoReparse (Split-Path -Parent $Path)
  if(-not ('V4NativeAcl' -as [type])){
    Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
public static class V4NativeAcl {
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
  [V4NativeAcl]::Create($Path,$sid)
  Assert-V4NoReparse $Path
  Assert-V4PrivateAcl $Path
}
# CreateNew + protected descriptor in ONE Win32 CreateFileW call.
function New-V4AtomicPrivateFile([string]$Path) {
  Assert-V4 (-not (Test-Path -LiteralPath $Path)) 'RECEIPT_ALREADY_EXISTS'
  Assert-V4NoReparse (Split-Path -Parent $Path)
  Assert-V4PrivateAcl (Split-Path -Parent $Path) $false
  if(-not ('V4NativePrivateFile' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.IO;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;
public static class V4NativePrivateFile {
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
  $stream=[V4NativePrivateFile]::Create($Path,[Security.Principal.WindowsIdentity]::GetCurrent().User.Value)
  try {
    Assert-V4NoReparse $Path
    Assert-V4PrivateAcl $Path $false
    return $stream
  } catch {$stream.Dispose();throw}
}
function Assert-V4TrustedDocument([string]$BodyPath,[string]$SignaturePath,[string]$PublicKeyPath) {
  Assert-V4 ($script:V4TrustedKeySha256 -ne ('0' * 64)) 'ISSUER_TRUST_ANCHOR_UNPROVISIONED'
  foreach($p in @($BodyPath,$SignaturePath,$PublicKeyPath)){
    Assert-V4 ([IO.File]::Exists($p)) 'SIGNED_DOCUMENT_MISSING'
    Assert-V4NoReparse $p
  }
  $key=[IO.File]::ReadAllBytes($PublicKeyPath)
  $keyHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($key))
  Assert-V4 ($keyHash -ceq $script:V4TrustedKeySha256) 'UNTRUSTED_ISSUER_KEY'
  $sigText=[IO.File]::ReadAllText($SignaturePath,[Text.Encoding]::ASCII).Trim()
  Assert-V4 ($sigText -match '^[A-Za-z0-9+/=]+$') 'SIGNATURE_ENCODING'
  $signature=[Convert]::FromBase64String($sigText)
  $body=[IO.File]::ReadAllBytes($BodyPath)
  $rsa=[Security.Cryptography.RSA]::Create()
  try {
    $rsa.ImportFromPem([Text.Encoding]::UTF8.GetString($key))
    Assert-V4 ($rsa.KeySize -ge 3072) 'ISSUER_KEY_TOO_SMALL'
    Assert-V4 ($rsa.VerifyData($body,$signature,
      [Security.Cryptography.HashAlgorithmName]::SHA256,
      [Security.Cryptography.RSASignaturePadding]::Pss)) 'INVALID_SIGNATURE'
  } finally {$rsa.Dispose();[Array]::Clear($key,0,$key.Length)}
  $json=[Text.Encoding]::UTF8.GetString($body)|ConvertFrom-Json -AsHashtable -Depth 16
  Assert-V4 ($json -is [hashtable]) 'SIGNED_DOCUMENT_SCHEMA'
  return $json
}
function Get-V4GitBlob([string]$Path) {
  $bytes=[IO.File]::ReadAllBytes($Path)
  try {
    $prefix=[Text.Encoding]::ASCII.GetBytes(('blob '+$bytes.Length+[char]0))
    $v=[byte[]]::new($prefix.Length+$bytes.Length)
    [Array]::Copy($prefix,0,$v,0,$prefix.Length)
    [Array]::Copy($bytes,0,$v,$prefix.Length,$bytes.Length)
    return [Convert]::ToHexString([Security.Cryptography.SHA1]::HashData($v)).ToLowerInvariant()
  } finally { [Array]::Clear($bytes,0,$bytes.Length) }
}
function Assert-V4Authority([string]$AuthorityDirectory,[string]$RunnerPath,[string]$LauncherPath) {
  # Two distinct signed documents: grant and original-operation reconciliation.
  # A JSON field claiming issuer/authority without the pinned signature is worthless.
  Assert-V4 ($script:V4TrustedKeySha256 -ne ('0' * 64)) 'NO_COMPETENT_ISSUER_PIN'
  $pub=Join-Path $AuthorityDirectory 'issuer.pem'
  $g=Assert-V4TrustedDocument (Join-Path $AuthorityDirectory 'grant.json') (Join-Path $AuthorityDirectory 'grant.sig') $pub
  $r=Assert-V4TrustedDocument (Join-Path $AuthorityDirectory 'reconciliation.json') (Join-Path $AuthorityDirectory 'reconciliation.sig') $pub
  Assert-V4 ($r.sourceCommit -ceq $g.sourceCommit) 'GRANT_RECONCILIATION_SOURCE_MISMATCH'
  Assert-V4 ($r.subjectBlob -ceq $g.subjectBlob) 'RECONCILIATION_SUBJECT_MISMATCH'
  foreach($d in @($g,$r)){
    Assert-V4 ($d.operation -ceq $script:V4Operation) 'OPERATION_MISMATCH'
    Assert-V4 ($d.attempt -ceq $script:V4Attempt) 'ATTEMPT_MISMATCH'
    Assert-V4 ($d.host -ceq $script:V4Host) 'HOST_MISMATCH'
    Assert-V4 ($d.issuer -ceq 'COMPETENT_EXPERIMENTAL_CONTROL') 'ISSUER_MISMATCH'
  }
  Assert-V4 ($g.scope -ceq $script:V4Scope -and $g.allowSqlEffect -ceq $true) 'SCOPE_OR_GRANT'
  Assert-V4 ($g.sourceCommit -match '^[a-f0-9]{40}
  Assert-V4 ($g.runnerSha256 -ceq (Get-FileHash -LiteralPath $RunnerPath -Algorithm SHA256).Hash) 'RUNNER_HASH_MISMATCH'
  Assert-V4 ($g.launcherSha256 -ceq (Get-FileHash -LiteralPath $LauncherPath -Algorithm SHA256).Hash) 'LAUNCHER_HASH_MISMATCH'
  Assert-V4 ($g.subjectBlob -match '^[a-f0-9]{40}$') 'SOURCE_BLOB_INVALID'
  $now=[datetimeoffset]::UtcNow
  $expiry=[datetimeoffset]::Parse($g.expiresUtc,[Globalization.CultureInfo]::InvariantCulture)
  Assert-V4 ($expiry -gt $now -and $expiry -lt $now.AddHours(24)) 'GRANT_EXPIRED_OR_TOO_WIDE'
  Assert-V4 ($r.priorEffectsReconciled -ceq $true -and $r.unknownCount -ceq 0) 'ORIGINAL_EFFECTS_UNRECONCILED'
  Assert-V4 ($r.exclusiveClaim -ceq 'CLAIMED_BY_COMPETENT_CONTROL') 'EXCLUSIVE_CLAIM_ABSENT'
  Assert-V4 ($r.claimGitCommit -match '^[a-f0-9]{40}
  Assert-V4 ($r.sourceCommit -ceq $g.sourceCommit) 'GRANT_RECONCILIATION_SOURCE_MISMATCH'
  Assert-V4 ($r.claimNonce -ceq $g.claimNonce -and $g.claimNonce -match '^[a-f0-9]{64}$') 'CLAIM_NONCE_MISMATCH'
  return [pscustomobject]@{Grant=$g;Reconciliation=$r}
}
function Assert-V4NoNetworkExposure {
  # This offline CLI fixture NEVER starts a SQL listener. Refuse even a possible
  # 3307 listener, unknown Tailscale CLI/schema, Serve or Funnel configuration.
  $connections=@(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object {$_.LocalPort -eq 3307})
  Assert-V4 ($connections.Count -eq 0) 'SQL_PORT_OCCUPIED'
  $ts=Get-Command 'tailscale.exe' -ErrorAction Stop
  foreach($mode in @('serve','funnel')){
    $raw=(& $ts.Source $mode status --json 2>$null | Out-String).Trim()
    Assert-V4 ($LASTEXITCODE -eq 0) ('TAILSCALE_'+$mode+'_UNKNOWN')
    # Strict empty-object schema only. New keys, null, empty, warnings all block.
    Assert-V4 ($raw -ceq '{}') ('TAILSCALE_'+$mode+'_CONFIG_PRESENT_OR_UNKNOWN')
  }
}
Export-ModuleMember -Function Assert-V4,Get-V4Root,Assert-V4NoReparse,Assert-V4PrivateAcl,New-V4AtomicPrivateDirectory,New-V4AtomicPrivateFile,Get-V4GitBlob,Assert-V4Authority,Assert-V4NoNetworkExposure
) 'SOURCE_COMMIT_INVALID'
  Assert-V4 ($g.subjectBlob -ceq (Get-V4GitBlob $RunnerPath)) 'SIGNED_SUBJECT_BLOB_MISMATCH'
  Assert-V4 ($g.runnerSha256 -ceq (Get-FileHash -LiteralPath $RunnerPath -Algorithm SHA256).Hash) 'RUNNER_HASH_MISMATCH'
  Assert-V4 ($g.launcherSha256 -ceq (Get-FileHash -LiteralPath $LauncherPath -Algorithm SHA256).Hash) 'LAUNCHER_HASH_MISMATCH'
  Assert-V4 ($g.subjectBlob -match '^[a-f0-9]{40}$') 'SOURCE_BLOB_INVALID'
  $now=[datetimeoffset]::UtcNow
  $expiry=[datetimeoffset]::Parse($g.expiresUtc,[Globalization.CultureInfo]::InvariantCulture)
  Assert-V4 ($expiry -gt $now -and $expiry -lt $now.AddHours(24)) 'GRANT_EXPIRED_OR_TOO_WIDE'
  Assert-V4 ($r.priorEffectsReconciled -ceq $true -and $r.unknownCount -ceq 0) 'ORIGINAL_EFFECTS_UNRECONCILED'
  Assert-V4 ($r.exclusiveClaim -ceq 'CLAIMED_BY_COMPETENT_CONTROL') 'EXCLUSIVE_CLAIM_ABSENT'
  Assert-V4 ($r.claimGitCommit -match '^[a-f0-9]{40}$' -and $r.claimBlob -match '^[a-f0-9]{40}$') 'CLAIM_PROVENANCE_MISSING'
  Assert-V4 ($r.sourceCommit -ceq $g.sourceCommit) 'GRANT_RECONCILIATION_SOURCE_MISMATCH'
  Assert-V4 ($r.claimNonce -ceq $g.claimNonce -and $g.claimNonce -match '^[a-f0-9]{64}$') 'CLAIM_NONCE_MISMATCH'
  return [pscustomobject]@{Grant=$g;Reconciliation=$r}
}
function Assert-V4NoNetworkExposure {
  # This offline CLI fixture NEVER starts a SQL listener. Refuse even a possible
  # 3307 listener, unknown Tailscale CLI/schema, Serve or Funnel configuration.
  $connections=@(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object {$_.LocalPort -eq 3307})
  Assert-V4 ($connections.Count -eq 0) 'SQL_PORT_OCCUPIED'
  $ts=Get-Command 'tailscale.exe' -ErrorAction Stop
  foreach($mode in @('serve','funnel')){
    $raw=(& $ts.Source $mode status --json 2>$null | Out-String).Trim()
    Assert-V4 ($LASTEXITCODE -eq 0) ('TAILSCALE_'+$mode+'_UNKNOWN')
    # Strict empty-object schema only. New keys, null, empty, warnings all block.
    Assert-V4 ($raw -ceq '{}') ('TAILSCALE_'+$mode+'_CONFIG_PRESENT_OR_UNKNOWN')
  }
}
Export-ModuleMember -Function Assert-V4,Get-V4Root,Assert-V4NoReparse,Assert-V4PrivateAcl,New-V4AtomicPrivateDirectory,New-V4AtomicPrivateFile,Assert-V4Authority,Assert-V4NoNetworkExposure
 -and $r.claimBlob -match '^[a-f0-9]{40}
  Assert-V4 ($r.sourceCommit -ceq $g.sourceCommit) 'GRANT_RECONCILIATION_SOURCE_MISMATCH'
  Assert-V4 ($r.claimNonce -ceq $g.claimNonce -and $g.claimNonce -match '^[a-f0-9]{64}$') 'CLAIM_NONCE_MISMATCH'
  return [pscustomobject]@{Grant=$g;Reconciliation=$r}
}
function Assert-V4NoNetworkExposure {
  # This offline CLI fixture NEVER starts a SQL listener. Refuse even a possible
  # 3307 listener, unknown Tailscale CLI/schema, Serve or Funnel configuration.
  $connections=@(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object {$_.LocalPort -eq 3307})
  Assert-V4 ($connections.Count -eq 0) 'SQL_PORT_OCCUPIED'
  $ts=Get-Command 'tailscale.exe' -ErrorAction Stop
  foreach($mode in @('serve','funnel')){
    $raw=(& $ts.Source $mode status --json 2>$null | Out-String).Trim()
    Assert-V4 ($LASTEXITCODE -eq 0) ('TAILSCALE_'+$mode+'_UNKNOWN')
    # Strict empty-object schema only. New keys, null, empty, warnings all block.
    Assert-V4 ($raw -ceq '{}') ('TAILSCALE_'+$mode+'_CONFIG_PRESENT_OR_UNKNOWN')
  }
}
Export-ModuleMember -Function Assert-V4,Get-V4Root,Assert-V4NoReparse,Assert-V4PrivateAcl,New-V4AtomicPrivateDirectory,New-V4AtomicPrivateFile,Get-V4GitBlob,Assert-V4Authority,Assert-V4NoNetworkExposure
) 'SOURCE_COMMIT_INVALID'
  Assert-V4 ($g.subjectBlob -ceq (Get-V4GitBlob $RunnerPath)) 'SIGNED_SUBJECT_BLOB_MISMATCH'
  Assert-V4 ($g.runnerSha256 -ceq (Get-FileHash -LiteralPath $RunnerPath -Algorithm SHA256).Hash) 'RUNNER_HASH_MISMATCH'
  Assert-V4 ($g.launcherSha256 -ceq (Get-FileHash -LiteralPath $LauncherPath -Algorithm SHA256).Hash) 'LAUNCHER_HASH_MISMATCH'
  Assert-V4 ($g.subjectBlob -match '^[a-f0-9]{40}$') 'SOURCE_BLOB_INVALID'
  $now=[datetimeoffset]::UtcNow
  $expiry=[datetimeoffset]::Parse($g.expiresUtc,[Globalization.CultureInfo]::InvariantCulture)
  Assert-V4 ($expiry -gt $now -and $expiry -lt $now.AddHours(24)) 'GRANT_EXPIRED_OR_TOO_WIDE'
  Assert-V4 ($r.priorEffectsReconciled -ceq $true -and $r.unknownCount -ceq 0) 'ORIGINAL_EFFECTS_UNRECONCILED'
  Assert-V4 ($r.exclusiveClaim -ceq 'CLAIMED_BY_COMPETENT_CONTROL') 'EXCLUSIVE_CLAIM_ABSENT'
  Assert-V4 ($r.claimGitCommit -match '^[a-f0-9]{40}$' -and $r.claimBlob -match '^[a-f0-9]{40}$') 'CLAIM_PROVENANCE_MISSING'
  Assert-V4 ($r.sourceCommit -ceq $g.sourceCommit) 'GRANT_RECONCILIATION_SOURCE_MISMATCH'
  Assert-V4 ($r.claimNonce -ceq $g.claimNonce -and $g.claimNonce -match '^[a-f0-9]{64}$') 'CLAIM_NONCE_MISMATCH'
  return [pscustomobject]@{Grant=$g;Reconciliation=$r}
}
function Assert-V4NoNetworkExposure {
  # This offline CLI fixture NEVER starts a SQL listener. Refuse even a possible
  # 3307 listener, unknown Tailscale CLI/schema, Serve or Funnel configuration.
  $connections=@(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object {$_.LocalPort -eq 3307})
  Assert-V4 ($connections.Count -eq 0) 'SQL_PORT_OCCUPIED'
  $ts=Get-Command 'tailscale.exe' -ErrorAction Stop
  foreach($mode in @('serve','funnel')){
    $raw=(& $ts.Source $mode status --json 2>$null | Out-String).Trim()
    Assert-V4 ($LASTEXITCODE -eq 0) ('TAILSCALE_'+$mode+'_UNKNOWN')
    # Strict empty-object schema only. New keys, null, empty, warnings all block.
    Assert-V4 ($raw -ceq '{}') ('TAILSCALE_'+$mode+'_CONFIG_PRESENT_OR_UNKNOWN')
  }
}
Export-ModuleMember -Function Assert-V4,Get-V4Root,Assert-V4NoReparse,Assert-V4PrivateAcl,New-V4AtomicPrivateDirectory,New-V4AtomicPrivateFile,Assert-V4Authority,Assert-V4NoNetworkExposure
) 'CLAIM_PROVENANCE_MISSING'
  # A signature claiming CAS is not an independently observed CAS receipt.
  Assert-V4 ($r.registryObservationVerified -ceq $true) 'OFFHOST_CAS_OBSERVATION_ABSENT'
  Assert-V4 ($r.originalProviderReceiptsJoined -ceq $true) 'ORIGINAL_PROVIDER_RECEIPTS_UNJOINED'
  Assert-V4 ($r.sourceCommit -ceq $g.sourceCommit) 'GRANT_RECONCILIATION_SOURCE_MISMATCH'
  Assert-V4 ($r.claimNonce -ceq $g.claimNonce -and $g.claimNonce -match '^[a-f0-9]{64}$') 'CLAIM_NONCE_MISMATCH'
  return [pscustomobject]@{Grant=$g;Reconciliation=$r}
}
function Assert-V4NoNetworkExposure {
  # This offline CLI fixture NEVER starts a SQL listener. Refuse even a possible
  # 3307 listener, unknown Tailscale CLI/schema, Serve or Funnel configuration.
  $connections=@(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object {$_.LocalPort -eq 3307})
  Assert-V4 ($connections.Count -eq 0) 'SQL_PORT_OCCUPIED'
  $ts=Get-Command 'tailscale.exe' -ErrorAction Stop
  foreach($mode in @('serve','funnel')){
    $raw=(& $ts.Source $mode status --json 2>$null | Out-String).Trim()
    Assert-V4 ($LASTEXITCODE -eq 0) ('TAILSCALE_'+$mode+'_UNKNOWN')
    # Strict empty-object schema only. New keys, null, empty, warnings all block.
    Assert-V4 ($raw -ceq '{}') ('TAILSCALE_'+$mode+'_CONFIG_PRESENT_OR_UNKNOWN')
  }
}
Export-ModuleMember -Function Assert-V4,Get-V4Root,Assert-V4NoReparse,Assert-V4PrivateAcl,New-V4AtomicPrivateDirectory,New-V4AtomicPrivateFile,Get-V4GitBlob,Assert-V4Authority,Assert-V4NoNetworkExposure
) 'SOURCE_COMMIT_INVALID'
  Assert-V4 ($g.subjectBlob -ceq (Get-V4GitBlob $RunnerPath)) 'SIGNED_SUBJECT_BLOB_MISMATCH'
  Assert-V4 ($g.runnerSha256 -ceq (Get-FileHash -LiteralPath $RunnerPath -Algorithm SHA256).Hash) 'RUNNER_HASH_MISMATCH'
  Assert-V4 ($g.launcherSha256 -ceq (Get-FileHash -LiteralPath $LauncherPath -Algorithm SHA256).Hash) 'LAUNCHER_HASH_MISMATCH'
  Assert-V4 ($g.subjectBlob -match '^[a-f0-9]{40}$') 'SOURCE_BLOB_INVALID'
  $now=[datetimeoffset]::UtcNow
  $expiry=[datetimeoffset]::Parse($g.expiresUtc,[Globalization.CultureInfo]::InvariantCulture)
  Assert-V4 ($expiry -gt $now -and $expiry -lt $now.AddHours(24)) 'GRANT_EXPIRED_OR_TOO_WIDE'
  Assert-V4 ($r.priorEffectsReconciled -ceq $true -and $r.unknownCount -ceq 0) 'ORIGINAL_EFFECTS_UNRECONCILED'
  Assert-V4 ($r.exclusiveClaim -ceq 'CLAIMED_BY_COMPETENT_CONTROL') 'EXCLUSIVE_CLAIM_ABSENT'
  Assert-V4 ($r.claimGitCommit -match '^[a-f0-9]{40}$' -and $r.claimBlob -match '^[a-f0-9]{40}$') 'CLAIM_PROVENANCE_MISSING'
  Assert-V4 ($r.sourceCommit -ceq $g.sourceCommit) 'GRANT_RECONCILIATION_SOURCE_MISMATCH'
  Assert-V4 ($r.claimNonce -ceq $g.claimNonce -and $g.claimNonce -match '^[a-f0-9]{64}$') 'CLAIM_NONCE_MISMATCH'
  return [pscustomobject]@{Grant=$g;Reconciliation=$r}
}
function Assert-V4NoNetworkExposure {
  # This offline CLI fixture NEVER starts a SQL listener. Refuse even a possible
  # 3307 listener, unknown Tailscale CLI/schema, Serve or Funnel configuration.
  $connections=@(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object {$_.LocalPort -eq 3307})
  Assert-V4 ($connections.Count -eq 0) 'SQL_PORT_OCCUPIED'
  $ts=Get-Command 'tailscale.exe' -ErrorAction Stop
  foreach($mode in @('serve','funnel')){
    $raw=(& $ts.Source $mode status --json 2>$null | Out-String).Trim()
    Assert-V4 ($LASTEXITCODE -eq 0) ('TAILSCALE_'+$mode+'_UNKNOWN')
    # Strict empty-object schema only. New keys, null, empty, warnings all block.
    Assert-V4 ($raw -ceq '{}') ('TAILSCALE_'+$mode+'_CONFIG_PRESENT_OR_UNKNOWN')
  }
}
Export-ModuleMember -Function Assert-V4,Get-V4Root,Assert-V4NoReparse,Assert-V4PrivateAcl,New-V4AtomicPrivateDirectory,New-V4AtomicPrivateFile,Assert-V4Authority,Assert-V4NoNetworkExposure
