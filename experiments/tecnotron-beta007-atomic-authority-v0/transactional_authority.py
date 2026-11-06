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
from typing import Iterator


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
                  fault: str | None = None) -> Result:
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
    """Idempotent read-model, with POSIX directory-descriptor anchored writes.

    A previously committed DB row is the only authority. The caller must supply
    an output root under a *trusted parent*; untrusted ancestors, same-UID/root
    attackers, NFS and hostile mounts remain explicitly outside this V0 model.
    """
    if not all(hasattr(os, flag) for flag in ['O_DIRECTORY','O_NOFOLLOW']):
        raise ProjectionConflict('POSIX_DIRECTORY_DESCRIPTORS_REQUIRED')
    if conn.in_transaction:
        raise RuntimeError('REENTRANT_READ_UNSUPPORTED')
    # Status and immutable committed payload are observed under ONE consistent
    # SQLite snapshot, not two independent read transactions. Nothing here
    # creates or refreshes a Developer grant or Product authority.
    conn.execute('BEGIN')
    try:
        result = _inspect_in_transaction(conn, attempt_id)
        if result.effect_state != 'CONFIRMED':
            raise IdentityConflict('no confirmed effect to project')
        row = conn.execute('SELECT grant_id,subject,payload_digest FROM effects WHERE attempt_id=?',
                           (attempt_id,)).fetchone()
        if row is None:
            raise OutcomeUnknown('missing confirmed source')
        conn.execute('COMMIT')
    except BaseException:
        if conn.in_transaction:
            conn.execute('ROLLBACK')
        raise
    grant_id, subject, payload_hash = row
    data = (json.dumps({'schema':'ts-authority-projection/v0','attempt_id':attempt_id,
                        'grant_id':grant_id,'subject':subject,'payload_sha256':payload_hash},
                       sort_keys=True,separators=(',',':')) + '\n').encode()
    folder = Path(output_dir)
    # Only the final directory is pinned; trust of its ancestors is a required
    # external precondition, not something path.is_symlink() can prove.
    if folder.is_symlink():
        raise ProjectionConflict('projection root is a symlink')
    folder.mkdir(mode=0o700, exist_ok=True)  # no implicit parent creation
    dir_fd = os.open(folder, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        st = os.fstat(dir_fd)
        if (not os.path.samestat(st, os.stat(folder, follow_symlinks=False))
                or st.st_uid != os.getuid() or (st.st_mode & 0o777) != 0o700):
            raise ProjectionConflict('unqualified or changed output directory')
        target_name = digest(attempt_id) + '.json'

        def existing_target() -> bool:
            try:
                read_fd = os.open(target_name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=dir_fd)
            except FileNotFoundError:
                return False
            except OSError as exc:
                raise ProjectionConflict('unsafe existing projection') from exc
            with os.fdopen(read_fd, 'rb') as handle:
                entry_stat = os.fstat(handle.fileno())
                if (not stat.S_ISREG(entry_stat.st_mode) or entry_stat.st_nlink != 1
                        or entry_stat.st_size != len(data) or entry_stat.st_uid != os.getuid()):
                    raise ProjectionConflict('unqualified projection inode')
                if handle.read(len(data) + 1) != data:
                    raise ProjectionConflict('existing projection differs from committed ledger')
            return True

        if existing_target():
            return 'EXACT'
        # Staging, link and cleanup all resolve RELATIVE TO ONE DIR FD, never
        # reopening the path between stage and publication.
        name = '.stage-' + os.urandom(16).hex()
        fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=dir_fd)
        try:
            with os.fdopen(fd, 'wb') as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            if fault == 'before_link':
                raise OutcomeUnknown('projection interrupted; DB remains CONFIRMED')
            try:
                os.link(name, target_name, src_dir_fd=dir_fd, dst_dir_fd=dir_fd,
                        follow_symlinks=False)
            except FileExistsError:
                if not existing_target():
                    raise ProjectionConflict('concurrent projection vanished')
                return 'EXACT'
            os.fsync(dir_fd)
            return 'CREATED'
        finally:
            os.unlink(name, dir_fd=dir_fd)
            # Final directory state is durable only after the stage unlink has
            # also been fsynced. Never mistake this for host power-loss proof.
            os.fsync(dir_fd)
    finally:
        os.close(dir_fd)

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
