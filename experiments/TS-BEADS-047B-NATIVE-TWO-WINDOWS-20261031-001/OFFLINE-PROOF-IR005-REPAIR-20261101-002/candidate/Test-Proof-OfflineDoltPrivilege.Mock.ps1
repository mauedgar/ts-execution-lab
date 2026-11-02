$ErrorActionPreference='Stop'
$scriptPath=Join-Path $PSScriptRoot 'Proof-OfflineDoltPrivilege.ps1'
function Assert-That($v,$m){if(-not $v){throw $m}}
function New-MockProvider([hashtable]$Change=@{}) {
  $calls=[Collections.Generic.List[string]]::new();$o=[ordered]@{Complete=$true;Reasons=@();Host='DESKTOP-DJLBEQH';Owner='DESKTOP-DJLBEQH\Orca';DoltPath='C:\Dolt\dolt.exe';DoltHash='BED880C0E6B522498A563FCD1F0FC1E25527BA07E66C1E0A85C2242B64DFD967';DoltVersion='dolt version 2.2.0';RootExists=$false;RootReparse=$false;RootAclSafe=$true;PrivilegeExists=$false;SqlListener=$false;ServeActive=$false;PriorReceipt=$false;PriorUnknown=$false};foreach($k in $Change.Keys){$o[$k]=$Change[$k]}
  $p=@{Calls=$calls;Observe={param($root)$calls.Add('Observe');[pscustomobject]$o};ReadGrant={throw 'must not read grant'};RunBounded={throw 'must not run process'}}
  foreach($key in @('Observe','ReadGrant','RunBounded')){$p[$key]=$p[$key].GetNewClosure()}
  $p
}
function Case($name,$change,$label,[switch]$Effect){$p=New-MockProvider $change;if($Effect){$r=& $scriptPath -Effect -ExecutionAttempt 'TS-BEADS-047B-FUTURE-20261102-001' -GrantFile mock.json -Provider $p}else{$r=& $scriptPath -Preflight -Provider $p};Assert-That ($r.Label -eq $label) "${name}: expected $label, got $($r.Label)";Assert-That (-not ($p.Calls -contains 'RunBounded')) "${name}: subprocess invoked";$name}
$results=@();$results+=Case 'provider absent' @{Complete=$false;Reasons=@('DOLT_BINARY_ABSENT')} 'INCOMPLETE_PROVIDER_OBSERVATION'
$results+=Case 'wrong binary hash' @{DoltHash='BAD'} 'WRONG_BINARY_HASH';$results+=Case 'existing root' @{RootExists=$true} 'ROOT_EXISTS';$results+=Case 'junction ancestor' @{RootReparse=$true} 'ROOT_JUNCTION';$results+=Case 'unsafe ACL' @{RootAclSafe=$false} 'ROOT_ACL';$results+=Case 'listener' @{SqlListener=$true} 'ACTIVE_LISTENER_SERVE';$results+=Case 'serve' @{ServeActive=$true} 'ACTIVE_LISTENER_SERVE';$results+=Case 'prior receipt' @{PriorReceipt=$true} 'PRIOR_UNKNOWN';$results+=Case 'prior unknown' @{PriorUnknown=$true} 'PRIOR_UNKNOWN'
$results+=Case 'effect grammar blocked' @{} 'PINNED_SQL_GRAMMAR_UNQUALIFIED' -Effect
[pscustomobject]@{status='REVIEW_REQUIRED';kind='bounded injected-provider mocks only';cases=$results;sqlExecuted=$false;empiricalPass=$false}|ConvertTo-Json -Depth 4
