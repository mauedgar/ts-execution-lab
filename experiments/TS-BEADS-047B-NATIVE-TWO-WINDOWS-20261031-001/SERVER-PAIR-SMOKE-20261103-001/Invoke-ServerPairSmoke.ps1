# Experimental one-time Windows CI on ephemeral runner only.
# Neither this source nor its completion authorizes SQL/Tailscale on notebook/desktop.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$DoltExe,
    [Parameter(Mandatory)][string]$BeadsExe
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { throw 'WINDOWS_ONLY' }
if ($env:GITHUB_ACTIONS -cne 'true' -or $env:RUNNER_ENVIRONMENT -cne 'github-hosted') {
    throw 'ONLY_EPHEMERAL_GITHUB_HOSTED_RUNNER'
}
if ($env:GITHUB_RUN_ATTEMPT -cne '1') { throw 'NO_RUN_RERUN' }
if (-not [IO.File]::Exists($DoltExe) -or -not [IO.File]::Exists($BeadsExe)) {
    throw 'PINNED_BINARIES_MISSING'
}

# The only writable location is the disposable runner's unique temp directory.
$root = Join-Path $env:RUNNER_TEMP 'ts047b-only-local-server-pair-20261103-001'
if (Test-Path -LiteralPath $root) { throw 'DISPOSABLE_ROOT_ALREADY_EXISTS' }
[IO.Directory]::CreateDirectory($root) | Out-Null
$dataDir = Join-Path $root 'data'
$clientA = Join-Path $root 'client-a'
$clientB = Join-Path $root 'client-b'
foreach ($folder in @($dataDir,$clientA,$clientB)) {
    [IO.Directory]::CreateDirectory($folder) | Out-Null
}
$port = 14337
if (@(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object LocalPort -eq $port).Count -ne 0) {
    throw 'ISOLATED_PORT_OCCUPIED'
}
if (@(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object LocalPort -eq 3307).Count -ne 0) {
    throw 'PRODUCTION_LIKE_PORT_OCCUPIED'
}
$server = $null

function Invoke-BoundedNative {
    param(
        [string]$Exe,
        [string[]]$ArgsList,
        [string]$Cwd,
        [hashtable]$ExtraEnv = @{},
        [AllowNull()][string]$StandardInput = $null,
        [int]$TimeoutMs = 90000
    )
    $psi = [Diagnostics.ProcessStartInfo]::new($Exe)
    $psi.UseShellExecute = $false
    $psi.WorkingDirectory = $Cwd
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    foreach ($a in $ArgsList) { [void]$psi.ArgumentList.Add($a) }
    foreach ($key in $ExtraEnv.Keys) { $psi.Environment[$key] = [string]$ExtraEnv[$key] }
    $proc = [Diagnostics.Process]::new()
    $proc.StartInfo = $psi
    if (-not $proc.Start()) { throw 'NATIVE_PROCESS_DID_NOT_START' }
    $outTask = $proc.StandardOutput.ReadToEndAsync()
    $errTask = $proc.StandardError.ReadToEndAsync()
    if ($null -ne $StandardInput) { $proc.StandardInput.Write($StandardInput) }
    $proc.StandardInput.Close()
    if (-not $proc.WaitForExit($TimeoutMs)) {
        # No process kill / replay after an ambiguous external effect.
        throw 'UNKNOWN_NATIVE_PROCESS_TIMEOUT_NO_RETRY'
    }
    $outTask.Wait()
    $errTask.Wait()
    return [pscustomobject]@{
        Exit = $proc.ExitCode
        Stdout = $outTask.Result
        Stderr = $errTask.Result
    }
}

function Require-NativeSuccess {
    param([object]$Result,[string]$Marker)
    if ($Result.Exit -ne 0) {
        # Do not echo SQL or provider output: it may contain generated credentials.
        throw ('FAILED_'+$Marker+'_EXIT_'+$Result.Exit)
    }
}

# All credentials are local, random and short-lived; NEVER log or upload them.
$writerPw = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
$readerPw = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
$rootPw   = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
$writer = 'ts047b_writer_synth'
$reader = 'ts047b_reader_synth'
$dbName = 'ts047b_synthetic_pair'
$sql = @"
CREATE DATABASE $dbName;
CREATE USER '$writer'@'%' IDENTIFIED BY '$writerPw';
GRANT ALL PRIVILEGES ON $dbName.* TO '$writer'@'%';
CREATE USER '$reader'@'%' IDENTIFIED BY '$readerPw';
GRANT SELECT ON $dbName.* TO '$reader'@'%';
ALTER USER 'root'@'localhost' IDENTIFIED BY '$rootPw';
"@

