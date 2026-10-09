# Independent Review TXT Carrier

`review_txt_carrier.py` projects a TAR containing only safe, regular UTF-8 text files into one deterministic UTF-8 `.txt` bundle. It preserves every accepted member payload byte-for-byte, while recording the source TAR hash, size, and entry count as metadata.

## Commands

```text
python review_txt_carrier.py project source.tar --out bundle.txt --report project-report.json
python review_txt_carrier.py verify bundle.txt --report verify-report.json
python review_txt_carrier.py extract bundle.txt --out extracted --report extract-report.json
```

`extract` requires its output directory to be absent or empty. The carrier rejects non-regular members, unsafe paths, duplicate paths, and non-UTF-8 payloads.

## Framing

The bundle starts with a format marker and canonical JSON manifest. Each member has a canonical JSON header with its path, byte length, and SHA-256, followed by exactly that number of UTF-8 payload bytes. Length framing means payload content cannot collide with framing text.

Reports explicitly state `member_payload_equivalence: PASS`, `source_archive_identity_preserved_as_metadata: true`, and `source_archive_byte_reconstruction: NOT_CLAIMED`. This experiment does not claim that TXT replaces TAR canonically or can recreate the original TAR bytes.

## Test

```text
python -m unittest -v test_review_txt_carrier.py
```
