param([string]$WorkRoot = 'C:\Temp\TS-EE-V2-REVIEWER-PREFLIGHT-QUALIFICATION-20261011-001')
$ErrorActionPreference = 'Stop'
if ([IO.Directory]::Exists($WorkRoot)) { throw 'BLOCKED_QUALIFICATION_WORKROOT_ALREADY_EXISTS_NO_REPLAY' }
[IO.Directory]::CreateDirectory($WorkRoot) | Out-Null
$checked = New-Object 'System.Collections.Generic.List[object]'
$testCount = 0
$passedCount = 0
$failures = New-Object 'System.Collections.Generic.List[string]'
$checkerPath = Join-Path $WorkRoot 'parse-check.ps1'
$shaExpected = 'c6da1e98197e8c53cfee64429d4664955a73161a'
$nativeExe = 'C:\Tools\opencode-v2\2.0.26\node_modules\@opencode\cli\bin\opencode.exe'
$nativeSha = 'E13E57A7F6B7ABDDEC887E0B2D912D22484077C50DFF5BED4F3199BCF63B6088'
function Get-PinnedFile {
  param([string]$Repository,[string]$Revision,[string]$File,[string]$ExpectedBlob,[string]$Destination)
  $endpoint = 'repos/' + $Repository + '/contents/' + $File + '?ref=' + $Revision
  $encoded = @(& gh.exe api $endpoint --jq .content)
  if ($LASTEXITCODE -ne 0 -or $encoded.Count -eq 0) { throw ('SOURCE_FETCH_FAILED:' + $File) }
  $bytes = [Convert]::FromBase64String(($encoded -join '').Trim())
  [IO.File]::WriteAllBytes($Destination, $bytes)
  $blob = ((& git.exe hash-object -- $Destination | Out-String).Trim()).ToLowerInvariant()
  if ($LASTEXITCODE -ne 0 -or $blob -ne $ExpectedBlob) {
    throw ('SOURCE_EXACT_BLOB_DRIFT:' + $File + ':' + $blob)
  }
  return $blob
}
function Assert-Case {
  param([string]$Label,[string]$Source,[string]$ExpectedBlob,[bool]$Review,[string]$Model,[bool]$StaticOnly,[string]$ExpectedDecision)
  $scriptArgs = @('-NoLogo','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',$checkerPath,'-ScriptPath',$Source)
  if ($Review) {
    $scriptArgs += @('-ReviewerDispatch','-ExpectedGitBlob',$ExpectedBlob,'-ModelBinding',$Model)
    if ($StaticOnly) {
      $scriptArgs += '-StaticOnly'
    } else {
      $scriptArgs += @('-V2Executable',$nativeExe,'-ExpectedV2Sha256',$nativeSha,'-ExpectedV2Version','2.0.26')
    }
  }
  $raw = @(& pwsh.exe @scriptArgs 2>&1)
  $exitCode = $LASTEXITCODE
  $result = $null
  try {
    $result = ($raw | Where-Object { $_ -match '^\{' } | Select-Object -Last 1 | Out-String).Trim() | ConvertFrom-Json -ErrorAction Stop
  } catch {
    throw ('PREFLIGHT_OUTPUT_NOT_JSON:' + $Label + ':' + (($raw | Out-String).Trim()))
  }
  $script:testCount++
  $ok = ($result.status -eq $ExpectedDecision) -and (($ExpectedDecision -eq 'BLOCKED' -and $exitCode -ne 0) -or ($ExpectedDecision -ne 'BLOCKED' -and $exitCode -eq 0))
  if ($ok) { $script:passedCount++ } else { $failures.Add(('FAIL:' + $Label + ':status=' + $result.status + ':exit=' + $exitCode)) }
  $checked.Add([ordered]@{ label=$Label;status=$result.status;exit_code=$exitCode;ok=$ok;finding_ids=@($result.source_errors);source=$Source;native_v2_checked=$result.native_v2_checked })
}
try {
  $sources = @(
    @{ name='checker'; repo='mauedgar/ts-execution-lab'; rev='f6d9116eb34a8c9e46bd72d6f8dc1a21392103fb'; path='scripts/parse-check.ps1';sha=$shaExpected;dest=$checkerPath },
    @{ name='beta_bad';repo='mauedgar/ts-execution-transport';rev='9ba8679b7349ebe93c1a535b4f8e5aa7375213a3';path='requests/TECNOTRON-BETA-ULC-OP02-FRESH-IR-2026-10-11-001/DISPATCH_FRESH_READONLY_REVIEW_001.ps1';sha='37b929603e0ed68cd96d9b3e00675f568a55b1c5';dest=(Join-Path $WorkRoot 'beta-bad.ps1')},
    @{ name='legacy_bad';repo='mauedgar/ts-execution-transport';rev='508a7b66e654ae27c5cbc9cbedab013cd891a4c3';path='requests/TECNOTRON-REVIEW-TXT-CARRIER-ADOPTION-IR-001/LAUNCH_FRESH_REVIEW.ps1';sha='67ae29df6d48d16d3792a2ffae922b4db6747238';dest=(Join-Path $WorkRoot 'legacy-bad.ps1')},
    @{ name='lab_benign';repo='mauedgar/ts-execution-lab';rev='50d94969e90360db8c0cc3ffc66ebbd96d4a2990';path='scripts/launch-worker.ps1';sha='f73cd780c492bbb009f6ceaf6924d1e95174ccc4';dest=(Join-Path $WorkRoot 'benign.ps1')}
  )
  foreach ($src in $sources) {
    $null = Get-PinnedFile -Repository $src.repo -Revision $src.rev -File $src.path -ExpectedBlob $src.sha -Destination $src.dest
  }
  $safe = Join-Path $WorkRoot 'safe-test-only.ps1'
  $safeText = @'
param()
# Fixture only: no reviewer invocation; static guard cannot prove runtime correctness.
$startReceipt = 'START_RECEIPT.json'
$operation = 'ExecutionAttempt'
Write-Output $startReceipt
Write-Output $operation
'@
  [IO.File]::WriteAllText($safe,$safeText,[Text.UTF8Encoding]::new($false))
  $safeBlob = ((& git.exe hash-object -- $safe | Out-String).Trim()).ToLowerInvariant()
  Assert-Case -Label 'LEGACY_DEFAULT_SYNTAX_BENIGN' -Source $sources[3].dest -ExpectedBlob $sources[3].sha -Review:$false -Model '' -StaticOnly:$true -ExpectedDecision 'PASS_SYNTAX'
  Assert-Case -Label 'BETA_OP02_BLOCKED_WAIT' -Source $sources[1].dest -ExpectedBlob $sources[1].sha -Review:$true -Model 'openai/gpt-6#medium' -StaticOnly:$true -ExpectedDecision 'BLOCKED'
  Assert-Case -Label 'LEGACY_LAUNCHER_WAIT_AND_KILL_BLOCKED' -Source $sources[2].dest -ExpectedBlob $sources[2].sha -Review:$true -Model 'openai/gpt-6#medium' -StaticOnly:$true -ExpectedDecision 'BLOCKED'
  Assert-Case -Label 'MODEL_LOW_DEFAULT_BLOCKED' -Source $safe -ExpectedBlob $safeBlob -Review:$true -Model 'openai/gpt-5.6-luna#low' -StaticOnly:$true -ExpectedDecision 'BLOCKED'
  Assert-Case -Label 'SAFE_SOURCE_STATIC_ONLY' -Source $safe -ExpectedBlob $safeBlob -Review:$true -Model 'openai/gpt-6#medium' -StaticOnly:$true -ExpectedDecision 'PASS_STATIC_SOURCE_ONLY'
  Assert-Case -Label 'PINNED_NATIVE_V2_SOURCE_ONLY' -Source $safe -ExpectedBlob $safeBlob -Review:$true -Model 'openai/gpt-6#medium' -StaticOnly:$false -ExpectedDecision 'PASS_V2_PREDISPATCH_SOURCE_AND_BINARY'
  $summary = [ordered]@{
    qualification_id='TS-EE-V2-REVIEWER-PREFLIGHT-QUALIFICATION-20261011-001'
    status=if ($failures.Count -eq 0) {'PASS_BOUNDED'} else {'FAIL'}
    total=$testCount;passed=$passedCount;failed=$failures.Count
    cases=@($checked.ToArray())
    failures=@($failures.ToArray())
    checker_expected_blob=$shaExpected
    native_exe=$nativeExe
    native_sha256=$nativeSha
    current_auth_tested=$false
    models_provider_catalog_tested=$false
    model_call_count=0
    review_dispatched=$false
    Product_effect='NONE'
    scope='source preflight + installed v2 binary; no independent review or credential guarantee'
  }
  $output = Join-Path $WorkRoot 'QUALIFICATION_RESULT.json'
  [IO.File]::WriteAllText($output,($summary | ConvertTo-Json -Depth 12),[Text.UTF8Encoding]::new($false))
  $summary | ConvertTo-Json -Depth 12 -Compress
  if ($failures.Count -gt 0) { exit 17 }
} catch {
  $status = [ordered]@{status='BLOCKED_PRE_EFFECT';reason=$_.Exception.Message;Product_effect='NONE';model_call_count=0;original_unknown_untouched=$true}
  $status | ConvertTo-Json -Compress
  exit 20
}