$boot = Invoke-BoundedNative -Exe $DoltExe -ArgsList @('--data-dir', $dataDir, 'sql') -Cwd $root -StandardInput $sql
Require-NativeSuccess $boot 'OFFLINE_SYNTHETIC_SQL_BOOTSTRAP'
$sql = $null
$rootPw = $null
$privs = Join-Path $dataDir '.doltcfg\privileges.db'
if (-not (Test-Path -LiteralPath $privs)) { throw 'OFFLINE_PRIVILEGE_STORE_NOT_PERSISTED' }
'OFFLINE_SQL_PRIVILEGES_PERSISTED=PASS'

# Explicit loopback, no Tailscale, 0.0.0.0 or public SQL listener.
$serverLog = Join-Path $root 'private-server-stdout.log'
$serverErr = Join-Path $root 'private-server-stderr.log'
$server = Start-Process -FilePath $DoltExe -WorkingDirectory $root -ArgumentList @(
    'sql-server', '--host', '127.0.0.1', '--port', [string]$port, '--data-dir', $dataDir
) -RedirectStandardOutput $serverLog -RedirectStandardError $serverErr -PassThru

$connected = $false
foreach ($i in 1..50) {
    if ($server.HasExited) { throw 'LOCAL_SERVER_EXITED_EARLY' }
    $tcp = [Net.Sockets.TcpClient]::new()
    try {
        $job = $tcp.ConnectAsync('127.0.0.1', $port)
        if ($job.Wait(250) -and $tcp.Connected) { $connected = $true; break }
    } catch {} finally { $tcp.Dispose() }
    Start-Sleep -Milliseconds 300
}
if (-not $connected) { throw 'LOCAL_SERVER_NOT_READY_NO_RETRY' }
$listeners = @(Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction Stop)
if ($listeners.Count -eq 0 -or @($listeners | Where-Object LocalAddress -ne '127.0.0.1').Count -ne 0) {
    throw 'NON_LOOPBACK_LISTENER'
}
'ISOLATED_LOOPBACK_SERVER_READY=PASS'

# No secret in argv, CI output, persistent Git, Transport, or uploaded artifacts.
$common = @{
    BEADS_DOLT_SERVER_MODE = '1'
    BEADS_DOLT_SERVER_HOST = '127.0.0.1'
    BEADS_DOLT_SERVER_PORT = [string]$port
    BEADS_DOLT_SERVER_USER = $writer
    BEADS_DOLT_PASSWORD = $writerPw
    BEADS_DOLT_SERVER_DB = $dbName
    BEADS_DOLT_SHARED_SERVER = '0'
    BEADS_TEST_MODE = '1'
}
foreach ($workspace in @($clientA,$clientB)) {
    $gitinit = Invoke-BoundedNative -Exe 'git.exe' -ArgsList @('init','--quiet') -Cwd $workspace
    Require-NativeSuccess $gitinit 'ISOLATED_GIT_INIT'
}
$initArgs = @(
    'init','--server','--server-host','127.0.0.1','--server-port',[string]$port,
    '--server-user',$writer,'--database',$dbName,'-p','ts047b','--skip-hooks','--quiet'
)
$initA = Invoke-BoundedNative -Exe $BeadsExe -ArgsList $initArgs -Cwd $clientA -ExtraEnv $common
Require-NativeSuccess $initA 'CLIENT_A_SERVER_INIT'
$metadataA = Join-Path $clientA '.beads\metadata.json'
if (-not (Test-Path -LiteralPath $metadataA)) { throw 'CLIENT_A_METADATA_MISSING' }
$metadata = Get-Content -LiteralPath $metadataA -Raw | ConvertFrom-Json
$metadataJson = Get-Content -LiteralPath $metadataA -Raw
if ($metadataJson -notmatch 'server') { throw 'CLIENT_A_NOT_SERVER_MODE' }
'BEADS_CLIENT_A_INIT_SERVER_MODE=PASS'

