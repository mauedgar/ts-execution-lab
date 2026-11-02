"""Public H6 Attendance V0 service boundary (stdlib only)."""
from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any

_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z", re.ASCII)
_RFC3339 = re.compile(
    r"([0-9]{4}-[0-9]{2}-[0-9]{2})[Tt]([0-9]{2}:[0-9]{2}:[0-9]{2})"
    r"(?:\.([0-9]+))?([Zz]|[+-][0-9]{2}:[0-9]{2})\Z"
)

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
    """Normalize an RFC3339 instant without discarding fractional precision.

    Canonical internal values omit 'Z' so that a stripped, variable-length
    fractional portion sorts correctly as text in SQLite. The public API
    converts them back to RFC3339 with at least six decimal places.
    """
    match = _RFC3339.fullmatch(value) if isinstance(value, str) else None
    if match is None:
        raise AttendanceError("INVALID_ARGUMENT", "timestamp must be RFC3339 with timezone")
    day, clock, fraction, zone = match.groups()
    zone = "+00:00" if zone.upper() == "Z" else zone
    try:
        dt = datetime.fromisoformat(f"{day}T{clock}{zone}")
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError("naive")
        utc_dt = dt.astimezone(timezone.utc)
        utc_second = (f"{utc_dt.year:04d}-{utc_dt.month:02d}-{utc_dt.day:02d}T"
                      f"{utc_dt.hour:02d}:{utc_dt.minute:02d}:{utc_dt.second:02d}")
    except (ValueError, OverflowError) as exc:
        raise AttendanceError("INVALID_ARGUMENT", "invalid timestamp") from exc
    digits = (fraction or "").rstrip("0")
    return utc_second + ("." + digits if digits else "")


def to_public(value: str | None) -> str | None:
    """Render UTC storage timestamps as RFC3339 without losing precision."""
    if value is None:
        return None
    if value.endswith("Z"):
        return value  # pre-migration idempotency response
    head, sep, fraction = value.partition(".")
    return head + "." + (fraction.ljust(6, "0") if sep else "000000") + "Z"


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
        return self.store.transition("checkIn", subject_id(args["subject_id"]), utc(args["occurred_at"]), request_id(args.get("request_id")), args["occurred_at"])

    def checkOut(self, payload: dict) -> dict:
        args = mapping(payload, {"subject_id", "occurred_at"}, {"request_id"})
        return self.store.transition("checkOut", subject_id(args["subject_id"]), utc(args["occurred_at"]), request_id(args.get("request_id")), args["occurred_at"])

    def getState(self, payload: dict) -> dict:
        args = mapping(payload, {"subject_id"})
        return self.store.state(subject_id(args["subject_id"]))

    def listSessions(self, payload: dict) -> list[dict]:
        args = mapping(payload, {"subject_id", "from", "to"})
        start, end = utc(args["from"]), utc(args["to"])
        if start >= end:
            raise AttendanceError("INVALID_ARGUMENT", "from must precede to")
        return self.store.sessions(subject_id(args["subject_id"]), start, end)
