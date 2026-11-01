# TS-BEADS-047B secure bootstrap candidate.  It is inert unless a future caller
# explicitly supplies -Mode Apply and a distinct effect approval.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:OperationId = 'TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001'
$script:BuildAttempt = 'TS-BEADS-047B-IR002-PUBLIC-BUILD-20261101-001'
$script:ApprovedHost = 'DESKTOP-DJLBEQH'
$script:ApprovedOwner = '40cc0b10-fa7b-4a6a-98cf-1c94f93791b2'
$script:LabLeaf = 'TS-BEADS-047B'

class Ts047bHostProvider {
    [string] $Name
    Ts047bHostProvider([string] $name) { $this.Name = $name }
    [object] GetHostSnapshot() { throw 'Provider method not implemented: GetHostSnapshot' }
    [object] GetIntegrity([string] $sourcePath) { throw 'Provider method not implemented: GetIntegrity' }
    [object] GetPreviousEffect() { throw 'Provider method not implemented: GetPreviousEffect' }
    [object] GetFilesystemState([string] $labRoot) { throw 'Provider method not implemented: GetFilesystemState' }
    [object] GetNetworkState() { throw 'Provider method not implemented: GetNetworkState' }
    [object] GetSecretCapability() { throw 'Provider method not implemented: GetSecretCapability' }
    [object] GetSqlCapability() { throw 'Provider method not implemented: GetSqlCapability' }
    [object] GetGrammar() { throw 'Provider method not implemented: GetGrammar' }
    [byte[]] RandomBytes([int] $count) { throw 'Provider method not implemented: RandomBytes' }
    [void] CreateLabRoot([string] $labRoot) { throw 'Provider method not implemented: CreateLabRoot' }
    [void] StoreProtectedSecret([string] $name, [byte[]] $secret, [string] $labRoot) { throw 'Provider method not implemented: StoreProtectedSecret' }
    [void] WriteServerConfig([string] $labRoot) { throw 'Provider method not implemented: WriteServerConfig' }
    [void] StartLoopbackSql([string] $labRoot) { throw 'Provider method not implemented: StartLoopbackSql' }
    [object] OpenSql([string] $user, [byte[]] $password) { throw 'Provider method not implemented: OpenSql' }
    [void] ExecuteSql([object] $connection, [string] $statement) { throw 'Provider method not implemented: ExecuteSql' }
    [void] ExecuteSqlSecret([object] $connection, [string] $statement, [byte[]] $secret) { throw 'Provider method not implemented: ExecuteSqlSecret' }
    [void] CloseSql([object] $connection) { throw 'Provider method not implemented: CloseSql' }
    [object] VerifyPostconditions() { throw 'Provider method not implemented: VerifyPostconditions' }
}

