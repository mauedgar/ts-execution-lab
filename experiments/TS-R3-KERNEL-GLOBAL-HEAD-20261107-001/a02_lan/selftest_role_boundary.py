"""IR001 F01-F03/A01-A02 source-only role/catalog/connect negative tests.

Includes fake psycopg dict_row-shaped queries and real lan_probe.connect()
boundary, with psycopg.connect intercepted. NO real DB, role, SQL or network.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from a02_lan import lan_probe as lan
from a02_lan.role_boundary import (
    DATABASE, OWNER_ROLE, WRITER_ROLE, SCHEMA, role_for_mode,
    assert_writer_boundary, assert_synthetic_catalog,
)

TABLE_REQUIRED = {
    "head": {"SELECT", "UPDATE"},
    "events": {"SELECT", "INSERT"},
    "receipts": {"SELECT", "INSERT"},
}
ALL_ACTIONS = {"SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE",
               "REFERENCES", "TRIGGER"}
EXPECTED_OBJECTS = [{"schema": SCHEMA, "name": n, "kind": "r",
                     "owner": OWNER_ROLE} for n in ("events", "head", "receipts")]


class Result:
    def __init__(self, data):
        self.data = data

    def fetchone(self):
        return self.data

    def fetchall(self):
        return self.data


class FakeConn:
    def __init__(self):
        self.role = WRITER_ROLE
        self.flags = {"rolsuper": False, "rolcreaterole": False,
                      "rolcreatedb": False, "rolreplication": False,
                      "rolbypassrls": False, "rolcanlogin": True,
                      "rolinherit": False}
        self.parents = []
        self.db = {"connect": True, "create": False, "temp": False,
                   "grant_connect": False}
        self.schema = {"usage": True, "create": False, "grant_usage": False}
        self.grants = {t: set(v) for t,v in TABLE_REQUIRED.items()}
        self.grant_options = {t:set() for t in TABLE_REQUIRED}
        self.schemas = [{"nspname":"public"},{"nspname":SCHEMA}]
        self.objects = [dict(v) for v in EXPECTED_OBJECTS]
        self.functions = []
        self.column_acl = []
        self.roles = [{"rolname":OWNER_ROLE},{"rolname":WRITER_ROLE},
                      {"rolname":"postgres"}]
        self.databases = [{"datname":"postgres"},{"datname":DATABASE}]
        self.extensions = [{"extname":"plpgsql"}]
        self.control = {"allowed":True,"grant_option":False}
        self.system_id = "7706270612558725155"
        self.statements = []
        self.closed = False

    def close(self):
        self.closed = True

    def execute(self, sql, params=None):
        assert sql.startswith(("SELECT ", "SHOW ")), "FAKE_DISALLOWS_SQL_MUTATION"
        self.statements.append((sql, params))
        if sql == "SHOW server_version":
            return Result({"server_version":"16.15"})
        if "pg_catalog.pg_database d WHERE d.datname=current_database()" in sql:
            return Result({"db":DATABASE,"role":self.role,
                           "session_role":self.role,"db_owner":OWNER_ROLE,
                           "template":False})
        if "SELECT system_identifier::text AS id" in sql:
            return Result({"id":self.system_id})
        if "pg_catalog.pg_roles WHERE rolname=current_user" in sql and "rolsuper" in sql:
            return Result({"rolname":self.role, **self.flags})
        if "pg_catalog.pg_auth_members" in sql:
            return Result([{"parent":v} for v in self.parents])
        if "has_database_privilege(" in sql:
            assert params == (DATABASE,)*4, params
            return Result(self.db)
        if "has_schema_privilege(" in sql:
            assert params == (SCHEMA,)*3, params
            return Result(self.schema)
        if "SELECT nspname FROM pg_catalog.pg_namespace" in sql:
            return Result(self.schemas)
        if "FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n" in sql:
            assert params == (SCHEMA,)
            return Result(self.objects)
        if "FROM pg_catalog.pg_proc p" in sql:
            assert params == (SCHEMA,)
            return Result(self.functions)
        if "FROM pg_catalog.pg_attribute a" in sql:
            assert params == (SCHEMA,)
            return Result(self.column_acl)
        if "SELECT rolname FROM pg_catalog.pg_roles" in sql:
            return Result(self.roles)
        if "SELECT datname FROM pg_catalog.pg_database" in sql:
            return Result(self.databases)
        if "SELECT extname FROM pg_catalog.pg_extension" in sql:
            return Result(self.extensions)
        if "has_table_privilege(" in sql:
            rel, privilege = params
            assert rel.startswith(SCHEMA + ".")
            table = rel.split(".")[-1]
            is_grant = privilege.endswith(" WITH GRANT OPTION")
            p = privilege.removesuffix(" WITH GRANT OPTION")
            assert p in ALL_ACTIONS, p
            allowed = p in (self.grant_options if is_grant else self.grants)[table]
            return Result({"allowed":allowed})
        if "has_function_privilege(" in sql:
            assert params == ("pg_catalog.pg_control_system()",)*2
            return Result(self.control)
        raise AssertionError("UNEXPECTED_FAKE_SQL:" + sql)


def rejects(conn, expected):
    try:
        assert_writer_boundary(conn)
    except AssertionError as exc:
        assert str(exc) == expected, (str(exc), expected)
        return 1
    raise AssertionError("UNSAFE_PROFILE_ACCEPTED:" + expected)


def main():
    assert OWNER_ROLE != WRITER_ROLE
    for mode in ("setup","reconcile-ddl","reconcile-genesis","witness"):
        assert role_for_mode(mode,"NOTEBOOK") == OWNER_ROLE
    for mode in ("hold","writer-a","writer-b","verify","reconcile-a","reconcile-b"):
        for site in ("NOTEBOOK","DESKTOP"):
            assert role_for_mode(mode,site) == WRITER_ROLE
    for mode,site,expected in (
        ("setup","DESKTOP","CONTROL_BOOTSTRAP_NOTEBOOK_ONLY"),
        ("witness","DESKTOP","CONTROL_BOOTSTRAP_NOTEBOOK_ONLY"),
        ("foreign","NOTEBOOK","ROLE_MODE_NOT_ADMITTED"),
        ("writer-a","OTHER","EXACT_PHYSICAL_SITE_REQUIRED"),
    ):
        try:
            role_for_mode(mode,site)
        except AssertionError as exc:
            assert str(exc) == expected
        else:
            raise AssertionError("UNSAFE_ROLE_MODE_ACCEPTED")

    positive = FakeConn()
    assert_writer_boundary(positive)
    assert len(positive.statements) == 54
    negatives=0
    for key in ("rolsuper","rolcreaterole","rolcreatedb","rolreplication",
                "rolbypassrls","rolinherit"):
        f=FakeConn(); f.flags[key]=True
        negatives+=rejects(f,"PRIVILEGED_WRITER_REJECTED")
    f=FakeConn(); f.role=OWNER_ROLE
    negatives+=rejects(f,"PRIVILEGED_WRITER_REJECTED")
    f=FakeConn(); f.flags["rolcanlogin"]=False
    negatives+=rejects(f,"PRIVILEGED_WRITER_REJECTED")
    for parent in (OWNER_ROLE,"pg_read_all_data","pg_write_all_data"):
        f=FakeConn();f.parents=[parent]
        negatives+=rejects(f,"WRITER_ROLE_MEMBERSHIP_FORBIDDEN")
    for key,val in (("connect",False),("create",True),
                    ("temp",True),("grant_connect",True)):
        f=FakeConn();f.db[key]=val
        negatives+=rejects(f,"WRITER_DATABASE_PRIVILEGES_INVALID")
    for key,val in (("usage",False),("create",True),("grant_usage",True)):
        f=FakeConn();f.schema[key]=val
        negatives+=rejects(f,"WRITER_SCHEMA_PRIVILEGES_INVALID")

    catalog_cases = (
        ("WRITER_FOREIGN_USER_SCHEMA", lambda f: f.schemas.append({"nspname":"foreign"})),
        ("WRITER_FOREIGN_OBJECT_OR_OWNER",
         lambda f: f.objects.append({"schema":"public","name":"other",
                                     "kind":"r","owner":OWNER_ROLE})),
        ("WRITER_FOREIGN_USER_FUNCTION",
         lambda f: f.functions.append({"schema":"public","name":"unsafe"})),
        ("WRITER_COLUMN_LEVEL_GRANT_PRESENT",
         lambda f: f.column_acl.append({"name":"events","column_name":"scope","acl":"x"})),
        ("WRITER_FOREIGN_CLUSTER_ROLE",
         lambda f: f.roles.append({"rolname":"foreign"})),
        ("WRITER_FOREIGN_DATABASE",
         lambda f: f.databases.append({"datname":"foreign"})),
        ("WRITER_FOREIGN_EXTENSION",
         lambda f: f.extensions.append({"extname":"foreign"})),
    )
    for code,mutator in catalog_cases:
        f=FakeConn();mutator(f)
        negatives+=rejects(f,code)

    for table,required in TABLE_REQUIRED.items():
        for privilege in required:
            f=FakeConn();f.grants[table].remove(privilege)
            negatives+=rejects(f, "WRITER_TABLE_GRANT_INVALID_" +
                                table.upper()+"_"+privilege)
        for privilege in ALL_ACTIONS-required:
            f=FakeConn();f.grants[table].add(privilege)
            negatives+=rejects(f, "WRITER_TABLE_GRANT_INVALID_" +
                                table.upper()+"_"+privilege)
        for privilege in ALL_ACTIONS:
            f=FakeConn();f.grant_options[table].add(privilege)
            negatives+=rejects(f, "WRITER_GRANT_OPTION_FORBIDDEN_" +
                                table.upper()+"_"+privilege)

    f=FakeConn();f.control["allowed"]=False
    negatives+=rejects(f,"CONTROL_SYSTEM_FUNCTION_ACCESS_NOT_ATTESTED")
    f=FakeConn();f.control["grant_option"]=True
    negatives+=rejects(f,"CONTROL_SYSTEM_FUNCTION_ACCESS_NOT_ATTESTED")
    assert negatives == 69, negatives

    # Integration boundary: real lan_probe.site_uri + connect + runtime preflight
    # under patched psycopg.connect. No network/SQL beyond FakeConn.execute.
    previous={key:os.environ.get(key) for key in (
        lan.URI_ENV,"TS_R3_A02_SITE","TS_R3_A02_EXPECTED_HOST_SHA256",
        "TS_R3_A02_EXPECTED_SYSTEM_IDENTIFIER","TS_R3_A02_EXECUTION_ATTEMPT",
    )}
    host=sha256(platform.node().strip().casefold().encode("utf-8")).hexdigest()
    os.environ.update({
        "TS_R3_A02_SITE":"NOTEBOOK",
        "TS_R3_A02_EXPECTED_HOST_SHA256":host,
        "TS_R3_A02_EXPECTED_SYSTEM_IDENTIFIER":"7706270612558725155",
        "TS_R3_A02_EXECUTION_ATTEMPT":
            "TS-R3-A02-LAN-PHYSICAL-RACE-20261109-001-A001",
    })
    def uri(role):
        return ("postgresql://"+role+":not-a-real-synthetic-credential-32"
                "@127.0.0.1:55433/"+DATABASE+"?sslmode=disable")
    try:
        os.environ[lan.URI_ENV]=uri(WRITER_ROLE)
        good=FakeConn()
        with patch.object(lan.psycopg,"connect",return_value=good) as mock:
            conn,site=lan.connect("writer-a")
            assert conn is good and site=="NOTEBOOK" and not conn.closed
            mock.assert_called_once()
        restricted=FakeConn();restricted.control["allowed"]=False
        with patch.object(lan.psycopg,"connect",return_value=restricted):
            try:
                lan.connect("writer-a")
            except AssertionError as exc:
                assert str(exc)=="CONTROL_SYSTEM_FUNCTION_ACCESS_NOT_ATTESTED"
                assert restricted.closed
            else:
                raise AssertionError("UNQUALIFIED_CONTROL_FUNCTION_ACCEPTED")
        os.environ[lan.URI_ENV]=uri(OWNER_ROLE)
        owner=FakeConn();owner.role=OWNER_ROLE
        with patch.object(lan.psycopg,"connect",return_value=owner):
            conn,site=lan.connect("witness")
            assert conn is owner and site=="NOTEBOOK"
        os.environ["TS_R3_A02_SITE"]="DESKTOP"
        try:
            lan.site_uri("witness")
        except AssertionError as exc:
            assert str(exc)=="CONTROL_BOOTSTRAP_NOTEBOOK_ONLY"
        else:
            raise AssertionError("REMOTE_CONTROL_WITNESS_ACCEPTED")
    finally:
        for key,val in previous.items():
            if val is None:
                os.environ.pop(key,None)
            else:
                os.environ[key]=val
    print(json.dumps({
        "status":"A02_LAN_IR001_SOURCE_REPAIR_NEGATIVES_PASS",
        "positive_profiles":1,"negative_profiles":negatives,
        "mocked_lan_connect":"PASS",
        "postgresql":"NOT_RUN","sql_mutation":"NONE",
        "role_ddl":"NOT_RUN","neon":"NOT_RUN","product_effect":"NONE",
    },sort_keys=True))


if __name__=="__main__":
    main()
