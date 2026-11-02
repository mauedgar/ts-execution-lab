# IR005 repaired offline-proof candidate

Execution attempt: `TS-BEADS-047B-OFFLINE-PROOF-IR005-REPAIR-20261101-002`.

This candidate makes no SQL or filesystem fixture effect. Its native provider observes the prospective root, ancestor reparse points, owner/ACL, pinned Dolt hash/version, Dolt listeners, Tailscale Serve/Funnel state, and a pre-existing protected external receipt area. Any unavailable or unsafe observation is `BLOCKED_INCOMPLETE_PROVIDER_OBSERVATION` or a specific block label.

`-Effect` is intentionally blocked as `BLOCKED_PINNED_CAPABILITY_UNVERIFIED` / `PINNED_SQL_GRAMMAR_UNQUALIFIED` before parsing a grant, creating a root, writing a receipt, or spawning Dolt. An arbitrary JSON file is not authority. A future separately reviewed implementation needs an immutable external grant blob with verified issuer/subject/attempt/host/owner/source binding, durable original receipt lookup, and an exclusive one-time lock. It must also qualify native Dolt 2.2.0 grammar and structured `mysql.db`/`mysql.tables_priv` or verified role readback; `SHOW GRANTS` substring matching is prohibited.

The included test is injected-provider mocks only. It asserts exact fail-closed labels and that no subprocess is reached. It makes no empirical SQL-pass claim.
