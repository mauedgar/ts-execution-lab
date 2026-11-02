<#
IR005 repaired offline-proof runner. This build is observation and mock-test
only. -Effect is intentionally fail-closed: no native 2.2.0 grammar/readback
qualification exists in this candidate, therefore it never creates a root,
receipt, account, database, or privilege.
#>
[CmdletBinding(DefaultParameterSetName='Preflight')]
param(
  [Parameter(ParameterSetName='Preflight', Mandatory)][switch]$Preflight,
  [Parameter(ParameterSetName='Effect', Mandatory)][switch]$Effect,
  [Parameter(ParameterSetName='Effect', Mandatory)][string]$ExecutionAttempt,
  [Parameter(ParameterSetName='Effect', Mandatory)][string]$GrantFile,
  [hashtable]$Provider
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$script:Attempt='TS-BEADS-047B-OFFLINE-PROOF-IR005-REPAIR-20261101-002'
$script:ExpectedDoltHash='BED880C0E6B522498A563FCD1F0FC1E25527BA07E66C1E0A85C2242B64DFD967'

function New-Result([string]$Status,[string]$Label,[string]$Detail='') { [pscustomobject]@{Status=$Status;Label=$Label;Detail=$Detail} }
function Get-CanonicalRoot([string]$Attempt) {
  if([string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)){throw 'LOCALAPPDATA_UNAVAILABLE'}
  [IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA ("TS047B-OfflineProof-"+$Attempt)))
}
function Test-ReparseAncestors([string]$Path) {
  $current=[IO.Path]::GetFullPath($Path)
  while($true) { if(Test-Path -LiteralPath $current) { if((Get-Item -Force -LiteralPath $current).Attributes -band [IO.FileAttributes]::ReparsePoint){return $true} }; $parent=[IO.Directory]::GetParent($current); if($null -eq $parent){return $false}; $current=$parent.FullName }
}
function Test-RestrictedAcl([string]$Path,[string]$ExpectedOwner) {
  try {
    $acl=Get-Acl -LiteralPath $Path
    if($acl.Owner -ne $ExpectedOwner){return $false}
    $broad='BUILTIN\Users','NT AUTHORITY\Authenticated Users','Everyone'
    foreach($rule in $acl.Access){if($broad -contains $rule.IdentityReference.Value -and $rule.AccessControlType -eq 'Allow' -and (($rule.FileSystemRights -band [Security.AccessControl.FileSystemRights]::Write) -ne 0)){return $false}}
    $true
  } catch {$false}
}
function Get-CommandOutput([string]$File,[string[]]$Arguments,[string]$Input='') {
  # Start all redirected streams before waiting. On timeout the live PID is returned;
  # callers must preserve state and must not kill, retry, or clean it up automatically.
  $p=[Diagnostics.Process]::new();$p.StartInfo=[Diagnostics.ProcessStartInfo]::new();$p.StartInfo.FileName=$File;$p.StartInfo.UseShellExecute=$false;$p.StartInfo.RedirectStandardInput=$true;$p.StartInfo.RedirectStandardOutput=$true;$p.StartInfo.RedirectStandardError=$true
  foreach($a in $Arguments){[void]$p.StartInfo.ArgumentList.Add($a)}
  if(-not $p.Start()){throw 'PROCESS_START_FAILED'}
  $pid=$p.Id;$outTask=$p.StandardOutput.ReadToEndAsync();$errTask=$p.StandardError.ReadToEndAsync();$inTask=$p.StandardInput.WriteAsync($Input);$p.StandardInput.Close()
  if(-not $p.WaitForExit(10000)){return [pscustomobject]@{TimedOut=$true;Pid=$pid;Output='';Error='';State='UNKNOWN_OR_PARTIAL'}}
  $inTask.GetAwaiter().GetResult();[pscustomobject]@{TimedOut=$false;Pid=$pid;Output=$outTask.GetAwaiter().GetResult();Error=$errTask.GetAwaiter().GetResult();State='EXITED'}
}
function New-NativeProvider {
  @{
    Observe={ param($Root)
      $reasons=[Collections.Generic.List[string]]::new();$owner=[Security.Principal.WindowsIdentity]::GetCurrent().Name
      $dolt=Join-Path ${env:ProgramFiles} 'Dolt\dolt.exe';$hash='';$version='';$listener=$null;$serve=$null;$prior=$null
      if(-not (Test-Path -LiteralPath $dolt -PathType Leaf)){$reasons.Add('DOLT_BINARY_ABSENT')}else{
        try {$hash=(Get-FileHash -LiteralPath $dolt -Algorithm SHA256).Hash.ToUpperInvariant();$v=Get-CommandOutput $dolt @('--version');if($v.TimedOut){$reasons.Add('DOLT_VERSION_TIMEOUT')}else{$version=($v.Output+$v.Error).Trim()}}catch{$reasons.Add('DOLT_BINARY_UNREADABLE')}
      }
      try {$listener=@(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object {$_.OwningProcess -in @(Get-Process -Name dolt -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)}).Count -gt 0}catch{$reasons.Add('LISTENER_OBSERVATION_UNAVAILABLE')}
      $tailscale=Get-Command tailscale.exe -ErrorAction SilentlyContinue
      if($null -eq $tailscale){$serve=$false}else{try{$t=Get-CommandOutput $tailscale.Source @('serve','status','--json');if($t.TimedOut){$reasons.Add('TAILSCALE_OBSERVATION_TIMEOUT')}else{$serve=($t.Output -match '"(Serve|Funnel)"\s*:\s*true')}}catch{$reasons.Add('TAILSCALE_OBSERVATION_UNAVAILABLE')}}
      $receiptArea=Join-Path $env:LOCALAPPDATA 'TS047B-OfflineProof-Receipts'
      try {if(-not (Test-Path -LiteralPath $receiptArea -PathType Container)){throw 'absent'};if(-not (Test-RestrictedAcl $receiptArea $owner)){throw 'unsafe'};$prior=@(Get-ChildItem -LiteralPath $receiptArea -File -ErrorAction Stop | Where-Object {$_.Name -match 'TS-BEADS-047B'}).Count -gt 0}catch{$reasons.Add('RECEIPT_AREA_UNAVAILABLE')}
      [pscustomobject]@{Complete=($reasons.Count -eq 0);Reasons=@($reasons);Host=$env:COMPUTERNAME;Owner=$owner;DoltPath=$dolt;DoltHash=$hash;DoltVersion=$version;Root=$Root;RootExists=(Test-Path -LiteralPath $Root);RootReparse=(Test-ReparseAncestors $Root);RootAclSafe=($null -ne [IO.Directory]::GetParent($Root) -and (Test-RestrictedAcl ([IO.Directory]::GetParent($Root).FullName) $owner));PrivilegeExists=(Test-Path -LiteralPath (Join-Path $Root 'privileges.db'));SqlListener=$listener;ServeActive=$serve;PriorReceipt=$prior;PriorUnknown=($null -eq $prior)}
    }
    ReadGrant={param($Path)throw 'External immutable-control verification is not implemented in this offline build'}
    RunBounded={param($File,$Arguments,$Input) Get-CommandOutput $File $Arguments $Input}
  }
}
function Get-Precheck([hashtable]$P,[string]$Attempt) {
  try {$root=Get-CanonicalRoot $Attempt;$o=& $P.Observe $root}catch{return New-Result BLOCKED_INCOMPLETE_PROVIDER_OBSERVATION PROVIDER_EXCEPTION $_.Exception.Message}
  if(-not $o.Complete){return New-Result BLOCKED_INCOMPLETE_PROVIDER_OBSERVATION INCOMPLETE_PROVIDER_OBSERVATION ($o.Reasons -join ',')}
  if([string]::IsNullOrWhiteSpace($o.Host) -or [string]::IsNullOrWhiteSpace($o.Owner)){return New-Result BLOCKED_INCOMPLETE_PROVIDER_OBSERVATION HOST_OWNER_UNKNOWN}
  if($o.DoltHash -ne $script:ExpectedDoltHash -or $o.DoltVersion -notmatch '(?<![0-9])2\.2\.0(?![0-9])'){return New-Result BLOCKED WRONG_BINARY_HASH}
  if($o.RootExists){return New-Result BLOCKED ROOT_EXISTS};if($o.RootReparse){return New-Result BLOCKED ROOT_JUNCTION};if(-not $o.RootAclSafe){return New-Result BLOCKED ROOT_ACL};if($o.PrivilegeExists){return New-Result BLOCKED PRIVILEGE_FILE_EXISTS}
  if($o.SqlListener -or $o.ServeActive){return New-Result BLOCKED ACTIVE_LISTENER_SERVE};if($o.PriorReceipt -or $o.PriorUnknown){return New-Result BLOCKED PRIOR_UNKNOWN}
  New-Result REVIEW_REQUIRED PRECHECK_OBSERVED
}
function Invoke-OfflineDoltPrivilegeProof([hashtable]$Provider) {
  $p=if($Provider){$Provider}else{New-NativeProvider};$attempt=if($Preflight){$script:Attempt}else{$ExecutionAttempt};$pre=Get-Precheck $p $attempt
  if($pre.Status -ne 'REVIEW_REQUIRED'){return $pre};if($Preflight){return $pre}
  # No arbitrary JSON is accepted: a verified external Git blob, issuer, one-time receipt and exclusive lock are required but absent here.
  return New-Result BLOCKED_PINNED_CAPABILITY_UNVERIFIED PINNED_SQL_GRAMMAR_UNQUALIFIED 'No root or subprocess was created.'
}
Invoke-OfflineDoltPrivilegeProof -Provider $Provider
