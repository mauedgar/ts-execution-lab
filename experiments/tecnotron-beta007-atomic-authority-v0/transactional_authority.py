"""Isolated NONPRODUCT transaction equivalence experiment. Authority: NONE.

SQLite is only an experimental transactional decision/effect ledger here.
Nothing in this module modifies Tecnotron Product, H6, or GitHub grants.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json
import os
import sqlite3
import stat
import sys
import tempfile
from typing import Callable, Iterator


class IdentityConflict(Exception):
    pass


class OutcomeUnknown(Exception):
    """An original commit might have succeeded; observe the same attempt."""


class ProjectionConflict(Exception):
    pass


@dataclass(frozen=True)
class Result:
    attempt_id: str
    status: str
    effect_state: str
    reason: str


def digest(raw: str) -> str:
    return sha256(raw.encode('utf-8')).hexdigest()


def connect(db_file: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_file), timeout=5.0, isolation_level=None)
    conn.execute('PRAGMA foreign_keys=ON')
    conn.execute('PRAGMA busy_timeout=5000')
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=FULL')
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[None]:
    if conn.in_transaction:
        raise RuntimeError('REENTRANT_TRANSACTION_UNSUPPORTED')
    conn.execute('BEGIN IMMEDIATE')
    try:
        yield
        conn.execute('COMMIT')
    except BaseException:
        if conn.in_transaction:
            conn.execute('ROLLBACK')
        raise


def initialize(conn: sqlite3.Connection) -> None:
    conn.executescript('''
    CREATE TABLE IF NOT EXISTS grants (
      grant_id TEXT PRIMARY KEY,
      subject TEXT NOT NULL,
      active INTEGER NOT NULL CHECK(active IN (0,1)),
      version INTEGER NOT NULL CHECK(version > 0)
    );
    CREATE TABLE IF NOT EXISTS attempts (
      attempt_id TEXT PRIMARY KEY,
      grant_id TEXT NOT NULL REFERENCES grants(grant_id),
      subject TEXT NOT NULL,
      payload_digest TEXT NOT NULL,
      state TEXT NOT NULL CHECK(state IN ('PREPARED','BLOCKED','CONFIRMED')),
      reason TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS effects (
      attempt_id TEXT PRIMARY KEY REFERENCES attempts(attempt_id),
      grant_id TEXT NOT NULL,
      subject TEXT NOT NULL,
      payload TEXT NOT NULL,
      payload_digest TEXT NOT NULL,
      grant_version_at_commit INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS audit_events (
      seq INTEGER PRIMARY KEY AUTOINCREMENT,
      kind TEXT NOT NULL,
      grant_id TEXT NOT NULL,
      attempt_id TEXT,
      detail TEXT NOT NULL
    );
    ''')


def create_grant(conn: sqlite3.Connection, grant_id: str, subject: str) -> None:
    if not grant_id or not subject:
        raise ValueError('identity required')
    with transaction(conn):
        conn.execute('INSERT INTO grants VALUES (?,?,1,1)', (grant_id, subject))
        conn.execute('INSERT INTO audit_events(kind,grant_id,attempt_id,detail) VALUES (?,?,NULL,?)',
                     ('GRANT_CREATED', grant_id, subject))


def revoke_grant(conn: sqlite3.Connection, grant_id: str) -> str:
    """Revocation uses exactly the same SQLite write lock as effect commit."""
    with transaction(conn):
        row = conn.execute('SELECT active FROM grants WHERE grant_id=?', (grant_id,)).fetchone()
        if row is None:
            raise IdentityConflict('unknown grant')
        if row[0] == 0:
            return 'ALREADY_REVOKED'
        conn.execute('UPDATE grants SET active=0,version=version+1 WHERE grant_id=?', (grant_id,))
        conn.execute('INSERT INTO audit_events(kind,grant_id,attempt_id,detail) VALUES (?,?,NULL,?)',
                     ('GRANT_REVOKED', grant_id, 'revoked under same write lock'))
        return 'REVOKED'


def prepare_attempt(conn: sqlite3.Connection, attempt_id: str, grant_id: str,
                    subject: str, payload: str) -> Result:
    if not all((attempt_id, grant_id, subject)):
        raise ValueError('identity required')
    h = digest(payload)
    with transaction(conn):
        existing = conn.execute('SELECT grant_id,subject,payload_digest,state,reason FROM attempts WHERE attempt_id=?',
                                (attempt_id,)).fetchone()
        if existing is not None:
            if existing[:3] != (grant_id, subject, h):
                raise IdentityConflict('attempt ID collision; no replay')
            state, reason = existing[3:]
            return Result(attempt_id, state, 'CONFIRMED' if state == 'CONFIRMED' else 'NONE', reason)
        conn.execute('INSERT INTO attempts VALUES (?,?,?,?,?,?)',
                     (attempt_id, grant_id, subject, h, 'PREPARED', 'PREPARED_NO_EFFECT'))
        conn.execute('INSERT INTO audit_events(kind,grant_id,attempt_id,detail) VALUES (?,?,?,?)',
                     ('ATTEMPT_PREPARED', grant_id, attempt_id, h))
    return Result(attempt_id, 'PREPARED', 'NONE', 'PREPARED_NO_EFFECT')


def _inspect_in_transaction(conn: sqlite3.Connection, attempt_id: str) -> Result:
    row = conn.execute('SELECT state,reason FROM attempts WHERE attempt_id=?', (attempt_id,)).fetchone()
    if row is None:
        return Result(attempt_id, 'NOT_FOUND', 'NONE', 'NO_ATTEMPT_RECORD')
    state, reason = row
    effect = conn.execute('SELECT 1 FROM effects WHERE attempt_id=?', (attempt_id,)).fetchone()
    if state == 'CONFIRMED' and effect is None:
        raise OutcomeUnknown('invariant violation: confirmed with missing effect')
    if state != 'CONFIRMED' and effect is not None:
        raise OutcomeUnknown('invariant violation: orphan effect')
    return Result(attempt_id, state, 'CONFIRMED' if state == 'CONFIRMED' else 'NONE', reason)


def inspect_attempt(conn: sqlite3.Connection, attempt_id: str) -> Result:
    # One SQLite read transaction = one consistent snapshot of attempt/effect.
    # Never silently reuse an unknown caller transaction.
    if conn.in_transaction:
        raise RuntimeError('REENTRANT_READ_UNSUPPORTED')
    conn.execute('BEGIN')
    try:
        result = _inspect_in_transaction(conn, attempt_id)
        conn.execute('COMMIT')
        return result
    except BaseException:
        if conn.in_transaction:
            conn.execute('ROLLBACK')
        raise

def commit_effect(conn: sqlite3.Connection, attempt_id: str, *,
                  fault: str | None = None,
                  after_authority_read: Callable[[], None] | None = None) -> Result:
    """Only the DB row is the effect; projection is a separate replayable read model.

    Do not retry on OutcomeUnknown. Reconcile the original attempt ID instead.
    """
    with transaction(conn):
        row = conn.execute('SELECT grant_id,subject,payload_digest,state,reason FROM attempts WHERE attempt_id=?',
                           (attempt_id,)).fetchone()
        if row is None:
            raise IdentityConflict('missing original attempt')
        grant_id, subject, h, state, reason = row
        if state == 'CONFIRMED':
            return _inspect_in_transaction(conn, attempt_id)  # exact, no effect/re-sign
        if state == 'BLOCKED':
            return Result(attempt_id, 'BLOCKED', 'NONE', reason)
        grant = conn.execute('SELECT subject,active,version FROM grants WHERE grant_id=?',
                             (grant_id,)).fetchone()
        if after_authority_read is not None:
            after_authority_read()
        if grant is None or grant[0] != subject or grant[1] != 1:
            conn.execute("UPDATE attempts SET state='BLOCKED',reason='NO_CURRENT_AUTHORITY' WHERE attempt_id=?", (attempt_id,))
            conn.execute('INSERT INTO audit_events(kind,grant_id,attempt_id,detail) VALUES (?,?,?,?)',
                         ('COMMIT_BLOCKED', grant_id, attempt_id, 'NO_CURRENT_AUTHORITY'))
            return Result(attempt_id, 'BLOCKED', 'NONE', 'NO_CURRENT_AUTHORITY')
        # The effect insertion and the current grant check are one transaction.
        # The grant cannot be revoked between this check and this insert/COMMIT.
        conn.execute('INSERT INTO effects VALUES (?,?,?,?,?,?)',
                     (attempt_id, grant_id, subject, h, h, grant[2]))
        conn.execute("UPDATE attempts SET state='CONFIRMED',reason='COMMITTED_WITH_CURRENT_AUTHORITY' WHERE attempt_id=?",
                     (attempt_id,))
        conn.execute('INSERT INTO audit_events(kind,grant_id,attempt_id,detail) VALUES (?,?,?,?)',
                     ('EFFECT_COMMITTED', grant_id, attempt_id, f'version={grant[2]}'))
        if fault == 'exit_before_commit':
            # Real process death; SQLite journal recovery rolls all changes back.
            os._exit(72)
        if fault == 'exception_before_commit':
            raise RuntimeError('forced failure inside uncommitted transaction')
    if fault == 'after_commit_receipt_lost':
        raise OutcomeUnknown('receipt lost after successful original commit; OBSERVE')
    return Result(attempt_id, 'CONFIRMED', 'CONFIRMED', 'COMMITTED_WITH_CURRENT_AUTHORITY')


def effect_count(conn: sqlite3.Connection) -> int:
    return conn.execute('SELECT count(*) FROM effects').fetchone()[0]


def committed_count_for_attempt(conn: sqlite3.Connection, attempt_id: str) -> int:
    return conn.execute("SELECT count(*) FROM audit_events WHERE kind='EFFECT_COMMITTED' AND attempt_id=?",
                        (attempt_id,)).fetchone()[0]


def project_committed_effect(conn: sqlite3.Connection, attempt_id: str,
                             output_dir: str | Path, *, fault: str | None = None) -> str:
    """Idempotent *derived* projection; never confers or changes DB authority.

    POSIX create-only hardlink avoids replacing an existing projection. A crash
    can leave staging, but DB COMMIT remains authoritative; repair by original ID.
    """
    result = inspect_attempt(conn, attempt_id)
    if result.effect_state != 'CONFIRMED':
        raise IdentityConflict('no confirmed effect to project')
    row = conn.execute('SELECT grant_id,subject,payload_digest FROM effects WHERE attempt_id=?',
                       (attempt_id,)).fetchone()
    if row is None:
        raise OutcomeUnknown('missing confirmed source')
    grant_id, subject, payload_hash = row
    data = (json.dumps({'schema':'ts-authority-projection/v0','attempt_id':attempt_id,
                        'grant_id':grant_id,'subject':subject,'payload_sha256':payload_hash},
                       sort_keys=True,separators=(',',':')) + '\n').encode()
    folder = Path(output_dir)
    if folder.is_symlink():
        raise ProjectionConflict('projection root symlink')
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    if folder.is_symlink():
        raise ProjectionConflict('projection root changed')
    target = folder / (digest(attempt_id) + '.json')
    if target.exists() or target.is_symlink():
        if target.is_symlink() or not target.is_file() or target.read_bytes() != data:
            raise ProjectionConflict('existing projection conflicts with committed ledger')
        return 'EXACT'
    fd, staged = tempfile.mkstemp(prefix='.stage-', dir=folder)
    try:
        with os.fdopen(fd, 'wb') as handle:
            os.fchmod(handle.fileno(), 0o600)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if fault == 'before_link':
            raise OutcomeUnknown('projection interrupted; DB remains CONFIRMED')
        try:
            os.link(staged, target, follow_symlinks=False)
        except FileExistsError:
            if not target.is_file() or target.is_symlink() or target.read_bytes() != data:
                raise ProjectionConflict('concurrent projection content mismatch')
            return 'EXACT'
        directory_fd = os.open(folder, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        return 'CREATED'
    finally:
        Path(staged).unlink(missing_ok=True)


def _main() -> int:
    if len(sys.argv) == 4 and sys.argv[1] in ('crash-before-commit','crash-after-commit'):
        db, attempt_id = sys.argv[2:]
        conn = connect(db)
        if sys.argv[1] == 'crash-before-commit':
            commit_effect(conn, attempt_id, fault='exit_before_commit')
            raise AssertionError('unreachable exit hook')
        commit_effect(conn, attempt_id)
        os._exit(73)  # real process death AFTER COMMIT, BEFORE returning receipt
    print('This is an experimental library, not a Product executable.', file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(_main())
