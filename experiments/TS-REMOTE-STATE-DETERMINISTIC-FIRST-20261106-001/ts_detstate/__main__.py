"""Credential-free CLI. No SQL mode is intentionally exposed at this gate."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

from .core import Command, Rejected, canonical, strict_loads


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Synthetic-only deterministic command planner; NO SQL")
    parser.add_argument("plan", choices=["plan"])
    parser.add_argument("--command-file", required=True, type=pathlib.Path)
    args = parser.parse_args(argv)
    try:
        # Bounded local input; must not embed credentials.
        if args.command_file.stat().st_size > 16_384:
            raise Rejected("INPUT_LIMIT")
        raw = args.command_file.read_text(encoding="utf-8")
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
