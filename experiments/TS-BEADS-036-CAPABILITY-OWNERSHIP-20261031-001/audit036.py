#!/usr/bin/env python3
"""Bounded Beads 036 evidence/ownership consistency check. No Product or Beads writes."""
import hashlib,json,os,pathlib,re,sys
from collections import Counter

def demand(ok, code):
    if not ok: raise RuntimeError("BLOCKED_EVIDENCE_"+code)

def main():
    raw=pathlib.Path(sys.argv[1]).read_bytes()
    doc=json.loads(raw)
    demand(doc["schema"]=="ts-ee-beads036-capability-ownership/v1","SCHEMA")
    demand(doc["authority"]=="EXPERIMENTAL_CONTROL_ONLY" and doc["product_effect"]=="NONE","AUTHORITY")
    demand(doc["target_canonical_issue"]=="mauedgar/tecnotron-ai#35","CANONICAL_ISSUE")
    demand(doc["canonical_execution_owner"]=="TECNOTRON_BETA_CONTROL","PRODUCT_OWNER")
    subject=doc["product_subject"]
    demand(subject["repository"]=="mauedgar/tecnotron-ai" and subject["branch"]=="tools","PRODUCT_REPOSITORY")
    demand(bool(re.fullmatch("[0-9a-f]{40}",subject["commit"])),"PRODUCT_COMMIT")
    demand(bool(re.fullmatch("[0-9a-f]{40}",subject["sot_blob"])),"SOT_BLOB")
    sources=doc["source_inventory"]
    demand(len(sources)==len({x["path"] for x in sources})==8,"SOURCE_INVENTORY")
    demand(all(bool(re.fullmatch("[0-9a-f]{40}",s["blob"])) and isinstance(s["bytes"],int) and s["bytes"]>0 for s in sources),"SOURCE_IDENTITIES")
    sizes={s["path"]:s["bytes"] for s in sources}
    kernel=sum(v for k,v in sizes.items() if k.startswith("src/state-kernel-v0/"))
    adapter=sizes["src/operational-spine-v0/state-kernel-adapter.js"]
    recipe=sizes["src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js"]
    demand((kernel,adapter,recipe)==(36715,12020,36279),"PHYSICAL_FOOTPRINT")
    evidence=doc["prior_evidence"]
    required={"021","028","029","030","032","033","034","035"}
    demand({x["id"] for x in evidence}==required and len(evidence)==8,"RECEIPT_COVERAGE")
    demand(all(bool(re.fullmatch("[0-9a-f]{40}",x["source_commit"])) and isinstance(x["run"],int) and x["run"]>0 for x in evidence),"RECEIPT_IDENTITIES")
    identifiers={x["id"]:x for x in evidence}
    demand("BYPASS" in identifiers["028"]["verdict"] and "SEMANTIC_DIVERGENCE" in identifiers["030"]["verdict"],"PRIOR_BLOCKERS")
    demand("PRIVILEGED_BOUNDARY_OPEN" in identifiers["035"]["verdict"],"WRITER_BOUNDARY")
    ins=doc["invariants"]
    demand(len(ins)==len({x["id"] for x in ins})==10,"INVARIANT_COVERAGE")
    demand(all(x["current_owner"] and x["optionA"] and x["optionB"] for x in ins),"INVARIANT_OWNER")
    b={x["id"]:x["optionB"] for x in ins}
    a={x["id"]:x["optionA"] for x in ins}
    demand(b["I02"]=="BLOCKED_SEMANTIC_PARITY" and b["I06"]=="BLOCKED_PRIVILEGED_BYPASS","REQUIRED_B_BLOCK")
    demand(b["I05"]=="BLOCKED_SEMANTIC_PARITY" and b["I09"]=="BLOCKED_ACTOR_AUTH","EFFECT_AND_AUTH_GAPS")
    demand(a["I06"]=="NOT_APPLICABLE_NONAUTHORITATIVE" and a["I07"]=="OPTIONAL_PROJECTION_ONLY","A_NONAUTHORITATIVE")
    demand(all(i["must_keep"] for i in ins if i["id"]!="I07"),"OWNERSHIP_RETAINED")
    policy=doc["policy"]
    demand(all(v is False for v in policy.values()),"PRODUCT_NONINTERVENTION")
    opt=doc["options"]
    demand(opt["A"]["authority"]=="NONE" and opt["B"]["recommending_product_adoption"] is False,"OPTION_AUTHORITY")
    demand(all(opt[k]["product_kernel_removed_bytes"]==0 for k in ("A","B")),"NO_FALSE_REMOVAL")
    demand(all(opt[k]["known_implementation_added_bytes"]=="UNMEASURED" for k in ("A","B")),"NO_FALSE_COST_CLAIM")
    counts=Counter(i["optionB"].split("_",1)[0] for i in ins)
    out={
      "experiment":doc["experiment"],"source_sha256":hashlib.sha256(raw).hexdigest(),
      "authority":"EXPERIMENTAL_CONTROL_ONLY","product_effect":"NONE",
      "canonical_issue":"mauedgar/tecnotron-ai#35","canonical_execution_owner":"TECNOTRON_BETA_CONTROL",
      "product_baseline":subject["commit"],
      "kernel_source_bytes":kernel,"adapter_source_bytes":adapter,"closure_recipe_source_bytes":recipe,
      "examined_source_bytes":kernel+adapter+recipe,
      "measured_product_code_removed_bytes":0,"measured_net_maintenance_savings":"NOT_ESTABLISHED",
      "source_count":len(sources),"evidence_receipt_refs":len(evidence),"invariants_mapped":len(ins),
      "authoritative_beads_adoption":"BLOCKED",
      "critical_gaps":["PRIVILEGED_WRITER_BYPASS_028_035","GLOBAL_REVISION_AND_HASH_CHAIN_PARITY","UNKNOWN_EFFECT_SEMANTIC_PARITY_030","PER_ACTOR_WRITE_AUTHORITY"],
      "non_authoritative_read_projection":"OPTIONAL_NO_PRODUCT_DEPENDENCY",
      "new_native_beads_runs":0,
      "counts_B_status_prefix":dict(sorted(counts.items())),
      "technical_result":"PASS_SOURCE_BOUNDED_OWNERSHIP_AUDIT_WITH_AUTHORITATIVE_GAPS_OPEN"
    }
    target=pathlib.Path(os.environ["TS_BEADS036_RESULT"])
    demand(not target.exists(),"RESULT_ALREADY_EXISTS")
    target.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("TS_BEADS036="+out["technical_result"]+";kernel_bytes="+str(kernel)+";adapter_bytes="+str(adapter)+";recipe_bytes="+str(recipe)+";Product=NONE",flush=True)
    print("TS_BEADS036_ORIGINAL_RESULT_SHA256="+hashlib.sha256(target.read_bytes()).hexdigest(),flush=True)

if __name__=="__main__":
    main()
