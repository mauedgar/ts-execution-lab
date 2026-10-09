# Stable MAT-XFORM Invocation

This experiment wraps the historical MAT-XFORM extractor as one bounded local invocation. It does not add Product, Tecnotron, registry, or Git behavior.

```text
python stable_materialize.py from-transport SOURCE.md --manifest MANIFEST.json --output STAGING --receipt RECEIPT.json
python stable_materialize.py from-inline REQUEST.json --output STAGING --receipt RECEIPT.json
```

`from-transport` validates with the historical extractor dry-run before writing. `from-inline` validates one `ts-devlab-text-materialization-request/v0` JSON request, creates temporary compatible transport files, and uses the same path. Staging must be absent or empty; paths are create-only and relative. Inline text must be non-empty and end in a line ending so the historical line-oriented transport can preserve bytes exactly.

Run tests from this directory with `python test_stable_materialize.py`.
