# Read-only terminal reconciliation of attempt 002; never replay Beads writes.
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$Pilot='TS-BEADS-INBOX-DEDUP-PILOT-20261013-002'
$Attempt='BEADS-INBOX-READBACK-20261013-003'
$Root=Join-Path $env:LOCALAPPDATA ('TS-Experiments\'+$Pilot)
$Store=Join-Path $Root 'data\.beads'
$Tool=Join-Path $env:LOCALAPPDATA 'TS-Experiments\TS-BEADS-CONTINUITY-PILOT-20261013-001\bin\bd.exe'
$Out=Join-Path $Root 'readback-003.json'
$Prior=Join-Path $Root 'result.json'
$Manifest=Join-Path $PSScriptRoot 'manifest-003.json'
$Stage='PREFLIGHT'
$Receipt=[ordered]@{contract='ts-beads-inbox-readback/v0-experimental';pilot=$Pilot;execution_attempt=$Attempt;source_attempt='BEADS-INBOX-LOCAL-20261013-002';status='UNKNOWN';stage=$Stage;authority='NONE_PRODUCT';checks=@();error=$null;started_utc=(Get-Date).ToUniversalTime().ToString('o')}
function Check([string]$Code,[bool]$Good,[string]$Explanation) {
 $Receipt.checks+= [ordered]@{code=$Code;pass=$Good;detail=$Explanation}
 if(-not $Good){throw ('CHECK_FAILED:'+ $Code+':'+$Explanation)}
}
function BdJson([string[]]$A) {
 $raw=& $Tool @A 2>&1
 if($LASTEXITCODE -ne 0){throw ('BD_FAILED:'+($A -join ' ')+':'+($raw -join ' '))}
 $s=($raw|Out-String).Trim()
 $m=[regex]::Match($s,'(?m)^[ \t]*(?:\[|\{)')
 if(-not $m.Success){throw 'NO_BD_JSON'}
 return ($s.Substring($m.Index)|ConvertFrom-Json)
}
function ReadSource([string]$Id) {
 $issue=@(BdJson -A @('show',$Id,'--json'))[0]
 if($null -eq $issue.PSObject.Properties['description']){return ''}
 foreach($line in ([string]$issue.description -split "\r?\n")){
  if($line.StartsWith('SOURCE_REF=')){return $line.Substring(11).Trim()}
 }
 return ''
}
try {
 Check 'LOCAL_PATH_PIN' ($env:LOCALAPPDATA -eq 'C:\Users\maued\AppData\Local') 'Same isolated local profile as source attempt'
 Check 'ORIGINAL_RESULT_PRESERVED' (Test-Path -LiteralPath $Prior) 'Original effect receipt retained'
 Check 'NEW_RESULT_ABSENT' (-not (Test-Path -LiteralPath $Out)) 'Never replay this readback attempt'
 $parent=Get-Content -LiteralPath $Prior -Raw|ConvertFrom-Json
 Check 'SOURCE_TERMINAL_IDENTITY' ($parent.execution_attempt -eq 'BEADS-INBOX-LOCAL-20261013-002' -and $parent.status -eq 'FAIL' -and $parent.stage -eq 'CLOSE_AT_CHECKPOINT_AND_FRESH_READBACK') 'Read back exact failed verifier attempt only'
 Check 'EXACT_IDS' ($parent.ids.active -eq 'dist-3gz' -and $parent.ids.source_a -eq 'dist-qlj' -and $parent.ids.source_b -eq 'dist-b1o') 'Frozen original Beads IDs'
 $m=Get-Content -LiteralPath $Manifest -Raw|ConvertFrom-Json
 $self=((& git hash-object -- $PSCommandPath)|Out-String).Trim()
 Check 'SCRIPT_PIN' ($LASTEXITCODE -eq 0 -and $self -eq $m.runner_blob_sha -and $m.execution_attempt -eq $Attempt) 'Pinned source and readback identity'
 Check 'STORE_AND_BINARY_EXIST' ((Test-Path -LiteralPath $Store) -and (Test-Path -LiteralPath $Tool)) 'Read-only reconciliation of existing store'
 $env:BEADS_DIR=$Store
 $Stage='READ_ONLY_CHECKPOINT'
 $activeId=[string]$parent.ids.active
 $aId=[string]$parent.ids.source_a
 $bId=[string]$parent.ids.source_b
 $activeItem=@(BdJson -A @('show',$activeId,'--json'))[0]
 $aItem=@(BdJson -A @('show',$aId,'--json'))[0]
 $bItem=@(BdJson -A @('show',$bId,'--json'))[0]
 $all=@(BdJson -A @('list','--json','--limit','100'))
 $ready=@(BdJson -A @('ready','--json'))
 $sourceA='test://TS-BEADS-INBOX-DEDUP-PILOT-20261013-002/ORIGIN-A@fixed'
 $sourceB='test://TS-BEADS-INBOX-DEDUP-PILOT-20261013-002/ORIGIN-B@fixed'
 $na=0;$nb=0
 foreach($item in $all){
  $src=ReadSource -Id ([string]$item.id)
  if($src -ceq $sourceA){$na++}
  if($src -ceq $sourceB){$nb++}
 }
 Check 'ACTIVE_CLOSED' ($activeItem.status -eq 'closed') 'Prior active responsibility completed'
 Check 'OPEN_HANDOFFS' ($aItem.status -eq 'open' -and $bItem.status -eq 'open') 'Handoffs survive after active close'
 Check 'IDENTITY_UNIQUE' ($na -eq 1 -and $nb -eq 1 -and $aId -ne $bId) 'Exactly one per source and two distinct issues'
 Check 'CORRECT_SOURCE_MARKERS' ((ReadSource -Id $aId) -ceq $sourceA -and (ReadSource -Id $bId) -ceq $sourceB) 'No title-based false deduplication'
 Check 'READY_AFTER_CHECKPOINT' (@($ready|Where-Object {$_.id -eq $aId}).Count -eq 1 -and @($ready|Where-Object {$_.id -eq $bId}).Count -eq 1) 'Recoverable after checkpoint'
 $Receipt.source_a_count=$na;$Receipt.source_b_count=$nb
 $Receipt.ids=$parent.ids
 $Stage='PASS';$Receipt.status='PASS'
} catch {
 $Receipt.status=if($Stage -eq 'PREFLIGHT'){'BLOCKED_PRECONDITION'}else{'FAIL'}
 $Receipt.error=$_.Exception.Message
} finally {
 $Receipt.stage=$Stage
 $Receipt.completed_utc=(Get-Date).ToUniversalTime().ToString('o')
 try{$Receipt|ConvertTo-Json -Depth 10|Set-Content -LiteralPath $Out -Encoding utf8}catch{$Receipt.persistence_error=$_.Exception.Message}
 [ordered]@{pilot=$Pilot;attempt=$Attempt;source_attempt=$Receipt.source_attempt;status=$Receipt.status;stage=$Stage;checks=$Receipt.checks;ids=$Receipt.ids;result=$Out;error=$Receipt.error}|ConvertTo-Json -Depth 7 -Compress | Write-Output
}
if($Receipt.status -ne 'PASS'){exit 1}
