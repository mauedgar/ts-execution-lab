Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# STATIC_OFFLINE_BOOTSTRAP_CANDIDATE_FOR_IR only.  Importing this module has no effects.
$script:CandidateId = 'TS-BEADS-047B-OFFLINE-PRIVILEGE-CANDIDATE-20261101-001'
$script:FailureLabels = @(
    'MISSING_BINARY_OR_HASH','DISALLOWED_ROOT_PATH','MISSING_EXECUTION_GRANT','WRONG_HOST_OR_OWNER',
    'REPARSE_POINT_OR_UNPROTECTED_ACL','STALE_DB_OR_PRIVILEGE_FILE','PRIOR_EFFECT_UNKNOWN',
    'CSPRNG_OR_DPAPI_FAILURE','STDIN_UNAVAILABLE','UNSUPPORTED_CLI_GLOBAL_FLAGS','OFFLINE_SQL_CREATION_FAILURE',
    'UNEXPECTED_ROOT_ACCOUNT','PRIVILEGE_FILE_NOT_SAME_AS_FUTURE_CONFIG','PASSWORDLESS_ROOT',
    'BAD_WRITER_DDL','READER_MUTATION','POSTCONDITION_FAILURE'
)

function Stop-ChildProcess {
    param([System.Diagnostics.Process]$Process)
    if (-not $Process.HasExited) { $Process.Kill($true); $Process.WaitForExit(5000) | Out-Null }
}

function Invoke-PinnedNative {
    param(
        [Parameter(Mandatory)] [string] $DoltPath,
        [Parameter(Mandatory)] [string[]] $Arguments,
        [AllowEmptyString()] [string] $Stdin,
        [Parameter(Mandatory)] [int] $TimeoutSeconds,
        [string[]] $ForbiddenOutput = @()
    )
    # ArgumentList (not a shell command) prevents argument re-parsing. Secrets enter only StandardInput.
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = $DoltPath
    $psi.UseShellExecute = $false
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    foreach ($argument in $Arguments) { [void]$psi.ArgumentList.Add($argument) }
    $process = [System.Diagnostics.Process]::new(); $process.StartInfo = $psi
    if (-not $process.Start()) { throw 'MISSING_BINARY_OR_HASH: process did not start' }
    try {
        $process.StandardInput.Write($Stdin); $process.StandardInput.Close()
        if (-not $process.WaitForExit($TimeoutSeconds * 1000)) { Stop-ChildProcess $process; throw 'OFFLINE_SQL_CREATION_FAILURE: timeout; child killed' }
        $stdout = $process.StandardOutput.ReadToEnd(); $stderr = $process.StandardError.ReadToEnd()
        foreach ($forbidden in $ForbiddenOutput) {
            if ($forbidden -and ($stdout.Contains($forbidden) -or $stderr.Contains($forbidden))) {
                throw 'OFFLINE_SQL_CREATION_FAILURE: native output contains protected input'
            }
        }
        if ($process.ExitCode -ne 0) { throw "OFFLINE_SQL_CREATION_FAILURE: native exit $($process.ExitCode)" }
        return [pscustomobject]@{ ProcessId=$process.Id; ExitCode=$process.ExitCode; StdoutLength=$stdout.Length; StderrLength=$stderr.Length }
    } finally { $process.Dispose() }
}

function New-SecretMaterial {
    # Password exists only in process memory until sent to the redirected stdin stream.
    $bytes = [byte[]]::new(32)
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    $password = [Convert]::ToBase64String($bytes).Replace('+','A').Replace('/','B').Replace('=','C')
    $secure = ConvertTo-SecureString $password -AsPlainText -Force
    $entropy = [System.Text.Encoding]::UTF8.GetBytes($script:CandidateId)
    $protected = [System.Security.Cryptography.ProtectedData]::Protect($bytes,$entropy,[System.Security.Cryptography.DataProtectionScope]::CurrentUser)
    [Array]::Clear($bytes,0,$bytes.Length)
    return [pscustomobject]@{ Password=$password; SecurePassword=$secure; DpapiBlob=$protected }
}

function Invoke-OfflinePrivilegeBootstrap {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [hashtable] $Plan,
        # A review harness injects this delegate. Production use must explicitly inject Invoke-PinnedNative after independent approval.
        [Parameter(Mandatory)] [scriptblock] $NativeInvoker,
        [Parameter(Mandatory)] [scriptblock] $Probe,
        [Parameter(Mandatory)] [scriptblock] $SecretFactory
    )
    $receipt = [ordered]@{ Candidate=$script:CandidateId; Phase='PRECHECK'; Effects='none until injected native invoker'; NativeCalls=@() }
    foreach ($check in @('ExactPinnedBinary','NoPriorEffects','PortAvailable','SafeRootAndAcl','ExecutionGrant','ProviderFlags')) {
        $result = & $Probe $check $Plan
        if (-not $result.Ok) { throw "$($result.Label): PRECHECK/$check" }
    }
    $receipt.Phase = 'RANDOM_DPAPI_ACL'
    $secret = & $SecretFactory
    if (-not $secret.Password -or -not $secret.DpapiBlob) { throw 'CSPRNG_OR_DPAPI_FAILURE: secret factory incomplete' }
    if (-not (& $Probe 'ProtectedAcl' $Plan).Ok) { throw 'REPARSE_POINT_OR_UNPROTECTED_ACL: protected secret destination rejected' }

    $receipt.Phase = 'DOLT_INIT'
    $init = & $NativeInvoker @('--data-dir',$Plan.DataDir,'--doltcfg-dir',$Plan.ConfigDir,'--privilege-file',$Plan.PrivilegeFile,'init') '' @()
    $receipt.NativeCalls += [pscustomobject]@{ Phase='DOLT_INIT'; ProcessId=$init.ProcessId; ExitCode=$init.ExitCode }

    $receipt.Phase = 'OFFLINE_PRIVILEGE_PROVISION'
    $sql = @"
CREATE USER 'recovery_admin'@'localhost' IDENTIFIED BY '$($secret.Password)';
CREATE USER 'scoped_writer'@'localhost' IDENTIFIED BY '$($secret.Password)';
CREATE USER 'select_reader'@'localhost' IDENTIFIED BY '$($secret.Password)';
GRANT ALL PRIVILEGES ON *.* TO 'recovery_admin'@'localhost' WITH GRANT OPTION;
GRANT SELECT, INSERT, UPDATE, DELETE ON appdb.* TO 'scoped_writer'@'localhost';
GRANT SELECT ON appdb.* TO 'select_reader'@'localhost';
FLUSH PRIVILEGES;
"@
    $sqlResult = & $NativeInvoker @('--data-dir',$Plan.DataDir,'--doltcfg-dir',$Plan.ConfigDir,'--privilege-file',$Plan.PrivilegeFile,'sql') $sql @($secret.Password)
    $receipt.NativeCalls += [pscustomobject]@{ Phase='OFFLINE_PRIVILEGE_PROVISION'; ProcessId=$sqlResult.ProcessId; ExitCode=$sqlResult.ExitCode }
    $receipt.Phase = 'POSTCONDITION'
    $post = & $Probe 'Postconditions' $Plan
    if (-not $post.Ok) { throw "$($post.Label): no server start permitted" }
    $receipt.Phase = 'STOP_AWAIT_INDEPENDENT_REVIEW'; $receipt.Effects = 'candidate completed; no sql-server invocation in adapter'
    return [pscustomobject]$receipt
}

Export-ModuleMember -Function Invoke-OfflinePrivilegeBootstrap,Invoke-PinnedNative,New-SecretMaterial
