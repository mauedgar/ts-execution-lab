# Disposable CI-only installer negatives; payload fixtures are inert and never executed.
[CmdletBinding()]
param([Parameter(Mandatory)][string]$Parent,[Parameter(Mandatory)][string]$Installer,[Parameter(Mandatory)][string]$SourceNode,[Parameter(Mandatory)][string]$NodeSha256)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$utf8=[Text.UTF8Encoding]::new($false,$true)
function Digest([byte[]]$b){[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($b)).ToLowerInvariant()}
function Add-Entry([IO.Compression.ZipArchive]$Archive,[string]$Name,[byte[]]$Bytes){
 $entry=$Archive.CreateEntry('ts-ee-mat-xform-kit/'+$Name);$stream=$entry.Open()
 try{$stream.Write($Bytes,0,$Bytes.Length)}finally{$stream.Dispose()}
}
function Test-Denial([string]$Label,[string[]]$ExtraFiles,[string[]]$ExtraDirs,[string]$Mode,[string]$Reason){
 $root=Join-Path $Parent ('negative-'+$Label)
 $archivePath=Join-Path $Parent ('fixture-'+$Label+'.zip')
 $paths=@('guard.mjs','Invoke-Guard.ps1','package.json','package-lock.json','src/mat-xform/cli.ts','src/mat-xform/contracts.ts','src/mat-xform/materializer.ts','node_modules/zod/package.json')+@($ExtraFiles)
 $bytes=$utf8.GetBytes('inert fixture data')
 $digest=Digest $bytes
 $entries=[Collections.Generic.List[string]]::new()
 $file=[IO.File]::Open($archivePath,[IO.FileMode]::CreateNew)
 $archive=[IO.Compression.ZipArchive]::new($file,[IO.Compression.ZipArchiveMode]::Create,$false)
 try{
  foreach($p in $paths){
   Add-Entry $archive ('install/'+$p) $bytes
   $encoded=ConvertTo-Json -InputObject ([string]$p) -Compress
   $entries.Add(('{"bytes":'+$bytes.Length+',"path":'+$encoded+',"sha256":"'+$digest+'"}'))
  }
  foreach($d in $ExtraDirs){Add-Entry $archive ('install/'+$d+'/') ([byte[]]::new(0))}
  $manifest='{"files":['+($entries -join ',')+'],"schema":"ts-ee/mat-xform-install/v1"}'
  if($Mode -eq 'duplicate'){$manifest=$manifest.Replace('"schema":','"schema":"duplicate","schema":')}
  if($Mode -eq 'wrong-type'){$manifest=$manifest.Replace('"bytes":'+$bytes.Length,'"bytes":"'+$bytes.Length+'"')}
  if($Mode -eq 'noncanonical'){$manifest=' '+$manifest}
  if($Mode -eq 'schema-ignorable'){
   $schema='ts-ee/mat-xform-install/v1'
   $mutated=$schema.Insert(2,[string][char]0x00ad)
   Write-Output ('ORDINAL_SCHEMA_PROBE old_schema_equal='+[bool]($mutated -ceq $schema)+' old_manifest_equal='+[bool]($manifest.Replace($schema,$mutated) -ceq $manifest)+' ordinal_equal='+[string]::Equals($mutated,$schema,[StringComparison]::Ordinal))
   $manifest=$manifest.Replace($schema,$mutated)
  }
  if($Mode -eq 'schema-escaped'){$manifest=$manifest.Replace('ts-ee/mat-xform-install/v1','\u0074s-ee/mat-xform-install/v1')}
  $manifestBytes=$utf8.GetBytes($manifest)
  Add-Entry $archive 'manifest.json' $manifestBytes
 }finally{$archive.Dispose();$file.Dispose()}
 $zipHash=(Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
 $result=@(pwsh.exe -NoLogo -NoProfile -NonInteractive -File $Installer -Root $root -KitZip $archivePath -ZipSha256 $zipHash -ManifestSha256 (Digest $manifestBytes) -SourceNode $SourceNode -NodeSha256 $NodeSha256)
 if($LASTEXITCODE -ne 1 -or $result.Count -ne 1 -or (Test-Path -LiteralPath $root)){throw ('NEGATIVE_EFFECT_'+$Label)}
 $r=$result[0]|ConvertFrom-Json
 if($r.status -cne 'BLOCKED_PRECONDITION' -or $r.effect -cne 'NONE' -or ($Reason -and $r.reason -cne $Reason)){throw ('NEGATIVE_RECEIPT_'+$Label+':'+$result[0])}
 Write-Output ('PASS install-'+$Label+' '+$r.reason+' root absent')
}
Test-Denial 'file-dir' @('a','a/b') @() '' 'ARCHIVE_NAMESPACE_CONFLICT'
Test-Denial 'dir-file' @('a/b','a') @() '' 'ARCHIVE_NAMESPACE_CONFLICT'
Test-Denial 'explicit-dir' @('a') @('a') '' 'ARCHIVE_NAMESPACE_CONFLICT'
Test-Denial 'ancestor-case' @('A/x','a/y') @() '' 'ARCHIVE_NAMESPACE_CONFLICT'
Test-Denial 'linefeed' @("x`n") @() '' 'ARCHIVE_PATH_DENIED'
Test-Denial 'manifest-duplicate' @() @() 'duplicate' 'MANIFEST_DUPLICATE_KEY'
Test-Denial 'manifest-type' @() @() 'wrong-type' ''
Test-Denial 'manifest-noncanonical' @() @() 'noncanonical' 'MANIFEST_NONCANONICAL'
Test-Denial 'manifest-schema-ignorable' @() @() 'schema-ignorable' 'MANIFEST_SCHEMA'
Test-Denial 'manifest-schema-escaped' @() @() 'schema-escaped' 'MANIFEST_NONCANONICAL'
