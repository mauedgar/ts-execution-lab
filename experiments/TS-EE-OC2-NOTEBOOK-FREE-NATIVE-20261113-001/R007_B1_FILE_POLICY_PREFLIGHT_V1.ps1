# R007 B1 preflight ONLY. NO inference. Orca-owned visible terminal of exact isolated worktree.
$ErrorActionPreference = 'Stop'
$root = 'C:\Users\Mauri\orca\workspaces\ts-ee-llm040-source-20261030-001\ts-ee-oc2-r007-b1-file-config-20261118-001'
$expectHead = '2c58013476d09eb63839f8ebb604c1954473f695'
$relativeConfig = 'experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R007_CLOSED_CONTEXT_RUNROOT/opencode.json'
$expectBlob = '16ed6e50bddf955db6f27484624b47cbe762fb3b'
$cli = 'C:\Users\Mauri\.local\bin\opencode2.cmd'
$expectShimSha256 = '4D793D1A5A4CEBEA5A404B53EB6D6D2065EC36AEB11CDA8803B7BF16CB8F2F49'
Write-Output 'R007_B1_FILE_POLICY_PREFLIGHT_BEGIN'
if ((Get-Location).ProviderPath.TrimEnd('\') -ine $root.TrimEnd('\')) { throw 'BLOCKED_ORCA_TERMINAL_WORKTREE_MISMATCH' }
$head = (& git rev-parse --verify HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $head -cne $expectHead) { throw 'BLOCKED_WORKTREE_HEAD_MISMATCH' }
$blob = (& git hash-object -- $relativeConfig).Trim()
if ($LASTEXITCODE -ne 0 -or $blob -cne $expectBlob) { throw 'BLOCKED_FILE_POLICY_BLOB_MISMATCH' }
if (-not (Test-Path -LiteralPath $cli -PathType Leaf)) { throw 'BLOCKED_CLI_SHIM_MISSING' }
$shimDigest = (Get-FileHash -LiteralPath $cli -Algorithm SHA256).Hash
if ($shimDigest -cne $expectShimSha256) { throw 'BLOCKED_CLI_SHIM_CHANGED' }
$version = ((& $cli --version) -join ' ').Trim()
if ($LASTEXITCODE -ne 0 -or $version -cne 'opencode v2.2.5') { throw 'BLOCKED_CLI_VERSION_CHANGED' }
$file = Join-Path $root ($relativeConfig.Replace('/','\'))
$expected = (Get-Content -LiteralPath $file -Raw -Encoding UTF8) | ConvertFrom-Json
if ($expected.model -cne 'opencode/deepseek-v4.1-flash-free' -or @($expected.policies).Count -ne 9) { throw 'BLOCKED_FILE_POLICY_SOURCE' }
$oldEnv = $env:OPENCODE_CONFIG_CONTENT
Remove-Item Env:OPENCODE_CONFIG_CONTENT -ErrorAction SilentlyContinue
try {
  Push-Location (Split-Path -Path $file -Parent)
  try {
    $raw = @(& $cli debug config --standalone 2>&1)
    $nativeExit = $LASTEXITCODE
  } finally {
    Pop-Location
  }
} finally {
  if ($null -ne $oldEnv) { $env:OPENCODE_CONFIG_CONTENT = $oldEnv } else { Remove-Item Env:OPENCODE_CONFIG_CONTENT -ErrorAction SilentlyContinue }
}
if ($nativeExit -ne 0) { throw 'BLOCKED_NATIVE_CONFIG_DEBUG_EXIT' }
try { $effective = (($raw -join [Environment]::NewLine) | ConvertFrom-Json -ErrorAction Stop) } catch { throw 'BLOCKED_NATIVE_CONFIG_NOT_JSON' }
$policyEqual = ((ConvertTo-Json -InputObject $expected.policies -Depth 20 -Compress) -ceq (ConvertTo-Json -InputObject $effective.policies -Depth 20 -Compress))
$globalDeny = ((ConvertTo-Json -InputObject $expected.permissions -Depth 20 -Compress) -ceq (ConvertTo-Json -InputObject $effective.permissions -Depth 20 -Compress))
$modelEqual = ($effective.model -ceq $expected.model -and $effective.small_model -ceq $expected.small_model -and $effective.default_agent -ceq $expected.default_agent)
$rolesEqual = $true
foreach ($role in @('plan','title','summary','compaction')) {
  if ($effective.agents.$role.model -cne $expected.agents.$role.model) { $rolesEqual = $false }
  $a = ConvertTo-Json -InputObject $expected.agents.$role.permissions -Depth 20 -Compress
  $b = ConvertTo-Json -InputObject $effective.agents.$role.permissions -Depth 20 -Compress
  if ($a -cne $b) { $rolesEqual = $false }
}
Write-Output ('R007_B1_NATIVE_FILE_POLICY_CHECK;POLICIES=' + $policyEqual + ';GLOBAL_DENY=' + $globalDeny + ';MODELS=' + $modelEqual + ';ROLES=' + $rolesEqual + ';NATIVE_POLICY_COUNT=' + @($effective.policies).Count)
if (-not ($policyEqual -and $globalDeny -and $modelEqual -and $rolesEqual)) { throw 'BLOCKED_NATIVE_EFFECTIVE_POLICY_MISMATCH' }
Write-Output 'R007_B1_FILE_POLICY_PREFLIGHT_PASS_SOURCE_AND_EFFECTIVE_CONFIG_ONLY'
