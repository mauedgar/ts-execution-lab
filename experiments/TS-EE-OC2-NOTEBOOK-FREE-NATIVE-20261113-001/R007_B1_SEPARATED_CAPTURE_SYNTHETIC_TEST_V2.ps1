# R007 B1 separated-capture synthetic contract test V2 (WindowsApps alias repair). No provider/model/tool usage.
$ErrorActionPreference='Stop'
if ($PSVersionTable.PSVersion.Major -lt 7) { throw 'BLOCKED_SELFTEST_REQUIRES_PWSH7' }
$root=Join-Path $env:TEMP 'TS-EE-R007-CAPTURE-SYNTHETIC-001'
if (Test-Path -LiteralPath $root) { throw 'BLOCKED_PREVIOUS_CAPTURE_SYNTHETIC_EFFECT' }
$exe=Join-Path $PSHOME 'pwsh.exe'
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw 'BLOCKED_REAL_PWSH_EXECUTABLE_MISSING' }
$hash=(Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash
$good='R007-B1-CAPTURE-TEST-A001'
$bad='R007-B1-CAPTURE-TEST-A002'
Write-Output 'R007_CAPTURE_TEST_BEGIN'
$code1='[Console]::OutputEncoding=[Text.Encoding]::UTF8;[Console]::Out.Write("{""type"":""step_finish""}"+[char]10);[Console]::Error.Write("synthetic-warning"+[char]10);exit 0'
$a=Invoke-R007SeparatedCapture -Attempt $good -CaptureRoot $root -Executable $exe -ExecutableSha256 $hash -ArgumentTokens @('-NoProfile','-NonInteractive','-Command',$code1) -SyntheticOnly
if ($a.native_exit_code -ne 0 -or $a.original_stdout_bytes -le 0 -or $a.original_stderr_bytes -le 0 -or $a.effect_state -cne 'CONFIRMED_EXECUTED') { throw 'BLOCKED_CAPTURE_TEST_A001_RESULT' }
if (-not (Test-Path (Join-Path (Join-Path $root $good) 'CAPTURE.terminal.json'))) { throw 'BLOCKED_CAPTURE_TEST_A001_RECEIPT' }
Write-Output ('R007_CAPTURE_TEST_A001_PASS;STDOUT_BYTES='+$a.original_stdout_bytes+';STDERR_BYTES='+$a.original_stderr_bytes)
$code2='[Console]::Out.Write("synthetic-error-exit"+[char]10);exit 7'
$b=Invoke-R007SeparatedCapture -Attempt $bad -CaptureRoot $root -Executable $exe -ExecutableSha256 $hash -ArgumentTokens @('-NoProfile','-NonInteractive','-Command',$code2) -SyntheticOnly
if ($b.native_exit_code -ne 7 -or $b.effect_state -cne 'CONFIRMED_EXECUTED') { throw 'BLOCKED_CAPTURE_TEST_A002_EXIT_RESULT' }
Write-Output 'R007_CAPTURE_TEST_A002_NONZERO_EXIT_PASS'
$blocked=$false
try {Invoke-R007SeparatedCapture -Attempt $good -CaptureRoot $root -Executable $exe -ExecutableSha256 $hash -ArgumentTokens @('-NoProfile','-NonInteractive','-Command','exit 0') -SyntheticOnly | Out-Null}
catch {if($_.Exception.Message -eq 'BLOCKED_CAPTURE_ATTEMPT_COLLISION'){$blocked=$true}else{throw}}
if (-not $blocked) { throw 'BLOCKED_CAPTURE_TEST_DUPLICATE_UNGUARDED' }
Write-Output 'R007_CAPTURE_TEST_DUPLICATE_BLOCKED_PASS'
Write-Output 'R007_CAPTURE_TEST_TERMINAL_3_OF_3_PASS_NO_MODEL'
