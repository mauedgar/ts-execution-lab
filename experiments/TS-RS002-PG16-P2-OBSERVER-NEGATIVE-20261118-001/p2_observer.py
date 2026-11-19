#!/usr/bin/env python3
"""Experimental TS Remote State 002 P2: authenticated observer negative evidence.

Fixed original PG16 container, no Product or Neon access. Password stays INSIDE
PostgreSQL container; native host executes only fixed Docker argv (shell=False).
Nothing here authorizes itself: external source/IR admission is mandatory.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import ipaddress
import base64
import json
import os
from pathlib import Path
import re
import selectors
import time
import stat
import subprocess
import sys

RUNNER_ID = "TS-RS002-P2-OBSERVER-20261119-004"
HOST = "DESKTOP-DJLBEQH"
CID = "5ce2b0833fa7ab04eac1b0c78e51ead0ed7c5e1dc2aede5621dba397b3c20d88"
DAEMON = "1219e4b8-5972-4880-8ebd-4fd2498a3e83"
NETWORK = "6c94a1fa2e3854335cdbb4b646439e8a03d4f9c3301b7a65b05a467856f5cc35"
VOLUME = "e0f82fa682d2559142b6d90e0c9d23aec384728b2ec618ee3344faa1fa3da899"
IMAGE = "postgres@sha256:5983db9a9c6ad225a48a46cfe2e03e6680b1826662befd0465eb05b34cb1c64e"
DB = "ts_rs002_a02_lab"
OBSERVER = "ts_rs002_observer"
ADMIN = "ts_rs002_admin"
DOCKER = "/usr/bin/docker"
SOURCE_ROOT = Path("/home/tsops/ts-remote-state-002/p1-c001-structured-20261117-003")
RECEIPTS = SOURCE_ROOT / "P2-observer-20261119-004"
ADMISSION = SOURCE_ROOT / "admission_P2_v4.json"
R001 = Path("/var/tmp/ts-rs002-a02-pg16-recovery-20261115-001/attempt-status.txt")
R001_SHA = "c66f4359dededc7221f13564178aa0749310f9d31d4dcc0541f65b35f529bd06"
C_TERMINAL = SOURCE_ROOT / "C" / "terminal.json"
C_SHA = "7aef5dff689e1ceb5575084f2445caf25116cff5a22917815400693d99316852"
SCHEMA = "ts_r3_global_head_20261107_001"
SECRET_MOUNT = "/run/secrets/observer.pass"
SECRET_SOURCE = "/var/tmp/ts-rs002-a02-pg16-20261113-001/secrets/observer.pass"
SECRET_ROOT = Path('/var/tmp/ts-rs002-a02-pg16-20261113-001')
GH = "/mnt/c/Program Files/GitHub CLI/gh.exe"
REVIEW_ID = "TS-RS002-P2-PR60-WEBINLINE-IR005-20261119-001"
REVIEW_REQUEST_PATH = "results/" + REVIEW_ID + "/ORIGINAL.md"
CONTROL_GRANT_PATH = "dispositions/TS-RS002-P2-PR60-PHYSICAL-ADMISSION-20261119-001/GRANT.json"
P0_DAC_ORIGINAL_PATH = "results/TS-RS002-P2-P0-OTHER-UID-DAC-20261119-001/ORIGINAL.json"
P0_REVIEW_ID = "TS-RS002-P2-P0-HOST-DAC-WEBINLINE-IR001-20261119-001"
P0_REVIEW_PATH = "results/" + P0_REVIEW_ID + "/ORIGINAL.md"
P0_NATIVE_ATTEMPT = "TS-RS002-P2-P0-HOST-DAC-20261119-001-A001"
P0_TERMINAL = "term_ad2e6b50-b30d-4e51-b32e-aa762e6a4b7e"
P0_TERMINAL_INCAR = "8541ed70-1732-4b31-b2b2-04957f984459"

# Host HBA SCRAM is independently checked before any observer login.
# pg_hba_file_rules reflects files on disk, NOT the last server-loaded rules.
# Check every include file's modification relative to pg_conf_load_time and
# inspect rule_number order, not just the existence of a SCRAM rule.
HBA = ("BEGIN READ ONLY; SELECT CASE WHEN bool_and((pg_stat_file(file_name)).modification <= pg_conf_load_time()) THEN 't' ELSE 'f' END "
       "FROM (SELECT DISTINCT file_name FROM pg_hba_file_rules) f; "
       "SELECT row_to_json(r)::text FROM (SELECT rule_number,file_name,line_number,type,database,user_name,address,netmask,auth_method,error "
       "FROM pg_hba_file_rules ORDER BY rule_number NULLS FIRST) r; COMMIT;")

def row_hash(tbl: str, keys: str) -> str:
    return (f"SELECT '{tbl}|' || COUNT(*)::text || '|' || "
            f"encode(sha256(convert_to(COALESCE(string_agg(to_jsonb(t)::text,E'\\n' ORDER BY {keys}),''),'UTF8')),'hex') "
            f"FROM {SCHEMA}.{tbl} t;")

# Stable keyed full-content SHA256 digests, plus schema and ACL fingerprints.
# Snapshots run in a single REPEATABLE READ READ ONLY transaction on one server.
SNAPSHOT = (
    "BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY; "
    + row_hash('head','t.scope') + row_hash('events','t.scope,t.revision')
    + row_hash('receipts','t.scope,t.mutation_id')
    + "SELECT 'columns|' || encode(sha256(convert_to(COALESCE(string_agg(table_name || '/' || ordinal_position::text || '/' || column_name || '/' || data_type || '/' || is_nullable,';' ORDER BY table_name,ordinal_position),''),'UTF8')),'hex') FROM information_schema.columns WHERE table_schema='"+SCHEMA+"'; "
    + "SELECT 'acl|' || encode(sha256(convert_to("
    + "COALESCE((SELECT string_agg(relname || '/' || relowner::text || '/' || COALESCE(relacl::text,''),';' ORDER BY relname) FROM pg_class c JOIN pg_namespace n ON c.relnamespace=n.oid WHERE n.nspname='"+SCHEMA+"' AND c.relkind='r'),'') || "
    + "'|' || COALESCE((SELECT datacl::text FROM pg_database WHERE datname='"+DB+"'),'') || "
    + "'|' || COALESCE((SELECT nspacl::text FROM pg_namespace WHERE nspname='"+SCHEMA+"'),'') || "
    + "'|' || COALESCE((SELECT rolconfig::text FROM pg_roles WHERE rolname='"+OBSERVER+"'),'') || "
    + "'|' || COALESCE((SELECT string_agg(c.relname || ':' || has_table_privilege('"+OBSERVER+"',c.oid,'SELECT')::text || '/' || has_table_privilege('"+OBSERVER+"',c.oid,'INSERT')::text || '/' || has_table_privilege('"+OBSERVER+"',c.oid,'UPDATE')::text || '/' || has_table_privilege('"+OBSERVER+"',c.oid,'DELETE')::text || '/' || has_table_privilege('"+OBSERVER+"',c.oid,'TRUNCATE')::text,';' ORDER BY c.relname) FROM pg_class c JOIN pg_namespace n ON c.relnamespace=n.oid WHERE n.nspname='"+SCHEMA+"' AND c.relkind='r'),'') "
    + ",'UTF8')),'hex'); COMMIT;"
)
# Additional fixed read-only authority + schema-definition fingerprints.
AUTHORITY_SNAPSHOT = f"""
SELECT 'authority|' || encode(sha256(convert_to(
COALESCE((SELECT string_agg(
    rolname || '/' || rolcanlogin::text || '/' || rolsuper::text || '/' ||
    rolcreatedb::text || '/' || rolcreaterole::text || '/' ||
    rolreplication::text || '/' || rolbypassrls::text || '/' ||
    rolinherit::text || '/' || rolconnlimit::text || '/' ||
    COALESCE(rolvaliduntil::text,'') || '/' || COALESCE(rolconfig::text,''),
    ';' ORDER BY rolname)
    FROM pg_roles),'')
|| '|' || COALESCE((SELECT string_agg(
    member::text || '/' || roleid::text || '/' || admin_option::text || '/' ||
    inherit_option::text || '/' || set_option::text, ';' ORDER BY member,roleid)
    FROM pg_auth_members),'')
|| '|' || (SELECT has_database_privilege('{OBSERVER}','{DB}','CONNECT')::text
    || '/' || has_database_privilege('{OBSERVER}','{DB}','CREATE')::text
    || '/' || has_database_privilege('{OBSERVER}','{DB}','TEMP')::text)
|| '|' || (SELECT has_schema_privilege('{OBSERVER}','{SCHEMA}','USAGE')::text
    || '/' || has_schema_privilege('{OBSERVER}','{SCHEMA}','CREATE')::text)
|| '|' || (SELECT has_schema_privilege('{OBSERVER}','public','CREATE')::text)
|| '|' || COALESCE((SELECT string_agg(
    c.relname || '/' || has_table_privilege('{OBSERVER}',c.oid,'REFERENCES')::text
    || '/' || has_table_privilege('{OBSERVER}',c.oid,'TRIGGER')::text,
    ';' ORDER BY c.relname)
    FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
    WHERE n.nspname='{SCHEMA}' AND c.relkind='r'),'')
,'UTF8')),'hex');
"""
DDL_SNAPSHOT = f"""
SELECT 'ddl|' || encode(sha256(convert_to(
COALESCE((SELECT string_agg(
    con.conname || '/' || con.contype::text || '/' || pg_get_constraintdef(con.oid,true),
    ';' ORDER BY con.conname,con.oid)
    FROM pg_constraint con JOIN pg_namespace n ON n.oid=con.connamespace
    WHERE n.nspname='{SCHEMA}'),'')
|| '|' || COALESCE((SELECT string_agg(
    indexname || '/' || indexdef, ';' ORDER BY indexname)
    FROM pg_indexes WHERE schemaname='{SCHEMA}'),'')
|| '|' || COALESCE((SELECT string_agg(
    t.tgname || '/' || t.tgenabled::text || '/' || pg_get_triggerdef(t.oid,true),
    ';' ORDER BY t.tgname,t.oid)
    FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid
    JOIN pg_namespace n ON n.oid=c.relnamespace
    WHERE n.nspname='{SCHEMA}' AND NOT t.tgisinternal),'')
|| '|' || COALESCE((SELECT string_agg(
    p.proname || '/' || p.prosecdef::text || '/' || COALESCE(p.proacl::text,''),
    ';' ORDER BY p.proname,p.oid)
    FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
    WHERE n.nspname='{SCHEMA}'),'')
,'UTF8')),'hex');
"""
SNAPSHOT = SNAPSHOT.replace(" COMMIT;", " " + AUTHORITY_SNAPSHOT + " " + DDL_SNAPSHOT + " COMMIT;")

# RLS policy and function *definitions*, not only their count/name/ACL,
# are independently hashed within the same fixed READ ONLY snapshot.
RLS_SNAPSHOT = f"""
SELECT 'rls|' || encode(sha256(convert_to(
COALESCE((SELECT string_agg(
    c.relname || '/' || c.relrowsecurity::text || '/' || c.relforcerowsecurity::text,
    ';' ORDER BY c.relname)
    FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
    WHERE n.nspname='{SCHEMA}' AND c.relkind='r'),'')
|| '|' || COALESCE((SELECT string_agg(
    c.relname || '/' || p.polname || '/' || p.polcmd::text || '/' ||
    p.polpermissive::text || '/' || p.polroles::text || '/' ||
    COALESCE(pg_get_expr(p.polqual,p.polrelid,true),'') || '/' ||
    COALESCE(pg_get_expr(p.polwithcheck,p.polrelid,true),''),
    ';' ORDER BY c.relname,p.polname,p.oid)
    FROM pg_policy p JOIN pg_class c ON c.oid=p.polrelid
    JOIN pg_namespace n ON n.oid=c.relnamespace
    WHERE n.nspname='{SCHEMA}'),'')
,'UTF8')),'hex');
"""
FUNCTION_SNAPSHOT = f"""
SELECT 'functions|' || encode(sha256(convert_to(
COALESCE((SELECT string_agg(
    p.proname || '/' || pg_get_function_identity_arguments(p.oid) || '/' ||
    p.prokind::text || '/' || p.proowner::text || '/' ||
    p.prolang::text || '/' || p.prosecdef::text || '/' ||
    COALESCE(p.proacl::text,'') || '/' ||
    CASE WHEN p.prokind IN ('f','p') THEN pg_get_functiondef(p.oid)
         ELSE COALESCE(p.prosrc,'') || '/' || COALESCE(p.probin,'') END,
    ';' ORDER BY p.proname,p.oid)
    FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
    WHERE n.nspname='{SCHEMA}'),'')
,'UTF8')),'hex');
"""
SNAPSHOT = SNAPSHOT.replace(" COMMIT;", " " + RLS_SNAPSHOT + " " + FUNCTION_SNAPSHOT + " COMMIT;")

POSITIVE = f"BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY; SELECT session_user,current_user,current_database(),current_setting('transaction_read_only'),current_setting('default_transaction_read_only'),inet_server_addr(),(SELECT ssl FROM pg_stat_ssl WHERE pid=pg_backend_pid()); SELECT COUNT(*) FROM {SCHEMA}.head; COMMIT;"
# Zero affected rows even if unauthorized DELETE surprisingly succeeds, then
# explicit rollback; READ WRITE intentionally probes ACL rather than being
# masked by observer's default_transaction_read_only=on.
DENY_DELETE = f"BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ WRITE; DELETE FROM {SCHEMA}.head WHERE FALSE; ROLLBACK;"
# Temporary object is session-local and transaction-rolled-back if privilege
# surprisingly exists; never writes the durable public or Product schema.
DENY_TEMP = "BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ WRITE; CREATE TEMP TABLE ts_rs002_p2_negative_probe (id integer); ROLLBACK;"
DENY_ROLE = "BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY; SET ROLE ts_rs002_owner; ROLLBACK;"
STEPS = (
    ("hba", HBA, False),
    ("snapshot_before", SNAPSHOT, False),
    ("observer_read", POSITIVE, True),
    ("deny_delete", DENY_DELETE, True),
    ("deny_temp", DENY_TEMP, True),
    ("deny_role", DENY_ROLE, True),
    ("snapshot_after", SNAPSHOT, False),
)
# The shell is executed inside the original *isolated container* only. It
# reads the readonly mounted secret and execs psql. No password appears in
# host argv, Docker CLI environment, stdout, receipt, or Git transport.
OBSERVER_WRAPPER = 'PGPASSWORD=$(cat /run/secrets/observer.pass); export PGPASSWORD; export PGSSLMODE=disable PGGSSENCMODE=disable; exec psql -X -qAt -v ON_ERROR_STOP=1 -h 127.0.0.1 -U ts_rs002_observer -d ts_rs002_a02_lab -c "$1"'


def fail(code: str) -> None:
    raise RuntimeError(code)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_read(path: Path, limit: int = 16000) -> bytes:
    st = path.lstat()
    if not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid() or st.st_nlink != 1 or st.st_mode & 0o022:
        fail("UNTRUSTED_INPUT_FILE")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        st2 = os.fstat(fd)
        if (st.st_dev, st.st_ino) != (st2.st_dev, st2.st_ino):
            fail("INPUT_RACE")
        data = os.read(fd, limit + 1)
        if len(data) > limit:
            fail("INPUT_SIZE")
        return data
    finally:
        os.close(fd)


def private_dir(path: Path) -> None:
    st = path.lstat()
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.getuid() or st.st_mode & 0o077:
        fail("UNTRUSTED_RESULT_DIR")


def parse_review_admission(review: str, j: dict) -> None:
    """Reject embedded, duplicated or contradictory review claims."""
    begin = "<!-- TS_RS002_P2_REVIEW_ADMISSION_V1_BEGIN -->"
    end = "<!-- TS_RS002_P2_REVIEW_ADMISSION_V1_END -->"
    if review.count(begin) != 1 or review.count(end) != 1:
        fail("REVIEW_ADMISSION_NOT_UNIQUE")
    marker = re.search(re.escape(begin) + r"\n([^\r]*?)\n" + re.escape(end), review, re.S)
    if marker is None or "\r" in marker.group(1):
        fail("REVIEW_ADMISSION_INVALID")
    expected = [
        "review_id: " + REVIEW_ID,
        "verdict: RECOMMEND",
        "findings: 0",
        "advisories: 0",
        "source_head: " + j["source_commit"],
        "source_blob: " + j["source_blob"],
    ]
    if marker.group(1).split("\n") != expected:
        fail("REVIEW_ADMISSION_FIELDS_MISMATCH")
    # Entire summary headers are unique and exact, not independent searches
    # for one favorable line within a contradictory report.
    for field, wanted in (("Verdict","**RECOMMEND**"),
                          ("Findings","**0**"),("Advisories","**0**")):
        lines = re.findall(r"(?m)^" + field + r":[ \t]*([^\r\n]*)$",review)
        if lines != [wanted]:
            fail("REVIEW_CONTRADICTORY_" + field.upper())
    ids = re.findall(r"(?m)^Review_ID:[ \t]*([^\r\n]*)$",review)
    if ids != [chr(96) + REVIEW_ID + chr(96)]:
        fail("REVIEW_ID_MISMATCH")

def verified_review(j: dict) -> None:
    """Control pins an immutable Git original. Verify actual path, Git blob and review fields.

    Without a separately selected ORIGINAL SHA/ref and an exact Control grant,
    this source is unadmitted. Content alone cannot confer Product authority.
    """
    ref = j['review_commit']
    assert isinstance(ref,str)
    if not re.fullmatch('[0-9a-f]{40}',ref): fail('REVIEW_COMMIT_NOT_FROZEN')
    # GitHub's signed HTTP transport supplies provenance for the immutable
    # selection by Control; do not construct branch-ref URLs from user input.
    url = f'repos/mauedgar/ts-execution-transport/contents/{REVIEW_REQUEST_PATH}?ref={ref}'
    data = json.loads(read_output([GH,'api',url],limit=40000))
    if data.get('sha') != j['review_original_blob'] or data.get('path') != REVIEW_REQUEST_PATH:
        fail('REVIEW_ORIGINAL_GIT_MISMATCH')
    review = base64.b64decode(data['content'],validate=False).decode('utf-8')
    parse_review_admission(review,j)
    # Verify source object through immutable Git blob and independently compare
    # with runner file + independently selected source commit from Control.
    obj = json.loads(read_output([GH,'api','repos/mauedgar/ts-execution-lab/git/blobs/'+j['source_blob']],limit=80000))
    from_git = base64.b64decode(obj['content'],validate=False)
    if obj.get('sha') != j['source_blob'] or sha(from_git) != j['source_sha256']:
        fail('SOURCE_GIT_CONTENT_MISMATCH')
    c = json.loads(read_output([GH,'api','repos/mauedgar/ts-execution-lab/git/commits/'+j['source_commit']],limit=100000))
    if not re.fullmatch('[0-9a-f]{40}',c.get('sha','')): fail('GIT_COMMIT_INVALID')
    expected_path = 'experiments/TS-RS002-PG16-P2-OBSERVER-NEGATIVE-20261118-001/p2_observer.py'
    gitfile = json.loads(read_output([GH,'api',f'repos/mauedgar/ts-execution-lab/contents/{expected_path}?ref='+j['source_commit']],limit=80000))
    if gitfile.get('sha') != j['source_blob']: fail('SOURCE_COMMIT_BLOB_MISMATCH')


def validate_p0_native(native: dict) -> None:
    """Shape and native identities are necessary, not independent proof."""
    required = {
        "protocol":"TS-RS002-P2-P0-HOST-DAC-NATIVE-v2",
        "execution_attempt":P0_NATIVE_ATTEMPT,
        "provider":"ORCA_NATIVE_TERMINAL",
        "status":"PASS","host":HOST,"distro":"Ubuntu-24.04",
        "terminal":P0_TERMINAL,"terminal_incarnation":P0_TERMINAL_INCAR,
        "container_id":CID,"prior_C_terminal_sha256":C_SHA,
        "secret_contents_exposed":False,"Product_effect":"NONE"}
    if type(native) is not dict or set(native) != set(required) | {"identity","denial"}:
        fail("P0_ORIGINAL_SCHEMA_INVALID")
    if any(native[k] != v for k,v in required.items()):
        fail("P0_ORIGINAL_IDENTITY_INVALID")
    for row,code in ((native["identity"],0),(native["denial"],1)):
        if type(row) is not dict or set(row) != {"request_id","native_pid","exit_code","observed_uid"}:
            fail("P0_NATIVE_PROVIDER_SCHEMA")
        if not re.fullmatch(r"[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}",str(row["request_id"])):
            fail("P0_NATIVE_PROVIDER_REQUEST_ID")
        if type(row["native_pid"]) is not int or row["native_pid"] <= 0:
            fail("P0_NATIVE_PID_NOT_VERIFIED")
        if type(row["exit_code"]) is not int or row["exit_code"] != code:
            fail("P0_NATIVE_EXIT_NOT_VERIFIED")
        if type(row["observed_uid"]) is not int or row["observed_uid"] != 65534:
            fail("P0_OTHER_UID_NOT_VERIFIED")
    if native["identity"]["request_id"] == native["denial"]["request_id"]:
        fail("P0_PROVIDER_REQUEST_COLLISION")


def validate_p0_review(review: str, native: dict, digest: str) -> None:
    """Independent reviewer must check original provider-native observations."""
    begin = "<!-- TS_RS002_P0_PROVIDER_REVIEW_V1_BEGIN -->"
    end = "<!-- TS_RS002_P0_PROVIDER_REVIEW_V1_END -->"
    if review.count(begin) != 1 or review.count(end) != 1:
        fail("P0_INDEPENDENT_ATTESTATION_MISSING")
    m = re.search(re.escape(begin) + r"\n([^\r]*?)\n" + re.escape(end),review,re.S)
    if m is None or "\r" in m.group(1):
        fail("P0_INDEPENDENT_ATTESTATION_INVALID")
    expected = [
        "review_id: " + P0_REVIEW_ID,"verdict: RECOMMEND",
        "findings: 0","advisories: 0",
        "native_attempt: " + P0_NATIVE_ATTEMPT,
        "native_original_sha256: " + digest,
        "identity_request_id: " + native["identity"]["request_id"],
        "denial_request_id: " + native["denial"]["request_id"],
        "native_exits: 0,1","provider_native_observed: true"]
    if m.group(1).split("\n") != expected:
        fail("P0_REVIEW_NATIVE_BINDING_INVALID")
    for name,wanted in (("Verdict","**RECOMMEND**"),("Findings","**0**"),("Advisories","**0**")):
        fields = re.findall(r"(?m)^"+name+r":[ \t]*([^\r\n]*)$",review)
        if fields != [wanted]:
            fail("P0_REVIEW_CONTRADICTORY_"+name.upper())
    ids = re.findall(r"(?m)^Review_ID:[ \t]*([^\r\n]*)$",review)
    if ids != [chr(96)+P0_REVIEW_ID+chr(96)]:
        fail("P0_REVIEW_ID_INVALID")


def verify_p0_dac(j: dict) -> None:
    """Both independent originals are required; one self-reported JSON fails."""
    for key in ("p0_receipt_commit","p0_review_commit"):
        if not re.fullmatch(r"[0-9a-f]{40}",str(j[key])):
            fail("P0_COMMIT_NOT_FROZEN")
    url = "repos/mauedgar/ts-execution-transport/contents/"+P0_DAC_ORIGINAL_PATH+"?ref="+j["p0_receipt_commit"]
    doc = json.loads(read_output([GH,"api",url],limit=40000))
    if doc.get("path") != P0_DAC_ORIGINAL_PATH or doc.get("sha") != j["p0_receipt_blob"]:
        fail("P0_PROVIDER_ORIGINAL_GIT_MISMATCH")
    raw = base64.b64decode(doc["content"],validate=False)
    if sha(raw) != j["p0_receipt_sha256"]:
        fail("P0_PROVIDER_ORIGINAL_HASH_MISMATCH")
    native = json.loads(raw)
    validate_p0_native(native)
    url = "repos/mauedgar/ts-execution-transport/contents/"+P0_REVIEW_PATH+"?ref="+j["p0_review_commit"]
    review = json.loads(read_output([GH,"api",url],limit=40000))
    if review.get("path") != P0_REVIEW_PATH or review.get("sha") != j["p0_review_blob"]:
        fail("P0_INDEPENDENT_REVIEW_GIT_MISMATCH")
    review_raw = base64.b64decode(review["content"],validate=False)
    if sha(review_raw) != j["p0_review_sha256"]:
        fail("P0_INDEPENDENT_REVIEW_HASH_MISMATCH")
    validate_p0_review(review_raw.decode("utf-8"),native,sha(raw))


def verified_grant(j: dict) -> None:
    # Real trust boundary: a pre-published immutable private GitHub Control
    # grant, retrieved from its exact qualified path and immutable commit.
    # A locally self-asserted manifest, review or digest alone is insufficient.
    url = f"repos/mauedgar/ts-execution-transport/contents/{CONTROL_GRANT_PATH}?ref={j['control_grant_commit']}"
    obj = json.loads(read_output([GH,'api',url],limit=40000))
    if obj.get('path') != CONTROL_GRANT_PATH or obj.get('sha') != j['control_grant_blob']:
        fail('CONTROL_GRANT_GIT_ORIGIN_MISMATCH')
    raw = base64.b64decode(obj['content'],validate=False)
    if sha(raw) != j['control_grant_sha256']:
        fail('CONTROL_GRANT_HASH_MISMATCH')
    ctrl = json.loads(raw)
    required = {'protocol':'TS-RS002-P2-EXTERNAL-CONTROL-GRANT-v3',
                'decision':'ADMIT_P2_SINGLE_ATTEMPT',
                'owner':'TS_REMOTE_STATE_002_EXPERIMENTAL_CONTROL',
                'execution_attempt':'TS-RS002-P2-OBSERVER-20261119-004-A001',
                'source_commit':j['source_commit'],'source_blob':j['source_blob'],
                'source_sha256':j['source_sha256'],
                'review_commit':j['review_commit'],
                'review_original_blob':j['review_original_blob'],
                'p0_receipt_commit':j['p0_receipt_commit'],
                 'p0_receipt_blob':j['p0_receipt_blob'],
                 'p0_receipt_sha256':j['p0_receipt_sha256'],
                 'p0_review_commit':j['p0_review_commit'],
                 'p0_review_blob':j['p0_review_blob'],
                 'p0_review_sha256':j['p0_review_sha256'],
                 'p0_native_attempt':P0_NATIVE_ATTEMPT,
                 'prior_C_terminal_sha256':C_SHA,'container_id':CID}
    if ctrl != required: fail('CONTROL_GRANT_FIELDS_NOT_ADMITTED')
    verify_p0_dac(j)


def admittance() -> tuple[str, str]:
    raw = safe_read(ADMISSION)
    j = json.loads(raw)
    required = {'protocol','runner_id','source_commit','source_blob','source_sha256',
                'review_commit','review_original_blob','review_verdict','container_id',
                'prior_C_terminal_sha256','allowed_effect','control_grant_sha256',
                'control_grant_commit','control_grant_blob',
                 'p0_receipt_commit','p0_receipt_blob','p0_receipt_sha256',
                 'p0_review_commit','p0_review_blob','p0_review_sha256'}
    if set(j) != required or j['protocol'] != 'TS-RS002-P2-OBSERVER-20261119-v4' or j['runner_id'] != RUNNER_ID:
        fail('P2_ADMISSION_SCHEMA')
    if (j['source_sha256'] != sha(Path(__file__).read_bytes()) or j['container_id'] != CID
        or j['prior_C_terminal_sha256'] != C_SHA or j['allowed_effect'] != 'P2_OBSERVER_ONE_SHOT'
        or j['review_verdict'] != 'RECOMMEND'):
        fail('P2_ADMISSION_NOT_GRANTED')
    for k in ('source_commit','source_blob','review_commit','review_original_blob','control_grant_commit','control_grant_blob','p0_receipt_commit','p0_receipt_blob','p0_review_commit','p0_review_blob'):
        if not re.fullmatch('[0-9a-f]{40}',j[k]): fail('P2_REF_INVALID')
    for key in ('control_grant_sha256','p0_receipt_sha256','p0_review_sha256'):
        if not re.fullmatch('[0-9a-f]{64}',j[key]): fail('CONTROL_OR_P0_DIGEST_INVALID')
    # The grant digest must be fixed by Control's external exact source-only
    # launcher before this source runs, and recorded in a distinct provider
    # receipt. A locally crafted JSON alone remains UNAUTHORIZED.
    verified_review(j)
    verified_grant(j)
    return sha(raw), j['source_sha256']


def capture_bounded(child: subprocess.Popen, *, timeout: float, limit: int = 16000) -> tuple[str,str]:
    """Bound both streams without pipe deadlock, no kill, and no blind retry.

    If a child remains alive on timeout/overflow, its PID is preserved in the
    step's durable pre-spawn/running records. Only original process may be
    joined later by competent provider-native observation.
    """
    out: list[bytes] = []; err: list[bytes] = []
    totals=[0,0]; started=time.monotonic()
    with selectors.DefaultSelector() as sel:
        for stream,slot in ((child.stdout,0),(child.stderr,1)):
            if stream is None: fail('PROCESS_STREAM_MISSING')
            os.set_blocking(stream.fileno(),False)
            sel.register(stream,selectors.EVENT_READ,slot)
        while sel.get_map() or child.poll() is None:
            remaining=timeout-(time.monotonic()-started)
            if remaining<=0: fail('NATIVE_CHILD_TIMEOUT_UNRECONCILED')
            events=sel.select(timeout=min(remaining,0.2))
            for key,_ in events:
                data=os.read(key.fileobj.fileno(),4096)
                if not data:
                    sel.unregister(key.fileobj)
                    continue
                idx=key.data
                totals[idx]+=len(data)
                if totals[idx]>limit: fail('NATIVE_OUTPUT_LIMIT_UNRECONCILED')
                (out if idx==0 else err).append(data)
    return b''.join(out).decode('utf-8','replace'),b''.join(err).decode('utf-8','replace')


def read_output(argv: list[str], limit: int = 32000) -> str:
    child = subprocess.Popen(argv,shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        stdout,_=capture_bounded(child,timeout=25,limit=limit)
    except RuntimeError as e:
        # Preflight is read-only. An original child on timeout may remain alive;
        # include exact original host PID and stop without new command.
        fail(str(e)+'_PID_'+str(child.pid))
    if child.returncode != 0: fail('NATIVE_PREFLIGHT_COMMAND_FAILED')
    return stdout.strip()


def preflight() -> tuple[str, str]:
    if os.uname().nodename.upper() != HOST or os.getuid() != 1000 or sys.version_info[:3] != (3, 15, 2):
        fail("WRONG_HOST_UID_OR_RUNTIME")
    private_dir(SOURCE_ROOT)
    admission_hash, source_hash = admittance()
    if sha(safe_read(C_TERMINAL)) != C_SHA:
        fail("PREVIOUS_C_ORIGINAL_DIGEST")
    c = json.loads(safe_read(C_TERMINAL))
    if c.get("status") != "PASS" or c.get("phase") != "C" or c.get("exit_code") != 0 or c.get("database_mutation") != "NONE_READ_ONLY" or c.get("container_id") != CID:
        fail("PREVIOUS_C_NOT_PASS")
    if sha(R001.read_bytes()) != R001_SHA:
        fail("ORIGINAL_R001_MISMATCH")
    if read_output([DOCKER,"info","--format","{{.ID}}"] ) != DAEMON:
        fail("WRONG_DOCKER_DAEMON")
    v = json.loads(read_output([DOCKER,"container","inspect",CID]))
    if type(v) is not list or len(v) != 1:
        fail("CONTAINER_INSPECT_UNEXPECTED")
    c = v[0]
    if c.get("Id") != CID or c["State"].get("Running") is not True or c["State"].get("RestartCount",0) != 0 or c.get("RestartCount") != 0:
        fail("CONTAINER_STATE_DRIFT")
    if c["Config"].get("Image") != IMAGE or c["HostConfig"].get("Privileged") or c["HostConfig"].get("PortBindings"):
        fail("CONTAINER_PRIVILEGE_OR_IMAGE_DRIFT")
    nets = c["NetworkSettings"]["Networks"]
    if len(nets) != 1 or next(iter(nets.values())).get("NetworkID") != NETWORK:
        fail("CONTAINER_NETWORK_DRIFT")
    if (c['HostConfig'].get('NetworkMode') != NETWORK or c['HostConfig'].get('RestartPolicy',{}).get('Name') != 'no'
        or c['HostConfig'].get('Memory') != 536870912 or c['HostConfig'].get('PidsLimit') != 256
        or c['HostConfig'].get('NanoCpus') != 1000000000):
        fail('CONTAINER_RESOURCE_OR_NETWORKMODE_DRIFT')
    labels = c['Config'].get('Labels') or {}
    if labels.get('ts.rs002.operation') != 'TS-RS002-A02-PG16-PROVISION-20261113-001' or labels.get('ts.rs002.attempt') != 'TS-RS002-A02-PG16-PROVISION-A001':
        fail('CONTAINER_ORIGIN_LABELS_DRIFT')
    net = json.loads(read_output([DOCKER,'network','inspect',NETWORK]))
    if len(net)!=1 or net[0].get('Id')!=NETWORK or net[0].get('Internal') is not True or net[0].get('Driver')!='bridge':
        fail('ORIGINAL_INTERNAL_NETWORK_NOT_ATTESTED')
    mounts = c["Mounts"]
    pgdata = [m for m in mounts if m.get("Destination") == "/var/lib/postgresql/data"]
    if (len(pgdata) != 1 or pgdata[0].get("Name") != VOLUME or
        pgdata[0].get("Type") != "volume" or pgdata[0].get("RW") is not True or
        pgdata[0].get("Driver") != "local"):
        fail("CONTAINER_PGDATA_DRIFT")
    expected_binds = {
        "/docker-entrypoint-initdb.d": str(SECRET_ROOT/"init"),
        "/run/secrets/ts-admin-pass": str(SECRET_ROOT/"secrets"/"admin.pass"),
        SECRET_MOUNT: SECRET_SOURCE,
        "/run/secrets/writer_a.pass": str(SECRET_ROOT/"secrets"/"writer_a.pass"),
        "/run/secrets/writer_b.pass": str(SECRET_ROOT/"secrets"/"writer_b.pass"),
    }
    binds = [m for m in mounts if m.get("Type") == "bind"]
    if (len(binds) != len(expected_binds) or
        any(m.get("Destination") not in expected_binds or
            m.get("Source") != expected_binds.get(m.get("Destination")) or
            m.get("RW") is not False for m in binds)):
        fail("ORIGINAL_READONLY_BIND_INVENTORY_DRIFT")
    # An independent other-UID host-DAC negative original is required by
    # Control before any physical grant. This runner cannot self-attest it.
    # Host secret has 0700 ancestor; actual mode is 0644 for UID999 in
    # read-only container. Other-UID traversal is a separate mandatory P0 test.
    if any(m.get('Type')=='bind' and m.get('RW') is not False for m in mounts):
        fail('UNEXPECTED_WRITABLE_HOST_BIND')
    # WSL owner-only ancestor controls the 0644 secret file needed by
    # container UID999. Reject symlinks, foreign owner or writable ancestors.
    for root in (SECRET_ROOT,SECRET_ROOT/'secrets'):
        st=root.lstat()
        if not stat.S_ISDIR(st.st_mode) or st.st_uid != 1000 or st.st_mode & 0o077:
            fail('SECRET_HOST_ANCESTOR_NOT_PRIVATE')
    secret_stat=(SECRET_ROOT/'secrets'/'observer.pass').lstat()
    if (not stat.S_ISREG(secret_stat.st_mode) or secret_stat.st_uid != 1000
        or secret_stat.st_nlink != 1 or secret_stat.st_mode & 0o022):
        fail('SECRET_HOST_FILE_NOT_TRUSTED')
    if c.get("Image") != read_output([DOCKER,"image","inspect","--format","{{.Id}}",IMAGE]):
        fail("EFFECTIVE_IMAGE_DRIFT")
    if RECEIPTS.exists() or RECEIPTS.is_symlink():
        fail("P2_ATTEMPT_ALREADY_EXISTS_NO_RETRY")
    return admission_hash, source_hash


def cmd_for(sql: str, observer: bool) -> list[str]:
    base = [DOCKER,"exec","--user","postgres",CID]
    if observer:
        return base + ["sh","-ec",OBSERVER_WRAPPER,"p2-fixed",sql]
    return base + ["psql","-X","-qAt","-v","ON_ERROR_STOP=1","-U",ADMIN,"-d",DB,"-c",sql]


def parse_rows(stdout: str) -> list[str]:
    if "\x00" in stdout or len(stdout) > 6000:
        fail("UNSAFE_NATIVE_OUTPUT")
    return [s.strip() for s in stdout.splitlines() if s.strip() not in ("BEGIN","COMMIT","ROLLBACK") and s.strip()]


def effective_scram(rows: list[str]) -> str:
    if len(rows)<2 or rows[0]!='t': fail('HBA_NOT_LOADED_OR_EMPTY')
    parsed=[]
    for raw in rows[1:]:
        try: j=json.loads(raw)
        except (ValueError,TypeError): fail('HBA_INVALID_JSON')
        if not isinstance(j,dict) or j.get('error') is not None or type(j.get('rule_number')) is not int:
            fail('HBA_INVALID_RULE')
        parsed.append(j)
    nums=[x['rule_number'] for x in parsed]
    if not nums or nums!=sorted(set(nums)): fail('HBA_ORDER_NOT_VERIFIED')
    ip=ipaddress.ip_address('127.0.0.1')
    for x in parsed:
        if x.get('type') not in ('host','hostnossl'): continue
        databases=x.get('database'); users=x.get('user_name')
        if not isinstance(databases,list) or not isinstance(users,list): fail('HBA_INVALID_SELECTOR')
        # A selector that may include group/regex/includes is ambiguous and
        # potentially shadows a later rule. Reject rather than guess.
        for value in databases+users:
            if type(value) is not str or value.startswith(('+','/','@')):
                fail('HBA_AMBIGUOUS_ROLE_OR_DB_SELECTOR')
        dbmatch='all' in databases or DB in databases
        usermatch='all' in users or OBSERVER in users
        if not dbmatch or not usermatch: continue
        addr=x.get('address'); mask=x.get('netmask')
        if addr=='all': is_match=True
        elif addr in ('samehost','samenet'): fail('HBA_AMBIGUOUS_ADDRESS')
        else:
            try:
                if type(addr)!=str: fail('HBA_ADDRESS_INVALID')
                network=ipaddress.ip_network(f'{addr}/{mask}' if mask else addr,strict=False)
                is_match = ip in network
            except ValueError:
                fail('HBA_UNRESOLVED_HOSTNAME')
        if is_match:
            if x.get('auth_method')!='scram-sha-256': fail('HBA_FIRST_RULE_NOT_SCRAM')
            return f"rule={x['rule_number']}|scram-sha-256"
    fail('HBA_NO_EFFECTIVE_RULE')


def interpret(step: str, returncode: int, stdout: str, stderr: str, before: list[str] | None) -> list[str]:
    if step == "hba":
        rows = parse_rows(stdout)
        if returncode != 0: fail('HBA_NATIVE_SQL_FAILED')
        return [effective_scram(rows)]
    if step in ("snapshot_before","snapshot_after"):
        rows = parse_rows(stdout)
        if (returncode != 0 or len(rows) != 9 or
            any(not re.fullmatch(r'(head|events|receipts)\|[0-9]+\|[0-9a-f]{64}',rows[i]) for i in range(3)) or
            any(not re.fullmatch(r'(columns|acl|authority|ddl|rls|functions)\|[0-9a-f]{64}',rows[i+3]) for i in range(6)) or
            [s.split('|')[0] for s in rows] != ['head','events','receipts','columns','acl','authority','ddl','rls','functions']):
            fail("SNAPSHOT_INVALID")
        if step == "snapshot_after" and rows != before:
            fail("SCHEMA_ROWS_CHANGED")
        return rows
    if step == "observer_read":
        rows = parse_rows(stdout)
        if returncode != 0 or len(rows) != 2 or rows[0] != "ts_rs002_observer|ts_rs002_observer|ts_rs002_a02_lab|on|on|127.0.0.1|f" or not re.fullmatch("[0-9]+",rows[1]):
            fail("OBSERVER_TCP_READ_NOT_PROVEN")
        return rows
    errors = {"deny_delete":"permission denied for table head", "deny_temp":"permission denied to create temporary tables", "deny_role":"permission denied to set role"}
    if step not in errors:
        fail("UNRECOGNIZED_STEP")
    # psql ON_ERROR_STOP returns 3 for actual SQL errors. In particular, a
    # READ ONLY error does not pass the ACL denial test; DELETE uses READ WRITE.
    if returncode != 3 or errors[step] not in stderr.lower():
        fail("OBSERVER_NEGATIVE_FAILED_" + step.upper())
    return ["ERROR: " + errors[step]]


def write_once(path: Path, obj: dict) -> bytes:
    raw = (json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=True) + "\n").encode()
    fd = os.open(path, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd,"wb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    dfd = os.open(path.parent, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try: os.fsync(dfd)
    finally: os.close(dfd)
    return raw


def execute() -> None:
    admission_sha, source_sha = preflight()
    RECEIPTS.mkdir(mode=0o700)
    private_dir(RECEIPTS)
    intent = write_once(RECEIPTS/"intent.json", {"runner_id":RUNNER_ID,"admission_sha256":admission_sha,"source_sha256":source_sha,"prior_C_original_sha256":C_SHA,"container_id":CID,"status":"PENDING","start_utc":now(),"Product_effect":"NONE"})
    status = "UNKNOWN"
    code = "P2_UNVERIFIED"
    steps: list[dict] = []
    before = None
    unresolved_child_pid: int | None = None
    unresolved_step: str | None = None
    try:
        for name, sql, observer in STEPS:
            cmd = cmd_for(sql, observer)
            # Intent is fsynced before a child could exist; interruption or
            # a failed spawn remains a non-replayable UNKNOWN boundary.
            before_spawn = {"name":name,"sql_sha256":sha(sql.encode()),"observer":observer,
                            "status":"PRE_SPAWN_UNKNOWN","parent_pid":os.getpid(),
                            "argv_sha256":sha(json.dumps(cmd).encode()),"utc":now()}
            intent_bytes = write_once(RECEIPTS/("step_intent_"+name+".json"),before_spawn)
            child = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            unresolved_child_pid = child.pid
            unresolved_step = name
            step = {"name":name,"pid":child.pid,"sql_sha256":sha(sql.encode()),"observer":observer,"start_utc":now(),"status":"UNKNOWN","intent_sha256":sha(intent_bytes)}
            running_bytes = write_once(RECEIPTS/("start_"+name+".json"),step)
            try:
                stdout, stderr = capture_bounded(child,timeout=20,limit=16000)
            except RuntimeError as e:
                write_once(RECEIPTS/('failure_'+name+'.json'),
                           {'name':name,'pid':child.pid,'status':'UNKNOWN','code':str(e),
                            'intent_sha256':sha(intent_bytes),'running_sha256':sha(running_bytes),
                            'native_exit_code':child.poll(),'no_retry':True})
                # Per-step pre-spawn and native PID already fsynced; do not
                # kill the child or blindly redispatch another process.
                raise
            try:
                rows = interpret(name,child.returncode,stdout,stderr,before)
            except RuntimeError as e:
                write_once(RECEIPTS/('failure_'+name+'.json'),
                           {'name':name,'pid':child.pid,'status':'FAILED','code':str(e),
                            'native_exit_code':child.returncode,'stderr_sha256':sha(stderr.encode()),
                            'stdout_sha256':sha(stdout.encode()),
                            'intent_sha256':sha(intent_bytes),'running_sha256':sha(running_bytes),
                            'no_retry':True})
                raise
            if name == "snapshot_before": before = rows
            step.update({"status":"PASS","end_utc":now(),"exit_code":child.returncode,
                         "result":rows,"stderr_sha256":sha(stderr.encode("utf-8"))})
            result_bytes = write_once(RECEIPTS/("result_"+name+".json"),step)
            steps.append({"name":name,"result":rows,"exit_code":child.returncode,"status":"PASS",
                          "step_intent_sha256":sha(intent_bytes),"running_sha256":sha(running_bytes),
                          "result_sha256":sha(result_bytes)})
            unresolved_child_pid = None
            unresolved_step = None
        status,code = "PASS","OK"
    except RuntimeError as e:
        code = str(e) if re.fullmatch("[A-Z0-9_]{3,100}",str(e)) else "P2_STEP_BLOCKED"
        status = "UNKNOWN" if code in ('NATIVE_CHILD_TIMEOUT_UNRECONCILED','NATIVE_OUTPUT_LIMIT_UNRECONCILED') else "FAILED"
    except Exception:
        status,code = "UNKNOWN","UNEXPECTED_NATIVE_EXCEPTION"
    terminal = {"runner_id":RUNNER_ID,"status":status,"code":code,"container_id":CID,"admission_sha256":admission_sha,"source_sha256":source_sha,"prior_C_original_sha256":C_SHA,"intent_sha256":sha(intent),"steps":steps,"end_utc":now(),"Product_effect":"NONE","database_mutation":"NONE_READONLY_OR_ROLLEDBACK" if status == "PASS" else "NOT_PROVEN",
                "possibly_unreconciled_child_pid":unresolved_child_pid,
                "possibly_unreconciled_step":unresolved_step,"no_retry":True}
    write_once(RECEIPTS/"terminal.json",terminal)
    print(json.dumps(terminal,sort_keys=True))
    if status != "PASS": sys.exit(3)


def main() -> None:
    ap=argparse.ArgumentParser()
    group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--preflight",action="store_true")
    group.add_argument("--run",action="store_true")
    args=ap.parse_args()
    try:
        if args.preflight:
            preflight()
            print("P2_PREFLIGHT_PASS effect=NONE")
        else: execute()
    except Exception as e:
        c=str(e) if re.fullmatch("[A-Z0-9_]{3,100}",str(e)) else "P2_PRECONDITION_BLOCKED"
        print("BLOCKED_"+c,file=sys.stderr)
        sys.exit(2)

if __name__=="__main__":
    main()
