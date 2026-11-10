"""A02-LAN SOURCE_ONLY negative and original Product JS packet qualification.

Run ONLY with a fresh generated disposable packet. Never opens a DB connection.
The source-native CI invokes this on CPython3.15.2 and psycopg binary3.3.8.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from a02_lan.lan_probe import (preflight_runtime, strict_packet,
                                pinned_schema_statements, asserted_host_identity,
                                assert_fresh_disposable_catalog,
                                private_receipt_dir, write_once_receipt)
from ts_global.bridge import StorageRejected


def require(ok: bool, code: str) -> None:
    if not ok:
        raise AssertionError(code)


def main() -> None:
    require(len(sys.argv) == 2, "ONE_ARTIFACT_ARGUMENT")
    source = Path(sys.argv[1]).resolve(strict=True)
    require(source.is_file() and source.stat().st_size < 6 * 1024 * 1024,
            "EXACT_FILE_BOUND")
    original = source.read_bytes()
    os.environ["TS_R3_A02_PACKET_SHA256"] = sha256(original).hexdigest()
    preflight_runtime()
    packet, genesis, proposals = strict_packet(str(source))
    require(packet["expected_revision_before"] == 0
            and packet["expected_revision_after"] == 1, "EXACT_REVISION")
    require(len(genesis) > 30 and
            all(p.expected_revision == 0 for p in proposals.values()),
            "ORIGINAL_JS_COMPETING_GENESIS")
    require(proposals["a"].mutation_id == "A10-A02-LAN-A"
            and proposals["b"].mutation_id == "A10-A02-LAN-B"
            and proposals["a"].payload_bytes != proposals["b"].payload_bytes,
            "DISTINCT_ORIGINAL_JS_MUTATIONS")
    require(packet["product_effect"] == "NONE"
            and packet["source"] == "FROZEN_ORIGINAL_PRODUCT_V0_JS_VIA_A10_SHADOW",
            "NONPRODUCT_ORIGINAL_JS_REQUIRED")
    negatives = [
        ("wrong-schema", lambda d: d.update(schema="INVALID")),
        ("wrong-scope", lambda d: d.update(scope="OTHER")),
        ("bad-effect-claim", lambda d: d.update(product_effect="CONFIRMED")),
        ("bad-source-claim", lambda d: d.update(source="UNVERIFIED")),
        ("nonzero-before", lambda d: d.update(expected_revision_before=1)),
        ("nonone-after", lambda d: d.update(expected_revision_after=2)),
        ("corrupt-genesis", lambda d: d.update(genesis_sha256="0" * 64)),
        ("foreign-side-a", lambda d: d["a"].update(scope="OTHER")),
        ("bad-mut-id", lambda d: d["a"].update(mutationId="A10-FOREIGN")),
        ("wrong-proposal-rev", lambda d: d["b"].update(expectedRevision=1)),
        ("bad-epoch", lambda d: d["b"].update(expectedEpoch=2)),
        ("bad-fingerprint", lambda d: d["a"].update(fingerprint="0" * 64)),
        ("bad-state-hash", lambda d: d["b"].update(stateSha256="0" * 64)),
        ("bad-eventline-hash", lambda d: d["a"].update(eventLineSha256="0" * 64)),
        ("extra-property", lambda d: d.update(unexpected=True)),
        ("missing-proposal", lambda d: d.pop("b")),
    ]
    observed = 0
    with TemporaryDirectory(prefix="ts-r3-a02-source-only-") as d:
        tmp = Path(d) / "negative.json"
        for name, mutate in negatives:
            candidate = deepcopy(packet)
            mutate(candidate)
            data = (json.dumps(candidate, separators=(",", ":")) + "\n").encode("utf-8")
            tmp.write_bytes(data)
            os.environ["TS_R3_A02_PACKET_SHA256"] = sha256(data).hexdigest()
            try:
                strict_packet(str(tmp))
            except (AssertionError, StorageRejected, ValueError, KeyError):
                observed += 1
            else:
                raise AssertionError("NEGATIVE_ACCEPTED_" + name)
        os.environ["TS_R3_A02_PACKET_SHA256"] = "0" * 64
        try:
            strict_packet(str(source))
        except AssertionError:
            observed += 1
        else:
            raise AssertionError("WRONG_PACKET_SHA_ACCEPTED")
    os.environ["TS_R3_A02_PACKET_SHA256"] = sha256(original).hexdigest()
    require(observed == 17, "EXACT_NEGATIVE_COUNT")
    assert strict_packet(str(source))[0]["schema"] == "TS_R3_A02_LAN_PROPOSALS_V1"
    statements = pinned_schema_statements()
    require(len(statements) == 4 and statements[0] ==
            "CREATE SCHEMA ts_r3_global_head_20261107_001",
            "IMMUTABLE_SQL_BLOB_NOT_RECOGNIZED")
    class FakeResult:
        def __init__(self, value):
            self.value = value
        def fetchall(self):
            return self.value
        def fetchone(self):
            return self.value
    class ForeignPublicObjectConn:
        def execute(self, sql):
            if "SELECT nspname" in sql and "pg_catalog.pg_namespace" in sql:
                return FakeResult([{"nspname":"public"}])
            if "pg_catalog.pg_class c" in sql and "ns.nspname='public'" in sql:
                return FakeResult({"n":1})
            raise AssertionError("UNEXPECTED_FAKE_DB_QUERY")
    try:
        assert_fresh_disposable_catalog(ForeignPublicObjectConn())
    except AssertionError as exc:
        require(str(exc) == "FOREIGN_PUBLIC_RELATION",
                "FOREIGN_PUBLIC_REJECTION_WRONG_CODE")
    else:
        raise AssertionError("FOREIGN_PUBLIC_OBJECT_ACCEPTED")
    hold_host = os.environ.pop("TS_R3_A02_EXPECTED_HOST_SHA256", None)
    hold_attempt = os.environ.pop("TS_R3_A02_EXECUTION_ATTEMPT", None)
    try:
        try:
            asserted_host_identity()
        except AssertionError as exc:
            require(str(exc) == "NATIVE_HOST_ATTESTATION_MISMATCH",
                    "HOST_ATTESTATION_WRONG_CODE")
        else:
            raise AssertionError("UNATTESTED_HOST_ACCEPTED")
    finally:
        if hold_host is not None:
            os.environ["TS_R3_A02_EXPECTED_HOST_SHA256"] = hold_host
        if hold_attempt is not None:
            os.environ["TS_R3_A02_EXECUTION_ATTEMPT"] = hold_attempt
    # Exercise the write-ahead receipt guard without any DB connectivity.
    previous_dir = os.environ.pop("TS_R3_A02_PRIVATE_RECEIPT_DIR", None)
    receipt_negatives = 0
    try:
        try:
            private_receipt_dir()
        except AssertionError as exc:
            require(str(exc) == "PRIVATE_RECEIPT_DIR_REQUIRED",
                    "MISSING_PRIVATE_RECEIPT_DIR_WRONG_CODE")
            receipt_negatives += 1
        else:
            raise AssertionError("MISSING_PRIVATE_RECEIPT_DIR_ACCEPTED")
        # A private ext4 home directory is required on BOTH WSL Linux clients.
        with TemporaryDirectory(prefix="ts-r3-a02-lan-physical-race-",
                                dir=str(Path.home())) as directory:
            os.environ["TS_R3_A02_PRIVATE_RECEIPT_DIR"] = directory
            target = private_receipt_dir()
            with patch("a02_lan.lan_probe.linux_mount_type", return_value="tmpfs"):
                try:
                    private_receipt_dir()
                except AssertionError as exc:
                    require(str(exc) == "RECEIPT_FS_NOT_DURABLE_EXT4",
                            "VOLATILE_TMPFS_REJECTION_WRONG_CODE")
                    receipt_negatives += 1
                else:
                    raise AssertionError("VOLATILE_TMPFS_RECEIPT_ACCEPTED")
            target.chmod(0o755)
            try:
                private_receipt_dir()
            except AssertionError as exc:
                require(str(exc) == "RECEIPT_DIR_NOT_PRIVATE_0700",
                        "WORLD_READABLE_RECEIPT_REJECTION_WRONG_CODE")
                receipt_negatives += 1
            else:
                raise AssertionError("WORLD_READABLE_RECEIPT_ACCEPTED")
            finally:
                target.chmod(0o700)
            # Source-native test of original-intent creation and duplicate fence.
            record = {"product_effect": "NONE", "phase": "SOURCE_ONLY_TEST"}
            write_once_receipt(target, "writer-a.intent.json", record)
            require((target / "writer-a.intent.json").is_file(),
                    "CREATE_ONLY_INTENT_NOT_WRITTEN")
            try:
                write_once_receipt(target, "writer-a.intent.json", record)
            except FileExistsError:
                receipt_negatives += 1
            else:
                raise AssertionError("DUPLICATE_WRITER_INTENT_ACCEPTED")
            # DDL and GENESIS are distinct create-only original effects.
            setup_intent = {"product_effect": "NONE", "phase": "SOURCE_ONLY_TEST"}
            write_once_receipt(target, "setup-ddl.intent.json", setup_intent)
            write_once_receipt(target, "setup-genesis.intent.json", setup_intent)
            try:
                write_once_receipt(target, "setup-ddl.intent.json", setup_intent)
            except FileExistsError:
                receipt_negatives += 1
            else:
                raise AssertionError("DUPLICATE_DDL_DISPATCH_ACCEPTED")
            try:
                write_once_receipt(target, "setup-foreign.intent.json", setup_intent)
            except AssertionError as exc:
                require(str(exc) == "RECEIPT_UNEXPECTED_NAME",
                        "FOREIGN_SETUP_EFFECT_WRONG_GUARD")
                receipt_negatives += 1
            else:
                raise AssertionError("FOREIGN_SETUP_EFFECT_ACCEPTED")
    finally:
        os.environ.pop("TS_R3_A02_PRIVATE_RECEIPT_DIR", None)
        if previous_dir is not None:
            os.environ["TS_R3_A02_PRIVATE_RECEIPT_DIR"] = previous_dir
    require(receipt_negatives == 6, "CREATE_ONLY_RECEIPT_GUARDS_FAILED")
    print(json.dumps({
        "status": "A02_LAN_SOURCE_ONLY_NEGATIVES_PASS",
        "original_js_pair": True,
        "negative_cases": observed,
        "additional_preflight_negatives": 2,
        "additional_receipt_negatives": receipt_negatives,
        "durable_original_writer_intent_guard": "PASS",
        "immutable_schema_pin": "PASS",
        "host_attestation_source_guard": "PASS",
        "foreign_public_object_rejected": True,
        "artifact_sha256": sha256(original).hexdigest(),
        "python": ".".join(map(str, sys.version_info[:3])),
        "postgresql": "NOT_RUN",
        "neon": "NOT_RUN",
        "product_effect": "NONE",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
