# TS-BEADS 047B A002 — one bounded, isolated GitHub GraphQL atomic-ref proof.
# ONLY the disjoint experimental Git ref. No SQL, Dolt, Beads, Product, Commander or retry.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$repo='mauedgar/ts-execution-lab'
$ref='refs/heads/experiment/ts-beads-047b-a002-atomic-cas-target-20261102-001'
$g0='566258f2307360137de765e8116c9174912d3c51'
$alpha='4f6486b45bfec63a30653b1e5cbc556a82fa9217'
$beta='99bab25a46d13fba92ceb80b2df9c01cddd80e2a'
$attempt='TS-BEADS-047B-A002-ATOMIC-GRAPHQL-CAS-20261102-001-ATTEMPT-001'
if($env:GITHUB_ACTIONS -cne 'true' -or [string]::IsNullOrWhiteSpace($env:RUNNER_TEMP)){throw 'HOSTED_RUNNER_REQUIRED'}
if([string]::IsNullOrWhiteSpace($env:GH_TOKEN)){throw 'EPHEMERAL_TOKEN_REQUIRED'}
$headers=@{Authorization=('Bearer '+$env:GH_TOKEN);Accept='application/vnd.github+json';'X-GitHub-Api-Version'='2022-11-28'}
$root='https://api.github.com'
$proof=[ordered]@{schema='TS047B_A002_GRAPHQL_CAS_V1';attempt=$attempt;repository=$repo;ref=$ref;g0=$g0;alpha=$alpha;beta=$beta;kind='INNOCUOUS_GIT_REF';subject='FROZEN';alphaResult='NOT_DISPATCHED';betaResult='NOT_DISPATCHED';finalHead=$null;sqlExecuted=$false;beadsMutated=$false;productEffect=$false;complete=$false}
$receipt=Join-Path $env:RUNNER_TEMP 'TS047B_A002_GRAPHQL_CAS_ORIGINAL_RECEIPT.json'
function Save-Receipt {
  $value=($proof|ConvertTo-Json -Depth 9)
  [IO.File]::WriteAllText($receipt,$value+"`n",[Text.UTF8Encoding]::new($false))
}
function Read-GitHub([string]$uri) {
  return Invoke-RestMethod -Method Get -Uri $uri -Headers $headers -TimeoutSec 20
}
function Read-Head {
  $path='heads/'+$ref.Substring('refs/heads/'.Length)
  $got=Read-GitHub ($root+'/repos/'+$repo+'/git/ref/'+$path)
  if($got.ref -cne $ref -or $got.object.type -cne 'commit'){throw 'TARGET_REF_IDENTITY_MISMATCH'}
  return [string]$got.object.sha
}
function One-Mutation([string]$actor,[string]$afterOid,[string]$repoNodeId) {
  # The actual documented mutation: server-side RefUpdate.beforeOid condition.
  $query='mutation($input: UpdateRefsInput!) { updateRefs(input: $input) { clientMutationId } }'
  $inputObject=[ordered]@{
    repositoryId=$repoNodeId
    refUpdates=@(@{name=$ref;beforeOid=$g0;afterOid=$afterOid;force=$false})
    clientMutationId=($attempt+'-'+$actor)
  }
  $request=(@{query=$query;variables=@{input=$inputObject}}|ConvertTo-Json -Compress -Depth 12)
  $response=$null
  try {
    $response=Invoke-WebRequest -Uri 'https://api.github.com/graphql' -Method Post -Headers $headers -ContentType 'application/json' -Body $request -TimeoutSec 25 -SkipHttpErrorCheck
  } catch {
    return [pscustomobject]@{status='UNKNOWN_TRANSPORT';httpStatus=$null;errors=@($_.Exception.GetType().Name);mutation=$actor}
  }
  $parsed=$null
  try{$parsed=($response.Content|ConvertFrom-Json -AsHashtable -Depth 20)}catch{
    return [pscustomobject]@{status='UNKNOWN_BODY';httpStatus=[int]$response.StatusCode;errors=@();mutation=$actor}
  }
  $messages=@()
  if($parsed.ContainsKey('errors') -and $null -ne $parsed.errors) {
    foreach($e in @($parsed.errors)) {
      $msg=[string]$e.message
      if($msg.Length -gt 320){$msg=$msg.Substring(0,320)}
      $messages+=@{type=[string]$e.type;message=$msg}
    }
  }
  $ok=([int]$response.StatusCode -ge 200 -and [int]$response.StatusCode -lt 300 -and
    $messages.Count -eq 0 -and $null -ne $parsed.data -and $null -ne $parsed.data.updateRefs)
  return [pscustomobject]@{
    status=$(if($ok){'SERVER_ACCEPTED'}elseif($messages.Count -gt 0){'PROVIDER_ERRORS'}else{'UNKNOWN_REPLY'})
    httpStatus=[int]$response.StatusCode;errors=$messages;mutation=$actor
  }
}
Save-Receipt
# Freeze and independently reobserve every effect precondition.
$repoMeta=Read-GitHub ($root+'/repos/'+$repo)
if($repoMeta.full_name -cne $repo -or [string]::IsNullOrWhiteSpace($repoMeta.node_id)){throw 'WRONG_REPO_NODE_ID'}
foreach($subject in @($alpha,$beta)){
  $c=Read-GitHub ($root+'/repos/'+$repo+'/git/commits/'+$subject)
  if($c.sha -cne $subject -or @($c.parents).Count -ne 1 -or $c.parents[0].sha -cne $g0){throw 'PREPARED_CLAIM_NOT_IMMUTABLE_G0_CHILD'}
}
$observed=Read-Head
if($observed -cne $g0){throw ('CAS_PRECONDITION_REF_MOVED_'+$observed)}
$proof['initialHead']=$observed
$proof['preflight']='PASS_EXACT_DISJOINT_REF'
Save-Receipt
# One original ALPHA GraphQL CAS. No duplicate dispatch on timeout/UNKNOWN.
$first=One-Mutation 'ALPHA' $alpha ([string]$repoMeta.node_id)
$proof['alphaResult']=$first.status;$proof['alphaResponse']=$first
Save-Receipt
$afterA=Read-Head
$proof['headAfterAlpha']=$afterA
Save-Receipt
if($first.status -cne 'SERVER_ACCEPTED' -or $afterA -cne $alpha){
  $proof['disposition']='STOP_ALPHA_NOT_CONFIRMED_NO_BETA'
  Save-Receipt
  throw 'ALPHA_NOT_CONFIRMED_OR_UNKNOWN_NO_BETA'
}
# Postcondition for a successful alpha is confirmed. One stale BETA call.
$second=One-Mutation 'BETA' $beta ([string]$repoMeta.node_id)
$proof['betaResult']=$second.status;$proof['betaResponse']=$second
Save-Receipt
$final=Read-Head
$proof['finalHead']=$final
Save-Receipt
if($final -cne $alpha){$proof['disposition']='BLOCKED_UNEXPECTED_REF_HEAD_NO_RETRY';Save-Receipt;throw 'UNEXPECTED_BRANCH_HEAD'}
if($second.status -ceq 'SERVER_ACCEPTED'){$proof['disposition']='FAIL_STALE_BETA_ACCEPTED';Save-Receipt;throw 'CAS_STALE_BETA_ACCEPTED'}
if($second.status -cne 'PROVIDER_ERRORS'){$proof['disposition']='BETA_PROVIDER_UNKNOWN_REF_ALPHA';Save-Receipt;throw 'BETA_PROVIDER_UNKNOWN_NO_RETRY'}
$evidence=@($second.errors|ForEach-Object {[string]$_.message}) -join ' | '
if($evidence -notmatch '(?i)before|expected|current|referenc|oid|update|out.of.date|has.changed') {
  $proof['disposition']='BETA_UNTYPED_PROVIDER_ERROR_REF_ALPHA'
  Save-Receipt
  throw 'BETA_UNTYPED_REJECTION_NO_RETRY'
}
$proof['disposition']='PASS_PROVIDER_GRAPHQL_STALE_CONDITION_REJECTED_REF_ALPHA'
$proof['complete']=$true
Save-Receipt
[pscustomobject]@{attempt=$attempt;result=$proof['disposition'];alphaResponse=$first.status;betaResponse=$second.status;finalHead=$final;sqlExecuted=$false;beadsMutated=$false;productEffect=$false} | ConvertTo-Json -Compress
