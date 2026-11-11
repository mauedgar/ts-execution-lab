"""No-DB/No-network negative qualification of distinct A02 bootstrap/writer roles."""
from __future__ import annotations

import json
from a02_lan.role_boundary import (
    DATABASE, OWNER_ROLE, WRITER_ROLE, SCHEMA, role_for_mode,
    assert_writer_boundary,
)

TABLE_REQUIRED = {
    "head": {"SELECT", "UPDATE"},
    "events": {"SELECT", "INSERT"},
    "receipts": {"SELECT", "INSERT"},
}
ALL_ACTIONS = {"SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE",
               "REFERENCES", "TRIGGER"}


class Result:
    def __init__(self, data):
        self.data = data

    def fetchone(self):
        return self.data

    def fetchall(self):
        return self.data


class FakeConn:
    """Exact SQL-shape aware synthetic effective privileges."""
    def __init__(self):
        self.role = WRITER_ROLE
        self.flags = {"rolsuper": False, "rolcreaterole": False,
                      "rolcreatedb": False, "rolreplication": False,
                      "rolbypassrls": False, "rolcanlogin": True}
        self.parents = []
        self.db = {"connect": True, "create": False, "temp": False}
        self.schema = {"usage": True, "create": False}
        self.grants = {t: set(v) for t, v in TABLE_REQUIRED.items()}
        self.statements = []

    def execute(self, sql, params=None):
        assert sql.startswith("SELECT "), "UNEXPECTED_SQL_MUTATION"
        self.statements.append((sql, params))
        if "pg_catalog.pg_roles WHERE rolname=current_user" in sql and "rolsuper" in sql:
            return Result({"rolname":self.role, **self.flags})
        if "pg_catalog.pg_auth_members" in sql:
            return Result([{"parent":v} for v in self.parents])
        if "has_database_privilege(" in sql:
            assert params == (DATABASE, DATABASE, DATABASE)
            return Result(self.db)
        if "has_schema_privilege(" in sql:
            assert params == (SCHEMA, SCHEMA)
            return Result(self.schema)
        if "has_table_privilege(" in sql:
            rel, privilege = params
            assert rel.startswith(SCHEMA + ".") and privilege in ALL_ACTIONS
            return Result({"allowed": privilege in self.grants[rel.split(".")[-1]]})
        raise AssertionError("UNEXPECTED_FAKE_SQL")


def rejects(conn, expected):
    try:
        assert_writer_boundary(conn)
    except AssertionError as exc:
        assert str(exc) == expected, (str(exc), expected)
        return 1
    raise AssertionError("UNSAFE_PROFILE_ACCEPTED:" + expected)


def main():
    assert OWNER_ROLE != WRITER_ROLE
    assert role_for_mode("setup", "NOTEBOOK") == OWNER_ROLE
    assert role_for_mode("reconcile-ddl", "NOTEBOOK") == OWNER_ROLE
    assert role_for_mode("reconcile-genesis", "NOTEBOOK") == OWNER_ROLE
    for mode in ("hold", "writer-a", "writer-b", "witness", "verify",
                 "reconcile-a", "reconcile-b"):
        for site in ("NOTEBOOK", "DESKTOP"):
            assert role_for_mode(mode, site) == WRITER_ROLE
    for mode,site,expected in (("setup","DESKTOP","BOOTSTRAP_NOTEBOOK_ONLY"),
                               ("foreign","NOTEBOOK","ROLE_MODE_NOT_ADMITTED"),
                               ("writer-a","OTHER","EXACT_PHYSICAL_SITE_REQUIRED")):
        try:
            role_for_mode(mode,site)
        except AssertionError as exc:
            assert str(exc) == expected
        else:
            raise AssertionError("UNSAFE_ROLE_MODE_ACCEPTED")

    positive = FakeConn()
    assert_writer_boundary(positive)
    assert len(positive.statements) >= 25
    negatives = 0
    for key in ("rolsuper", "rolcreaterole", "rolcreatedb", "rolreplication",
                "rolbypassrls"):
        f = FakeConn()
        f.flags[key] = True
        negatives += rejects(f, "PRIVILEGED_WRITER_REJECTED")
    f = FakeConn()
    f.role = OWNER_ROLE
    negatives += rejects(f, "PRIVILEGED_WRITER_REJECTED")
    f = FakeConn()
    f.flags["rolcanlogin"] = False
    negatives += rejects(f, "PRIVILEGED_WRITER_REJECTED")
    for parent in (OWNER_ROLE, "pg_read_all_data", "pg_write_all_data"):
        f = FakeConn()
        f.parents = [parent]
        negatives += rejects(f, "WRITER_ROLE_MEMBERSHIP_FORBIDDEN")
    for key,val in (("connect",False),("create",True),("temp",True)):
        f = FakeConn()
        f.db[key] = val
        negatives += rejects(f, "WRITER_DATABASE_PRIVILEGES_INVALID")
    for key,val in (("usage",False),("create",True)):
        f = FakeConn()
        f.schema[key] = val
        negatives += rejects(f, "WRITER_SCHEMA_PRIVILEGES_INVALID")
    for table,required in TABLE_REQUIRED.items():
        for privilege in required:
            f = FakeConn()
            f.grants[table].remove(privilege)
            negatives += rejects(f, "WRITER_TABLE_GRANT_INVALID_" +
                                 table.upper() + "_" + privilege)
        for privilege in ALL_ACTIONS - required:
            f = FakeConn()
            f.grants[table].add(privilege)
            negatives += rejects(f, "WRITER_TABLE_GRANT_INVALID_" +
                                 table.upper() + "_" + privilege)
    assert negatives == 34, negatives
    print(json.dumps({
        "status": "A02_LAN_SOURCE_ONLY_ROLE_BOUNDARY_PASS",
        "positive_profiles": 1, "negative_profiles": negatives,
        "postgresql": "NOT_RUN", "writer_effect": "NONE",
        "product_effect": "NONE", "role_ddl": "NOT_RUN",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
