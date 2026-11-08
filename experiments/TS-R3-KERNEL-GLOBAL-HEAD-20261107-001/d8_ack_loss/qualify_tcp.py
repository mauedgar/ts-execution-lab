"""D8 NONPRODUCT: drop real PostgreSQL COMMIT response over a loopback TCP proxy.

Proof ceiling: genuine client/server socket ACK *response* loss on one Linux host,
not a cross-host or remote Neon partition, and not raw TCP packet-level ACK loss.
Provider-owned disposable PG16 only. Exactly one mutation; no retry.
"""
from __future__ import annotations
import base64
from hashlib import sha256
import json
import os
from pathlib import Path
import socket
import struct
import sys
import threading

import psycopg
from psycopg.rows import dict_row
from ts_global.bridge import EffectUnknown, Mutation, apply, initialize, read, reconcile

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "ts_r3_global_head_20261107_001"
SCOPE = "ts-r3-d8-disposable-tcp-ackloss-20261108-001"
URI = ("postgresql://tsr3_e2_synthetic:e2_local_disposable_only"
       "@127.0.0.1:5432/tsr3_e2_synthetic?sslmode=disable")


def require(value, label):
    if not value:
        raise AssertionError(label)


def direct():
    require(os.getenv("TS_R3_NEON_CHILD_DSN") is None, "NO_NEON_CREDENTIALS")
    require(os.getenv("TS_R3_LOCAL_SYNTHETIC_PG_URI") == URI, "EXACT_DISPOSABLE_URI")
    return psycopg.connect(URI, autocommit=True, row_factory=dict_row, connect_timeout=6)


class DropCommitResponse:
    """PostgreSQL v3 framed backend relay: suppress only CommandComplete(COMMIT)."""

    def __init__(self):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind(("127.0.0.1", 0))
        self.listener.listen(1)
        self.listener.settimeout(16)
        self.port = self.listener.getsockname()[1]
        self.commit_response_suppressed = threading.Event()
        self.done = threading.Event()
        self.error = None
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        client = server = None
        try:
            client, _ = self.listener.accept()
            client.settimeout(16)
            server = socket.create_connection(("127.0.0.1", 5432), timeout=6)
            server.settimeout(16)

            def client_to_server():
                try:
                    while True:
                        data = client.recv(65536)
                        if not data:
                            return
                        server.sendall(data)
                except (OSError, ValueError):
                    return

            sender = threading.Thread(target=client_to_server, daemon=True)
            sender.start()
            buf = bytearray()
            while True:
                block = server.recv(65536)
                if not block:
                    return
                buf.extend(block)
                while len(buf) >= 5:
                    size = struct.unpack("!I", buf[1:5])[0]
                    require(4 <= size <= 16 * 1024 * 1024, "BACKEND_FRAME_BOUNDS")
                    frame_length = 1 + size
                    if len(buf) < frame_length:
                        break
                    frame = bytes(buf[:frame_length])
                    del buf[:frame_length]
                    if frame[0:1] == b"C" and frame[5:] == b"COMMIT\x00":
                        # COMMIT already executed server-side. Do not deliver its reply.
                        self.commit_response_suppressed.set()
                        try:
                            client.shutdown(socket.SHUT_RDWR)
                        except OSError:
                            pass
                        return
                    client.sendall(frame)
        except (OSError, ValueError, AssertionError) as exc:
            self.error = repr(exc)
        finally:
            for stream in (client, server, self.listener):
                if stream:
                    try:
                        stream.close()
                    except OSError:
                        pass
            self.done.set()

    def join(self):
        require(self.done.wait(10), "TCP_PROXY_NOT_TERMINAL")
        self.thread.join(1)
        require(self.error is None, "TCP_PROXY_ERROR_" + str(self.error))


