# TS-BEADS 047B V6P3 - source-only AST + adversarial tests, NO SQL or effects.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$base=Join-Path $PSScriptRoot '..\candidate'
$names=@('Security-047B-V6.psm1','Invoke-047B-V6-Fixture.ps1','Start-047B-V6.ps1')
$protected=@('pid','home','lastexitcode','pshome','psversiontable','psscriptroot','pscommandpath','myinvocation','executioncontext','host','pwd','error','null','true','false','args','input','matches','foreach','pscmdlet','stacktrace','nestedpromptlevel','this')
$protectedPattern='(?i)\$(?:(?:script|global|local|private):)?(?:'+(($protected | ForEach-Object {[regex]::Escape($_)}) -join '|')+')(?![A-Za-z0-9_])'
function Assert-V6P3SafeAst([string]$Code,[string]$Label) {
  $tokens=$null
  $errors=$null
  $ast=[System.Management.Automation.Language.Parser]::ParseInput($Code,[ref]$tokens,[ref]$errors)
  if(@($errors).Count -gt 0){throw ('PARSER_FAIL_'+$Label)}
  foreach($a in @($ast.FindAll({
    param($node)
    $node -is [System.Management.Automation.Language.AssignmentStatementAst]
  },$true))) {
    $left=$a.Left.Extent.Text
    if($left -match $protectedPattern){throw ('PROTECTED_LHS_'+$Label)}
  }
  foreach($u in @($ast.FindAll({
    param($node)
    $node -is [System.Management.Automation.Language.UnaryExpressionAst]
  },$true))) {
    $statement=$u.Extent.Text
    if($statement -match '(?i)(?:\+\+|--)' -and $statement -match $protectedPattern){
      throw ('PROTECTED_UNARY_'+$Label)
    }
  }
  foreach($c in @($ast.FindAll({
    param($node)
    $node -is [System.Management.Automation.Language.CommandAst]
  },$true))) {
    $name=$c.GetCommandName()
    # No dynamic variable-provider mutation in a fail-closed source candidate.
    if($null -ne $name -and $name -in @('Set-Variable','New-Variable','Remove-Variable','Clear-Variable')){
      throw ('DYNAMIC_VARIABLE_PROVIDER_'+$Label)
    }
    if($null -ne $name -and $name -in @('Set-Item','New-Item','Remove-Item','Clear-Item')){
      $elements=$c.Extent.Text
      if($elements -match '(?i)variable\s*:'){
        throw ('VARIABLE_DRIVE_MUTATION_'+$Label)
      }
    }
  }
  foreach($call in @($ast.FindAll({
    param($node)
    $node -is [System.Management.Automation.Language.InvokeMemberExpressionAst]
  },$true))) {
    if($call.Extent.Text -match '(?i)\.PSVariable\s*\.\s*(?:Set|Remove)\s*\('){
      throw ('PSVARIABLE_DYNAMIC_MUTATION_'+$Label)
    }
  }
  return $ast
}
foreach($name in $names){
  $path=Join-Path $base $name
  if(-not [IO.File]::Exists($path)){throw ('SOURCE_MISSING_'+$name)}
  $raw=[IO.File]::ReadAllBytes($path)
  if($raw.Length -gt 0 -and $raw[0] -eq 239){throw ('UNEXPECTED_BOM_'+$name)}
  if([Text.Encoding]::UTF8.GetString($raw).Contains([char]13)){throw ('NON_LF_SOURCE_'+$name)}
  $code=[IO.File]::ReadAllText($path,[Text.UTF8Encoding]::new($false))
  $parsed=Assert-V6P3SafeAst $code $name
  if($name -like 'Invoke-*'){
    $calls=@($parsed.FindAll({
      param($node)
      $node -is [System.Management.Automation.Language.CommandAst] -and
        $node.GetCommandName() -ceq 'Assert-V6PrivateAcl'
    },$true))
    if($calls.Count -lt 3){throw 'ACL_CALLS_MISSING'}
    foreach($c in $calls){if($c.CommandElements.Count -gt 3){throw 'ACL_EXTRA_POSITIONAL_ARGUMENT'}}
  }
}
$negatives=@(
  '$PID=9',
  '$script:HOME += "x"',
  '$PSVersionTable.Major = 8',
  '$LASTEXITCODE++',
  '$MyInvocation[0] = 3',
  'Set-Variable -Name PID -Value 9',
  'New-Variable -Name PID -Value 9',
  'Set-Item -Path variable:PID -Value 9',
  '$ExecutionContext.SessionState.PSVariable.Set("PID",9)'
)
foreach($sample in $negatives){
  $rejected=$false
  try{[void](Assert-V6P3SafeAst $sample 'NEGATIVE_FIXTURE')}catch{$rejected=$true}
  if(-not $rejected){throw ('NEGATIVE_ACCEPTED_'+$sample)}
}
[void](Assert-V6P3SafeAst '$script:ChildProcessId=9; Write-Output $PID' 'BENIGN_FIXTURE')
[pscustomobject]@{status='PASS_V6P3_AST_SOURCE_ONLY';files=$names.Count;negativeFixtures=$negatives.Count;benignFixtures=1;effect=false;sql=false}
