"""Frozen read-contract and exact-byte negative probes (no Product authority)."""
from __future__ import annotations

import base64
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import json
import unittest

from ts_global import legacy_v0
from ts_global.bridge import StorageRejected, apply, initialize, read
from test_bridge import FakeConn, GOLDEN, mutation, genesis

DATE = "2026-11-07T00:00:00.000Z"


def bootstrap():
    refs = [{"kind":"AUTHORITY","id":"AUTH-SYNTHETIC-BOOTSTRAP"}]
    evidence = [{"kind":"EVIDENCE","id":"EV-SYNTHETIC-BOOTSTRAP"}]
    after = {
        "schema_version":"tecnotron-state-kernel/v0","kind":"TaskCycle","id":"TC-SYNTHETIC-IMPORT",
        "revision":1,"state":"READY","created_at":DATE,"updated_at":DATE,
        "authority_refs":refs,"related_ids":[],"last_event_id":"event-1",
        "responsibility":"synthetic import only", "obligations":[], "terminal_disposition_ref":None,
    }
    provenance={"mode":"IMPORTED_ESTABLISHED_STATE","cutover_at":DATE,
                "historical_events_reconstructed":False,"authority_refs":refs,"evidence_refs":evidence}
    return {"id":"event-1","sequence":1,"kind":"TaskCycle","aggregate_id":after["id"],
            "before_revision":0,"after":after,"previous_hash":None,"at":DATE,
            "action":"BOOTSTRAP_IMPORT","bootstrap_provenance":provenance}


