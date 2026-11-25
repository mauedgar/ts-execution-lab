[CmdletBinding()]
param([Parameter(Mandatory)][string]$Root,[Parameter(Mandatory)][string]$Attempt,
 [Parameter(Mandatory)][string]$GrantSha256,[Parameter(Mandatory)][string]$Node,
 [Parameter(Mandatory)][string]$NodeSha256,[Parameter(Mandatory)][string]$GuardSha256)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$launched=$false;$nativeExit=$null;$stdoutBytes=$null;$stderrBytes=$null
function Hash([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
function Assert-Path([string]$Path,[bool]$Directory) {
 $a=[IO.File]::GetAttributes($Path)
 if(($a -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or ((($a -band [IO.FileAttributes]::Directory) -ne 0) -ne $Directory)){throw 'UNSAFE_OBJECT'}
}
$self=[Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$trusted=@($self,'S-1-5-18','S-1-5-32-544')
$writeMask=[Security.AccessControl.FileSystemRights]::WriteData -bor [Security.AccessControl.FileSystemRights]::AppendData -bor [Security.AccessControl.FileSystemRights]::WriteAttributes -bor [Security.AccessControl.FileSystemRights]::WriteExtendedAttributes -bor [Security.AccessControl.FileSystemRights]::Delete -bor [Security.AccessControl.FileSystemRights]::DeleteSubdirectoriesAndFiles -bor [Security.AccessControl.FileSystemRights]::ChangePermissions -bor [Security.AccessControl.FileSystemRights]::TakeOwnership
function Assert-Acl([string]$Path) {
 $acl=Get-Acl -LiteralPath $Path
 $raw=[Security.AccessControl.RawSecurityDescriptor]::new($acl.GetSecurityDescriptorBinaryForm(),0)
 if($null -eq $raw.DiscretionaryAcl -or $trusted -notcontains $raw.Owner.Value){throw 'UNTRUSTED_OWNER_OR_DACL'}
 foreach($rule in $acl.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier])){
  if($rule.AccessControlType -eq [Security.AccessControl.AccessControlType]::Allow -and ($rule.FileSystemRights -band $writeMask) -ne 0 -and $trusted -notcontains $rule.IdentityReference.Value){throw 'UNTRUSTED_WRITE_ACL'}
 }
 return $acl
}
function Assert-Tree([string]$Path) {
 $stack=[Collections.Generic.Stack[string]]::new();$stack.Push($Path);$count=0
 while($stack.Count){
  $p=$stack.Pop();Assert-Path $p $true;$null=Assert-Acl $p
  foreach($entry in [IO.Directory]::EnumerateFileSystemEntries($p)){
   $count++;if($count -gt 6000){throw 'TREE_LIMIT'}
   $attr=[IO.File]::GetAttributes($entry);if(($attr -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'UNSAFE_OBJECT'}
   if(($attr -band [IO.FileAttributes]::Directory) -ne 0){$stack.Push($entry)}else{$null=Assert-Acl $entry}
  }
 }
}
function Resolve-Terminal([byte[]]$Out,[byte[]]$Err,[int]$Code) {
 if($Err.Length -ne 0){throw 'GUARD_STDERR_PRESENT'}
 $text=[Text.UTF8Encoding]::new($false,$true).GetString($Out)
 if($text -cnotmatch '\A[^\r\n]+\r?\n\z'){throw 'MISSING_OR_AMBIGUOUS_GUARD_TERMINAL'}
 $line=$text.TrimEnd([char]13,[char]10)
 $doc=[Text.Json.JsonDocument]::Parse($line)
 try{
  $r=$doc.RootElement
  if($r.ValueKind -ne [Text.Json.JsonValueKind]::Object){throw 'GUARD_TERMINAL_NOT_OBJECT'}
  $keys=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
  foreach($prop in $r.EnumerateObject()){if(-not $keys.Add($prop.Name)){throw 'GUARD_TERMINAL_DUPLICATE'}}
  $status=$r.GetProperty('status').GetString();$effect=$r.GetProperty('effect').GetString()
  if((-not [string]::Equals($r.GetProperty('schema').GetString(),'ts-ee/mat-xform-station-terminal/v1',[StringComparison]::Ordinal)) -or (-not [string]::Equals($r.GetProperty('attempt').GetString(),$Attempt,[StringComparison]::Ordinal)) -or (-not [string]::Equals($r.GetProperty('Product_effect').GetString(),'NONE',[StringComparison]::Ordinal))){throw 'GUARD_TERMINAL_IDENTITY'}
  if([string]::Equals($status,'PASS',[StringComparison]::Ordinal)){
   $expected=@('schema','attempt','status','effect','grant_sha256','carrier_sha256','request_identity','result_sha256','receipt_sha256','artifact_count','Product_effect')
   if(-not $keys.SetEquals([string[]]$expected) -or $Code -ne 0 -or (-not [string]::Equals($effect,'CONFIRMED',[StringComparison]::Ordinal)) -or (-not [string]::Equals($r.GetProperty('grant_sha256').GetString(),$GrantSha256,[StringComparison]::Ordinal)) -or (-not [string]::Equals($r.GetProperty('carrier_sha256').GetString(),$g.carrier_sha256,[StringComparison]::Ordinal)) -or (-not [string]::Equals($r.GetProperty('request_identity').GetString(),('sha256:'+$g.carrier_sha256),[StringComparison]::Ordinal)) -or $r.GetProperty('artifact_count').GetInt32() -ne $g.artifacts.Count){throw 'GUARD_PASS_CONTRADICTION'}
   foreach($kind in @('result','receipt')){
    $p=Join-Path $runs ($Attempt+'.'+$kind+'.json')
    Assert-Path $p $false;$null=Assert-Acl $p
    if((-not [string]::Equals((Hash $p),$r.GetProperty($kind+'_sha256').GetString(),[StringComparison]::Ordinal))){throw 'GUARD_PUBLICATION_HASH'}
   }
  }else{
   $expected=@('schema','attempt','status','effect','reason','Product_effect')
   if(-not $keys.SetEquals([string[]]$expected) -or $Code -ne 1 -or -not (([string]::Equals($status,'BLOCKED_PRECONDITION',[StringComparison]::Ordinal) -and [string]::Equals($effect,'NONE',[StringComparison]::Ordinal)) -or ([string]::Equals($status,'UNAVAILABLE',[StringComparison]::Ordinal) -and [string]::Equals($effect,'UNKNOWN',[StringComparison]::Ordinal)))){throw 'GUARD_FAILURE_CONTRADICTION'}
   $reason=$r.GetProperty('reason').GetString();if([string]::IsNullOrEmpty($reason) -or $reason.Length -gt 240){throw 'GUARD_REASON'}
  }
  return $line
 }finally{$doc.Dispose()}
}
try{
 if(-not $IsWindows -or $Attempt -cnotmatch '\A[A-Za-z0-9_-]{1,96}\z' -or $Root -cnotmatch '^[A-Za-z]:\\' -or (-not [string]::Equals([IO.Path]::GetFullPath($Root),$Root,[StringComparison]::Ordinal))){throw 'ARGUMENTS'}
 foreach($h in @($GrantSha256,$NodeSha256,$GuardSha256)){if($h -cnotmatch '\A[a-f0-9]{64}\z'){throw 'HASH_ARGUMENT'}}
 # The stable, exclusively owned parent chain is an externally admitted precondition.
 # Check every ancestor for reparse points; do not change ACLs.
 $p=$Root;while($p){Assert-Path $p $true;$next=[IO.Path]::GetDirectoryName($p);if($next -eq $p){break};$p=$next}
 $acl=Assert-Acl $Root;if(-not $acl.AreAccessRulesProtected){throw 'ROOT_DACL_NOT_PROTECTED'}
 $sddl=$acl.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Owner -bor [Security.AccessControl.AccessControlSections]::Group -bor [Security.AccessControl.AccessControlSections]::Access)
 $aclHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($sddl))).ToLowerInvariant()
 $inbox=Join-Path $Root 'inbox';$runs=Join-Path $Root 'runs'
 foreach($p in @($inbox,$runs)){Assert-Path $p $true;$null=Assert-Acl $p}
 $grant=Join-Path $inbox ($Attempt+'.grant.json');$carrier=Join-Path $inbox ($Attempt+'.txt');$manifest=Join-Path $Root 'manifest.json';$guard=Join-Path $Root 'install\guard.mjs'
 foreach($p in @($grant,$carrier,$manifest)){Assert-Path $p $false;$null=Assert-Acl $p}
 if(([IO.FileInfo]::new($grant)).Length -gt 32768 -or (-not [string]::Equals((Hash $grant),$GrantSha256,[StringComparison]::Ordinal))){throw 'GRANT_HASH_OR_SIZE'}
 $g=Get-Content -LiteralPath $grant -Raw -Encoding UTF8 | ConvertFrom-Json -AsHashtable
 if((-not [string]::Equals($g.root_acl_sha256,$aclHash,[StringComparison]::Ordinal)) -or (-not [string]::Equals($g.node_sha256,$NodeSha256,[StringComparison]::Ordinal)) -or (-not [string]::Equals($g.station_root,$Root,[StringComparison]::Ordinal)) -or (-not [string]::Equals($g.attempt,$Attempt,[StringComparison]::Ordinal))){throw 'GRANT_BINDING'}
 Assert-Tree (Join-Path $Root 'install')
 Assert-Path $guard $false
 if((-not [string]::Equals((Hash $guard),$GuardSha256,[StringComparison]::Ordinal))){throw 'GUARD_HASH'}
 $runtime=Join-Path $Root 'runtime';$expectedNode=Join-Path $runtime 'node.exe'
 if((-not [string]::Equals([IO.Path]::GetFullPath($Node),$Node,[StringComparison]::Ordinal)) -or (-not [string]::Equals($Node,$expectedNode,[StringComparison]::Ordinal))){throw 'RUNTIME_PATH_BINDING'}
 Assert-Tree $runtime
 $runtimeEntries=@([IO.Directory]::EnumerateFileSystemEntries($runtime))
 if($runtimeEntries.Count -ne 1 -or (-not [string]::Equals($runtimeEntries[0],$expectedNode,[StringComparison]::Ordinal))){throw 'RUNTIME_INVENTORY'}
 Assert-Path $Node $false;if((-not [string]::Equals((Hash $Node),$NodeSha256,[StringComparison]::Ordinal))){throw 'NODE_HASH'}
 # Bound both native streams before interpreting a terminal. No unbounded ReadToEnd.
 Add-Type -TypeDefinition @'
using System;
using System.IO;
using System.Threading.Tasks;
public static class MatXformBoundedNative {
 public static async Task<byte[]> Read(Stream s,int cap) {
  using(var m=new MemoryStream()) {
   byte[] b=new byte[4096]; int n;
   while((n=await s.ReadAsync(b,0,b.Length).ConfigureAwait(false))!=0) {
    if(m.Length+n>cap)throw new IOException("NATIVE_STREAM_LIMIT");
    m.Write(b,0,n);
   }
   return m.ToArray();
  }
 }
}
'@
 # No caller NODE_OPTIONS, NODE_PATH or arbitrary child environment.
 $psi=[Diagnostics.ProcessStartInfo]::new();$psi.FileName=$Node;$psi.UseShellExecute=$false
 $psi.WorkingDirectory=Join-Path $Root 'install';$psi.Environment.Clear()
 $psi.RedirectStandardOutput=$true;$psi.RedirectStandardError=$true
 $psi.Environment['SystemRoot']=$env:SystemRoot;$psi.Environment['WINDIR']=$env:WINDIR
 foreach($arg in @($guard,$Root,$Attempt,$GrantSha256)){$psi.ArgumentList.Add($arg)}
 $process=[Diagnostics.Process]::new();$process.StartInfo=$psi
 $launched=$true
 $outTask=$null;$errTask=$null
 try{
  if(-not $process.Start()){throw 'START_FAILED'}
  $outTask=[MatXformBoundedNative]::Read($process.StandardOutput.BaseStream,16384)
  $errTask=[MatXformBoundedNative]::Read($process.StandardError.BaseStream,16384)
  $waitTask=$process.WaitForExitAsync()
  $all=[Threading.Tasks.Task]::WhenAll([Threading.Tasks.Task[]]@($outTask,$errTask,$waitTask))
  $deadline=[Threading.Tasks.Task]::Delay(180000)
  $winner=[Threading.Tasks.Task]::WhenAny([Threading.Tasks.Task[]]@($all,$deadline)).GetAwaiter().GetResult()
  if(-not [Object]::ReferenceEquals($winner,$all)){throw 'GUARD_DEADLINE'}
  if($process.HasExited){$nativeExit=$process.ExitCode}
  $all.GetAwaiter().GetResult()
  $stdoutBytes=$outTask.GetAwaiter().GetResult();$stderrBytes=$errTask.GetAwaiter().GetResult()
  $line=Resolve-Terminal $stdoutBytes $stderrBytes $nativeExit
  [Console]::WriteLine($line)
 }catch{
  # Preserve each independently completed bounded stream, even when its sibling fails.
  try{if($null -ne $outTask -and $outTask.IsCompletedSuccessfully){$stdoutBytes=$outTask.GetAwaiter().GetResult()}}catch{}
  try{if($null -ne $errTask -and $errTask.IsCompletedSuccessfully){$stderrBytes=$errTask.GetAwaiter().GetResult()}}catch{}
  try{
   if(-not $process.HasExited){$process.Kill($true);$null=$process.WaitForExit(5000)}
   if($process.HasExited){$nativeExit=$process.ExitCode}
  }catch{}
  # Root exit is not proof that descendants terminated; UNKNOWN remains mandatory.
  throw
 }finally{$process.Dispose()}
 exit $nativeExit
}catch{
 $status=if($launched){'UNAVAILABLE'}else{'BLOCKED_PRECONDITION'}
 $effect=if($launched){'UNKNOWN'}else{'NONE'}
 $terminal=@{schema='ts-ee/mat-xform-station-terminal/v1';attempt=$Attempt;status=$status;effect=$effect;reason=$_.Exception.Message;Product_effect='NONE'}
 if($launched){
  $terminal.native_exit=$nativeExit
  if($null -ne $stdoutBytes){$terminal.stdout_bytes=$stdoutBytes.Length;$terminal.stdout_sha256=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($stdoutBytes)).ToLowerInvariant()}
  if($null -ne $stderrBytes){$terminal.stderr_bytes=$stderrBytes.Length;$terminal.stderr_sha256=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($stderrBytes)).ToLowerInvariant()}
 }
 [Console]::WriteLine(($terminal|ConvertTo-Json -Compress))
 exit 1
}
