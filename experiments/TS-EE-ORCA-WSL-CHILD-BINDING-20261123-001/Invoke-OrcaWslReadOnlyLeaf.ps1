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
$RequestId = 'TS-EE-004-ORCA-WSL-E4-ATOMIC-RECEIPT-20261123-001'
$AttemptId = 'TS-EE-004-ORCA-WSL-E4-ATOMIC-RECEIPT-20261123-001-A001'
$Marker = 'TS_EE004_CHILD_JSON='
$MarkerSchema = 'ts-ee/wsl-child-marker/v0.2'
$MaxStdoutBytes = 4096
$MaxStderrBytes = 2048
$ExpectedLinuxExit = 7
$ExpectedUid = 1000
$WorkRoot = 'C:\TS\station'
$OutputDir = 'C:\TS\station\ts-ee004-wsl-leaf-e4-20261123-001'


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


# System.Text.Json preserves original JSON token kinds and duplicate object keys.
# ConvertFrom-Json alone is too permissive for identity- and receipt-bound checks.
Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Text.RegularExpressions;
public static class TSEEStrict {
 static string[] MarkerKeys={"schema","request_id","attempt","pid","ppid","uid","pid_namespace","intended_exit"};
 static string[] ReceiptKeys={"schema","request_id","attempt","effect_state","windows_runner_pid","windows_wsl_pid",
   "windows_wsl_exit","windows_cim_parent_status","windows_cim_parent_pid","linux_child_pid",
   "linux_child_ppid","linux_child_uid","linux_pid_namespace","original_stdout_sha256",
   "original_stderr_sha256","original_stdout_base64","original_stderr_base64",
   "original_stdout_bytes","original_stderr_bytes","supplied_orca_runtime_id","supplied_orca_handle",
   "supplied_orca_incarnation_id","supplied_orca_host_id","native_orca_join",
   "linux_stdout_identity","source_sha256","Product_effect","acceptance"};
 static HashSet<string> Fields(JsonElement obj,string[] expected,string[] integers) {
  if(obj.ValueKind!=JsonValueKind.Object) throw new Exception("EXPECTED_JSON_OBJECT");
  var known=new HashSet<string>(expected,StringComparer.Ordinal);
  var nums=new HashSet<string>(integers,StringComparer.Ordinal);
  var actual=new HashSet<string>(StringComparer.Ordinal);
  foreach(var item in obj.EnumerateObject()) {
   if(!known.Contains(item.Name) || !actual.Add(item.Name)) throw new Exception("UNEXPECTED_OR_DUPLICATE_PROPERTY");
   if(nums.Contains(item.Name)) {
    int value;
    if(item.Value.ValueKind!=JsonValueKind.Number ||
       !Regex.IsMatch(item.Value.GetRawText(),@"^(0|[1-9][0-9]*)$") ||
       !item.Value.TryGetInt32(out value)) throw new Exception("NON_INTEGER_JSON_TOKEN");
   } else if(item.Value.ValueKind!=JsonValueKind.String) {
    throw new Exception("NON_STRING_JSON_TOKEN");
   }
  }
  if(actual.Count!=known.Count) throw new Exception("INCOMPLETE_JSON_SCHEMA");
  return actual;
 }
 public static void Marker(string json,string schema,string req,string attempt) {
  using(var doc=JsonDocument.Parse(json)) {
   var e=doc.RootElement;
   Fields(e,MarkerKeys,new[]{"pid","ppid","uid","intended_exit"});
   if(!String.Equals(e.GetProperty("schema").GetString(),schema,StringComparison.Ordinal) ||
      !String.Equals(e.GetProperty("request_id").GetString(),req,StringComparison.Ordinal) ||
      !String.Equals(e.GetProperty("attempt").GetString(),attempt,StringComparison.Ordinal)) throw new Exception("MARKER_IDENTITY_MISMATCH");
   if(e.GetProperty("pid").GetInt32()<=1 || e.GetProperty("ppid").GetInt32()<1 ||
      e.GetProperty("uid").GetInt32()!=1000 || e.GetProperty("intended_exit").GetInt32()!=7 ||
      !Regex.IsMatch(e.GetProperty("pid_namespace").GetString(),@"^pid:\[[0-9]+\]$")) throw new Exception("MARKER_VALUE_MISMATCH");
  }
 }
 public static void Receipt(string json) {
  using(var doc=JsonDocument.Parse(json)) {
   Fields(doc.RootElement,ReceiptKeys,new[]{"windows_runner_pid","windows_wsl_pid",
    "windows_wsl_exit","windows_cim_parent_pid","linux_child_pid","linux_child_ppid",
    "linux_child_uid","original_stdout_bytes","original_stderr_bytes"});
  }
 }
}
'@

