# Beads v1.3.1 cross-run durable backup experiment. Synthetic. NONE_PRODUCT.
param([ValidateSet('produce','consume')][string]$Mode='produce',
  [string]$SourceRun='', [string]$SourceCommit='')
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
$Pilot='TS-BEADS-CROSSRUN-CONTINUITY-20261013-006'
$root=Join-Path $env:RUNNER_TEMP ('ts-beads-crossrun006-'+$Mode)
if(Test-Path -LiteralPath $root){throw 'ATTEMPT_DIRECTORY_ALREADY_PRESENT'}
New-Item -ItemType Directory -Path $root|Out-Null
$binArchive=Join-Path $root 'beads-v1.3.1.zip'
Invoke-WebRequest -Uri 'https://github.com/gastownhall/beads/releases/download/v1.3.1/beads_1.3.1_windows_amd64.zip' -OutFile $binArchive
$hash=(Get-FileHash -LiteralPath $binArchive -Algorithm SHA256).Hash.ToLowerInvariant()
if($hash -cne '48cd82e1d3e311c9bf9a5d6d67ad1a8542ae13d4e20c5bfb527656c5e666af76'){throw 'BINARY_ARCHIVE_SHA256_MISMATCH'}
$bindir=Join-Path $root 'binary'
Expand-Archive -LiteralPath $binArchive -DestinationPath $bindir
$bd=Get-ChildItem -LiteralPath $bindir -File -Recurse -Filter 'bd.exe'|Select-Object -First 1 -ExpandProperty FullName
if(-not $bd){throw 'BD_BINARY_MISSING'}
& $bd version
if($LASTEXITCODE -ne 0){throw 'BD_VERSION_FAILED'}
$work=Join-Path $root 'work'
New-Item -ItemType Directory -Path $work|Out-Null
$env:BEADS_DIR=Join-Path $work '.beads'
$transport=Join-Path $root 'transport'
New-Item -ItemType Directory -Path $transport|Out-Null
$backup=Join-Path $transport 'backup'
$origin='ts-execution-lab-6c0a11aa'
$dependency='ts-execution-lab-6c0b22bb'
$resume='ts-execution-lab-6c0c33cc'
$independent='ts-execution-lab-6c0d44dd'
$source='test://TS-BEADS-CROSSRUN-CONTINUITY-20261013-006/ORIGIN-A@CHECKPOINT-02'
function BdRaw([string[]]$Arguments) {
  $output=(& $bd @Arguments|Out-String).Trim()
  if($LASTEXITCODE -ne 0){throw ('BD_EXIT_NONZERO:' + ($Arguments -join ' '))}
  return $output
}
function BdJson([string[]]$Arguments) {
  $s=BdRaw $Arguments
  $o=$s.IndexOf('{'); $a=$s.IndexOf('[')
  $i=if($o -lt 0){$a}elseif($a -lt 0){$o}else{[Math]::Min($o,$a)}
  if($i -lt 0){throw 'BD_JSON_PAYLOAD_MISSING'}
  return ($s.Substring($i)|ConvertFrom-Json)
}
function Ensure([bool]$Yes,[string]$Reason){if(-not $Yes){throw ('GUARD_'+$Reason)}}
function Status([string]$Id) {return [string](@(BdJson @('show',$Id,'--json'))[0].status)}
function ReadyIds {return @(BdJson @('ready','--json')|ForEach-Object {[string]$_.id})}
function AuditFiles([string]$Directory) {
  $all=@(Get-ChildItem -LiteralPath $Directory -Recurse -File -Force)
  Ensure ($all.Count -gt 0) 'NONEMPTY_NATIVE_BACKUP'
  $result=@()
  foreach($f in $all){
    $result+=@{path=$f.FullName.Substring($Directory.Length+1).Replace('\','/');sha256=(Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash.ToLowerInvariant();size=$f.Length}
  }
  return @($result|Sort-Object path)
}
& $bd init --quiet --stealth
if($LASTEXITCODE -ne 0){throw 'ISOLATED_DB_INIT_FAILED'}
if($Mode -eq 'produce'){
  $argsList=@(
    @('create','Synthetic original pipeline A','--id',$origin,'--type','task','--description',('ORIGIN_REF='+$source),'--json'),
    @('create','Synthetic module B dependency','--id',$dependency,'--type','task','--description',('SOURCE_REF='+$source),'--json'),
    @('create','Synthetic pipeline A continuation','--id',$resume,'--type','task','--description',('CHECKPOINT_REF='+$source),'--json'),
    @('create','Synthetic independent C','--id',$independent,'--type','task','--json')
  )
  foreach($argv in $argsList){[void](BdJson $argv)}
  [void](BdRaw @('update',$origin,'--status','in_progress','--json'))
  [void](BdRaw @('dep','add',$resume,$dependency))
  [void](BdRaw @('dep','add',$dependency,$origin,'--type','discovered-from'))
  Ensure ((Status $origin) -eq 'in_progress') 'ORIGINAL_ACTIVE'
  Ensure ((Status $dependency) -eq 'open') 'DEPENDENCY_OPEN'
  $ready=ReadyIds
  Ensure (($ready -contains $dependency) -and ($ready -contains $independent) -and ($ready -notcontains $resume)) 'PRODUCER_DEPENDENCY_GRAPH'
  [void](BdRaw @('backup','init',$backup))
  [void](BdRaw @('backup','sync'))
  $files=AuditFiles $backup
  $receipt=[ordered]@{
    contract='ts-beads-crossrun-native-backup/v0-experimental'
    pilot=$Pilot;authority='NONE_PRODUCT';mode='produce'
    producer_run_id=[string]$env:GITHUB_RUN_ID
    producer_commit=[string]$env:GITHUB_SHA
    issued_utc=[DateTime]::UtcNow.ToString('o')
    binary_release='v1.3.1';binary_archive_sha256=$hash
    source_ref=$source; origin_id=$origin; dependency_id=$dependency
    resume_id=$resume;independent_id=$independent
    backup_type='native_bd_backup_sync_full_dolt'
    file_count=$files.Count;file_entries=$files
    initial_ready=$ready
  }
  $receipt|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $transport 'manifest.json') -Encoding utf8
  Write-Output ('TS_CROSSRUN_PRODUCE=PASS;run='+$env:GITHUB_RUN_ID+';filecount='+$files.Count+';ids='+$origin+','+$dependency+','+$resume+','+$independent)
}elseif($Mode -eq 'consume'){
  Ensure ([bool]$SourceRun -and [bool]$SourceCommit) 'SOURCE_IDENTITY_REQUIRED'
  $incoming=Join-Path $env:RUNNER_TEMP 'incoming'
  Ensure (Test-Path (Join-Path $incoming 'manifest.json')) 'SOURCE_MANIFEST_MISSING'
  $meta=Get-Content -LiteralPath (Join-Path $incoming 'manifest.json') -Raw|ConvertFrom-Json
  Ensure ($meta.contract -ceq 'ts-beads-crossrun-native-backup/v0-experimental' -and $meta.authority -ceq 'NONE_PRODUCT' -and $meta.mode -ceq 'produce') 'MANIFEST_CONTRACT'
  Ensure ($meta.producer_run_id -ceq $SourceRun -and $meta.producer_commit -ceq $SourceCommit) 'ORIGINAL_SOURCE_PIN'
  Ensure ($meta.source_ref -ceq $source -and $meta.origin_id -ceq $origin -and $meta.dependency_id -ceq $dependency -and $meta.resume_id -ceq $resume -and $meta.independent_id -ceq $independent) 'ORIGIN_AND_IDS_PIN'
  $retrieved=Join-Path $incoming 'backup'
  $items=@(AuditFiles $retrieved)
  Ensure ($items.Count -eq $meta.file_count) 'BACKUP_FILE_COUNT'
  foreach($entry in $meta.file_entries) {
    $found=@($items|Where-Object {$_.path -ceq $entry.path})
    Ensure ($found.Count -eq 1 -and $found[0].sha256 -ceq $entry.sha256 -and $found[0].size -eq $entry.size) ('BACKUP_HASH_'+$entry.path)
  }
  [void](BdRaw @('backup','restore','--force',$retrieved))
  Ensure ((Status $origin) -eq 'in_progress') 'ORIGIN_RESTORED'
  Ensure ((Status $dependency) -eq 'open') 'DEPENDENCY_RESTORED'
  Ensure ((Status $resume) -eq 'open') 'CONTINUATION_RESTORED'
  $ready=ReadyIds
  Ensure (($ready -contains $dependency) -and ($ready -contains $independent) -and ($ready -notcontains $resume)) 'BLOCKED_AND_INDEPENDENT_RESTORED'
  [void](BdRaw @('close',$dependency,'--reason','Synthetic dependency completed after native cross-run restore','--json'))
  $unblocked=ReadyIds
  Ensure ($unblocked -contains $resume) 'CONTINUATION_NEWLY_READY'
  [void](BdRaw @('close',$resume,'--reason','Synthetic continuation consumed after independent workflow','--json'))
  [void](BdRaw @('close',$origin,'--reason','Synthetic original completed from exact recovered checkpoint','--json'))
  $all=@(BdJson @('list','--all','--json','--limit','100'))
  Ensure ($all.Count -eq 4) 'EXACT_FOUR_RECORDS'
  Ensure ((Status $independent) -eq 'open' -and (Status $origin) -eq 'closed' -and (Status $dependency) -eq 'closed' -and (Status $resume) -eq 'closed') 'INDEPENDENCE_AND_TERMINALS'
  $receipt=[ordered]@{
    contract='ts-beads-crossrun-native-restore-result/v0-experimental';pilot=$Pilot;authority='NONE_PRODUCT'
    status='PASS_SYNTHETIC_CROSS_RUN_RESTORE';mode='consume'
    source_run_id=$SourceRun;source_commit=$SourceCommit;consumer_run_id=[string]$env:GITHUB_RUN_ID;consumer_commit=[string]$env:GITHUB_SHA
    source_ref=$source;record_count=$all.Count;verified_backup_file_count=$items.Count
    origin_id=$origin;dependency_id=$dependency;resume_id=$resume;independent_id=$independent
    restored_blocked_ready=$ready;after_resolution_ready=$unblocked;completed_utc=[DateTime]::UtcNow.ToString('o')
    limitation='Actions artifact time-bound; restoration requires explicit referenced original and manual workflow trigger'
  }
  $receipt|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $transport 'result.json') -Encoding utf8
  Write-Output ('TS_CROSSRUN_CONSUME=PASS;source_run='+$SourceRun+';consumer_run='+$env:GITHUB_RUN_ID+';records='+$all.Count)
}else{throw 'UNEXPECTED_MODE'}
