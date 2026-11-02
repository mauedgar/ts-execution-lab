"""Fail-closed SQLite compatibility admission for persisted H6 V0."""
import json
import re
from attendance.core.service import AttendanceError, to_public, utc
from attendance.storage.legacy_v1 import original_stamp, validate_session_identity, OPAQUE

_TABLES = {
 'subjects': [('subject_id','TEXT',1)],
 'sessions': [('session_id','TEXT',1),('subject_id','TEXT',0),
              ('checked_in_at','TEXT',0),('checked_out_at','TEXT',0)],
 'requests': [('subject_id','TEXT',1),('request_id','TEXT',2),
              ('operation','TEXT',0),('payload','TEXT',0),('response','TEXT',0)]
}


def _reject(message):
    raise AttendanceError('STORAGE_ERROR',message)


def _unique_index(conn, table, cols, partial=None):
    for row in conn.execute(f'PRAGMA index_list("{table}")'):
        if row[2] != 1 or (partial is not None and row[4] != int(partial)):
            continue
        names = [x[2] for x in conn.execute(f'PRAGMA index_info("{row[1]}")')]
        if names != list(cols):
            continue
        if partial:
            sql = conn.execute('SELECT sql FROM sqlite_master WHERE type=? AND name=?',
                               ('index',row[1])).fetchone()
            if sql is None or sql[0] is None:
                continue
            norm = re.sub(r'\s+', '', sql[0]).lower()
            original = re.sub(r'\s+', '',
                'CREATE UNIQUE INDEX one_open_session '
                'ON sessions(subject_id) WHERE checked_out_at IS NULL').lower()
            if norm != original:
                continue
        return True
    return False


def verify_original_v1_schema(conn):
    # Must be called BEFORE CREATE TABLE/INDEX IF NOT EXISTS can conceal a mismatch.
    for name, expected in _TABLES.items():
        entry = conn.execute('SELECT type FROM sqlite_master WHERE name=?',(name,)).fetchone()
        if entry is None or entry[0] != 'table':
            _reject('missing original v1 table')
        actual = [(r[1],r[2].upper(),r[5]) for r in conn.execute(f'PRAGMA table_info("{name}")')]
        if actual != expected:
            _reject('altered historical table constraints')
    # The original producer DDL is a stronger invariant than PRAGMA version.
    # In particular CHECK, foreign-key and partial-index semantics must match.
    original_ddl = {
        'subjects': 'CREATE TABLE subjects (subject_id TEXT PRIMARY KEY)',
        'sessions': ('CREATE TABLE sessions ('
                     'session_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL REFERENCES subjects(subject_id), '
                     'checked_in_at TEXT NOT NULL, checked_out_at TEXT, '
                     'CHECK (checked_out_at IS NULL OR checked_out_at > checked_in_at))'),
        'requests': ('CREATE TABLE requests ('
                     'subject_id TEXT NOT NULL, request_id TEXT NOT NULL, operation TEXT NOT NULL, '
                     'payload TEXT NOT NULL, response TEXT NOT NULL, '
                     'PRIMARY KEY (subject_id, request_id), FOREIGN KEY(subject_id) REFERENCES subjects(subject_id))')
    }
    for name, expected_sql in original_ddl.items():
        row = conn.execute('SELECT sql FROM sqlite_master WHERE type=? AND name=?',
                           ('table',name)).fetchone()
        if row is None or not isinstance(row[0],str):
            _reject('missing historical table definition')
        if re.sub(r'\s+','',row[0]).lower() != re.sub(r'\s+','',expected_sql).lower():
            _reject('nonoriginal v1 DDL')

    for table, cols, partial in (
        ('subjects', ['subject_id'],False),
        ('sessions',['session_id'],False),
        ('requests',['subject_id','request_id'],False),
        ('sessions',['subject_id'],True)):
        if not _unique_index(conn,table,cols,partial):
            _reject('missing historical uniqueness constraint')
    for child in ('sessions','requests'):
        if not any(r[2]=='subjects' and r[3]=='subject_id' and r[4]=='subject_id'
                   for r in conn.execute(f'PRAGMA foreign_key_list("{child}")')):
            _reject('missing historical foreign key')
    if conn.execute('PRAGMA foreign_key_check').fetchone() is not None:
        _reject('historical foreign key violation')


def verify_original_v1_intervals(conn):
    # One original v1 operation creates a subject only along with a session.
    cursor = conn.execute('SELECT subject_id FROM subjects')
    while True:
        chunk = cursor.fetchmany(128)
        if not chunk:
            break
        for (sid,) in chunk:
            if not isinstance(sid,str) or OPAQUE.fullmatch(sid) is None:
                _reject('invalid historical subject')
            if conn.execute('SELECT 1 FROM sessions WHERE subject_id=? LIMIT 1',(sid,)).fetchone() is None:
                _reject('orphan historical subject')
    cursor = conn.execute('SELECT session_id,subject_id,checked_in_at,checked_out_at '
                          'FROM sessions ORDER BY subject_id,checked_in_at,session_id')
    last_subject,last_finish=None,None
    while True:
        chunk=cursor.fetchmany(128)
        if not chunk:
            break
        for row in chunk:
            validate_session_identity(row)
            entered=original_stamp(row['checked_in_at'])
            exited=original_stamp(row['checked_out_at']) if row['checked_out_at'] is not None else None
            if exited is not None and exited<=entered:
                _reject('invalid historical interval')
            if row['subject_id']==last_subject and (last_finish is None or entered<=last_finish):
                _reject('overlapping historical sessions')
            last_subject,last_finish=row['subject_id'],exited


def verify_persisted_response(conn, previous, subject, operation):
    try:
        response=json.loads(previous['response'])
        if (not isinstance(response,dict) or
            set(response)!={'session_id','subject_id','checked_in_at','checked_out_at'} or
            response['subject_id']!=subject or
            not isinstance(response['session_id'],str) or not response['session_id'] or
            not isinstance(response['checked_in_at'],str) or
            not (response['checked_out_at'] is None or isinstance(response['checked_out_at'],str))):
            raise ValueError('invalid Session shape')
        entered=utc(response['checked_in_at'])
        exited=utc(response['checked_out_at']) if response['checked_out_at'] is not None else None
        if to_public(entered)!=response['checked_in_at']:
            raise ValueError('noncanonical checked_in_at')
        if exited is not None and to_public(exited)!=response['checked_out_at']:
            raise ValueError('noncanonical checked_out_at')
        session=conn.execute('SELECT subject_id,checked_in_at,checked_out_at FROM sessions WHERE session_id=?',
                             (response['session_id'],)).fetchone()
        if session is None or session['subject_id']!=subject or session['checked_in_at']!=entered:
            raise ValueError('unmatched persisted Session')
        if operation=='checkIn':
            if exited is not None:
                raise ValueError('invalid checkIn response')
        elif operation=='checkOut':
            if exited is None or session['checked_out_at']!=exited:
                raise ValueError('invalid checkOut response')
        else:
            raise ValueError('invalid operation')
        return response
    except (ValueError,TypeError,KeyError,AttendanceError,UnicodeError) as exc:
        raise AttendanceError('STORAGE_ERROR','corrupt persisted Session') from exc
