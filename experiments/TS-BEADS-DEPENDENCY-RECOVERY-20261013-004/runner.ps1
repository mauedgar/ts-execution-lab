# TS Beads Dependency Recovery Pilot 004 - synthetic experimental only
param([ValidateSet('main','before','resume','verify')][string]$Mode='main',
      [string]$Workspace='')
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$Pilot='TS-BEADS-DEPENDENCY-RECOVERY-20261013-004'
$Attempt='BEADS-DEPENDENCY-RECOVERY-20261013-001'
$Base=Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'TS-Experiments'
if(-not $Workspace){$Workspace=Join-Path $Base $Pilot}
$Bin=Join-Path (Join-Path $Base 'TS-BEADS-CONTINUITY-PILOT-20261013-001') 'bin\bd.exe'
$Store=Join-Path $Workspace 'data\.beads'
$env:BEADS_DIR=$Store
$Checkpoint='test://TS-BEADS-DEPENDENCY-RECOVERY-20261013-004/ORIGIN-A@CHECKPOINT-2'
function InvokeBD([string[]]$Argv){
  $output=& $Bin @Argv 2>&1
  if($LASTEXITCODE -ne 0){throw ('BEADS_EXIT_NONZERO:'+($Argv -join ' ')+':'+(($output|Out-String).Trim()))}
  return ($output|Out-String).Trim()
}
function GetBDJson([string[]]$Argv){
  $raw=InvokeBD $Argv
  $match=[regex]::Match($raw,'(?m)^[ \t]*(?:\{|\[)')
  if(-not $match.Success){throw ('BEADS_JSON_MISSING:'+ $raw)}
  return ($raw.Substring($match.Index)|ConvertFrom-Json)
}
function Assert([bool]$OK,[string]$Name){if(-not $OK){throw ('ASSERT_'+$Name)}}
function WriteReceipt([string]$Path,$Value){$Value|ConvertTo-Json -Depth 10|Set-Content -LiteralPath $Path -Encoding utf8}
function Fresh([string]$Stage){
  & pwsh.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $PSCommandPath -Mode $Stage -Workspace $Workspace
  if($LASTEXITCODE -ne 0){throw ('FRESH_PROCESS_FAILED_'+$Stage)}
}
if($Mode -ne 'main'){
  $item=Get-Content -LiteralPath (Join-Path $Workspace 'identities.json') -Raw|ConvertFrom-Json
  $originId=[string]$item.origin; $dependencyId=[string]$item.dependency; $resumeId=[string]$item.resume; $peerId=[string]$item.peer
  $dependency=@(GetBDJson @('show',$dependencyId,'--json'))[0]
  $origin=@(GetBDJson @('show',$originId,'--json'))[0]
  $resume=@(GetBDJson @('show',$resumeId,'--json'))[0]
  $peer=@(GetBDJson @('show',$peerId,'--json'))[0]
  $ready=@(GetBDJson @('ready','--json'))
  $readyIds=@($ready|ForEach-Object {[string]$_.id})
  if($Mode -eq 'before'){
    Assert ($dependency.status -eq 'open' -and $resume.status -eq 'open') 'dependency_open'
    Assert ($origin.status -eq 'in_progress') 'original_ongoing'
    Assert ($readyIds -cnotcontains $resumeId) 'blocked_resume_not_ready'
    Assert ($readyIds -ccontains $peerId) 'independent_peer_ready'
    Assert (([string]$resume.description).Contains($Checkpoint)) 'checkpoint_retained'
    WriteReceipt (Join-Path $Workspace 'before.json') ([ordered]@{status='PASS';pid=$PID;dependency=$dependency.status;origin=$origin.status;readyIds=$readyIds;checkpoint=$Checkpoint})
    exit 0
  }
  if($Mode -eq 'resume'){
    Assert ($dependency.status -eq 'closed') 'dependency_must_be_closed'
    Assert ($origin.status -eq 'in_progress') 'origin_original_ongoing'
    Assert ($readyIds -ccontains $resumeId) 'resume_newly_ready'
    Assert ($readyIds -ccontains $peerId) 'peer_unaffected'
    Assert (([string]$resume.description).Contains($Checkpoint)) 'exact_checkpoint'
    [void](InvokeBD @('update',$resumeId,'--status','in_progress','--json'))
    [void](InvokeBD @('close',$resumeId,'--reason','Synthetic checkpoint resumed from independent fresh process.','--json'))
    [void](InvokeBD @('close',$originId,'--reason','Synthetic original responsibility completed after exact checkpoint.','--json'))
    WriteReceipt (Join-Path $Workspace 'resumed.json') ([ordered]@{status='PASS';pid=$PID;checkpoint=$Checkpoint;origin=$originId;resume=$resumeId;dependency=$dependencyId;peer=$peerId})
    exit 0
  }
  if($Mode -eq 'verify'){
    $dependency=@(GetBDJson @('show',$dependencyId,'--json'))[0]
    $origin=@(GetBDJson @('show',$originId,'--json'))[0]
    $resume=@(GetBDJson @('show',$resumeId,'--json'))[0]
    $peer=@(GetBDJson @('show',$peerId,'--json'))[0]
    Assert ($dependency.status -eq 'closed' -and $origin.status -eq 'closed' -and $resume.status -eq 'closed') 'three_terminal'
    Assert ($peer.status -eq 'open') 'independent_unmodified'
    $all=@(GetBDJson @('list','--all','--json','--limit','100'))
    Assert ($all.Count -eq 4) 'four_only_no_duplicates'
    Assert (@($all|Where-Object {$_.title -eq 'Dependency B from module B'}).Count -eq 1) 'dependency_unique'
    WriteReceipt (Join-Path $Workspace 'readback.json') ([ordered]@{status='PASS';pid=$PID;record_count=$all.Count;ids=@($originId,$dependencyId,$resumeId,$peerId);dependency_status=$dependency.status;origin_status=$origin.status;resume_status=$resume.status;independent_status=$peer.status})
    exit 0
  }
}
$stage='PREFLIGHT'
$r=[ordered]@{pilot=$Pilot;execution_attempt=$Attempt;authority='NONE_PRODUCT';status='UNKNOWN';stage=$stage;host=[Environment]::MachineName;started_utc=[datetime]::UtcNow.ToString('o');refs=@{};error=$null}
try {
  Assert ([Environment]::MachineName -ceq 'DESKTOP-3LJ0E54') 'host'
  Assert (-not(Test-Path -LiteralPath $Workspace)) 'no_replay_workspace'
  $m=Get-Content (Join-Path $PSScriptRoot 'manifest.json') -Raw|ConvertFrom-Json
  Assert ($m.execution_attempt -ceq $Attempt -and $m.authority -ceq 'NONE_PRODUCT' -and $m.pilot -ceq $Pilot) 'manifest'
  $thisBlob=((& git hash-object -- $PSCommandPath)|Out-String).Trim()
  Assert ($LASTEXITCODE -eq 0 -and $thisBlob -ceq $m.runner_git_blob) 'runner_blob'
  Assert (Test-Path -LiteralPath $Bin) 'binary_present'
  $prior=Get-Content (Join-Path $Base 'TS-BEADS-CONTINUITY-PILOT-20261013-001\result.json') -Raw|ConvertFrom-Json
  Assert (((Get-FileHash -LiteralPath $Bin -Algorithm SHA256).Hash.ToLowerInvariant()) -ceq ([string]$prior.bd_binary_sha256)) 'original_binary_sha256'
  $drive=Get-PSDrive -Name ([IO.Path]::GetPathRoot($Workspace).Substring(0,1))
  Assert ($drive.Free -gt 1073741824) 'disk_free'
  $stage='INIT_NEW_STORE'
  New-Item -ItemType Directory -Path (Join-Path $Workspace 'data') -Force|Out-Null
  [void](InvokeBD @('init','--quiet','--stealth'))
  $stage='SYNTHETIC_GRAPH'
  $objOrigin=@(GetBDJson @('create','Pipeline A origin','--description',('ORIGIN_REF='+$Checkpoint),'--type','task','--json'))[0]
  $idOrigin=[string]$objOrigin.id
  Assert ([bool]$idOrigin) 'origin_id'
  [void](InvokeBD @('update',$idOrigin,'--status','in_progress','--json'))
  $objDependency=@(GetBDJson @('create','Dependency B from module B','--description',('SOURCE_REF='+$Checkpoint),'--type','task','--json'))[0]
  $idDependency=[string]$objDependency.id
  [void](InvokeBD @('dep','add',$idDependency,$idOrigin,'--type','discovered-from'))
  $objResume=@(GetBDJson @('create','Pipeline A resume after B','--description',('CHECKPOINT_REF='+$Checkpoint),'--type','task','--json'))[0]
  $idResume=[string]$objResume.id
  [void](InvokeBD @('dep','add',$idResume,$idDependency))
  $objPeer=@(GetBDJson @('create','Independent pipeline C task','--type','task','--json'))[0]
  $idPeer=[string]$objPeer.id
  Assert ($idOrigin -ne $idDependency -and $idDependency -ne $idResume -and $idPeer -ne $idResume) 'unique_ids'
  $r.refs=[ordered]@{origin=$idOrigin;dependency=$idDependency;resume=$idResume;peer=$idPeer}
  WriteReceipt (Join-Path $Workspace 'identities.json') $r.refs
  $stage='INDEPENDENT_PRECHECK'
  Fresh 'before'
  $stage='SIMULATED_DEPENDENCY_RESOLUTION'
  [void](InvokeBD @('close',$idDependency,'--reason','Simulated competent dependency result; NO Product authority.','--json'))
  $stage='FRESH_PROCESS_RESUME'
  Fresh 'resume'
  $stage='INDEPENDENT_TERMINAL_READBACK'
  Fresh 'verify'
  $reader=Get-Content (Join-Path $Workspace 'readback.json') -Raw|ConvertFrom-Json
  Assert ($reader.status -eq 'PASS') 'reader'
  $r.readback=$reader
  $r.status='PASS_SYNTHETIC_CONTINUITY'
  $stage='TERMINAL'
}catch{
  $r.status=if($stage -eq 'PREFLIGHT'){'BLOCKED_PRECONDITION'}else{'FAIL_RECONCILIATION_REQUIRED'}
  $r.error=$_.Exception.Message
}finally{
  $r.stage=$stage;$r.completed_utc=[datetime]::UtcNow.ToString('o')
  if(Test-Path $Workspace){try{WriteReceipt (Join-Path $Workspace 'result.json') $r}catch{}}
  [ordered]@{attempt=$Attempt;status=$r.status;stage=$stage;refs=$r.refs;receipt=(Join-Path $Workspace 'result.json');error=$r.error}|ConvertTo-Json -Depth 4 -Compress|Write-Output
}
if($r.status -ne 'PASS_SYNTHETIC_CONTINUITY'){exit 1}
