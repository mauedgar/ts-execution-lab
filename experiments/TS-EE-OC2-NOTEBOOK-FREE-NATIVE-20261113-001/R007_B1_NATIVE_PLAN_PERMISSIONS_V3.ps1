# R007 B1: read-only effective agent deny matrix, isolated Orca worktree. No inference.
$ErrorActionPreference='Stop'
$root='C:\Users\Mauri\orca\workspaces\ts-ee-llm040-source-20261030-001\ts-ee-oc2-r007-b1-file-config-20261118-001'
$dir='experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R007_CLOSED_CONTEXT_RUNROOT'
$cli='C:\Users\Mauri\.local\bin\opencode2.cmd'
Write-Output 'R007_B1_PLAN_V3_START'
if((Get-Location).ProviderPath.TrimEnd('\') -ine $root.TrimEnd('\')){throw 'BLOCKED_ROOT'}
if(((& git rev-parse --verify HEAD).Trim()) -cne '2c58013476d09eb63839f8ebb604c1954473f695' -or $LASTEXITCODE -ne 0){throw 'BLOCKED_HEAD'}
if(((& git hash-object -- ($dir+'/opencode.json')).Trim()) -cne '16ed6e50bddf955db6f27484624b47cbe762fb3b' -or $LASTEXITCODE -ne 0){throw 'BLOCKED_CONFIG_BLOB'}
Push-Location (Join-Path $root $dir)
try {$raw=@(& $cli debug agents --standalone 2>&1);$exitCode=$LASTEXITCODE} finally {Pop-Location}
if($exitCode -ne 0){throw 'BLOCKED_NATIVE_AGENT_DEBUG_EXIT'}
try {$doc=(($raw -join [Environment]::NewLine) | ConvertFrom-Json -ErrorAction Stop)}catch{throw 'BLOCKED_NATIVE_AGENT_FORMAT'}
$items=@()
if($doc -is [array]){$items=@($doc)}
elseif($null -ne $doc.agents){$items=@($doc.agents)}
elseif($null -ne $doc.data){$items=@($doc.data)}
elseif($null -ne $doc.plan){$items=@($doc.plan)}
else{$items=@($doc)}
$shapeKeys=if($items.Count -gt 0){@($items[0].PSObject.Properties.Name)-join ','}else{'EMPTY'}
$plan=$null
foreach($item in $items) {
  if(($item.name -ceq 'plan') -or ($item.id -ceq 'plan') -or ($item.agent -ceq 'plan')) { $plan=$item;break }
}
if($null -eq $plan -and $null -ne $doc.plan){$plan=$doc.plan}
Write-Output ('R007_B1_PLAN_V3_SHAPE;COUNT='+$items.Count+';KEYS='+$shapeKeys+';PLAN_FOUND='+($null -ne $plan))
if($null -eq $plan){throw 'BLOCKED_AGENT_PLAN_NOT_FOUND'}
$rules=@()
if($null -ne $plan.permissions){$rules=@($plan.permissions)}
elseif($null -ne $plan.permission){$rules=@($plan.permission)}
$rulesShape=if($rules.Count -gt 0){@($rules[0].PSObject.Properties.Name)-join ','}else{'EMPTY'}
$denyAllIdx=-1
for($i=0;$i -lt $rules.Count;$i++){
  if($rules[$i].action -ceq '*' -and $rules[$i].resource -ceq '*' -and $rules[$i].effect -ceq 'deny'){$denyAllIdx=$i}
}
$unsafeAfter=0
if($denyAllIdx -ge 0){
  for($i=$denyAllIdx+1;$i -lt $rules.Count;$i++){
    if($rules[$i].effect -in @('allow','ask')){$unsafeAfter++}
  }
}
$strict=($denyAllIdx -ge 0 -and $unsafeAfter -eq 0)
$model=if($null -ne $plan.model){[string]$plan.model}else{'MODEL_NOT_EXPOSED'}
Write-Output ('R007_B1_PLAN_V3_RULES;COUNT='+$rules.Count+';SHAPE='+$rulesShape+';LAST_DENY_ALL_INDEX='+$denyAllIdx+';ALLOW_OR_ASK_AFTER='+$unsafeAfter+';STRICT_DENY='+$strict)
Write-Output ('R007_B1_PLAN_V3_MODEL;MODEL='+$model)
if(-not $strict){throw 'BLOCKED_PLAN_EFFECTIVE_DENY_NOT_PROVEN'}
Write-Output 'R007_B1_PLAN_V3_PERMISSION_DENY_PASS_SOURCE_ONLY_NO_INFERENCE'
