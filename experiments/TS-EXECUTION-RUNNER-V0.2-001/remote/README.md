# Remote Binding Fixtures

These fixtures are input-only evidence for the Worker B Actions adapter.

The workflows intentionally invoke the shared runner with `node src/cli.ts run`.
They do not duplicate profile semantics or accept arbitrary commands.

Actual dispatch depends on Worker A publishing the v0.2 CLI and its runtime
contracts on the selected lab ref. No dispatch is claimed from this branch
before that dependency exists.
