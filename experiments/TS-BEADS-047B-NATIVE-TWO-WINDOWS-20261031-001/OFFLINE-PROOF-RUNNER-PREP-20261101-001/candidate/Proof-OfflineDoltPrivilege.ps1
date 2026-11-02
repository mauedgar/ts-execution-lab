<#
Disposable offline-Dolt privilege fixture.  This script is preparation only:
its effect path requires a future, external, immutable grant and is never
invoked by this preparation attempt.
#>
[CmdletBinding(DefaultParameterSetName='Preflight')]
param(
  [Parameter(ParameterSetName='Preflight', Mandatory)][switch]$Preflight,
  [Parameter(ParameterSetName='Effect', Mandatory)][switch]$Effect,
  [Parameter(ParameterSetName='Effect', Mandatory)][string]$ExecutionAttempt,
  [Parameter(ParameterSetName='Effect', Mandatory)][string]$GrantFile,
  [hashtable]$Provider
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$script:PrepAttempt = 'TS-BEADS-047B-OFFLINE-PROOF-RUNNER-PREP-20261101-001'
$script:Principal = 'ts047b_proof_fixture@localhost'
$script:ExpectedDoltHash = 'BED880C0E6B522498A563FCD1F0FC1E25527BA07E66C1E0A85C2242B64DFD967'

function New-Result([string]$Status, [string]$Label, [string]$Detail = '') {
  [pscustomobject]@{ Status=$Status; Label=$Label; Detail=$Detail }
}
function Test-SafeAttempt([string]$Value) { return $Value -match '^TS-BEADS-047B-[A-Z0-9-]+-[0-9]{8}-[0-9]{3}$' -and $Value -ne $script:PrepAttempt }
function Get-SourceHash { (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToUpperInvariant() }
function Get-DisposableRoot([string]$Attempt) {
  if ([string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) { throw 'LOCALAPPDATA unavailable' }
  Join-Path $env:LOCALAPPDATA ('TS047B-OfflineProof-' + $Attempt)
}
function Assert-Complete([object]$Value, [string]$Label) {
  if ($null -eq $Value -or ($Value -is [hashtable] -and $Value.ContainsKey('Complete') -and -not $Value.Complete)) { throw "BLOCKED:$Label" }
  $Value
}
function Sanitize-ProcessResult([object]$R) {
  [pscustomobject]@{ ExitCode=[int]$R.ExitCode; TimedOut=[bool]$R.TimedOut; FoundPrincipal=([bool]$R.FoundPrincipal); FoundGrant=([bool]$R.FoundGrant) }
}
function New-NativeProvider {
  @{
    Observe = {
      $dolt = 'C:\Program Files\Dolt\dolt.exe'
      [pscustomobject]@{
        Complete=$true; Host=$env:COMPUTERNAME; Owner=([System.Security.Principal.WindowsIdentity]::GetCurrent().Name)
        DoltPath=$dolt; DoltVersion='2.2.0'; DoltHash=(Get-FileHash -LiteralPath $dolt -Algorithm SHA256).Hash.ToUpperInvariant()
        RootExists=$false; RootReparse=$false; RootAclSafe=$true; PrivilegeExists=$false
        SqlListener=$false; ServeActive=$false; PriorReceipt=$false; PriorUnknown=$false; NeedsInitialization=$true
      }
    }
    ReadGrant = { param($Path) Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json }
    MakeRoot = { param($Path) New-Item -ItemType Directory -LiteralPath $Path -ErrorAction Stop | Out-Null }
    WriteReceipt = { param($Path,$Receipt) [System.IO.File]::WriteAllText($Path, ($Receipt | ConvertTo-Json -Depth 8), [Text.UTF8Encoding]::new($false)) }
    RunDolt = {
      param($Exe,$Arguments,$Sql)
      $psi=[Diagnostics.ProcessStartInfo]::new(); $psi.FileName=$Exe; $psi.UseShellExecute=$false
      $psi.RedirectStandardInput=$true; $psi.RedirectStandardOutput=$true; $psi.RedirectStandardError=$true
      foreach($a in $Arguments){ [void]$psi.ArgumentList.Add([string]$a) }
      $p=[Diagnostics.Process]::new(); $p.StartInfo=$psi
      if(-not $p.Start()){ throw 'process did not start' }; $p.StandardInput.Write($Sql); $p.StandardInput.Close()
      if(-not $p.WaitForExit(30000)){ return [pscustomobject]@{ExitCode=-1;TimedOut=$true;FoundPrincipal=$false;FoundGrant=$false} }
      $out=$p.StandardOutput.ReadToEnd(); $err=$p.StandardError.ReadToEnd()
      [pscustomobject]@{ ExitCode=$p.ExitCode; TimedOut=$false; FoundPrincipal=($out -match [regex]::Escape($script:Principal)); FoundGrant=($out -match 'SELECT'); RawOutput=$out; RawError=$err }
    }
    FileMeta = { param($Path) $i=Get-Item -LiteralPath $Path -ErrorAction Stop; [pscustomobject]@{Length=$i.Length;Sha256=(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()} }
    NoSurpriseStore = { param($Root,$Data,$Cfg,$Privilege) @($Root,$Data,$Cfg,$Privilege).ForEach({ Test-Path -LiteralPath $_ }) -notcontains $false }
  }
}
function Get-Precheck([hashtable]$P, [string]$Attempt = '') {
  try {
    $o=Assert-Complete (& $P.Observe) 'INCOMPLETE_PROVIDER_OBSERVATION'
    if([string]::IsNullOrWhiteSpace($o.DoltPath) -or -not [IO.Path]::IsPathFullyQualified($o.DoltPath) -or $o.DoltPath -notmatch '\.exe$') { return New-Result BLOCKED WRONG_BINARY }
    if($o.DoltVersion -ne '2.2.0' -or $o.DoltHash -ne $script:ExpectedDoltHash) { return New-Result BLOCKED WRONG_BINARY_HASH }
    if($o.SqlListener -or $o.ServeActive) { return New-Result BLOCKED ACTIVE_LISTENER_SERVE }
    if($o.RootExists) { return New-Result BLOCKED ROOT_EXISTS }
    if($o.RootReparse) { return New-Result BLOCKED ROOT_JUNCTION }
    if(-not $o.RootAclSafe) { return New-Result BLOCKED ROOT_ACL }
    if($o.PrivilegeExists) { return New-Result BLOCKED PRIVILEGE_FILE_EXISTS }
    if($o.PriorReceipt -or $o.PriorUnknown) { return New-Result BLOCKED PRIOR_UNKNOWN }
    New-Result REVIEW_REQUIRED PRECHECK_OK
  } catch { New-Result BLOCKED ($_.Exception.Message -replace '^BLOCKED:','') }
}
function Test-Grant([object]$G,[object]$O,[string]$Attempt) {
  if($G.Authority -ne 'EXTERNAL_ONE_TIME_USER_GRANT' -or $G.Subject -ne 'TS-BEADS-047B-OFFLINE-DISPOSABLE-PROOF' -or -not $G.OneTime) { return 'WRONG_GRANT' }
  if($G.ExecutionAttempt -ne $Attempt -or $G.SourceSha256 -ne (Get-SourceHash)) { return 'WRONG_GRANT' }
  if($G.ExpectedHost -ne $O.Host -or $G.ExpectedOwner -ne $O.Owner) { return 'WRONG_HOST_OWNER' }
  'OK'
}
function Invoke-OfflineDoltPrivilegeProof([hashtable]$Provider) {
  $p=if($Provider){$Provider}else{New-NativeProvider}
  if($Preflight){ return Get-Precheck $p }
  if(-not (Test-SafeAttempt $ExecutionAttempt)){ return New-Result BLOCKED WRONG_GRANT }
  $pre=Get-Precheck $p $ExecutionAttempt; if($pre.Status -eq 'BLOCKED'){ return $pre }
  try { $o=Assert-Complete (& $p.Observe) 'INCOMPLETE_PROVIDER_OBSERVATION'; $g=& $p.ReadGrant $GrantFile } catch { return New-Result BLOCKED WRONG_GRANT }
  $grantStatus=Test-Grant $g $o $ExecutionAttempt; if($grantStatus -ne 'OK'){ return New-Result BLOCKED $grantStatus }
  $root=Get-DisposableRoot $ExecutionAttempt; $data=Join-Path $root 'data'; $cfg=Join-Path $root 'cfg'; $privilege=Join-Path $root 'privileges.db'; $receipt=Join-Path $root 'effect-receipt.json'
  # No path is caller-controlled. Root is created only after every gate above passes.
  try { & $p.MakeRoot $root; & $p.WriteReceipt $receipt @{status='CONDITIONED_EFFECT_STARTED';attempt=$ExecutionAttempt;sourceSha256=(Get-SourceHash)} } catch { return New-Result UNKNOWN_OR_PARTIAL_PRESERVE_STATE RECEIPT_OR_ROOT_FAILURE }
  if($o.NeedsInitialization) {
    if(-not $g.AllowInitialize) { return New-Result BLOCKED WRONG_GRANT }
    try { $init=& $p.RunDolt $o.DoltPath @('--data-dir',$data,'--doltcfg-dir',$cfg,'--privilege-file',$privilege,'init') '' } catch { return New-Result UNKNOWN_OR_PARTIAL_PRESERVE_STATE PROCESS_AMBIGUOUS }
    if($init.TimedOut) { return New-Result UNKNOWN_OR_PARTIAL_PRESERVE_STATE PROCESS_AMBIGUOUS_TIMEOUT }
    if($init.ExitCode -ne 0) { return New-Result NO_GO_OFFLINE_PRIVILEGE_PERSISTENCE INITIALIZATION_UNSUPPORTED }
    try { & $p.WriteReceipt $receipt @{status='INITIALIZATION_COMPLETED';attempt=$ExecutionAttempt;initialization=(Sanitize-ProcessResult $init)} } catch { return New-Result UNKNOWN_OR_PARTIAL_PRESERVE_STATE RECEIPT_CHECKPOINT_FAILURE }
  }
  $args=@('--data-dir',$data,'--doltcfg-dir',$cfg,'--privilege-file',$privilege,'sql')
  $sql="CREATE USER 'ts047b_proof_fixture'@'localhost'; GRANT SELECT ON ``ts047b_proof_fixture_db``.* TO 'ts047b_proof_fixture'@'localhost';"
  try { $write=& $p.RunDolt $o.DoltPath $args $sql } catch { return New-Result UNKNOWN_OR_PARTIAL_PRESERVE_STATE PROCESS_AMBIGUOUS }
  if($write.TimedOut){ return New-Result UNKNOWN_OR_PARTIAL_PRESERVE_STATE PROCESS_AMBIGUOUS_TIMEOUT }
  if($write.ExitCode -ne 0){ return New-Result NO_GO_OFFLINE_PRIVILEGE_PERSISTENCE MALFORMED_SQL }
  try { & $p.WriteReceipt $receipt @{status='WRITE_COMPLETED';attempt=$ExecutionAttempt;write=(Sanitize-ProcessResult $write)} } catch { return New-Result UNKNOWN_OR_PARTIAL_PRESERVE_STATE RECEIPT_CHECKPOINT_FAILURE }
  try { $read=& $p.RunDolt $o.DoltPath $args "SELECT User,Host FROM mysql.user WHERE User='ts047b_proof_fixture'; SHOW GRANTS FOR 'ts047b_proof_fixture'@'localhost';" } catch { return New-Result UNKNOWN_OR_PARTIAL_PRESERVE_STATE PROCESS_AMBIGUOUS }
  if($read.TimedOut){ return New-Result UNKNOWN_OR_PARTIAL_PRESERVE_STATE PROCESS_AMBIGUOUS_TIMEOUT }
  if($read.ExitCode -ne 0 -or -not $read.FoundPrincipal -or -not $read.FoundGrant){ return New-Result NO_GO_OFFLINE_PRIVILEGE_PERSISTENCE READBACK_MISSING }
  try { $m=& $p.FileMeta $privilege; if($m.Length -le 0 -or -not (& $p.NoSurpriseStore $root $data $cfg $privilege)){ return New-Result NO_GO_OFFLINE_PRIVILEGE_PERSISTENCE PRIVILEGE_FILE_MISMATCH }; & $p.WriteReceipt $receipt @{status='REVIEW_REQUIRED';attempt=$ExecutionAttempt;privilegeFile=@{length=$m.Length;sha256=$m.Sha256};readback=(Sanitize-ProcessResult $read)} } catch { return New-Result NO_GO_OFFLINE_PRIVILEGE_PERSISTENCE PRIVILEGE_FILE_MISMATCH }
  New-Result REVIEW_REQUIRED EMPIRICAL_FIXTURE_AUDITABLE
}

Invoke-OfflineDoltPrivilegeProof -Provider $Provider
