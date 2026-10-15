# TS-BEADS-NOTEBOOK-MIGRATION-20261015-001
# Fixed, isolated qualification. Mechanical executor only; Product authority NONE.
# Source/intent owned by experiment lab Git, NOT Remote Desktop Commander.
param(
  [Parameter(Mandatory=$true)]
  [ValidatePattern('^[a-f0-9]{40}$')]
  [string]$ExpectedRunnerCommit
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$labRoot = 'C:\TS\execution\beads\qualification-20261015-001'
$toolRoot = 'C:\TS\tools\experimental\beads\v1.3.1'
$receiptRoot = 'C:\TS\execution\receipts'
$receiptPath = Join-Path $receiptRoot 'TS-BEADS-NOTEBOOK-MIGRATION-20261015-001.json'
$sourceZipHash = '48cd82e1d3e311c9bf9a5d6d67ad1a8542ae13d4e20c5bfb527656c5e666af76'
$sourceExeHash = 'ac5b60114e5e7ef9de8878b45fc35941937341d3447366c99bc91c81557be7a4'
$doltZipHash = '7a4be662d5548bc63ae4ab6d8d93daa2a6681f3e076817908ac4a08d782eb6f6'
$bdUrl = 'https://github.com/gastownhall/beads/releases/download/v1.3.1/beads_1.3.1_windows_amd64.zip'
$doltUrl = 'https://github.com/dolthub/dolt/releases/download/v2.2.0/dolt-windows-amd64.zip'
$fixtureId = 'nbmig-20261015-001'
$stage = 'PRECONDITION'
$hostObserved = ''
$runnerCommitObserved = ''
$bdBinaryHash = ''
$doltBinaryHash = ''
$beadsVersion = ''
$doltVersion = ''
$storePath = Join-Path $labRoot 'store'
$sourceDesktopStores = @(
  'TS-BEADS-CONTINUITY-PILOT-20261013-001',
  'TS-BEADS-INBOX-DEDUP-PILOT-20261013-002',
  'TS-BEADS-DEPENDENCY-RECOVERY-20261013-004'
)
$locationPushed = $false
$receipt = $null
function Native {
  param([string]$Binary,[string[]]$Arguments,[string]$What)
  $message = (& $Binary @Arguments 2>&1 | Out-String)
  if ($LASTEXITCODE -ne 0) {
    throw ("NATIVE_FAIL:"+$What+";exit="+$LASTEXITCODE+";log="+$message.Substring(0,[Math]::Min(480,$message.Length)))
  }
  return $message
}
function ParseNativeIssue {
  param([string]$Text,[string]$ExactId)
  $brace = $Text.IndexOf('{')
  $bracket = $Text.IndexOf('[')
  if ($brace -lt 0 -and $bracket -lt 0) { throw 'NATIVE_JSON_BEGIN_MISSING' }
  $index = if ($brace -lt 0) {$bracket} elseif ($bracket -lt 0) {$brace} else {[Math]::Min($brace,$bracket)}
  $parsed = $Text.Substring($index) | ConvertFrom-Json
  $item = if ($parsed -is [array]) { $parsed[0] } else { $parsed }
  if ($null -eq $item -or $item.id -cne $ExactId) { throw 'NATIVE_ISSUE_IDENTITY_MISMATCH' }
  return $item
}
function Digest {
  param([string]$Path)
  return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}
try {
  $hostObserved = ((& hostname.exe | Out-String).Trim())
  if ($hostObserved -cne 'DESKTOP-DJLBEQH') { throw ('UNAUTHORIZED_HOST='+$hostObserved) }
  if (-not (Test-Path 'C:\TS\repos\ts-execution-lab\.git')) { throw 'MISSING_EXISTING_LAB_REPO' }
  if (Test-Path -LiteralPath $receiptPath) { throw 'EXISTING_RECEIPT_RECONCILE_BEFORE_RETRY' }
  if (Test-Path -LiteralPath $labRoot) { throw 'LAB_ROOT_ALREADY_EXISTS_RECONCILE_BEFORE_RETRY' }
  if (Test-Path -LiteralPath $toolRoot) { throw 'TOOL_ROOT_ALREADY_EXISTS_RECONCILE_BEFORE_RETRY' }
  $runnerRepo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
  $runnerCommitObserved = (Native 'git.exe' @('-C',$runnerRepo,'rev-parse','HEAD') 'RUNNER_COMMIT').Trim()
  if ($runnerCommitObserved -cne $ExpectedRunnerCommit) { throw 'EXACT_RUNNER_COMMIT_MISMATCH' }
  $runnerClean = (Native 'git.exe' @('-C',$runnerRepo,'status','--porcelain=v1') 'RUNNER_STATUS').Trim()
  if ($runnerClean -ne '') { throw 'RUNNER_TREE_NOT_CLEAN' }
  if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) { throw 'GIT_EXECUTABLE_MISSING' }
  New-Item -ItemType Directory -Path $labRoot,$toolRoot -Force | Out-Null
  $stage = 'DOWNLOAD_VERIFIED_NATIVE_BINARIES'
  $bdZip = Join-Path $toolRoot 'beads_1.3.1_windows_amd64.zip'
  Invoke-WebRequest -Uri $bdUrl -OutFile $bdZip
  if ((Digest $bdZip) -cne $sourceZipHash) { throw 'BEADS_UPSTREAM_ARCHIVE_HASH_MISMATCH' }
  $bdExpanded = Join-Path $toolRoot 'bd'
  Expand-Archive -LiteralPath $bdZip -DestinationPath $bdExpanded -ErrorAction Stop
  $bdEntry = @(Get-ChildItem -LiteralPath $bdExpanded -Recurse -File -Filter bd.exe | Select-Object -First 1)
  if ($bdEntry.Count -ne 1) { throw 'BEADS_EXE_MISSING_OR_AMBIGUOUS' }
  $bdExe = $bdEntry[0].FullName
  $bdBinaryHash = Digest $bdExe
  if ($bdBinaryHash -cne $sourceExeHash) { throw 'DESKTOP_NOTEBOOK_BINARY_INTEGRITY_MISMATCH' }
  $beadsVersion = (Native $bdExe @('version') 'BD_VERSION').Trim()
  if ($beadsVersion -notmatch 'bd version 1\.3\.1\b') { throw 'WRONG_BEADS_VERSION' }
  $doltZip = Join-Path $toolRoot 'dolt-windows-amd64-v2.2.0.zip'
  Invoke-WebRequest -Uri $doltUrl -OutFile $doltZip
  if ((Digest $doltZip) -cne $doltZipHash) { throw 'DOLT_ARCHIVE_HASH_MISMATCH' }
  $doltExpanded = Join-Path $toolRoot 'dolt'
  Expand-Archive -LiteralPath $doltZip -DestinationPath $doltExpanded -ErrorAction Stop
  $doltEntries = @(Get-ChildItem -LiteralPath $doltExpanded -Recurse -File -Filter dolt.exe | Select-Object -First 1)
  if ($doltEntries.Count -ne 1) { throw 'DOLT_EXE_MISSING_OR_AMBIGUOUS' }
  $doltExe = $doltEntries[0].FullName
  $doltBinaryHash = Digest $doltExe
  $doltVersion = (Native $doltExe @('version') 'DOLT_VERSION').Trim()
  if ($doltVersion -notmatch '2\.2\.0') { throw 'WRONG_DOLT_VERSION' }
  $stage = 'DISPOSABLE_NATIVE_BEADS_QUALIFICATION'
  New-Item -ItemType Directory -Path $storePath -Force | Out-Null
  Native 'git.exe' @('-C',$storePath,'init','-q') 'QUALIFICATION_GIT_INIT' | Out-Null
  $remote = (Native 'git.exe' @('-C',$storePath,'remote') 'QUALIFICATION_REMOTE_CHECK').Trim()
  if ($remote -ne '') { throw 'QUALIFICATION_STORE_HAS_REMOTE' }
  Push-Location $storePath
  $locationPushed = $true
  Native $bdExe @('init','--quiet','--stealth') 'BEADS_NATIVE_INIT' | Out-Null
  $createLog = Native $bdExe @('create','Synthetic notebook qualification; not Product','--type','task','--id',$fixtureId,'--force','--description','test://TS-BEADS-NOTEBOOK-MIGRATION-20261015-001/SYNTHETIC_ONLY','--json') 'SYNTHETIC_CREATE'
  $created = ParseNativeIssue (Native $bdExe @('show',$fixtureId,'--json') 'FIRST_PROCESS_READBACK') $fixtureId
  if ($created.status -ne 'open') { throw 'NEW_NOTEBOOK_SYNTHETIC_ISSUE_NOT_OPEN' }
  Native $bdExe @('update',$fixtureId,'--status','in_progress') 'SYNTHETIC_UPDATE' | Out-Null
  $secondRead = ParseNativeIssue (Native $bdExe @('show',$fixtureId,'--json') 'SECOND_PROCESS_READBACK') $fixtureId
  if ($secondRead.status -ne 'in_progress') { throw 'SECOND_PROCESS_MISMATCH' }
  Native $bdExe @('close',$fixtureId,'--reason','Synthetic migration qualification terminal') 'SYNTHETIC_CLOSE' | Out-Null
  $stage = 'THIRD_PROCESS_PERSISTENCE_READBACK'
  $thirdRead = ParseNativeIssue (Native $bdExe @('show',$fixtureId,'--json') 'THIRD_PROCESS_READBACK') $fixtureId
  if ($thirdRead.status -ne 'closed') { throw 'THIRD_PROCESS_PERSISTENCE_MISMATCH' }
  if (-not (Test-Path (Join-Path $storePath '.beads\config.yaml'))) { throw 'BEADS_ISOLATED_CONFIG_MISSING' }
  Pop-Location
  $locationPushed = $false
  if (Get-Command bd -ErrorAction SilentlyContinue) { throw 'GLOBAL_BD_WAS_SET_BY_QUALIFICATION' }
  if (Get-Command dolt -ErrorAction SilentlyContinue) { throw 'GLOBAL_DOLT_WAS_SET_BY_QUALIFICATION' }
  $stage = 'WRITE_TERMINAL_LOCAL_RECEIPT'
  $receipt = [ordered]@{
    schema = 'TS-BEADS-NOTEBOOK-MIGRATION-20261015-001/v1'
    status = 'NOTEBOOK_NATIVE_INSTALL_AND_FRESH_STORE_PASS'
    authority = 'NONE_PRODUCT'
    product_effect = 'NONE'
    original_desktop_data_mutated = $false
    old_desktop_store_copied = $false
    historical_archive_status = 'PRESERVED_ON_DESKTOP_NOT_TRANSFERRED'
    legacy_historical_store_ids = $sourceDesktopStores
    notebook_host = $hostObserved
    notebook_device = '40cc0b10-fa7b-4a6a-98cf-1c94f93791b2'
    exact_experiment_source = ('mauedgar/ts-execution-lab@'+$runnerCommitObserved)
    bd_version = $beadsVersion
    bd_archive_sha256 = $sourceZipHash
    bd_exe_sha256 = $bdBinaryHash
    dolt_version = $doltVersion
    dolt_archive_sha256 = $doltZipHash
    dolt_exe_sha256 = $doltBinaryHash
    qualified_store_dir = $storePath
    qualified_beads_config_sha256 = (Digest (Join-Path $storePath '.beads\config.yaml'))
    synthetic_fixture_id = $fixtureId
    synthetic_closed_third_readback = ($thirdRead.status -eq 'closed')
    global_path_changed = $false
    git_remote_for_test_store = 'NONE'
    checked_at_utc = [DateTime]::UtcNow.ToString('o')
  }
  New-Item -ItemType Directory -Path $receiptRoot -Force | Out-Null
  $receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receiptPath -Encoding utf8NoBOM -NoNewline
  Write-Output ('TS_BEADS_NOTEBOOK=PASS;BD='+$bdBinaryHash+';DOLT='+$doltBinaryHash+';THIRD_PROCESS=CLOSED;HISTORICAL_STORES=DESKTOP_PRESERVED;PRODUCT=NONE')
  Write-Output ('TS_BEADS_NOTEBOOK_RECEIPT='+$receiptPath)
} catch {
  $errorSummary = [string]$_.Exception.Message
  if ($errorSummary.Length -gt 450) { $errorSummary = $errorSummary.Substring(0,450) }
  if ($locationPushed) { Pop-Location; $locationPushed = $false }
  if (-not (Test-Path -LiteralPath $receiptPath)) {
    New-Item -ItemType Directory -Path $receiptRoot -Force | Out-Null
    [ordered]@{
      schema = 'TS-BEADS-NOTEBOOK-MIGRATION-20261015-001/v1'
      status = 'BLOCKED_NEEDS_EXACT_RECONCILIATION'
      stage = $stage
      error = $errorSummary
      notebook_host = $hostObserved
      exact_experiment_source = $runnerCommitObserved
      authority = 'NONE_PRODUCT'
      product_effect = 'NONE'
      historical_archive_status = 'PRESERVED_ON_DESKTOP_NOT_TRANSFERRED'
      checked_at_utc = [DateTime]::UtcNow.ToString('o')
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $receiptPath -Encoding utf8NoBOM -NoNewline
  }
  Write-Output ('TS_BEADS_NOTEBOOK=BLOCKED;STAGE='+$stage+';ERROR='+$errorSummary+';RECEIPT='+$receiptPath)
  exit 1
}