def main():
    require(len(sys.argv) == 2, "ONE_FROZEN_FIXTURE")
    fixture = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    require(fixture["kind"] == "PRODUCT_JS_V0_EXACT_GENERATIONS" and
            fixture["product_git_commit"] == "26509b74d50207bb247dcc9bdb929a63f5451e88",
            "FROZEN_PRODUCT_SOURCE")
    g = fixture["generations"]
    require(len(g) == 20 and [x["revision"] for x in g] == list(range(20)), "FROZEN_SEQUENCE")
    require(psycopg.__version__ == "3.3.8" and psycopg.pq.__impl__ == "binary",
            "PINNED_PG_DRIVER")
    b64 = lambda value: base64.b64decode(value, validate=True)
    initial = b64(g[0]["state_b64"])
    expected = g[1]

    with direct() as admin:
        schema = (ROOT / "schema.sql").read_text(encoding="utf-8")
        statements = [p.strip() for p in "\n".join(
            line for line in schema.splitlines() if not line.lstrip().startswith("--")
        ).split(";") if p.strip()]
        require(len(statements) == 4, "SCHEMA_SHAPE")
        with admin.transaction():
            for statement in statements:
                admin.execute(statement)
        original = initialize(admin, SCOPE, initial)
        require(original.revision == 0 and original.state_bytes == initial, "GENESIS")
        command = Mutation(
            SCOPE, "d8-commit-response-drop-once", 0, None,
            b64(expected["payload_b64"]), b64(expected["event_line_b64"]),
            b64(expected["state_b64"]), sha256(b"D8_NONPRODUCT_TCP").hexdigest()
        )

    proxy = DropCommitResponse()
    proxy_uri = URI.replace(":5432/", f":{proxy.port}/")
    try:
        with psycopg.connect(proxy_uri, autocommit=True, row_factory=dict_row,
                             connect_timeout=6) as writer:
            try:
                apply(writer, command)
            except EffectUnknown:
                # No replay: await original backend response interception and read-only reconcile.
                pass
            else:
                raise AssertionError("LOST_COMMIT_RESPONSE_WAS_NOT_FENCED")
    finally:
        proxy.join()
    require(proxy.commit_response_suppressed.is_set(), "NO_COMMIT_RESPONSE_DROPPED")

    with direct() as observer:
        verdict = reconcile(observer, command)
        final = read(observer, SCOPE)
        require(verdict.disposition == "CONFIRMED" and verdict.replay and
                verdict.revision == 1 and verdict.event_hash == expected["event_hash"],
                "OBSERVER_NOT_CONFIRMED")
        require(final.revision == 1 and final.state_bytes == command.state_bytes and
                final.event_bytes == command.event_line, "COMMITTED_BYTES_MISMATCH")
        rows = observer.execute(
            f"SELECT (SELECT count(*) FROM {SCHEMA}.events WHERE scope=%s) AS events, "
            f"(SELECT count(*) FROM {SCHEMA}.receipts WHERE scope=%s) AS receipts",
            (SCOPE, SCOPE)
        ).fetchone()
        require(rows == {"events": 1, "receipts": 1}, "RECEIPT_OR_EVENT_COUNT")
        print(json.dumps({
            "status": "D8_REAL_TCP_COMMIT_RESPONSE_LOSS_PASS",
            "host_count": 1, "postgresql": "16-disposable",
            "transport": "TCP_LOOPBACK_PG_PROTOCOL_PLAINTEXT",
            "forced_loss": "POSTGRES_COMMIT_COMMAND_COMPLETE_BEFORE_CLIENT_DELIVERY",
            "client_effect": "UNKNOWN_FENCED",
            "observer_effect": "CONFIRMED",
            "mutation_attempts": 1, "events": rows["events"],
            "receipts": rows["receipts"], "revision": final.revision,
            "event_hash": verdict.event_hash,
            "state_sha256": sha256(final.state_bytes).hexdigest(),
            "event_stream_sha256": sha256(final.event_bytes).hexdigest(),
            "remote_neon": "NOT_RUN", "two_host": "NOT_RUN",
            "product_effect": "NONE"
        }, sort_keys=True))


if __name__ == "__main__":
    main()
