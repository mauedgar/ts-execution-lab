# R007_B1 — Single-host, same-user, cross-worktree attempt admission helper. NONPRODUCT.
# Source-only until qualified. This helper DOES NOT launch a provider or modify Product.
Set-StrictMode -Version Latest

function Invoke-R007LedgerGate {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)][ValidatePattern('^[A-Za-z0-9][A-Za-z0-9_.-]{7,119}$')][string]$Attempt,
    [Parameter(Mandatory)][ValidatePattern('^[a-f0-9]{64}$')][string]$CarrierSha256,
    [Parameter(Mandatory)][ValidatePattern('^[a-f0-9]{40}$')][string]$SubjectHead,
    [Parameter(Mandatory)][string]$LedgerRoot,
    [Parameter(Mandatory)][scriptblock]$BoundedOperation,
    [switch]$SyntheticOnly
  )

  # Caller must pre-qualify a host-wide trusted directory before non-synthetic use.
  $expectedRoot = Join-Path $env:LOCALAPPDATA 'TS-EE\OC2-R007\ledger'
  $testBase = Join-Path $env:TEMP 'TS-EE-R007-LEDGER-SYNTHETIC-001'
  $target = [IO.Path]::GetFullPath($LedgerRoot).TrimEnd([char]'\')
  $canonical = [IO.Path]::GetFullPath($expectedRoot).TrimEnd([char]'\')
  $testCanonical = [IO.Path]::GetFullPath($testBase).TrimEnd([char]'\')
  if ($SyntheticOnly) {
    if ($target -ine $testCanonical) { throw 'BLOCKED_SYNTHETIC_LEDGER_ROOT' }
  } elseif ($target -ine $canonical) { throw 'BLOCKED_LEDGER_ROOT' }

  $mutex = [Threading.Mutex]::new($false, 'Local\TS_EE_OC2_R007_SINGLE_HOST_V1')
  $lockHeld = $false
  $effectPossible = $false
  try {
    try { $lockHeld = $mutex.WaitOne(0) }
    catch [Threading.AbandonedMutexException] { throw 'BLOCKED_ABANDONED_SLOT_UNKNOWN' }
    if (-not $lockHeld) { throw 'BLOCKED_SLOT_BUSY' }

    if (-not [IO.Directory]::Exists($target)) {
      [IO.Directory]::CreateDirectory($target) | Out-Null
    }
    $info = [IO.DirectoryInfo]::new($target)
    if (([int]$info.Attributes -band [int][IO.FileAttributes]::ReparsePoint) -ne 0) {
      throw 'BLOCKED_LEDGER_ROOT_REPARSE'
    }
    $claims = @([IO.Directory]::GetFiles($target, '*.claim.json', [IO.SearchOption]::TopDirectoryOnly))
    foreach ($claim in $claims) {
      $basename = [IO.Path]::GetFileName($claim)
      $done = Join-Path $target ($basename.Substring(0, $basename.Length - '.claim.json'.Length) + '.terminal.json')
      if (-not [IO.File]::Exists($done)) { throw 'BLOCKED_PRIOR_UNKNOWN_EFFECT' }
    }

    $claimPath = Join-Path $target ($Attempt + '.claim.json')
    if ([IO.File]::Exists($claimPath)) { throw 'BLOCKED_ATTEMPT_ALREADY_CLAIMED' }
    $terminalPath = Join-Path $target ($Attempt + '.terminal.json')
    if ([IO.File]::Exists($terminalPath)) { throw 'BLOCKED_TERMINAL_COLLISION' }
    $claim = @{
      schema='ts-ee-r007-attempt-claim/v1'
      attempt=$Attempt
      subject_head=$SubjectHead
      carrier_sha256=$CarrierSha256
      effect_state='UNKNOWN_UNTIL_TERMINAL'
      synthetic_only=[bool]$SyntheticOnly
      Product_effect='NONE'
    } | ConvertTo-Json -Compress
    $bytes = [Text.Encoding]::UTF8.GetBytes($claim + [Environment]::NewLine)
    try {
      # Durable claim precedes every possible model effect. CreateNew excludes replay.
      $effectPossible = $true
      $file = [IO.FileStream]::new($claimPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
      try { $file.Write($bytes,0,$bytes.Length);$file.Flush($true) }
      finally { $file.Dispose() }
    } catch { throw 'UNKNOWN_CLAIM_WRITE_POSTCONDITION' }

    $outcome = & $BoundedOperation
    # Only a complete bounded operation may create the terminal receipt.
    if ($null -eq $outcome -or $outcome -notin @('CONFIRMED','NONE')) {
      throw 'UNKNOWN_OPERATION_RETURN_NO_TERMINAL'
    }
    $terminal = @{
      schema='ts-ee-r007-attempt-terminal/v1'
      attempt=$Attempt
      subject_head=$SubjectHead
      carrier_sha256=$CarrierSha256
      effect_state=$outcome
      synthetic_only=[bool]$SyntheticOnly
      Product_effect='NONE'
    } | ConvertTo-Json -Compress
    $receiptBytes=[Text.Encoding]::UTF8.GetBytes($terminal + [Environment]::NewLine)
    try {
      $receipt=[IO.FileStream]::new($terminalPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
      try {$receipt.Write($receiptBytes,0,$receiptBytes.Length);$receipt.Flush($true)}
      finally {$receipt.Dispose()}
    } catch { throw 'UNKNOWN_TERMINAL_WRITE_POSTCONDITION' }
    Write-Output ("R007_LEDGER_TERMINAL;ATTEMPT=" + $Attempt + ";EFFECT=" + $outcome)
  } finally {
    if ($lockHeld) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
  }
}
