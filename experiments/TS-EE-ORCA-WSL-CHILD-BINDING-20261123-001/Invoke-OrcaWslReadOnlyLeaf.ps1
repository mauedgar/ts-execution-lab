# TS EE 004 NONPRODUCT Windows to WSL child exit source candidate.
# Native mode requires a distinct exact host grant, immutable source and caller hash.
[CmdletBinding()]
param(
    [ValidateSet('SelfTest','Provision','Native')][string]$Mode = 'SelfTest',
    [string]$ExpectedRunnerSha256 = '',
    [string]$ExpectedOrcaRuntimeId = '',
    [string]$ExpectedOrcaHandle = '',
    [string]$ExpectedOrcaIncarnationId = '',
    [string]$ExpectedOrcaHostId = '',
    [string]$ExpectedDriveAclSha256 = '',
    [string]$ExpectedProvisionAttempt = '',
    [string]$ExpectedStationAclSha256 = ''
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$RequestId = 'TS-EE-004-ORCA-WSL-E7-ISOLATED-STATION-20261124-001'
$AttemptId = 'TS-EE-004-ORCA-WSL-E7-ISOLATED-STATION-20261124-001-A001'
$Marker = 'TS_EE004_CHILD_JSON='
$MarkerSchema = 'ts-ee/wsl-child-marker/v0.2'
$MaxStdoutBytes = 4096
$MaxStderrBytes = 2048
$ExpectedLinuxExit = 7
$ExpectedUid = 1000
$WorkRoot = 'C:\TS-EE-station'
$OutputDir = 'C:\TS-EE-station\ts-ee004-wsl-leaf-e7-20261124-001'
$ProvisionAttempt = 'TS-EE-004-E7-STATION-PROVISION-20261124-001-A001'


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
 [StructLayout(LayoutKind.Sequential)]
 private struct SecurityAttributes { public int Length; public IntPtr Descriptor; public int InheritHandle; }
 [DllImport("kernel32.dll",EntryPoint="CreateDirectoryW",CharSet=CharSet.Unicode,SetLastError=true)]
 [return: MarshalAs(UnmanagedType.Bool)]
 private static extern bool CreateWithSecurity(string path,ref SecurityAttributes attributes);
 [DllImport("advapi32.dll",EntryPoint="ConvertStringSecurityDescriptorToSecurityDescriptorW",CharSet=CharSet.Unicode,SetLastError=true)]
 [return: MarshalAs(UnmanagedType.Bool)]
 private static extern bool ParseSecurity(string sddl,uint revision,out IntPtr descriptor,out uint size);
 [DllImport("kernel32.dll")]
 private static extern IntPtr LocalFree(IntPtr memory);
 public static void ReserveTrusted(string path,string sid) {
  string sddl="D:P(A;OICI;FA;;;"+sid+")(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)";
  IntPtr descriptor; uint size;
  if(!ParseSecurity(sddl,1,out descriptor,out size))
   throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error(),"OUTPUT_DESCRIPTOR_PARSE_FAILED");
  try {
   var a=new SecurityAttributes {Length=Marshal.SizeOf<SecurityAttributes>(),Descriptor=descriptor,InheritHandle=0};
   if(!CreateWithSecurity(path,ref a))
    throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error(),"OUTPUT_RESERVATION_FAILED");
  } finally {LocalFree(descriptor);}
 }
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
 param([string]$Directory,[string]$OutputAclPin)
 $null=Assert-OutputDirectory -Path $Directory -Expected $OutputAclPin
 # Enumeration errors propagate, never interpreted as absence.
 $names=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
 $enum=[IO.EnumerationOptions]::new()
 $enum.IgnoreInaccessible=$false;$enum.RecurseSubdirectories=$false;$enum.AttributesToSkip=[IO.FileAttributes]0
 foreach($entry in [IO.Directory]::EnumerateFileSystemEntries($Directory,'*',$enum)) {
  if($names.Count -ge 16) {throw 'RECEIPT_NAMESPACE_LIMIT'}
  if(-not $names.Add([IO.Path]::GetFileName($entry))) {throw 'RECEIPT_NAMESPACE_AMBIGUOUS'}
 }
 if($names.Contains('FAILURE.json')) {throw 'FAILURE_RECEIPT_DOMINATES'}
 if($names.Contains('INCOMPLETE.txt')) {throw 'INCOMPLETE_MARKER_DOMINATES'}
 if($names.Contains('RESULT.tmp')) {throw 'PARTIAL_STAGING_PRESENT'}
 if(-not $names.Contains('RESULT.json')) {throw 'MISSING_TERMINAL_RECEIPT'}
 if($names.Count -ne 1) {throw 'UNEXPECTED_RECEIPT_OCCUPANT'}
 $path=Join-Path $Directory 'RESULT.json'
 Assert-TrustedFileAcl -Path $path
 $stream=[IO.FileStream]::new($path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read)
 try {
  if($stream.Length -gt 16384) {throw 'RECEIPT_BYTE_LIMIT'}
  $data=[byte[]]::new([int]$stream.Length)
  $stream.ReadExactly($data)
  if($stream.ReadByte() -ne -1) {throw 'RECEIPT_GREW'}
  $raw=[Text.UTF8Encoding]::new($false,$true).GetString($data)
 } finally {$stream.Dispose()}
 [TSEEStrict]::Receipt($raw)
 $r=ConvertFrom-Json -InputObject $raw -AsHashtable -ErrorAction Stop
 if($r.schema -cne 'ts-ee/wsl-child-relay/v0.3' -or
    $r.request_id -cne $RequestId -or $r.attempt -cne $AttemptId -or
    $r.effect_state -cne 'OBSERVED_LOCAL_REQUIRES_PROVIDER_JOIN' -or
    $r.Product_effect -cne 'NONE' -or $r.acceptance -cne 'NOT_AUTHORIZED' -or
    $r.source_sha256 -cne $ExpectedRunnerSha256.ToLowerInvariant() -or
    $r.supplied_orca_runtime_id -cne $ExpectedOrcaRuntimeId -or
    $r.supplied_orca_handle -cne $ExpectedOrcaHandle -or
    $r.supplied_orca_incarnation_id -cne $ExpectedOrcaIncarnationId -or
    $r.supplied_orca_host_id -cne $ExpectedOrcaHostId -or
    [int]$r.windows_runner_pid -le 0 -or [int]$r.windows_wsl_pid -le 0 -or
    $r.windows_cim_parent_status -cne 'NOT_ATTESTED_BY_RUNNER_SEPARATE_PROVIDER_JOIN' -or [int]$r.windows_cim_parent_pid -ne 0 -or
    $r.native_orca_join -cne 'REQUIRES_EXTERNAL_PROVIDER_READBACK' -or
    $r.linux_stdout_identity -cne 'SELF_REPORTED_BOUNDED_NOT_KERNEL_ATTESTED' -or
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
 $null=Assert-OutputDirectory -Path $Directory -Expected $OutputAclPin
 return $r
}
function Get-AclFingerprint {
 param([Security.AccessControl.DirectorySecurity]$Acl)
 $sections=[Security.AccessControl.AccessControlSections]::Access -bor [Security.AccessControl.AccessControlSections]::Owner -bor [Security.AccessControl.AccessControlSections]::Group
 $sddl=$Acl.GetSecurityDescriptorSddlForm($sections)
 return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($sddl))).ToLowerInvariant()
}
function Assert-AclObject {
 param([Security.AccessControl.FileSystemSecurity]$Acl,[string]$SelfSid,[switch]$DriveAnchor)
 $raw=[Security.AccessControl.RawSecurityDescriptor]::new($Acl.GetSecurityDescriptorBinaryForm(),0)
 if($null -eq $raw.DiscretionaryAcl -or $null -eq $raw.Owner) {throw 'NULL_DACL_NOT_ADMITTED'}
 $trusted=@($SelfSid,'S-1-5-18','S-1-5-32-544')
 $owners=@($trusted)
 if($DriveAnchor){$owners+=@('S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464')}
 if($raw.Owner.Value -notin $owners) {throw 'UNTRUSTED_DIRECTORY_OWNER'}
 if($raw.DiscretionaryAcl.Count -gt 64){throw 'ACL_ACE_LIMIT'}
 # Admit only ordinary common allow/deny ACEs; do not project away callback/object/unknown ACEs.
 foreach($ace in $raw.DiscretionaryAcl){
  if($ace -isnot [Security.AccessControl.CommonAce] -or $ace.IsCallback -or
     $ace.AceQualifier -notin @([Security.AccessControl.AceQualifier]::AccessAllowed,[Security.AccessControl.AceQualifier]::AccessDenied)){
   throw 'UNSUPPORTED_ACL_ACE'
  }
  if($ace.AceQualifier -ne [Security.AccessControl.AceQualifier]::AccessAllowed -or $ace.SecurityIdentifier.Value -in $trusted){continue}
  # A drive-root inherit-only allow is not effective on the anchor. The isolated child
  # is created atomically with a protected DACL, so this ACE is not inherited there.
  if($DriveAnchor -and (($ace.AceFlags -band [Security.AccessControl.AceFlags]::InheritOnly) -ne 0)){continue}
  # Known read/traverse/synchronize rights only; on the fixed drive anchor allow ADD_SUBDIRECTORY
  # (0x4) but never DELETE_CHILD, DELETE, WRITE_DAC, WRITE_OWNER, generic write/all or other bits.
  [long]$allowed=0x1200a9
  if($DriveAnchor){$allowed=$allowed -bor 4}
  [long]$mask=([long]$ace.AccessMask -band 4294967295L)
  if(($mask -band (-bnot $allowed)) -ne 0){throw 'UNTRUSTED_DIRECTORY_WRITE_ACL'}
 }
}
function Assert-TrustedDirectoryAcl {
 param([string]$Path,[string]$Expected,[switch]$DriveAnchor)
 if($Expected -cnotmatch '\A[a-f0-9]{64}\z') {throw 'EXTERNAL_ACL_PIN_REQUIRED'}
 $attrs=[IO.File]::GetAttributes($Path)
 if(($attrs -band [IO.FileAttributes]::Directory) -eq 0 -or ($attrs -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'UNSAFE_ANCESTOR_REPARSE'}
 $acl=Get-Acl -LiteralPath $Path -ErrorAction Stop
 if(-not $acl.AreAccessRulesProtected){throw 'ANCESTOR_DACL_NOT_PROTECTED'}
 Assert-AclObject -Acl $acl -SelfSid (Get-CurrentSid) -DriveAnchor:$DriveAnchor
 if((Get-AclFingerprint -Acl $acl) -cne $Expected) {throw 'EXTERNAL_ACL_PIN_MISMATCH'}
}
function Assert-DriveAnchor {
 param([string]$Expected)
 $drive=[IO.DriveInfo]::new('C:\')
 if($drive.DriveType -ne [IO.DriveType]::Fixed -or $drive.DriveFormat -cne 'NTFS'){throw 'UNQUALIFIED_DRIVE'}
 Assert-TrustedDirectoryAcl -Path 'C:\' -Expected $Expected -DriveAnchor
}
function Get-CurrentSid {
 return [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
}
function Assert-OutputDirectory {
 param([string]$Path,[string]$Expected,[switch]$Initial)
 $attrs=[IO.File]::GetAttributes($Path)
 if(($attrs -band [IO.FileAttributes]::Directory) -eq 0 -or ($attrs -band [IO.FileAttributes]::ReparsePoint) -ne 0) {throw 'UNSAFE_OUTPUT_DIRECTORY'}
 $acl=Get-Acl -LiteralPath $Path -ErrorAction Stop
 if(-not $acl.AreAccessRulesProtected) {throw 'OUTPUT_DACL_NOT_PROTECTED'}
 Assert-AclObject -Acl $acl -SelfSid (Get-CurrentSid)
 $pin=Get-AclFingerprint -Acl $acl
 if(-not $Initial -and ($Expected -cnotmatch '^[a-f0-9]{64}$' -or $pin -cne $Expected)) {throw 'OUTPUT_ACL_PIN_MISMATCH'}
 return $pin
}
function Assert-EmptyProtectedRoot {
 param([string]$Path)
 $pin=Assert-OutputDirectory -Path $Path -Initial
 $enum=[IO.EnumerationOptions]::new()
 $enum.IgnoreInaccessible=$false;$enum.RecurseSubdirectories=$false;$enum.AttributesToSkip=[IO.FileAttributes]0
 foreach($entry in [IO.Directory]::EnumerateFileSystemEntries($Path,'*',$enum)){throw 'STATION_ROOT_NOT_EMPTY'}
 $null=Assert-OutputDirectory -Path $Path -Expected $pin
 return $pin
}
function Assert-TrustedFileAcl {
 param([string]$Path)
 $attrs=[IO.File]::GetAttributes($Path)
 if(($attrs -band ([IO.FileAttributes]::ReparsePoint -bor [IO.FileAttributes]::Directory)) -ne 0) {throw 'UNSAFE_RECEIPT_FILE'}
 $acl=Get-Acl -LiteralPath $Path -ErrorAction Stop
 Assert-AclObject -Acl $acl -SelfSid (Get-CurrentSid)
}
function New-TestDirectory {
 param([string]$Path)
 [TSEEBounded]::ReserveTrusted($Path,(Get-CurrentSid))
 $testPins.Add($Path,(Assert-OutputDirectory -Path $Path -Initial))
}
function Read-TestResult {
 param([string]$Directory)
 return (Read-QualifiedResult -Directory $Directory -OutputAclPin $testPins[$Directory])
}
function Assert-Rejection {
 param([scriptblock]$Action,[string]$Reason,[string]$Case)
 try {$null=& $Action} catch {
  $actual=$_.Exception.GetBaseException().Message
  if($actual -cne $Reason) {throw ('WRONG_REJECTION_'+$Case+': '+$actual+' expected '+$Reason)}
  return
 }
 throw ('NEGATIVE_NOT_DENIED_'+$Case)
}
function Wait-LeafTasks {
 param([Threading.Tasks.Task[]]$Tasks,[int]$Milliseconds)
 $all=[Threading.Tasks.Task]::WhenAll($Tasks)
 $deadline=[Threading.Tasks.Task]::Delay($Milliseconds)
 $winner=[Threading.Tasks.Task]::WhenAny([Threading.Tasks.Task[]]@($all,$deadline)).GetAwaiter().GetResult()
 if(-not [Object]::ReferenceEquals($winner,$all)) {throw 'WSL_DEADLINE_EFFECT_UNKNOWN'}
 $all.GetAwaiter().GetResult()
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
          'intended','missing','extra','json','extra_key','uid_string','uid_fraction','uid_exponent',
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
   'uid_fraction' {$str=$text.Replace('"uid":1000','"uid":1000.5')}
   'uid_exponent' {$str=$text.Replace('"uid":1000','"uid":1e3')}
   'wrong_case' {$copy.request_id=$RequestId.ToLowerInvariant()}
   'duplicate_key' {$str=$Marker+('{"uid":1000,'+((ConvertTo-Json $good -Compress).Substring(1)))+[string][char]10}
   'empty_line' {$str=$text+[string][char]10}
  }
  if($c -in @('request','attempt','schema','uid','namespace','pid','ppid','intended',
              'extra_key','uid_string','wrong_case')) {
   $str=$Marker+(ConvertTo-Json $copy -Compress)+[string][char]10
  }
  $expected=@{
   exit='WSL_EXIT_MISMATCH';request='MARKER_IDENTITY_MISMATCH';attempt='MARKER_IDENTITY_MISMATCH';schema='MARKER_IDENTITY_MISMATCH'
   uid='MARKER_VALUE_MISMATCH';duplicate='CHILD_MARKER_FRAMING_INVALID';namespace='MARKER_VALUE_MISMATCH'
   pid='MARKER_VALUE_MISMATCH';ppid='MARKER_VALUE_MISMATCH';intended='MARKER_VALUE_MISMATCH';missing='CHILD_MARKER_FRAMING_INVALID'
   extra='CHILD_MARKER_FRAMING_INVALID';extra_key='UNEXPECTED_OR_DUPLICATE_PROPERTY';uid_string='NON_INTEGER_JSON_TOKEN'
   uid_fraction='NON_INTEGER_JSON_TOKEN';uid_exponent='NON_INTEGER_JSON_TOKEN';wrong_case='MARKER_IDENTITY_MISMATCH'
   duplicate_key='UNEXPECTED_OR_DUPLICATE_PROPERTY';empty_line='CHILD_MARKER_FRAMING_INVALID'
  }
  if($c -eq 'json') {Assert-Negative -Case $c -Action {Assert-ChildOutput -Stdout $str -ExitCode $code}}
  else {Assert-Rejection -Case $c -Reason $expected[$c] -Action {Assert-ChildOutput -Stdout $str -ExitCode $code}}
 }
 $oversize=[Text.UTF8Encoding]::new($false).GetBytes('X'*17)
 $read=[TSEEBounded]::Capture([IO.MemoryStream]::new($oversize),16,[Threading.CancellationToken]::None)
 Assert-Rejection -Case 'byte_limit' -Reason 'OUTPUT_BYTE_LIMIT_EXCEEDED' -Action {$null=$read.GetAwaiter().GetResult()}
 $temp=Join-Path ([IO.Path]::GetTempPath()) ('ts-ee-self-'+[guid]::NewGuid().ToString('N'))
 $testPins=[Collections.Generic.Dictionary[string,string]]::new([StringComparer]::Ordinal)
 New-TestDirectory -Path $temp
 try {
  $reserved=Join-Path $temp 'reservation'
  New-TestDirectory -Path $reserved
  if((Assert-EmptyProtectedRoot -Path $reserved) -cne $testPins[$reserved]){throw 'PROVISION_PIN_MISMATCH'}
  $collision=$false
  try {[TSEEBounded]::ReserveTrusted($reserved,(Get-CurrentSid))} catch {
   $ex=$_.Exception.GetBaseException()
   if($ex -isnot [ComponentModel.Win32Exception] -or $ex.NativeErrorCode -ne 183) {throw}
   $collision=$true
  }
  if(-not $collision) {throw 'ATOMIC_COLLISION_NOT_BLOCKED'}
  Assert-Rejection -Case 'no_receipt' -Reason 'MISSING_TERMINAL_RECEIPT' -Action {Read-TestResult -Directory $reserved}
  Write-ExclusiveUtf8 -Path (Join-Path $reserved 'INCOMPLETE.txt') -Text 'UNTRUSTED'
  Assert-Rejection -Case 'provision_nonempty' -Reason 'STATION_ROOT_NOT_EMPTY' -Action {Assert-EmptyProtectedRoot -Path $reserved}
  Assert-Rejection -Case 'marker' -Reason 'INCOMPLETE_MARKER_DOMINATES' -Action {Read-TestResult -Directory $reserved}
  Write-ExclusiveUtf8 -Path (Join-Path $reserved 'RESULT.json') -Text '{"spoofed":true}'
  Assert-Rejection -Case 'marker_dominates_result' -Reason 'INCOMPLETE_MARKER_DOMINATES' -Action {Read-TestResult -Directory $reserved}
  Assert-Negative -Case 'leaf_collision' -Action {Write-ExclusiveUtf8 -Path (Join-Path $reserved 'RESULT.json') -Text 'REPLACE'}
  # Positive complete original result test; the entire bounded stdout is
  # embedded and its hash checked by the consumer, not reconstructed from fields.
  $ExpectedRunnerSha256=('a'*64)
  $ExpectedOrcaRuntimeId='12345678-1234-1234-1234-123456789abc'
  $ExpectedOrcaHandle='term_12345678-1234-1234-1234-123456789abc'
  $ExpectedOrcaIncarnationId='12345678-1234-1234-1234-123456789abc'
  $ExpectedOrcaHostId='local'
  $outRaw=[Text.UTF8Encoding]::new($false).GetBytes($text)
  $errRaw=[byte[]]@(0,255,128,10)
  $outHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($outRaw)).ToLowerInvariant()
  $errHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($errRaw)).ToLowerInvariant()
  $fixture=[ordered]@{
    schema='ts-ee/wsl-child-relay/v0.3';request_id=$RequestId;attempt=$AttemptId
    effect_state='OBSERVED_LOCAL_REQUIRES_PROVIDER_JOIN';windows_runner_pid=101;windows_wsl_pid=102
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
  New-TestDirectory -Path $okdir
  Write-ExclusiveUtf8 -Path (Join-Path $okdir 'RESULT.json') -Text ((ConvertTo-Json $fixture -Compress -Depth 6)+[Environment]::NewLine)
  if((Read-TestResult -Directory $okdir).request_id -cne $RequestId) {throw 'POSITIVE_RECEIPT_REJECTED'}
  Write-ExclusiveUtf8 -Path (Join-Path $okdir 'FAILURE.json') -Text '{"effect_state":"UNKNOWN"}'
  Assert-Rejection -Case 'failure_dominates_success' -Reason 'FAILURE_RECEIPT_DOMINATES' -Action {Read-TestResult -Directory $okdir}
  [IO.File]::Delete((Join-Path $okdir 'FAILURE.json'))
  $markerReasons=@{'FAILURE.json'='FAILURE_RECEIPT_DOMINATES';'INCOMPLETE.txt'='INCOMPLETE_MARKER_DOMINATES';'RESULT.tmp'='PARTIAL_STAGING_PRESENT'}
  foreach($name in $markerReasons.Keys) {
   $occupant=Join-Path $okdir $name
   [IO.Directory]::CreateDirectory($occupant)|Out-Null
   try {Assert-Rejection -Case ('directory_occupant_'+$name) -Reason $markerReasons[$name] -Action {Read-TestResult -Directory $okdir}}
   finally {[IO.Directory]::Delete($occupant)}
  }
  Assert-Rejection -Case 'wrong_output_pin' -Reason 'OUTPUT_ACL_PIN_MISMATCH' -Action {Read-QualifiedResult -Directory $okdir -OutputAclPin ('0'*64)}
  $altered=Join-Path $temp 'altered';New-TestDirectory -Path $altered
  $acl=Get-Acl -LiteralPath $altered
  $acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new([Security.Principal.SecurityIdentifier]::new('S-1-1-0'),[Security.AccessControl.FileSystemRights]::WriteData,[Security.AccessControl.AccessControlType]::Allow))
  Set-Acl -LiteralPath $altered -AclObject $acl
  Assert-Rejection -Case 'untrusted_child_acl' -Reason 'UNTRUSTED_DIRECTORY_WRITE_ACL' -Action {Assert-OutputDirectory -Path $altered -Expected $testPins[$altered]}
  $bad=(ConvertFrom-Json -InputObject (ConvertTo-Json $fixture -Depth 6 -Compress) -AsHashtable)
  $tampered=[byte[]]$outRaw.Clone();$tampered[0]=$tampered[0] -bxor 1
  $bad.original_stdout_base64=[Convert]::ToBase64String($tampered)
  $tamper=Join-Path $temp 'tampered';New-TestDirectory -Path $tamper
  Write-ExclusiveUtf8 -Path (Join-Path $tamper 'RESULT.json') -Text ((ConvertTo-Json $bad -Compress -Depth 6)+[Environment]::NewLine)
  Assert-Rejection -Case 'original_bytes_tampered' -Reason 'ORIGINAL_BYTE_HASH_MISMATCH' -Action {Read-TestResult -Directory $tamper}
  $bad=(ConvertFrom-Json -InputObject (ConvertTo-Json $fixture -Depth 6 -Compress) -AsHashtable)
  $errTampered=[byte[]]$errRaw.Clone();$errTampered[0]=1
  $bad.original_stderr_base64=[Convert]::ToBase64String($errTampered)
  $errdir=Join-Path $temp 'tampered_stderr';New-TestDirectory -Path $errdir
  Write-ExclusiveUtf8 -Path (Join-Path $errdir 'RESULT.json') -Text (ConvertTo-Json $bad -Compress)
  Assert-Rejection -Case 'stderr_tampered' -Reason 'ORIGINAL_BYTE_HASH_MISMATCH' -Action {Read-TestResult -Directory $errdir}
  $tiny=Join-Path $temp 'tiny';New-TestDirectory -Path $tiny
  Write-ExclusiveUtf8 -Path (Join-Path $tiny 'RESULT.json') -Text '{"schema":"ts-ee/wsl-child-relay/v0.3","effect_state":"OBSERVED_LOCAL_REQUIRES_PROVIDER_JOIN","Product_effect":"NONE","windows_wsl_exit":7}'
  Assert-Rejection -Case 'partial_receipt' -Reason 'INCOMPLETE_JSON_SCHEMA' -Action {Read-TestResult -Directory $tiny}
  $never=[Threading.Tasks.TaskCompletionSource[bool]]::new()
  Assert-Rejection -Case 'independent_deadline' -Reason 'WSL_DEADLINE_EFFECT_UNKNOWN' -Action {Wait-LeafTasks -Tasks @($never.Task) -Milliseconds 20}
  $identity=[Security.Principal.WindowsIdentity]::GetCurrent().User
  $goodAcl=[Security.AccessControl.DirectorySecurity]::new()
  $goodAcl.SetOwner($identity)
  $readSid=[Security.Principal.SecurityIdentifier]::new('S-1-1-0')
  $read=[Security.AccessControl.FileSystemAccessRule]::new($readSid,[Security.AccessControl.FileSystemRights]::ReadAndExecute,[Security.AccessControl.AccessControlType]::Allow)
  $goodAcl.AddAccessRule($read)
  Assert-AclObject -Acl $goodAcl -SelfSid $identity.Value
  if((Get-AclFingerprint -Acl $goodAcl) -cnotmatch '^[a-f0-9]{64}$') {throw 'ACL_FINGERPRINT_FAILED'}
  $write=[Security.AccessControl.FileSystemAccessRule]::new($readSid,[Security.AccessControl.FileSystemRights]::WriteData,[Security.AccessControl.AccessControlType]::Allow)
  $goodAcl.AddAccessRule($write)
  Assert-Rejection -Case 'untrusted_write_acl' -Reason 'UNTRUSTED_DIRECTORY_WRITE_ACL' -Action {Assert-AclObject -Acl $goodAcl -SelfSid $identity.Value}
  # Model the observed fixed-volume root ACL and distinguish anchor from station.
  $anchorAcl=[Security.AccessControl.DirectorySecurity]::new()
  $ti='S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464'
  $anchorSddl='O:'+$ti+'G:SYD:P(A;;0x4;;;AU)(A;OICIIO;0xe0010000;;;AU)(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)(A;OICI;0x1200a9;;;BU)'
  $anchorAcl.SetSecurityDescriptorSddlForm($anchorSddl)
  Assert-AclObject -Acl $anchorAcl -SelfSid $identity.Value -DriveAnchor
  Assert-Rejection -Case 'anchor_not_station' -Reason 'UNTRUSTED_DIRECTORY_OWNER' -Action {Assert-AclObject -Acl $anchorAcl -SelfSid $identity.Value}
  foreach($case in @(@{label='delete_child';mask='0x40'},@{label='delete';mask='0x10000'},@{label='write_dac';mask='0x40000'},@{label='write_owner';mask='0x80000'},@{label='generic_write';mask='0x40000000'})){
   $badAnchor=[Security.AccessControl.DirectorySecurity]::new()
   $badAnchor.SetSecurityDescriptorSddlForm($anchorSddl.Replace('(A;;0x4;;;AU)',('(A;;'+$case.mask+';;;AU)')))
   Assert-Rejection -Case ('anchor_'+$case.label) -Reason 'UNTRUSTED_DIRECTORY_WRITE_ACL' -Action {Assert-AclObject -Acl $badAnchor -SelfSid $identity.Value -DriveAnchor}
  }
  $inheritedStation=[Security.AccessControl.DirectorySecurity]::new()
  $inheritedStation.SetSecurityDescriptorSddlForm(('O:'+$identity.Value+'G:SYD:P(A;OICIIO;0x40000000;;;AU)(A;OICI;FA;;;SY)'))
  Assert-Rejection -Case 'station_inherit_only_write' -Reason 'UNTRUSTED_DIRECTORY_WRITE_ACL' -Action {Assert-AclObject -Acl $inheritedStation -SelfSid $identity.Value}
  $oversizedDir=Join-Path $temp 'oversized';New-TestDirectory -Path $oversizedDir
  Write-ExclusiveUtf8 -Path (Join-Path $oversizedDir 'RESULT.json') -Text ('x'*16385)
  Assert-Rejection -Case 'oversized_receipt' -Reason 'RECEIPT_BYTE_LIMIT' -Action {Read-TestResult -Directory $oversizedDir}
 } finally {[IO.Directory]::Delete($temp,$true)}
 Write-Output '{"source_only":"PASS_E7_ISOLATED_ANCHOR_PROVISION_AND_PROTECTED_OUTPUT_FIXTURES","Native_Provision":"NOT_RUN","Native_WSL":"NOT_RUN","Orca":"NOT_RUN","Product_effect":"NONE"}'
 exit 0
}

