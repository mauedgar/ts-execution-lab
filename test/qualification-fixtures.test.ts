import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..", "experiments", "TS-EXECUTION-RUNNER-V0.2-001");

function load<T>(path: string): T {
  return JSON.parse(readFileSync(resolve(root, path), "utf8")) as T;
}

test("qualification matrix reflects terminal DOD-01 through DOD-14 reconciliation", () => {
  const matrix = load<{ terminal_disposition?: string; items: Array<{ id: string; status: string }> }>("qualification/matrix.json");
  assert.deepEqual(matrix.items.map((item) => item.id), Array.from({ length: 14 }, (_, i) => `DOD-${String(i + 1).padStart(2, "0")}`));
  assert.equal(matrix.terminal_disposition, "PASS_RECONCILED_TERMINAL");
  assert.ok(matrix.items.every((item) => item.status === "PASS"));
});

test("equivalence fixture preserves one request and one expected digest", () => {
  const fixture = load<{ request: { contract_version: string }; expected: { semantic_digest: string }; execution_status: string }>("qualification/local-remote-equivalence.json");
  assert.equal(fixture.request.contract_version, "ts-execution-request/v0.2");
  assert.match(fixture.expected.semantic_digest, /^sha256:[0-9a-f]{64}$/);
  assert.equal(fixture.execution_status, "NOT_EXECUTED");
});

test("fallback fixture requires a new attempt and blocks UNKNOWN", () => {
  const fixture = load<{ attempt_A: { ExecutionAttempt_ref: string; effect_state: string }; attempt_B: { ExecutionAttempt_ref: string; required_invariants: string[] }; blocking_rule: string }>("qualification/fallback-proof.json");
  assert.notEqual(fixture.attempt_A.ExecutionAttempt_ref, fixture.attempt_B.ExecutionAttempt_ref);
  assert.equal(fixture.attempt_A.effect_state, "NONE");
  assert.ok(fixture.attempt_B.required_invariants.includes("new ExecutionAttempt_ref"));
  assert.match(fixture.blocking_rule, /EFFECT_UNKNOWN/);
});
