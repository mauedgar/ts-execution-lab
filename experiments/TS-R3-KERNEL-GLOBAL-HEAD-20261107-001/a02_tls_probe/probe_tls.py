"""One-shot SECRETLESS SSLRequest TLS certificate/hostname probe of a known Neon child endpoint.

No SQL startup, credentials, Product state, Neon DML/DDL, or external state mutation.
This is not authenticated psycopg/role TLS or a two-host concurrency qualification.
"""
from __future__ import annotations

import json
import socket
import ssl
import struct
import sys

HOST = "ep-lucky-waterfall-b6244mdy.c-2.sa-east-1.aws.neon.tech"
PORT = 5432
SSL_REQUEST = struct.pack("!II", 8, 80877103)


def require(value: bool, code: str) -> None:
    if not value:
        raise AssertionError(code)


def main() -> None:
    require(sys.version_info[:3] == (3, 15, 2), "PYTHON_3152_PIN")
    require(HOST.endswith(".sa-east-1.aws.neon.tech"), "KNOWN_NEON_HOST_SUFFIX")
    context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    require(context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname,
            "TLS_CA_HOSTNAME_VERIFY_REQUIRED")
    with socket.create_connection((HOST, PORT), timeout=12) as plain:
        plain.settimeout(12)
        plain.sendall(SSL_REQUEST)
        negotiation = plain.recv(1)
        require(negotiation == b"S", "POSTGRES_SSLREQUEST_NOT_ACCEPTED")
        with context.wrap_socket(plain, server_hostname=HOST) as secure:
            require(secure.version() in ("TLSv1.2", "TLSv1.3"), "TLS_VERSION_REJECTED")
            negotiated_cipher = secure.cipher()
            require(negotiated_cipher is not None, "TLS_CIPHER_ABSENT")
            certificate = secure.getpeercert()
            require(bool(certificate), "VERIFIED_CERTIFICATE_ABSENT")
            require(bool(certificate.get("subjectAltName")), "CERTIFICATE_SAN_ABSENT")
            # The Python SSLContext checks CA chain and SNI hostname during handshake.
            # No PostgreSQL StartupMessage or credential exchange is attempted.
            print(json.dumps({
                "status": "A02_EXTERNAL_NEON_POSTGRES_TLS_CA_HOSTNAME_PASS",
                "endpoint": HOST,
                "port": PORT,
                "sslrequest_response": "S",
                "tls_version": secure.version(),
                "cipher": negotiated_cipher[0],
                "ca_chain_verified": True,
                "hostname_verified": True,
                "peer_cert_present": True,
                "postgres_authentication": "NOT_RUN",
                "remote_psycopg_sql": "NOT_RUN",
                "concurrent_hosts": "NOT_RUN",
                "neon_data_effect": "NONE",
                "product_effect": "NONE",
                "credentials_used": False,
            }, sort_keys=True))


if __name__ == "__main__":
    main()
