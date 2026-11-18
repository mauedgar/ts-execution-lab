# R007 B1 separated byte capture; NONPRODUCT source-only candidate.
# Does not select a provider, authorize inference, or modify Product.
Set-StrictMode -Version Latest

function Invoke-R007SeparatedCapture {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)][ValidatePattern('^[A-Za-z0-9][A-Za-z0-9_.-]{7,119}$')][string]$Attempt,
    [Parameter(Mandatory)][string]$CaptureRoot,
    [Parameter(Mandatory)][string]$Executable,
    [Parameter(Mandatory)][ValidatePattern('^[A-Fa-f0-9]{64}$')][string]$ExecutableSha256,
    [Parameter(Mandatory)][string[]]$ArgumentTokens,
    [switch]$SyntheticOnly
  )
  if ($PSVersionTable.PSVersion.Major -lt 7) { throw 'BLOCKED_REQUIRES_POWERSHELL7' }
  $expectedRoot = if ($SyntheticOnly) {
    Join-Path $env:TEMP 'TS-EE-R007-CAPTURE-SYNTHETIC-001'
  } else {
    Join-Path $env:LOCALAPPDATA 'TS-EE\OC2-R007\capture'
  }
  $canonical = [IO.Path]::GetFullPath($expectedRoot).TrimEnd([char]'\')
  $target = [IO.Path]::GetFullPath($CaptureRoot).TrimEnd([char]'\')
  if ($target -ine $canonical) { throw 'BLOCKED_CAPTURE_ROOT_OUTSIDE_ALLOWLIST' }
  if (-not [IO.File]::Exists($Executable)) { throw 'BLOCKED_EXECUTABLE_ABSENT' }
  $exeRealPath = [IO.Path]::GetFullPath($Executable)
  if ($exeRealPath -ine $Executable) { throw 'BLOCKED_EXECUTABLE_PATH_UNCANONICAL' }
  $exeActualSha = (Get-FileHash -LiteralPath $Executable -Algorithm SHA256).Hash
  if ($exeActualSha -ine $ExecutableSha256) { throw 'BLOCKED_EXECUTABLE_DIGEST_MISMATCH' }
  if (-not [IO.Directory]::Exists($target)) {
    [IO.Directory]::CreateDirectory($target) | Out-Null
  }
  $rootInfo = [IO.DirectoryInfo]::new($target)
  if (([int]$rootInfo.Attributes -band [int][IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw 'BLOCKED_CAPTURE_ROOT_REPARSE'
  }
  $runDir = Join-Path $target $Attempt
  if ([IO.Directory]::Exists($runDir) -or [IO.File]::Exists($runDir)) {
    throw 'BLOCKED_CAPTURE_ATTEMPT_COLLISION'
  }
  [IO.Directory]::CreateDirectory($runDir) | Out-Null
  $outPath = Join-Path $runDir 'ORIGINAL.stdout'
  $errPath = Join-Path $runDir 'ORIGINAL.stderr'
  $receiptPath = Join-Path $runDir 'CAPTURE.terminal.json'
  $out = $null
  $err = $null
  $process = $null
  $started = $false
  try {
    $out = [IO.FileStream]::new($outPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    $err = [IO.FileStream]::new($errPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    $psi = [Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = $exeRealPath
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    foreach ($token in $ArgumentTokens) {
      if ($null -eq $token -or $token.Contains([char]0)) { throw 'BLOCKED_NULL_ARGUMENT_TOKEN' }
      [void]$psi.ArgumentList.Add($token)
    }
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $psi
    if (-not $process.Start()) { throw 'UNKNOWN_NATIVE_START' }
    $started = $true
    $stdoutCopy = $process.StandardOutput.BaseStream.CopyToAsync($out)
    $stderrCopy = $process.StandardError.BaseStream.CopyToAsync($err)
    [Threading.Tasks.Task]::WhenAll([Threading.Tasks.Task[]]@($stdoutCopy,$stderrCopy)).GetAwaiter().GetResult()
    $process.WaitForExit()
    $code = $process.ExitCode
    $pidNative = $process.Id
    $out.Flush($true)
    $err.Flush($true)
    $out.Dispose(); $out = $null
    $err.Dispose(); $err = $null
    $stdoutFile = [IO.FileInfo]::new($outPath)
    $stderrFile = [IO.FileInfo]::new($errPath)
    $receipt = @{
      schema = 'ts-ee-r007-separated-capture/v1'
      attempt = $Attempt
      original_stdout_bytes = [long]$stdoutFile.Length
      original_stderr_bytes = [long]$stderrFile.Length
      original_stdout_sha256 = (Get-FileHash -LiteralPath $outPath -Algorithm SHA256).Hash.ToLowerInvariant()
      original_stderr_sha256 = (Get-FileHash -LiteralPath $errPath -Algorithm SHA256).Hash.ToLowerInvariant()
      executable_sha256 = $exeActualSha.ToLowerInvariant()
      native_process_id = $pidNative
      native_exit_code = $code
      effect_state = 'CONFIRMED_EXECUTED'
      semantic_verdict = 'NOT_ASSESSED'
      structural_jsonl_verdict = 'NOT_ASSESSED'
      synthetic_only = [bool]$SyntheticOnly
      Product_effect = 'NONE'
    }
    $bytes = [Text.Encoding]::UTF8.GetBytes(($receipt | ConvertTo-Json -Compress) + [Environment]::NewLine)
    $fs = [IO.FileStream]::new($receiptPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    try { $fs.Write($bytes,0,$bytes.Length); $fs.Flush($true) }
    finally { $fs.Dispose() }
    return $receipt
  }
  catch {
    # If native launch occurred, preserve output and UNKNOWN; never retry/clean up.
    if ($started) { throw ('UNKNOWN_CAPTURE_POST_NATIVE_EFFECT: ' + $_.Exception.Message) }
    throw
  }
  finally {
    if ($null -ne $out) { $out.Dispose() }
    if ($null -ne $err) { $err.Dispose() }
    if ($null -ne $process) { $process.Dispose() }
  }
}
