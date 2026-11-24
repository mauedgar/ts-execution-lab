[CmdletBinding()]
param([Parameter(Mandatory)][string]$Root,[Parameter(Mandatory)][string]$Attempt,
 [Parameter(Mandatory)][string]$GrantSha256,[Parameter(Mandatory)][string]$Node,
 [Parameter(Mandatory)][string]$NodeSha256,[Parameter(Mandatory)][string]$GuardSha256)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$launched=$false
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
try{
 if(-not $IsWindows -or $Attempt -cnotmatch '^[A-Za-z0-9_-]{1,96}$' -or $Root -cnotmatch '^[A-Za-z]:\\' -or [IO.Path]::GetFullPath($Root) -cne $Root){throw 'ARGUMENTS'}
 foreach($h in @($GrantSha256,$NodeSha256,$GuardSha256)){if($h -cnotmatch '^[a-f0-9]{64}$'){throw 'HASH_ARGUMENT'}}
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
 if(([IO.FileInfo]::new($grant)).Length -gt 32768 -or (Hash $grant) -cne $GrantSha256){throw 'GRANT_HASH_OR_SIZE'}
 $g=Get-Content -LiteralPath $grant -Raw -Encoding UTF8 | ConvertFrom-Json -AsHashtable
 if($g.root_acl_sha256 -cne $aclHash -or $g.node_sha256 -cne $NodeSha256 -or $g.station_root -cne $Root -or $g.attempt -cne $Attempt){throw 'GRANT_BINDING'}
 Assert-Tree (Join-Path $Root 'install')
 Assert-Path $guard $false
 if((Hash $guard) -cne $GuardSha256){throw 'GUARD_HASH'}
 Assert-Path $Node $false;if((Hash $Node) -cne $NodeSha256){throw 'NODE_HASH'}
 # No caller NODE_OPTIONS, NODE_PATH or arbitrary child environment.
 $psi=[Diagnostics.ProcessStartInfo]::new();$psi.FileName=$Node;$psi.UseShellExecute=$false
 $psi.WorkingDirectory=Join-Path $Root 'install';$psi.Environment.Clear()
 $psi.Environment['SystemRoot']=$env:SystemRoot;$psi.Environment['WINDIR']=$env:WINDIR
 foreach($arg in @($guard,$Root,$Attempt,$GrantSha256)){$psi.ArgumentList.Add($arg)}
 $process=[Diagnostics.Process]::new();$process.StartInfo=$psi
 $launched=$true
 try{if(-not $process.Start()){throw 'START_FAILED'}
  if(-not $process.WaitForExit(180000)){try{$process.Kill($true)}catch{};throw 'GUARD_DEADLINE'}
  $code=$process.ExitCode
 }finally{$process.Dispose()}
 exit $code
}catch{
 $status=if($launched){'UNAVAILABLE'}else{'BLOCKED_PRECONDITION'}
 $effect=if($launched){'UNKNOWN'}else{'NONE'}
 [Console]::WriteLine((@{schema='ts-ee/mat-xform-station-terminal/v1';attempt=$Attempt;status=$status;effect=$effect;reason=$_.Exception.Message;Product_effect='NONE'}|ConvertTo-Json -Compress))
 exit 1
}
