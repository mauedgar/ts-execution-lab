# TS-BEADS-CONCURRENCY-PILOT-20261013-003 / synthetics only / NONE_PRODUCT
param([ValidateSet('main','worker','verify')][string]$Role='main',[ValidateSet('A','B')][string]$Slot='A',[string]$Work='')
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$Pilot='TS-BEADS-CONCURRENCY-PILOT-20261013-003'
$Attempt='BEADS-CONCURRENCY-LOCAL-20261013-001'
$Top=Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'TS-Experiments'
$Old=Join-Path $Top 'TS-BEADS-CONTINUITY-PILOT-20261013-001'
$Old2=Join-Path $Top 'TS-BEADS-INBOX-DEDUP-PILOT-20261013-002'
$Bd=Join-Path $Old 'bin\bd.exe'
if(-not $Work){$Work=Join-Path $Top $Pilot}
$Store=Join-Path $Work 'data\.beads'
$Source='test://TS-BEADS-CONCURRENCY-PILOT-20261013-003/SHARED@fixed'
$Tag='TS_BDS003_CONCURRENT_001'
function EName([string]$x){'Local\'+$Tag+'_'+$x}
function EOpen([string]$x){[System.Threading.EventWaitHandle]::OpenExisting((EName $x))}
function ESignal([string]$x){$e=EOpen $x;try{[void]$e.Set()}finally{$e.Dispose()}}
function EAwait([string]$x,[int]$sec){$e=EOpen $x;try{if(-not $e.WaitOne([TimeSpan]::FromSeconds($sec))){throw ('EVENT_TIMEOUT_'+$x)}}finally{$e.Dispose()}}
function OutJson([string]$p,$o){$o|ConvertTo-Json -Depth 9|Set-Content -LiteralPath $p -Encoding utf8}
function BDJson([string[]]$a){
  $reply=& $Bd @a 2>&1
  if($LASTEXITCODE -ne 0){throw ('BD_FAILED_'+($a -join '_')+':'+(($reply|Out-String).Trim()))}
  $str=($reply|Out-String).Trim()
  $m=[regex]::Match($str,'(?m)^[ \t]*(?:\{|\[)')
  if(-not $m.Success){throw ('BD_NO_JSON:'+ $str)}
  return ($str.Substring($m.Index)|ConvertFrom-Json)
}
if($Role -eq 'worker'){
  $o=[ordered]@{slot=$Slot;pid=$PID;attempt=$Attempt;status='UNKNOWN';precheck_count=$null;created_id=$null;write_start_utc=$null;write_end_utc=$null;error=$null}
  try{
    $env:BEADS_DIR=$Store
    $ids=Get-Content (Join-Path $Work 'ids.json') -Raw|ConvertFrom-Json
    $own=if($Slot -eq 'A'){$ids.A}else{$ids.B}
    ESignal ($Slot+'Ready')
    EAwait 'Go' 25
    [void](BDJson @('update',([string]$own),'--status','in_progress','--json'))
    $items=@(BDJson @('list','--json','--limit','100'))
    $o.precheck_count=@($items|Where-Object {$_.title -eq 'Synthetic collision 003'}).Count
    ESignal ($Slot+'Prechecked')
    EAwait 'RaceGo' 25
    $o.write_start_utc=[datetime]::UtcNow.ToString('o')
    try{
      $item=@(BDJson @('create','Synthetic collision 003','--description',('SOURCE_REF='+$Source),'--type','task','--priority','2','--json'))[0]
      $o.created_id=[string]$item.id
      $o.status='PASS'
    }catch{$o.status='WRITE_FAILED';$o.error=$_.Exception.Message}
    finally{$o.write_end_utc=[datetime]::UtcNow.ToString('o')}
  }catch{$o.status='FAIL';$o.error=$_.Exception.Message}
  finally{
    try{OutJson (Join-Path $Work ('worker-'+$Slot+'.json')) $o}catch{}
    try{ESignal ($Slot+'Done')}catch{}
  }
  if($o.status -eq 'PASS'){exit 0}else{exit 1}
}
if($Role -eq 'verify'){
  $o=[ordered]@{status='UNKNOWN';reader_pid=$PID;source_count=0;source_ids=@();A_status=$null;B_status=$null;error=$null}
  try{
    $env:BEADS_DIR=$Store
    $ids=Get-Content (Join-Path $Work 'ids.json') -Raw|ConvertFrom-Json
    $all=@(BDJson @('list','--json','--limit','100'))
    $matches=@()
    foreach($rec in $all){
      $obj=@(BDJson @('show',([string]$rec.id),'--json'))[0]
      if(([string]$obj.description).Contains('SOURCE_REF='+$Source)){$matches+=([string]$rec.id)}
    }
    $a=@(BDJson @('show',([string]$ids.A),'--json'))[0]
    $b=@(BDJson @('show',([string]$ids.B),'--json'))[0]
    $o.A_status=$a.status;$o.B_status=$b.status
    $o.source_ids=$matches
    $o.source_count=@($matches).Count
    $o.status=if($o.A_status -eq 'in_progress' -and $o.B_status -eq 'in_progress'){'PASS'}else{'FAIL'}
  }catch{$o.status='FAIL';$o.error=$_.Exception.Message}
  finally{OutJson (Join-Path $Work 'readback.json') $o}
  if($o.status -eq 'PASS'){exit 0}else{exit 1}
}
# Main: strict preflight before any creation, one attempt, no retry
$stage='PREFLIGHT'
$r=[ordered]@{pilot=$Pilot;attempt=$Attempt;authority='NONE_PRODUCT';host=[Environment]::MachineName;status='UNKNOWN';stage='PREFLIGHT';started_utc=[datetime]::UtcNow.ToString('o');source_commit=$null;child_pids=@();workers=@();overlap_proven=$false;reader=$null;dedup_guarantee_proven=$false;error=$null}
$events=@{};$children=@()
try{
  if([Environment]::MachineName -cne 'DESKTOP-3LJ0E54'){throw 'WRONG_HOST'}
  if(Test-Path -LiteralPath $Work){throw 'WORKSPACE_EXISTS_NO_REPLAY'}
  $m=Get-Content (Join-Path $PSScriptRoot 'manifest.json') -Raw|ConvertFrom-Json
  if($m.execution_attempt -cne $Attempt -or $m.host -cne 'DESKTOP-3LJ0E54' -or $m.authority -cne 'NONE_PRODUCT'){throw 'MANIFEST_IDENTITY'}
  $sha=((& git hash-object -- $PSCommandPath)|Out-String).Trim()
  if($LASTEXITCODE -ne 0 -or $sha -cne $m.runner_git_blob){throw 'RUNNER_HASH_MISMATCH'}
  $r.source_commit=$m.source_commit
  if(-not(Test-Path $Bd)){throw 'INSTALLED_BINARY_NOT_FOUND'}
  $prev=Get-Content (Join-Path $Old 'result.json') -Raw|ConvertFrom-Json
  $p1=Get-Content (Join-Path $Old 'continuation-003-result.json') -Raw|ConvertFrom-Json
  $p2=Get-Content (Join-Path $Old2 'readback-003.json') -Raw|ConvertFrom-Json
  if($p1.status -ne 'PASS' -or $p2.status -ne 'PASS' -or ((Get-FileHash $Bd -Algorithm SHA256).Hash.ToLowerInvariant() -cne $prev.bd_binary_sha256)){throw 'PRIOR_RECEIPT_OR_BINARY_MISMATCH'}
  $drive=Get-PSDrive -Name ([IO.Path]::GetPathRoot($Work).Substring(0,1))
  if($drive.Free -lt 1073741824){throw 'DISK_FLOOR'}
  $stage='INIT'
  New-Item -ItemType Directory -Path (Join-Path $Work 'data') -Force|Out-Null
  $env:BEADS_DIR=$Store
  $init=& $Bd init --quiet --stealth 2>&1
  if($LASTEXITCODE -ne 0){throw ('INIT_FAILED:'+($init|Out-String))}
  $a=@(BDJson @('create','Independent task A','--type','task','--priority','2','--json'))[0]
  $b=@(BDJson @('create','Independent task B','--type','task','--priority','2','--json'))[0]
  if(-not $a.id -or -not $b.id -or $a.id -eq $b.id){throw 'TASK_CREATION'}
  OutJson (Join-Path $Work 'ids.json') ([ordered]@{A=[string]$a.id;B=[string]$b.id})
  $stage='PARALLEL_WORKERS'
  foreach($x in @('AReady','BReady','Go','APrechecked','BPrechecked','RaceGo','ADone','BDone')){
    $events[$x]=[System.Threading.EventWaitHandle]::new($false,[System.Threading.EventResetMode]::ManualReset,(EName $x))
  }
  foreach($slot in @('A','B')){
    $cmd='-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "'+$PSCommandPath+'" -Role worker -Slot '+$slot+' -Work "'+$Work+'"'
    $p=Start-Process -FilePath 'pwsh.exe' -ArgumentList $cmd -PassThru -WindowStyle Hidden
    $children+=@{slot=$slot;pid=$p.Id}
  }
  EAwait 'AReady' 20; EAwait 'BReady' 20
  [void]$events['Go'].Set()
  EAwait 'APrechecked' 25; EAwait 'BPrechecked' 25
  [void]$events['RaceGo'].Set()
  EAwait 'ADone' 30; EAwait 'BDone' 30
  $wa=Get-Content (Join-Path $Work 'worker-A.json') -Raw|ConvertFrom-Json
  $wb=Get-Content (Join-Path $Work 'worker-B.json') -Raw|ConvertFrom-Json
  $r.workers=@($wa,$wb)
  if($wa.write_start_utc -and $wb.write_start_utc -and $wa.write_end_utc -and $wb.write_end_utc){
    $r.overlap_proven=([datetime]$wa.write_start_utc -le [datetime]$wb.write_end_utc -and [datetime]$wb.write_start_utc -le [datetime]$wa.write_end_utc)
  }
  $stage='FRESH_READBACK'
  & pwsh.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $PSCommandPath -Role verify -Work $Work
  $ve=$LASTEXITCODE
  $read=Get-Content (Join-Path $Work 'readback.json') -Raw|ConvertFrom-Json
  $r.reader=$read
  $both=($wa.status -eq 'PASS' -and $wb.status -eq 'PASS')
  $pre=($wa.precheck_count -eq 0 -and $wb.precheck_count -eq 0)
  $r.dedup_guarantee_proven=($r.overlap_proven -and $both -and $pre -and $read.source_count -eq 1 -and $wa.created_id -eq $wb.created_id -and $ve -eq 0)
  if($ve -ne 0 -or -not $pre -or -not $r.overlap_proven){$r.status='INCONCLUSIVE'}
  elseif(-not $both){$r.status='CONTENTION_OR_WRITE_FAILURE'}
  elseif($r.dedup_guarantee_proven){$r.status='PASS_ATOMIC_DEDUP'}
  elseif($read.source_count -eq 2){$r.status='OBSERVED_DUPLICATES'}
  else{$r.status='INCONCLUSIVE'}
  $stage='TERMINAL'
}catch{$r.status=if($stage -eq 'PREFLIGHT'){'BLOCKED_PRECONDITION'}else{'UNKNOWN_RECONCILIATION_REQUIRED'};$r.error=$_.Exception.Message}
finally{
  foreach($e in $events.Values){try{$e.Dispose()}catch{}}
  $r.child_pids=$children
  $r.stage=$stage
  $r.completed_utc=[datetime]::UtcNow.ToString('o')
  if(Test-Path -LiteralPath $Work){try{OutJson (Join-Path $Work 'result.json') $r}catch{}}
  [ordered]@{attempt=$Attempt;status=$r.status;stage=$stage;overlap=$r.overlap_proven;dedup_proven=$r.dedup_guarantee_proven;source_count=$r.reader.source_count;receipt=(Join-Path $Work 'result.json');error=$r.error}|ConvertTo-Json -Depth 5 -Compress|Write-Output
}
if($r.status -in @('PASS_ATOMIC_DEDUP','OBSERVED_DUPLICATES')){exit 0}else{exit 1}
