# TS-BEADS 047B A002: PURE SOURCE-ONLY PROTOTYPE. NO EFFECT LAUNCHER.
# This standalone library does not call GitHub, PowerShell processes, files, SQL, Dolt, or Beads.
# It is NOT installed into / invoked by the historical mutating CAS runner.
Set-StrictMode -Version Latest
function Get-A002-PureReplyDecision {
  [CmdletBinding()]
  param(
    [AllowEmptyString()][string]$DecodedBody,
    [int]$HttpStatus,
    [string]$Actor,
    [string]$ExpectedMutationId,
    [string]$ExpectedOid,
    [string]$ObservedOid
  )
  # Conservative. Real provider error-code taxonomy unverified; unknown is never PASS.
  if($HttpStatus -ne 200 -or $Actor -cnotin @('ALPHA','BETA') -or [string]::IsNullOrWhiteSpace($ExpectedMutationId)){
    return 'UNKNOWN_RESPONSE'
  }
  $doc=$null
  try { $doc=ConvertFrom-Json -InputObject $DecodedBody -AsHashtable -Depth 24 -ErrorAction Stop }
  catch { return 'UNKNOWN_RESPONSE' }
  if($null -eq $doc -or $doc -isnot [System.Collections.IDictionary]){return 'UNKNOWN_RESPONSE'}
  $errors=@()
  if($doc.Contains('errors')){
    if($doc.errors -isnot [System.Array]){return 'UNKNOWN_RESPONSE'}
    foreach($item in $doc.errors){
      if($null -eq $item -or $item -isnot [System.Collections.IDictionary] -or
         -not $item.Contains('message') -or $item.message -isnot [string] -or
         [string]::IsNullOrWhiteSpace([string]$item.message)){
        return 'UNKNOWN_RESPONSE'
      }
      $code=''
      if($item.Contains('extensions')){
        if($null -eq $item.extensions -or $item.extensions -isnot [System.Collections.IDictionary]){return 'UNKNOWN_RESPONSE'}
        if($item.extensions.Contains('code')){
          if($item.extensions.code -isnot [string]){return 'UNKNOWN_RESPONSE'}
          $code=[string]$item.extensions.code
        }
      }
      $errors+=@{code=$code;message=[string]$item.message}
    }
  }
  if($doc.Contains('data') -and $null -ne $doc.data){
    if($doc.data -isnot [System.Collections.IDictionary] -or
       -not $doc.data.Contains('updateRefs') -or
       $doc.data.updateRefs -isnot [System.Collections.IDictionary] -or
       -not $doc.data.updateRefs.Contains('clientMutationId') -or
       $doc.data.updateRefs.clientMutationId -isnot [string] -or
       [string]$doc.data.updateRefs.clientMutationId -cne $ExpectedMutationId){
      return 'UNKNOWN_RESPONSE'
    }
    if($errors.Count -ne 0){return 'UNKNOWN_RESPONSE'}
    return 'SERVER_ACCEPTED'
  }
  if($errors.Count -eq 0){return 'UNKNOWN_RESPONSE'}
  if($Actor -ceq 'ALPHA'){return 'PROVIDER_REJECTED_ALPHA'}
  if($errors.Count -ne 1){return 'BETA_REJECTED_UNTYPED'}
  if($ExpectedOid -cnotmatch '^[a-f0-9]{40}$' -or
     $ObservedOid -cnotmatch '^[a-f0-9]{40}$' -or
     $ExpectedOid -ceq $ObservedOid){return 'BETA_REJECTED_UNTYPED'}
  $errorCode=[string]$errors[0].code
  $message=[string]$errors[0].message
  if($errorCode -cnotmatch '^(STALE_BEFORE_OID|EXPECTED_OID_MISMATCH)$'){return 'BETA_REJECTED_UNTYPED'}
  if(-not $message.Contains($ExpectedOid) -or -not $message.Contains($ObservedOid)){return 'BETA_REJECTED_UNTYPED'}
  if($message -cnotmatch '(?i)(stale|out.of.date|mismatch|does not match|different from current)'){return 'BETA_REJECTED_UNTYPED'}
  if($message -cnotmatch '(?i)(beforeOid|expected (oid|sha|object))'){return 'BETA_REJECTED_UNTYPED'}
  return 'BETA_EXPLICIT_BEFOREOID_REJECTION'
}
function Test-A002-PureTerminalGate {
  [CmdletBinding()]
  param(
    [string]$AlphaResult,
    [string]$HeadAfterAlpha,
    [string]$BetaResult,
    [string]$FinalHead,
    [string]$ExpectedAlpha
  )
  # Only the exact explicit rejection following confirmed Alpha may qualify.
  if($ExpectedAlpha -cnotmatch '^[a-f0-9]{40}$'){return $false}
  return [bool](
    $AlphaResult -ceq 'SERVER_ACCEPTED' -and
    $HeadAfterAlpha -ceq $ExpectedAlpha -and
    $BetaResult -ceq 'BETA_EXPLICIT_BEFOREOID_REJECTION' -and
    $FinalHead -ceq $ExpectedAlpha
  )
}
