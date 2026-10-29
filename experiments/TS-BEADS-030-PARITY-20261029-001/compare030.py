#!/usr/bin/env python3
"""030 B-first parity for same original Product recipe, verified A and B native receipts."""
import json,os,pathlib,hashlib
a=json.loads(pathlib.Path(os.environ["A_RESULT"]).read_text())
b=json.loads(pathlib.Path(os.environ["B_RESULT"]).read_text())
dest=pathlib.Path(os.environ["RESULT_PATH"])
assert a["status"]=="PASS_A_ACTUAL_KERNEL_SAME_RECIPE_POSITIVE_AND_NEGATIVES",a
assert b["status"]=="PASS_B_ORIGINAL_PRODUCT_RECIPE_NATIVE_BEADS_PENDING_AND_NEGATIVES",b
assert a["Product_effect"]==b["Product_effect"]=="NONE"
ac=a["measurements"]["positive"]
bm=b["metrics"]["B_only_positive_execute"]
bc={x["key"]:x["result"] for x in b["check"]}
an=a["measurements"]["negative"]
tests={}
def test(name,condition):
 tests[name]="PASS" if condition else "FAIL"
test("same_original_Product_recipe_sha256",a["product_recipe_sha256"]==bm["Product_original_recipe_sha256"])
test("both_real_positive_pass_confirmed",ac["status"]=="PASS" and ac["effect_state"]=="CONFIRMED" and
    bc.get("actual_Product_consumer_full_pending_obligations_PASS")=="PASS")
test("five_obligations_and_close_A_and_B",
     ac["final_state"]=="CLOSED" and ac["satisfied"]==5 and
     bc.get("five_original_Product_obligations_satisfied")=="PASS" and
     bc.get("native_aggregate_closed_all_obligations_terminal")=="PASS")
test("competent_authority_attached_same_semantics",
     ac["authority_ids"]==["authority:developer-001","authority:effect-001","authority:reviewer-001"] and
     bc.get("native_aggregate_authority_refs_attached_from_competent_fixture")=="PASS")
test("terminal_replay_refused_A_and_B",
     ac["repeated_status"]=="FAIL" and bc.get("terminal_reexecution_denied")=="PASS")
test("UNKNOWN_blocks_A_and_B",
     an["unknown"]["status"]=="BLOCKED" and
     bc.get("pending_unreconciled_UNKNOWN_blocks_original_recipe")=="PASS")
test("ACK_loss_preserves_partial_CONFIRMED_A_and_B",
     an["ack"]["effect_state"]=="CONFIRMED" and an["ack"]["satisfied"]==1 and
     bc.get("native_pending_obligation_wrong_ack_classified_CONFIRMED")=="PASS" and
     bc.get("partial_native_obligation_effect_preserved_not_replayed")=="PASS")
test("causal_race_preserves_TaskCycle_A_and_B_with_classification_recorded",
     an["race"]["status"]=="FAIL" and
     an["race"]["effect_state"] in ("NONE","UNKNOWN") and an["race"]["remaining"]==5 and
     bc.get("GET_revision_scoped_causal_race_rejected_without_partial_native_effect")=="PASS")
test("original_presatisfied_REJECTED_authority_gap_not_fixed",
     an["presatisfied_developer_rejected"]["status"]=="READY" and
     bc.get("original_Product_presatisfied_developer_REJECTED_returns_READY")=="PASS")
test("both_exact_native_CAS_audited",ac["store_calls"]["mutate"]>=6 and
     bm["batches"]>=6 and bc.get("native_revision_and_event_six_step_correspondence")=="PASS")
test("B_real_durable_terminal_CLI_readback",
     bc.get("independent_native_process_terminal_root_closed")=="PASS")
