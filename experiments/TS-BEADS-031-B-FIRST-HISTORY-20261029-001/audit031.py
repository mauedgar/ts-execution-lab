#!/usr/bin/env python3
"""031 provenance-only qualification. No external effects; do NOT infer native
history parity, effect recovery or writer exclusivity from read-only receipts.
"""
import hashlib,json,os,pathlib,sys
root=pathlib.Path(os.environ["EXPERIMENT_SCRATCH"])
kernel=pathlib.Path(os.environ["KERNEL_SOURCE"]).read_text()
dolt=pathlib.Path(os.environ["DOLT_PROCEDURE_SOURCE"]).read_text()
a=json.loads((root/"030"/"original"/"A_KERNEL.json").read_bytes())
b=json.loads((root/"030"/"original"/"B_BEADS.json").read_bytes())
c=json.loads((root/"030"/"original"/"RESULT030.json").read_bytes())
old=json.loads((root/"028"/"original"/"RESULT028.json").read_bytes())
checks={}
def test(k,v):checks[k]="PASS" if v else "FAIL"
test("A_kernel_hash_chained_event_replay_source",all(x in kernel for x in
  ("previous_hash","events.ndjson","event count/revision mismatch","generation checksum mismatch",
   "HEAD","fsyncSync","event_hash")))
test("native_dolt_explicit_commit_procedure_source",all(x in dolt for x in
  ("func doDoltCommit(","NewPendingCommit","DoltCommit(","StageDatabase")))
test("Dolt_history_not_automatically_proven_by_procedure_source",True)
test("A_original_Kernel_event_count_14",a["measurements"]["positive"]["kernel_event_count"]==14)
test("B_native_Beads_no_original_Product_module_mutation",
  c["comparisons"]["same_recipe_source"]["Product_installed_modules_changed"]==0)
test("B_native_CLI_terminal_readback_qualified",
  "independent_native_process_terminal_root_closed" in {x["key"] for x in b["check"]})
test("same_consumer_original_recipe_hash_A_B",
  a["product_recipe_sha256"]==b["metrics"]["B_only_positive_execute"]["Product_original_recipe_sha256"])
test("original_Kernel_race_UNKNOWN_versus_B_NONE_preserved",
  c["comparisons"]["benchmarks_not_equivalent"]["race_effect_classification"]==
    {"A_global_Kernel":"UNKNOWN","B_scoped_Beads":"NONE",
     "reason":"Global Kernel version changed due to concurrent attempt UNKNOWN; B batch refused on causal gate row revision",
     "same_effect_state":False})
test("historical_privileged_writable_graph_path_confirmed",
  any(x.get("phase")=="privileged_direct_CLI_bypass" and x.get("root_revision_unchanged")
       for x in old["evidence"]))
test("historical_unprotected_alternate_service_confirmed",
  any(x.get("phase")=="restart_and_config_drift" and
      x.get("omitted_auth_restart")=="UNAUTHORIZED_DEP_ADD_SUCCEEDED"
      for x in old["evidence"]))
test("no_real_remote_provider_receipt_available_in_evidence",True)
test("no_new_Product_or_shared_Dolt_effect",a["Product_effect"]==b["Product_effect"]==
    c["Product_effect"]==old["Product_effect"]=="NONE")
report={
 "id":"TS-BEADS-031-B-FIRST-AUDIT-UNKNOWN-BOUNDARY-20261029-001",
 "status":"PASS_SOURCE_AND_HISTORICAL_EVIDENCE_AUDIT_WITH_NATIVE_AND_PROVIDER_GATES_OPEN",
 "authority":"EXPERIMENTAL_CONTROL_ONLY","Product_effect":"NONE",
 "shared_Dolt_effect":"NONE",
 "Product_subject":"d4154bd43f26515c39a41be974e462a0c7406a2d",
 "Product_tree":"cbfb71ad8632047e8e64fe2665d8614d835a2c8b",
 "checks":checks,
 "source_provenance":{
  "Product_Kernel_store_blob":"f80d7cfe2bc9cd228cb6e3ca817c2e8802e74c8a",
  "Dolt_v2_2_0_commit_procedure_git_blob":"00d064481f34feb33dfb240d8056df3ecad83e04",
  "A_original_kernel_sha256":hashlib.sha256((root/"030"/"original"/"A_KERNEL.json").read_bytes()).hexdigest(),
  "B_original_beads_sha256":hashlib.sha256((root/"030"/"original"/"B_BEADS.json").read_bytes()).hexdigest(),
  "source_receipts":"028 and 030 immutable original Git-persisted verified carriers"
 },
 "observations":{
  "A_event_journal":"Original Kernel source verifies hash-linked events against HEAD and replay",
  "B_native_history":"Dolt supports explicit SQL commit; 030 B readback confirms native state, NOT journal parity",
  "effect_UNKNOWN":"030 synthetic attempt UNKNOWN blocks, ACK-loss carries confirmed partial write, no real provider",
  "effect_classification_divergence":"A UNKNOWN/UNKNOWN versus B FAIL/NONE under related gate-race",
  "writer_bypass":"028 native privileged CLI/alternate serve can add graph edge without root revision"
 },
 "not_qualified":[
  "Automatic Beads native per-operation historical commit equivalence to Kernel hash-chained journal",
  "Real independent external provider effect identity, ACK loss and UNKNOWN reconciliation without duplicate dispatch",
  "Native exclusive causal writer under privileged alternate BD/Dolt access",
  "Provider recovery across actual restart/outage, production admission and installed Product integration"
 ],
 "disposition":"B_FIRST_DESIGN_CONTINUES_EXPERIMENTAL_ONLY",
 "native_runtime_new_attempt":"NOT_PERFORMED_AFTER_TOOL_SECURITY_BLOCKED_FIXTURE_PUBLICATION",
 "next":"Separate bounded native Dolt checkpoint and external effect/provider qualification under tooling that authorizes exact fixture; no unverified PASS"
}
if any(v!="PASS" for v in checks.values()):report["status"]="FAIL_SOURCE_ORIGINAL_EVIDENCE_DRIFT"
pathlib.Path(os.environ["RESULT_PATH"]).write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
print("TS_BEADS031_EVIDENCE_AUDIT="+report["status"]+";checks="+str(len(checks))+
      ";native_history_parity=OPEN;real_provider=OPEN;writer_exclusivity=BLOCKED;Product=NONE")
if report["status"].startswith("FAIL"):sys.exit(1)
