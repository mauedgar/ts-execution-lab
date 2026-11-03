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
  @{name='HTTP401_with_match';http=401;errors=@(@{code='EXPECTED_OID_MISMATCH';message=$canonical});want=$reject}
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
  @{name='null_error';http=200;errors=@($null);want=$reject}
  @{name='malformed_error_object';http=200;errors=@([pscustomobject]@{code='EXPECTED_OID_MISMATCH';message=$canonical});want=$reject}
  @{name='missing_message';http=200;errors=@(@{code='EXPECTED_OID_MISMATCH'});want=$reject}
  @{name='mixed_success_data_and_error';http=200;errors=@(@{code='EXPECTED_OID_MISMATCH';message=$canonical});hasSuccessData=$true;want=$reject}
  @{name='no_oid_context';http=200;errors=@(@{code='STALE_BEFORE_OID';message='stale beforeOid'});want=$reject}
)
$tested=0
foreach($test in $cases){
  $dataFlag=($test.ContainsKey('hasSuccessData') -and $test.hasSuccessData)
  $actual=Classify-BetaCasError -HttpStatus $test.http -Errors $test.errors -ExpectedOid $expected -ObservedOid $current -HasSuccessData ([bool]$dataFlag)
  if($actual -cne $test.want){throw ('CAS_CLASSIFIER_FAIL_'+$test.name+'_GOT_'+$actual)}
  $tested++
}
# Safely extract only the pure body-evidence helper; do not dot-source the full runner.
$bodyFn=@($tree.FindAll({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -ceq 'Get-A002-BodyEvidence'},$true))
if($bodyFn.Count -ne 1){throw 'V2_BODY_HELPER_NOT_UNIQUE'}
. ([scriptblock]::Create($bodyFn[0].Extent.Text))
$ordinary='{"errors":[{"message":"expected OID mismatch"}]}'
$bodyEvidence=Get-A002-BodyEvidence -DecodedContent $ordinary
if(-not $bodyEvidence.safe -or $bodyEvidence.captureKind -cne 'DECODED_CONTENT_REENCODED_UTF8_NOT_WIRE'){throw 'F03_BODY_NOT_SAFE_OR_MISLABELED'}
$back=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($bodyEvidence.utf8Base64))
if($back -cne $ordinary -or $bodyEvidence.byteCount -ne [Text.Encoding]::UTF8.GetByteCount($ordinary)){throw 'F03_BODY_ROUNDTRIP_FAILED'}
if($bodyEvidence.sha256 -cne [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($ordinary)))){throw 'F03_BODY_HASH_MISMATCH'}
foreach($unsafe in @('{"token":"test-secret"}','{"authorization":"Bearer abcdefg"}','Bearer secret-token','ghp_12345678901234567890',('x' * 65537))){
  $negative=Get-A002-BodyEvidence -DecodedContent $unsafe
  if($negative.safe -or $negative.utf8Base64 -cne ''){throw 'F03_SENSITIVE_OR_OVERSIZE_FAILED'}
}
# Verify source-only static invariants; never call GraphQL, journal writer or effect runner.
$full=[IO.File]::ReadAllText($source)
if(-not $full.Contains("GRAPHQL_PROVIDER_CONTENT_UTF8_REENCODED")){throw 'F03_CONTENT_LABEL_MISSING'}
if(-not $full.Contains("contentUtf8Base64")){throw 'F03_BODY_BYTES_MISSING'}
if($full.Contains('$msg=$msg.Substring(0,400)')){throw 'A02_MESSAGE_TRUNCATION_REMAINS'}
if(-not $full.Contains('-HasSuccessData $hasSuccessPayload')){throw 'MIXED_RESPONSE_CLASSIFICATION_GUARD_MISSING'}
if(-not $full.Contains("A002_NO_RERUN_ALLOWED")){throw 'SINGLE_ATTEMPT_GUARD_MISSING'}
if(-not $full.Contains('beforeOid=$g0')){throw 'GENERATION_MATCH_GUARD_MISSING'}
[pscustomobject]@{result='PASS_V2_IR021_SOURCE_ONLY_GUARDS';negativeCases=($tested-2);positiveSyntheticCases=2;bodyEvidencePureNegativeCases=5;graphqlMutationExecuted=$false;sqlExecuted=$false;beadsMutated=$false;offHostReceiptProven=$false}
