# Separate fresh-process readback; no Product effects.
param(
 [Parameter(Mandatory=$true)][string]$BdPath,
 [Parameter(Mandatory=$true)][string]$BeadsDir,
 [Parameter(Mandatory=$true)][string]$ActiveId,
 [Parameter(Mandatory=$true)][string]$HandoffId,
 [Parameter(Mandatory=$true)][string]$OutputPath
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$env:BEADS_DIR = $BeadsDir
function GetBdJson([string[]]$Args) {
 $v = & $BdPath @Args 2>&1
 if ($LASTEXITCODE -ne 0) { throw ("bd failed: " + ($v -join ' ')) }
 return (($v | Out-String).Trim() | ConvertFrom-Json)
}
try {
 $active = @(GetBdJson -Args @('show',$ActiveId,'--json'))[0]
 $handoff = @(GetBdJson -Args @('show',$HandoffId,'--json'))[0]
 $listing = @(GetBdJson -Args @('list','--json','--limit','100'))
 $ready = @(GetBdJson -Args @('ready','--json'))
 $count = @($listing | Where-Object { $_.id -eq $HandoffId }).Count
 $valid = ($active.status -eq 'closed' -and $handoff.status -eq 'open' -and ($ready | Where-Object { $_.id -eq $HandoffId }).Count -ge 1)
 [ordered]@{recovered=[bool]$valid;active_status=$active.status;handoff_status=$handoff.status;handoff_count=$count;handoff_ready=[bool](($ready | Where-Object {$_.id -eq $HandoffId}).Count -ge 1);second_process_pid=$PID} | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $OutputPath -Encoding utf8
 if (-not $valid -or $count -ne 1) { exit 1 }
 exit 0
} catch {
 [ordered]@{recovered=$false;error=$_.Exception.Message} | ConvertTo-Json | Set-Content -LiteralPath $OutputPath -Encoding utf8
 exit 1
}
