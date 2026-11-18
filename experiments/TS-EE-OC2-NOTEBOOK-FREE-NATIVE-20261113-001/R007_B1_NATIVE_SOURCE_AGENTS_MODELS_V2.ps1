# R007 B1 native static provider preflight, no inference, no account or global changes.
$ErrorActionPreference='Stop'
$root='C:\Users\Mauri\orca\workspaces\ts-ee-llm040-source-20261030-001\ts-ee-oc2-r007-b1-file-config-20261118-001'
$head='2c58013476d09eb63839f8ebb604c1954473f695'
$rel='experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R007_CLOSED_CONTEXT_RUNROOT/opencode.json'
$cli='C:\Users\Mauri\.local\bin\opencode2.cmd'
Write-Output 'R007_B1_NATIVE_V2_START'
if ((Get-Location).ProviderPath.TrimEnd('\') -ine $root.TrimEnd('\')) { throw 'BLOCKED_ORCA_BINDING' }
if ((& git rev-parse --verify HEAD).Trim() -cne $head -or $LASTEXITCODE -ne 0) { throw 'BLOCKED_HEAD' }
if ((& git hash-object -- $rel).Trim() -cne '16ed6e50bddf955db6f27484624b47cbe762fb3b' -or $LASTEXITCODE -ne 0) { throw 'BLOCKED_CONFIG_BLOB' }
$dir=Join-Path $root 'experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R007_CLOSED_CONTEXT_RUNROOT'
$oldInline=$env:OPENCODE_CONFIG_CONTENT
Remove-Item Env:OPENCODE_CONFIG_CONTENT -ErrorAction SilentlyContinue
try {
  Push-Location $dir
  try {
    $cfg=@(& $cli debug config --standalone 2>&1); $cfgExit=$LASTEXITCODE
    $agents=@(& $cli debug agents --standalone 2>&1); $agentsExit=$LASTEXITCODE
    $models=@(& $cli models --standalone 2>&1); $modelsExit=$LASTEXITCODE
  } finally { Pop-Location }
} finally {
  if ($null -ne $oldInline) { $env:OPENCODE_CONFIG_CONTENT=$oldInline } else {Remove-Item Env:OPENCODE_CONFIG_CONTENT -ErrorAction SilentlyContinue}
}
if ($cfgExit -ne 0 -or $agentsExit -ne 0 -or $modelsExit -ne 0) { Write-Output ('R007_B1_NATIVE_V2_EXIT;CFG='+$cfgExit+';AGENTS='+$agentsExit+';MODELS='+$modelsExit); throw 'BLOCKED_NATIVE_PROBE_NONZERO' }
$cfgText=($cfg -join [Environment]::NewLine)
try { $cfgObj=$cfgText | ConvertFrom-Json -ErrorAction Stop; $cfgParsed=$true } catch {$cfgParsed=$false}
$cfgKeys=if($cfgParsed){(@($cfgObj.PSObject.Properties.Name) -join ',')}else{'NOT_JSON'}
$cfgMentionsFile=$cfgText.Contains('R007_CLOSED_CONTEXT_RUNROOT')
$agentText=($agents -join [Environment]::NewLine)
try { $agentObj=$agentText | ConvertFrom-Json -ErrorAction Stop; $agentParsed=$true } catch {$agentParsed=$false}
$planMention=$agentText -match '(?i)(?:^|[^a-z])plan(?:[^a-z]|$)'
$modelMention=$agentText.Contains('opencode/deepseek-v4.1-flash-free')
$denyMention=$agentText -match '(?i)deny'
$modelLines=@($models | ForEach-Object { [string]$_ } | Where-Object {$_ -match '^[a-z][a-z0-9-]*/'})
$freeCount=@($modelLines | Where-Object {$_ -match '^opencode/'}).Count
$outsideCount=@($modelLines | Where-Object {$_ -notmatch '^opencode/'}).Count
$pinnedCount=@($modelLines | Where-Object {$_ -ceq 'opencode/deepseek-v4.1-flash-free'}).Count
Write-Output ('R007_B1_NATIVE_V2_CONFIG;JSON='+$cfgParsed+';KEYS='+$cfgKeys+';FILE_MENTION='+$cfgMentionsFile)
Write-Output ('R007_B1_NATIVE_V2_AGENTS;JSON='+$agentParsed+';PLAN_MENTION='+$planMention+';MODEL_MENTION='+$modelMention+';DENY_MENTION='+$denyMention+';COUNT='+@($agents).Count)
Write-Output ('R007_B1_NATIVE_V2_MODELS;OPENCODE='+$freeCount+';OTHER_PROVIDER='+$outsideCount+';PINNED='+$pinnedCount)
Write-Output 'R007_B1_NATIVE_V2_TERMINAL_NO_INFERENCE'