test("no_Product_mutation",a["Product_effect"]=="NONE" and b["Product_effect"]=="NONE")
race_divergence=an["race"]["effect_state"]!="NONE"
failed=[k for k,v in tests.items() if v!="PASS"]
report={"id":"TS-BEADS-030-B-FIRST-CONSUMER-PARITY-20261029-001",
 "status":"FAIL_PARITY_RECONCILE" if failed else (
    "PASS_B_FIRST_SHARED_TASKCYCLE_OUTCOMES_EFFECT_CLASSIFICATION_DIVERGENCE"
    if race_divergence else "PASS_B_FIRST_SAME_PRODUCT_CONSUMER_SEMANTIC_PARITY_WITH_LIMITATIONS"),
 "authority":"EXPERIMENTAL_CONTROL_ONLY","Product_effect":"NONE","shared_Dolt_effect":"NONE",
 "product_sha":"d4154bd43f26515c39a41be974e462a0c7406a2d",
 "product_tree":"cbfb71ad8632047e8e64fe2665d8614d835a2c8b",
 "original_recipe_sha256":a["product_recipe_sha256"],
 "checks":tests,
 "comparisons":{
  "A_original_state_kernel":{"single_execute_ms":ac["elapsed_ms"],"store_calls":ac["store_calls"],
    "status":ac["status"],"effect_state":ac["effect_state"],"events":ac["kernel_event_count"],
    "final_state":ac["final_state"],"authority_ids":ac["authority_ids"],"obligations_satisfied":5,
    "negative":an},
  "B_native_Beads_port":{"single_execute_ms":bm["elapsed_ms"],
     "native_GET":bm["reads"],"native_batch":bm["batches"],
     "native_write_items":bm["write_items"],"status":"PASS","effect_state":"CONFIRMED",
     "original_test_checks":len(b["check"]),
     "native_termination":"readback_CLI_passed",
     "native_get_revision":"per_issue_tokens_no_extra_batch"},
  "same_recipe_source":{"original_bytes":b["metrics"]["consumer_source"]["original_bytes"],
    "async_adapted_bytes":b["metrics"]["consumer_source"]["experimental_bytes"],
    "in_memory_anchor_substitutions":b["metrics"]["consumer_source"]["inserted_or_replaced_anchors"],
    "Product_installed_modules_changed":0},
  "benchmarks_not_equivalent":{"runtime_sample_size_each":1,
    "A_is_sync_FS_event_journal":True,"B_is_async_local_Beads_Dolt_HTTP":True,
    "not_a_production_latency_winner":True,"no_measured_net_deletion":True,
    "no_security_equivalence":"023-028 native privileged graph write bypass not remediated",
    "race_effect_classification":{"A_global_Kernel":an["race"]["effect_state"],
       "B_scoped_Beads":"NONE","same_effect_state":not race_divergence,
       "reason":"Global Kernel version changed due to concurrent attempt UNKNOWN; B batch refused on causal gate row revision"},

    "no_external_provider_unknown":"synthetic UNKNOWN/ACK only",
    "global_history_equivalence":"NOT_QUALIFIED",
    "causal_graph_full_writer_exclusivity":"NOT_QUALIFIED",
    "semantic_authority_REJECTED_source_gap":"REPRODUCED_IN_BOTH",
    "consumer_context":"same original Product recipe and same evidence rules, different authorized native storage boundaries",
    "B_first_priority":"DO_NOT_RECLASSIFY_AS_PRODUCT_ADOPTION"}
 },
 "source_artifacts":{"A_sha256":hashlib.sha256(pathlib.Path(os.environ["A_RESULT"]).read_bytes()).hexdigest(),
                     "B_sha256":hashlib.sha256(pathlib.Path(os.environ["B_RESULT"]).read_bytes()).hexdigest()},
 "limitations":["Only one cold timed positive execution each; source instrumented but not a performance study",
 "Original Product Kernel uses global event journal; B relies on scoped synthetic epoch, not equivalent history",
 "Synthetic authority fixture; no historical legitimate reachability of rejected Developer after satisfied",
 "B tested only adapted in-memory Product consumer with native Beads; no installed Product consumer migration",
 "Writer-exclusivity bypass remains material, no real external provider UNKNOWN or multi-host recovery",
 "No net Product code deletion or maintenance advantage established"]}
dest.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
if failed:raise AssertionError("030_PARITY_FAILURE:"+",".join(failed))
print("TS_BEADS030_PARITY=PASS;checks="+str(len(tests))+
      ";B_PRIORITY=YES;AUTHORITY=EXPERIMENTAL_ONLY;Product=NONE")
print("TS_BEADS030_METRICS A_ms="+str(round(ac["elapsed_ms"],3))+
      " B_ms="+str(round(bm["elapsed_ms"],3))+
      " B_get="+str(bm["reads"])+" B_batch="+str(bm["batches"]))
