"""A003 deterministic boundary qualification, isolated from SQL and Product."""
from __future__ import annotations
import json
from ts_global.bridge import MAX_BYTES, MAX_SAFE, StorageRejected, _parse, _bytes, _require_conn

def reject(fn, code):
    try:
        fn()
    except StorageRejected as exc:
        assert exc.code == code, (exc.code, code)
    else:
        raise AssertionError("ACCEPTED_" + code)

def main():
    cases = [
        (lambda: _parse(b'{"a":1,"a":2}'), "DUPLICATE_JSON_KEY"),
        (lambda: _parse(b'\xff'), "INVALID_JSON"),
        (lambda: _parse(('{"n":' + str(MAX_SAFE + 1) + '}').encode()), "UNSAFE_JSON_INTEGER"),
        (lambda: _parse(b'{"n":NaN}'), "NONFINITE_JSON"),
        (lambda: _parse(b'{"n":1.2}'), "UNSUPPORTED_JSON_FLOAT"),
        (lambda: _bytes(b"x" * (MAX_BYTES + 1)), "INVALID_BYTES"),
    ]
    for action, expected in cases:
        reject(action, expected)
    assert len(_bytes(b"x" * MAX_BYTES)) == MAX_BYTES
    class NonIdle:
        autocommit = True
        class Info:
            class Status:
                name = "INTRANS"
            transaction_status = Status()
        info = Info()
        def transaction(self): pass
        def cursor(self): pass
    reject(lambda: _require_conn(NonIdle()), "TRANSACTION_NOT_IDLE")
    print(json.dumps({"status":"A003_BOUNDARY_NEGATIVE_PASS",
                      "cases":len(cases)+1,"max_bytes":MAX_BYTES,
                      "max_safe_integer":MAX_SAFE,"sql_effect":"NONE",
                      "neon":"NOT_RUN","product_effect":"NONE"},sort_keys=True))
if __name__ == "__main__":
    main()
