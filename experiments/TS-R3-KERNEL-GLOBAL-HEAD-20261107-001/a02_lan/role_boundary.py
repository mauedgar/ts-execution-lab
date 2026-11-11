"""NONPRODUCT A02-LAN source-only role boundary; no role or SQL mutations.

The original bootstrap owner is *not* a writer credential. Missing effective
privilege proof fails closed; no fallback to bootstrap, superuser or SET ROLE.
PostgreSQL role catalog and table ACL observations alone do not attest a host.
"""
from __future__ import annotations

OWNER_ROLE = "tsr3_a02_lab"
WRITER_ROLE = "tsr3_a02_writer"
DATABASE = "tsr3_a02_lab"
SCHEMA = "ts_r3_global_head_20261107_001"
OWNER_MODES = frozenset(("setup", "reconcile-ddl", "reconcile-genesis"))
WRITER_MODES = frozenset(("hold", "writer-a", "writer-b",
                          "witness", "verify", "reconcile-a", "reconcile-b"))
# SELECT FOR UPDATE requires UPDATE in addition to SELECT. Writers never need
# DELETE, TRUNCATE, REFERENCES, TRIGGER, DDL, TEMP, or ownership.
_TABLE_REQUIRED = {
    "head": frozenset(("SELECT", "UPDATE")),
    "events": frozenset(("SELECT", "INSERT")),
    "receipts": frozenset(("SELECT", "INSERT")),
}
_TABLE_DENIED = frozenset(("DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"))


def require(ok: bool, code: str) -> None:
    if not ok:
        raise AssertionError(code)


def role_for_mode(mode: str, site: str) -> str:
    require(site in ("NOTEBOOK", "DESKTOP"), "EXACT_PHYSICAL_SITE_REQUIRED")
    if mode in OWNER_MODES:
        require(site == "NOTEBOOK", "BOOTSTRAP_NOTEBOOK_ONLY")
        return OWNER_ROLE
    require(mode in WRITER_MODES, "ROLE_MODE_NOT_ADMITTED")
    return WRITER_ROLE


def assert_writer_boundary(conn) -> None:
    """Verify *effective* grants and role properties before any writer effect.

    The current experiment assumes the synthetic lab is a dedicated database.
    Fresh catalog/server and native two-host proofs remain separate gates.
    """
    row = conn.execute(
        "SELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolreplication, "
        "rolbypassrls, rolcanlogin FROM pg_catalog.pg_roles WHERE rolname=current_user"
    ).fetchone()
    require(type(row) is dict and set(row) == {
        "rolname", "rolsuper", "rolcreaterole", "rolcreatedb",
        "rolreplication", "rolbypassrls", "rolcanlogin"
    }, "ROLE_PROPERTIES_NOT_ATTESTED")
    require(row["rolname"] == WRITER_ROLE and row["rolcanlogin"] is True and
            all(row[k] is False for k in (
                "rolsuper", "rolcreaterole", "rolcreatedb",
                "rolreplication", "rolbypassrls")), "PRIVILEGED_WRITER_REJECTED")
    # Deny ALL direct memberships, including admin and predefined pg_* roles.
    # A role with zero direct parents cannot inherit a transitive parent.
    parents = conn.execute(
        "SELECT roleid::regrole::text AS parent FROM pg_catalog.pg_auth_members "
        "WHERE member=(SELECT oid FROM pg_catalog.pg_roles "
        "WHERE rolname=current_user)"
    ).fetchall()
    require(type(parents) is list and len(parents) == 0,
            "WRITER_ROLE_MEMBERSHIP_FORBIDDEN")

    db = conn.execute(
        "SELECT has_database_privilege(current_user,%s,'CONNECT') AS connect, "
        "has_database_privilege(current_user,%s,'CREATE') AS create, "
        "has_database_privilege(current_user,%s,'TEMP') AS temp",
        (DATABASE, DATABASE, DATABASE),
    ).fetchone()
    require(db == {"connect": True, "create": False, "temp": False},
            "WRITER_DATABASE_PRIVILEGES_INVALID")
    schema = conn.execute(
        "SELECT has_schema_privilege(current_user,%s,'USAGE') AS usage, "
        "has_schema_privilege(current_user,%s,'CREATE') AS create",
        (SCHEMA, SCHEMA),
    ).fetchone()
    require(schema == {"usage": True, "create": False},
            "WRITER_SCHEMA_PRIVILEGES_INVALID")

    for table, required in _TABLE_REQUIRED.items():
        rel = SCHEMA + "." + table
        for privilege in sorted(required | _TABLE_DENIED |
                                frozenset(("SELECT", "INSERT", "UPDATE"))):
            value = conn.execute(
                "SELECT has_table_privilege(current_user,%s,%s) AS allowed",
                (rel, privilege),
            ).fetchone()
            require(type(value) is dict and
                    value == {"allowed": privilege in required},
                    "WRITER_TABLE_GRANT_INVALID_" + table.upper() +
                    "_" + privilege)
    # No SQL mutation in this function. No claim about authenticated remote
    # transport, non-Product server identity, or independent host provenance.
