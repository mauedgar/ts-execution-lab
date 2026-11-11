"""NONPRODUCT source-only PG16 security boundary, no SQL/role/host mutations.

Post-IR001 repair: separate Control witness from A/B writers, fail closed on
unexpected user objects, explicit column ACLs, grant options, and pg_control
EXECUTE privilege. This cannot replace independently verified physical
PostgreSQL roles, cluster identity, ACL/Tailnet, original effects or IR.
"""
from __future__ import annotations

OWNER_ROLE = "tsr3_a02_lab"
WRITER_ROLE = "tsr3_a02_writer"
DATABASE = "tsr3_a02_lab"
SCHEMA = "ts_r3_global_head_20261107_001"
# Witness is local Control observation, never an A/B writer or remote credential.
OWNER_MODES = frozenset(("setup", "reconcile-ddl", "reconcile-genesis", "witness"))
WRITER_MODES = frozenset(("hold", "writer-a", "writer-b",
                          "verify", "reconcile-a", "reconcile-b"))
_TABLE_REQUIRED = {
    "head": frozenset(("SELECT", "UPDATE")),
    "events": frozenset(("SELECT", "INSERT")),
    "receipts": frozenset(("SELECT", "INSERT")),
}
_TABLE_ACTIONS = frozenset(("SELECT", "INSERT", "UPDATE", "DELETE",
                            "TRUNCATE", "REFERENCES", "TRIGGER"))


def require(ok: bool, code: str) -> None:
    if not ok:
        raise AssertionError(code)


def role_for_mode(mode: str, site: str) -> str:
    require(site in ("NOTEBOOK", "DESKTOP"), "EXACT_PHYSICAL_SITE_REQUIRED")
    if mode in OWNER_MODES:
        require(site == "NOTEBOOK", "CONTROL_BOOTSTRAP_NOTEBOOK_ONLY")
        return OWNER_ROLE
    require(mode in WRITER_MODES, "ROLE_MODE_NOT_ADMITTED")
    return WRITER_ROLE


def assert_synthetic_catalog(conn) -> None:
    """Require a virgin synthetic-only database before accepting writer access.

    This is *current DB* catalog footprint only, not cross-database security,
    authenticated remote host proof, owner role creation or runtime admission.
    """
    schemas = conn.execute(
        "SELECT nspname FROM pg_catalog.pg_namespace "
        "WHERE nspname <> 'information_schema' "
        "AND nspname NOT LIKE 'pg\\_%' ESCAPE '\\' ORDER BY nspname"
    ).fetchall()
    require(type(schemas) is list and
            [r["nspname"] for r in schemas] == ["public", SCHEMA],
            "WRITER_FOREIGN_USER_SCHEMA")

    objects = conn.execute(
        "SELECT n.nspname AS schema, c.relname AS name, c.relkind AS kind, "
        "pg_catalog.pg_get_userbyid(c.relowner) AS owner "
        "FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n "
        "ON n.oid=c.relnamespace "
        "WHERE n.nspname IN ('public',%s) "
        "AND c.relkind IN ('r','p','v','m','f','S') "
        "ORDER BY n.nspname,c.relname", (SCHEMA,)
    ).fetchall()
    expected = [{"schema": SCHEMA, "name": n, "kind": "r",
                 "owner": OWNER_ROLE} for n in ("events", "head", "receipts")]
    require(objects == expected, "WRITER_FOREIGN_OBJECT_OR_OWNER")

    funcs = conn.execute(
        "SELECT n.nspname AS schema, p.proname AS name FROM pg_catalog.pg_proc p "
        "JOIN pg_catalog.pg_namespace n ON n.oid=p.pronamespace "
        "WHERE n.nspname IN ('public',%s)", (SCHEMA,)
    ).fetchall()
    require(funcs == [], "WRITER_FOREIGN_USER_FUNCTION")

    column_acl = conn.execute(
        "SELECT c.relname AS name,a.attname AS column_name,a.attacl::text AS acl "
        "FROM pg_catalog.pg_attribute a "
        "JOIN pg_catalog.pg_class c ON c.oid=a.attrelid "
        "JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace "
        "WHERE n.nspname=%s AND c.relkind IN ('r','p') "
        "AND a.attnum>0 AND NOT a.attisdropped AND a.attacl IS NOT NULL",
        (SCHEMA,)
    ).fetchall()
    require(column_acl == [], "WRITER_COLUMN_LEVEL_GRANT_PRESENT")

    roles = conn.execute(
        "SELECT rolname FROM pg_catalog.pg_roles "
        "WHERE rolname NOT LIKE 'pg\\_%' ESCAPE '\\' ORDER BY rolname"
    ).fetchall()
    require(type(roles) is list and set(r["rolname"] for r in roles) in (
            {OWNER_ROLE, WRITER_ROLE}, {OWNER_ROLE, WRITER_ROLE, "postgres"}) and
            len(roles) == len(set(r["rolname"] for r in roles)),
            "WRITER_FOREIGN_CLUSTER_ROLE")
    databases = conn.execute(
        "SELECT datname FROM pg_catalog.pg_database "
        "WHERE NOT datistemplate ORDER BY datname"
    ).fetchall()
    require(databases == [{"datname": "postgres"}, {"datname": DATABASE}],
            "WRITER_FOREIGN_DATABASE")
    extensions = conn.execute(
        "SELECT extname FROM pg_catalog.pg_extension ORDER BY extname"
    ).fetchall()
    require(extensions == [{"extname": "plpgsql"}],
            "WRITER_FOREIGN_EXTENSION")


