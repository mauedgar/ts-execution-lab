"""Strict validation of real persisted v1 rows before grandfather migration."""
import json
import re
from attendance.core.service import AttendanceError, to_public, utc

UUID4 = re.compile(r"[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}\Z")
OPAQUE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z")
CANONICAL = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z\Z")


def original_stamp(value):
    """Only canonical microsecond UTC text the original v1 parser emitted."""
    if not isinstance(value, str) or CANONICAL.fullmatch(value) is None:
        raise AttendanceError('STORAGE_ERROR', 'malformed historical UTC timestamp')
    try:
        key = utc(value)
    except AttendanceError as exc:
        raise AttendanceError('STORAGE_ERROR', 'invalid historical UTC timestamp') from exc
    if to_public(key) != value:
        raise AttendanceError('STORAGE_ERROR', 'noncanonical historical UTC timestamp')
    return key


def validate_session_identity(row):
    if (not isinstance(row['session_id'], str) or UUID4.fullmatch(row['session_id']) is None or
        not isinstance(row['subject_id'], str) or OPAQUE.fullmatch(row['subject_id']) is None):
        raise AttendanceError('STORAGE_ERROR', 'invalid historical session identity')


def migrate_request(conn, row):
    """No invented original bytes: require provably v1-shaped schema and response."""
    try:
        sid, rid = row['subject_id'], row['request_id']
        if (not isinstance(sid, str) or OPAQUE.fullmatch(sid) is None or
            not isinstance(rid, str) or OPAQUE.fullmatch(rid) is None):
            raise ValueError('invalid historical opaque IDs')
        original = json.loads(row['payload'])
        response = json.loads(row['response'])
        if (not isinstance(original, dict) or
            set(original) != {'operation', 'occurred_at'} or
            original['operation'] not in ('checkIn','checkOut') or
            original['operation'] != row['operation'] or
            json.dumps(original, sort_keys=True, separators=(',', ':')) != row['payload'] or
            not isinstance(response, dict) or
            set(response) != {'session_id','subject_id','checked_in_at','checked_out_at'} or
            response['subject_id'] != sid or
            not isinstance(response['session_id'], str) or
            UUID4.fullmatch(response['session_id']) is None):
            raise ValueError('invalid historical signature or response')
        occurred = original_stamp(original['occurred_at'])
        checked_in = original_stamp(response['checked_in_at'])
        checked_out = (original_stamp(response['checked_out_at'])
                       if response['checked_out_at'] is not None else None)
        persisted = conn.execute(
            'SELECT subject_id,checked_in_at,checked_out_at FROM sessions WHERE session_id=?',
            (response['session_id'],)).fetchone()
        if (persisted is None or persisted['subject_id'] != sid or
            persisted['checked_in_at'] != checked_in):
            raise ValueError('response not linked to actual session')
        if original['operation'] == 'checkIn':
            if checked_out is not None or occurred != checked_in:
                raise ValueError('invalid historical checkIn response')
        elif (checked_out is None or occurred != checked_out or
              persisted['checked_out_at'] != checked_out):
            raise ValueError('invalid historical checkOut response')
        return json.dumps({'signature_version': 1,'operation': original['operation'],
                           'utc_occurred_at': occurred},sort_keys=True,separators=(',', ':'))
    except (KeyError,TypeError,ValueError,AttendanceError,UnicodeError) as exc:
        raise AttendanceError('STORAGE_ERROR', 'corrupt historical request') from exc
