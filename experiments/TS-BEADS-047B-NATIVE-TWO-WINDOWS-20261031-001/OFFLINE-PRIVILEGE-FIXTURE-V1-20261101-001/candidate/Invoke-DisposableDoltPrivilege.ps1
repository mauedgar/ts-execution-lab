# TS-BEADS 047B — disposable OFFLINE privilege persistence; source-only candidate.
# No SQL is authorized by publication. Invocation -Effect needs a separately
# vetted exact-source launcher and a competent, immutable one-time grant.
[CmdletBinding(DefaultParameterSetName='Preflight')]
param(
  [Parameter(Mandatory,ParameterSetName='Preflight')][switch]$Preflight,
  [Parameter(Mandatory,ParameterSetName='Effect')][switch]$Effect,
  [Parameter(Mandatory,ParameterSetName='Effect')][string]$ExecutionAttempt,
  [Parameter(Mandatory,ParameterSetName='Effect')][string]$GrantPath,
  [Parameter(Mandatory,ParameterSetName='Effect')][string]$ApprovedGrantSha256
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$script:Operation='TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001'
$script:HostExpected='DESKTOP-DJLBEQH'
$script:ExpectedDoltHash='BED880C0E6B522498A563FCD1F0FC1E25527BA07E66C1E0A85C2242B64DFD967'
$script:ReceiptWriter=$null
$script:ReceiptStream=$null
$script:AnySqlSpawn=$false
$script:LastPid=$null
$script:Trace=@()
function Outcome([string]$State,[string]$Reason) {
  [pscustomobject]@{ Operation=$script:Operation; State=$State; Reason=$Reason;
    AnySqlSpawn=$script:AnySqlSpawn; LastPid=$script:LastPid }
}
function Assert-Safe([bool]$Condition,[string]$Label) { if(-not $Condition){ throw $Label } }
function Safe-Path([string]$Attempt) {
  Assert-Safe ($Attempt -match '^TS-BEADS-047B-DOLT-FIXTURE-20261101-[0-9]{3}$') 'ATTEMPT_ID_INVALID'
  Assert-Safe (-not [string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) 'APPDATA_MISSING'
  [IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA ('TS047B-DoltFixture-'+$Attempt)))
}
function Test-Reparse([string]$Path) {
  $item=[IO.Path]::GetFullPath($Path)
  while($true) {
    if(Test-Path -LiteralPath $item){
      if((Get-Item -LiteralPath $item -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){return $true}
    }
    $parent=[IO.Directory]::GetParent($item); if($null -eq $parent){return $false}
    $item=$parent.FullName
  }
}
function Test-Acl([string]$Path,[bool]$RequireProtected) {
  try {
    $acl=Get-Acl -LiteralPath $Path
    $owner=[Security.Principal.WindowsIdentity]::GetCurrent().Name
    if($acl.Owner -ne $owner){return $false}
    if($RequireProtected -and -not $acl.AreAccessRulesProtected){return $false}
    $broad=@('S-1-1-0','S-1-5-11','S-1-5-32-545')
    foreach($r in $acl.Access){
      $sid=$r.IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value
      if($sid -in $broad -and $r.AccessControlType -eq 'Allow'){
        if(($r.FileSystemRights -band [Security.AccessControl.FileSystemRights]::Write) -ne 0){return $false}
      }
    }
    return $true
  } catch {return $false}
}
function Protect-NewDirectory([string]$Path) {
  Assert-Safe (-not (Test-Path -LiteralPath $Path)) 'DIRECTORY_EXISTS'
  [void][IO.Directory]::CreateDirectory($Path)
  $sid=[Security.Principal.WindowsIdentity]::GetCurrent().User
  $acl=[Security.AccessControl.DirectorySecurity]::new()
  $acl.SetAccessRuleProtection($true,$false)
  $acl.SetOwner($sid)
  $rule=[Security.AccessControl.FileSystemAccessRule]::new($sid,
    [Security.AccessControl.FileSystemRights]::FullControl,
    [Security.AccessControl.InheritanceFlags]'ContainerInherit, ObjectInherit',
    [Security.AccessControl.PropagationFlags]::None,
    [Security.AccessControl.AccessControlType]::Allow)
  $acl.AddAccessRule($rule)
  Set-Acl -LiteralPath $Path -AclObject $acl
  Assert-Safe (Test-Acl $Path $true) 'NEW_DIRECTORY_ACL_UNVERIFIED'
}
function Check-Host([string]$Root,[string]$Attempt) {
  Assert-Safe ($env:COMPUTERNAME -eq $script:HostExpected) 'WRONG_HOST'
  Assert-Safe ($PSVersionTable.PSEdition -eq 'Core') 'PWSH_CORE_REQUIRED'
  $exe=Join-Path $env:ProgramFiles 'Dolt\dolt.exe'
  Assert-Safe (Test-Path -LiteralPath $exe -PathType Leaf) 'DOLT_MISSING'
  Assert-Safe ((Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash -eq $script:ExpectedDoltHash) 'DOLT_HASH_MISMATCH'
  Assert-Safe (-not (Test-Path -LiteralPath $Root)) 'FIXTURE_ALREADY_EXISTS'
  Assert-Safe (-not (Test-Reparse $Root)) 'REPARSE_ANCESTOR'
  Assert-Safe (Test-Acl (Split-Path -Parent $Root) $false) 'PARENT_ACL_UNVERIFIED'
  $receipts=Join-Path $env:LOCALAPPDATA 'TS047B-Fixture-Receipts'
  Assert-Safe (-not (Test-Reparse $receipts)) 'RECEIPT_REPARSE'
  if(Test-Path -LiteralPath $receipts){Assert-Safe (Test-Acl $receipts $true) 'RECEIPT_ACL_UNVERIFIED'}
  Assert-Safe (-not (Test-Path -LiteralPath (Join-Path $receipts ($Attempt+'.jsonl')))) 'PRIOR_ATTEMPT_RECEIPT'
  # Every TCP 3307 listener, independent of executable name. Failure to observe blocks.
  $listeners=@(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object {$_.LocalPort -eq 3307})
  Assert-Safe ($listeners.Count -eq 0) 'PORT_3307_OCCUPIED'
  # Separate grant/launcher preconditions must verify the Tailscale Serve/Funnel
  # structured configuration. This local offline fixture never enables them.
  $ts=Get-Command tailscale.exe -ErrorAction Stop
  Assert-Safe ($null -ne $ts) 'TAILSCALE_CLI_NOT_OBSERVABLE'
  $state=& $ts.Source serve status --json 2>$null
  Assert-Safe ($LASTEXITCODE -eq 0) 'TAILSCALE_STATUS_UNVERIFIED'
  $config=($state | Out-String | ConvertFrom-Json -AsHashtable)
  Assert-Safe ($null -ne $config -and $config -is [hashtable]) 'TAILSCALE_JSON_UNVERIFIED'
  foreach($k in @('TCP','Web','AllowFunnel')){
    if($config.ContainsKey($k)) { Assert-Safe ($config[$k].Count -eq 0) 'TAILSCALE_EXPOSURE_PRESENT' }
  }
  return [pscustomobject]@{Executable=$exe;ReceiptDir=$receipts}
}
function Check-Grant([string]$Attempt) {
  Assert-Safe ($ApprovedGrantSha256 -match '^[0-9a-fA-F]{64}$') 'GRANT_HASH_MISSING'
  Assert-Safe (Test-Path -LiteralPath $GrantPath -PathType Leaf) 'GRANT_MISSING'
  Assert-Safe (-not (Test-Reparse $GrantPath)) 'GRANT_REPARSE'
  Assert-Safe ((Get-FileHash -LiteralPath $GrantPath -Algorithm SHA256).Hash -eq $ApprovedGrantSha256) 'GRANT_HASH_MISMATCH'
  $g=Get-Content -LiteralPath $GrantPath -Raw -Encoding UTF8 | ConvertFrom-Json -AsHashtable
  Assert-Safe ($g.operation -ceq $script:Operation) 'GRANT_OPERATION'
  Assert-Safe ($g.attempt -ceq $Attempt) 'GRANT_ATTEMPT'
  Assert-Safe ($g.host -ceq $script:HostExpected) 'GRANT_HOST'
  Assert-Safe ($g.effectScope -ceq 'OFFLINE_DOLT_PRIVILEGE_PERSISTENCE_ONLY') 'GRANT_SCOPE'
  Assert-Safe ($g.allowEffect -ceq $true) 'GRANT_NOT_EFFECT'
  Assert-Safe ($g.sourceSha256 -ceq (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant()) 'GRANT_SOURCE'
  Assert-Safe ($g.issuer -ceq 'COMPETENT_EXPERIMENTAL_CONTROL') 'GRANT_ISSUER'
  Assert-Safe ($g.grantGitCommit -match '^[a-f0-9]{40}$') 'GRANT_GIT_ID'
  $expiry=[datetimeoffset]::Parse($g.expiresUtc,[Globalization.CultureInfo]::InvariantCulture)
  Assert-Safe ($expiry -gt [datetimeoffset]::UtcNow -and $expiry -lt [datetimeoffset]::UtcNow.AddDays(3)) 'GRANT_EXPIRED_OR_TOO_WIDE'
  # Important: local hash+JSON cannot establish the issuer! The independently
  # reviewed launcher MUST verify exact Git blob, issuer/authority and one-time
  # approval OUTSIDE this process before passing ApprovedGrantSha256.
  return $g
}
function Record([string]$Kind,[hashtable]$Fields) {
  $obj=[ordered]@{kind=$Kind;utc=[datetimeoffset]::UtcNow.ToString('o');
    operation=$script:Operation}
  foreach($key in $Fields.Keys){$obj[$key]=$Fields[$key]}
  $script:ReceiptWriter.WriteLine(($obj|ConvertTo-Json -Compress -Depth 8))
  $script:ReceiptWriter.Flush()
  $script:ReceiptStream.Flush($true)
}
function Spawn-Sql([string]$Exe,[string]$Data,[string]$Cfg,[string]$Priv,[string]$Sql,[string]$Stage) {
  # Only bounded synthetic queries; SQL is supplied on stdin, never process argv.
  Record 'SPAWN_INTENT' @{stage=$Stage}
  $p=[Diagnostics.Process]::new()
  $pi=[Diagnostics.ProcessStartInfo]::new()
  $pi.FileName=$Exe
  $pi.WorkingDirectory=$Data
  $pi.UseShellExecute=$false
  $pi.RedirectStandardInput=$true
  $pi.RedirectStandardOutput=$true
  $pi.RedirectStandardError=$true
  foreach($a in @("--data-dir=$Data","--doltcfg-dir=$Cfg","--privilege-file=$Priv",
      'sql','--result-format','json')){[void]$pi.ArgumentList.Add($a)}
  $p.StartInfo=$pi
  Assert-Safe ($p.Start()) 'SQL_CHILD_START_FAILED'
  $script:AnySqlSpawn=$true
  $script:LastPid=$p.Id
  Record 'PID' @{stage=$Stage;pid=$p.Id}
  $out=$p.StandardOutput.ReadToEndAsync()
  $err=$p.StandardError.ReadToEndAsync()
  $write=$p.StandardInput.WriteAsync($Sql)
  $write.GetAwaiter().GetResult()
  $p.StandardInput.Close()
  if(-not $p.WaitForExit(15000)){
    Record 'UNKNOWN_PROCESS_ACTIVE' @{stage=$Stage;pid=$p.Id}
    throw 'SQL_PROCESS_UNKNOWN_NO_RETRY'
  }
  $write.GetAwaiter().GetResult()
  $stdout=$out.GetAwaiter().GetResult()
  $stderr=$err.GetAwaiter().GetResult()
  if($stdout.Length -gt 16384 -or $stderr.Length -gt 16384){
    Record 'OUTPUT_LIMIT' @{stage=$Stage;pid=$p.Id}
    throw 'SQL_OUTPUT_OVERFLOW'
  }
  Record 'EXIT' @{stage=$Stage;pid=$p.Id;exitCode=$p.ExitCode}
  Assert-Safe ($p.ExitCode -eq 0) ('SQL_STAGE_FAILED_'+$Stage)
  return $stdout
}
function One-Row([string]$Raw,[string]$Stage) {
  # Dolt JSON formatting must empirically agree with this contract or fail closed.
  $parsed=$Raw.Trim()|ConvertFrom-Json -AsHashtable
  if($parsed -is [hashtable] -and $parsed.ContainsKey('rows')) {$rows=@($parsed.rows)}
  elseif($parsed -is [array]) {$rows=@($parsed)}
  else {throw ('JSON_READBACK_SCHEMA_'+$Stage)}
  Assert-Safe ($rows.Count -eq 1) ('ROW_COUNT_'+$Stage)
  return $rows[0]
}
function Run-Fixture([string]$Attempt,[string]$Root,[object]$H) {
  # All local mutations begin only after externally authorized grant verification.
  if(-not (Test-Path -LiteralPath $H.ReceiptDir)){Protect-NewDirectory $H.ReceiptDir}
  Assert-Safe (Test-Acl $H.ReceiptDir $true) 'RECEIPT_ACL'
  $path=Join-Path $H.ReceiptDir ($Attempt+'.jsonl')
  $script:ReceiptStream=[IO.FileStream]::new($path,[IO.FileMode]::CreateNew,
    [IO.FileAccess]::Write,[IO.FileShare]::None,4096,[IO.FileOptions]::WriteThrough)
  $script:ReceiptWriter=[IO.StreamWriter]::new($script:ReceiptStream,[Text.UTF8Encoding]::new($false),1024,$true)
  try {
    Record 'ATTEMPT_CLAIMED' @{attempt=$Attempt;root=$Root;host=$env:COMPUTERNAME}
    Protect-NewDirectory $Root
    $data=Join-Path $Root 'data'
    $cfg=Join-Path $Root 'cfg'
    Protect-NewDirectory $data
    Protect-NewDirectory $cfg
    $priv=Join-Path $cfg 'privileges.db'
    Assert-Safe (-not (Test-Path -LiteralPath $priv)) 'PRIVILEGES_PREEXIST'
    $password=[Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(24))
    $sql1="CREATE DATABASE ts047b_fixture; CREATE USER 'ts047b_reader'@'localhost' IDENTIFIED BY '$password'; GRANT SELECT ON ts047b_fixture.* TO 'ts047b_reader'@'localhost';"
    [void](Spawn-Sql $H.Executable $data $cfg $priv $sql1 'CREATE_GRANT')
    Assert-Safe (Test-Path -LiteralPath $priv -PathType Leaf) 'PRIVILEGE_FILE_NOT_PERSISTED'
    $h1=(Get-FileHash -LiteralPath $priv -Algorithm SHA256).Hash
    Record 'PRIVILEGE_FILE_FIRST' @{sha256=$h1}
    $query="SELECT User, Host, Db, Select_priv, Insert_priv, Update_priv, Delete_priv FROM mysql.db WHERE User='ts047b_reader' AND Host='localhost' AND Db='ts047b_fixture';"
    $raw=Spawn-Sql $H.Executable $data $cfg $priv $query 'REOPEN_READBACK'
    $row=One-Row $raw 'REOPEN_READBACK'
    Assert-Safe ($row.User -ceq 'ts047b_reader' -and $row.Host -ceq 'localhost' -and $row.Db -ceq 'ts047b_fixture') 'READBACK_IDENTITY'
    Assert-Safe ($row.Select_priv -ceq 'Y' -and $row.Insert_priv -ceq 'N' -and $row.Update_priv -ceq 'N' -and $row.Delete_priv -ceq 'N') 'READBACK_PRIVILEGES'
    $h2=(Get-FileHash -LiteralPath $priv -Algorithm SHA256).Hash
    Assert-Safe ($h1 -eq $h2) 'PRIVILEGES_CHANGED_ON_READ'
    Record 'PASS_OFFLINE_PERSISTENCE_ONLY' @{attempt=$Attempt;sha256=$h2}
    return Outcome 'PASS_OFFLINE_PERSISTENCE_ONLY' 'NOT_A_REMOTE_AUTH_OR_HOST_INDEPENDENCE_PROOF'
  } finally {
    if($null -ne $script:ReceiptWriter){$script:ReceiptWriter.Dispose()}
    if($null -ne $script:ReceiptStream){$script:ReceiptStream.Dispose()}
  }
}
try {
  $attempt=if($Preflight){'TS-BEADS-047B-DOLT-FIXTURE-20261101-001'}else{$ExecutionAttempt}
  $root=Safe-Path $attempt
  $h=Check-Host $root $attempt
  if($Preflight){Outcome 'READY_FOR_REVIEW_ONLY' 'NO_GRANT_NO_SQL';return}
  [void](Check-Grant $attempt)
  Run-Fixture $attempt $root $h
} catch {
  # No SQL, input or exception text is emitted; preserve partial/UNKNOWN states.
  if($script:AnySqlSpawn){Outcome 'UNKNOWN_OR_FAILED_PRESERVE' 'REQUIRES_ORIGINAL_RECEIPT_RECONCILIATION'}
  else {Outcome 'BLOCKED_OR_PARTIAL_PRESERVE' 'INSPECT_PRECONDITION_AND_ORIGINAL_RECEIPT'}
}
