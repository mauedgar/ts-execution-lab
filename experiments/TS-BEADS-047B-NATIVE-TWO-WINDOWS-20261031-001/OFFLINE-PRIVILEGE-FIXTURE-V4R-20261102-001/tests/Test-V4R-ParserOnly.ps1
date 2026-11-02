# No-effect PowerShell parser gate. Does not invoke scripts or SQL.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$base=Join-Path $PSScriptRoot '..\candidate'
$files=@('Security-047B-V4R.psm1','Invoke-047B-V4R-Fixture.ps1','Start-047B-V4R.ps1')
foreach($name in $files) {
  $path=Join-Path $base $name
  $tokens=$null
  $errors=$null
  [void][System.Management.Automation.Language.Parser]::ParseFile($path,[ref]$tokens,[ref]$errors)
  if(@($errors).Count -ne 0){throw ('PARSER_FAIL_'+$name)}
}
[pscustomobject]@{state='PASS_PARSER_ONLY';files=$files.Count;sqlExecuted=$false;effectAuthorized=$false}
