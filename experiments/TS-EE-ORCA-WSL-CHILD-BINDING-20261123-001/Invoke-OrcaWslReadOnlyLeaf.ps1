# TS EE 004 NONPRODUCT Windows to WSL child exit source candidate.
# Native mode requires a distinct exact host grant, immutable source and caller hash.
[CmdletBinding()]
param(
    [ValidateSet('SelfTest','Native')][string]$Mode = 'SelfTest',
    [string]$ExpectedRunnerSha256 = ''
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$RequestId = 'TS-EE-004-ORCA-WSL-E2-DIRECT-LEAF-20261123-001'
$AttemptId = 'TS-EE-004-ORCA-WSL-E2-DIRECT-LEAF-20261123-001-A001'
$Marker = 'TS_EE004_CHILD_JSON='
$ExpectedLinuxExit = 7
$ExpectedUid = 1000
$WorkRoot = 'C:\TS\station'
$OutputDir = 'C:\TS\station\ts-ee004-wsl-direct-leaf-20261123-001'

function Assert-ChildOutput {
    param([string]$Stdout,[int]$ExitCode)
    if ($ExitCode -ne $ExpectedLinuxExit) { throw 'WSL_EXIT_MISMATCH' }
    $lines = @($Stdout -split '\r?\n' | Where-Object { $_.StartsWith($Marker) })
    if ($lines.Count -ne 1) { throw 'CHILD_MARKER_COUNT_INVALID' }
    $child = ConvertFrom-Json -InputObject $lines[0].Substring($Marker.Length) -ErrorAction Stop
    if ($child.schema -ne 'ts-ee/wsl-child-marker/v0.1' -or
        $child.request_id -ne $RequestId -or $child.attempt -ne $AttemptId) {
        throw 'CHILD_IDENTITY_MISMATCH'
    }
    if ([int]$child.uid -ne $ExpectedUid) { throw 'CHILD_UID_MISMATCH' }
    if ([int]$child.pid -le 1 -or [int]$child.ppid -lt 1) {
        throw 'CHILD_PID_INVALID'
    }
    if ($child.pid_namespace -notmatch '^pid:\[[0-9]+\]$') {
        throw 'CHILD_NAMESPACE_INVALID'
    }
    if ([int]$child.intended_exit -ne $ExpectedLinuxExit) {
        throw 'CHILD_INTENDED_EXIT_MISMATCH'
    }
    return $child
}

function Write-ExclusiveUtf8 {
    param([string]$Path,[string]$Text)
    $bytes = [System.Text.UTF8Encoding]::new($false).GetBytes($Text)
    $stream = [System.IO.FileStream]::new(
        $Path,[System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::Write,[System.IO.FileShare]::None)
    try {
        $stream.Write($bytes,0,$bytes.Length)
        $stream.Flush($true)
    } finally {
        $stream.Dispose()
    }
}

if ($Mode -eq 'SelfTest') {
    $good = @{schema='ts-ee/wsl-child-marker/v0.1';
        request_id=$RequestId;attempt=$AttemptId;
        pid=101;ppid=1;uid=1000;pid_namespace='pid:[4026532211]';
        intended_exit=7}
    $text = $Marker+(ConvertTo-Json -InputObject $good -Compress)
    $parsed = Assert-ChildOutput -Stdout $text -ExitCode 7
    if ([int]$parsed.pid -ne 101) { throw 'POSITIVE_CASE_INVALID' }
    foreach ($negative in @('exit','request','uid','duplicate','namespace','pid')) {
        $copy = $good.Clone()
        $testText = $text
        $testExit = 7
        switch ($negative) {
            'exit' { $testExit = 0 }
            'request' { $copy.request_id='SPOOFED'; $testText=$Marker+(ConvertTo-Json $copy -Compress) }
            'uid' { $copy.uid=0; $testText=$Marker+(ConvertTo-Json $copy -Compress) }
            'duplicate' { $testText=$text+[Environment]::NewLine+$text }
            'namespace' { $copy.pid_namespace='NOT_ATTESTED'; $testText=$Marker+(ConvertTo-Json $copy -Compress) }
            'pid' { $copy.pid=0; $testText=$Marker+(ConvertTo-Json $copy -Compress) }
        }
        $denied=$false
        try { $null=Assert-ChildOutput -Stdout $testText -ExitCode $testExit }
        catch { $denied=$true }
        if (-not $denied) { throw ('NEGATIVE_NOT_REJECTED_'+$negative) }
    }
    Write-Output '{"source_only":"PASS_SIX_NEGATIVES","native_wsl":"NOT_RUN","Product_effect":"NONE"}'
    exit 0
}

# No host native code is executed by the source-only GitHub workflow.
if ($PSVersionTable.PSVersion.Major -lt 7) { throw 'PWSH7_REQUIRED' }
if ($env:COMPUTERNAME -ne 'DESKTOP-DJLBEQH') { throw 'WRONG_HOST' }
if ($ExpectedRunnerSha256 -notmatch '^[a-fA-F0-9]{64}$') { throw 'MISSING_CALLER_HASH' }
$actual = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $ExpectedRunnerSha256.ToLowerInvariant()) { throw 'SOURCE_HASH_MISMATCH' }
if (-not [IO.Directory]::Exists($WorkRoot)) { throw 'MISSING_WORKROOT' }
$root=Get-Item -LiteralPath $WorkRoot -Force
if (($root.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw 'UNSAFE_WORKROOT_REPARSE'
}
if ([IO.Directory]::Exists($OutputDir) -or [IO.File]::Exists($OutputDir)) {
    throw 'CREATE_ONLY_COLLISION'
}
$wsl=Join-Path $env:WINDIR 'System32\wsl.exe'
if (-not [IO.File]::Exists($wsl)) { throw 'WSL_BINARY_MISSING' }
if ((Get-AuthenticodeSignature -LiteralPath $wsl).Status.ToString() -ne 'Valid') {
    throw 'WSL_BINARY_SIGNATURE_UNVERIFIED'
}

# Fixed Python Linux argv: no external script input, shell, user command or secrets.
$linux = @'
import json
import os
import sys
import time
pid=os.getpid()
entry={
 "schema":"ts-ee/wsl-child-marker/v0.1",
 "request_id":"TS-EE-004-ORCA-WSL-E2-DIRECT-LEAF-20261123-001",
 "attempt":"TS-EE-004-ORCA-WSL-E2-DIRECT-LEAF-20261123-001-A001",
 "pid":pid,
 "ppid":os.getppid(),
 "uid":os.getuid(),
 "pid_namespace":os.readlink("/proc/%s/ns/pid" % pid),
 "intended_exit":7
}
print("TS_EE004_CHILD_JSON="+json.dumps(entry,sort_keys=True,separators=(",",":")),flush=True)
time.sleep(3)
sys.exit(7)
'@
# After this point the new attempt's result path is reserved; preserve incomplete on error.
[IO.Directory]::CreateDirectory($OutputDir) | Out-Null
Write-ExclusiveUtf8 -Path (Join-Path $OutputDir 'INCOMPLETE.txt') -Text 'UNTRUSTED_PARTIAL_OUTPUT'
$process=$null
try {
    $psi=[Diagnostics.ProcessStartInfo]::new()
    $psi.FileName=$wsl
    foreach($arg in @('-d','Ubuntu-24.04','--exec','/usr/bin/python3','-I','-c',$linux)) {
        [void]$psi.ArgumentList.Add($arg)
    }
    $psi.UseShellExecute=$false
    $psi.RedirectStandardOutput=$true
    $psi.RedirectStandardError=$true
    $process=[Diagnostics.Process]::new()
    $process.StartInfo=$psi
    if (-not $process.Start()) { throw 'WSL_START_FAILED' }
    $wslPid=$process.Id
    $stdoutTask=$process.StandardOutput.ReadToEndAsync()
    $stderrTask=$process.StandardError.ReadToEndAsync()
    $win=Get-CimInstance Win32_Process -Filter ("ProcessId = "+$wslPid)
    if ($null -eq $win -or $win.Name -ne 'wsl.exe' -or
        [int]$win.ParentProcessId -ne $PID) {
        throw 'WINDOWS_WSL_PARENT_MISMATCH'
    }
    if (-not $process.WaitForExit(20000)) {
        try {$process.Kill($true)} catch {}
        throw 'WSL_TIMEOUT_EFFECT_UNKNOWN'
    }
    $stdout=$stdoutTask.GetAwaiter().GetResult()
    $stderr=$stderrTask.GetAwaiter().GetResult()
    if ($stdout.Length -gt 8192 -or $stderr.Length -gt 8192) {
        throw 'CHILD_OUTPUT_TOO_LARGE'
    }
    $child=Assert-ChildOutput -Stdout $stdout -ExitCode $process.ExitCode
    Write-ExclusiveUtf8 -Path (Join-Path $OutputDir 'ORIGINAL_STDOUT.txt') -Text $stdout
    Write-ExclusiveUtf8 -Path (Join-Path $OutputDir 'ORIGINAL_STDERR.txt') -Text $stderr
    $receipt=@{
        schema='ts-ee/wsl-child-relay/v0.1';
        request_id=$RequestId;attempt=$AttemptId;
        windows_runner_pid=$PID;windows_wsl_pid=$wslPid;
        windows_wsl_parent_pid=[int]$win.ParentProcessId;
        windows_wsl_exit=$process.ExitCode;
        linux_child_pid=[int]$child.pid;linux_child_ppid=[int]$child.ppid;
        linux_child_uid=[int]$child.uid;
        linux_pid_namespace=[string]$child.pid_namespace;
        orca_native_identity='REQUIRES_SEPARATE_PROVIDER_JOIN';
        cross_kernel_pid_attestation='NOT_CRYPTOGRAPHIC';
        OriginalStdoutSha256=[Convert]::ToHexString(
            [Security.Cryptography.SHA256]::HashData(
                [Text.Encoding]::UTF8.GetBytes($stdout))).ToLowerInvariant();
        Product_effect='NONE';acceptance='NOT_AUTHORIZED'
    }
    Write-ExclusiveUtf8 -Path (Join-Path $OutputDir 'RESULT.json') -Text (
        (ConvertTo-Json -InputObject $receipt -Depth 5 -Compress)+[Environment]::NewLine)
    [IO.File]::Delete((Join-Path $OutputDir 'INCOMPLETE.txt'))
    Write-Output ('TS_EE004_WSL_RELAY_RESULT='+(ConvertTo-Json -InputObject $receipt -Depth 5 -Compress))
    exit 0
} catch {
    [Console]::Error.WriteLine(('TS_EE004_WSL_RELAY_BLOCKED='+$_.Exception.Message))
    # Incomplete is retained; no automatic retry, no Product mutations.
    exit 2
} finally {
    if ($null -ne $process) {$process.Dispose()}
}
