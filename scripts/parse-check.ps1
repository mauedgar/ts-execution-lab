param(
  [Parameter(Mandatory = $true)][string]$ScriptPath,
  [switch]$ReviewerDispatch,
  [string]$ExpectedGitBlob = '',
  [string]$ModelBinding = '',
  [string]$V2Executable = '',
  [string]$ExpectedV2Sha256 = '',
  [string]$ExpectedV2Version = '2.0.26',
  [switch]$StaticOnly
)
# Pre-dispatch source qualification only; never launches a reviewer.
# Backward-compatible default mode: existing syntax-only parse-check.
$ErrorActionPreference = 'Stop'
$errors = $null
$tokens = $null
$findings = New-Object 'System.Collections.Generic.List[string]'
$parseOk = $false
$nativeV2Checked = $false
$verifiedBlob = ''
try {
  $file = Get-Item -LiteralPath $ScriptPath -ErrorAction Stop
  if (-not ($file -is [IO.FileInfo])) { throw 'SOURCE_NOT_REGULAR_FILE' }
  [System.Management.Automation.Language.Parser]::ParseFile($file.FullName, [ref]$tokens, [ref]$errors) | Out-Null
  $parseOk = ($null -ne $errors -and $errors.Count -eq 0)
  if (-not $parseOk) {
    foreach ($item in $errors) { $findings.Add(('PARSER_ERROR:' + $item.Message)) }
  }

  if ($ReviewerDispatch) {
    if ($ExpectedGitBlob -notmatch '^[0-9a-fA-F]{40}$') {
      $findings.Add('EXPECTED_SOURCE_GIT_BLOB_REQUIRED')
    } else {
      $gitOut = & git.exe hash-object -- $file.FullName 2>&1
      if ($LASTEXITCODE -ne 0) {
        $findings.Add('SOURCE_GIT_HASH_UNAVAILABLE')
      } else {
        $verifiedBlob = (($gitOut | Out-String).Trim()).ToLowerInvariant()
        if ($verifiedBlob -ne $ExpectedGitBlob.ToLowerInvariant()) { $findings.Add('SOURCE_GIT_BLOB_MISMATCH') }
      }
    }

    # The caller must select a qualified OpenAI GPT, with sufficient non-low reasoning for semantic review.
    # This is syntactic qualification only, NOT proof of provider model availability.
    if ($ModelBinding -notmatch '^openai/gpt-[a-zA-Z0-9][a-zA-Z0-9._-]*#(medium|high|extra-high)$') {
      $findings.Add('REVIEWER_OPENAI_GPT_COMPETENT_EFFORT_BINDING_REQUIRED')
    }
    $source = [IO.File]::ReadAllText($file.FullName)
    $checks = @(
      @{ id = 'FOREGROUND_WAIT_FOR_EXIT'; rx = '(?i)\.\s*WaitForExit\s*\(' },
      @{ id = 'FOREGROUND_WAIT_PROCESS'; rx = '(?i)\bWait-Process\b' },
      @{ id = 'FOREGROUND_WAIT_JOB'; rx = '(?i)\bWait-Job\b' },
      @{ id = 'FOREGROUND_START_PROCESS_WAIT'; rx = '(?i)\bStart-Process\b[^\r\n]*\s-Wait\b' },
      @{ id = 'FOREGROUND_RECEIVE_JOB_WAIT'; rx = '(?i)\bReceive-Job\b[^\r\n]*\s-Wait\b' },
      @{ id = 'FOREGROUND_SYNCHRONOUS_STREAM_READ'; rx = '(?i)\.\s*ReadToEnd\s*\(' },
      @{ id = 'FOREGROUND_SYNC_ASYNC_GETRESULT'; rx = '(?i)\.\s*GetAwaiter\s*\(\s*\)\s*\.\s*GetResult\s*\(' },
      @{ id = 'LOCAL_SLEEP_AS_WEB_WAIT'; rx = '(?i)\bStart-Sleep\b|\[Threading\.Thread\]\s*::\s*Sleep\s*\(' },
      @{ id = 'FORCED_TERMINATION'; rx = '(?i)\btaskkill(?:\.exe)?\b|\bStop-Process\b|\bStop-Job\b|\.\s*Kill\s*\(' },
      @{ id = 'LEGACY_OPENCODE_V1_BINDING'; rx = '(?i)(?:\bopencode\.cmd\b|opencode-v1|1\.18\.35|\\npm\\opencode(?:\.cmd)?)' },
      @{ id = 'UNDERPOWERED_HARDCODED_REVIEWER'; rx = '(?i)\bopenai/gpt-[a-zA-Z0-9._-]+#low\b' }
    )
    foreach ($check in $checks) {
      if ([regex]::IsMatch($source, $check.rx)) { $findings.Add($check.id) }
    }

    # A reviewer launcher must return a start receipt before any long-running provider work;
    # the terminal receipt is generated outside that launcher and joined natively.
    if ($source -notmatch '(?i)START_RECEIPT\.json') { $findings.Add('DURABLE_START_RECEIPT_NOT_DECLARED') }
    if ($source -notmatch '(?i)ExecutionAttempt') { $findings.Add('EXECUTION_ATTEMPT_BINDING_NOT_DECLARED') }

    if (-not $StaticOnly) {
      if (-not $V2Executable -or -not [IO.File]::Exists($V2Executable)) {
        $findings.Add('NATIVE_V2_EXECUTABLE_MISSING')
      } elseif ($ExpectedV2Sha256 -notmatch '^[0-9a-fA-F]{64}$') {
        $findings.Add('EXPECTED_V2_EXE_SHA256_REQUIRED')
      } else {
        $exe = Get-Item -LiteralPath $V2Executable
        if ($exe.FullName -notmatch '(?i)\\opencode-v2\\' -or $exe.FullName -notmatch [regex]::Escape(('\' + $ExpectedV2Version + '\'))) {
          $findings.Add('V2_EXECUTABLE_PATH_OR_VERSION_MISMATCH')
        } else {
          $hash = (Get-FileHash -LiteralPath $exe.FullName -Algorithm SHA256).Hash
          if ($hash -ne $ExpectedV2Sha256.ToUpperInvariant()) {
            $findings.Add('V2_EXECUTABLE_BYTES_MISMATCH')
          } else {
            $ver = & $exe.FullName --version 2>&1
            if ($LASTEXITCODE -ne 0 -or ($ver | Out-String) -notmatch [regex]::Escape($ExpectedV2Version)) {
              $findings.Add('V2_NATIVE_VERSION_MISMATCH')
            } else {
              $nativeV2Checked = $true
            }
          }
        }
      }
    }
  }
} catch {
  $findings.Add(('PREFLIGHT_EXCEPTION:' + $_.Exception.Message))
}
$allowed = $parseOk -and $findings.Count -eq 0
$result = [ordered]@{
  status = if ($allowed) { if ($ReviewerDispatch -and $StaticOnly) { 'PASS_STATIC_SOURCE_ONLY' } elseif ($ReviewerDispatch) { 'PASS_V2_PREDISPATCH_SOURCE_AND_BINARY' } else { 'PASS_SYNTAX' } } else { 'BLOCKED' }
  mode = if ($ReviewerDispatch) { 'REVIEWER_DISPATCH_PRECHECK' } else { 'SYNTAX_ONLY' }
  source = $ScriptPath
  expected_git_blob = if ($ReviewerDispatch) { $ExpectedGitBlob } else { $null }
  observed_git_blob = $verifiedBlob
  parse_ok = $parseOk
  source_errors = @($findings.ToArray())
  model_binding = if ($ReviewerDispatch) { $ModelBinding } else { $null }
  native_v2_checked = $nativeV2Checked
  model_provider_auth_checked = $false
  model_semantic_competence_checked = $false
  user_authorization_checked = $false
  Product_effect = 'NONE'
  reviewer_launched = $false
}
$result | ConvertTo-Json -Depth 8 -Compress
if (-not $allowed) { exit 1 }
