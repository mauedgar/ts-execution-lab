# F001 advisory A001: post-Start() receipt-write failure after a BENIGN child.
# Source-only experimental hosted Windows test; NEVER invokes actual Dolt/SQL.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$runner=Join-Path $PSScriptRoot '..\candidate\Invoke-047B-V6-Fixture.ps1'
$tokens=$null; $errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($runner,[ref]$tokens,[ref]$errors)
if(@($errors).Count -ne 0){throw 'F001_RUNNER_PARSE_ERROR'}
foreach($name in @('Reset-V6ChildStage','Mark-V6ChildStarted','Invoke-SqlStage')){
  $hits=@($ast.FindAll({param($node)
    $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -ceq $name
  },$true))
  if($hits.Count -ne 1){throw ('FUNCTION_IDENTITY_'+$name)}
  . ([scriptblock]::Create($hits[0].Extent.Text))
}
function Assert-V6NoReparse {param($Path)}
function Assert-V6PrivateAcl {param($Path,$RequireFile)}
function Assert-V6NoNetworkExposure {}
function Assert-V6 {param($Condition,$Reason) if(-not $Condition){throw $Reason}}
function Get-FileHash {param($LiteralPath,$Algorithm) [pscustomobject]@{Hash='BENIGN_WINDOWS_BINARY'} }
$script:Events=[Collections.Generic.List[object]]::new()
$script:ChildStartedWriteAttempted=$false
function Record {
  param([string]$Event,[hashtable]$Fields)
  if($Event -ceq 'CHILD_STARTED'){
    $script:ChildStartedWriteAttempted=$true
    throw 'SYNTHETIC_CHILD_STARTED_LOGGER_FAILURE'
  }
  $script:Events.Add([pscustomobject]@{event=$Event;stage=$script:LastStage;fields=$Fields})
}
$script:Spawned=$false
$script:CurrentStageSpawned=$false
$script:CurrentStagePid=$null
$script:ChildProcessId=$null
$script:ChildStartAttempted=$false
$script:ConfirmedStages=0
$script:ChildEffectAmbiguous=$false
$script:ChildExitConfirmed=$false
$script:StageInFlight=$false
# whoami is a fixed Windows OS utility, invoked with unwanted flags; it does
# not parse or execute the fixture's SQL input. Exchange is never reached.
$whoami=Join-Path $env:WINDIR 'System32\whoami.exe'
if(-not [IO.File]::Exists($whoami)){throw 'BENIGN_OS_PROCESS_MISSING'}
$priv=Join-Path $env:TEMP 'TS047B_NO_PRIVILEGE_V6P3R2.db'
if([IO.File]::Exists($priv)){throw 'UNEXPECTED_PRIVILEGE_PATH'}
$originalError=$null
try{
  [void](Invoke-SqlStage $whoami $env:TEMP $env:TEMP $priv 'NOT_SQL' 'BENIGN_POST_START')
}catch{
  $originalError=$_.Exception.Message
}
if(-not $script:ChildStartedWriteAttempted){throw 'POST_START_LOGGER_PATH_NOT_REACHED'}
if($originalError -cne 'SYNTHETIC_CHILD_STARTED_LOGGER_FAILURE'){throw ('WRONG_EXCEPTION_'+$originalError)}
$intent=@($script:Events | Where-Object {$_.event -ceq 'SPAWN_INTENT'})
$ambiguous=@($script:Events | Where-Object {$_.event -ceq 'CHILD_AMBIGUOUS'})
if($intent.Count -ne 1 -or $ambiguous.Count -ne 1){throw 'MISSING_OBSERVED_EVENTS'}
$x=$ambiguous[0]
if($x.stage -cne 'BENIGN_POST_START'){throw 'UNEXPECTED_STAGE'}
if(-not $script:Spawned -or -not $script:CurrentStageSpawned){throw 'POST_START_SPAWN_STATUS_LOST'}
if($null -eq $script:CurrentStagePid -or $script:CurrentStagePid -le 0){throw 'POSITIVE_CURRENT_PID_MISSING'}
if($script:CurrentStagePid -ne $script:ChildProcessId -or $x.fields.pid -ne $script:CurrentStagePid){throw 'F001_WRONG_POSTSTART_PID'}
if($x.fields.reconciled -ne $false -or $script:ChildEffectAmbiguous -ne $true -or $script:StageInFlight -ne $true){throw 'UNKNOWN_INCORRECTLY_RESOLVED'}
if($script:ConfirmedStages -ne 0 -or $script:ChildExitConfirmed -ne $false){throw 'STAGE_FALSE_SUCCESS'}
[pscustomobject]@{state='PASS_F001_POSTSTART_PID_AMBIGUOUS';childClass='BENIGN_OS_WHOAMI_ONLY';currentPidConfirmed=$true;receiptFailureSimulated=$true;sqlExecuted=$false;beadsMutated=$false;productEffect=$false}
