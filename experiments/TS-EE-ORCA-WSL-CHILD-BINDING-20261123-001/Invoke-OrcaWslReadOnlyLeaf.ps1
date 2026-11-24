# TS EE 004 NONPRODUCT Windows to WSL child exit source candidate.
# Native mode requires a distinct exact host grant, immutable source and caller hash.
[CmdletBinding()]
param(
    [ValidateSet('SelfTest','Native')][string]$Mode = 'SelfTest',
    [string]$ExpectedRunnerSha256 = '',
    [string]$ExpectedOrcaRuntimeId = '',
    [string]$ExpectedOrcaHandle = '',
    [string]$ExpectedOrcaIncarnationId = '',
    [string]$ExpectedOrcaHostId = ''
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$RequestId = 'TS-EE-004-ORCA-WSL-E3-BOUNDED-LEAF-20261123-001'
$AttemptId = 'TS-EE-004-ORCA-WSL-E3-BOUNDED-LEAF-20261123-001-A001'
$Marker = 'TS_EE004_CHILD_JSON='
$MarkerSchema = 'ts-ee/wsl-child-marker/v0.2'
$MaxStdoutBytes = 4096
$MaxStderrBytes = 2048
$ExpectedLinuxExit = 7
$ExpectedUid = 1000
$WorkRoot = 'C:\TS\station'
$OutputDir = 'C:\TS\station\ts-ee004-wsl-leaf-e3-20261123-001'


# Windows-only atomic create-only namespace reservation and bounded async reads.
# This does not protect against a hostile administrator racing parent rename.
Add-Type -TypeDefinition @'
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Threading;
using System.Threading.Tasks;
public static class TSEEBounded {
 [DllImport("kernel32.dll",EntryPoint="CreateDirectoryW",CharSet=CharSet.Unicode,SetLastError=true)]
 [return: MarshalAs(UnmanagedType.Bool)]
 public static extern bool ReserveDirectory(string path,IntPtr security);
 public static async Task<byte[]> Capture(Stream stream,int limit,CancellationToken token) {
  using (var output=new MemoryStream()) {
   byte[] buffer=new byte[2048];
   while(true) {
    int n=await stream.ReadAsync(buffer.AsMemory(0,buffer.Length),token).ConfigureAwait(false);
    if(n==0) break;
    if(output.Length+n>limit) throw new InvalidDataException("OUTPUT_BYTE_LIMIT_EXCEEDED");
    output.Write(buffer,0,n);
   }
   return output.ToArray();
  }
 }
}
'@

function Assert-ChildOutput {
 param([string]$Stdout,[int]$ExitCode)
 if($ExitCode -ne $ExpectedLinuxExit) {throw 'WSL_EXIT_MISMATCH'}
 $lines=@($Stdout -split '\r?\n' | Where-Object {$_ -ne ''})
 if($lines.Count -ne 1 -or -not $lines[0].StartsWith($Marker)) {throw 'CHILD_MARKER_COUNT_INVALID'}
 $child=ConvertFrom-Json -InputObject $lines[0].Substring($Marker.Length) -AsHashtable -ErrorAction Stop
 if($null -eq $child -or $child.Count -ne 8) {throw 'CHILD_MARKER_SHAPE_INVALID'}
 foreach($key in @('schema','request_id','attempt','pid','ppid','uid','pid_namespace','intended_exit')) {
   if(-not $child.ContainsKey($key)) {throw 'CHILD_MARKER_SHAPE_INVALID'}
 }
 if($child.schema -ne $MarkerSchema -or $child.request_id -ne $RequestId -or
    $child.attempt -ne $AttemptId) {throw 'CHILD_IDENTITY_MISMATCH'}
 if([int]$child.uid -ne $ExpectedUid) {throw 'CHILD_UID_MISMATCH'}
 if([int]$child.pid -le 1 -or [int]$child.ppid -lt 1) {throw 'CHILD_PID_INVALID'}
 if([string]$child.pid_namespace -notmatch '^pid:\[[0-9]+\]$') {throw 'CHILD_NAMESPACE_INVALID'}
 if([int]$child.intended_exit -ne $ExpectedLinuxExit) {throw 'CHILD_INTENDED_EXIT_MISMATCH'}
 return $child
}
function Write-ExclusiveUtf8 {
 param([string]$Path,[string]$Text)
 $bytes=[System.Text.UTF8Encoding]::new($false).GetBytes($Text)
 $stream=[IO.FileStream]::new($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
 try {$stream.Write($bytes,0,$bytes.Length);$stream.Flush($true)} finally {$stream.Dispose()}
}
function Read-QualifiedResult {
 param([string]$Directory)
 if([IO.File]::Exists((Join-Path $Directory 'INCOMPLETE.txt'))) {throw 'INCOMPLETE_MARKER_DOMINATES'}
 if([IO.File]::Exists((Join-Path $Directory 'RESULT.tmp'))) {throw 'PARTIAL_STAGING_PRESENT'}
 $path=Join-Path $Directory 'RESULT.json'
 if(-not [IO.File]::Exists($path)) {throw 'MISSING_TERMINAL_RECEIPT'}
 $r=ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($path,[Text.UTF8Encoding]::new($false,$true))) -AsHashtable -ErrorAction Stop
 if($r.schema -ne 'ts-ee/wsl-child-relay/v0.2' -or $r.effect_state -ne 'CONFIRMED_BOUNDED' -or
    $r.Product_effect -ne 'NONE' -or [int]$r.windows_wsl_exit -ne $ExpectedLinuxExit) {throw 'TERMINAL_RECEIPT_INVALID'}
 return $r
}
function Assert-Negative {
 param([scriptblock]$Action,[string]$Case)
 $denied=$false
 try {$null=& $Action} catch {$denied=$true}
 if(-not $denied) {throw ("NEGATIVE_NOT_DENIED_"+$Case)}
}


if ($Mode -eq 'SelfTest') {
 $good=@{schema=$MarkerSchema;request_id=$RequestId;attempt=$AttemptId;
         pid=101;ppid=1;uid=1000;pid_namespace='pid:[4026532211]';intended_exit=7}
 $text=$Marker+(ConvertTo-Json $good -Compress)
 if((Assert-ChildOutput -Stdout $text -ExitCode 7).pid -ne 101) {throw 'POSITIVE_CASE_FAILED'}
 $cases=@('exit','request','attempt','schema','uid','duplicate','namespace','pid','ppid','intended','missing','extra','json','extra_key')
 foreach($c in $cases) {
  $copy=$good.Clone();$str=$text;$code=7
  switch($c) {
   'exit' {$code=0}
   'request' {$copy.request_id='BAD'}
   'attempt' {$copy.attempt='BAD'}
   'schema' {$copy.schema='BAD'}
   'uid' {$copy.uid=0}
   'duplicate' {$str=$text+[Environment]::NewLine+$text}
   'namespace' {$copy.pid_namespace='BAD'}
   'pid' {$copy.pid=0}
   'ppid' {$copy.ppid=0}
   'intended' {$copy.intended_exit=0}
   'missing' {$str=''}
   'extra' {$str=$text+[Environment]::NewLine+'UNEXPECTED'}
   'json' {$str=$Marker+'{'}
   'extra_key' {$copy.other='UNTRUSTED'}
  }
  if($c -in @('request','attempt','schema','uid','namespace','pid','ppid','intended','extra_key')) {
   $str=$Marker+(ConvertTo-Json $copy -Compress)
  }
  Assert-Negative -Case $c -Action {Assert-ChildOutput -Stdout $str -ExitCode $code}
 }
 $oversize=[Text.UTF8Encoding]::new($false).GetBytes('X'*17)
 $read=[TSEEBounded]::Capture([IO.MemoryStream]::new($oversize),16,[Threading.CancellationToken]::None)
 Assert-Negative -Case 'byte_limit' -Action {$null=$read.GetAwaiter().GetResult()}
 $temp=Join-Path ([IO.Path]::GetTempPath()) ('ts-ee-self-'+[guid]::NewGuid().ToString('N'))
 [IO.Directory]::CreateDirectory($temp)|Out-Null
 try {
  $reserved=Join-Path $temp 'reservation'
  if(-not [TSEEBounded]::ReserveDirectory($reserved,[IntPtr]::Zero)) {throw 'ATOMIC_RESERVE_SELFTEST_FAILED'}
  if([TSEEBounded]::ReserveDirectory($reserved,[IntPtr]::Zero)) {throw 'ATOMIC_COLLISION_NOT_BLOCKED'}
  Assert-Negative -Case 'no_receipt' -Action {Read-QualifiedResult -Directory $temp}
  Write-ExclusiveUtf8 -Path (Join-Path $temp 'INCOMPLETE.txt') -Text 'UNTRUSTED'
  Assert-Negative -Case 'marker' -Action {Read-QualifiedResult -Directory $temp}
  Write-ExclusiveUtf8 -Path (Join-Path $temp 'RESULT.json') -Text '{"spoofed":true}'
  Assert-Negative -Case 'marker_dominates_result' -Action {Read-QualifiedResult -Directory $temp}
  Assert-Negative -Case 'leaf_collision' -Action {Write-ExclusiveUtf8 -Path (Join-Path $temp 'RESULT.json') -Text 'REPLACE'}
 } finally {[IO.Directory]::Delete($temp,$true)}
 Write-Output '{"source_only":"PASS_14_MARKER_NEGATIVES_IO_ATOMIC_AND_BYTE_LIMIT","Native_WSL":"NOT_RUN","Orca":"NOT_RUN","Product_effect":"NONE"}'
 exit 0
}


# Native mode is a separately grant-bound NEW attempt, NEVER a PR77 rerun.
if($PSVersionTable.PSVersion.Major -lt 7 -or -not $IsWindows) {throw 'PWSH7_WINDOWS_REQUIRED'}
if($env:COMPUTERNAME -ne 'DESKTOP-DJLBEQH') {throw 'WRONG_HOST'}
if($ExpectedRunnerSha256 -notmatch '^[a-fA-F0-9]{64}$') {throw 'MISSING_CALLER_HASH'}
$actual=(Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant()
if($actual -ne $ExpectedRunnerSha256.ToLowerInvariant()) {throw 'SOURCE_HASH_MISMATCH'}
if($ExpectedOrcaRuntimeId -notmatch '^[a-f0-9-]{36}$' -or
   $ExpectedOrcaHandle -notmatch '^term_[a-f0-9-]{36}$' -or
   $ExpectedOrcaIncarnationId -notmatch '^[a-f0-9-]{36}$' -or
   $ExpectedOrcaHostId -ne 'local') {throw 'EXTERNAL_ORCA_BINDING_REQUIRED'}
if(-not [IO.Directory]::Exists($WorkRoot)) {throw 'MISSING_WORKROOT'}
foreach($ancestor in @('C:\TS',$WorkRoot)) {
 if(([IO.File]::GetAttributes($ancestor) -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
  throw 'UNSAFE_ANCESTOR_REPARSE'
 }
}
$wsl=Join-Path $env:WINDIR 'System32\wsl.exe'
if(-not [IO.File]::Exists($wsl)) {throw 'WSL_BINARY_MISSING'}
if((Get-AuthenticodeSignature -LiteralPath $wsl).Status.ToString() -ne 'Valid') {throw 'WSL_BINARY_SIGNATURE_UNVERIFIED'}
$linux=@'
import json,os,sys,time
p=os.getpid()
v={"schema":"ts-ee/wsl-child-marker/v0.2",
   "request_id":"TS-EE-004-ORCA-WSL-E3-BOUNDED-LEAF-20261123-001",
   "attempt":"TS-EE-004-ORCA-WSL-E3-BOUNDED-LEAF-20261123-001-A001",
   "pid":p,"ppid":os.getppid(),"uid":os.getuid(),
   "pid_namespace":os.readlink("/proc/%d/ns/pid"%p),"intended_exit":7}
print("TS_EE004_CHILD_JSON="+json.dumps(v,sort_keys=True,separators=(',',':')),flush=True)
time.sleep(2)
sys.exit(7)
'@
$owned=$false;$started=$false;$settled=$false;$process=$null;$cts=$null
$cim='NOT_ATTESTED';$cimParent=0
try {
 # Atomic Win32 fail-on-existing reservation; a checked Directory.CreateDirectory
 # would silently reuse an occupied path. Exclusive leaf writes also fail closed.
 if(-not [TSEEBounded]::ReserveDirectory($OutputDir,[IntPtr]::Zero)) {
  throw ('ATOMIC_OUTPUT_COLLISION_'+[Runtime.InteropServices.Marshal]::GetLastWin32Error())
 }
 $owned=$true
 if(([IO.File]::GetAttributes($OutputDir) -band [IO.FileAttributes]::ReparsePoint) -ne 0) {throw 'UNSAFE_OUTPUT_REPARSE'}
 Write-ExclusiveUtf8 -Path (Join-Path $OutputDir 'INCOMPLETE.txt') -Text 'UNTRUSTED_UNSETTLED'
 $psi=[Diagnostics.ProcessStartInfo]::new()
 $psi.FileName=$wsl
 foreach($arg in @('-d','Ubuntu-24.04','--exec','/usr/bin/python3','-I','-c',$linux)) {[void]$psi.ArgumentList.Add($arg)}
 $psi.UseShellExecute=$false;$psi.RedirectStandardOutput=$true;$psi.RedirectStandardError=$true
 $process=[Diagnostics.Process]::new();$process.StartInfo=$psi
 if(-not $process.Start()) {throw 'WSL_START_FAILED'}
 $started=$true;$wslPid=$process.Id
 $cts=[Threading.CancellationTokenSource]::new([TimeSpan]::FromSeconds(16))
 $outTask=[TSEEBounded]::Capture($process.StandardOutput.BaseStream,$MaxStdoutBytes,$cts.Token)
 $errTask=[TSEEBounded]::Capture($process.StandardError.BaseStream,$MaxStderrBytes,$cts.Token)
 $exitTask=$process.WaitForExitAsync($cts.Token)
 try {
  $win=Get-CimInstance Win32_Process -Filter ('ProcessId = '+$wslPid) -ErrorAction Stop
  if($null -ne $win) {
   $cimParent=[int]$win.ParentProcessId
   if($win.Name -ne 'wsl.exe' -or $cimParent -ne $PID) {throw 'WIN_PARENT_MISMATCH'}
   $cim='SAMPLED_BOUNDED_ONLY'
  }
 } catch {
  if($_.Exception.Message -eq 'WIN_PARENT_MISMATCH') {throw}
  $cim='NOT_ATTESTED_CIM_RACE_OR_PROVIDER'
 }
 [Threading.Tasks.Task]::WhenAll([Threading.Tasks.Task[]]@($outTask,$errTask,$exitTask)).GetAwaiter().GetResult()
 $settled=$true
 $stdout=[Text.UTF8Encoding]::new($false,$true).GetString($outTask.GetAwaiter().GetResult())
 $stderr=[Text.UTF8Encoding]::new($false,$true).GetString($errTask.GetAwaiter().GetResult())
 $child=Assert-ChildOutput -Stdout $stdout -ExitCode $process.ExitCode
 $receipt=[ordered]@{
  schema='ts-ee/wsl-child-relay/v0.2';request_id=$RequestId;attempt=$AttemptId
  effect_state='CONFIRMED_BOUNDED';windows_runner_pid=$PID;windows_wsl_pid=$wslPid
  windows_wsl_exit=$process.ExitCode;windows_cim_parent_status=$cim;windows_cim_parent_pid=$cimParent
  linux_child_pid=[int]$child.pid;linux_child_ppid=[int]$child.ppid
  linux_child_uid=[int]$child.uid;linux_pid_namespace=[string]$child.pid_namespace
  original_stdout_sha256=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($stdout))).ToLowerInvariant()
  original_stderr_sha256=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($stderr))).ToLowerInvariant()
  supplied_orca_runtime_id=$ExpectedOrcaRuntimeId;supplied_orca_handle=$ExpectedOrcaHandle
  supplied_orca_incarnation_id=$ExpectedOrcaIncarnationId;supplied_orca_host_id=$ExpectedOrcaHostId
  native_orca_join='REQUIRES_EXTERNAL_PROVIDER_READBACK'
  linux_stdout_identity='SELF_REPORTED_BOUNDED_NOT_KERNEL_ATTESTED'
  source_sha256=$actual;Product_effect='NONE';acceptance='NOT_AUTHORIZED'
 }
 # The authoritative INCOMPLETE marker takes precedence over all result files.
 # Flush a create-only temporary; remove marker before atomic same-volume rename.
 Write-ExclusiveUtf8 -Path (Join-Path $OutputDir 'RESULT.tmp') -Text ((ConvertTo-Json $receipt -Depth 6 -Compress)+[Environment]::NewLine)
 [IO.File]::Delete((Join-Path $OutputDir 'INCOMPLETE.txt'))
 [IO.File]::Move((Join-Path $OutputDir 'RESULT.tmp'),(Join-Path $OutputDir 'RESULT.json'))
 $final=Read-QualifiedResult -Directory $OutputDir
 Write-Output ('TS_EE004_WSL_RELAY_RESULT='+(ConvertTo-Json $final -Compress))
 exit 0
} catch {
 $reason=$_.Exception.Message
 if($started -and -not $settled -and $null -ne $process) {
  try {$process.Kill($true)} catch {}
  try {
   $wait=[Threading.CancellationTokenSource]::new([TimeSpan]::FromSeconds(2))
   try {$process.WaitForExitAsync($wait.Token).GetAwaiter().GetResult()} finally {$wait.Dispose()}
  } catch {$reason+='|CHILD_SETTLEMENT_UNKNOWN'}
 }
 # If child started, UNKNOWN is preserved even when a failure receipt exists.
 if($owned) {
  try {
   $failure=@{schema='ts-ee/wsl-failure/v0.2';request_id=$RequestId;attempt=$AttemptId
      effect_state=$(if($started){'UNKNOWN'}else{'NONE'});reason=$reason;Product_effect='NONE'}
   Write-ExclusiveUtf8 -Path (Join-Path $OutputDir 'FAILURE.json') -Text ((ConvertTo-Json $failure -Compress)+[Environment]::NewLine)
  } catch {}
 }
 [Console]::Error.WriteLine('TS_EE004_WSL_RELAY_BLOCKED='+$reason)
 exit 2
} finally {
 if($null -ne $cts) {$cts.Dispose()}
 if($null -ne $process) {$process.Dispose()}
}
