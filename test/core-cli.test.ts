import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import test from "node:test";
import {
  ExecutionReceiptSchema,
  ExecutionRequestSchema,
  ExecutionResultSchema,
} from "../src/contracts.ts";

const root = resolve(import.meta.dirname, "..");
const fixture = join(root, "examples", "requests", "canonical-v0.2.json");

test("request contract is binding-agnostic and strict", () => {
  const request = JSON.parse(readFileSync(fixture, "utf8"));
  assert.equal(ExecutionRequestSchema.safeParse(request).success, true);
  assert.equal(ExecutionRequestSchema.safeParse({ ...request, binding: { provider: "local-commander" } }).success, false);
});

test("run publishes validated result and receipt", () => {
  const out = mkdtempSync(join(tmpdir(), "ts-exec-core-"));
  try {
    execFileSync(process.execPath, ["src/cli.ts", "run", fixture, "--out", out, "--binding", "test-binding"], {
      cwd: root,
      encoding: "utf8",
    });
    const result = ExecutionResultSchema.parse(JSON.parse(readFileSync(join(out, "result.json"), "utf8")));
    const receipt = ExecutionReceiptSchema.parse(JSON.parse(readFileSync(join(out, "receipt.json"), "utf8")));
    assert.equal(result.result_status, "PASS");
    assert.equal(result.effect_state, "NONE");
    assert.equal(result.semantic_digest, "sha256:32b769982a3a6e2df120530b06dcbaf1e8f75e004ceea92ac3e91bd7a248d728");
    assert.equal(result.observation.subprocess_count, 0);
    assert.equal(receipt.request_identity, result.request_identity);
    assert.equal(receipt.selected_binding_ref, "test-binding");
    assert.equal(receipt.authority_created, false);
    assert.equal(receipt.Product_effect_created, false);
  } finally {
    rmSync(out, { recursive: true, force: true });
  }
});

test("unsupported version emits BLOCKED/NONE artifacts when identity is recoverable", () => {
  const directory = mkdtempSync(join(tmpdir(), "ts-exec-rejected-"));
  try {
    const request = JSON.parse(readFileSync(fixture, "utf8"));
    request.contract_version = "ts-execution-request/v9";
    const requestPath = join(directory, "request.json");
    const out = join(directory, "out");
    writeFileSync(requestPath, JSON.stringify(request));
    const execution = spawnSync(process.execPath, ["src/cli.ts", "run", requestPath, "--out", out], {
      cwd: root,
      encoding: "utf8",
    });
    assert.equal(execution.status, 1);
    const result = ExecutionResultSchema.parse(JSON.parse(readFileSync(join(out, "result.json"), "utf8")));
    const receipt = ExecutionReceiptSchema.parse(JSON.parse(readFileSync(join(out, "receipt.json"), "utf8")));
    assert.equal(result.result_status, "BLOCKED");
    assert.equal(result.effect_state, "NONE");
    assert.equal(result.observation.result_class, "UNSUPPORTED_VERSION");
    assert.equal(receipt.result_status, "BLOCKED");
    assert.equal(receipt.effect_state, "NONE");
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test("profiles lists only registered known profiles", () => {
  const profiles = JSON.parse(execFileSync(process.execPath, ["src/cli.ts", "profiles"], { cwd: root, encoding: "utf8" }));
  assert.deepEqual(profiles.map((profile: { profile_id: string }) => profile.profile_id), [
    "canonical-sha256/v0",
    "git-exact-subject/v0",
  ]);
});
