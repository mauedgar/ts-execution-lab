# Beads inbox source-ref dedup experiment. NONE_PRODUCT.
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$Pilot='TS-BEADS-INBOX-DEDUP-PILOT-20261013-002'
$Attempt='BEADS-INBOX-LOCAL-20261013-002'
$Prior='TS-BEADS-CONTINUITY-PILOT-20261013-001'
$Root=Join-Path $env:LOCALAPPDATA 'TS-Experiments'
$Work=Join-Path $Root $Pilot
$Old=Join-Path $Root $Prior
$Tool=Join-Path $Old 'bin\bd.exe'
$Store=Join-Path $Work 'data\.beads'
$Output=Join-Path $Work 'result.json'
$Stage='PREFLIGHT'
$Manifest=Join-Path $PSScriptRoot 'manifest-002.json'
$Receipt=[ordered]@{connector_device='DESKTOP-3LJ0E54';prior_terminal='BEADS-INBOX-LOCAL-20261013-001:BLOCKED_PRECONDITION_NO_WORKSPACE';contract='ts-beads-inbox-dedup-result/v0-experimental';pilot=$Pilot;execution_attempt=$Attempt;status='UNKNOWN';stage=$Stage;authority='NONE_PRODUCT';host=$env:COMPUTERNAME;started_utc=(Get-Date).ToUniversalTime().ToString('o');checks=@();inbox_events=@();ids=@{};error=$null;limitations=@('Sequential ingest only; no concurrent race proof','Source-ref dedup is experiment-owned policy, not native Beads guarantee','No automatic chat completion detection','No host-native Git Transport publication')}
function Check([string]$Name,[bool]$Okay,[string]$Detail) {
 $Receipt.checks+= [ordered]@{code=$Name;pass=$Okay;detail=$Detail}
 if(-not $Okay){throw ('GUARD_OR_ASSERT:'+ $Name +':'+ $Detail)}
}
function Bd([string[]]$A) {
 $r = & $Tool @A 2>&1
 if($LASTEXITCODE -ne 0){throw ('BD_COMMAND_FAILED:'+($A -join ' ')+':'+($r -join ' '))}
 return ($r | Out-String).Trim()
}
function BdJson([string[]]$A) {
 $raw=Bd -A $A
 $m=[regex]::Match($raw,'(?m)^[ \t]*(?:\[|\{)')
 if(-not $m.Success){throw 'BD_JSON_NOT_FOUND'}
 return ($raw.Substring($m.Index) | ConvertFrom-Json)
}
function GetSource([string]$IssueId) {
 $obj=@(BdJson -A @('show',$IssueId,'--json'))[0]
 if($null -eq $obj -or $null -eq $obj.PSObject.Properties['description']){return ''}
 foreach($line in ([string]$obj.description -split "\r?\n")) {
  if($line.StartsWith('SOURCE_REF=')){return $line.Substring(11).Trim()}
 }
 return ''
}
function FindSource([string]$Ref) {
 $matches=@()
 $all=@(BdJson -A @('list','--json','--limit','100'))
 foreach($entry in $all){
  if((GetSource -IssueId ([string]$entry.id)) -ceq $Ref){$matches+= [string]$entry.id}
 }
 return $matches
}
function Ingest([string]$Ref,[string]$Title) {
 $existing=@(FindSource -Ref $Ref)
 if($existing.Count -gt 1){throw ('SOURCE_REF_CONFLICT:'+ $Ref)}
 if($existing.Count -eq 1) {
  $Receipt.inbox_events += [ordered]@{source_ref=$Ref;disposition='REUSED';id=$existing[0]}
  return [string]$existing[0]
 }
 $item=@(BdJson -A @('create',$Title,'--description',("SOURCE_REF="+$Ref+"`nSynthetic inbox handoff. No Product authority."),'-t','task','-p','2','--json'))[0]
 if($null -eq $item -or -not $item.id){throw 'CREATE_RETURNED_NO_ID'}
 $newId=[string]$item.id
 $count=@(FindSource -Ref $Ref)
 if($count.Count -ne 1 -or $count[0] -ne $newId){throw 'SOURCE_NOT_RETRIEVABLE'}
 $Receipt.inbox_events += [ordered]@{source_ref=$Ref;disposition='CREATED';id=$newId}
 return $newId
}
try {
 Check 'ISOLATED_USER_LOCALAPPDATA' ($env:LOCALAPPDATA -eq 'C:\Users\maued\AppData\Local') 'Pin isolated destination; connector device separately verified'
 Check 'PRIOR_BINARY' (Test-Path -LiteralPath $Tool) 'Use already installed isolated binary'
 Check 'PRIOR_RESULT' (Test-Path -LiteralPath (Join-Path $Old 'continuation-003-result.json')) 'Previous successful receipt'
 $previous=Get-Content -LiteralPath (Join-Path $Old 'continuation-003-result.json') -Raw | ConvertFrom-Json
 Check 'PRIOR_PASS' ($previous.execution_attempt -eq 'BEADS-LOCAL-TRIAL-20261013-003' -and $previous.status -eq 'PASS' -and $previous.handoff -eq 'dist-dur') 'Continue from verified original, do not replay'
 $oldFailure=Get-Content -LiteralPath (Join-Path $Old 'result.json') -Raw | ConvertFrom-Json
 $bHash=(Get-FileHash -LiteralPath $Tool -Algorithm SHA256).Hash.ToLowerInvariant()
 Check 'BINARY_SAME' ($bHash -eq $oldFailure.bd_binary_sha256) 'Beads existing binary same hash'
 Check 'FRESH_WORKSPACE' (-not (Test-Path -LiteralPath $Work)) 'Never overwrite or retry existing attempt'
 $m=Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json
 $hashRunner=((& git hash-object -- $PSCommandPath) | Out-String).Trim()
 Check 'RUNNER_BLOB_PIN' ($LASTEXITCODE -eq 0 -and $hashRunner -eq $m.runner_blob_sha) 'Git blob of runner pinned'
 $verify=Join-Path (Split-Path -Parent $PSScriptRoot) 'verify-fresh.ps1'
 $hashVerify=((& git hash-object -- $verify) | Out-String).Trim()
 Check 'VERIFY_BLOB_PIN' ($LASTEXITCODE -eq 0 -and $hashVerify -eq $m.verify_blob_sha) 'Git blob of verifier pinned'
 Check 'FROZEN_MANIFEST' ($m.execution_attempt -eq $Attempt -and $m.pilot -eq $Pilot -and $m.authority -eq 'NONE_PRODUCT' -and $m.tool_release -eq 'v1.3.1') 'Frozen IDs and scope'
 $drive=Get-PSDrive -Name ([IO.Path]::GetPathRoot($Work).Substring(0,1))
 Check 'DISK_FREE' ($drive.Free -gt 1073741824) 'Require over 1GiB available'
 $Stage='INITIALIZE_NEW_ISOLATED_STORE'
 New-Item -ItemType Directory -Path (Join-Path $Work 'data') -Force | Out-Null
 $env:BEADS_DIR=$Store
 [void](Bd -A @('init','--quiet','--stealth'))
 $task=@(BdJson -A @('create','PILOT active responsibility 002','--description','Synthetic active work, separate from handoffs.','-t','task','-p','2','--json'))[0]
 $active=[string]$task.id
 Check 'ACTIVE_CREATED' ([bool]$active) 'Synthetic task created'
 [void](Bd -A @('update',$active,'--status','in_progress','--json'))
 $Stage='INGEST_WHILE_ACTIVE'
 $sourceA='test://TS-BEADS-INBOX-DEDUP-PILOT-20261013-002/ORIGIN-A@fixed'
 $sourceB='test://TS-BEADS-INBOX-DEDUP-PILOT-20261013-002/ORIGIN-B@fixed'
 $a1=Ingest -Ref $sourceA -Title 'Synthetic incoming handoff'
 [void](Bd -A @('dep','add',$a1,$active,'--type','related'))
 $a2=Ingest -Ref $sourceA -Title 'Synthetic incoming handoff'
 $a3=Ingest -Ref $sourceA -Title 'Synthetic incoming handoff changed text'
 $b1=Ingest -Ref $sourceB -Title 'Synthetic incoming handoff'
 $Receipt.ids=[ordered]@{active=$active;source_a=$a1;source_b=$b1}
 Check 'SAME_SOURCE_REUSED' ($a1 -eq $a2 -and $a1 -eq $a3) 'Three submissions resolve to one Beads ID'
 Check 'DISTINCT_SOURCE_PRESERVED' ($b1 -ne $a1) 'Equal title with different source remains separate'
 Check 'SOURCE_A_UNIQUE' (@(FindSource -Ref $sourceA).Count -eq 1) 'Exactly one original source'
 Check 'SOURCE_B_UNIQUE' (@(FindSource -Ref $sourceB).Count -eq 1) 'Exactly one other source'
 $ready=@(BdJson -A @('ready','--json'))
 Check 'HANDOFFS_READY_WITH_ACTIVE' (@($ready|Where-Object {$_.id -eq $a1}).Count -eq 1 -and @($ready|Where-Object {$_.id -eq $b1}).Count -eq 1) 'Informational link does not block independent inbox'
 $activeNow=@(BdJson -A @('show',$active,'--json'))[0]
 Check 'ACTIVE_NOT_INTERRUPTED' ($activeNow.status -eq 'in_progress') 'Handoffs received before checkpoint without changing active status'
 $Stage='CLOSE_AT_CHECKPOINT_AND_FRESH_READBACK'
 [void](Bd -A @('close',$active,'--reason','Synthetic active work finished; now consult inbox.','--json'))
 $readback=Join-Path $Work 'readback.json'
 & pwsh.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $verify -Tool $Tool -Store $Store -Active $active -A $a1 -B $b1 -SourceA $sourceA -SourceB $sourceB -Out $readback
 Check 'FRESH_PROCESS_EXIT' ($LASTEXITCODE -eq 0) 'Independent process verified checkpoint and source refs'
 $read=Get-Content -LiteralPath $readback -Raw | ConvertFrom-Json
 Check 'READBACK_PASS' ($read.status -eq 'PASS' -and $read.handoff_count -eq 2 -and $read.source_a_count -eq 1 -and $read.source_b_count -eq 1) 'Two uniquely sourced handoffs remain recoverable'
 $Receipt.readback=$read
 $Receipt.status='PASS'
 $Stage='PASS'
} catch {
 $Receipt.status=if($Stage -eq 'PREFLIGHT'){'BLOCKED_PRECONDITION'}else{'FAIL'}
 $Receipt.error=$_.Exception.Message
} finally {
 $Receipt.stage=$Stage
 $Receipt.completed_utc=(Get-Date).ToUniversalTime().ToString('o')
 if(Test-Path -LiteralPath $Work){
  try {$Receipt|ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $Output -Encoding utf8} catch{$Receipt.persistence_error=$_.Exception.Message}
 }
 [ordered]@{pilot=$Pilot;attempt=$Attempt;status=$Receipt.status;stage=$Stage;ids=$Receipt.ids;events=$Receipt.inbox_events;result=$Output;error=$Receipt.error} | ConvertTo-Json -Depth 7 -Compress | Write-Output
}
if($Receipt.status -ne 'PASS'){exit 1}
