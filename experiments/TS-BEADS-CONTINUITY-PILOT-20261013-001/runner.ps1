# TS-BEADS-CONTINUITY-PILOT-20261013-001 | isolated local trial
# Product authority: NONE. Never touches any Product repository or global PATH.
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PilotId = 'TS-BEADS-CONTINUITY-PILOT-20261013-001'
$Dir = Join-Path $env:LOCALAPPDATA "TS-Experiments\$PilotId"
$Out = Join-Path $Dir 'result.json'
$StartedUtc = (Get-Date).ToUniversalTime().ToString('o')
$Stage = 'PREFLIGHT'
$Receipt = [ordered]@{execution_attempt='BEADS-LOCAL-TRIAL-20261013-002';contract='ts-beads-pilot-result/v0-experimental'; pilot=$PilotId; status='UNKNOWN'; phase=$Stage; started_utc=$StartedUtc; host=$env:COMPUTERNAME; product_authority='NONE'; local_dir=$Dir; release='v1.3.1'; checks=@(); issue_ids=@{}; error=$null; limitations=@('No automatic ChatGPT task-completion signal','No web MCP connector qualified','Git Transport host publication not established')}
function Check([string]$Key,[bool]$Valid,[string]$Detail) {
  $Receipt.checks += [ordered]@{key=$Key;pass=$Valid;detail=$Detail}
  if (-not $Valid) { throw "PRECONDITION_OR_ASSERTION:${Key}:${Detail}" }
}
function RunBd([string[]]$Arguments) {
  $response = & $script:BD @Arguments 2>&1
  if ($LASTEXITCODE -ne 0) { throw ('BD_FAIL {0}: {1}' -f ($Arguments -join ' '), ($response -join ' ')) }
  $t = (($response | Out-String).Trim())
  return $t
}
function ParseIssueId([string]$Content) {
  $v = $Content | ConvertFrom-Json
  if ($v -is [array]) { $v = $v[0] }
  if (-not $v.id) { throw 'Missing issue id in JSON output' }
  return [string]$v.id
}
try {
  Check 'WINDOWS_X64' ([Environment]::OSVersion.Platform -eq 'Win32NT' -and [Environment]::Is64BitOperatingSystem -and $env:PROCESSOR_ARCHITECTURE -eq 'AMD64') 'Requires Windows AMD64'
  $drive = Get-PSDrive -Name ([IO.Path]::GetPathRoot($Dir).Substring(0,1))
  Check 'FREE_DISK' ($drive.Free -gt 1073741824) ('Available disk bytes: ' + $drive.Free)
  Check 'FRESH_ISOLATED_WORKSPACE' (-not (Test-Path -LiteralPath $Dir)) 'Fail closed rather than modifying any prior attempt'
  $m = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifest.json') -Raw | ConvertFrom-Json
  $thisSha = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant()
  Check 'RUNNER_INTEGRITY' ($thisSha -eq $m.runner_sha256) 'Manifest-pinned runner bytes'
  Check 'ATTEMPT_ID' ($m.attempt -eq $Receipt.execution_attempt) 'Original blocked attempt 001 is not reused'
  $readbackHash = (Get-FileHash -LiteralPath (Join-Path $PSScriptRoot 'verify-readback.ps1') -Algorithm SHA256).Hash.ToLowerInvariant()
  Check 'READBACK_INTEGRITY' ($readbackHash -eq $m.readback_sha256) 'Manifest-pinned readback script'
  Check 'RELEASE_PIN' ($m.release_version -eq 'v1.3.1' -and $m.archive_sha256 -eq '48cd82e1d3e311c9bf9a5d6d67ad1a8542ae13d4e20c5bfb527656c5e666af76') 'Pinned verified upstream archive'
  $Stage = 'INSTALL_ISOLATED'
  New-Item -ItemType Directory -Path $Dir -Force | Out-Null
  $zip = Join-Path $Dir 'beads_1.3.1_windows_amd64.zip'
  Invoke-WebRequest -Uri 'https://github.com/gastownhall/beads/releases/download/v1.3.1/beads_1.3.1_windows_amd64.zip' -OutFile $zip -MaximumRedirection 5 -TimeoutSec 120
  $archiveHash = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()
  Check 'ARCHIVE_SHA256' ($archiveHash -eq $m.archive_sha256) $archiveHash
  $extract = Join-Path $Dir 'unpacked'
  Expand-Archive -LiteralPath $zip -DestinationPath $extract -ErrorAction Stop
  $binaries = @(Get-ChildItem -Path $extract -Filter 'bd.exe' -Recurse -File)
  Check 'BD_BINARY_PRESENT' ($binaries.Count -eq 1) "bd.exe matches: $($binaries.Count)"
  $bin = Join-Path $Dir 'bin'
  New-Item -ItemType Directory -Path $bin -Force | Out-Null
  Copy-Item -LiteralPath $binaries[0].FullName -Destination (Join-Path $bin 'bd.exe') -ErrorAction Stop
  $script:BD = Join-Path $bin 'bd.exe'
  $Receipt.bd_binary_sha256 = (Get-FileHash -LiteralPath $script:BD -Algorithm SHA256).Hash.ToLowerInvariant()
  $Receipt.bd_version = RunBd -Arguments @('version')
  $Stage = 'CREATE_OBLIGATIONS'
  $env:BEADS_DIR = Join-Path $Dir 'data\.beads'
  New-Item -ItemType Directory -Path (Join-Path $Dir 'data') -Force | Out-Null
  [void](RunBd -Arguments @('init','--quiet','--stealth'))
  $active = ParseIssueId (RunBd -Arguments @('create','PILOT active responsibility','--description','Synthetic responsibility; never a real Product TaskCycle.','-t','task','-p','2','--json'))
  [void](RunBd -Arguments @('update',$active,'--status','in_progress','--json'))
  $handoff = ParseIssueId (RunBd -Arguments @('create','PILOT incoming handoff','--description','Synthetic durable ref: test://TS-BEADS-CONTINUITY-PILOT-20261013-001/H1. Must not interrupt active responsibility.','-t','task','-p','2','--json'))
  [void](RunBd -Arguments @('dep','add',$handoff,$active,'--type','related'))
  $Receipt.issue_ids = [ordered]@{active=$active;handoff=$handoff}
  $Stage = 'BEFORE_CLOSURE'
  $before = RunBd -Arguments @('ready','--json')
  Check 'READY_QUERY_SUCCEEDS' ($before.Length -gt 0) 'Independent queue can be queried while active task is open'
  Check 'HANDOFF_READY_BEFORE_CLOSURE' ($before.Contains($handoff)) 'Related edge must not block incoming handoff'
  $Stage = 'FINISH_CURRENT_AND_RECOVER'
  [void](RunBd -Arguments @('close',$active,'--reason','Synthetic active responsibility finished; Product unaffected.','--json'))
  # Deliberately spawn a fresh PowerShell process, not a reused bd session.
  $verifyScript = Join-Path $PSScriptRoot 'verify-readback.ps1'
  $readbackFile = Join-Path $Dir 'fresh-process-readback.json'
  & pwsh.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $verifyScript -BdPath $script:BD -BeadsDir $env:BEADS_DIR -ActiveId $active -HandoffId $handoff -OutputPath $readbackFile
  Check 'FRESH_PROCESS_EXIT' ($LASTEXITCODE -eq 0) 'Fresh process must succeed'
  $readback = Get-Content -LiteralPath $readbackFile -Raw | ConvertFrom-Json
  Check 'FRESH_PROCESS_RECOVERY' ($readback.recovered -eq $true) 'Closed active responsibility and open handoff observable from fresh process'
  Check 'DUPLICATE_HANDOFF_NOT_CREATED' ($readback.handoff_count -eq 1) 'Deduplication by stable source ref is caller policy; no second insertion'
  $Stage = 'PASS'
  $Receipt.status = 'PASS'
  $Receipt.readback = $readback
} catch {
  $Receipt.status = if ($Stage -eq 'PREFLIGHT') {'BLOCKED_PRECONDITION'} else {'FAIL'}
  $Receipt.error = $_.Exception.Message
} finally {
  $Receipt.phase = $Stage
  $Receipt.completed_utc = (Get-Date).ToUniversalTime().ToString('o')
  try {
    if (Test-Path -LiteralPath $Dir) {
      $Receipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $Out -Encoding utf8
    }
  } catch { $Receipt.persistence_error = $_.Exception.Message }
  $summary = [ordered]@{pilot=$PilotId;status=$Receipt.status;phase=$Stage;local_dir=$Dir;result=$Out;ids=$Receipt.issue_ids;error=$Receipt.error}
  $summary | ConvertTo-Json -Compress -Depth 5 | Write-Output
}
if ($Receipt.status -ne 'PASS') { exit 1 }
