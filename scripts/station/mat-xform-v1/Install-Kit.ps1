# Owner-controlled one-time installation; NOT a Commander command or a TS-EXB extractor.
[CmdletBinding()]
param([Parameter(Mandatory)][string]$Root,[Parameter(Mandatory)][string]$KitZip,
 [Parameter(Mandatory)][string]$ZipSha256,[Parameter(Mandatory)][string]$ManifestSha256,
 [Parameter(Mandatory)][string]$SourceNode,[Parameter(Mandatory)][string]$NodeSha256)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$created=$false
function Digest([byte[]]$b){[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($b)).ToLowerInvariant()}
function Absolute([string]$p){
 if($p -cnotmatch '^[A-Za-z]:\\' -or (-not [string]::Equals([IO.Path]::GetFullPath($p),$p,[StringComparison]::Ordinal))){throw 'NONCANONICAL_LOCAL_PATH'}
}
function Read-Exact([IO.Stream]$Stream,[int64]$Length,[int64]$Limit){
 if($Length -lt 0 -or $Length -gt $Limit){throw 'INPUT_BYTE_LIMIT'}
 $b=[byte[]]::new([int]$Length);$Stream.ReadExactly($b,0,$b.Length)
 if($Stream.ReadByte() -ne -1){throw 'INPUT_LENGTH_MISMATCH'}
 return ,$b
}
function Read-File([string]$p,[int64]$max){
 $attr=[IO.File]::GetAttributes($p)
 if(($attr -band ([IO.FileAttributes]::Directory -bor [IO.FileAttributes]::ReparsePoint)) -ne 0){throw 'UNSAFE_INPUT_FILE'}
 $f=[IO.FileStream]::new($p,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read)
 try{return ,(Read-Exact $f $f.Length $max)}finally{$f.Dispose()}
}
function Safe-Relative([string]$p){
 if([string]::IsNullOrEmpty($p) -or $p.Length -gt 250){throw 'ARCHIVE_PATH_LENGTH'}
 foreach($s in $p.Split('/')){
  if($s -cnotmatch '\A[A-Za-z0-9_.-]{1,96}\z' -or $s -in @('.','..') -or $s.EndsWith('.') -or $s -match '^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)'){throw 'ARCHIVE_PATH_DENIED'}
 }
}
# Typed Windows namespace: compare folded names and exact spelling at EVERY ancestor.
function Add-Namespace([Collections.Generic.Dictionary[string,string]]$Index,[string]$Name,[bool]$Directory){
 $parts=$Name.Split('/')
 for($j=0;$j -lt $parts.Length;$j++){
  $prefix=$parts[0..$j] -join '/'
  $type=if($j -lt $parts.Length-1 -or $Directory){'D:'}else{'F:'}
  $entry=$type+$prefix
  if($Index.ContainsKey($prefix)){
   if((-not [string]::Equals($Index[$prefix],$entry,[StringComparison]::Ordinal))){throw 'ARCHIVE_NAMESPACE_CONFLICT'}
  }else{$Index.Add($prefix,$entry)}
 }
}
function Assert-ManifestKeys([Text.Json.JsonElement]$Element,[string[]]$Expected){
 if($Element.ValueKind -ne [Text.Json.JsonValueKind]::Object){throw 'MANIFEST_SCHEMA'}
 $keys=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
 foreach($prop in $Element.EnumerateObject()){if(-not $keys.Add($prop.Name)){throw 'MANIFEST_DUPLICATE_KEY'}}
 if(-not $keys.SetEquals($Expected)){throw 'MANIFEST_SCHEMA'}
}
$self=[Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$trusted=@($self,'S-1-5-18','S-1-5-32-544')
$writeMask=[Security.AccessControl.FileSystemRights]::WriteData -bor [Security.AccessControl.FileSystemRights]::AppendData -bor [Security.AccessControl.FileSystemRights]::WriteAttributes -bor [Security.AccessControl.FileSystemRights]::WriteExtendedAttributes -bor [Security.AccessControl.FileSystemRights]::Delete -bor [Security.AccessControl.FileSystemRights]::DeleteSubdirectoriesAndFiles -bor [Security.AccessControl.FileSystemRights]::ChangePermissions -bor [Security.AccessControl.FileSystemRights]::TakeOwnership
function Assert-Acl([string]$p){
 $acl=Get-Acl -LiteralPath $p
 $raw=[Security.AccessControl.RawSecurityDescriptor]::new($acl.GetSecurityDescriptorBinaryForm(),0)
 if($null -eq $raw.DiscretionaryAcl -or $trusted -notcontains $raw.Owner.Value){throw 'UNTRUSTED_OWNER_OR_DACL'}
 foreach($rule in $acl.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier])){
  if($rule.AccessControlType -eq [Security.AccessControl.AccessControlType]::Allow -and ($rule.FileSystemRights -band $writeMask) -ne 0 -and $trusted -notcontains $rule.IdentityReference.Value){throw 'UNTRUSTED_WRITE_ACL'}
 }
 return $acl
}
function Write-Exclusive([string]$p,[byte[]]$b){
 $f=[IO.FileStream]::new($p,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
 try{$f.Write($b,0,$b.Length);$f.Flush($true)}finally{$f.Dispose()}
 if((-not [string]::Equals((Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant(),(Digest $b),[StringComparison]::Ordinal))){throw 'INSTALLED_BYTES_MISMATCH'}
}
try{
 if(-not $IsWindows){throw 'WINDOWS_ONLY'}
 foreach($p in @($Root,$KitZip,$SourceNode)){Absolute $p}
 foreach($h in @($ZipSha256,$ManifestSha256,$NodeSha256)){if($h -cnotmatch '\A[a-f0-9]{64}\z'){throw 'HASH_ARGUMENT'}}
 $parent=[IO.Path]::GetDirectoryName($Root)
 # Stable trusted ancestor chain and exclusive maintenance are externally admitted; no parent mutations.
 $p=$parent
 while($p){
  $attr=[IO.File]::GetAttributes($p)
  if(($attr -band [IO.FileAttributes]::Directory) -eq 0 -or ($attr -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'UNSAFE_PARENT_CHAIN'}
  $next=[IO.Path]::GetDirectoryName($p);if($next -eq $p){break};$p=$next
 }
 $null=Assert-Acl $parent
 $zipBytes=Read-File $KitZip (2*1024*1024)
 if((-not [string]::Equals((Digest $zipBytes),$ZipSha256,[StringComparison]::Ordinal))){throw 'ZIP_HASH'}
 $nodeBytes=Read-File $SourceNode (128*1024*1024)
 if((-not [string]::Equals((Digest $nodeBytes),$NodeSha256,[StringComparison]::Ordinal))){throw 'NODE_SOURCE_HASH'}
 $mem=[IO.MemoryStream]::new($zipBytes,$false);$zip=[IO.Compression.ZipArchive]::new($mem,[IO.Compression.ZipArchiveMode]::Read,$false)
 $payload=[Collections.Generic.Dictionary[string,byte[]]]::new([StringComparer]::Ordinal)
 $seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
 $dirs=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
 $namespace=[Collections.Generic.Dictionary[string,string]]::new([StringComparer]::OrdinalIgnoreCase)
 foreach($d in @('install','runtime','inbox','runs')){Add-Namespace $namespace $d $true}
 Add-Namespace $namespace 'runtime/node.exe' $false
 Add-Namespace $namespace 'manifest.json' $false
 $prefix='ts-ee-mat-xform-kit/'
 try{
  if($zip.Entries.Count -lt 1 -or $zip.Entries.Count -gt 6000){throw 'ARCHIVE_ENTRY_LIMIT'}
  $total=0L
  foreach($e in $zip.Entries){
   $name=$e.FullName
   if(-not $name.StartsWith($prefix,[StringComparison]::Ordinal) -or -not $seen.Add($name)){throw 'ARCHIVE_NAME_COLLISION_OR_PREFIX'}
   $rel=$name.Substring($prefix.Length)
   if((($e.ExternalAttributes -shr 16) -band 0xf000) -eq 0xa000 -or ($e.ExternalAttributes -band 0x400) -ne 0){throw 'ARCHIVE_LINK'}
   if($rel.EndsWith('/')){
    $rel=$rel.Substring(0,$rel.Length-1);Safe-Relative $rel
    Add-Namespace $namespace $rel $true
    if($e.Length -ne 0){throw 'DIRECTORY_HAS_BYTES'}
    $null=$dirs.Add($rel);continue
   }
   Safe-Relative $rel
   Add-Namespace $namespace $rel $false
   if((-not [string]::Equals($rel,'manifest.json',[StringComparison]::Ordinal)) -and -not $rel.StartsWith('install/',[StringComparison]::Ordinal)){throw 'ARCHIVE_EXTRA_FILE'}
   $total+=$e.Length;if($total -gt 64*1024*1024){throw 'ARCHIVE_TOTAL_LIMIT'}
   $stream=$e.Open()
   try{$payload.Add($rel,(Read-Exact $stream $e.Length (4*1024*1024)))}finally{$stream.Dispose()}
  }
 }finally{$zip.Dispose();$mem.Dispose()}
 if(-not $payload.ContainsKey('manifest.json') -or (-not [string]::Equals((Digest $payload['manifest.json']),$ManifestSha256,[StringComparison]::Ordinal))){throw 'MANIFEST_HASH'}
 if($payload['manifest.json'].Length -gt 2*1024*1024){throw 'MANIFEST_LIMIT'}
 $manifestText=[Text.UTF8Encoding]::new($false,$true).GetString($payload['manifest.json'])
 $manifestDoc=[Text.Json.JsonDocument]::Parse($manifestText)
 $manifestFiles=[Collections.Generic.List[object]]::new()
 $canonicalEntries=[Collections.Generic.List[string]]::new()
 try{
  $element=$manifestDoc.RootElement
  Assert-ManifestKeys $element @('schema','files')
  if((-not [string]::Equals($element.GetProperty('schema').GetString(),'ts-ee/mat-xform-install/v1',[StringComparison]::Ordinal))){throw 'MANIFEST_SCHEMA'}
  $items=$element.GetProperty('files')
  if($items.ValueKind -ne [Text.Json.JsonValueKind]::Array -or $items.GetArrayLength() -lt 1 -or $items.GetArrayLength()+1 -ne $payload.Count){throw 'MANIFEST_INVENTORY'}
  foreach($item in $items.EnumerateArray()){
   Assert-ManifestKeys $item @('path','bytes','sha256')
   $name=$item.GetProperty('path').GetString()
   $length=$item.GetProperty('bytes').GetInt64()
   $hash=$item.GetProperty('sha256').GetString()
   Safe-Relative $name
   if($length -lt 0 -or $length -gt 4*1024*1024 -or $hash -cnotmatch '\A[a-f0-9]{64}\z'){throw 'MANIFEST_ENTRY'}
   $manifestFiles.Add(@{path=$name;bytes=$length;sha256=$hash})
   # Safe-Relative restricts names to unescaped ASCII; decimal length is invariant.
   $canonicalEntries.Add(('{"bytes":'+$length.ToString([Globalization.CultureInfo]::InvariantCulture)+',"path":"'+$name+'","sha256":"'+$hash+'"}'))
  }
 }finally{$manifestDoc.Dispose()}
 $canonicalManifest='{"files":['+($canonicalEntries -join ',')+'],"schema":"ts-ee/mat-xform-install/v1"}'
 if((-not [string]::Equals($manifestText,$canonicalManifest,[StringComparison]::Ordinal))){throw 'MANIFEST_NONCANONICAL'}
 $expected=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
 $allowedDirs=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
 foreach($d in @('install','runtime','inbox','runs')){$null=$allowedDirs.Add($d)}
 foreach($f in $manifestFiles){
  Safe-Relative $f.path
  $name='install/'+$f.path
  if(-not $expected.Add($name) -or -not $payload.ContainsKey($name) -or $payload[$name].Length -ne $f.bytes -or (-not [string]::Equals((Digest $payload[$name]),$f.sha256,[StringComparison]::Ordinal))){throw 'MANIFEST_FILE_MISMATCH'}
  $segments=$name.Split('/')
  for($i=1;$i -lt $segments.Length;$i++){$null=$allowedDirs.Add(($segments[0..($i-1)] -join '/'))}
 }
 foreach($d in $dirs){if(-not $allowedDirs.Contains($d)){throw 'ARCHIVE_EXTRA_DIRECTORY'}}
 foreach($required in @('install/guard.mjs','install/Invoke-Guard.ps1','install/package.json','install/package-lock.json','install/src/mat-xform/cli.ts','install/src/mat-xform/contracts.ts','install/src/mat-xform/materializer.ts','install/node_modules/zod/package.json')){if(-not $payload.ContainsKey($required)){throw 'KIT_REQUIRED_FILE'}}
 # All bytes and paths are verified before any target creation. Atomic create with explicit protected DACL.
 Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class MatXformInstallDirectory {
 [StructLayout(LayoutKind.Sequential)] private struct SA { public int Length; public IntPtr Descriptor; public int InheritHandle; }
 [DllImport("kernel32.dll",EntryPoint="CreateDirectoryW",CharSet=CharSet.Unicode,SetLastError=true)]
 [return:MarshalAs(UnmanagedType.Bool)] private static extern bool Create(string path,ref SA a);
 [DllImport("advapi32.dll",EntryPoint="ConvertStringSecurityDescriptorToSecurityDescriptorW",CharSet=CharSet.Unicode,SetLastError=true)]
 [return:MarshalAs(UnmanagedType.Bool)] private static extern bool Parse(string s,uint rev,out IntPtr p,out uint size);
 [DllImport("kernel32.dll")] private static extern IntPtr LocalFree(IntPtr p);
 public static void Reserve(string path,string sid){
  IntPtr p;uint size;
  if(!Parse("D:P(A;OICI;FA;;;"+sid+")(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)",1,out p,out size))throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error());
  try{var a=new SA{Length=Marshal.SizeOf<SA>(),Descriptor=p,InheritHandle=0};if(!Create(path,ref a))throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error(),"INSTALL_ROOT_RESERVATION_FAILED");}
  finally{LocalFree(p);}
 }
}
'@
 [MatXformInstallDirectory]::Reserve($Root,$self)
 $created=$true
 $acl=Assert-Acl $Root;if(-not $acl.AreAccessRulesProtected){throw 'ROOT_DACL_NOT_PROTECTED'}
 foreach($d in @($allowedDirs | Sort-Object Length)){[IO.Directory]::CreateDirectory((Join-Path $Root ($d.Replace('/','\')))) | Out-Null}
 foreach($name in $payload.Keys){Write-Exclusive (Join-Path $Root ($name.Replace('/','\'))) $payload[$name]}
 Write-Exclusive (Join-Path $Root 'runtime\node.exe') $nodeBytes
 $actualAcl=Assert-Acl $Root
 $sddl=$actualAcl.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Owner -bor [Security.AccessControl.AccessControlSections]::Group -bor [Security.AccessControl.AccessControlSections]::Access)
 $result=@{schema='ts-ee/mat-xform-install-terminal/v1';status='INSTALLED_NOT_ADMITTED';effect='CONFIRMED';root=$Root;zip_sha256=$ZipSha256;manifest_sha256=$ManifestSha256;node_sha256=$NodeSha256;root_acl_sha256=(Digest ([Text.Encoding]::UTF8.GetBytes($sddl)));entry_sha256=(Digest $payload['install/Invoke-Guard.ps1']);guard_sha256=(Digest $payload['install/guard.mjs']);file_count=$manifestFiles.Count;Product_effect='NONE'}
 [Console]::WriteLine(($result | ConvertTo-Json -Compress))
 exit 0
}catch{
 $status=if($created){'UNAVAILABLE'}else{'BLOCKED_PRECONDITION'}
 $effect=if($created){'UNKNOWN'}else{'NONE'}
 [Console]::WriteLine((@{schema='ts-ee/mat-xform-install-terminal/v1';status=$status;effect=$effect;root=$Root;reason=$_.Exception.Message;Product_effect='NONE'}|ConvertTo-Json -Compress))
 exit 1
}
