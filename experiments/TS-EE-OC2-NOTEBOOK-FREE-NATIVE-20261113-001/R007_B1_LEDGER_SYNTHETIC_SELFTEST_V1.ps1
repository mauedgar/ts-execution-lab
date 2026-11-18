# Run only in isolated Orca Experiment terminal. Invoke source module in same scope before this.
# One-shot source-only synthetic test. No OpenCode2, provider, network or Product.
$ErrorActionPreference='Stop'
$subject='2c58013476d09eb63839f8ebb604c1954473f695'
$carrier=('a'*64)
$root=Join-Path $env:TEMP 'TS-EE-R007-LEDGER-SYNTHETIC-001'
Write-Output 'R007_LEDGER_TEST_BEGIN'
if (Test-Path -LiteralPath $root) { throw 'BLOCKED_SYNTHETIC_TEST_PREVIOUS_EFFECT' }
$one='R007-B1-SYNTHETIC-A001'
$two='R007-B1-SYNTHETIC-A002'
$three='R007-B1-SYNTHETIC-A003'
$four='R007-B1-SYNTHETIC-A004'
$first=@(Invoke-R007LedgerGate -Attempt $one -CarrierSha256 $carrier -SubjectHead $subject -LedgerRoot $root -SyntheticOnly -BoundedOperation { 'NONE' })
if(@($first | Where-Object {$_ -match 'EFFECT=NONE'}).Count -ne 1){throw 'BLOCKED_FIRST_CLAIM_RESULT'}
Write-Output 'R007_LEDGER_TEST_FIRST_PASS'
$blocked=$false
try {Invoke-R007LedgerGate -Attempt $one -CarrierSha256 $carrier -SubjectHead $subject -LedgerRoot $root -SyntheticOnly -BoundedOperation { throw 'UNEXPECTED_DUPLICATE_OPERATION' } | Out-Null}
catch{ if($_.Exception.Message -eq 'BLOCKED_ATTEMPT_ALREADY_CLAIMED'){$blocked=$true}else{throw}}
if(-not $blocked){throw 'BLOCKED_DUPLICATE_TEST_FALSE_PASS'}
Write-Output 'R007_LEDGER_TEST_DUPLICATE_BLOCKED_PASS'
$second=@(Invoke-R007LedgerGate -Attempt $two -CarrierSha256 $carrier -SubjectHead $subject -LedgerRoot $root -SyntheticOnly -BoundedOperation { 'CONFIRMED' })
if(@($second | Where-Object {$_ -match 'EFFECT=CONFIRMED'}).Count -ne 1){throw 'BLOCKED_SECOND_CLAIM_RESULT'}
Write-Output 'R007_LEDGER_TEST_SECOND_PASS'
$unknown=$false
try {Invoke-R007LedgerGate -Attempt $three -CarrierSha256 $carrier -SubjectHead $subject -LedgerRoot $root -SyntheticOnly -BoundedOperation { throw 'SYNTHETIC_OPERATION_UNKNOWN' } | Out-Null}
catch{if($_.Exception.Message -eq 'SYNTHETIC_OPERATION_UNKNOWN'){$unknown=$true}else{throw}}
if(-not $unknown){throw 'BLOCKED_UNKNOWN_TEST_MISSING'}
$future=$false
try {Invoke-R007LedgerGate -Attempt $four -CarrierSha256 $carrier -SubjectHead $subject -LedgerRoot $root -SyntheticOnly -BoundedOperation { throw 'UNEXPECTED_FUTURE_OPERATION' } | Out-Null}
catch{if($_.Exception.Message -eq 'BLOCKED_PRIOR_UNKNOWN_EFFECT'){$future=$true}else{throw}}
if(-not $future){throw 'BLOCKED_FUTURE_UNKNOWN_FENCE'}
if(-not (Test-Path (Join-Path $root ($three+'.claim.json')))){throw 'BLOCKED_UNKNOWN_CLAIM_MISSING'}
if(Test-Path (Join-Path $root ($three+'.terminal.json'))){throw 'BLOCKED_UNKNOWN_TERMINAL_WRITTEN'}
if(Test-Path (Join-Path $root ($four+'.claim.json'))){throw 'BLOCKED_UNEXPECTED_FUTURE_CLAIM'}
Write-Output 'R007_LEDGER_TEST_UNKNOWN_FENCE_PASS'
Write-Output 'R007_LEDGER_TEST_TERMINAL_4_OF_4_PASS_NO_MODEL'
