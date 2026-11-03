# 047B A002 V2: isolated GitHub GraphQL CAS. HARMLESS REF ONLY.
# This runner is not an effect launcher for Dolt, SQL, Beads or Product.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$operation='TS-BEADS-047B-A002-ATOMIC-GRAPHQL-CAS-V2-20261102-001'
$g0='566258f2307360137de765e8116c9174912d3c51'
$alpha='618db9768d65dd0022a4c428e1a263b269e22a41'
$beta='1c209310fc4a0e6b80f1f536a963556f46181c54'
$repo='mauedgar/ts-execution-lab'
$ref='refs/heads/experiment/ts-beads-047b-a002-atomic-cas-v2-target-20261102-001'
$api='https://api.github.com'
$script:ReceiptPath=$null
if($env:GITHUB_ACTIONS -cne 'true' -or [string]::IsNullOrWhiteSpace($env:RUNNER_TEMP)){throw 'A002_HOSTED_ACTIONS_ONLY'}
if([string]::IsNullOrWhiteSpace($env:GH_TOKEN)){throw 'A002_GITHUB_EPHEMERAL_TOKEN_MISSING'}
if($env:GITHUB_RUN_ATTEMPT -cne '1'){throw 'A002_NO_RERUN_ALLOWED'}
if($env:GITHUB_REF -cne 'refs/heads/experiment/ts-beads-047b-a002-atomic-cas-v2-control-20261102-001'){throw 'A002_WRONG_CONTROL_REF'}
$script:ReceiptPath=Join-Path $env:RUNNER_TEMP 'TS047B_A002_V2_ORIGINAL_PROVIDER_JOURNAL.jsonl'
if([IO.File]::Exists($script:ReceiptPath)){throw 'A002_RECEIPT_ALREADY_PRESENT'}
$script:Header=@{Authorization=('Bearer '+$env:GH_TOKEN);Accept='application/vnd.github+json';'X-GitHub-Api-Version'='2022-11-28'}
function Append-Event([string]$Name,[hashtable]$Fields) {
  $obj=[ordered]@{event=$Name;utc=[datetimeoffset]::UtcNow.ToString('o');operation=$operation;attempt='ATTEMPT-001';ref=$ref}
  foreach($k in $Fields.Keys){$obj[$k]=$Fields[$k]}
  $bytes=[Text.UTF8Encoding]::new($false).GetBytes((($obj|ConvertTo-Json -Compress -Depth 15)+"`n"))
  $f=[IO.FileStream]::new($script:ReceiptPath,[IO.FileMode]::Append,[IO.FileAccess]::Write,[IO.FileShare]::Read)
  try{$f.Write($bytes,0,$bytes.Length);$f.Flush($true)}finally{$f.Dispose()}
}
function Read-Provider([string]$Url) {
  return Invoke-RestMethod -Method Get -Uri $Url -Headers $script:Header -TimeoutSec 20
}
function Read-Head {
  $h=Read-Provider ($api+'/repos/'+$repo+'/git/ref/heads/'+$ref.Substring('refs/heads/'.Length))
  if($h.ref -cne $ref -or $h.object.type -cne 'commit'){throw 'A002_REF_IDENTITY_INVALID'}
  return [string]$h.object.sha
}
function Call-AtomicGraphql([string]$Actor,[string]$After,[string]$RepositoryNodeId) {
  $mutation='mutation($input: UpdateRefsInput!) { updateRefs(input: $input) { clientMutationId } }'
  $inputData=@{query=$mutation;variables=@{input=@{
    repositoryId=$RepositoryNodeId
    refUpdates=@(@{name=$ref;beforeOid=$g0;afterOid=$After;force=$false})
    clientMutationId=($operation+'-ATTEMPT-001-'+$Actor)
  }}}
  $body=$inputData|ConvertTo-Json -Depth 16 -Compress
  # Durably record intent before first network byte. No automatic retry.
  Append-Event 'GRAPHQL_MUTATION_INTENT' @{actor=$Actor;afterOid=$After;beforeOid=$g0;force=$false;operationName='updateRefs'}
  $response=$null
  try{
    $response=Invoke-WebRequest -Method Post -Uri ($api+'/graphql') -Headers $script:Header -ContentType 'application/json' -Body $body -TimeoutSec 30 -SkipHttpErrorCheck
  }catch{
    Append-Event 'GRAPHQL_TRANSPORT_UNKNOWN' @{actor=$Actor;exceptionClass=$_.Exception.GetType().FullName}
    return 'UNKNOWN_TRANSPORT'
  }
  $http=[int]$response.StatusCode
  $requestId=''
  try {$requestId=[string]$response.Headers['x-github-request-id']}catch {}
  $bodyHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes([string]$response.Content)))
  Append-Event 'GRAPHQL_HTTP_RESPONSE_METADATA' @{actor=$Actor;httpStatus=$http;requestId=$requestId;bodySha256=$bodyHash}
  $parsed=$null
  try{$parsed=[string]$response.Content|ConvertFrom-Json -AsHashtable -Depth 24}catch{
    Append-Event 'GRAPHQL_RESPONSE_UNKNOWN' @{actor=$Actor;httpStatus=$http;reason='UNPARSEABLE_JSON'}
    return 'UNKNOWN_RESPONSE'
  }
  $errors=@()
  if($parsed.ContainsKey('errors') -and $null -ne $parsed.errors){
    foreach($errorItem in @($parsed.errors)){
      $msg=[string]$errorItem.message
      if($msg.Length -gt 400){$msg=$msg.Substring(0,400)}
      $code=''
      if($errorItem.ContainsKey('extensions') -and $null -ne $errorItem.extensions -and $errorItem.extensions.ContainsKey('code')){$code=[string]$errorItem.extensions.code}
      $errors+=@{code=$code;message=$msg}
    }
  }
  # Store observed server response BEFORE interpreting success/failure.
  $accepted=($http -ge 200 -and $http -lt 300 -and $errors.Count -eq 0 -and $null -ne $parsed.data -and $null -ne $parsed.data.updateRefs)
  Append-Event 'GRAPHQL_PROVIDER_RESPONSE' @{actor=$Actor;httpStatus=$http;errors=$errors;accepted=$accepted;providerBodyParsed=$true}
  if($accepted){return 'SERVER_ACCEPTED'}
  if($errors.Count -eq 0){return 'UNKNOWN_RESPONSE'}
  if($Actor -cne 'BETA'){return 'PROVIDER_REJECTED_ALPHA'}
  # Strict classification: never infer CAS on generic words like "update" or "reference".
  $typed=$false
  foreach($e in $errors){
    if($e.code -cmatch '^(STALE_BEFORE_OID|EXPECTED_OID_MISMATCH|REF_UPDATE_CONFLICT)$'){$typed=$true}
    if($e.message -cmatch '(?i)(beforeOid|expected (object|oid|sha)|does not match (the )?(current|expected) (oid|sha))'){$typed=$true}
  }
  if($typed){return 'BETA_EXPLICIT_BEFOREOID_REJECTION'}
  return 'BETA_REJECTED_UNTYPED'
}
$disposition='UNRESOLVED'
try{
  Append-Event 'ATTEMPT_OPEN' @{g0=$g0;alpha=$alpha;beta=$beta;sql=$false;beads=$false;product=$false}
  $metadata=Read-Provider ($api+'/repos/'+$repo)
  if($metadata.full_name -cne $repo -or [string]::IsNullOrWhiteSpace([string]$metadata.node_id)){throw 'A002_REPOSITORY_IDENTITY'}
  foreach($sha in @($alpha,$beta)){
    $commit=Read-Provider ($api+'/repos/'+$repo+'/git/commits/'+$sha)
    if($commit.sha -cne $sha -or @($commit.parents).Count -ne 1){throw 'A002_COMMIT_IDENTITY_INVALID'}
    $expectedParent=$(if($sha -ceq $alpha){$g0}else{$alpha})
    if($commit.parents[0].sha -cne $expectedParent){throw 'A002_FF_ANCESTRY_MISMATCH'}
  }
  $initial=Read-Head
  Append-Event 'PRECONDITIONS_OBSERVED' @{head=$initial;g0=$g0;alphaParent=$g0;betaParent=$alpha}
  if($initial -cne $g0){throw 'A002_REF_ALREADY_MOVED_NO_DISPATCH'}
  $a=Call-AtomicGraphql 'ALPHA' $alpha ([string]$metadata.node_id)
  $headA=Read-Head
  Append-Event 'ALPHA_POST_OBSERVATION' @{result=$a;head=$headA}
  if($a -cne 'SERVER_ACCEPTED' -or $headA -cne $alpha){throw 'A002_ALPHA_UNCONFIRMED_STOP_NO_BETA'}
  # BETA is a legal FAST-FORWARD from ALPHA, yet uses STALE beforeOid=G0.
  # Any server refusal can therefore be contrasted with an ancestor-safe commit.
  $b=Call-AtomicGraphql 'BETA' $beta ([string]$metadata.node_id)
  $final=Read-Head
  Append-Event 'BETA_POST_OBSERVATION' @{result=$b;head=$final;expectedAlpha=$alpha}
  if($final -cne $alpha){throw 'A002_UNEXPECTED_FINAL_HEAD_NO_RETRY'}
  if($b -cne 'BETA_EXPLICIT_BEFOREOID_REJECTION'){throw ('A002_NOT_QUALIFIED_'+$b)}
  $disposition='PASS_ATOMIC_GRAPHQL_BEFOREOID_CONFLICT_EXPLICIT'
  Append-Event 'TERMINAL_PASS' @{disposition=$disposition;finalHead=$final;noRetry=$true}
  Write-Output $disposition
}catch{
  $reason=$_.Exception.Message
  try{Append-Event 'TERMINAL_BLOCKED_OR_UNKNOWN' @{reason=$reason;disposition='NO_RETRY_OR_INFERRED_PASS'}}catch{}
  throw
}finally{
  Remove-Variable -Name Header -Scope Script -ErrorAction SilentlyContinue
}