# Provision and Native are separate grant-bound effects. No automatic transition or replay.
if($PSVersionTable.PSVersion.Major -lt 7 -or -not $IsWindows) {throw 'PWSH7_WINDOWS_REQUIRED'}
if($env:COMPUTERNAME -ne 'DESKTOP-DJLBEQH') {throw 'WRONG_HOST'}
if($ExpectedRunnerSha256 -notmatch '\A[a-fA-F0-9]{64}\z') {throw 'MISSING_CALLER_HASH'}
$actual=(Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant()
if($actual -ne $ExpectedRunnerSha256.ToLowerInvariant()) {throw 'SOURCE_HASH_MISMATCH'}
Assert-DriveAnchor -Expected $ExpectedDriveAclSha256
if($Mode -eq 'Provision'){
 if($ExpectedProvisionAttempt -cne $ProvisionAttempt -or $ExpectedOrcaRuntimeId -or $ExpectedOrcaHandle -or
    $ExpectedOrcaIncarnationId -or $ExpectedOrcaHostId -or $ExpectedStationAclSha256){throw 'PROVISION_GRANT_BINDING'}
 $created=$false
 try{
  [TSEEBounded]::ReserveTrusted($WorkRoot,(Get-CurrentSid))
  $created=$true
  $pin=Assert-EmptyProtectedRoot -Path $WorkRoot
  Assert-DriveAnchor -Expected $ExpectedDriveAclSha256
  [Console]::WriteLine((@{schema='ts-ee/e7-station-provision/v1';attempt=$ProvisionAttempt;root=$WorkRoot;status='PROVISIONED_NOT_ADMITTED';effect='CONFIRMED';root_acl_sha256=$pin;drive_acl_sha256=$ExpectedDriveAclSha256;source_sha256=$actual;Native_WSL='NOT_RUN';Orca='NOT_RUN';Product_effect='NONE'}|ConvertTo-Json -Compress))
  exit 0
 }catch{
  [Console]::WriteLine((@{schema='ts-ee/e7-station-provision/v1';attempt=$ProvisionAttempt;root=$WorkRoot;status='PROVISION_BLOCKED';effect=$(if($created){'UNKNOWN'}else{'NONE'});reason=$_.Exception.Message;Product_effect='NONE'}|ConvertTo-Json -Compress))
  exit 2
 }
}
if($ExpectedProvisionAttempt){throw 'NATIVE_PROVISION_ID_CONFLICT'}
$uuid='[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
if($ExpectedOrcaRuntimeId -cnotmatch ('^'+$uuid+'$') -or
   $ExpectedOrcaHandle -cnotmatch ('^term_'+$uuid+'$') -or
   $ExpectedOrcaIncarnationId -cnotmatch ('^'+$uuid+'$') -or
   $ExpectedOrcaHostId -ne 'local') {throw 'EXTERNAL_ORCA_BINDING_REQUIRED'}
if(-not [IO.Directory]::Exists($WorkRoot)) {throw 'MISSING_WORKROOT'}
Assert-DriveAnchor -Expected $ExpectedDriveAclSha256
Assert-TrustedDirectoryAcl -Path $WorkRoot -Expected $ExpectedStationAclSha256
$wsl=Join-Path $env:WINDIR 'System32\wsl.exe'
if(-not [IO.File]::Exists($wsl)) {throw 'WSL_BINARY_MISSING'}
if((Get-AuthenticodeSignature -LiteralPath $wsl).Status.ToString() -ne 'Valid') {throw 'WSL_BINARY_SIGNATURE_UNVERIFIED'}
$linux=@'
import json,os,sys,time
p=os.getpid()
v={"schema":"ts-ee/wsl-child-marker/v0.2",
   "request_id":"TS-EE-004-ORCA-WSL-E7-ISOLATED-STATION-20261124-001",
   "attempt":"TS-EE-004-ORCA-WSL-E7-ISOLATED-STATION-20261124-001-A001",
   "pid":p,"ppid":os.getppid(),"uid":os.getuid(),
   "pid_namespace":os.readlink("/proc/%d/ns/pid"%p),"intended_exit":7}
print("TS_EE004_CHILD_JSON="+json.dumps(v,sort_keys=True,separators=(',',':')),flush=True)
time.sleep(2)
sys.exit(7)
'@
$owned=$false;$safeOutput=$false;$outputAclPin='';$started=$false;$settled=$false;$process=$null;$cts=$null
$cim='NOT_ATTESTED';$cimParent=0
try {
 # Atomic Win32 fail-on-existing reservation; a checked Directory.CreateDirectory
 # would silently reuse an occupied path. Exclusive leaf writes also fail closed.
 [TSEEBounded]::ReserveTrusted($OutputDir,(Get-CurrentSid))
 $owned=$true
 $outputAclPin=Assert-OutputDirectory -Path $OutputDir -Initial
 $safeOutput=$true
 Write-ExclusiveUtf8 -Path (Join-Path $OutputDir 'INCOMPLETE.txt') -Text 'UNTRUSTED_UNSETTLED'
 Assert-TrustedFileAcl -Path (Join-Path $OutputDir 'INCOMPLETE.txt')
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
 Wait-LeafTasks -Tasks @($outTask,$errTask,$exitTask) -Milliseconds 16000
 $settled=$true
 $outBytes=$outTask.GetAwaiter().GetResult()
 $errBytes=$errTask.GetAwaiter().GetResult()
 $stdout=[Text.UTF8Encoding]::new($false,$true).GetString($outBytes)
 # Stderr is opaque bounded bytes; no lossy or unnecessary text decode.
 $child=Assert-ChildOutput -Stdout $stdout -ExitCode $process.ExitCode
 Assert-DriveAnchor -Expected $ExpectedDriveAclSha256
 Assert-TrustedDirectoryAcl -Path $WorkRoot -Expected $ExpectedStationAclSha256
 $null=Assert-OutputDirectory -Path $OutputDir -Expected $outputAclPin
 $receipt=[ordered]@{
  schema='ts-ee/wsl-child-relay/v0.3';request_id=$RequestId;attempt=$AttemptId
  effect_state='OBSERVED_LOCAL_REQUIRES_PROVIDER_JOIN';windows_runner_pid=$PID;windows_wsl_pid=$wslPid
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
 Assert-TrustedFileAcl -Path (Join-Path $OutputDir 'RESULT.tmp')
 $null=Assert-OutputDirectory -Path $OutputDir -Expected $outputAclPin
 [IO.File]::Delete((Join-Path $OutputDir 'INCOMPLETE.txt'))
 [IO.File]::Move((Join-Path $OutputDir 'RESULT.tmp'),(Join-Path $OutputDir 'RESULT.json'))
 $final=Read-QualifiedResult -Directory $OutputDir -OutputAclPin $outputAclPin
 Write-Output ('TS_EE004_OUTPUT_ACL_PIN='+$outputAclPin)
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
 if($owned -and $safeOutput) {
  try {
   Assert-DriveAnchor -Expected $ExpectedDriveAclSha256
   Assert-TrustedDirectoryAcl -Path $WorkRoot -Expected $ExpectedStationAclSha256
    $null=Assert-OutputDirectory -Path $OutputDir -Expected $outputAclPin
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
