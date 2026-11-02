"""Public H6 Attendance V0 service boundary (stdlib only)."""
from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any

_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z", re.ASCII)
_RFC3339 = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})\Z")

class AttendanceError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def subject_id(value: Any) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise AttendanceError("INVALID_ARGUMENT", "invalid subject_id")
    return value


def request_id(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise AttendanceError("INVALID_ARGUMENT", "invalid request_id")
    return value


def utc(value: Any) -> str:
    if not isinstance(value, str) or not _RFC3339.fullmatch(value):
        raise AttendanceError("INVALID_ARGUMENT", "timestamp must be RFC3339 with timezone")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError("naive")
        return dt.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    except ValueError as exc:
        raise AttendanceError("INVALID_ARGUMENT", "invalid timestamp") from exc


def mapping(payload: Any, required: set[str], optional: set[str] = frozenset()) -> dict:
    if not isinstance(payload, dict) or not required <= payload.keys() or not payload.keys() <= required | optional:
        raise AttendanceError("INVALID_ARGUMENT", "invalid operation arguments")
    return payload


class AttendanceService:
    """Logical API. The caller supplies a private SQLite file path."""

    def __init__(self, database_path: str):
        from attendance.storage.sqlite_store import SQLiteAttendanceStore
        self.store = SQLiteAttendanceStore(database_path)

    def checkIn(self, payload: dict) -> dict:
        args = mapping(payload, {"subject_id", "occurred_at"}, {"request_id"})
        return self.store.transition("checkIn", subject_id(args["subject_id"]), utc(args["occurred_at"]), request_id(args.get("request_id")))

    def checkOut(self, payload: dict) -> dict:
        args = mapping(payload, {"subject_id", "occurred_at"}, {"request_id"})
        return self.store.transition("checkOut", subject_id(args["subject_id"]), utc(args["occurred_at"]), request_id(args.get("request_id")))

    def getState(self, payload: dict) -> dict:
        args = mapping(payload, {"subject_id"})
        return self.store.state(subject_id(args["subject_id"]))

    def listSessions(self, payload: dict) -> list[dict]:
        args = mapping(payload, {"subject_id", "from", "to"})
        start, end = utc(args["from"]), utc(args["to"])
        if start >= end:
            raise AttendanceError("INVALID_ARGUMENT", "from must precede to")
        return self.store.sessions(subject_id(args["subject_id"]), start, end)
