"""Nonproduct source-only setup DDL/genesis receipt/reconciliation negative tests.

Fake SQL connection has SELECT/SET READ ONLY only. Never touches actual PostgreSQL.
No Product or Neon credentials. Exact original effect IDs are preserved.
"""
from __future__ import annotations

from contextlib import nullcontext
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from a02_lan import lan_probe as p
from ts_global.bridge import StorageRejected


class Row:
    def __init__(self, data):
        self.data = data
    def fetchone(self):
        return self.data
    def fetchall(self):
        return self.data


class ReadOnlyFakeConnection:
    def __init__(self, marker):
        self.marker = marker
        self.statements = []
    def transaction(self):
        return nullcontext()
    def execute(self, sql, params=None):
        self.statements.append(sql)
        if sql == "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY":
            return Row(None)
        if "obj_description(" in sql:
            return Row({"marker": self.marker} if self.marker is not None else None)
        if "SELECT tablename, tableowner" in sql:
            return Row([{"tablename":name, "tableowner":p.ROLE}
                        for name in ("events", "head", "receipts")])
        if "c.relkind IN" in sql and "SELECT count(*)" in sql:
            return Row({"n":0})
        raise AssertionError("UNEXPECTED_SQL_IN_SOURCE_ONLY_FAKE")
    def assert_read_only(self):
        assert all(q.startswith("SELECT ") or q.startswith(
            "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
                   for q in self.statements)


def main():
    old = {key:os.environ.get(key) for key in (
        "TS_R3_A02_EXECUTION_ATTEMPT", "TS_R3_A02_EXPECTED_HOST_SHA256",
        "TS_R3_A02_EXPECTED_SYSTEM_IDENTIFIER", p.SHA_ENV, p.RECEIPT_DIR_ENV)}
    host = sha256(platform.node().strip().casefold().encode()).hexdigest()
    os.environ.update({
        "TS_R3_A02_EXECUTION_ATTEMPT":
            "TS-R3-A02-LAN-PHYSICAL-RACE-20261109-001-A001",
        "TS_R3_A02_EXPECTED_HOST_SHA256":host,
        "TS_R3_A02_EXPECTED_SYSTEM_IDENTIFIER":"12345678901234567890",
        p.SHA_ENV:"e"*64,
    })
    negatives = 0
    try:
        with TemporaryDirectory(prefix="ts-r3-a02-lan-physical-race-",
                                dir=str(Path.home())) as directory:
            os.environ[p.RECEIPT_DIR_ENV] = directory
            folder = p.private_receipt_dir()
            for phase,effect_id in (("ddl",p.SETUP_DDL_EFFECT),
                                    ("genesis",p.SETUP_GENESIS_EFFECT)):
                base = p.setup_effect_record(effect_id)
                p.write_once_receipt(
                    folder,"setup-"+phase+".intent.json",
                    {**base, "phase":"BEFORE_FIRST_DISPATCH",
                     "effect":"UNKNOWN_PENDING","created_ns":1794260000000000000})
            c = ReadOnlyFakeConnection(p.FROZEN_SCHEMA_COMMENT)
            d = p.reconcile_setup(c,b"frozen_original_genesis","ddl")
            assert d["effect"] == "CONFIRMED_PENDING_PROVIDER_REVIEW"
            assert d["redispatched"] is False
            c.assert_read_only()
            with patch.object(p,"read",return_value=SimpleNamespace(
                    revision=0,state_bytes=b"frozen_original_genesis",
                    event_bytes=b"")):
                g = p.reconcile_setup(c,b"frozen_original_genesis","genesis")
            assert g["effect"] == "CONFIRMED_PENDING_PROVIDER_REVIEW"
            assert g["redispatched"] is False
            c.assert_read_only()
            absent = ReadOnlyFakeConnection(None)
            x = p.reconcile_setup(absent,b"frozen_original_genesis","ddl")
            assert x["effect"] == "UNKNOWN"
            absent.assert_read_only()
            negatives += 1
            with patch.object(p,"read",side_effect=StorageRejected("UNINITIALIZED")):
                g = p.reconcile_setup(c,b"frozen_original_genesis","genesis")
            assert g["effect"] == "UNKNOWN"
            negatives += 1
            forged = folder / "setup-ddl.intent.json"
            data = json.loads(forged.read_text("utf-8"))
            data["original_effect_id"] = "FOREIGN_EFFECT"
            forged.write_text(json.dumps(data)+"\n",encoding="utf-8")
            try:
                p.read_original_setup_intent(folder,"ddl")
            except AssertionError as exc:
                assert str(exc) == "ORIGINAL_SETUP_INTENT_MISMATCH"
                negatives += 1
            else:
                raise AssertionError("FORGED_SETUP_INTENT_ACCEPTED")
            wrong = ReadOnlyFakeConnection("FOREIGN_SCHEMA_MARKER")
            try:
                p.ddl_comment_readonly(wrong)
            except AssertionError as exc:
                assert str(exc) == "UNEXPECTED_DDL_MARKER"
                negatives += 1
            else:
                raise AssertionError("FOREIGN_SCHEMA_MARKER_ACCEPTED")
            assert negatives == 4
    finally:
        for key,val in old.items():
            if val is None:
                os.environ.pop(key,None)
            else:
                os.environ[key] = val
    print(json.dumps({
        "status":"A02_LAN_SETUP_SEPARATE_EFFECT_READONLY_SOURCE_PASS",
        "negative_cases":negatives,
        "source_only":True,"postgresql":"NOT_RUN","product_effect":"NONE",
    },sort_keys=True))


if __name__ == "__main__":
    main()
