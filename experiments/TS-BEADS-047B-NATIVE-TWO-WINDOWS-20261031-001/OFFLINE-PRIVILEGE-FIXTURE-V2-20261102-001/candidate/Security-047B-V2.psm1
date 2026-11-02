# TS-BEADS 047B V2. EXPERIMENTAL SOURCE ONLY; NO GRANT OR SQL EFFECT IS IMPLIED.
Set-StrictMode -Version Latest
$script:V2Operation='TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001'
$script:V2Host='DESKTOP-DJLBEQH'
$script:V2Attempt='TS-BEADS-047B-DOLT-FIXTURE-V2-20261102-001'
$script:V2Scope='OFFLINE_DOLT_PRIVILEGE_PERSISTENCE_ONLY'
# Deliberately UNPROVISIONED. Only a new independently reviewed immutable source
# revision may pin a real competent issuer key. A caller-supplied hash is NEVER trust.
$script:V2TrustedKeySha256=('0' * 64)
$script:V2DoltSha256='BED880C0E6B522498A563FCD1F0FC1E25527BA07E66C1E0A85C2242B64DFD967'
function Assert-V2([bool]$Condition,[string]$Code) {
  if(-not $Condition){throw [System.InvalidOperationException]::new($Code)}
}
function Get-V2Root {
  Assert-V2 ([Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT) 'WINDOWS_REQUIRED'
  $local=[Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)
  Assert-V2 (-not [string]::IsNullOrWhiteSpace($local)) 'LOCALAPPDATA_UNRESOLVED'
  $base=[IO.Path]::GetFullPath($local).TrimEnd('\')
  Assert-V2 ($base -eq [IO.Path]::GetFullPath($env:LOCALAPPDATA).TrimEnd('\')) 'LOCALAPPDATA_ENV_MISMATCH'
  $home=[Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
  Assert-V2 ($base.StartsWith(([IO.Path]::GetFullPath($home).TrimEnd('\')+'\'),[StringComparison]::OrdinalIgnoreCase)) 'LOCALAPPDATA_NOT_UNDER_PROFILE'
  $parent=[IO.Path]::Combine($base,'TS047B-Offline-V2')
  [pscustomobject]@{Base=$base;Parent=$parent;Root=[IO.Path]::Combine($parent,$script:V2Attempt);
    Receipt=[IO.Path]::Combine($parent,($script:V2Attempt+'.jsonl'))}
}
function Assert-V2NoReparse([string]$Path) {
  $p=[IO.Path]::GetFullPath($Path)
  while($true){
    if([IO.File]::Exists($p) -or [IO.Directory]::Exists($p)){
      $a=[IO.File]::GetAttributes($p)
      Assert-V2 (($a -band [IO.FileAttributes]::ReparsePoint) -eq 0) 'REPARSE_ANCESTOR'
    }
    $parent=[IO.Directory]::GetParent($p)
    if($null -eq $parent){break}
    $p=$parent.FullName
  }
}
function Assert-V2PrivateAcl([string]$Path) {
  Assert-V2 (-not ([IO.File]::GetAttributes($Path) -band [IO.FileAttributes]::ReparsePoint)) 'REPARSE_ITEM'
  $acl=Get-Acl -LiteralPath $Path -ErrorAction Stop
  $current=[Security.Principal.WindowsIdentity]::GetCurrent().User.Value
  $owner=$acl.GetOwner([Security.Principal.SecurityIdentifier]).Value
  Assert-V2 ($owner -eq $current) 'ACL_OWNER'
  Assert-V2 ($acl.AreAccessRulesProtected) 'ACL_NOT_PROTECTED'
  $allowed=@($current,'S-1-5-18')
  foreach($ace in $acl.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier])){
    if($ace.AccessControlType -eq [Security.AccessControl.AccessControlType]::Allow){
      Assert-V2 ($ace.IdentityReference.Value -in $allowed) 'ACL_UNTRUSTED_ALLOW'
    }
  }
  Assert-V2 ($acl.Access.Count -gt 0) 'ACL_EMPTY'
}
function New-V2AtomicPrivateDirectory([string]$Path) {
  # Win32 CreateDirectoryW receives a protected security descriptor AT CREATION.
  # No create-then-Set-Acl window. An existing directory is never adopted here.
  Assert-V2 (-not (Test-Path -LiteralPath $Path)) 'DIRECTORY_ALREADY_EXISTS'
  Assert-V2NoReparse (Split-Path -Parent $Path)
  if(-not ('V2NativeAcl' -as [type])){
    Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
public static class V2NativeAcl {
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
  string sddl="O:"+userSid+"G:"+userSid+"D:P(A;;FA;;;"+userSid+")(A;;FA;;;SY)";
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
  [V2NativeAcl]::Create($Path,$sid)
  Assert-V2NoReparse $Path
  Assert-V2PrivateAcl $Path
}
function Assert-V2TrustedDocument([string]$BodyPath,[string]$SignaturePath,[string]$PublicKeyPath) {
  Assert-V2 ($script:V2TrustedKeySha256 -ne ('0' * 64)) 'ISSUER_TRUST_ANCHOR_UNPROVISIONED'
  foreach($p in @($BodyPath,$SignaturePath,$PublicKeyPath)){
    Assert-V2 ([IO.File]::Exists($p)) 'SIGNED_DOCUMENT_MISSING'
    Assert-V2NoReparse $p
  }
  $key=[IO.File]::ReadAllBytes($PublicKeyPath)
  $keyHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($key))
  Assert-V2 ($keyHash -ceq $script:V2TrustedKeySha256) 'UNTRUSTED_ISSUER_KEY'
  $sigText=[IO.File]::ReadAllText($SignaturePath,[Text.Encoding]::ASCII).Trim()
  Assert-V2 ($sigText -match '^[A-Za-z0-9+/=]+$') 'SIGNATURE_ENCODING'
  $signature=[Convert]::FromBase64String($sigText)
  $body=[IO.File]::ReadAllBytes($BodyPath)
  $rsa=[Security.Cryptography.RSA]::Create()
  try {
    $rsa.ImportFromPem([Text.Encoding]::UTF8.GetString($key))
    Assert-V2 ($rsa.KeySize -ge 3072) 'ISSUER_KEY_TOO_SMALL'
    Assert-V2 ($rsa.VerifyData($body,$signature,
      [Security.Cryptography.HashAlgorithmName]::SHA256,
      [Security.Cryptography.RSASignaturePadding]::Pss)) 'INVALID_SIGNATURE'
  } finally {$rsa.Dispose();[Array]::Clear($key,0,$key.Length)}
  $json=[Text.Encoding]::UTF8.GetString($body)|ConvertFrom-Json -AsHashtable -Depth 16
  Assert-V2 ($json -is [hashtable]) 'SIGNED_DOCUMENT_SCHEMA'
  return $json
}
function Assert-V2Authority([string]$AuthorityDirectory,[string]$RunnerPath,[string]$LauncherPath) {
  # Two distinct signed documents: grant and original-operation reconciliation.
  # A JSON field claiming issuer/authority without the pinned signature is worthless.
  Assert-V2 ($script:V2TrustedKeySha256 -ne ('0' * 64)) 'NO_COMPETENT_ISSUER_PIN'
  $pub=Join-Path $AuthorityDirectory 'issuer.pem'
  $g=Assert-V2TrustedDocument (Join-Path $AuthorityDirectory 'grant.json') (Join-Path $AuthorityDirectory 'grant.sig') $pub
  $r=Assert-V2TrustedDocument (Join-Path $AuthorityDirectory 'reconciliation.json') (Join-Path $AuthorityDirectory 'reconciliation.sig') $pub
  foreach($d in @($g,$r)){
    Assert-V2 ($d.operation -ceq $script:V2Operation) 'OPERATION_MISMATCH'
    Assert-V2 ($d.attempt -ceq $script:V2Attempt) 'ATTEMPT_MISMATCH'
    Assert-V2 ($d.host -ceq $script:V2Host) 'HOST_MISMATCH'
    Assert-V2 ($d.issuer -ceq 'COMPETENT_EXPERIMENTAL_CONTROL') 'ISSUER_MISMATCH'
  }
  Assert-V2 ($g.scope -ceq $script:V2Scope -and $g.allowSqlEffect -ceq $true) 'SCOPE_OR_GRANT'
  Assert-V2 ($g.sourceCommit -match '^[a-f0-9]{40}$') 'SOURCE_COMMIT_INVALID'
  Assert-V2 ($g.runnerSha256 -ceq (Get-FileHash -LiteralPath $RunnerPath -Algorithm SHA256).Hash) 'RUNNER_HASH_MISMATCH'
  Assert-V2 ($g.launcherSha256 -ceq (Get-FileHash -LiteralPath $LauncherPath -Algorithm SHA256).Hash) 'LAUNCHER_HASH_MISMATCH'
  Assert-V2 ($g.subjectBlob -match '^[a-f0-9]{40}$') 'SOURCE_BLOB_INVALID'
  $now=[datetimeoffset]::UtcNow
  $expiry=[datetimeoffset]::Parse($g.expiresUtc,[Globalization.CultureInfo]::InvariantCulture)
  Assert-V2 ($expiry -gt $now -and $expiry -lt $now.AddHours(24)) 'GRANT_EXPIRED_OR_TOO_WIDE'
  Assert-V2 ($r.priorEffectsReconciled -ceq $true -and $r.unknownCount -ceq 0) 'ORIGINAL_EFFECTS_UNRECONCILED'
  Assert-V2 ($r.exclusiveClaim -ceq 'CLAIMED_BY_COMPETENT_CONTROL') 'EXCLUSIVE_CLAIM_ABSENT'
  Assert-V2 ($r.claimGitCommit -match '^[a-f0-9]{40}$' -and $r.claimBlob -match '^[a-f0-9]{40}$') 'CLAIM_PROVENANCE_MISSING'
  Assert-V2 ($r.sourceCommit -ceq $g.sourceCommit) 'GRANT_RECONCILIATION_SOURCE_MISMATCH'
  Assert-V2 ($r.claimNonce -ceq $g.claimNonce -and $g.claimNonce -match '^[a-f0-9]{64}$') 'CLAIM_NONCE_MISMATCH'
  return [pscustomobject]@{Grant=$g;Reconciliation=$r}
}
function Assert-V2NoNetworkExposure {
  # This offline CLI fixture NEVER starts a SQL listener. Refuse even a possible
  # 3307 listener, unknown Tailscale CLI/schema, Serve or Funnel configuration.
  $connections=@(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object {$_.LocalPort -eq 3307})
  Assert-V2 ($connections.Count -eq 0) 'SQL_PORT_OCCUPIED'
  $ts=Get-Command 'tailscale.exe' -ErrorAction Stop
  foreach($mode in @('serve','funnel')){
    $raw=(& $ts.Source $mode status --json 2>$null | Out-String).Trim()
    Assert-V2 ($LASTEXITCODE -eq 0) ('TAILSCALE_'+$mode+'_UNKNOWN')
    # Strict empty-object schema only. New keys, null, empty, warnings all block.
    Assert-V2 ($raw -ceq '{}') ('TAILSCALE_'+$mode+'_CONFIG_PRESENT_OR_UNKNOWN')
  }
}
Export-ModuleMember -Function Assert-V2,Get-V2Root,Assert-V2NoReparse,Assert-V2PrivateAcl,New-V2AtomicPrivateDirectory,Assert-V2Authority,Assert-V2NoNetworkExposure