def assert_writer_boundary(conn) -> None:
    """Enforce a bounded effective-ACL profile for an isolated PG16 lab.

    PRIVILEGE_METADATA is evaluated before any A/B write or holder; missing,
    unexpected, inherited or excessive privileges fail closed. SOURCE_ONLY
    mocks do not prove real PG16 permissions: native Control must separately
    attest grants, physical host, original effect, cluster and role provisioning.
    """
    row = conn.execute(
        "SELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolreplication, "
        "rolbypassrls, rolcanlogin, rolinherit "
        "FROM pg_catalog.pg_roles WHERE rolname=current_user"
    ).fetchone()
    require(type(row) is dict and set(row) == {
        "rolname", "rolsuper", "rolcreaterole", "rolcreatedb",
        "rolreplication", "rolbypassrls", "rolcanlogin", "rolinherit"
    }, "ROLE_PROPERTIES_NOT_ATTESTED")
    require(row["rolname"] == WRITER_ROLE and row["rolcanlogin"] is True and
            all(row[k] is False for k in (
                "rolsuper", "rolcreaterole", "rolcreatedb",
                "rolreplication", "rolbypassrls", "rolinherit")),
            "PRIVILEGED_WRITER_REJECTED")
    parents = conn.execute(
        "SELECT roleid::regrole::text AS parent FROM pg_catalog.pg_auth_members "
        "WHERE member=(SELECT oid FROM pg_catalog.pg_roles "
        "WHERE rolname=current_user)"
    ).fetchall()
    require(type(parents) is list and parents == [],
            "WRITER_ROLE_MEMBERSHIP_FORBIDDEN")

    db = conn.execute(
        "SELECT has_database_privilege(current_user,%s,'CONNECT') AS connect, "
        "has_database_privilege(current_user,%s,'CREATE') AS create, "
        "has_database_privilege(current_user,%s,'TEMP') AS temp, "
        "has_database_privilege(current_user,%s,'CONNECT WITH GRANT OPTION') AS grant_connect",
        (DATABASE, DATABASE, DATABASE, DATABASE),
    ).fetchone()
    require(db == {"connect": True, "create": False, "temp": False,
                   "grant_connect": False},
            "WRITER_DATABASE_PRIVILEGES_INVALID")
    schema = conn.execute(
        "SELECT has_schema_privilege(current_user,%s,'USAGE') AS usage, "
        "has_schema_privilege(current_user,%s,'CREATE') AS create, "
        "has_schema_privilege(current_user,%s,'USAGE WITH GRANT OPTION') AS grant_usage",
        (SCHEMA, SCHEMA, SCHEMA),
    ).fetchone()
    require(schema == {"usage": True, "create": False, "grant_usage": False},
            "WRITER_SCHEMA_PRIVILEGES_INVALID")

    assert_synthetic_catalog(conn)
    for table, required in _TABLE_REQUIRED.items():
        rel = SCHEMA + "." + table
        for privilege in sorted(_TABLE_ACTIONS):
            value = conn.execute(
                "SELECT has_table_privilege(current_user,%s,%s) AS allowed",
                (rel, privilege),
            ).fetchone()
            require(value == {"allowed": privilege in required},
                    "WRITER_TABLE_GRANT_INVALID_" + table.upper() +
                    "_" + privilege)
            grant = conn.execute(
                "SELECT has_table_privilege(current_user,%s,%s) AS allowed",
                (rel, privilege + " WITH GRANT OPTION"),
            ).fetchone()
            require(grant == {"allowed": False},
                    "WRITER_GRANT_OPTION_FORBIDDEN_" + table.upper() +
                    "_" + privilege)

    # pg_control_system() can be protected by PostgreSQL. Allow only an
    # exact, independently approved FUNCTION EXECUTE privilege on this function,
    # not pg_monitor/pg_read_all_stats/superuser membership to pass this guard.
    control_read = conn.execute(
        "SELECT has_function_privilege(current_user,%s,'EXECUTE') AS allowed, "
        "has_function_privilege(current_user,%s,'EXECUTE WITH GRANT OPTION') AS grant_option",
        ("pg_catalog.pg_control_system()", "pg_catalog.pg_control_system()"),
    ).fetchone()
    require(control_read == {"allowed": True, "grant_option": False},
            "CONTROL_SYSTEM_FUNCTION_ACCESS_NOT_ATTESTED")
    # Successful has_function_privilege still needs *real* PostgreSQL EXECUTE
    # qualification; it cannot cryptographically authenticate the remote host.
