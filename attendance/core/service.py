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


# Positive UTC leap seconds published by IERS through 2016. No new insertion
# dates are inferred: unknown :60 instants fail closed until this data is updated.
_LEAP_SECOND_DATES = frozenset("""1972-06-30 1972-12-31 1973-12-31 1974-12-31 1975-12-31
1976-12-31 1977-12-31 1978-12-31 1979-12-31 1981-06-30
1982-06-30 1983-06-30 1985-06-30 1987-12-31 1989-12-31
1990-12-31 1992-06-30 1993-06-30 1994-06-30 1995-12-31
1997-06-30 1998-12-31 2005-12-31 2008-12-31 2012-06-30
2015-06-30 2016-12-31""".split())


def utc(value: Any) -> str:
    """Normalize an RFC3339 instant without discarding fractional precision.

    Canonical internal values omit 'Z' so that a stripped, variable-length
    fractional portion sorts correctly as text in SQLite. The public API
    converts them back to RFC3339 with at least six decimal places.
    """
    if isinstance(value, str):
        if len(value) > 8218:
            raise AttendanceError("INVALID_ARGUMENT", "timestamp exceeds H6 V0 resource budget")
        # Cheap pre-regex precision guard, as required by the frozen Control
        # resource contract. Count ASCII digits only after the time separator.
        # Malformed strings still undergo the normal RFC3339 validation.
        dot = value.find(".", 19)
        if dot != -1:
            cursor = dot + 1
            while cursor < len(value) and "0" <= value[cursor] <= "9":
                if cursor - dot > 8192:
                    raise AttendanceError("INVALID_ARGUMENT", "RFC3339 fractional precision exceeds H6 V0 budget")
                cursor += 1
    match = _RFC3339.fullmatch(value) if isinstance(value, str) else None
    if match is None:
        raise AttendanceError("INVALID_ARGUMENT", "timestamp must be RFC3339 with timezone")
    day, clock, fraction, zone = match.groups()
    if fraction is not None and len(fraction) > 8192:
        raise AttendanceError("INVALID_ARGUMENT", "RFC3339 fractional precision exceeds H6 V0 budget")
    zone = "+00:00" if zone.upper() == "Z" else zone
    if zone != "+00:00":
        hours, minutes = int(zone[1:3]), int(zone[4:6])
        if hours > 23 or minutes > 59:
            raise AttendanceError("INVALID_ARGUMENT", "invalid RFC3339 offset")
    is_leap = clock.endswith(":60")
    normal_clock = clock[:-2] + "59" if is_leap else clock
    try:
        dt = datetime.fromisoformat(f"{day}T{normal_clock}{zone}")
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError("naive")
        utc_dt = dt.astimezone(timezone.utc)
        utc_second = (f"{utc_dt.year:04d}-{utc_dt.month:02d}-{utc_dt.day:02d}T"
                      f"{utc_dt.hour:02d}:{utc_dt.minute:02d}:{utc_dt.second:02d}")
        if is_leap:
            # RFC3339 :60 is representable as the distinct UTC second after
            # 23:59:59; lexicographic SQLite ordering remains exact.
            if utc_second[:10] not in _LEAP_SECOND_DATES or not utc_second.endswith("23:59:59"):
                raise ValueError("not an announced UTC leap second")
            utc_second = utc_second[:-2] + "60"
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
