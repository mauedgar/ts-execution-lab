# TS-BEADS 047B: bounded private peer/Windows ACL observation, not SQL admission.
# SOURCE_ONLY. Never configure Tailscale, SQL, ACL or DPAPI.
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)]
  [ValidateSet('Notebook','Desktop')][string]$Role
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$tailscaleSha256='9AB35EB10B9076EC7262696EA98428C91CC6E5F4EFE3FAEFD786EFED0BB6C68D'
$tailscaleExe='C:\Program Files\Tailscale\tailscale.exe'
$expectedHost=if($Role -ceq 'Notebook'){'DESKTOP-DJLBEQH'}else{'DESKTOP-3LJ0E54'}
$expectedPeer=if($Role -ceq 'Notebook'){'DESKTOP-3LJ0E54'}else{'DESKTOP-DJLBEQH'}

function Get-StringDigest {
  param([Parameter(Mandatory)][string]$Value)
  if([string]::IsNullOrWhiteSpace($Value)){throw 'EMPTY_IDENTITY'}
  $bytes=[Text.Encoding]::UTF8.GetBytes($Value)
  return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes))
}
function Evaluate-Status {
  param([Parameter(Mandatory)][string]$Text,
        [Parameter(Mandatory)][string]$SelfName,
        [Parameter(Mandatory)][string]$PeerName)
  if($Text.Length -gt 2097152){throw 'STATUS_TOO_LARGE'}
  $doc=ConvertFrom-Json -InputObject $Text -AsHashtable -Depth 32 -ErrorAction Stop
  if($doc -isnot [Collections.IDictionary]){throw 'STATUS_NOT_OBJECT'}
  if($doc['BackendState'] -cne 'Running'){throw 'TS_NOT_RUNNING'}
  $self=$doc['Self']
  if($self -isnot [Collections.IDictionary] -or
      $self['Online'] -cne $true -or
      $self['HostName'] -ine $SelfName){throw 'TS_SELF_UNVERIFIED'}
  $peers=$doc['Peer']
  if($peers -isnot [Collections.IDictionary]){throw 'TS_PEERS_UNVERIFIED'}
  $matches=@($peers.Values | Where-Object {
    $_ -is [Collections.IDictionary] -and $_['HostName'] -ieq $PeerName
  })
  if($matches.Count -ne 1){throw 'TS_PEER_NOT_UNIQUE'}
  $peer=$matches[0]
  if($peer['Online'] -cne $true){throw 'TS_PEER_OFFLINE'}
  $selfKey=[string]$self['PublicKey']
  $peerKey=[string]$peer['PublicKey']
  if(-not $selfKey.StartsWith('nodekey:') -or
     -not $peerKey.StartsWith('nodekey:')){throw 'TS_NODE_KEY_MISSING'}
  return [pscustomobject]@{
    self_node_key_sha256=(Get-StringDigest $selfKey)
    peer_node_key_sha256=(Get-StringDigest $peerKey)
  }
}
function Run-TailscaleStatus {
  param([string]$Exe)
  # Fixed one-shot observational command. Both streams consumed asynchronously.
  # No untrusted arguments, authentication material or raw status printed.
  $psi=[Diagnostics.ProcessStartInfo]::new()
  $psi.FileName=$Exe
  $psi.ArgumentList.Add('status')
  $psi.ArgumentList.Add('--json')
  $psi.UseShellExecute=$false
  $psi.RedirectStandardOutput=$true
  $psi.RedirectStandardError=$true
  $psi.CreateNoWindow=$true
  $child=[Diagnostics.Process]::new()
  $child.StartInfo=$psi
  try {
    if(-not $child.Start()){throw 'TS_STATUS_START_FAILED'}
    $stdoutTask=$child.StandardOutput.ReadToEndAsync()
    $stderrTask=$child.StandardError.ReadToEndAsync()
    if(-not $child.WaitForExit(12000)){
      $child.Kill($true)
      throw 'TS_STATUS_TIMEOUT'
    }
    if($child.ExitCode -ne 0){throw 'TS_STATUS_FAILED'}
    $out=$stdoutTask.GetAwaiter().GetResult()
    [void]$stderrTask.GetAwaiter().GetResult()
    return $out
  } finally {
    $child.Dispose()
  }
}
try {
  if([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT -or
     [Environment]::MachineName -cne $expectedHost){throw 'HOST_MISMATCH'}
  $win=[Security.Principal.WindowsIdentity]::GetCurrent()
  if($null -eq $win -or $null -eq $win.User -or
     $win.User.Value -notmatch '^S-1-5-21-'){throw 'WIN_SID_UNVERIFIED'}
  if(-not [IO.File]::Exists($tailscaleExe)){throw 'TS_EXECUTABLE_MISSING'}
  if((Get-FileHash -LiteralPath $tailscaleExe -Algorithm SHA256).Hash -cne $tailscaleSha256){
    throw 'TS_BINARY_HASH_MISMATCH'
  }
  $service=Get-Service -Name 'Tailscale' -ErrorAction Stop
  if($service.Status -ne 'Running'){
    throw 'TS_SERVICE_NOT_RUNNING'
  }
  $localApp=[IO.Path]::GetFullPath($env:LOCALAPPDATA)
  if(-not [IO.Directory]::Exists($localApp)){throw 'LOCALAPPDATA_MISSING'}
  $acl=Get-Acl -LiteralPath $localApp -ErrorAction Stop
  if($null -eq $acl -or [string]::IsNullOrWhiteSpace([string]$acl.Owner)){
    throw 'LOCALAPPDATA_ACL_UNREADABLE'
  }
  $aclRules=@($acl.Access)
  $statusText=Run-TailscaleStatus -Exe $tailscaleExe
  $evaluated=Evaluate-Status -Text $statusText -SelfName $expectedHost -PeerName $expectedPeer
  'READONLY_HOST_PEER_SNAPSHOT_PARTIAL'
  'ROLE='+$Role.ToUpperInvariant()
  'SID_SHA256='+ (Get-StringDigest $win.User.Value)
  'LOCALAPPDATA_ACL_RULE_COUNT='+$aclRules.Count
  'LOCALAPPDATA_ACL_IS_PROTECTED='+([string]$acl.AreAccessRulesProtected).ToUpperInvariant()
  'TAILSCALE_SELF_NODE_SHA256='+$evaluated.self_node_key_sha256
  'TAILSCALE_PEER_NODE_SHA256='+$evaluated.peer_node_key_sha256
  'TAILSCALE_PEER_ADVERTISED_ONLINE=TRUE'
  'ACL_EFFECTIVE_ON_FUTURE_SQL_ROOT_UNVERIFIED'
  'TAILSCALE_DATA_ROUTE_AND_SERVE_FUNNEL_UNVERIFIED'
  'SID_DIGEST_OBSERVED_NOT_INDEPENDENTLY_PINNED'
  'SQL_AUTH_DPAPI_BACKUP_AND_UNKNOWN_UNVERIFIED'
  'NO_SQL_OR_CONFIGURATION_EFFECT'
  exit 0
} catch {
  # Intentionally no exception messages, raw CLI JSON, SID, path or IP.
  'BLOCKED_READONLY_HOST_PEER_QUALIFICATION'
  'NO_SQL_OR_CONFIGURATION_EFFECT'
  exit 22
}
