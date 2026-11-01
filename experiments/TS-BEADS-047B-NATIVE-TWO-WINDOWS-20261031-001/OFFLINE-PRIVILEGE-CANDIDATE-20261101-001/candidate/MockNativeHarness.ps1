Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$module = Join-Path $PSScriptRoot 'OfflinePrivilegeBootstrap.psm1'
Import-Module $module -Force
$labels = @('MISSING_BINARY_OR_HASH','DISALLOWED_ROOT_PATH','MISSING_EXECUTION_GRANT','WRONG_HOST_OR_OWNER','REPARSE_POINT_OR_UNPROTECTED_ACL','STALE_DB_OR_PRIVILEGE_FILE','PRIOR_EFFECT_UNKNOWN','CSPRNG_OR_DPAPI_FAILURE','STDIN_UNAVAILABLE','UNSUPPORTED_CLI_GLOBAL_FLAGS','OFFLINE_SQL_CREATION_FAILURE','UNEXPECTED_ROOT_ACCOUNT','PRIVILEGE_FILE_NOT_SAME_AS_FUTURE_CONFIG','PASSWORDLESS_ROOT','BAD_WRITER_DDL','READER_MUTATION','POSTCONDITION_FAILURE')
$plan = @{ DataDir='C:\isolated\data'; ConfigDir='C:\isolated\cfg'; PrivilegeFile='C:\isolated\cfg\privileges.db'; FutureConfigPrivilegeFile='C:\isolated\cfg\privileges.db' }
$calls = [System.Collections.Generic.List[object]]::new()
$native = {
    param([string[]]$Arguments,[string]$Stdin,[string[]]$Forbidden)
    if ($Arguments -contains 'sql-server') { throw 'downstream side effect forbidden' }
    if ($Arguments[-1] -eq 'sql' -and [string]::IsNullOrWhiteSpace($Stdin)) { throw 'STDIN_UNAVAILABLE' }
    if ($Arguments -match 'password|secret') { throw 'secret present in arguments' }
    $calls.Add([pscustomobject]@{Arguments=$Arguments; StdinLength=$Stdin.Length; ForbiddenCount=$Forbidden.Count})
    [pscustomobject]@{ ProcessId=4242 + $calls.Count; ExitCode=0 }
}
$probe = { param($check,$ignoredPlan) [pscustomobject]@{ Ok=$true; Label='' } }
$secrets = { [pscustomobject]@{ Password='mock-password-not-real'; DpapiBlob=[byte[]](1,2,3) } }
$positive = Invoke-OfflinePrivilegeBootstrap -Plan $plan -NativeInvoker $native -Probe $probe -SecretFactory $secrets
if ($positive.Phase -ne 'STOP_AWAIT_INDEPENDENT_REVIEW' -or $calls.Count -ne 2) { throw 'positive mock receipt invalid' }
$negative = foreach ($label in $labels) {
    $expectedLabel = $label
    $failingProbe = { param($check,$ignoredPlan) if ($check -eq 'ExactPinnedBinary') { [pscustomobject]@{Ok=$false;Label=$expectedLabel} } else { [pscustomobject]@{Ok=$true;Label=''} } }.GetNewClosure()
    try { Invoke-OfflinePrivilegeBootstrap -Plan $plan -NativeInvoker $native -Probe $failingProbe -SecretFactory $secrets | Out-Null; [pscustomobject]@{Label=$label;Result='FAILED_TO_REJECT'} }
    catch { [pscustomobject]@{Label=$label;Result=$(if ($_.Exception.Message -match [regex]::Escape($label)) {'REJECTED_BY_MOCK'} else {'WRONG_REJECTION'});Detail=$_.Exception.Message} }
}
if (@($negative | Where-Object Result -ne 'REJECTED_BY_MOCK').Count -ne 0) { throw 'negative labels not rejected with exact label' }
[pscustomobject]@{ Harness='deterministic-mock-native'; Candidate='TS-BEADS-047B-OFFLINE-PRIVILEGE-CANDIDATE-20261101-001'; PositivePhase=$positive.Phase; NativeCalls=$calls.Count; NegativeLabels=$negative; NoSqlServer=($calls.Arguments -notcontains 'sql-server') } | ConvertTo-Json -Depth 5
