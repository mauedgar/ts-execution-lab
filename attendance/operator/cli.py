"""H6 Attendance operator CLI. Does not import SQLite or modify schema."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Callable


def build_parser():
    parser = argparse.ArgumentParser(prog='attendance')
    parser.add_argument('--db', required=True, help='Path to isolated Attendance SQLite database')
    sub = parser.add_subparsers(dest='action', required=True)
    for name in ('check-in', 'check-out'):
        s = sub.add_parser(name)
        s.add_argument('--subject-id', required=True)
        s.add_argument('--occurred-at', required=True)
        s.add_argument('--request-id')
    state = sub.add_parser('state')
    state.add_argument('--subject-id', required=True)
    ls = sub.add_parser('list')
    ls.add_argument('--subject-id', required=True)
    ls.add_argument('--from', dest='from_time', required=True)
    ls.add_argument('--to', dest='to_time', required=True)
    return parser


def main(argv=None, *, service_factory: Callable | None = None, out=None, err=None):
    out = sys.stdout if out is None else out
    err = sys.stderr if err is None else err
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if service_factory is None:
        # Late dependency resolution: isolated operator tests use an injected service.
        from attendance.core.service import AttendanceService
        service_factory = AttendanceService
    try:
        service = service_factory(args.db)
        if args.action in ('check-in', 'check-out'):
            payload = {'subject_id': args.subject_id, 'occurred_at': args.occurred_at}
            if args.request_id is not None:
                payload['request_id'] = args.request_id
            method = service.checkIn if args.action == 'check-in' else service.checkOut
            result = method(payload)
        elif args.action == 'state':
            result = service.getState({'subject_id': args.subject_id})
        else:
            result = service.listSessions({'subject_id': args.subject_id, 'from': args.from_time, 'to': args.to_time})
        print(json.dumps({'ok': True, 'data': result}, sort_keys=True), file=out)
        return 0
    except Exception as exc:
        code = getattr(exc, 'code', 'STORAGE_ERROR')
        if code not in {'INVALID_ARGUMENT','ALREADY_OPEN','NO_OPEN_SESSION','NON_MONOTONIC_TIME',
                        'REQUEST_CONFLICT','NOT_FOUND','STORAGE_ERROR'}:
            code = 'STORAGE_ERROR'
        print(json.dumps({'ok': False, 'error': {'code': code, 'message': str(exc)}}, sort_keys=True), file=err)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
