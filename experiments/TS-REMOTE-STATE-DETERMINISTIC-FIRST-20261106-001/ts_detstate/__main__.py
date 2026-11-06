"""Credential-free CLI. No SQL mode is intentionally exposed at this gate."""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import stat
import sys

from .core import Command, Rejected, MAX_JSON_BYTES, canonical, strict_loads


def _read_bounded_regular_file(path: pathlib.Path) -> str:
    """Read one stable opened descriptor; never stat path and reopen by name.

    O_NOFOLLOW rejects symlink at the final component. Full parent-directory
    custody remains the responsibility of the trusted runner; no Product I/O.
    """
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    flags |= getattr(os, "O_NONBLOCK", 0)
    fd = os.open(path, flags)
    try:
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode):
            raise Rejected("INPUT_NOT_REGULAR")
        if metadata.st_size > MAX_JSON_BYTES:
            raise Rejected("INPUT_LIMIT")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            data = stream.read(MAX_JSON_BYTES + 1)
        if len(data) > MAX_JSON_BYTES:
            raise Rejected("INPUT_LIMIT")
        try:
            return data.decode("utf-8", errors="strict")
        except UnicodeError:
            raise Rejected("INPUT_UTF8_INVALID") from None
    finally:
        os.close(fd)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Synthetic-only deterministic command planner; NO SQL")
    parser.add_argument("plan", choices=["plan"])
    parser.add_argument("--command-file", required=True, type=pathlib.Path)
    args = parser.parse_args(argv)
    try:
        raw = _read_bounded_regular_file(args.command_file)
        cmd = Command.from_dict(strict_loads(raw))
        print(canonical({"disposition": "PLANNED_ONLY", "effect": "NONE", "retry_authorized": False,
                         "command_fingerprint": cmd.fingerprint(), "event_id": cmd.event_id(),
                         "state_id": cmd.state_id, "next_revision": cmd.expected_revision + 1}))
        return 0
    except (Rejected, OSError, UnicodeError) as exc:
        code = exc.code if isinstance(exc, Rejected) else "INPUT_UNAVAILABLE"
        print(json.dumps({"disposition": "BLOCKED", "effect": "NONE", "code": code}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
