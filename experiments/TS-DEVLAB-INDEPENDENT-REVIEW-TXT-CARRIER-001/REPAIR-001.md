# Independent Review TXT Carrier — Repair 001

Preserve candidate e7f17bdd58af33f049940e1fc863bc12bb26d428.

Real Tecnotron frozen TAR qualification exposed a gap.

Real source:
- Git blob: 35fa3c1da0cc1f8db27e86422fd7d8b8e4cdaa8f
- TAR sha256: b887750e9f5a3eb3bbaa9f7dff95cd8aaa7fa8a4072b8679cad5fe6a43fe6ff2
- bytes: 314880
- entries: 12
- contains evidence/history.tar:
  - bytes: 204800
  - sha256: 04e61e07b271def968d0d3e99f8cac7bb69e56d6ba79c3bfeb5b4ded8f3929e0

The current candidate accepts any UTF-8-decodable byte sequence as raw text. TAR/NUL payloads can decode but are not a readable TXT carrier.

Repair requirements:

1. Make the carrier itself strictly readable UTF-8:
   - textual member: transport_encoding = "utf8"; store raw text payload.
   - binary/non-readable member: transport_encoding = "base64"; store canonical unwrapped base64 ASCII payload.
   - readable text = UTF-8 decode succeeds AND every character is printable or TAB/CR/LF.
   - NUL or other control characters must force base64.

2. Per-member metadata must preserve ORIGINAL member facts:
   - path
   - original_byte_length
   - original_sha256
   - transport_encoding
   - encoded_byte_length or equivalent deterministic framing fact.

3. verify/extract:
   - parse encoded payload by encoded length;
   - decode according to transport_encoding;
   - verify original length/hash after decoding;
   - extraction reconstructs original bytes exactly.

4. Whole bundle:
   - valid UTF-8
   - no NUL/control bytes except TAB/CR/LF
   - deterministic ordering
   - source TAR identity retained as metadata
   - source_archive_byte_reconstruction = NOT_CLAIMED
   - member_payload_equivalence remains the target property.

5. Harden portable paths:
   - case-insensitive duplicate paths rejected
   - reject Windows reserved device segments
   - reject path segments ending dot/space.

6. Tests:
   - preserve existing tests
   - binary NUL member becomes base64 and round-trips
   - readable UTF-8 remains raw
   - bundle has no NUL/disallowed controls
   - case-insensitive duplicate blocked
   - Windows reserved path blocked.

7. README must explain hybrid utf8/base64 representation and non-claim.

Do not claim Product adoption or canonical TAR replacement.
Run focused tests. Commit/push branch. Do not merge.
