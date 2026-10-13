# Fresh-process proof for continuation 003.
param([Parameter(Mandatory=$true)][string]$Bd,[Parameter(Mandatory=$true)][string]$Store,[Parameter(Mandatory=$true)][string]$Active,[Parameter(Mandatory=$true)][string]$Handoff,[Parameter(Mandatory=$true)][string]$Output)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$env:BEADS_DIR=$Store
function ReadJson([string[]]$Arguments) {
 $v=& $Bd @Arguments 2>&1
 if($LASTEXITCODE -ne 0){throw ('BD_FAIL '+($v -join ' '))}
 $s=($v|Out-String).Trim()
 $m=[regex]::Match($s,'(?m)^[ \t]*(?:\[|\{)')
 if(-not $m.Success){throw 'NO_JSON_ARRAY_OR_OBJECT'}
 return ($s.Substring($m.Index)|ConvertFrom-Json)
}
try {
 $a=@(ReadJson -Arguments @('show',$Active,'--json'))[0]
 $h=@(ReadJson -Arguments @('show',$Handoff,'--json'))[0]
 $all=@(ReadJson -Arguments @('list','--json','--limit','100'))
 $ready=@(ReadJson -Arguments @('ready','--json'))
 $n=@($all|Where-Object {$_.id -eq $Handoff}).Count
 $visible=@($ready|Where-Object {$_.id -eq $Handoff}).Count -eq 1
 $ok=$a.status -eq 'closed' -and $h.status -eq 'open' -and $n -eq 1 -and $visible
 [ordered]@{recovered=[bool]$ok;active_status=$a.status;handoff_status=$h.status;handoff_count=$n;handoff_ready=[bool]$visible;pid=$PID} | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $Output -Encoding utf8
 if(-not $ok){exit 1}
 exit 0
} catch {
 [ordered]@{recovered=$false;error=$_.Exception.Message} | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $Output -Encoding utf8
 exit 1
}
