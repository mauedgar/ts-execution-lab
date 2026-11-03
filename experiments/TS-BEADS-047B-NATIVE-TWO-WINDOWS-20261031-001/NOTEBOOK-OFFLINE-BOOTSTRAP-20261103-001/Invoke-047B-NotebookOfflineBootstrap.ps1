# TS-BEADS 047B: experimental source candidate; NOT an effect grant.
# Default Inspect mode never creates directories, files or SQL effects.
[CmdletBinding()]
param(
    [ValidateSet('Inspect','Execute')][string]$Mode = 'Inspect',
    [string]$GrantPath = '',
    [string]$ExpectedGrantSha256 = '',
    [string]$ExpectedSourceSha256 = ''
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$attempt = 'TS047B_NOTEBOOK_OFFLINE_BOOTSTRAP_20261103_001'
$owner = 'DESKTOP-DJLBEQH'
$doltHash = 'DF49F737CB80FC0F32B02220C701F476D378F322FA1BB51D696728FDAE825B91'
$bdHash = '280517091DDA13CB195A39F991144771117B2BC26A4D472612F8FC9FD80F46E2'
$effectStarted = $false

function Assert-ExactFile {
    param([string]$Path,[string]$ExpectedHash,[string]$Kind)
    if (-not [IO.File]::Exists($Path)) { throw ('BLOCKED_'+$Kind+'_ABSENT') }
    if ((Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash -cne $ExpectedHash) {
        throw ('BLOCKED_'+$Kind+'_HASH')
    }
}
function Require-EmptyProxy {
    param([string]$Exe,[string]$Kind)
    # Do not print tailnet status: it can contain private host/peer identifiers.
    $s = (& $Exe $Kind status --json 2>$null | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $s -cne '{}') { throw 'BLOCKED_NONEMPTY_OR_UNKNOWN_TAILNET_PROXY' }
}
function Secure-Directory {
    param([string]$Path,[Security.Principal.SecurityIdentifier]$Sid)
    $security = [Security.AccessControl.DirectorySecurity]::new()
    $security.SetOwner($Sid)
    $security.SetAccessRuleProtection($true,$false)
    $inherit = [Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [Security.AccessControl.InheritanceFlags]::ObjectInherit
    $rule = [Security.AccessControl.FileSystemAccessRule]::new(
        $Sid,[Security.AccessControl.FileSystemRights]::FullControl,
        $inherit,[Security.AccessControl.PropagationFlags]::None,
        [Security.AccessControl.AccessControlType]::Allow)
    $security.AddAccessRule($rule)
    Set-Acl -LiteralPath $Path -AclObject $security -ErrorAction Stop
    $test = Get-Acl -LiteralPath $Path
    if (-not $test.AreAccessRulesProtected) { throw 'BLOCKED_ACL_INHERITANCE' }
    if (@($test.Access | Where-Object {
        $_.AccessControlType -eq [Security.AccessControl.AccessControlType]::Allow -and
        $_.IdentityReference -ne $Sid
    }).Count -ne 0) { throw 'BLOCKED_ACL_UNEXPECTED_PRINCIPAL' }
}
function Save-DpapiCurrentUser {
    param([string]$Path,[string]$Text)
    $bytes = [Text.Encoding]::UTF8.GetBytes($Text)
    try {
        $cipher = [Security.Cryptography.ProtectedData]::Protect(
            $bytes,$null,[Security.Cryptography.DataProtectionScope]::CurrentUser)
        [IO.File]::WriteAllBytes($Path,$cipher)
    } finally { [Array]::Clear($bytes,0,$bytes.Length) }
}
function Invoke-OfflineSql {
    param([string]$Exe,[string]$Cwd,[string]$DataRoot,[string]$Sql)
    $pinfo = [Diagnostics.ProcessStartInfo]::new($Exe)
    $pinfo.WorkingDirectory = $Cwd
    $pinfo.UseShellExecute = $false
    $pinfo.CreateNoWindow = $true
    $pinfo.RedirectStandardInput = $true
    $pinfo.RedirectStandardOutput = $true
    $pinfo.RedirectStandardError = $true
    foreach($a in @('--data-dir',$DataRoot,'sql')) { [void]$pinfo.ArgumentList.Add($a) }
    $p = [Diagnostics.Process]::new()
    $p.StartInfo = $pinfo
    if (-not $p.Start()) { throw 'UNKNOWN_NATIVE_START' }
    $outTask = $p.StandardOutput.ReadToEndAsync()
    $errTask = $p.StandardError.ReadToEndAsync()
    $p.StandardInput.Write($Sql)
    $p.StandardInput.Close()
    if (-not $p.WaitForExit(90000)) { throw 'UNKNOWN_NATIVE_TIMEOUT_NO_KILL' }
    $outTask.Wait()
    $errTask.Wait()
    if ($p.ExitCode -ne 0) { throw 'UNKNOWN_OR_PARTIAL_NATIVE_SQL_FAILURE' }
    # Do NOT echo subprocess output, SQL, secrets or errors.
}
try {
    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT -or
        [Environment]::MachineName -cne $owner) { throw 'BLOCKED_HOST' }
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    if ($null -eq $sid) { throw 'BLOCKED_IDENTITY' }
    $dolt = 'C:\Program Files\Dolt\bin\dolt.exe'
    $bd = Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages\GasTownHall.Beads_Microsoft.Winget.Source_8wekyb3d8bbwe\bd.exe'
    Assert-ExactFile $dolt $doltHash 'DOLT'
    Assert-ExactFile $bd $bdHash 'BD'
    $dv = ((& $dolt version 2>&1 | Select-Object -First 1) | Out-String).Trim()
    if ($dv -notmatch 'dolt version 2[.]6[.]2') { throw 'BLOCKED_DOLT_VERSION' }
    $bv = ((& $bd version 2>&1 | Select-Object -First 1) | Out-String).Trim()
    if ($bv -notmatch 'bd version 1[.]3[.]2') { throw 'BLOCKED_BD_VERSION' }
    if (@(Get-Process -Name dolt -ErrorAction SilentlyContinue).Count -ne 0) {
        throw 'BLOCKED_DOLT_RUNNING'
    }
    if (@(Get-NetTCPConnection -State Listen -ErrorAction Stop |
        Where-Object { $_.LocalPort -eq 3307 -or $_.LocalPort -eq 14337 }).Count -ne 0) {
        throw 'BLOCKED_SQL_LISTENER'
    }
    $ts = (Get-Command tailscale -ErrorAction Stop).Source
    Require-EmptyProxy $ts 'serve'
    Require-EmptyProxy $ts 'funnel'
    $root = Join-Path $env:LOCALAPPDATA 'TS-BEADS-047B'
    if (Test-Path -LiteralPath $root) { throw 'BLOCKED_EXISTING_ATTEMPT_OR_DATA' }

    if ($Mode -ceq 'Inspect') {
        'NOTEBOOK_READONLY_PREFLIGHT_PASS'
        'NO_SQL_OR_TAILSCALE_EFFECT'
        exit 0
    }

    # Local grant validation is a necessary precondition, NOT proof of Product authority.
    # Control MUST already have reconciled the immutable private Transport receipt.
    if ($ExpectedSourceSha256 -notmatch '^[A-Fa-f0-9]{64}$' -or
        $ExpectedGrantSha256 -notmatch '^[A-Fa-f0-9]{64}$' -or
        [string]::IsNullOrWhiteSpace($GrantPath)) {
        throw 'BLOCKED_GRANT_OR_SOURCE_PIN_ABSENT'
    }
    Assert-ExactFile $PSCommandPath $ExpectedSourceSha256 'RUNNER'
    Assert-ExactFile $GrantPath $ExpectedGrantSha256 'GRANT'
    $grant = Get-Content -LiteralPath $GrantPath -Raw | ConvertFrom-Json -ErrorAction Stop
    if ($grant.schema -cne 'TS047B_NOTEBOOK_SQL_GRANT_V1' -or
        $grant.attempt -cne $attempt -or
        $grant.ownerHost -cne $owner -or
        $grant.effect -cne 'OFFLINE_SYNTHETIC_SQL_BOOTSTRAP_ONLY' -or
        $grant.decision -cne 'ADMITTED' -or
        $grant.sourceSha256 -cne $ExpectedSourceSha256 -or
        [string]::IsNullOrWhiteSpace([string]$grant.originalTransportReceipt)) {
        throw 'BLOCKED_INCOMPLETE_GRANT'
    }

    # The following is an EFFECT. No source qualification invokes Execute.
    [IO.Directory]::CreateDirectory($root) | Out-Null
    Secure-Directory $root $sid
    $data = Join-Path $root 'data'
    $secretDir = Join-Path $root 'protected'
    foreach($dir in @($data,$secretDir)) {
        [IO.Directory]::CreateDirectory($dir) | Out-Null
        Secure-Directory $dir $sid
    }
    # Local marker is not a replacement for durable Transport original receipt.
    $nl = [Environment]::NewLine
    [IO.File]::WriteAllText((Join-Path $root 'ORIGINAL_ATTEMPT_STARTED.txt'),
        $attempt+$nl+'OFFLINE_SQL_EFFECT_PENDING_OR_UNKNOWN'+$nl)
    $rootPw = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
    $writerPw = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
    $readerPw = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
    $encoded = @{root=$rootPw;writer=$writerPw;reader=$readerPw} | ConvertTo-Json -Compress
    Save-DpapiCurrentUser (Join-Path $secretDir 'credentials.user.dpapi') $encoded
    $encoded = $null
    $sql = @"
CREATE DATABASE ts047b_beads;
CREATE USER 'ts047b_writer'@'%' IDENTIFIED BY '$writerPw';
GRANT ALL PRIVILEGES ON ts047b_beads.* TO 'ts047b_writer'@'%';
CREATE USER 'ts047b_reader'@'%' IDENTIFIED BY '$readerPw';
GRANT SELECT ON ts047b_beads.* TO 'ts047b_reader'@'%';
ALTER USER 'root'@'localhost' IDENTIFIED BY '$rootPw';
"@
    $effectStarted = $true
    Invoke-OfflineSql $dolt $root $data $sql
    $sql = $null
    $rootPw = $null; $writerPw = $null; $readerPw = $null
    if (-not (Test-Path -LiteralPath (Join-Path $data '.doltcfg\privileges.db'))) {
        throw 'UNKNOWN_PRIVILEGE_STORE_MISSING_NO_RETRY'
    }
    [IO.File]::WriteAllText((Join-Path $root 'OFFLINE_BOOTSTRAP_TERMINAL.txt'),
        $attempt+$nl+'OFFLINE_PRIVILEGE_FILE_OBSERVED'+$nl+'NO_SERVER_STARTED'+$nl)
    'OFFLINE_PRIVILEGE_FILE_OBSERVED'
    'SQL_SERVER_STARTED=FALSE'
    'TAILSCALE_MODIFIED=FALSE'
    'REQUIRES_EXTERNAL_RECEIPT_RECONCILIATION'
    exit 0
} catch {
    if ($effectStarted) {
        'UNKNOWN_OR_PARTIAL_OFFLINE_SQL_EFFECT_DO_NOT_RETRY_OR_CLEAN'
        exit 12
    }
    'BLOCKED_PRECONDITION_OR_PARTIAL_LOCAL_PREPARATION_DO_NOT_RETRY'
    exit 11
}
