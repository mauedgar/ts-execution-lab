# Continuation 003, verified recovery of original failed attempt without replay.
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$Id='TS-BEADS-CONTINUITY-PILOT-20261013-001'
$Attempt='BEADS-LOCAL-TRIAL-20261013-003'
$HomeDir=Join-Path $env:LOCALAPPDATA "TS-Experiments\$Id"
$B=Join-Path $HomeDir 'bin\bd.exe'
$env:BEADS_DIR=Join-Path $HomeDir 'data\.beads'
$Out=Join-Path $HomeDir 'continuation-003-result.json'
$Stage='PREFLIGHT'
$Receipt=[ordered]@{contract='ts-beads-continuation/v0-experimental';pilot=$Id;execution_attempt=$Attempt;status='UNKNOWN';stage=$Stage;host=$env:COMPUTERNAME;subject='dist-bra';handoff=$null;source_failed_attempt='BEADS-LOCAL-TRIAL-20261013-002';product_authority='NONE';checks=@();error=$null;started_utc=(Get-Date).ToUniversalTime().ToString('o')}
function Assert([string]$Code,[bool]$Okay,[string]$Context) {
 $Receipt.checks += [ordered]@{code=$Code;pass=$Okay;context=$Context}
 if(-not $Okay){throw "GUARD_OR_ASSERTION:${Code}:${Context}"}
}
function Bd([string[]]$Arguments) {
 $v = & $B @Arguments 2>&1
 if($LASTEXITCODE -ne 0) {throw ('BD_FAIL '+($Arguments -join ' ')+': '+($v -join ' '))}
 return ($v|Out-String).Trim()
}
function BdJson([string[]]$Arguments) {
 $s=Bd -Arguments $Arguments
 $m=[regex]::Match($s,'(?m)^[ \t]*(?:\[|\{)')
 if(-not $m.Success){throw ('BD_JSON_NOT_FOUND: '+$s.Substring(0,[Math]::Min(150,$s.Length)))}
 return ($s.Substring($m.Index)|ConvertFrom-Json)
}
try {
 Assert 'RUNNER_EXISTS' (Test-Path -LiteralPath $B) 'Existing isolated binary required'
 Assert 'ORIGINAL_FAIL_RESULT' (Test-Path -LiteralPath (Join-Path $HomeDir 'result.json')) 'Original result must be preserved'
 $old=Get-Content -LiteralPath (Join-Path $HomeDir 'result.json') -Raw | ConvertFrom-Json
 Assert 'ORIGINAL_IDENTITY' ($old.execution_attempt -eq 'BEADS-LOCAL-TRIAL-20261013-002' -and $old.status -eq 'FAIL' -and $old.phase -eq 'CREATE_OBLIGATIONS') 'Must reconcile original failing attempt exactly'
 $actual=(Get-FileHash -LiteralPath $B -Algorithm SHA256).Hash.ToLowerInvariant()
 Assert 'BINARY_PIN' ($actual -eq $old.bd_binary_sha256) 'Installed binary must match original downloaded release'
 $m=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifest-003.json') -Raw | ConvertFrom-Json
 $runnerHash=(Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant()
 $verifyHash=(Get-FileHash -LiteralPath (Join-Path $PSScriptRoot 'verify-003.ps1') -Algorithm SHA256).Hash.ToLowerInvariant()
 Assert 'RUNNER_PIN' ($runnerHash -eq $m.runner_sha256 -and $verifyHash -eq $m.verify_sha256 -and $m.attempt -eq $Attempt) 'Immutable scripts and attempt'
 Assert 'NO_PREVIOUS_CONTINUATION' (-not (Test-Path -LiteralPath $Out)) 'Never replay this continuation'
 $items=@(BdJson -Arguments @('list','--json','--limit','100'))
 Assert 'ONLY_EXPECTED_ACTIVE' ($items.Count -eq 1 -and $items[0].id -eq 'dist-bra' -and $items[0].status -eq 'open' -and $items[0].title -eq 'PILOT active responsibility') ('Observed entries='+$items.Count)
 $Stage='COMPLETE_ACTIVE_AND_HANDOFF'
 [void](Bd -Arguments @('update','dist-bra','--status','in_progress','--json'))
 $created=@(BdJson -Arguments @('create','PILOT incoming handoff','--description','Synthetic ref test://TS-BEADS-CONTINUITY-PILOT-20261013-001/H1. Nonblocking, independent and without Product authority.','-t','task','-p','2','--json'))
 Assert 'HANDOFF_CREATED' ($created.Count -eq 1 -and [bool]$created[0].id) 'Exactly one created issue parsed'
 $handoff=[string]$created[0].id
 $Receipt.handoff=$handoff
 [void](Bd -Arguments @('dep','add',$handoff,'dist-bra','--type','related'))
 $ready=@(BdJson -Arguments @('ready','--json'))
 Assert 'READY_NONBLOCKING' (@($ready | Where-Object {$_.id -eq $handoff}).Count -eq 1) 'Related is not a blocking prerequisite'
 [void](Bd -Arguments @('close','dist-bra','--reason','Synthetic active work completed; separate handoff remains open.','--json'))
 $Stage='FRESH_PROCESS_READBACK'
 $child=Join-Path $HomeDir 'continuation-003-readback.json'
 & pwsh.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'verify-003.ps1') -Bd $B -Store $env:BEADS_DIR -Active 'dist-bra' -Handoff $handoff -Output $child
 Assert 'CHILD_EXIT' ($LASTEXITCODE -eq 0) 'Independent pwsh process is required'
 $verify=Get-Content -LiteralPath $child -Raw | ConvertFrom-Json
 Assert 'RECOVERED_DURABLY' ($verify.recovered -eq $true -and $verify.active_status -eq 'closed' -and $verify.handoff_status -eq 'open' -and $verify.handoff_count -eq 1) 'Fresh process verifies durable state'
 $Receipt.readback=$verify
 $Receipt.status='PASS'
 $Stage='PASS'
} catch {
 $Receipt.status=if($Stage -eq 'PREFLIGHT'){'BLOCKED_PRECONDITION'}else{'FAIL'}
 $Receipt.error=$_.Exception.Message
} finally {
 $Receipt.stage=$Stage
 $Receipt.completed_utc=(Get-Date).ToUniversalTime().ToString('o')
 try { $Receipt | ConvertTo-Json -Depth 11 | Set-Content -LiteralPath $Out -Encoding utf8 } catch {$Receipt.persistence_error=$_.Exception.Message}
 [ordered]@{pilot=$Id;attempt=$Attempt;status=$Receipt.status;stage=$Stage;subject='dist-bra';handoff=$Receipt.handoff;result=$Out;error=$Receipt.error} | ConvertTo-Json -Compress -Depth 6 | Write-Output
}
if($Receipt.status -ne 'PASS'){exit 1}
