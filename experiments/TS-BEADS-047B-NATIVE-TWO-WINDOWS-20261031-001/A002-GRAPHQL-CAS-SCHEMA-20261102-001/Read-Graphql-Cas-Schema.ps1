# TS-BEADS 047B A002: AUTHENTICATED READ-ONLY GitHub schema introspection.
# This file has NO GitHub mutation, no SQL, no Beads, no Product, no retries.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if(-not $env:GITHUB_ACTIONS -or -not $env:RUNNER_TEMP){throw 'HOSTED_ACTIONS_ONLY'}
if([string]::IsNullOrWhiteSpace($env:GH_TOKEN)){throw 'READ_ONLY_TOKEN_MISSING'}
if(-not (Get-Command gh -ErrorAction SilentlyContinue)){throw 'GITHUB_CLI_MISSING'}
$query='query A002CasSchemaReadOnly { __schema { mutationType { fields { name } } } refUpdateType: __type(name: "RefUpdate") { inputFields { name } } singleRefInput: __type(name: "UpdateRefInput") { inputFields { name } } }'
# gh api graphql with a QUERY operation and ephemeral GitHub Actions read-only token.
# No query values or response headers are output to logs.
$json=& gh api graphql --raw-field "query=$query" 2>$null
if($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace(($json -join ''))){throw 'GRAPHQL_READONLY_QUERY_FAILED'}
$data=($json -join "`n") | ConvertFrom-Json -AsHashtable -Depth 20
if($data.ContainsKey('errors') -or -not $data.ContainsKey('data')){throw 'GRAPHQL_RESPONSE_NOT_VALIDATED'}
$root=$data['data']
if($null -eq $root['__schema'] -or $null -eq $root['refUpdateType'] -or $null -eq $root['singleRefInput']){throw 'GRAPHQL_SCHEMA_MISSING'}
$mutations=@($root['__schema']['mutationType']['fields'] | ForEach-Object { $_['name'] })
$refUpdateFields=@($root['refUpdateType']['inputFields'] | ForEach-Object { $_['name'] })
$oneInputFields=@($root['singleRefInput']['inputFields'] | ForEach-Object { $_['name'] })
$hasAtomicMutation=('updateRefs' -in $mutations)
$hasBefore=('beforeOid' -in $refUpdateFields)
$hasAfter=('afterOid' -in $refUpdateFields)
$singleBefore=('beforeOid' -in $oneInputFields)
if(-not $hasAtomicMutation -or -not $hasBefore -or -not $hasAfter){throw 'REQUIRED_ATOMIC_PROVIDER_PRIMITIVE_ABSENT'}
if($singleBefore){throw 'EXPECTED_SINGLE_UPDATE_REF_INPUT_DISTINCTION_FAILED'}
[pscustomobject]@{
 result='PASS_A002_GRAPHQL_SCHEMA_READ_ONLY'
 hasUpdateRefs=$hasAtomicMutation
 refUpdateHasBeforeOid=$hasBefore
 refUpdateHasAfterOid=$hasAfter
 updateRefInputHasBeforeOid=$singleBefore
 mutationExecuted=$false
 refMoved=$false
 sqlExecuted=$false
 beadsMutated=$false
 sourceOnly=$true
 providerContractBinding='SCHEMA_ONLY_NOT_CONNECTOR_IMPLEMENTATION_NOT_FENCING'
} | ConvertTo-Json -Compress