# Confirm a native write/read cycle and an independent fresh second client.
$created = Invoke-BoundedNative -Exe $BeadsExe -ArgsList @(
    'create','TS047B public synthetic alpha','--type','task','--json'
) -Cwd $clientA -ExtraEnv $common
Require-NativeSuccess $created 'CLIENT_A_CREATE'
try { $record = $created.Stdout | ConvertFrom-Json -ErrorAction Stop } catch { throw 'CLIENT_A_CREATE_JSON_INVALID' }
$id = [string]$record.id
if ([string]::IsNullOrWhiteSpace($id) -or $id -notmatch '^ts047b-') { throw 'SYNTHETIC_ISSUE_ID_INVALID' }
$showA = Invoke-BoundedNative -Exe $BeadsExe -ArgsList @('show',$id,'--json') -Cwd $clientA -ExtraEnv $common
Require-NativeSuccess $showA 'CLIENT_A_SHOW'
if ($showA.Stdout -notmatch [regex]::Escape($id)) { throw 'CLIENT_A_READ_AFTER_WRITE_FAILED' }
'BEADS_CLIENT_A_WRITE_READ=PASS'

$initB = Invoke-BoundedNative -Exe $BeadsExe -ArgsList $initArgs -Cwd $clientB -ExtraEnv $common
Require-NativeSuccess $initB 'CLIENT_B_FRESH_INIT'
$metadataB = Join-Path $clientB '.beads\metadata.json'
if (-not (Test-Path -LiteralPath $metadataB)) { throw 'CLIENT_B_METADATA_MISSING' }
$showB = Invoke-BoundedNative -Exe $BeadsExe -ArgsList @('show',$id,'--json') -Cwd $clientB -ExtraEnv $common
Require-NativeSuccess $showB 'CLIENT_B_READ_SAME_DB'
if ($showB.Stdout -notmatch [regex]::Escape($id)) { throw 'SHADOW_DATABASE_OR_PROJECT_ID_MISMATCH' }
'BEADS_FRESH_CLIENT_B_SHARED_STATE=PASS'

# Negative authentication and read-only mutation tests, fail closed.
$badEnv = $common.Clone()
$badEnv['BEADS_DOLT_PASSWORD'] = 'SYNTHETIC_WRONG_PASSWORD'
$bad = Invoke-BoundedNative -Exe $BeadsExe -ArgsList @('list','--json') -Cwd $clientA -ExtraEnv $badEnv -TimeoutMs 30000
if ($bad.Exit -eq 0) { throw 'WRONG_PASSWORD_ACCEPTED' }
'WRONG_SQL_PASSWORD_REJECTED=PASS'
$readerEnv = $common.Clone()
$readerEnv['BEADS_DOLT_SERVER_USER'] = $reader
$readerEnv['BEADS_DOLT_PASSWORD'] = $readerPw
$denied = Invoke-BoundedNative -Exe $BeadsExe -ArgsList @(
    'create','TS047B forbidden reader mutation','--type','task','--json'
) -Cwd $clientA -ExtraEnv $readerEnv -TimeoutMs 30000
if ($denied.Exit -eq 0) { throw 'READ_ONLY_SQL_ACTOR_MUTATED' }
'READ_ONLY_SQL_MUTATION_REJECTED=PASS'

$closed = Invoke-BoundedNative -Exe $BeadsExe -ArgsList @('close',$id) -Cwd $clientB -ExtraEnv $common
Require-NativeSuccess $closed 'CLIENT_B_CLOSE'
$final = Invoke-BoundedNative -Exe $BeadsExe -ArgsList @('show',$id,'--json') -Cwd $clientA -ExtraEnv $common
Require-NativeSuccess $final 'CLIENT_A_FINAL_READ'
if ($final.Stdout -notmatch '"status"\s*:\s*"closed"') { throw 'SHARED_CLOSE_NOT_VISIBLE' }
'BEADS_CLIENT_B_CLOSE_VISIBLE_TO_A=PASS'

# Only the original server process created here, after all gates passed.
if (-not $server.HasExited) {
    Stop-Process -Id $server.Id -ErrorAction Stop
    $server.WaitForExit(10000) | Out-Null
}
$writerPw = $null; $readerPw = $null
'SERVER_PAIR_SYNTHETIC_FUNCTIONAL_PASS'
'PRODUCT_WRITES=ZERO'
'TAILSCALE_CHANGED=FALSE'
'REAL_CLIENT_DATA=NONE'
