#!/usr/bin/env python3
"""039 comparison: original Product Recipe unchanged; Native Beads B conservative post-read."""
import hashlib,json,os,pathlib,sys
A=pathlib.Path(os.environ["A_RESULT"])
B=pathlib.Path(os.environ["B_RESULT"])
OUT=pathlib.Path(os.environ["RESULT_PATH"])
a=json.loads(A.read_text());b=json.loads(B.read_text())
checks={}
def check(k,v):
 checks[k]="PASS" if v else "FAIL"
check("A_original_real_Kernel_fixture_PASS",a["status"]=="PASS_A_ACTUAL_KERNEL_SAME_RECIPE_POSITIVE_AND_NEGATIVES")
check("B_original_same_Product_Recipe_fixture_PASS",b["status"]=="PASS_B_ORIGINAL_PRODUCT_RECIPE_NATIVE_BEADS_PENDING_AND_NEGATIVES")
check("no_Product_effect",a["Product_effect"]==b["Product_effect"]=="NONE")
original_a=a["measurements"]["negative"]["race"]
reconciled=[x for x in b["negative"] if x.get("type")=="DIRECT_GET_REVISION_CAUSAL_RACE_CONSERVATIVE_JOIN"]
check("exactly_one_conservative_native_join",len(reconciled)==1)
c=reconciled[0] if reconciled else {}
check("original_B_race_classification_preserved",c.get("original_status")=="FAIL" and c.get("original_effect_state")=="NONE")
check("B_postread_native_attempt_is_UNKNOWN",c.get("native_attempt_state")=="UNKNOWN")
check("postread_conservative_state_matches_A",original_a["status"]=="UNKNOWN" and original_a["effect_state"]=="UNKNOWN" and c.get("post_join_status")=="UNKNOWN" and c.get("post_join_effect_state")=="UNKNOWN")
check("no_redispatch_in_this_join",c.get("provider_redispatch_count")==0)
bm=b["metrics"]["B_only_positive_execute"]
check("same_original_recipe_hash",a["product_recipe_sha256"]==bm["Product_original_recipe_sha256"])
bc={x["key"]:x["result"] for x in b["check"]}
check("full_native_Beads_5_obligation_and_close",bc.get("five_original_Product_obligations_satisfied")=="PASS" and bc.get("native_aggregate_closed_all_obligations_terminal")=="PASS")
check("native_Beads_ack_loss_partial_confirmed",bc.get("partial_native_obligation_effect_preserved_not_replayed")=="PASS")
check("native_Beads_terminal_readback",bc.get("independent_native_process_terminal_root_closed")=="PASS")
check("source_is_in_memory_only",b["metrics"]["consumer_source"]["inserted_or_replaced_anchors"]==15)
result={"experiment":"TS-BEADS-039-UNKNOWN-RACE-20261031-001",
 "authority":"EXPERIMENTAL_CONTROL_ONLY","product_effect":"NONE",
 "source_product_recipe_sha256":a["product_recipe_sha256"],
 "original_source_A_SHA256":hashlib.sha256(A.read_bytes()).hexdigest(),
 "original_source_B_SHA256":hashlib.sha256(B.read_bytes()).hexdigest(),
 "original_race":{"A":original_a,"B_original":{"status":c.get("original_status"),"effect_state":c.get("original_effect_state")},
  "B_conservative_join":{"status":c.get("post_join_status"),"effect_state":c.get("post_join_effect_state")}},
 "checks":checks,"checks_passed":sum(v=="PASS" for v in checks.values()),
 "checks_total":len(checks),
 "limitations":["Same original Product recipe source remains unmodified; conservative post-read adapter is experimental, not installed Product.",
 "Native Beads still does NOT enforce no-retry; client post-read logic must remain authoritative and reject ambiguous provider writes.",
 "A race snapshot from global Kernel revision is not equivalent to Beads per-row revision or global Product hash-chain.",
 "Native privileged writer bypass proven in Beads 028 remains open.",
 "No real remote provider ACK-loss; original Product and external effect untouched.",
 "Synthetic fixture does not prove all Developer rejection reachability or Product acceptance."],
 "status":"PASS_BOUNDED_CONSERVATIVE_UNKNOWN_PARITY_OVER_NATIVE_BEADS_WITH_GLOBAL_GAPS" if all(v=="PASS" for v in checks.values()) else "FAIL_CLOSED_SEMANTIC_PARITY"}
OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
print("TS_BEADS039="+result["status"]+";checks="+str(result["checks_passed"])+"/"+str(len(checks))+";Product=NONE",flush=True)
if result["status"].startswith("FAIL"):raise SystemExit(1)
