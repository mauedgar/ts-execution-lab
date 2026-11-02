# Distinct attempt 002 on GitHub-hosted Windows. No SQL/Beads or notebook. Verify exact LF bytes.
[CmdletBinding()] param([Parameter(Mandatory=$true)][string]$SourceCheckoutRoot)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$PSNativeCommandUseErrorActionPreference=$false
$attempt='TS-BEADS-047B-V6P1-WINDOWS-PYFIX-20261102-003'
$subject='0118028c2508c2ce274fd42240f847adf7ff2187'
$root=(Resolve-Path -LiteralPath $SourceCheckoutRoot).Path
$base=Join-Path $root 'experiments\TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001\OFFLINE-PRIVILEGE-FIXTURE-V6P1-20261102-001'
$reportPath=Join-Path $env:RUNNER_TEMP 'TS_BEADS_047B_V6P1_WINDOWS_PYFIX_003_RESULT.json'
$report=[ordered]@{
  attempt=$attempt;sourceCommit=$subject;githubRunId=$env:GITHUB_RUN_ID;
  githubRunAttempt=$env:GITHUB_RUN_ATTEMPT;platform='GITHUB_HOSTED_WINDOWS_2022';
  hostNotebookTested=$false;sqlExecuted=$false;beadsModified=$false;
  productModified=$false;issuerProvisioned=$false;lastStage='PRECHECK';
  stages=@();fileChecks=@();testCopyPatched=$false;testCopyHash=$null;verdict='IN_PROGRESS';failureCode=$null
}
$failed=$false
function Require([bool]$ok,[string]$reason){if(-not $ok){throw $reason}}
try {
  Require ($env:GITHUB_RUN_ATTEMPT -ceq '1') 'RETRY_NOT_AUTHORIZED'
  Require ($env:RUNNER_OS -ceq 'Windows') 'WRONG_HOST_CLASS'
  Require ([IO.Directory]::Exists($base)) 'SOURCE_NOT_MATERIALIZED'
  Require ([IO.Directory]::Exists($env:RUNNER_TEMP)) 'RUNNER_TEMP_MISSING'
  $got=(& git -C $root rev-parse HEAD).Trim()
  Require ($LASTEXITCODE -eq 0 -and $got -ceq $subject) 'CHECKOUT_NOT_EXACT_SUBJECT'
  $manifestPath=Join-Path $base 'MANIFEST.json'
  $manifestBlob=(& git -C $root -c core.autocrlf=false hash-object --no-filters $manifestPath).Trim()
  Require ($LASTEXITCODE -eq 0 -and $manifestBlob -ceq '401e5e11fb88f537ed0b0bd6b25b346afa1e3d96') 'MANIFEST_PIN_MISMATCH'
  $manifest=Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json -NoEnumerate
  Require ($manifest.sourceOnly -eq $true -and $manifest.notDispatchable -eq $true -and $manifest.grantPresent -eq $false -and $manifest.realOffHostExclusiveClaimVerified -eq $false) 'SOURCE_FENCE_MISMATCH'
  foreach($entry in $manifest.files){
    $p=Join-Path $base $entry.path
    Require ([IO.File]::Exists($p)) 'SOURCE_FILE_MISSING'
    $bytes=[IO.File]::ReadAllBytes($p)
    $lfCount=0; $crCount=0; $crlfCount=0
    for($i=0;$i -lt $bytes.Length;$i++){
      if($bytes[$i] -eq 10){$lfCount++;if($i -gt 0 -and $bytes[$i-1] -eq 13){$crlfCount++}}
      if($bytes[$i] -eq 13){$crCount++}
    }
    $bom=($bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191)
    $sha=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes))
    $blob=(& git -C $root -c core.autocrlf=false hash-object --no-filters $p).Trim()
    $blobExit=$LASTEXITCODE
    $record=[ordered]@{
      path=[string]$entry.path; expectedBytes=[int]$entry.bytes; actualBytes=$bytes.Length;
      actualLF=$lfCount; actualCR=$crCount; actualCRLF=$crlfCount; bom=$bom;
      expectedSha256=[string]$entry.sha256Utf8Lf; actualSha256=$sha;
      expectedGitBlob=[string]$entry.gitBlobSha1; actualGitBlob=$blob
    }
    $report.fileChecks+= $record
    Require ($bytes.Length -eq [int]$entry.bytes) ('SOURCE_BYTE_LENGTH_MISMATCH:'+ $entry.path)
    Require (-not $bom) ('SOURCE_BOM:'+ $entry.path)
    Require ($crCount -eq 0) ('SOURCE_NOT_LF:'+ $entry.path)
    Require ($sha -ceq [string]$entry.sha256Utf8Lf) ('SOURCE_SHA256_MISMATCH:'+ $entry.path)
    Require ($blobExit -eq 0 -and $blob -ceq [string]$entry.gitBlobSha1) ('SOURCE_BLOB_MISMATCH:'+ $entry.path)
  }
  Require ($report.fileChecks.Count -eq 7) 'EXPECTED_SEVEN_SOURCE_FILES'
  $report.stages+= 'PINNED_7_FILES_AND_MANIFEST_PASS'
  $report.lastStage='PYTHON_UNITTEST'
  $env:PYTHONDONTWRITEBYTECODE='1'
  $copyRoot=Join-Path $env:RUNNER_TEMP ('ts047b-unittest-copy-'+$env:GITHUB_RUN_ID)
  Require (-not (Test-Path -LiteralPath $copyRoot)) 'TEST_COPY_COLLISION'
  $copyCandidate=Join-Path $copyRoot 'candidate'
  $copyTests=Join-Path $copyRoot 'tests'
  [void][IO.Directory]::CreateDirectory($copyRoot)
  [void][IO.Directory]::CreateDirectory($copyTests)
  Copy-Item -LiteralPath (Join-Path $base 'candidate') -Destination $copyCandidate -Recurse -ErrorAction Stop
  $originalTest=Join-Path $base 'tests\\test_source_contract.py'
  $testCopy=Join-Path $copyTests 'test_source_contract.py'
  $originalText=[IO.File]::ReadAllText($originalTest,[Text.Encoding]::UTF8)
  Require ($originalText.Contains('cls.run=RUN.read_text(encoding=') -and $originalText.Contains('self.run')) 'EXPECTED_ORIGINAL_TEST_DEFECT_ABSENT'
  $modified=$originalText.Replace('cls.run=RUN.read_text(', 'cls.runner_source=RUN.read_text(').Replace('self.run', 'self.runner_source')
  Require (-not $modified.Contains('cls.run=RUN.read_text(') -and -not $modified.Contains('self.run,') -and $modified.Contains('cls.runner_source=RUN.read_text(')) 'TEST_COPY_PATCH_FAILED'
  [IO.File]::WriteAllText($testCopy,$modified,[Text.UTF8Encoding]::new($false))
  $report.testCopyPatched=$true
  $report.testCopyHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([IO.File]::ReadAllBytes($testCopy)))
  & python -m unittest discover -s $copyTests -p 'test_source_contract.py' -v
  Require ($LASTEXITCODE -eq 0) 'PATCHED_COPY_PYTHON_UNITTEST_FAIL'
  $report.stages+= 'PATCHED_COPY_PYTHON_UNITTEST_PASS'
  $report.lastStage='POWERSHELL_PARSER_AST'
  & pwsh -NoLogo -NoProfile -NonInteractive -File (Join-Path $base 'tests\Test-V6-ParserAndAst.ps1')
  Require ($LASTEXITCODE -eq 0) 'POWERSHELL_AST_FAIL'
  $report.stages+= 'POWERSHELL_AST_PASS'
  $report.lastStage='NEGATIVE_UNPROVISIONED_ISSUER'
  & pwsh -NoLogo -NoProfile -NonInteractive -File (Join-Path $base 'tests\Test-V6-Negative.ps1')
  Require ($LASTEXITCODE -eq 0) 'NEGATIVE_ISSUER_FAIL'
  $report.stages+= 'NEGATIVE_ISSUER_PASS'
  $report.lastStage='WIN32_CSHARP_AND_PRIVATE_SCRATCH_ACL'
  $module=Join-Path $base 'candidate\Security-047B-V6.psm1'
  Import-Module $module -Force -ErrorAction Stop
  $scratch=Join-Path $env:RUNNER_TEMP ('ts047b-nosql-'+$env:GITHUB_RUN_ID)
  Require (-not (Test-Path -LiteralPath $scratch)) 'SCRATCH_EXISTS'
  New-V6AtomicPrivateDirectory $scratch
  Assert-V6PrivateAcl $scratch $false
  $scratchFile=Join-Path $scratch 'receipt.txt'
  $stream=New-V6AtomicPrivateFile $scratchFile
  try { $stream.WriteByte(65); $stream.Flush($true) } finally { $stream.Dispose() }
  Assert-V6PrivateAcl $scratchFile $false
  $report.stages+= 'WIN32_ADDTYPE_AND_ATOMIC_ACL_SCRATCH_PASS'
  $report.lastStage='TERMINAL'
  $report.verdict='PASS_NATIVE_NO_SQL_GITHUB_HOST_ONLY'
} catch {
  $failed=$true
  $report.verdict='FAILED_NO_SQL'
  $report.failureCode=$_.Exception.Message
} finally {
  $json=($report | ConvertTo-Json -Depth 5)
  [IO.File]::WriteAllText($reportPath,($json+[Environment]::NewLine),[Text.UTF8Encoding]::new($false))
  Write-Output ('TS047B_WINDOWS_NOSQL_RESULT='+$report.verdict+';LAST_STAGE='+$report.lastStage+';SQL=false;Product=false')
}
if($failed){throw ('NO_SQL_NATIVE_GATE_'+$report.lastStage)}
