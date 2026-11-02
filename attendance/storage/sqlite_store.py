"""Transactionally safe SQLite backend for H6 Attendance V0."""
from __future__ import annotations

import json
from contextlib import closing
from pathlib import Path
import sqlite3
import uuid

from attendance.core.service import AttendanceError


class SQLiteAttendanceStore:
    def __init__(self, database_path: str):
        if not isinstance(database_path, (str, Path)) or not str(database_path) or str(database_path) == ':memory:':
            raise AttendanceError('INVALID_ARGUMENT', 'a filesystem SQLite path is required')
        self.path = str(database_path)
        self._setup()

    def _connect(self):
        conn = sqlite3.connect(self.path, isolation_level=None, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys=ON')
        conn.execute('PRAGMA busy_timeout=15000')
        return conn

    def _setup(self):
        try:
            with closing(self._connect()) as conn:
                conn.execute('BEGIN IMMEDIATE')
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
                conn.execute('PRAGMA user_version=1')
                conn.commit()
        except sqlite3.Error as exc:
            raise AttendanceError('STORAGE_ERROR', 'SQLite setup failure') from exc

    @staticmethod
    def _session(row):
        return {k: row[k] for k in ('session_id', 'subject_id', 'checked_in_at', 'checked_out_at')}

    def transition(self, operation: str, subject: str, occurred_at: str, request_id: str | None):
        signature = json.dumps({'operation': operation, 'occurred_at': occurred_at}, sort_keys=True, separators=(',', ':'))
        conn = None
        try:
            conn = self._connect()
            conn.execute('BEGIN IMMEDIATE')
            if request_id is not None:
                previous = conn.execute('SELECT payload,response FROM requests WHERE subject_id=? AND request_id=?', (subject, request_id)).fetchone()
                if previous is not None:
                    if previous['payload'] != signature:
                        raise AttendanceError('REQUEST_CONFLICT', 'request_id used for different arguments')
                    response = json.loads(previous['response'])
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
                session = {'session_id': uuid.uuid4().hex, 'subject_id': subject, 'checked_in_at': occurred_at, 'checked_out_at': None}
                conn.execute('INSERT INTO sessions(session_id,subject_id,checked_in_at,checked_out_at) VALUES(?,?,?,NULL)',
                             (session['session_id'], subject, occurred_at))
            elif operation == 'checkOut':
                if not active:
                    raise AttendanceError('NO_OPEN_SESSION', 'subject has no open interval')
                if occurred_at <= active['checked_in_at']:
                    raise AttendanceError('NON_MONOTONIC_TIME', 'check-out must follow check-in')
                conn.execute('UPDATE sessions SET checked_out_at=? WHERE session_id=?', (occurred_at, active['session_id']))
                session = self._session(active)
                session['checked_out_at'] = occurred_at
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
                rows = conn.execute('''SELECT * FROM sessions WHERE subject_id=? AND checked_in_at>=? AND checked_in_at<?
                                      ORDER BY checked_in_at, session_id''', (subject, start, end)).fetchall()
                return [self._session(row) for row in rows]
        except sqlite3.Error as exc:
            raise AttendanceError('STORAGE_ERROR', 'SQLite read failure') from exc
