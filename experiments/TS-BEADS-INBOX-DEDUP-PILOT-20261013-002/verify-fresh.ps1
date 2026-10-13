# Independent PowerShell process; read-only Beads checkpoint verification.
param([Parameter(Mandatory=$true)][string]$Tool,[Parameter(Mandatory=$true)][string]$Store,[Parameter(Mandatory=$true)][string]$Active,[Parameter(Mandatory=$true)][string]$A,[Parameter(Mandatory=$true)][string]$B,[Parameter(Mandatory=$true)][string]$SourceA,[Parameter(Mandatory=$true)][string]$SourceB,[Parameter(Mandatory=$true)][string]$Out)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$env:BEADS_DIR=$Store
function BdJson([string[]]$ArgsArray) {
 $r=& $Tool @ArgsArray 2>&1
 if($LASTEXITCODE -ne 0){throw ('BD_FAIL:'+($r -join ' '))}
 $s=($r|Out-String).Trim()
 $match=[regex]::Match($s,'(?m)^[ \t]*(?:\[|\{)')
 if(-not $match.Success){throw 'NO_JSON_PAYLOAD'}
 return ($s.Substring($match.Index)|ConvertFrom-Json)
}
function ReadSource([string]$Id){
 $x=@(BdJson -ArgsArray @('show',$Id,'--json'))[0]
 foreach($line in ([string]$x.description -split "\r?\n")){
  if($line.StartsWith('SOURCE_REF=')){return $line.Substring(11).Trim()}
 }
 return ''
}
try {
 $all=@(BdJson -ArgsArray @('list','--json','--limit','100'))
 $ready=@(BdJson -ArgsArray @('ready','--json'))
 $active=@(BdJson -ArgsArray @('show',$Active,'--json'))[0]
 $hA=@(BdJson -ArgsArray @('show',$A,'--json'))[0]
 $hB=@(BdJson -ArgsArray @('show',$B,'--json'))[0]
 $ca=0;$cb=0
 foreach($item in $all){
  $src=ReadSource -Id ([string]$item.id)
  if($src -ceq $SourceA){$ca++}
  if($src -ceq $SourceB){$cb++}
 }
 $visibleA=@($ready|Where-Object {$_.id -eq $A}).Count -eq 1
 $visibleB=@($ready|Where-Object {$_.id -eq $B}).Count -eq 1
 $pass=$active.status -eq 'closed' -and $hA.status -eq 'open' -and $hB.status -eq 'open' -and $ca -eq 1 -and $cb -eq 1 -and $visibleA -and $visibleB -and $A -ne $B
 $o=[ordered]@{status= $(if($pass){'PASS'}else{'FAIL'});fresh_process_pid=$PID;active_status=$active.status;source_a_count=$ca;source_b_count=$cb;handoff_count=($ca+$cb);source_a_ready=$visibleA;source_b_ready=$visibleB;ids=@($A,$B)}
 $o|ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $Out -Encoding utf8
 if(-not $pass){exit 1}
 exit 0
} catch {
 [ordered]@{status='FAIL';error=$_.Exception.Message}|ConvertTo-Json|Set-Content -LiteralPath $Out -Encoding utf8
 exit 1
}
