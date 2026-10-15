# Read-only preflight, no installers / secrets / TaskCycle or repo writes.
# Example:
# pwsh -NoProfile -File scripts/devux/verify-station.ps1 -FitFlowRoot C:\TS\repos\FitFlow -TecnotronWindowsRoot C:\TS\repos\tecnotron-ai -TecnotronLinuxRoot /home/tsops/workspaces/tecnotron-ai -LabRoot C:\TS\repos\ts-execution-lab -TransportRoot C:\TS\repos\ts-execution-transport -Distro Ubuntu-24.04 -LinuxUser tsops
[CmdletBinding()]
param(
  [Parameter(Mandatory)][string]$FitFlowRoot,
  [Parameter(Mandatory)][string]$TecnotronWindowsRoot,
  [Parameter(Mandatory)][string]$TecnotronLinuxRoot,
  [Parameter(Mandatory)][string]$LabRoot,
  [Parameter(Mandatory)][string]$TransportRoot,
  [string]$Distro = "Ubuntu-24.04",
  [string]$LinuxUser = "tsops"
)
$ErrorActionPreference = "Stop"
$rows = [System.Collections.Generic.List[object]]::new()
$failed = $false
function Check-WindowsRepo([string]$name, [string]$path, [string]$expected) {
  if (-not (Test-Path -LiteralPath $path -PathType Container)) {
    $script:rows.Add([pscustomobject]@{ name=$name; result="MISSING"; root=$path; branch=$null; head=$null; tree=$null })
    $script:failed=$true
    return
  }
  $head = (& git.exe -C $path rev-parse HEAD 2>$null)
  $branch = (& git.exe -C $path branch --show-current 2>$null)
  $tree = (& git.exe -C $path rev-parse HEAD^{tree} 2>$null)
  $dirty = (& git.exe -C $path status --porcelain=v1 2>$null)
  if ($LASTEXITCODE -ne 0 -or -not $head -or -not $tree) {
    $script:rows.Add([pscustomobject]@{name=$name;result="INVALID_GIT";root=$path;branch=$branch;head=$head;tree=$tree})
    $script:failed=$true
    return
  }
  $result = if ($branch -ne $expected -or $dirty) { "DRIFT" } else { "PASS" }
  if ($result -ne "PASS") { $script:failed=$true }
  $script:rows.Add([pscustomobject]@{name=$name;result=$result;root=$path;branch=$branch;head=$head;tree=$tree})
}
function Check-LinuxRepo([string]$name, [string]$path, [string]$expected) {
  $base = @("-d", $Distro, "-u", $LinuxUser, "--exec", "/usr/bin/git", "-C", $path)
  $head = (& wsl.exe @base rev-parse HEAD 2>$null)
  $headExit = $LASTEXITCODE
  $branch = (& wsl.exe @base branch --show-current 2>$null)
  $branchExit = $LASTEXITCODE
  $tree = (& wsl.exe @base rev-parse "HEAD^{tree}" 2>$null)
  $treeExit = $LASTEXITCODE
  $dirty = (& wsl.exe @base status --porcelain=v1 2>$null)
  $statusExit = $LASTEXITCODE
  $result = if (($headExit -ne 0) -or ($branchExit -ne 0) -or ($treeExit -ne 0) -or ($statusExit -ne 0)) { "INVALID_GIT" } elseif ($branch -ne $expected -or $dirty) { "DRIFT" } else { "PASS" }
  if ($result -ne "PASS") { $script:failed=$true }
  $script:rows.Add([pscustomobject]@{name=$name;result=$result;root=$path;branch=$branch;head=$head;tree=$tree})
}
Check-WindowsRepo "FitFlow" $FitFlowRoot "develop"
Check-WindowsRepo "TecnotronWindowsNavigation" $TecnotronWindowsRoot "tools"
Check-LinuxRepo "TecnotronLinuxExecution" $TecnotronLinuxRoot "tools"
Check-WindowsRepo "TSExecutionLab" $LabRoot "main"
Check-WindowsRepo "TSExecutionTransport" $TransportRoot "main"
[pscustomobject]@{schema="ts-devux-station-preflight/v0";status= $(if($failed){"BLOCKED_OR_DRIFT"}else{"PASS"}); checks=$rows} | ConvertTo-Json -Depth 6
if($failed) { exit 2 }
