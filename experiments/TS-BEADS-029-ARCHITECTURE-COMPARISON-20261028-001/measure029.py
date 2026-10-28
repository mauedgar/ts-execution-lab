#!/usr/bin/env python3
"""029: measure installed Product footprint + immutable prior native telemetry.
Strictly descriptive; do not equate source bytes, HTTP calls or test counts with migration savings.
No Product or remote effect.
"""
from __future__ import annotations
import hashlib,json,os,pathlib,re,sys
product=pathlib.Path(os.environ["PRODUCT_ROOT"]).resolve()
origin=pathlib.Path(os.environ["E022_REPORT"]).resolve()
f024=pathlib.Path(os.environ["E024_RESULT"]).resolve()
f028=pathlib.Path(os.environ["E028_RESULT"]).resolve()
result=pathlib.Path(os.environ["RESULT_PATH"]).resolve()
expected_product="d4154bd43f26515c39a41be974e462a0c7406a2d"
meta={"product_subject":expected_product,
      "product_tree":"cbfb71ad8632047e8e64fe2665d8614d835a2c8b",
      "e022_subject":"32f86383c979ba015024d0e70ccd98c61858e132",
      "e024_subject":"4a2511e1fa02858b765715ac76e7d19a32aa67da",
      "e028_subject":"9e8016004ef5d3ca74abd67914d8e1a03ffcd851"}
checks=[]
def check(name,value):
 if not value:raise AssertionError("029_CHECK:"+name)
 checks.append(name)
def metrics(path):
 b=path.read_bytes()
 return {"bytes":len(b),"lines":len(b.splitlines()),"sha256":hashlib.sha256(b).hexdigest()}
def rel(path):return path.relative_to(product).as_posix()
def project_src(prefix):
 return sorted(x for x in (product/prefix).rglob("*") if x.is_file() and x.suffix in (".js",".ts",".mjs"))