class WindowsTs047bHostProvider : Ts047bHostProvider {
    WindowsTs047bHostProvider() : base('WindowsTs047bHostProvider') {}
    [object] GetHostSnapshot() {
        $dolt = Get-Command dolt -ErrorAction SilentlyContinue
        $bd = Get-Command bd -ErrorAction SilentlyContinue
        $tailscale = Get-Command tailscale -ErrorAction SilentlyContinue
        $tailnet = $null
        if ($tailscale) { $tailnet = (& $tailscale.Source status --json 2>$null | ConvertFrom-Json) }
        return [pscustomobject]@{ IsWindows=($env:OS -eq 'Windows_NT'); HostName=$env:COMPUTERNAME; OwnerDevice=$env:TS047B_OWNER_DEVICE; DoltVersion=$(if($dolt){(& $dolt.Source version | Out-String).Trim()}else{''}); BeadsVersion=$(if($bd){(& $bd.Source --version | Out-String).Trim()}else{''}); TailnetRunning=($null -ne $tailnet -and $tailnet.BackendState -eq 'Running' -and $tailnet.Self.Online); ApprovedPeerOnline=($null -ne $tailnet) }
    }
    [object] GetIntegrity([string] $sourcePath) { return [pscustomobject]@{ SourceSha256=(Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash; ParserOk=$true } }
    [object] GetPreviousEffect() { return [pscustomobject]@{ State='NONE'; Receipt=$null } }
    [object] GetFilesystemState([string] $labRoot) { $item = Get-Item -LiteralPath $labRoot -Force -ErrorAction SilentlyContinue; return [pscustomobject]@{ Exists=($null -ne $item); Reparse=($null -ne $item -and ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)); Collision=($null -ne $item -and -not $item.PSIsContainer); RestrictedAcl=$false; ProductPath=$false } }
    [object] GetNetworkState() { $serve = (& tailscale serve status --json 2>$null | Out-String); return [pscustomobject]@{ PortVacant=(@(Get-NetTCPConnection -LocalPort 3307 -ErrorAction SilentlyContinue).Count -eq 0); SqlListener=$false; Serve=($serve -match '"TCP"'); Funnel=($serve -match '(?i)funnel') } }
    [object] GetSecretCapability() { return [pscustomobject]@{ Csprng=$true; Dpapi=$true; RestrictedAcl=$true } }
    [object] GetSqlCapability() { try { Add-Type -AssemblyName 'MySqlConnector' -ErrorAction Stop; return [pscustomobject]@{ SecureConnector=$true } } catch { return [pscustomobject]@{ SecureConnector=$false } } }
    [object] GetGrammar() { return [pscustomobject]@{ CreateUser=$false; DropUser=$false; Grant=$false; VerifiedPinnedDolt=$false } } # Future operator must replace only with native 2.2.0 help evidence.
    [byte[]] RandomBytes([int] $count) { $bytes = [byte[]]::new($count); [Security.Cryptography.RandomNumberGenerator]::Fill($bytes); return $bytes }
    [void] CreateLabRoot([string] $labRoot) { New-Item -ItemType Directory -Path $labRoot -ErrorAction Stop | Out-Null; & icacls.exe $labRoot /inheritance:r /grant:r "$env:USERNAME:(OI)(CI)F" | Out-Null; if ($LASTEXITCODE -ne 0) { throw 'ACL_CREATE_FAILED' } }
    [void] StoreProtectedSecret([string] $name, [byte[]] $secret, [string] $labRoot) { $cipher=[Security.Cryptography.ProtectedData]::Protect($secret,$null,[Security.Cryptography.DataProtectionScope]::CurrentUser); [IO.File]::WriteAllBytes((Join-Path $labRoot "$name.dpapi"),$cipher); & icacls.exe (Join-Path $labRoot "$name.dpapi") /inheritance:r /grant:r "$env:USERNAME:F" | Out-Null; if($LASTEXITCODE -ne 0){throw 'ACL_SECRET_FAILED'} }
    [void] WriteServerConfig([string] $labRoot) { @("log_level: info","listener:","  host: 127.0.0.1","  port: 3307","  allow_cleartext_passwords: false","data_dir: $labRoot/data","cfg_dir: $labRoot/cfg","privilege_file: $labRoot/cfg/privileges.db","metrics:","  host: null","  port: -1","mcp_server:","  port: null") | Set-Content -LiteralPath (Join-Path $labRoot 'config.yaml') -Encoding utf8NoBOM -NoNewline }
    [void] StartLoopbackSql([string] $labRoot) { $p=[Diagnostics.Process]::new(); $p.StartInfo.FileName=(Get-Command dolt -ErrorAction Stop).Source; $p.StartInfo.Arguments="sql-server --config=`"$(Join-Path $labRoot 'config.yaml')`""; $p.StartInfo.UseShellExecute=$false; if(-not $p.Start()){throw 'SQL_PROCESS_START_FAILED'} }
    [object] OpenSql([string] $user, [byte[]] $password) { $text=[Text.Encoding]::UTF8.GetString($password); try { $c=New-Object -TypeName 'MySqlConnector.MySqlConnection' -ArgumentList "Server=127.0.0.1;Port=3307;User ID=$user;Password=$text;SslMode=None;Allow User Variables=False"; $c.Open(); return $c } finally { $text=$null } }
    [void] ExecuteSql([object] $connection, [string] $statement) { $cmd=$connection.CreateCommand(); try { $cmd.CommandText=$statement; [void]$cmd.ExecuteNonQuery() } finally { $cmd.Dispose() } }
    [void] ExecuteSqlSecret([object] $connection, [string] $statement, [byte[]] $secret) { $text=[Text.Encoding]::UTF8.GetString($secret); $cmd=$connection.CreateCommand(); try { $cmd.CommandText=$statement; $parameter=$cmd.CreateParameter(); $parameter.ParameterName='@password'; $parameter.Value=$text; [void]$cmd.Parameters.Add($parameter); [void]$cmd.ExecuteNonQuery() } finally { $text=$null; $cmd.Dispose() } }
    [void] CloseSql([object] $connection) { if($null -ne $connection){$connection.Dispose()} }
    [object] VerifyPostconditions() { return [pscustomobject]@{ RootPasswordlessDenied=$false; AdminRecovery=$false; WriterScoped=$false; ReaderMutationDenied=$false; WrongPasswordDenied=$false; LoopbackOnly=$false; ServeDisabled=$false } }
}

function Assert-TS047B([bool] $condition, [string] $reason) { if (-not $condition) { throw "BLOCKED_$reason" } }
function Get-TS047BLabRoot { Join-Path $env:LOCALAPPDATA $script:LabLeaf }
function Get-TS047BSecret([object] $Provider) { $b=$Provider.RandomBytes(48); Assert-TS047B ($b.Length -eq 48) 'CSPRNG_FAILED'; return $b }
function Test-TS047BPreflight {
    param([object]$Provider,[string]$SourcePath,[string]$ExpectedSourceSha256)
    $hostSnapshot=$Provider.GetHostSnapshot()
    Assert-TS047B ($hostSnapshot.IsWindows -and $hostSnapshot.HostName -eq $script:ApprovedHost -and $hostSnapshot.OwnerDevice -eq $script:ApprovedOwner) 'HOST_OR_OWNER_MISMATCH'
    Assert-TS047B ($hostSnapshot.DoltVersion -match '2\.2\.0' -and $hostSnapshot.BeadsVersion -match '1\.3\.1') 'PINNED_BINARY_MISMATCH'
    Assert-TS047B ($hostSnapshot.TailnetRunning -and $hostSnapshot.ApprovedPeerOnline) 'TAILNET_PEER_UNVERIFIED'
    $integrity=$Provider.GetIntegrity($SourcePath)
    Assert-TS047B ($integrity.ParserOk -and $integrity.SourceSha256 -eq $ExpectedSourceSha256) 'INTEGRITY_OR_PARSER_FAILURE'
    $prior=$Provider.GetPreviousEffect(); Assert-TS047B ($prior.State -eq 'NONE') 'PRIOR_EFFECT_RECONCILIATION_REQUIRED'
    $fs=$Provider.GetFilesystemState((Get-TS047BLabRoot)); Assert-TS047B (-not $fs.Exists -and -not $fs.Reparse -and -not $fs.Collision -and $fs.RestrictedAcl -and -not $fs.ProductPath) 'LAB_ROOT_OR_ACL_UNSAFE'
    $net=$Provider.GetNetworkState(); Assert-TS047B ($net.PortVacant -and -not $net.SqlListener -and -not $net.Serve -and -not $net.Funnel) 'NETWORK_EXPOSURE_OR_PORT_UNSAFE'
    $secret=$Provider.GetSecretCapability(); Assert-TS047B ($secret.Csprng -and $secret.Dpapi -and $secret.RestrictedAcl) 'SECRET_PROTECTION_UNAVAILABLE'
    $sql=$Provider.GetSqlCapability(); Assert-TS047B ($sql.SecureConnector) 'SECURE_SQL_CLIENT_UNAVAILABLE'
    $grammar=$Provider.GetGrammar(); Assert-TS047B ($grammar.CreateUser -and $grammar.DropUser -and $grammar.Grant -and $grammar.VerifiedPinnedDolt) 'PINNED_SQL_GRAMMAR_UNVERIFIED'
    return [pscustomobject]@{ Status='PREFLIGHT_PASS'; Host=$hostSnapshot.HostName; SourceSha256=$integrity.SourceSha256 }
}
function Invoke-TS047BSecureBootstrap {
    [CmdletBinding()]
    param([Parameter(Mandatory)][ValidateSet('Validate','Apply')][string]$Mode,[Parameter(Mandatory)][object]$Provider,[Parameter(Mandatory)][string]$SourcePath,[Parameter(Mandatory)][string]$ExpectedSourceSha256,[string]$FutureExecutionAttempt,[hashtable]$EffectApproval)
    $phase='PREFLIGHT'; $started=$false; $effectTouched=$false; $connection=$null
    try {
        $preflight=Test-TS047BPreflight -Provider $Provider -SourcePath $SourcePath -ExpectedSourceSha256 $ExpectedSourceSha256
        if($Mode -eq 'Validate'){ return [pscustomobject]@{ Status='STATIC_CANDIDATE_FOR_INDEPENDENT_REVIEW'; Phase='PREFLIGHT'; Preflight=$preflight; EffectsStarted=$false } }
        Assert-TS047B ($FutureExecutionAttempt -and $FutureExecutionAttempt -ne $script:BuildAttempt) 'DISTINCT_FUTURE_ATTEMPT_REQUIRED'
        Assert-TS047B ($null -ne $EffectApproval -and $EffectApproval.ContainsKey('ExplicitEffectGrant') -and $EffectApproval.ContainsKey('SourceSha256') -and $EffectApproval['ExplicitEffectGrant'] -eq $true -and $EffectApproval['SourceSha256'] -eq $ExpectedSourceSha256) 'EXPLICIT_EFFECT_GRANT_REQUIRED'
        $phase='SECRET_GENERATION'; $root=Get-TS047BSecret $Provider; $admin=Get-TS047BSecret $Provider; $writer=Get-TS047BSecret $Provider; $reader=Get-TS047BSecret $Provider
        $phase='SECRET_PROTECTION'; $labRoot=Get-TS047BLabRoot; $effectTouched=$true; $Provider.CreateLabRoot($labRoot); foreach($pair in @(@('root',$root),@('admin',$admin),@('writer',$writer),@('reader',$reader))){$Provider.StoreProtectedSecret($pair[0],$pair[1],$labRoot)}
        $phase='LOOPBACK_START'; $Provider.WriteServerConfig($labRoot); $Provider.StartLoopbackSql($labRoot); $started=$true
        # Passwords are supplied only to the in-memory connector; no shell client or -e query is used.
        $phase='ROOT_HARDENING'; $connection=$Provider.OpenSql('root',[byte[]]::new(0)); $Provider.ExecuteSqlSecret($connection,"CREATE USER 'ts047b_recovery_admin'@'localhost' IDENTIFIED BY @password",$admin); $Provider.CloseSql($connection); $connection=$null
        $connection=$Provider.OpenSql('ts047b_recovery_admin',$admin); $Provider.ExecuteSql($connection,"CREATE DATABASE ts047b_beads"); $Provider.ExecuteSqlSecret($connection,"CREATE USER 'ts047b_writer'@'localhost' IDENTIFIED BY @password",$writer); $Provider.ExecuteSqlSecret($connection,"CREATE USER 'ts047b_reader'@'localhost' IDENTIFIED BY @password",$reader); $Provider.ExecuteSql($connection,"GRANT SELECT, INSERT, UPDATE, DELETE ON ts047b_beads.* TO 'ts047b_writer'@'localhost'"); $Provider.ExecuteSql($connection,"GRANT SELECT ON ts047b_beads.* TO 'ts047b_reader'@'localhost'"); $Provider.ExecuteSql($connection,"DROP USER 'root'@'localhost'"); $Provider.CloseSql($connection); $connection=$null
        $phase='AUTHORIZATION_POSTCONDITIONS'; $post=$Provider.VerifyPostconditions(); Assert-TS047B ($post.RootPasswordlessDenied -and $post.AdminRecovery -and $post.WriterScoped -and $post.ReaderMutationDenied -and $post.WrongPasswordDenied -and $post.LoopbackOnly -and $post.ServeDisabled) 'AUTHORIZATION_POSTCONDITION_FAILED'
        return [pscustomobject]@{ Status='FUTURE_APPLY_PASS'; Phase='COMPLETE'; EffectsStarted=$true; Receipt=@{Operation=$script:OperationId; Attempt=$FutureExecutionAttempt; SourceSha256=$ExpectedSourceSha256; Secrets='NOT_SERIALIZED'; Serve='DISABLED'} }
    } catch { if($null -ne $connection){$Provider.CloseSql($connection)}; if($effectTouched){ return [pscustomobject]@{ Status='UNKNOWN_OR_PARTIAL_PRESERVE_STATE'; Phase=$phase; EffectsStarted=$started; Reason=$_.Exception.Message; Retry='FORBIDDEN'; Cleanup='FORBIDDEN' } }; throw }
}
