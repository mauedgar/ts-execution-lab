# TS-BEADS 047B A002 - isolated durable receipt on controller-process loss.
# No real SQL, Dolt, Beads, Product, or existing local notebook processes.
[CmdletBinding()]
param(
  [ValidateSet('Run','Produce','Child')][string]$Role='Run',
  [ValidateSet('Recorded','MissingPid')][string]$Case='Recorded',
  [string]$Directory='',
  [string]$Nonce=''
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
function Write-FirstRecord([string]$File,[hashtable]$Record) {
  if([IO.File]::Exists($File)){throw 'RECEIPT_ALREADY_PRESENT'}
  $line=($Record|ConvertTo-Json -Compress -Depth 5)+"`n"
  $b=[Text.UTF8Encoding]::new($false).GetBytes($line)
  $f=[IO.FileStream]::new($File,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
  try{$f.Write($b,0,$b.Length);$f.Flush($true)}finally{$f.Dispose()}
}
function Write-AppendedRecord([string]$File,[hashtable]$Record) {
  if(-not [IO.File]::Exists($File)){throw 'NO_SPAWN_INTENT'}
  $line=($Record|ConvertTo-Json -Compress -Depth 5)+"`n"
  $b=[Text.UTF8Encoding]::new($false).GetBytes($line)
  $f=[IO.FileStream]::new($File,[IO.FileMode]::Append,[IO.FileAccess]::Write,[IO.FileShare]::Read)
  try{$f.Write($b,0,$b.Length);$f.Flush($true)}finally{$f.Dispose()}
}
function New-ChildProcess([string]$Case,[string]$Directory,[string]$Nonce) {
  $exe=Join-Path $PSHOME 'pwsh.exe'
  if(-not [IO.File]::Exists($exe)){throw 'NO_PWSH_CHILD_BINARY'}
  $psi=[Diagnostics.ProcessStartInfo]::new()
  $psi.FileName=$exe
  $psi.UseShellExecute=$false
  $psi.CreateNoWindow=$true
  foreach($a in @('-NoLogo','-NoProfile','-NonInteractive','-File',$PSCommandPath,'-Role','Child','-Case',$Case,'-Directory',$Directory,'-Nonce',$Nonce)){
    [void]$psi.ArgumentList.Add($a)
  }
  $p=[Diagnostics.Process]::new()
  $p.StartInfo=$psi
  if(-not $p.Start()){throw 'CHILD_START_FAILED'}
  return $p
}
if($Role -eq 'Child') {
  $witness=Join-Path $Directory 'independent-child-witness.jsonl'
  $record=@{event='CHILD_SELF_ATTESTED';nonce=$Nonce;case=$Case;pid=[int]$PID;processStartUtc=[Diagnostics.Process]::GetCurrentProcess().StartTime.ToUniversalTime().ToString('o');utc=[datetimeoffset]::UtcNow.ToString('o')}
  Write-FirstRecord $witness $record
  # Keep the harmless child briefly alive; never write external state.
  [Threading.Thread]::Sleep(2500)
  exit 0
}
if($Role -eq 'Produce'){
  $journal=Join-Path $Directory 'controller-receipt.jsonl'
  Write-FirstRecord $journal @{event='SPAWN_INTENT';nonce=$Nonce;case=$Case;pid=$null;effect='NONE_AUTHORIZED';utc=[datetimeoffset]::UtcNow.ToString('o')}
  $p=New-ChildProcess $Case $Directory $Nonce
  if($Case -eq 'Recorded'){
    $start=$p.StartTime.ToUniversalTime().ToString('o')
    Write-AppendedRecord $journal @{event='CHILD_STARTED';nonce=$Nonce;case=$Case;pid=[int]$p.Id;processStartUtc=$start;reconciled=$false;utc=[datetimeoffset]::UtcNow.ToString('o')}
  }
  # Test-only abrupt stop: terminates THIS disposable controller without
  # running finally or invoking Stop-Process / killing another process.
  [Environment]::Exit(73)
  throw 'UNREACHABLE_AFTER_EXIT'
}
if($Role -ne 'Run'){throw 'UNKNOWN_ROLE'}
if(-not [string]::IsNullOrWhiteSpace($Directory)){throw 'RUN_USES_UNIQUE_EPHEMERAL_DIRECTORY_ONLY'}
if(-not [string]::IsNullOrWhiteSpace($Nonce)){throw 'RUN_CREATES_FRESH_NONCE'}
if([string]::IsNullOrWhiteSpace($env:RUNNER_TEMP)){throw 'HOSTED_RUNNER_TEMP_REQUIRED'}
$cases=@('Recorded','MissingPid')
foreach($c in $cases){
  $nonce=[guid]::NewGuid().ToString('N')
  $root=Join-Path $env:RUNNER_TEMP ('ts047b-a002-'+$nonce)
  if(Test-Path -LiteralPath $root){throw 'NON_FRESH_SCRATCH'}
  [void][IO.Directory]::CreateDirectory($root)
  $exe=Join-Path $PSHOME 'pwsh.exe'
  $psi=[Diagnostics.ProcessStartInfo]::new()
  $psi.FileName=$exe
  $psi.UseShellExecute=$false
  $psi.CreateNoWindow=$true
  foreach($a in @('-NoLogo','-NoProfile','-NonInteractive','-File',$PSCommandPath,'-Role','Produce','-Case',$c,'-Directory',$root,'-Nonce',$nonce)){
    [void]$psi.ArgumentList.Add($a)
  }
  $controller=[Diagnostics.Process]::new()
  $controller.StartInfo=$psi
  if(-not $controller.Start()){throw 'CONTROLLER_START_FAILED'}
  # Bounded wait on an OWNED short-lived producer (not Commander polling).
  if(-not $controller.WaitForExit(15000)){throw 'OWNED_TEST_CONTROLLER_NOT_TERMINAL'}
  if($controller.ExitCode -ne 73){throw ('WRONG_EXPECTED_CONTROLLER_EXIT_'+$controller.ExitCode)}
  $controller.Dispose()
  # One independent join after controller is terminal. This is not polling.
  [Threading.Thread]::Sleep(900)
  $journal=Join-Path $root 'controller-receipt.jsonl'
  $witness=Join-Path $root 'independent-child-witness.jsonl'
  if(-not [IO.File]::Exists($journal)){throw 'JOURNAL_NOT_DURABLE'}
  if(-not [IO.File]::Exists($witness)){throw 'WITNESS_NOT_DURABLE'}
  $events=@([IO.File]::ReadAllLines($journal,[Text.UTF8Encoding]::new($false)) | Where-Object {$_} | ForEach-Object {$_ | ConvertFrom-Json -AsHashtable})
  $w=@([IO.File]::ReadAllLines($witness,[Text.UTF8Encoding]::new($false)) | Where-Object {$_} | ForEach-Object {$_ | ConvertFrom-Json -AsHashtable})
  if($w.Count -ne 1 -or $w[0].event -cne 'CHILD_SELF_ATTESTED' -or $w[0].nonce -cne $nonce -or $w[0].case -cne $c){throw 'WITNESS_CORRELATION_FAILED'}
  if($events.Count -lt 1 -or $events[0].event -cne 'SPAWN_INTENT' -or $events[0].nonce -cne $nonce){throw 'INTENT_CORRELATION_FAILED'}
  if($null -ne $events[0].pid){throw 'SPAWN_INTENT_MUST_NOT_CLAIM_PID'}
  if($c -ceq 'Recorded'){
    if($events.Count -ne 2 -or $events[1].event -cne 'CHILD_STARTED'){throw 'CHILD_STARTED_NOT_DURABLE'}
    if($events[1].nonce -cne $nonce -or $events[1].pid -ne $w[0].pid){throw 'JOURNAL_WITNESS_PID_MISMATCH'}
    if($events[1].processStartUtc -cne $w[0].processStartUtc){throw 'PROCESS_CREATION_TIME_MISMATCH'}
    $disposition='IDENTITY_RECOVERABLE_LOCAL_ONLY_EFFECT_UNKNOWN'
  } else {
    if($events.Count -ne 1){throw 'UNEXPECTED_PID_RECORD_IN_MISSINGPID_CASE'}
    # Even with a separate child witness, the controller's original PID
    # record is absent. Never infer NO_CHILD or authorize a retry.
    $disposition='ORIGINAL_PID_ABSENT_EXTERNAL_JOIN_REQUIRED_NO_RETRY'
  }
  if([int]$w[0].pid -le 0){throw 'INVALID_WITNESS_PID'}
  [pscustomobject]@{
    state='PASS_A002_ISOLATED_CONTROLLER_EXIT_SOURCE_ONLY';case=$c;
    disposition=$disposition;originalControllerExit=73;
    controllerJournalEvents=$events.Count;independentWitnessCount=$w.Count;
    witnessNonceMatched=$true;processStartIdentityMatched=($c -ceq 'Recorded');
    sqlExecuted=$false;beadsMutated=$false;productEffect=$false;
    proofScope='SAME_HOST_FLUSHED_FILE_ONLY_NOT_HOST_CRASH_OR_CAS'
  }
}