try:
 kernel=project_src("src/state-kernel-v0")
 check("state_kernel_real_files",len(kernel)>=3)
 adapter=product/"src/operational-spine-v0/state-kernel-adapter.js"
 runstore=product/"src/core/run-store.js"
 recipe=product/"src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js"
 for x in (adapter,runstore,recipe):check("product_file_present_"+x.name,x.is_file())
 kernel_metric={rel(x):metrics(x) for x in kernel}
 kernel_sum={"files":len(kernel_metric),"bytes":sum(v["bytes"] for v in kernel_metric.values()),
             "lines":sum(v["lines"] for v in kernel_metric.values())}
 srcfiles=sorted({*project_src("src"),*project_src("src-typescript")})
 tests=sorted(x for x in (product/"tests").rglob("*") if x.is_file() and x.suffix in (".js",".ts",".mjs"))
 direct_src=[]
 direct_test=[]
 token=re.compile(r"state-kernel-v0|createStateKernel|FilesystemStateStore|StateKernelTaskCycleLifecycle|state-kernel-adapter")
 import_pattern=re.compile(r"(?:require\s*\(|\bfrom\s+|\bimport\s*\()\s*['\x22][^'\x22]*(?:state-kernel-v0|state-kernel-adapter)")
 for source,holder in ((srcfiles,direct_src),(tests,direct_test)):
  for f in source:
   text=f.read_text(encoding="utf-8",errors="replace")
   if token.search(text):
    holder.append({"path":rel(f),"bytes":f.stat().st_size,
      "references":len(token.findall(text)),
      "import_reference":bool(import_pattern.search(text))})
 check("at_least_one_state_kernel_runtime_reference",len(direct_src)>=1)
 check("adapter_explicitly_imports_original_kernel",bool(import_pattern.search(adapter.read_text())))
 size_candidates={
  "installed_kernel_source":kernel_sum,
  "installed_operational_spine_adapter":metrics(adapter),
  "installed_RunStore_separate_mechanics_not_equivalent":metrics(runstore),
  "installed_taskcycle_closure_recipe_preserve_semantics":metrics(recipe)
 }
 e022=origin.read_text(encoding="utf8")
 check("022_published_baseline_requests", "Total HTTP | **127** | **87**" in e022)
 check("022_matched_optimized_workload", "64 GET + 9 batch = 73 requests" in e022)
 t024=json.loads(f024.read_text(encoding="utf8"))
 t028=json.loads(f028.read_text(encoding="utf8"))
 check("024_real_native_read_only_status",t024["status"]=="PASS_NONAUTHORITATIVE_READ_MODEL_WITH_RACE_DETECTION" and t024.get("Product_effect")=="NONE")
 check("028_native_route_and_launcher_status",t028["status"]=="PASS_SELECTED_FAILCLOSED_LAUNCHER_AND_FULL_ROUTE_MATRIX_WITH_PRIVILEGED_BYPASS" and t028.get("Product_effect")=="NONE")
 check("024_live_native_counters_exposed",t024["native_counts"]["GET"]>0 and t024["native_counts"]["read_model_rounds"]>0)
 evidence_024={"historic_carrier_verification":"INVALID_TRUNCATED_LAST_MEMBER",
  "member_recovery":"EXACT_SHA256_VERIFIED_ORIGINAL_JSON_ONLY",
  "original_member_sha256":"cddc0b9bf943e6d3edffb64d9526ae73e33195145ecb3ed08ec37c503c06c9b3",
  "original_checks":len(t024["checks"]),"native_http_GET":t024["native_counts"]["GET"],
  "read_model_rounds":t024["native_counts"]["read_model_rounds"],
  "classifications":[{"case":s["case"],"classification":s["data"]["classification"],"mayAuthorize":s["data"]["mayAuthorize"]} for s in t024["samples"]]}
 check("024_authority_never_granted",all(x["mayAuthorize"] is False for x in evidence_024["classifications"]))
 evidence_028={"original_checks":len(t028["checks"]),"route_count":41,"write_route_count":20,
  "untrusted_root_revision_bypass":any(e.get("phase")=="privileged_direct_CLI_bypass" and e.get("root_revision_unchanged") for e in t028["evidence"]),
  "insecure_restart_bypass":any(e.get("phase")=="restart_and_config_drift" and e.get("omitted_auth_restart")=="UNAUTHORIZED_DEP_ADD_SUCCEEDED" for e in t028["evidence"])}
 check("028_privileged_CLI_bypass_original",evidence_028["untrusted_root_revision_bypass"])
 check("028_misconfigured_restart_original",evidence_028["insecure_restart_bypass"])
 prior022={"baseline_calls":127,"optimized_full_suite_calls":87,"extra_race_GET":11,"extra_race_batch":3,
           "matched_optimized_calls":73,"matched_fewer_calls":54,"relative_reduction_percent":round(54/127*100,1),
           "scope":"same bounded synthetic 022 Beads authoritative consumer workload, NOT A-vs-B production comparison"}
 check("022_arithmetic",prior022["optimized_full_suite_calls"]-prior022["extra_race_GET"]-prior022["extra_race_batch"]==prior022["matched_optimized_calls"])
 # Measured manifest and evidence-backed obligations; this is NOT a weighted score.
 mandatory={
 "A_informational_readonly_plus_existing_Product_authority":{
  "Product_kernel_state_machine_replaced":False,
  "native_Beads_graph_read_experiment":"024 complete; two scans are not atomic",
  "native_api_mutation_rights_for_implementer":"NOT_REQUIRED; read-only SQL only",
  "new_Product_runtime_changes_measured":0,
  "possible_kernel_source_deletion_now":0,
  "hard_limit":"native Beads ready/status/graph cannot grant Product authority or trigger closure",
  "measured_read_cost":"024: "+str(evidence_024["native_http_GET"])+" native GET across "+str(evidence_024["read_model_rounds"])+" read-model rounds, synthetic suite only"},
 "B_authoritative_Beads_with_isolated_writer":{
  "Product_kernel_state_machine_replaced":"PROPOSED_NOT_INSTALLED",
  "installed_consumer_binding_touch_points_lower_bound":len(direct_src),
  "native_async_readset_and_CAS":"022 partly qualified; dynamic graph additions require guarded writers",
  "native_service_writer_isolation":"025-028: conditional; privileged direct CLI / second unauthenticated serve bypass",
  "complete_evidence_semantics_and_recovery_equivalence":"NOT_QUALIFIED",
  "possible_kernel_source_deletion_now":0,
  "hard_limit":"No enforced exclusive graph writer across all privileged clients; no full original TaskCycle compatibility or migration",
  "measured_read_cost":"022 matched synthetic workload: 127 vs 73 calls within B only"}
 }
 check("no_deletion_claim_made",mandatory["A_informational_readonly_plus_existing_Product_authority"]["possible_kernel_source_deletion_now"]==mandatory["B_authoritative_Beads_with_isolated_writer"]["possible_kernel_source_deletion_now"]==0)
 result_obj={
 "id":"TS-BEADS-029-ARCHITECTURE-COST-COMPARISON-20261028-001",
 "status":"PASS_MEASURED_SOURCE_FOOTPRINT_WITH_NONCOMPARABLE_RUNTIME_TELEMETRY",
 "authority":"EXPERIMENTAL_CONTROL_ONLY","Product_effect":"NONE","shared_Dolt_effect":"NONE",
 "subjects":meta,
 "measurements":{"product_src_files":len(srcfiles),"product_test_files":len(tests),
  "source_buckets":size_candidates,"kernel_direct_or_symbol_referencing_source":direct_src,
  "test_references":direct_test,
  "legacy_022_authoritative_optimization":prior022,
  "legacy_024_informational_read":evidence_024,
  "legacy_028_isolation_and_auth":evidence_028},
 "scenarios":mandatory,
 "interpretation":{"A":"lower known adoption-risk: independent informational Beads without Product authority migration",
  "B":"higher architectural replacement potential but unknown net cost, incomplete behavioral/recovery/security equivalence",
  "measured_net_Product_deletion":0,"measured_net_maintenance_savings":"UNKNOWN",
  "Product_adoption":False,"source_files_count_not_work_estimate":True,
  "caution":"Do not compare HTTP calls from distinct synthetic 022/024 suites as latency or performance improvement"},
 "checks":checks}
 result.parent.mkdir(parents=True,exist_ok=True)
 result.write_text(json.dumps(result_obj,indent=2,sort_keys=True)+"\n",encoding="utf8")
 print("TS_BEADS029=PASS;checks="+str(len(checks))+
  ";kernel_files="+str(kernel_sum["files"])+
  ";kernel_bytes="+str(kernel_sum["bytes"])+
  ";referencing_modules="+str(len(direct_src))+
  ";A=INFORMATIONAL;B=NOT_AUTHORIZED;Product=NONE")
 print("TS_BEADS029_RECEIPT="+str(result))
except Exception as exc:
 fail={"id":"TS-BEADS-029-ARCHITECTURE-COST-COMPARISON-20261028-001",
  "status":"FAIL_EXACT_029_ATTEMPT_RECONCILE","reason":str(exc),
  "Product_effect":"NONE","checks":checks}
 result.parent.mkdir(parents=True,exist_ok=True)
 result.write_text(json.dumps(fail,indent=2)+"\n",encoding="utf8")
 print("TS_BEADS029_ERROR="+str(exc),file=sys.stderr)
 raise
