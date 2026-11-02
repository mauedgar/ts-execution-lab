# TS-BEADS 047B V5. Offline synthetic Dolt privilege persistence ONLY.
# A real SQL path exists, but an unprovisioned competent signer prevents effects.
[CmdletBinding(DefaultParameterSetName='Preflight')]
param(
  [Parameter(Mandatory,ParameterSetName='Preflight')][switch]$Preflight,
  [Parameter(Mandatory,ParameterSetName='Effect')][switch]$Effect,
  [Parameter(Mandatory,ParameterSetName='Effect')][string]$AuthorityDirectory,
  [Parameter(Mandatory,ParameterSetName='Effect')][string]$LauncherPath
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$script:Spawned=$false
$script:LocalMutation=$false
$script:Pid=$null
$script:ReceiptStream=$null
$script:ReceiptWriter=$null
$script:LastStage='NONE'
$script:StageInFlight=$false
$script:ConfirmedStages=0
$script:ChildExitConfirmed=$false
$script:LastExitCode=$null
$script:V5Module=Join-Path $PSScriptRoot 'Security-047B-V5.psm1'
$script:V5ModuleBlob='32eb389c771c42576238fc1e308fdb76f77f7207'
function State([string]$Kind,[string]$Reason) {
  [pscustomobject]@{operation='TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001';
    attempt='TS-BEADS-047B-DOLT-FIXTURE-V5-20261102-001';
    state=$Kind;reason=$Reason;spawned=$script:Spawned;lastStage=$script:LastStage;pid=$script:Pid;lastExitCode=$script:LastExitCode;confirmedStages=$script:ConfirmedStages}
}
function Record([string]$Event,[hashtable]$Fields) {
  if($null -eq $script:ReceiptWriter){throw 'RECEIPT_NOT_OPEN'}
  $obj=[ordered]@{event=$Event;utc=[datetimeoffset]::UtcNow.ToString('o');stage=$script:LastStage}
  foreach($key in $Fields.Keys){$obj[$key]=$Fields[$key]}
  $script:ReceiptWriter.WriteLine(($obj | ConvertTo-Json -Compress -Depth 6))
  $script:ReceiptWriter.Flush()
  $script:ReceiptStream.Flush($true)
}
function Install-BoundedIo {
  if('V5BoundedIo' -as [type]){return}
  Add-Type -TypeDefinition @'
using System;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;
public static class V5BoundedIo {
 public sealed class Result {
  public string Stdout {get;set;}
  public int StderrBytes {get;set;}
  public int ExitCode {get;set;}
 }
 static async Task<byte[]> ReadCap(Stream stream,int cap) {
  using(var ms=new MemoryStream()) {
   var buffer=new byte[2048];
   while(true){
    int n=await stream.ReadAsync(buffer,0,buffer.Length).ConfigureAwait(false);
    if(n==0)break;
    if(ms.Length+n>cap)throw new InvalidDataException("OUTPUT_LIMIT_EXCEEDED");
    ms.Write(buffer,0,n);
   }
   return ms.ToArray();
  }
 }
 static async Task WriteInput(Stream stream,byte[] bytes) {
  try {
   await stream.WriteAsync(bytes,0,bytes.Length).ConfigureAwait(false);
   await stream.FlushAsync().ConfigureAwait(false);
  } finally {
   Array.Clear(bytes,0,bytes.Length);
   stream.Close();
  }
 }
 public static Result Exchange(Process p,string sql,int maxOutput,int deadlineMs) {
  byte[] bytes=Encoding.UTF8.GetBytes(sql);
  Task<byte[]> stdout=ReadCap(p.StandardOutput.BaseStream,maxOutput);
  Task<byte[]> stderr=ReadCap(p.StandardError.BaseStream,maxOutput);
  Task write=WriteInput(p.StandardInput.BaseStream,bytes);
  Task exit=p.WaitForExitAsync();
  Task all=Task.WhenAll(new Task[]{stdout,stderr,write,exit});
  if(Task.WhenAny(all,Task.Delay(deadlineMs)).GetAwaiter().GetResult()!=all)
   throw new TimeoutException("PROCESS_UNKNOWN_TIMEOUT_NO_KILL_NO_RETRY");
  all.GetAwaiter().GetResult();
  var o=stdout.GetAwaiter().GetResult();
  var e=stderr.GetAwaiter().GetResult();
  return new Result {Stdout=Encoding.UTF8.GetString(o),StderrBytes=e.Length,ExitCode=p.ExitCode};
 }
}
'@ -ErrorAction Stop
}
function One-Row([string]$Json,[string]$Stage) {
  $parsed=ConvertFrom-Json -InputObject $Json.Trim() -AsHashtable -NoEnumerate -Depth 16
  if($parsed -is [hashtable] -and $parsed.ContainsKey('rows')) {
    if($parsed.rows -isnot [array]){throw ('READBACK_ROWS_NOT_ARRAY_'+$Stage)}
    $rows=@($parsed.rows)
  }
  elseif($parsed -is [array]){$rows=@($parsed)}
  else{throw ('READBACK_SCHEMA_'+$Stage)}
  if($rows.Count -ne 1 -or $rows[0] -isnot [hashtable]){throw ('READBACK_COUNT_'+$Stage)}
  return $rows[0]
}
function Invoke-SqlStage([string]$Exe,[string]$Data,[string]$Cfg,[string]$Privilege,[string]$Sql,[string]$Stage) {
  $script:LastStage=$Stage
  $script:StageInFlight=$false
  $script:ChildExitConfirmed=$false
  $script:LastExitCode=$null
  Assert-V5NoReparse $Data
  Assert-V5NoReparse $Cfg
  Assert-V5PrivateAcl $Data
  Assert-V5PrivateAcl $Cfg
  Assert-V5NoNetworkExposure
  if(Test-Path -LiteralPath $Privilege){
    Assert-V5NoReparse $Privilege
    Assert-V5PrivateAcl $Privilege $true
  }
  Record 'SPAWN_INTENT' @{binarySha256=(Get-FileHash -LiteralPath $Exe -Algorithm SHA256).Hash}
  $script:StageInFlight=$true
  $psi=[Diagnostics.ProcessStartInfo]::new()
  $psi.FileName=$Exe
  $psi.WorkingDirectory=$Data
  $psi.UseShellExecute=$false
  $psi.CreateNoWindow=$true
  $psi.RedirectStandardInput=$true
  $psi.RedirectStandardOutput=$true
  $psi.RedirectStandardError=$true
  foreach($a in @("--data-dir=$Data","--doltcfg-dir=$Cfg","--privilege-file=$Privilege",
    'sql','--result-format','json')){[void]$psi.ArgumentList.Add($a)}
  $p=[Diagnostics.Process]::new()
  $p.StartInfo=$psi
  try {
    Assert-V5 ($p.Start()) 'PROCESS_START_FAILED'
    $script:Spawned=$true
    $script:Pid=$p.Id
    # Any failure before this record is UNKNOWN; original SPAWN_INTENT survives.
    Record 'CHILD_STARTED' @{pid=$p.Id;startUtc=$p.StartTime.ToUniversalTime().ToString('o')}
    $result=[V5BoundedIo]::Exchange($p,$Sql,16384,15000)
    Record 'CHILD_EXIT' @{pid=$p.Id;exitCode=$result.ExitCode}
    $script:ChildExitConfirmed=$true
    $script:LastExitCode=$result.ExitCode
    $script:StageInFlight=$false
    $script:ConfirmedStages++
    Assert-V5 ($result.ExitCode -eq 0) ('SQL_EXIT_NONZERO_'+$Stage)
    return $result.Stdout
  } catch {
    if(-not $script:ChildExitConfirmed){
      try { Record 'CHILD_AMBIGUOUS' @{pid=$script:Pid;lastExitKnown=$false} } catch {}
    }
    throw
  } finally {
    # Dispose does NOT call Kill(). An unobserved effect remains UNKNOWN.
    $p.Dispose()
  }
}
function Invoke-AuthorizedFixture([string]$AuthorityDirectory,[string]$LauncherPath) {
  Assert-V5 ($env:COMPUTERNAME -ceq 'DESKTOP-DJLBEQH') 'WRONG_HOST'
  Assert-V5 ($PSVersionTable.PSEdition -ceq 'Core') 'PWSH_CORE_REQUIRED'
  $paths=Get-V5Root
  Assert-V5NoReparse $paths.Base
  Assert-V5NoReparse $paths.Parent
  Assert-V5 (-not (Test-Path -LiteralPath $paths.Root)) 'ORIGINAL_ROOT_PRESENT'
  Assert-V5 (-not (Test-Path -LiteralPath $paths.Receipt)) 'ORIGINAL_RECEIPT_PRESENT'
  # Grant is verified by the runner itself, not merely by the launcher.
  $attested=Assert-V5Authority $AuthorityDirectory $PSCommandPath $LauncherPath
  Assert-V5NoNetworkExposure
  $exe=$attested.Grant.doltExePath
  Assert-V5 ([IO.File]::Exists($exe)) 'DOLT_EXE_MISSING'
  Assert-V5NoReparse $exe
  Assert-V5 ((Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash -ceq 'BED880C0E6B522498A563FCD1F0FC1E25527BA07E66C1E0A85C2242B64DFD967') 'DOLT_HASH_MISMATCH'
  # No root or receipt is created until after the trusted grant + reconciliation.
  if(-not (Test-Path -LiteralPath $paths.Parent)){
    New-V5AtomicPrivateDirectory $paths.Parent
    $script:LocalMutation=$true
  } else {Assert-V5PrivateAcl $paths.Parent}
  Assert-V5NoReparse $paths.Parent
  $script:LocalMutation=$true  # conservative if atomic creation fails after mutation
  $script:ReceiptStream=New-V5AtomicPrivateFile $paths.Receipt
  $script:LocalMutation=$true
  $script:ReceiptWriter=[IO.StreamWriter]::new($script:ReceiptStream,[Text.UTF8Encoding]::new($false),1024,$true)
  try {
    Assert-V5PrivateAcl $paths.Receipt
    Record 'CLAIM_LOCAL' @{sourceCommit=$attested.Grant.sourceCommit;
      claimGitCommit=$attested.Reconciliation.claimGitCommit;claimBlob=$attested.Reconciliation.claimBlob}
    New-V5AtomicPrivateDirectory $paths.Root
    $data=Join-Path $paths.Root 'data'
    $cfg=Join-Path $paths.Root 'cfg'
    New-V5AtomicPrivateDirectory $data
    New-V5AtomicPrivateDirectory $cfg
    $priv=Join-Path $cfg 'privileges.db'
    Assert-V5 (-not (Test-Path -LiteralPath $priv)) 'PRIVILEGE_FILE_PREEXISTS'
    Install-BoundedIo
    # Synthetic secret exists only in process memory/stdin; never in argv or receipt.
    $secretBytes=[Security.Cryptography.RandomNumberGenerator]::GetBytes(32)
    try {
      $password=[Convert]::ToHexString($secretBytes)
      [void](Invoke-SqlStage $exe $data $cfg $priv 'CREATE DATABASE ts047b_fixture;' 'CREATE_DATABASE')
      [void](Invoke-SqlStage $exe $data $cfg $priv ("CREATE USER 'ts047b_reader'@'localhost' IDENTIFIED BY '"+$password+"';") 'CREATE_USER')
      [void](Invoke-SqlStage $exe $data $cfg $priv "GRANT SELECT ON ts047b_fixture.* TO 'ts047b_reader'@'localhost';" 'GRANT_SELECT')
      Assert-V5 ([IO.File]::Exists($priv)) 'PRIVILEGE_FILE_ABSENT'
      Assert-V5PrivateAcl $priv $true
      $hash1=(Get-FileHash -LiteralPath $priv -Algorithm SHA256).Hash
      Record 'PRIVILEGE_PERSISTED' @{sha256=$hash1}
      # Separate native CLI processes; both account and database grant required.
      $u=Invoke-SqlStage $exe $data $cfg $priv "SELECT User,Host FROM mysql.user WHERE User='ts047b_reader' AND Host='localhost';" 'REOPEN_USER'
      $d=Invoke-SqlStage $exe $data $cfg $priv "SELECT User,Host,Db,Select_priv,Insert_priv,Update_priv,Delete_priv FROM mysql.db WHERE User='ts047b_reader' AND Host='localhost' AND Db='ts047b_fixture';" 'REOPEN_DB_GRANT'
      $user=One-Row $u 'REOPEN_USER'
      $grant=One-Row $d 'REOPEN_DB_GRANT'
      Assert-V5 ($user.User -ceq 'ts047b_reader' -and $user.Host -ceq 'localhost') 'ACCOUNT_MISMATCH'
      Assert-V5 ($grant.User -ceq 'ts047b_reader' -and $grant.Host -ceq 'localhost' -and $grant.Db -ceq 'ts047b_fixture') 'GRANT_IDENTITY_MISMATCH'
      Assert-V5 ($grant.Select_priv -ceq 'Y' -and $grant.Insert_priv -ceq 'N' -and $grant.Update_priv -ceq 'N' -and $grant.Delete_priv -ceq 'N') 'GRANT_RIGHTS_MISMATCH'
      $hash2=(Get-FileHash -LiteralPath $priv -Algorithm SHA256).Hash
      Assert-V5 ($hash1 -ceq $hash2) 'PRIVILEGE_HASH_CHANGED'
      Record 'PASS_OFFLINE_PERSISTENCE_ONLY' @{sha256=$hash2;note='NOT_REMOTE_AUTH_NOT_HOST_INDEPENDENCE'}
      return (State 'PASS_OFFLINE_PERSISTENCE_ONLY' 'PERSISTENCE_OBSERVED_ONLY')
    } finally {
      [Array]::Clear($secretBytes,0,$secretBytes.Length)
      $password=$null
    }
  } finally {
    if($null -ne $script:ReceiptWriter){$script:ReceiptWriter.Dispose()}
    if($null -ne $script:ReceiptStream){$script:ReceiptStream.Dispose()}
  }
}
try {
  if(-not [IO.File]::Exists($script:V5Module)){throw 'SECURITY_MODULE_MISSING'}
  $sourceBytes=[IO.File]::ReadAllBytes($script:V5Module)
  $prefix=[Text.Encoding]::ASCII.GetBytes(('blob '+$sourceBytes.Length+[char]0))
  $payload=[byte[]]::new($prefix.Length+$sourceBytes.Length)
  [Array]::Copy($prefix,0,$payload,0,$prefix.Length)
  [Array]::Copy($sourceBytes,0,$payload,$prefix.Length,$sourceBytes.Length)
  $blob=[Convert]::ToHexString([Security.Cryptography.SHA1]::HashData($payload)).ToLowerInvariant()
  if($blob -cne $script:V5ModuleBlob){throw 'SECURITY_MODULE_BLOB_MISMATCH'}
  Import-Module -Name $script:V5Module -Force -ErrorAction Stop
  if($Preflight){
    $paths=Get-V5Root
    Assert-V5NoReparse $paths.Base
    Assert-V5 (-not (Test-Path -LiteralPath $paths.Root)) 'PRIOR_ROOT'
    Assert-V5 (-not (Test-Path -LiteralPath $paths.Receipt)) 'PRIOR_RECEIPT'
    Assert-V5NoNetworkExposure
    State 'BLOCKED_PRECONDITION' 'SIGNED_COMPETENT_GRANT_UNPROVISIONED_NO_SQL'
  } else {
    Invoke-AuthorizedFixture $AuthorityDirectory $LauncherPath
  }
} catch {
  if($script:StageInFlight){State 'UNKNOWN_EFFECT' 'PRESERVE_ORIGINAL_PID_AND_RECEIPT_NO_RETRY'}
  elseif($script:Spawned){State 'FAILED_OR_PARTIAL_SQL_EFFECT' 'EXACT_STAGE_AND_ORIGINAL_RECEIPT_RECONCILIATION_REQUIRED'}
  elseif($script:LocalMutation){State 'PARTIAL_NO_SQL' 'PRESERVE_LOCAL_RECEIPT_AND_ROOT'}
  else{State 'BLOCKED_PRECONDITION' 'NO_SQL_EFFECT'}
}