function Assert-ChildOutput {
 param([string]$Stdout,[int]$ExitCode)
 if($ExitCode -ne $ExpectedLinuxExit) {throw 'WSL_EXIT_MISMATCH'}
 # Exact UTF8 Python print: one line and exactly one terminal LF, no blank lines.
 if($null -eq $Stdout -or $Stdout.Length -le $Marker.Length -or
    -not $Stdout.EndsWith([string][char]10) -or
    $Stdout.Substring(0,$Stdout.Length-1).Contains([string][char]10) -or
    $Stdout.Contains([string][char]13)) {throw 'CHILD_MARKER_FRAMING_INVALID'}
 $line=$Stdout.Substring(0,$Stdout.Length-1)
 if(-not $line.StartsWith($Marker,[StringComparison]::Ordinal)) {throw 'CHILD_MARKER_PREFIX_INVALID'}
 $json=$line.Substring($Marker.Length)
 [TSEEStrict]::Marker($json,$MarkerSchema,$RequestId,$AttemptId)
 return (ConvertFrom-Json -InputObject $json -AsHashtable -ErrorAction Stop)
}
function Write-ExclusiveUtf8 {
 param([string]$Path,[string]$Text)
 $bytes=[System.Text.UTF8Encoding]::new($false).GetBytes($Text)
 $stream=[IO.FileStream]::new($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
 try {$stream.Write($bytes,0,$bytes.Length);$stream.Flush($true)} finally {$stream.Dispose()}
}
function Read-QualifiedResult {
 param([string]$Directory)
 # Check failure *first*, including a contradictory FAILURE+RESULT after emit error.
 if([IO.File]::Exists((Join-Path $Directory 'FAILURE.json'))) {throw 'FAILURE_RECEIPT_DOMINATES'}
 if([IO.File]::Exists((Join-Path $Directory 'INCOMPLETE.txt'))) {throw 'INCOMPLETE_MARKER_DOMINATES'}
 if([IO.File]::Exists((Join-Path $Directory 'RESULT.tmp'))) {throw 'PARTIAL_STAGING_PRESENT'}
 $path=Join-Path $Directory 'RESULT.json'
 if(-not [IO.File]::Exists($path)) {throw 'MISSING_TERMINAL_RECEIPT'}
 $raw=[IO.File]::ReadAllText($path,[Text.UTF8Encoding]::new($false,$true))
 [TSEEStrict]::Receipt($raw)
 $r=ConvertFrom-Json -InputObject $raw -AsHashtable -ErrorAction Stop
 if($r.schema -cne 'ts-ee/wsl-child-relay/v0.3' -or
    $r.request_id -cne $RequestId -or $r.attempt -cne $AttemptId -or
    $r.effect_state -cne 'CONFIRMED_BOUNDED' -or
    $r.Product_effect -cne 'NONE' -or $r.acceptance -cne 'NOT_AUTHORIZED' -or
    $r.source_sha256 -cne $ExpectedRunnerSha256.ToLowerInvariant() -or
    $r.supplied_orca_runtime_id -cne $ExpectedOrcaRuntimeId -or
    $r.supplied_orca_handle -cne $ExpectedOrcaHandle -or
    $r.supplied_orca_incarnation_id -cne $ExpectedOrcaIncarnationId -or
    $r.supplied_orca_host_id -cne $ExpectedOrcaHostId -or
    [int]$r.windows_wsl_exit -ne $ExpectedLinuxExit) {throw 'TERMINAL_RECEIPT_BINDING_INVALID'}
 $out=[Convert]::FromBase64String($r.original_stdout_base64)
 $err=[Convert]::FromBase64String($r.original_stderr_base64)
 if($out.Length -ne [int]$r.original_stdout_bytes -or
    $err.Length -ne [int]$r.original_stderr_bytes -or
    $out.Length -gt $MaxStdoutBytes -or $err.Length -gt $MaxStderrBytes) {throw 'ORIGINAL_BYTE_LENGTH_INVALID'}
 $outSha=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($out)).ToLowerInvariant()
 $errSha=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($err)).ToLowerInvariant()
 if($outSha -cne $r.original_stdout_sha256 -or $errSha -cne $r.original_stderr_sha256) {throw 'ORIGINAL_BYTE_HASH_MISMATCH'}
 $decoded=[Text.UTF8Encoding]::new($false,$true).GetString($out)
 $child=Assert-ChildOutput -Stdout $decoded -ExitCode ([int]$r.windows_wsl_exit)
 if([int]$r.linux_child_pid -ne [int]$child.pid -or
    [int]$r.linux_child_ppid -ne [int]$child.ppid -or
    [int]$r.linux_child_uid -ne [int]$child.uid -or
    $r.linux_pid_namespace -cne $child.pid_namespace) {throw 'ORIGINAL_CHILD_BINDING_MISMATCH'}
 return $r
}
function Assert-TrustedDirectoryAcl {
 param([string]$Path)
 $acl=Get-Acl -LiteralPath $Path -ErrorAction Stop
 $ownerSid=$acl.GetOwner([Security.Principal.SecurityIdentifier]).Value
 $selfSid=[Security.Principal.WindowsIdentity]::GetCurrent().User.Value
 $trusted=@($selfSid,'S-1-5-18','S-1-5-32-544','S-1-3-0')
 if($ownerSid -notin $trusted) {throw 'UNTRUSTED_DIRECTORY_OWNER'}
 $rights=[IO.FileSystemRights]::Write -bor [IO.FileSystemRights]::Modify -bor
         [IO.FileSystemRights]::Delete -bor [IO.FileSystemRights]::DeleteSubdirectoriesAndFiles -bor
         [IO.FileSystemRights]::ChangePermissions -bor [IO.FileSystemRights]::TakeOwnership
 foreach($ace in $acl.Access) {
  if($ace.AccessControlType -ne [Security.AccessControl.AccessControlType]::Allow) {continue}
  try {$trustee=$ace.IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value}
  catch {throw 'UNRESOLVED_ACL_TRUSTEE'}
  if($trustee -notin $trusted -and (($ace.FileSystemRights -band $rights) -ne 0)) {
   throw 'UNTRUSTED_DIRECTORY_WRITE_ACL'
  }
 }
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
 $text=$Marker+(ConvertTo-Json $good -Compress)+[string][char]10
 if((Assert-ChildOutput -Stdout $text -ExitCode 7).pid -ne 101) {throw 'POSITIVE_CASE_FAILED'}
 $cases=@('exit','request','attempt','schema','uid','duplicate','namespace','pid','ppid',
          'intended','missing','extra','json','extra_key','uid_string','uid_fraction',
          'wrong_case','duplicate_key','empty_line')
 foreach($c in $cases) {
  $copy=$good.Clone();$str=$text;$code=7
  switch($c) {
   'exit' {$code=0}
   'request' {$copy.request_id='BAD'}
   'attempt' {$copy.attempt='BAD'}
   'schema' {$copy.schema='BAD'}
   'uid' {$copy.uid=0}
   'duplicate' {$str=$text+$text}
   'namespace' {$copy.pid_namespace='BAD'}
   'pid' {$copy.pid=0}
   'ppid' {$copy.ppid=0}
   'intended' {$copy.intended_exit=0}
   'missing' {$str=''}
   'extra' {$str=$text+'UNEXPECTED'+[string][char]10}
   'json' {$str=$Marker+'{'+[string][char]10}
   'extra_key' {$copy.other='UNTRUSTED'}
   'uid_string' {$copy.uid='1000'}
   'uid_fraction' {$str=$Marker+('{"uid":1000.5,'+((ConvertTo-Json $good -Compress).Substring(1)))+[string][char]10}
   'wrong_case' {$copy.request_id=$RequestId.ToLowerInvariant()}
   'duplicate_key' {$str=$Marker+('{"uid":1000,'+((ConvertTo-Json $good -Compress).Substring(1)))+[string][char]10}
   'empty_line' {$str=$text+[string][char]10}
  }
  if($c -in @('request','attempt','schema','uid','namespace','pid','ppid','intended',
              'extra_key','uid_string','wrong_case')) {
   $str=$Marker+(ConvertTo-Json $copy -Compress)+[string][char]10
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
  # Positive complete original result test; the entire bounded stdout is
  # embedded and its hash checked by the consumer, not reconstructed from fields.
  $ExpectedRunnerSha256=('a'*64)
  $ExpectedOrcaRuntimeId='12345678-1234-1234-1234-123456789abc'
  $ExpectedOrcaHandle='term_12345678-1234-1234-1234-123456789abc'
  $ExpectedOrcaIncarnationId='12345678-1234-1234-1234-123456789abc'
  $ExpectedOrcaHostId='local'
  $outRaw=[Text.UTF8Encoding]::new($false).GetBytes($text)
  $errRaw=[byte[]]@()
  $outHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($outRaw)).ToLowerInvariant()
  $errHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($errRaw)).ToLowerInvariant()
  $fixture=[ordered]@{
    schema='ts-ee/wsl-child-relay/v0.3';request_id=$RequestId;attempt=$AttemptId
    effect_state='CONFIRMED_BOUNDED';windows_runner_pid=101;windows_wsl_pid=102
    windows_wsl_exit=7;windows_cim_parent_status='NOT_ATTESTED_BY_RUNNER_SEPARATE_PROVIDER_JOIN';windows_cim_parent_pid=0
    linux_child_pid=101;linux_child_ppid=1;linux_child_uid=1000;linux_pid_namespace='pid:[4026532211]'
    original_stdout_sha256=$outHash;original_stderr_sha256=$errHash
    original_stdout_base64=[Convert]::ToBase64String($outRaw)
    original_stderr_base64=[Convert]::ToBase64String($errRaw)
    original_stdout_bytes=$outRaw.Length;original_stderr_bytes=$errRaw.Length
    supplied_orca_runtime_id=$ExpectedOrcaRuntimeId;supplied_orca_handle=$ExpectedOrcaHandle
    supplied_orca_incarnation_id=$ExpectedOrcaIncarnationId;supplied_orca_host_id=$ExpectedOrcaHostId
    native_orca_join='REQUIRES_EXTERNAL_PROVIDER_READBACK'
    linux_stdout_identity='SELF_REPORTED_BOUNDED_NOT_KERNEL_ATTESTED'
    source_sha256=$ExpectedRunnerSha256;Product_effect='NONE';acceptance='NOT_AUTHORIZED'
  }
  $okdir=Join-Path $temp 'valid'
  [IO.Directory]::CreateDirectory($okdir)|Out-Null
  Write-ExclusiveUtf8 -Path (Join-Path $okdir 'RESULT.json') -Text ((ConvertTo-Json $fixture -Compress -Depth 6)+[Environment]::NewLine)
  if((Read-QualifiedResult -Directory $okdir).request_id -cne $RequestId) {throw 'POSITIVE_RECEIPT_REJECTED'}
  Write-ExclusiveUtf8 -Path (Join-Path $okdir 'FAILURE.json') -Text '{"effect_state":"UNKNOWN"}'
  Assert-Negative -Case 'failure_dominates_success' -Action {Read-QualifiedResult -Directory $okdir}
  $bad=(ConvertFrom-Json -InputObject (ConvertTo-Json $fixture -Depth 6 -Compress) -AsHashtable);$bad.original_stdout_base64=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('TAMPERED'))
  $tamper=Join-Path $temp 'tampered';[IO.Directory]::CreateDirectory($tamper)|Out-Null
  Write-ExclusiveUtf8 -Path (Join-Path $tamper 'RESULT.json') -Text ((ConvertTo-Json $bad -Compress -Depth 6)+[Environment]::NewLine)
  Assert-Negative -Case 'original_bytes_tampered' -Action {Read-QualifiedResult -Directory $tamper}
  $tiny=Join-Path $temp 'tiny';[IO.Directory]::CreateDirectory($tiny)|Out-Null
  Write-ExclusiveUtf8 -Path (Join-Path $tiny 'RESULT.json') -Text '{"schema":"ts-ee/wsl-child-relay/v0.3","effect_state":"CONFIRMED_BOUNDED","Product_effect":"NONE","windows_wsl_exit":7}'
  Assert-Negative -Case 'partial_receipt' -Action {Read-QualifiedResult -Directory $tiny}
 } finally {[IO.Directory]::Delete($temp,$true)}
 Write-Output '{"source_only":"PASS_STRICT_TYPED_MARKER_AND_COMPLETE_ORIGINAL_RECEIPT_NEGATIVES","Native_WSL":"NOT_RUN","Orca":"NOT_RUN","Product_effect":"NONE"}'
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
 Assert-TrustedDirectoryAcl -Path $ancestor
}
$wsl=Join-Path $env:WINDIR 'System32\wsl.exe'
if(-not [IO.File]::Exists($wsl)) {throw 'WSL_BINARY_MISSING'}
if((Get-AuthenticodeSignature -LiteralPath $wsl).Status.ToString() -ne 'Valid') {throw 'WSL_BINARY_SIGNATURE_UNVERIFIED'}
$linux=@'
import json,os,sys,time
p=os.getpid()
v={"schema":"ts-ee/wsl-child-marker/v0.2",
   "request_id":"TS-EE-004-ORCA-WSL-E4-ATOMIC-RECEIPT-20261123-001",
   "attempt":"TS-EE-004-ORCA-WSL-E4-ATOMIC-RECEIPT-20261123-001-A001",
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
 # CIM sampling is intentionally OUTSIDE this time-critical runner.
 # The controller's independently bounded native process inventory is authoritative;
 # no unbounded synchronous provider call occurs before the stream/exit join.
 $cim='NOT_ATTESTED_BY_RUNNER_SEPARATE_PROVIDER_JOIN'
 $cimParent=0
 [Threading.Tasks.Task]::WhenAll([Threading.Tasks.Task[]]@($outTask,$errTask,$exitTask)).GetAwaiter().GetResult()
 $settled=$true
 $outBytes=$outTask.GetAwaiter().GetResult()
 $errBytes=$errTask.GetAwaiter().GetResult()
 $stdout=[Text.UTF8Encoding]::new($false,$true).GetString($outBytes)
 $stderr=[Text.UTF8Encoding]::new($false,$true).GetString($errBytes)
 $child=Assert-ChildOutput -Stdout $stdout -ExitCode $process.ExitCode
 $receipt=[ordered]@{
  schema='ts-ee/wsl-child-relay/v0.3';request_id=$RequestId;attempt=$AttemptId
  effect_state='CONFIRMED_BOUNDED';windows_runner_pid=$PID;windows_wsl_pid=$wslPid
  windows_wsl_exit=$process.ExitCode;windows_cim_parent_status=$cim;windows_cim_parent_pid=$cimParent
  linux_child_pid=[int]$child.pid;linux_child_ppid=[int]$child.ppid
  linux_child_uid=[int]$child.uid;linux_pid_namespace=[string]$child.pid_namespace
  original_stdout_sha256=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($outBytes)).ToLowerInvariant()
  original_stderr_sha256=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($errBytes)).ToLowerInvariant()
  original_stdout_base64=[Convert]::ToBase64String($outBytes)
  original_stderr_base64=[Convert]::ToBase64String($errBytes)
  original_stdout_bytes=$outBytes.Length;original_stderr_bytes=$errBytes.Length
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
