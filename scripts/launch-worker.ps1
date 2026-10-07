param([string]$Prompt = "")
if ($Prompt -eq "") { Write-Output "no-op worker"; exit 0 }
Write-Output "worker invoked with prompt of length $($Prompt.Length)"
