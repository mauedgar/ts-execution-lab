# TS-BEADS 047B V6P3R2 F001 — SOURCE-ONLY synthetic stage identity test.
# Never imports or invokes the real fixture, Dolt, SQL, Beads, network, or Product.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$source=Join-Path $PSScriptRoot '..\candidate\Invoke-047B-V6-Fixture.ps1'
if(-not [IO.File]::Exists($source)){throw 'RUNNER_MISSING'}
$tokens=$null
$errors=$null
$tree=[Management.Automation.Language.Parser]::ParseFile($source,[ref]$tokens,[ref]$errors)
if(@($errors).Count){throw ('SOURCE_PARSE_FAILURE_'+(@($errors) -join '; '))}
$required=@('Reset-V6ChildStage','Mark-V6ChildStarted','Invoke-SqlStage')
foreach($name in $required){
  $matches=@($tree.FindAll({
    param($n)
    $n -is [Management.Automation.Language.FunctionDefinitionAst] -and
    $n.Name -ceq $name
  },$true))
  if($matches.Count -ne 1){throw ('SOURCE_FUNCTION_IDENTITY_'+$name)}
  # Extract only these original functions; never execute top-level runner code.
  . ([scriptblock]::Create($matches[0].Extent.Text))
}
$script:Events=[Collections.Generic.List[object]]::new()
function Assert-V6NoReparse { param([object]$Path) }
function Assert-V6PrivateAcl { param([object]$Path,[object]$Strict) }
function Assert-V6NoNetworkExposure { }
function Assert-V6 {param($Condition,$Reason) if(-not $Condition){throw $Reason}}
# This local mock is read-only: avoids hashing/reading a missing child binary.
function Get-FileHash {param($LiteralPath,$Algorithm) [pscustomobject]@{Hash='SYNTHETIC_NO_CHILD'} }
function Record {
  param([string]$Event,[hashtable]$Fields)
  $script:Events.Add([pscustomobject]@{
    event=$Event;stage=$script:LastStage;fields=$Fields
  })
}
$script:Spawned=$false
$script:ConfirmedStages=0
$script:ChildProcessId=$null
$script:CurrentStagePid=$null
$script:ChildExitConfirmed=$false
$script:ChildEffectAmbiguous=$false
Reset-V6ChildStage 'STAGE_ONE_SYNTHETIC'
Mark-V6ChildStarted 41041
$script:ChildExitConfirmed=$true
$script:ConfirmedStages=1
$script:StageInFlight=$false
if(-not $script:Spawned -or $script:CurrentStagePid -ne 41041){throw 'FIRST_STAGE_SIMULATION_FAILED'}
# A nonexistent binary path guarantees Start() raises BEFORE any child exists.
# No SQL interpreter can run. This tests the exact original function's catch path.
$fake=Join-Path $env:TEMP 'TS047B_V6P3R2_NO_SUCH_EXECUTABLE_414141.exe'
if([IO.File]::Exists($fake)){throw 'FAKE_CHILD_PATH_EXISTS'}
$failure=$null
try {
  [void](Invoke-SqlStage $fake $env:TEMP $env:TEMP (Join-Path $env:TEMP 'NO_PRIVILEGE_FILE') 'NOT_SQL_EXECUTED' 'STAGE_TWO_START_FAIL')
} catch {
  $failure=$_.Exception.GetType().FullName
}
if([string]::IsNullOrEmpty($failure)){throw 'STAGE_TWO_DID_NOT_FAIL'}
$ambiguous=@($script:Events | Where-Object {$_.event -ceq 'CHILD_AMBIGUOUS'})
$intent=@($script:Events | Where-Object {$_.event -ceq 'SPAWN_INTENT'})
if($ambiguous.Count -ne 1 -or $intent.Count -ne 1){throw 'MISSING_SYNTHETIC_RECEIPTS'}
$x=$ambiguous[0]
if($x.stage -cne 'STAGE_TWO_START_FAIL'){throw 'WRONG_STAGE'}
if($null -ne $x.fields.pid){throw 'F001_STALE_PRIOR_PID'}
if($x.fields.currentStageSpawned -ne $false){throw 'F001_STAGE_SPAWN_WRONGLY_TRUE'}
if($x.fields.everSpawned -ne $true){throw 'HISTORY_LOST'}
if($x.fields.startAttempted -ne $true){throw 'START_ATTEMPT_MISSING'}
if($x.fields.reconciled -ne $false){throw 'FALSE_RECONCILIATION'}
if($script:ConfirmedStages -ne 1 -or $script:ChildExitConfirmed -ne $false){throw 'STAGE_COUNTER_INCORRECT'}
if($script:ChildEffectAmbiguous -ne $true -or $script:CurrentStagePid -ne $null){throw 'UNKNOWN_NOT_PRESERVED'}
[pscustomobject]@{state='PASS_F001_STAGE_PID_SYNTHETIC_SOURCE_ONLY';confirmedStages=1;stage2Pid=$x.fields.pid;historicalSpawned=$x.fields.everSpawned;childExecuted=$false;sqlExecuted=$false;beadsMutated=$false;productEffect=$false}
