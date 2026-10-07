param(
  [Parameter(Mandatory = $true)][string]$ScriptPath
)
$errors = $null
$tokens = $null
[System.Management.Automation.Language.Parser]::ParseFile($ScriptPath, [ref]$tokens, [ref]$errors) | Out-Null
$result = @{
  script = $ScriptPath
  parsed_at = (Get-Date).ToUniversalTime().ToString("o")
  parse_ok = ($errors.Count -eq 0)
  error_count = $errors.Count
  errors = @($errors | ForEach-Object { $_.Message })
}
$result | ConvertTo-Json -Depth 5
if (-not $result.parse_ok) { exit 1 }
