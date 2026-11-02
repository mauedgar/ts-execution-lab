"""Transactionally safe SQLite backend for H6 Attendance V0."""
from __future__ import annotations

import json
from contextlib import closing
from pathlib import Path
import sqlite3
import uuid

from attendance.core.service import AttendanceError, to_public
from attendance.storage.legacy_v1 import original_stamp, validate_session_identity, migrate_request
from attendance.storage.integrity import verify_original_v1_schema, verify_original_v1_intervals, verify_persisted_response


class SQLiteAttendanceStore:
    def __init__(self, database_path: str):
        if not isinstance(database_path, (str, Path)):
            raise AttendanceError('INVALID_ARGUMENT', 'a filesystem SQLite path is required')
        try:
            path = str(database_path)
            path.encode('utf-8', errors='strict')
        except (UnicodeError, ValueError, TypeError) as exc:
            raise AttendanceError('INVALID_ARGUMENT', 'invalid SQLite filesystem path') from exc
        if not path or path == ':memory:' or '\x00' in path:
            raise AttendanceError('INVALID_ARGUMENT', 'invalid SQLite filesystem path')
        self.path = path
        self._setup()

    def _connect(self):
        conn = sqlite3.connect(self.path, isolation_level=None, timeout=15)
        try:
            conn.row_factory = sqlite3.Row
            conn.execute('PRAGMA foreign_keys=ON')
            conn.execute('PRAGMA busy_timeout=15000')
            return conn
        except Exception:
            conn.close()
            raise

    def _setup(self):
        try:
            with closing(self._connect()) as conn:
                conn.execute('BEGIN IMMEDIATE')
                version = conn.execute('PRAGMA user_version').fetchone()[0]
                if version not in (0, 1, 2):
                    raise AttendanceError('STORAGE_ERROR', 'unsupported future SQLite schema version')
                if version == 0:
                    if conn.execute("SELECT 1 FROM sqlite_master WHERE type IN ('table','view','trigger','index') "
                                    "AND name NOT LIKE 'sqlite_%' LIMIT 1").fetchone() is not None:
                        raise AttendanceError('STORAGE_ERROR','unknown unversioned nonempty SQLite file')
                if version == 1:
                    verify_original_v1_schema(conn)
                    verify_original_v1_intervals(conn)
                elif version == 2:
                    verify_original_v1_schema(conn, version=2)
                conn.execute('CREATE TABLE IF NOT EXISTS subjects (subject_id TEXT PRIMARY KEY)')
                conn.execute('''CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL REFERENCES subjects(subject_id),
                    checked_in_at TEXT NOT NULL, checked_out_at TEXT,
                    CHECK (checked_out_at IS NULL OR checked_out_at > checked_in_at))''')
                conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS one_open_session ON sessions(subject_id) WHERE checked_out_at IS NULL')
                conn.execute('CREATE INDEX IF NOT EXISTS sessions_order ON sessions(subject_id,checked_in_at,session_id)')
                conn.execute('''CREATE TABLE IF NOT EXISTS requests (
                    subject_id TEXT NOT NULL, request_id TEXT NOT NULL, operation TEXT NOT NULL,
                    payload TEXT NOT NULL, response TEXT NOT NULL,
                    PRIMARY KEY (subject_id, request_id), FOREIGN KEY(subject_id) REFERENCES subjects(subject_id))''')
                # Atomic provenance ledger is populated ONLY by verified v1
                # migration; future schema-v2 keys are never grandfathered.
                conn.execute('''CREATE TABLE IF NOT EXISTS v1_provenance (
                    subject_id TEXT NOT NULL, request_id TEXT NOT NULL,
                    operation TEXT NOT NULL, utc_occurred_at TEXT NOT NULL,
                    PRIMARY KEY(subject_id,request_id),
                    FOREIGN KEY(subject_id,request_id)
                    REFERENCES requests(subject_id,request_id))''')
                if version == 1:
                    # Migrate in keyset batches, with bounded memory usage.
                    # Original v1 stored canonical UTC but not raw argument bytes.
                    last_session_id = None
                    while True:
                        if last_session_id is None:
                            rows = conn.execute(
                                'SELECT session_id,subject_id,checked_in_at,checked_out_at '
                                'FROM sessions ORDER BY session_id LIMIT 128').fetchall()
                        else:
                            rows = conn.execute(
                                'SELECT session_id,subject_id,checked_in_at,checked_out_at '
                                'FROM sessions WHERE session_id>? ORDER BY session_id LIMIT 128',
                                (last_session_id,)).fetchall()
                        if not rows:
                            break
                        for row in rows:
                            validate_session_identity(row)
                            entered = original_stamp(row['checked_in_at'])
                            exited = original_stamp(row['checked_out_at']) if row['checked_out_at'] is not None else None
                            if exited is not None and exited <= entered:
                                raise AttendanceError('STORAGE_ERROR', 'invalid historical interval')
                            conn.execute('UPDATE sessions SET checked_in_at=?, checked_out_at=? WHERE session_id=?',
                                         (entered, exited, row['session_id']))
                        last_session_id = rows[-1]['session_id']
                    last_subject, last_request = None, None
                    while True:
                        if last_subject is None:
                            requests = conn.execute(
                                'SELECT subject_id,request_id,operation,payload,response '
                                'FROM requests ORDER BY subject_id,request_id LIMIT 128').fetchall()
                        else:
                            requests = conn.execute(
                                'SELECT subject_id,request_id,operation,payload,response FROM requests '
                                'WHERE (subject_id,request_id)>(?,?) '
                                'ORDER BY subject_id,request_id LIMIT 128',
                                (last_subject, last_request)).fetchall()
                        if not requests:
                            break
                        for req in requests:
                            marked = migrate_request(conn, req)
                            proof = json.loads(marked)
                            conn.execute('INSERT INTO v1_provenance '
                                         '(subject_id,request_id,operation,utc_occurred_at) VALUES(?,?,?,?)',
                                         (req['subject_id'],req['request_id'],proof['operation'],
                                          proof['utc_occurred_at']))
                            conn.execute('UPDATE requests SET payload=? WHERE subject_id=? AND request_id=?',
                                         (marked, req['subject_id'], req['request_id']))
                        last_subject, last_request = requests[-1]['subject_id'], requests[-1]['request_id']
                if version < 2:
                    verify_original_v1_schema(conn, version=2)
                    conn.execute('PRAGMA user_version=2')
                conn.commit()
        except sqlite3.Error as exc:
            raise AttendanceError('STORAGE_ERROR', 'SQLite setup failure') from exc

    @staticmethod
    def _session(row):
        from attendance.core.service import utc
        result = {k: row[k] for k in ('session_id', 'subject_id', 'checked_in_at', 'checked_out_at')}
        try:
            if (not isinstance(result['session_id'],str) or not result['session_id'] or
                not isinstance(result['subject_id'],str) or
                not isinstance(result['checked_in_at'],str) or
                not (result['checked_out_at'] is None or isinstance(result['checked_out_at'],str))):
                raise ValueError('invalid Session type')
            entered = to_public(result['checked_in_at'])
            if utc(entered) != result['checked_in_at']:
                raise ValueError('noncanonical stored check-in time')
            closed = (to_public(result['checked_out_at'])
                      if result['checked_out_at'] is not None else None)
            if closed is not None:
                if utc(closed) != result['checked_out_at'] or result['checked_out_at'] <= result['checked_in_at']:
                    raise ValueError('invalid stored check-out time')
            result['checked_in_at'], result['checked_out_at'] = entered, closed
            return result
        except (ValueError, TypeError, AttendanceError) as exc:
            raise AttendanceError('STORAGE_ERROR', 'corrupt stored Session') from exc

    def transition(self, operation: str, subject: str, occurred_at: str, request_id: str | None, raw_occurred_at: str):
        # Identical arguments means literal caller arguments, NOT UTC equivalence.
        signature = json.dumps({'operation': operation, 'occurred_at': raw_occurred_at}, sort_keys=True, separators=(',', ':'))
        conn = None
        try:
            conn = self._connect()
            conn.execute('BEGIN IMMEDIATE')
            if request_id is not None:
                previous = conn.execute('SELECT operation,payload,response FROM requests WHERE subject_id=? AND request_id=?', (subject, request_id)).fetchone()
                if previous is not None:
                    try:
                        previous_sig = json.loads(previous['payload'])
                        if not isinstance(previous_sig, dict):
                            raise ValueError('request signature must be object')
                    except (ValueError, TypeError) as exc:
                        raise AttendanceError('STORAGE_ERROR', 'corrupt stored request signature') from exc
                    kind=previous_sig.get('signature_version')
                    if type(kind) is int and kind == 1 and set(previous_sig) == {
                        'signature_version','operation','utc_occurred_at'
                    }:
                        if not isinstance(previous_sig.get('utc_occurred_at'),str):
                            raise AttendanceError('STORAGE_ERROR','invalid historical signature')
                        proof = conn.execute('SELECT operation,utc_occurred_at FROM v1_provenance '
                                             'WHERE subject_id=? AND request_id=?',
                                             (subject,request_id)).fetchone()
                        if (proof is None or proof['operation'] != previous_sig.get('operation') or
                            proof['utc_occurred_at'] != previous_sig['utc_occurred_at']):
                            raise AttendanceError('STORAGE_ERROR','missing original v1 provenance')
                        identical=(previous_sig.get('operation')==operation and
                                   previous_sig['utc_occurred_at']==occurred_at)
                    elif 'signature_version' not in previous_sig:
                        if set(previous_sig)!={'operation','occurred_at'}:
                            raise AttendanceError('STORAGE_ERROR','invalid v2 signature')
                        identical=previous['payload']==signature
                    else:
                        raise AttendanceError('STORAGE_ERROR','unsupported signature version')
                    if previous['operation']!=operation or previous_sig.get('operation')!=operation:
                        raise AttendanceError('REQUEST_CONFLICT','request_id reused across operations')
                    if not identical:
                        raise AttendanceError('REQUEST_CONFLICT','request_id used for different arguments')
                    response=verify_persisted_response(conn,previous,subject,operation)
                    conn.commit()
                    return response
            active = conn.execute('SELECT * FROM sessions WHERE subject_id=? AND checked_out_at IS NULL', (subject,)).fetchone()
            if operation == 'checkIn':
                if active:
                    raise AttendanceError('ALREADY_OPEN', 'subject has an open interval')
                last = conn.execute('SELECT MAX(checked_out_at) AS finished FROM sessions WHERE subject_id=?', (subject,)).fetchone()
                if last and last['finished'] is not None and occurred_at <= last['finished']:
                    raise AttendanceError('NON_MONOTONIC_TIME', 'check-in must follow last check-out')
                conn.execute('INSERT OR IGNORE INTO subjects(subject_id) VALUES(?)', (subject,))
                session = {'session_id': uuid.uuid4().hex, 'subject_id': subject, 'checked_in_at': to_public(occurred_at), 'checked_out_at': None}
                conn.execute('INSERT INTO sessions(session_id,subject_id,checked_in_at,checked_out_at) VALUES(?,?,?,NULL)',
                             (session['session_id'], subject, occurred_at))
            elif operation == 'checkOut':
                if not active:
                    raise AttendanceError('NO_OPEN_SESSION', 'subject has no open interval')
                if occurred_at <= active['checked_in_at']:
                    raise AttendanceError('NON_MONOTONIC_TIME', 'check-out must follow check-in')
                conn.execute('UPDATE sessions SET checked_out_at=? WHERE session_id=?', (occurred_at, active['session_id']))
                session = self._session(active)
                session['checked_out_at'] = to_public(occurred_at)
            else:
                raise AttendanceError('INVALID_ARGUMENT', 'unsupported transition')
            if request_id is not None:
                conn.execute('INSERT INTO requests(subject_id,request_id,operation,payload,response) VALUES(?,?,?,?,?)',
                             (subject, request_id, operation, signature, json.dumps(session, sort_keys=True)))
            conn.commit()
            return session
        except sqlite3.Error as exc:
            if conn:
                conn.rollback()
            raise AttendanceError('STORAGE_ERROR', 'SQLite transaction failure') from exc
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def _known(self, conn, subject):
        if conn.execute('SELECT 1 FROM subjects WHERE subject_id=?', (subject,)).fetchone() is None:
            raise AttendanceError('NOT_FOUND', 'subject does not exist')

    def state(self, subject: str):
        try:
            with closing(self._connect()) as conn:
                self._known(conn, subject)
                active = conn.execute('SELECT * FROM sessions WHERE subject_id=? AND checked_out_at IS NULL', (subject,)).fetchone()
                return {'subject_id': subject, 'active': active is not None, 'active_session': self._session(active) if active else None}
        except sqlite3.Error as exc:
            raise AttendanceError('STORAGE_ERROR', 'SQLite read failure') from exc

    def sessions(self, subject: str, start: str, end: str):
        try:
            with closing(self._connect()) as conn:
                self._known(conn, subject)
                cursor=conn.execute('''SELECT * FROM sessions WHERE subject_id=? AND checked_in_at>=? AND checked_in_at<?
                                       ORDER BY checked_in_at, session_id LIMIT 10001''', (subject,start,end))
                # The V0 Session[] necessarily materializes final output, but SQL fetch is bounded.
                result=[]
                while True:
                    chunk=cursor.fetchmany(128)
                    if not chunk:
                        break
                    if len(result) + len(chunk) > 10000:
                        raise AttendanceError('INVALID_ARGUMENT', 'result exceeds H6 V0 10000-session budget; narrow from/to')
                    result.extend(self._session(row) for row in chunk)
                return result
        except sqlite3.Error as exc:
            raise AttendanceError('STORAGE_ERROR', 'SQLite read failure') from exc

