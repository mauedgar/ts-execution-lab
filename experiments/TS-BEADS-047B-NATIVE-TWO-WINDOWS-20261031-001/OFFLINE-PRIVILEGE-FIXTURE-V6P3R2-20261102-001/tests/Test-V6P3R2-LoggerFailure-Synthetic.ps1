# F001 synthetic second-stage Start() failure plus receipt logger loss.
# Extract only functions; never invoke top-level SQL fixture or a real child.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$p=Join-Path $PSScriptRoot '..\candidate\Invoke-047B-V6-Fixture.ps1'
$tokens=$null;$errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($p,[ref]$tokens,[ref]$errors)
if(@($errors).Count -ne 0){throw 'PARSE_FAIL'}
foreach($name in @('Reset-V6ChildStage','Mark-V6ChildStarted','Invoke-SqlStage')){
  $items=@($ast.FindAll({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -ceq $name},$true))
  if($items.Count -ne 1){throw ('FUNCTION_MISMATCH_'+$name)}
  . ([scriptblock]::Create($items[0].Extent.Text))
}
function Assert-V6NoReparse {param($Path)}
function Assert-V6PrivateAcl {param($Path,$Strict)}
function Assert-V6NoNetworkExposure {}
function Assert-V6 {param($Condition,$Reason) if(-not $Condition){throw $Reason}}
function Get-FileHash {param($LiteralPath,$Algorithm) [pscustomobject]@{Hash='SYNTHETIC'} }
$script:Observed=[Collections.Generic.List[string]]::new()
function Record {
  param([string]$Event,[hashtable]$Fields)
  if($Event -ceq 'CHILD_AMBIGUOUS'){throw 'SYNTHETIC_LOGGER_UNAVAILABLE'}
  $script:Observed.Add($Event)
}
$script:Spawned=$false
$script:ChildProcessId=$null
$script:CurrentStagePid=$null
$script:ConfirmedStages=0
Reset-V6ChildStage 'STAGE_ONE'
Mark-V6ChildStarted 51515
$script:ChildExitConfirmed=$true
$script:ConfirmedStages=1
$script:StageInFlight=$false
$badExe=Join-Path $env:TEMP 'TS047B_NO_CHILD_NO_SQL_V6P3R2_51515.exe'
if([IO.File]::Exists($badExe)){throw 'UNSAFE_FAKE_CHILD_PATH'}
$err=$null
try {[void](Invoke-SqlStage $badExe $env:TEMP $env:TEMP (Join-Path $env:TEMP 'MISSING_PRIVILEGE_FILE') 'NO_SQL' 'STAGE_TWO')}
catch {$err=$_.Exception.Message}
if([string]::IsNullOrWhiteSpace($err)){throw 'START_FAILURE_SWALLOWED'}
if($script:ChildProcessId -ne $null -or $script:CurrentStagePid -ne $null){throw 'F001_STALE_PID_WITH_LOGGER_FAILURE'}
if($script:CurrentStageSpawned -ne $false -or $script:Spawned -ne $true){throw 'STAGE_HISTORY_MISMATCH'}
if($script:ChildEffectAmbiguous -ne $true -or $script:StageInFlight -ne $true){throw 'LOST_UNKNOWN_WITH_LOGGER_FAILURE'}
if($script:ConfirmedStages -ne 1 -or $script:ChildExitConfirmed -ne $false){throw 'CONFIRMED_STAGE_CORRUPTED'}
if(@($script:Observed).Count -ne 1 -or $script:Observed[0] -cne 'SPAWN_INTENT'){throw 'MISSING_DURABLE_INTENT_MOCK'}
[pscustomobject]@{state='PASS_F001_LOGGER_FAILURE_PRESERVES_UNKNOWN';priorPid=51515;currentPid=$script:CurrentStagePid;confirmedStages=1;childExecuted=$false;sqlExecuted=$false}
