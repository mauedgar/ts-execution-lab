# Static source-extracted classifier regression ONLY; never invokes the effect runner.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$source=Join-Path $PSScriptRoot 'Invoke-A002-AtomicCas-V2.ps1'
$tokens=$null; $parseErrors=$null
$tree=[Management.Automation.Language.Parser]::ParseFile($source,[ref]$tokens,[ref]$parseErrors)
if(@($parseErrors).Count -ne 0){throw 'V2_RUNNER_PARSER_FAIL'}
$fn=@($tree.FindAll({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -ceq 'Classify-BetaCasError'},$true))
if($fn.Count -ne 1){throw 'V2_CLASSIFIER_FUNCTION_NOT_UNIQUE'}
. ([scriptblock]::Create($fn[0].Extent.Text))
$expected='566258f2307360137de765e8116c9174912d3c51'
$current='618db9768d65dd0022a4c428e1a263b269e22a41'
$pass='BETA_EXPLICIT_BEFOREOID_REJECTION'
$reject='BETA_REJECTED_UNTYPED'
$canonical='beforeOid expected '+$expected+' does not match current '+$current
$cases=@(
  @{name='synthetic_exact_oid_conflict';http=200;errors=@(@{code='EXPECTED_OID_MISMATCH';message=$canonical});want=$pass}
  @{name='explicit_stale_code';http=200;errors=@(@{code='STALE_BEFORE_OID';message=$canonical});want=$pass}
  @{name='HTTP403_with_match';http=403;errors=@(@{code='EXPECTED_OID_MISMATCH';message=$canonical});want=$reject}
  @{name='HTTP422_with_match';http=422;errors=@(@{code='EXPECTED_OID_MISMATCH';message=$canonical});want=$reject}
  @{name='HTTP500_with_match';http=500;errors=@(@{code='EXPECTED_OID_MISMATCH';message=$canonical});want=$reject}
  @{name='mixed_conflict_auth';http=200;errors=@(@{code='EXPECTED_OID_MISMATCH';message=$canonical},@{code='FORBIDDEN';message='Access denied'});want=$reject}
  @{name='generic_conflict';http=200;errors=@(@{code='REF_UPDATE_CONFLICT';message=$canonical});want=$reject}
  @{name='schema_invalid_before_oid';http=200;errors=@(@{code='EXPECTED_OID_MISMATCH';message='beforeOid is invalid'});want=$reject}
  @{name='schema_ambiguous';http=200;errors=@(@{code='BAD_USER_INPUT';message=$canonical});want=$reject}
  @{name='expected_only';http=200;errors=@(@{code='EXPECTED_OID_MISMATCH';message='beforeOid expected '+$expected+' is stale'});want=$reject}
  @{name='current_only';http=200;errors=@(@{code='EXPECTED_OID_MISMATCH';message='beforeOid does not match current '+$current});want=$reject}
  @{name='no_mismatch_words';http=200;errors=@(@{code='EXPECTED_OID_MISMATCH';message='beforeOid expected '+$expected+' current '+$current});want=$reject}
  @{name='untyped_permission';http=200;errors=@(@{code='FORBIDDEN';message='beforeOid expected '+$expected+' does not match current '+$current});want=$reject}
  @{name='no_errors';http=200;errors=@();want=$reject}
)
$tested=0
foreach($test in $cases){
  $actual=Classify-BetaCasError -HttpStatus $test.http -Errors $test.errors -ExpectedOid $expected -ObservedOid $current
  if($actual -cne $test.want){throw ('CAS_CLASSIFIER_FAIL_'+$test.name+'_GOT_'+$actual)}
  $tested++
}
# Verify source-only static invariants, never call GraphQL.
$full=[IO.File]::ReadAllText($source)
if(-not $full.Contains("GRAPHQL_PROVIDER_BODY_ORIGINAL")){throw 'F03_RAW_BODY_MARKER_MISSING'}
if(-not $full.Contains("bodyUtf8Base64")){throw 'F03_BODY_BYTES_MISSING'}
if(-not $full.Contains("A002_NO_RERUN_ALLOWED")){throw 'SINGLE_ATTEMPT_GUARD_MISSING'}
if(-not $full.Contains('beforeOid=$g0')){throw 'GENERATION_MATCH_GUARD_MISSING'}
[pscustomobject]@{result='PASS_V2_STRICT_CLASSIFIER_SOURCE_ONLY';negativeCases=($tested-2);positiveSyntheticCases=2;graphqlMutationExecuted=$false;sqlExecuted=$false;beadsMutated=$false;offHostReceiptProven=$false}