class FrozenLegacyV0Tests(unittest.TestCase):
    def test_01_valid_bootstrap_contract(self):
        legacy_v0.validate_event(bootstrap())

    def test_02_bootstrap_missing_provenance_denied(self):
        p=bootstrap()
        del p["bootstrap_provenance"]
        with self.assertRaisesRegex(ValueError,"BOOTSTRAP_CONTRACT_MISMATCH"):
            legacy_v0.validate_event(p)

    def test_03_nonbootstrap_provenance_denied(self):
        p=bootstrap()
        p["action"]="CREATE"
        with self.assertRaisesRegex(ValueError,"BOOTSTRAP_CONTRACT_MISMATCH"):
            legacy_v0.validate_event(p)

    def test_04_bootstrap_terminal_state_denied(self):
        p=bootstrap()
        p["after"]["state"]="CLOSED"
        with self.assertRaisesRegex(ValueError,"BOOTSTRAP_CONTRACT_MISMATCH"):
            legacy_v0.validate_event(p)

    def test_05_bootstrap_cutover_time_mismatch_denied(self):
        p=bootstrap()
        p["after"]["created_at"]="2026-11-07T00:00:01.000Z"
        with self.assertRaisesRegex(ValueError,"BOOTSTRAP_CONTRACT_MISMATCH"):
            legacy_v0.validate_event(p)

    def test_06_bootstrap_no_authority_denied(self):
        p=bootstrap()
        p["bootstrap_provenance"]["authority_refs"]=[]
        with self.assertRaisesRegex(ValueError,"BOOTSTRAP_CONTRACT_MISMATCH"):
            legacy_v0.validate_event(p)

    def test_07_bootstrap_no_evidence_denied(self):
        p=bootstrap()
        p["bootstrap_provenance"]["evidence_refs"]=[]
        with self.assertRaisesRegex(ValueError,"BOOTSTRAP_CONTRACT_MISMATCH"):
            legacy_v0.validate_event(p)

    def test_08_bootstrap_required_authority_undeclared_denied(self):
        p=bootstrap()
        p["after"]["obligations"]=[{"id":"O1","status":"SATISFIED","authority_ref":"AUTH-OTHER"}]
        with self.assertRaisesRegex(ValueError,"BOOTSTRAP_CONTRACT_MISMATCH"):
            legacy_v0.validate_event(p)

    def test_09_bootstrap_acceptance_pending_obligation_denied(self):
        p=bootstrap()
        p["after"]["state"]="PENDING_ACCEPTANCE"
        p["after"]["obligations"]=[{"id":"O1","status":"PENDING","authority_ref":None}]
        with self.assertRaisesRegex(ValueError,"BOOTSTRAP_CONTRACT_MISMATCH"):
            legacy_v0.validate_event(p)

    def test_10_bootstrap_cutover_reconstructed_true_denied(self):
        p=bootstrap()
        p["bootstrap_provenance"]["historical_events_reconstructed"]=True
        with self.assertRaisesRegex(ValueError,"BOOTSTRAP_CONTRACT_MISMATCH"):
            legacy_v0.validate_event(p)

    def test_11_invalid_attempt_unknown_flag_denied(self):
        state=json.loads(mutation(8).state_bytes)
        attempt=state["aggregates"]["ExecutionAttempt"]["AT-SYNTHETIC"]
        self.assertEqual(attempt["state"],"UNKNOWN")
        attempt["reconciliation_required"]=False
        with self.assertRaisesRegex(ValueError,"PRODUCT_V0_CONTRACT_MISMATCH"):
            legacy_v0.validate_state(state,9)

    def test_12_invalid_snapshot_milestone_missing_title_denied(self):
        state=json.loads(mutation(1).state_bytes)
        del state["aggregates"]["Milestone"]["MS-SYNTHETIC"]["title"]
        with self.assertRaisesRegex(ValueError,"PRODUCT_V0_CONTRACT_MISMATCH"):
            legacy_v0.validate_state(state,2)

    def test_13_unicode_js_snapshot_reference_all_events(self):
        for i in range(len(GOLDEN["mutations"])):
            with self.subTest(sequence=i+1):
                m=mutation(i)
                v=json.loads(m.state_bytes)
                legacy_v0.validate_state(v,i+1)
                self.assertEqual(legacy_v0.exact_js_snapshot(v),m.state_bytes)

    def test_14_reordered_snapshot_keys_rejected_before_sql(self):
        conn=FakeConn()
        initialize(conn,GOLDEN['scope'],genesis())
        m=mutation(0)
        v=json.loads(m.state_bytes)
        wrong=json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False).encode()+b'\n'
        self.assertNotEqual(wrong,m.state_bytes)
        prior=conn.queries
        with self.assertRaisesRegex(StorageRejected,'PRODUCT_V0_CONTRACT_MISMATCH'):
            apply(conn,replace(m,state_bytes=wrong))
        self.assertEqual(conn.queries,prior)

    def test_15_compact_snapshot_rejected_before_sql(self):
        conn=FakeConn()
        initialize(conn,GOLDEN['scope'],genesis())
        m=mutation(0)
        wrong=json.dumps(json.loads(m.state_bytes),ensure_ascii=False,separators=(',',':')).encode()+b'\n'
        prior=conn.queries
        with self.assertRaisesRegex(StorageRejected,'SNAPSHOT_JS_BYTES_MISMATCH'):
            apply(conn,replace(m,state_bytes=wrong))
        self.assertEqual(conn.queries,prior)

    def test_16_unicode_escaped_equivalent_snapshot_rejected(self):
        conn=FakeConn()
        initialize(conn,GOLDEN['scope'],genesis())
        m=mutation(0)
        wrong=json.dumps(json.loads(m.state_bytes),ensure_ascii=True,indent=2).encode()+b'\n'
        self.assertNotEqual(wrong,m.state_bytes)
        with self.assertRaisesRegex(StorageRejected,'SNAPSHOT_JS_BYTES_MISMATCH'):
            apply(conn,replace(m,state_bytes=wrong))

    def test_17_self_consistent_tamper_rejected_on_read(self):
        conn=FakeConn()
        initialize(conn,GOLDEN['scope'],genesis())
        m=mutation(0)
        apply(conn,m)
        state=json.loads(m.state_bytes)
        state['aggregates']['TaskCycle']['TC-SYNTHETIC']['state']='NOT_A_LEGAL_STATE'
        raw=legacy_v0.exact_js_snapshot(state)
        conn.heads[GOLDEN['scope']]['state_bytes']=raw
        conn.heads[GOLDEN['scope']]['state_sha256']=sha256(raw).hexdigest()
        with self.assertRaisesRegex(StorageRejected,'PRODUCT_V0_CONTRACT_MISMATCH'):
            read(conn,GOLDEN['scope'])

    def test_18_js_numeric_keys_order_reference(self):
        # ECMAScript enumerates array-index keys numerically before insertion-order keys.
        src={'aggregates':{'10':1,'2':2,'alpha':3,'1':4}}
        expected=b'{\n  "aggregates": {\n    "1": 4,\n    "2": 2,\n    "10": 1,\n    "alpha": 3\n  }\n}\n'
        self.assertEqual(legacy_v0.exact_js_snapshot(src),expected)

    def test_19_noncanonical_date_denied(self):
        p=bootstrap()
        p['at']='2026-11-07T00:00:00Z'
        with self.assertRaisesRegex(ValueError,'PRODUCT_V0_CONTRACT_MISMATCH'):
            legacy_v0.validate_event(p)


if __name__ == '__main__':
    unittest.main()
