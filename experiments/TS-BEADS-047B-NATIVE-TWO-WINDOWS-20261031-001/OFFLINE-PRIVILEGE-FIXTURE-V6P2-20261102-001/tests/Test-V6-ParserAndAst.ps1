# SOURCE-ONLY Windows PowerShell AST/parser check. NO source invocation or SQL.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$base=Join-Path $PSScriptRoot '..\candidate'
$files=@('Security-047B-V6.psm1','Invoke-047B-V6-Fixture.ps1','Start-047B-V6.ps1')
foreach($name in $files) {
  $path=Join-Path $base $name
  $tokens=$null; $errors=$null
  $ast=[System.Management.Automation.Language.Parser]::ParseFile($path,[ref]$tokens,[ref]$errors)
  if(@($errors).Count -gt 0){throw ('PARSER_FAIL_'+$name)}
  $assignments=@($ast.FindAll({
    param($node)
    $node -is [System.Management.Automation.Language.AssignmentStatementAst]
  },$true))
  foreach($assignment in $assignments) {
    $lhs=$assignment.Left.Extent.Text.Trim()
    if($lhs -match '(?i)^\$(?:(?:script|global|local):)?(?:pid|home|lastexitcode)$') {
      throw ('PROTECTED_AUTOMATIC_ASSIGNMENT_'+$lhs)
    }
  }
  if($name -like 'Invoke-*') {
    $calls=@($ast.FindAll({
      param($node)
      $node -is [System.Management.Automation.Language.CommandAst] -and
        $node.GetCommandName() -ceq 'Assert-V6PrivateAcl'
    },$true))
    if($calls.Count -lt 3){throw 'ACL_CALLS_MISSING'}
    foreach($call in $calls) {
      if($call.CommandElements.Count -gt 3){throw 'ACL_EXTRA_POSITIONAL_ARGUMENT'}
    }
    $src=[IO.File]::ReadAllText($path)
    $start=$src.LastIndexOf([string]([char]10)+'try {')
    if($start -lt 0){throw 'RUNNER_BOOTSTRAP_MISSING'}
    $boot=$src.Substring($start)
    $import=$boot.IndexOf('Import-Module -Name $script:V6Module')
    if($import -lt 0){throw 'RUNNER_IMPORT_MISSING'}
    if($boot.Substring(0,$import) -match '(?m)^\s*Assert-V6\s*\('){
      throw 'UNBOUND_GUARD_BEFORE_IMPORT'
    }
  }
}
[pscustomobject]@{state='PASS_PARSER_AND_AST_ONLY';files=$files.Count;sqlExecuted=$false;effectAuthorized=$false}
