"""A11 synthetic IPC fault fixture, never a PostgreSQL client."""
from __future__ import annotations
import os
import sys
import time

if os.environ.get("TS_R3_A11_SYNTHETIC_FAULTS") != "1" or len(sys.argv) != 2:
    raise SystemExit(49)
if sys.argv[1] == "MALFORMED":
    sys.stdout.write('{"not_valid_json":')
elif sys.argv[1] == "EXIT":
    raise SystemExit(9)
elif sys.argv[1] == "TIMEOUT":
    time.sleep(3)
else:
    raise SystemExit(49)
