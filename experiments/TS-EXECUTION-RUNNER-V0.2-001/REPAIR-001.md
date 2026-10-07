# Worker B Actions — Repair 001

Preserve current candidate. Apply only these review findings, then commit/push branch and stop.

1. Both ts-exec-runner.yml and ts-exec-reusable.yml must install the runner's pinned dependencies before node src/cli.ts run. Use the smallest deterministic npm command compatible with package-lock (normally npm ci).
2. Do not duplicate runner/profile semantics in YAML.
3. Keep private-caller checkout + public runner checkout topology and no extra credentials.
4. Do not edit src/** or package.json.
5. Do not dispatch yet; integrated core is not on this branch.

Do not merge.
