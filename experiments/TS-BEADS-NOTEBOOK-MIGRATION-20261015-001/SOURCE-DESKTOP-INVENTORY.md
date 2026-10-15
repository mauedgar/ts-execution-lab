# TS Beads Notebook Migration | Sanitized desktop source inventory (read-only)

**Evidence class:** `NONPRODUCT_EXPERIMENTAL_HOST_OBSERVATION`. **Date:** 2026-10-15. **Carrier:** `mauedgar/ts-execution-transport@2ac2ef0a370d2e6c863900f2605379def16595b0:handoffs/TS-BEADS-NOTEBOOK-MIGRATION-20261015-001/HANDOFF.md` (blob `e8066ee2b81999438d239ec2ec2df452d8150670`).

**Source:** `DESKTOP-3LJ0E54`, Remote Commander device `777b57a0-70df-4bd6-b9ed-f6a4998e6022`. **Target:** `DESKTOP-DJLBEQH`, device `40cc0b10-fa7b-4a6a-98cf-1c94f93791b2`. Source read-only, no local code or Product mutation. The experiments were first observed in GitHub receipts, not invented from the host.

## Source executable

Under `%LOCALAPPDATA%\TS-Experiments\TS-BEADS-CONTINUITY-PILOT-20261013-001\`:

- Upstream Beads 1.3.1 zip SHA256 `48cd82e1d3e311c9bf9a5d6d67ad1a8542ae13d4e20c5bfb527656c5e666af76`.
- Extracted `bin\bd.exe` SHA256 `ac5b60114e5e7ef9de8878b45fc35941937341d3447366c99bc91c81557be7a4`.
- Native `bd version`: `bd version 1.3.1 (c1c4b642a: HEAD@c1c4b642ac1c)`.

## Original stores observed in exact source

Root `%LOCALAPPDATA%\TS-Experiments\`. Each experiment has an isolated `data\.beads` with `config.yaml`, `metadata.json`, and `embeddeddolt`; *no* `.beads` in the desktop `TS-Execution-Lab` repo root. In each store the config SHA256 is `6fcb85f47f6e9c3bc194df5aac99e73091ff9777f24ebd91d4343d04bd774073`. No config contents were exported.

| Pilot | Local files | Bytes | Qualified historical evidence |
| --- | ---: | ---: | --- |
| `TS-BEADS-CONTINUITY-PILOT-20261013-001` | 15 | 2,164,308 | `mauedgar/ts-execution-lab@603fa23657a656852784ed034f188647dcb6c089:experiments/TS-BEADS-CONTINUITY-PILOT-20261013-001/PILOT-RESULT-20261013-001.md` |
| `TS-BEADS-INBOX-DEDUP-PILOT-20261013-002` | 15 | 2,187,558 | `mauedgar/ts-execution-lab@2c98305af8ae72b02f571d0ec13be62c8635df15:experiments/TS-BEADS-INBOX-DEDUP-PILOT-20261013-002/PILOT-RESULT-20261013-002.md` |
| `TS-BEADS-DEPENDENCY-RECOVERY-20261013-004` | 15 | 2,322,470 | observed store and five JSON files; do not infer semantic result from mere local presence |

### Native receipt digests, byte-preserving historical identity

These are SHA256 hashes of the original files on desktop, **not** transferred copies. No original JSON contents or credentials were exported.

| Original pilot/filename | Bytes | SHA256 |
| --- | ---: | --- |
| 001/`result.json` | 2,131 | `0bcbd1fb126ff5fe2f00141bec333d015b9bcc047968d3bb16ab36b3f851d91b` |
| 001/`continuation-003-result.json` | 2,094 | `6606b5ceb8f3a4c1fd8a31828783b1aa3eef02c2bfd23fa52eccd31baabd0b13` |
| 001/`continuation-003-readback.json` | 152 | `439036b495385c71a4f09c2faa06bfc8a825144e3d4b5a416c9bf0bcd84e1195` |
| 002/`result.json` | 4,002 | `b7419709603102b369637df85b754f93eacb856e1153a5b8992cd9e4beb4af84` |
| 002/`readback.json` | 132 | `49b294d7c5b5812895510d14f60d2a3607d890d468271db12a6bc36a3379b121` |
| 002/`readback-003.json` | 2,140 | `8c09f4a82f944aa76614e7b0245d3238b03a32c6f7c5075a19b816f13b0120a5` |
| 004/`before.json` | 241 | `6a2348810ce435a818baa9b353765957f8a28ce23fc9be20026d5e4f16ba4444` |
| 004/`identities.json` | 107 | `5bf630b1620bafdc9484e369ba54c98adba6dc3a7368a2b9f7fc67efd2f01656` |
| 004/`readback.json` | 277 | `9c65f9c78884ca9cf6a78b58a2a1ccbe0c595848f7fdd2b98f2d667ae628fecb` |
| 004/`result.json` | 824 | `7a16d530bc4e315009e2e9020419792ff4c4895a981a4b0c4d613a0c678e8e2a` |
| 004/`resumed.json` | 236 | `321029a3f298d47c7e1e998286c59860f257ff7de81261edd5de82a0160975c6` |

## Deliberate migration scope

The three original stores have **historical test fixture** value; later native pilots 015–018 executed in disposable Actions workspaces and persisted their report/workflow Git refs. The later experiments do not require mutating or reusing the desktop's historical Dolt data. The sanitized manifest is portable and sufficient to identify historic stores, compare any future backups and continue *new* isolated research; **it is not a binary backup nor a proof of cross-machine Dolt data migration**.

Until a secure native archive/export/import mechanism is separately qualified, leave original desktop bytes intact (no shutdown/revoke of desktop agent in this task); do not claim their migration to notebook or destroy the source. Do not copy secrets into Git/Transport. Notebook Beads installation and clean separate-store qualification are another effect with its own receipt.

**Product:** none. **TaskCycle/Phase2:** none. **Shared Dolt remote:** unchanged. **No automatic Beads adoption.**
