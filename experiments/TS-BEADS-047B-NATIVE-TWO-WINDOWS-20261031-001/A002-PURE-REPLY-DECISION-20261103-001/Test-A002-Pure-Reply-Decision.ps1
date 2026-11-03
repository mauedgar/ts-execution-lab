# Source-only synthetic tests: no network, no Git mutation, no effects.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$library=Join-Path $PSScriptRoot 'A002-Pure-Reply-Decision.ps1'
$tokens=$null; $parseErrors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($library,[ref]$tokens,[ref]$parseErrors)
if(@($parseErrors).Count -ne 0){throw 'PURE_LIBRARY_PARSER_ERROR'}
$definitions=@($ast.FindAll({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst]},$true))
if($definitions.Count -ne 2){throw 'PURE_LIBRARY_UNEXPECTED_FUNCTION_COUNT'}
if(@($definitions|Where-Object{$_.Name -cnotin @('Get-A002-PureReplyDecision','Test-A002-PureTerminalGate')}).Count -gt 0){throw 'PURE_LIBRARY_UNEXPECTED_FUNCTION'}
# This is the standalone NO-EFFECT library; it defines only pure functions and strict mode.
. $library
$g0='566258f2307360137de765e8116c9174912d3c51'
$alpha='618db9768d65dd0022a4c428e1a263b269e22a41'
$cid='TS-BEADS-047B-A002-ATOMIC-GRAPHQL-CAS-V2-20261102-001-ATTEMPT-001-ALPHA'
$betaCid='TS-BEADS-047B-A002-ATOMIC-GRAPHQL-CAS-V2-20261102-001-ATTEMPT-001-BETA'
$canonical='beforeOid expected '+$g0+' does not match current '+$alpha
$good='{"data":{"updateRefs":{"clientMutationId":"'+$cid+'"}}}'
$betaGood='{"data":{"updateRefs":{"clientMutationId":"'+$betaCid+'"}}}'
$err='{"errors":[{"message":"'+$canonical+'","extensions":{"code":"EXPECTED_OID_MISMATCH"}}]}'
$stale='{"errors":[{"message":"'+$canonical+'","extensions":{"code":"STALE_BEFORE_OID"}}]}'
$generic='{"errors":[{"message":"'+$canonical+'","extensions":{"code":"REF_UPDATE_CONFLICT"}}]}'
$mixed='{"data":{"updateRefs":{"clientMutationId":"'+$betaCid+'"}},"errors":[{"message":"'+$canonical+'","extensions":{"code":"EXPECTED_OID_MISMATCH"}}]}'
$cases=@(
  @{name='valid_alpha_receipt';body=$good;http=200;actor='ALPHA';id=$cid;want='SERVER_ACCEPTED'}
  @{name='valid_beta_receipt';body=$betaGood;http=200;actor='BETA';id=$betaCid;want='SERVER_ACCEPTED'}
  @{name='explicit_beta_error';body=$err;http=200;actor='BETA';id=$betaCid;want='BETA_EXPLICIT_BEFOREOID_REJECTION'}
  @{name='explicit_stale_code';body=$stale;http=200;actor='BETA';id=$betaCid;want='BETA_EXPLICIT_BEFOREOID_REJECTION'}
  @{name='alpha_error';body=$err;http=200;actor='ALPHA';id=$cid;want='PROVIDER_REJECTED_ALPHA'}
  @{name='generic_beta';body=$generic;http=200;actor='BETA';id=$betaCid;want='BETA_REJECTED_UNTYPED'}
  @{name='http401';body=$err;http=401;actor='BETA';id=$betaCid;want='UNKNOWN_RESPONSE'}
  @{name='http403';body=$err;http=403;actor='BETA';id=$betaCid;want='UNKNOWN_RESPONSE'}
  @{name='http500';body=$good;http=500;actor='ALPHA';id=$cid;want='UNKNOWN_RESPONSE'}
  @{name='mixed_data_errors';body=$mixed;http=200;actor='BETA';id=$betaCid;want='UNKNOWN_RESPONSE'}
  @{name='missing_data';body='{}';http=200;actor='ALPHA';id=$cid;want='UNKNOWN_RESPONSE'}
  @{name='missing_updateRefs';body='{"data":{}}';http=200;actor='ALPHA';id=$cid;want='UNKNOWN_RESPONSE'}
  @{name='updateRefs_null';body='{"data":{"updateRefs":null}}';http=200;actor='ALPHA';id=$cid;want='UNKNOWN_RESPONSE'}
  @{name='updateRefs_string';body='{"data":{"updateRefs":"yes"}}';http=200;actor='ALPHA';id=$cid;want='UNKNOWN_RESPONSE'}
  @{name='missing_correlation';body='{"data":{"updateRefs":{}}}';http=200;actor='ALPHA';id=$cid;want='UNKNOWN_RESPONSE'}
  @{name='wrong_correlation';body=$good;http=200;actor='ALPHA';id='incorrect';want='UNKNOWN_RESPONSE'}
  @{name='numeric_correlation';body='{"data":{"updateRefs":{"clientMutationId":7}}}';http=200;actor='ALPHA';id=$cid;want='UNKNOWN_RESPONSE'}
  @{name='null_correlation';body='{"data":{"updateRefs":{"clientMutationId":null}}}';http=200;actor='ALPHA';id=$cid;want='UNKNOWN_RESPONSE'}
  @{name='malformed_json';body='{broken';http=200;actor='BETA';id=$betaCid;want='UNKNOWN_RESPONSE'}
  @{name='root_array';body='[]';http=200;actor='BETA';id=$betaCid;want='UNKNOWN_RESPONSE'}
  @{name='root_null';body='null';http=200;actor='BETA';id=$betaCid;want='UNKNOWN_RESPONSE'}
  @{name='null_errors';body='{"errors":null}';http=200;actor='BETA';id=$betaCid;want='UNKNOWN_RESPONSE'}
  @{name='errors_object';body='{"errors":{"message":"X"}}';http=200;actor='BETA';id=$betaCid;want='UNKNOWN_RESPONSE'}
  @{name='errors_string';body='{"errors":"X"}';http=200;actor='BETA';id=$betaCid;want='UNKNOWN_RESPONSE'}
  @{name='errors_empty';body='{"errors":[]}';http=200;actor='BETA';id=$betaCid;want='UNKNOWN_RESPONSE'}
  @{name='errors_null_item';body='{"errors":[null]}';http=200;actor='BETA';id=$betaCid;want='UNKNOWN_RESPONSE'}
  @{name='errors_numeric_message';body='{"errors":[{"message":42}]}';http=200;actor='BETA';id=$betaCid;want='UNKNOWN_RESPONSE'}
  @{name='errors_missing_message';body='{"errors":[{}]}';http=200;actor='BETA';id=$betaCid;want='UNKNOWN_RESPONSE'}
  @{name='extensions_string';body='{"errors":[{"message":"bad","extensions":"invalid"}]}';http=200;actor='BETA';id=$betaCid;want='UNKNOWN_RESPONSE'}
  @{name='extensions_bad_code';body='{"errors":[{"message":"bad","extensions":{"code":42}}]}';http=200;actor='BETA';id=$betaCid;want='UNKNOWN_RESPONSE'}
  @{name='wrong_actor';body=$good;http=200;actor='OTHER';id=$cid;want='UNKNOWN_RESPONSE'}
  @{name='blank_correlation';body=$good;http=200;actor='ALPHA';id='';want='UNKNOWN_RESPONSE'}
)
$n=0
foreach($case in $cases){
  $actual=Get-A002-PureReplyDecision -DecodedBody $case.body -HttpStatus $case.http -Actor $case.actor -ExpectedMutationId $case.id -ExpectedOid $g0 -ObservedOid $alpha
  if($actual -cne $case.want){throw ('PURE_REPLY_FAIL_'+$case.name+'_GOT_'+$actual)}
  $n++
}
$gateCases=@(
  @{name='only_qualified';a='SERVER_ACCEPTED';headA=$alpha;b='BETA_EXPLICIT_BEFOREOID_REJECTION';final=$alpha;valid=$true}
  @{name='beta_unknown_transport';a='SERVER_ACCEPTED';headA=$alpha;b='UNKNOWN_TRANSPORT';final=$alpha;valid=$false}
  @{name='beta_unknown_response';a='SERVER_ACCEPTED';headA=$alpha;b='UNKNOWN_RESPONSE';final=$alpha;valid=$false}
  @{name='beta_untyped';a='SERVER_ACCEPTED';headA=$alpha;b='BETA_REJECTED_UNTYPED';final=$alpha;valid=$false}
  @{name='beta_accepted';a='SERVER_ACCEPTED';headA=$alpha;b='SERVER_ACCEPTED';final=$alpha;valid=$false}
  @{name='alpha_unknown';a='UNKNOWN_TRANSPORT';headA=$alpha;b='BETA_EXPLICIT_BEFOREOID_REJECTION';final=$alpha;valid=$false}
  @{name='alpha_rejected';a='PROVIDER_REJECTED_ALPHA';headA=$alpha;b='BETA_EXPLICIT_BEFOREOID_REJECTION';final=$alpha;valid=$false}
  @{name='alpha_head_wrong';a='SERVER_ACCEPTED';headA=$g0;b='BETA_EXPLICIT_BEFOREOID_REJECTION';final=$alpha;valid=$false}
  @{name='beta_head_wrong';a='SERVER_ACCEPTED';headA=$alpha;b='BETA_EXPLICIT_BEFOREOID_REJECTION';final=$g0;valid=$false}
)
$m=0
foreach($g in $gateCases){
  $actual=Test-A002-PureTerminalGate -AlphaResult $g.a -HeadAfterAlpha $g.headA -BetaResult $g.b -FinalHead $g.final -ExpectedAlpha $alpha
  if([bool]$actual -ne [bool]$g.valid){throw ('PURE_GATE_FAIL_'+$g.name)}
  $m++
}
if(Test-A002-PureTerminalGate -AlphaResult 'SERVER_ACCEPTED' -HeadAfterAlpha $alpha -BetaResult 'BETA_EXPLICIT_BEFOREOID_REJECTION' -FinalHead $alpha -ExpectedAlpha 'invalid'){throw 'PURE_GATE_BAD_SHA_ACCEPTED'}
[pscustomobject]@{result='PURE_READONLY_SOURCE_TESTS_PASS';replyCases=$n;gateCases=$m;invalidExpectedShaCases=1;providerCalls=0;refWrites=0;sqlWrites=0;beadsWrites=0;productWrites=0;fullCasEffectProven=$false}
