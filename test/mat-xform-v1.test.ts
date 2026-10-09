import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { join, resolve } from "node:path";
import test from "node:test";
import { MatXformReceiptSchema, MatXformResultSchema, requestIdentity } from "../src/mat-xform/contracts.ts";

const root = resolve(import.meta.dirname, "..");
const cli = join(root, "src", "mat-xform", "cli.ts");
const schemaResult = JSON.parse(readFileSync(join(root, "schemas", "mat-xform-result.schema.json"), "utf8"));
const schemaReceipt = JSON.parse(readFileSync(join(root, "schemas", "mat-xform-receipt.schema.json"), "utf8"));

function request(artifacts = [{ artifact_id: "one", relative_path: "one.txt", utf8_text: "one" }]) {
  return { contract_version: "ts-mat-xform-request/v1", request_id: "request-1", batch_id: "batch-1", artifacts };
}
function run(value: unknown, extra: string[] = []) {
  const dir = mkdtempSync(join(root, ".mat-xform-test-"));
  const input = join(dir, "request.json");
  writeFileSync(input, JSON.stringify(value));
  const output = join(dir, "out");
  const result = spawnSync(process.execPath, [cli, "materialize", input, "--out", output, "--result", join(dir, "result.json"), "--receipt", join(dir, "receipt.json"), ...extra], { cwd: root, encoding: "utf8" });
  return { dir, input, output, result };
}
function cleanup(dir: string) { rmSync(dir, { recursive: true, force: true }); }
function hash(bytes: Buffer) { return `sha256:${createHash("sha256").update(bytes).digest("hex")}`; }

test("materializes 50 files, nested paths, empty/no-newline/LF/CRLF/Unicode/sentinel content", () => {
  const artifacts = Array.from({ length: 50 }, (_, index) => ({ artifact_id: `id-${index}`, relative_path: `nested/${index}/file.txt`, utf8_text: index === 0 ? "" : index === 1 ? "no newline" : index === 2 ? "LF\n" : index === 3 ? "CRLF\r\n" : index === 4 ? "日本語" : index === 5 ? "BEGIN_MAT_XFORM\n```markdown\nEND_MAT_XFORM" : `file ${index}` }));
  const execution = run(request(artifacts));
  try {
    assert.equal(execution.result.status, 0);
    const result = MatXformResultSchema.parse(JSON.parse(readFileSync(join(execution.dir, "result.json"), "utf8")));
    assert.equal(result.result_status, "PASS");
    assert.equal(result.effect_state, "CONFIRMED");
    assert.equal(result.artifact_count, 50);
    assert.equal(readFileSync(join(execution.output, "nested", "3", "file.txt"), "utf8"), "CRLF\r\n");
    assert.equal(readFileSync(join(execution.output, "nested", "5", "file.txt"), "utf8"), artifacts[5].utf8_text);
    for (const artifact of result.artifacts) {
      const bytes = readFileSync(join(execution.output, ...artifact.relative_path.split("/")));
      assert.equal(artifact.bytes, bytes.length);
      assert.equal(artifact.sha256, hash(bytes));
    }
    assert.deepEqual(readdirSync(join(execution.output, "nested", "0")), ["file.txt"]);
  } finally { cleanup(execution.dir); }
});

for (const [name, artifact] of [
  ["duplicate id", [{ artifact_id: "same", relative_path: "a", utf8_text: "" }, { artifact_id: "same", relative_path: "b", utf8_text: "" }]],
  ["case-insensitive path", [{ artifact_id: "a", relative_path: "Dir/a", utf8_text: "" }, { artifact_id: "b", relative_path: "dir/A", utf8_text: "" }]],
  ["traversal", [{ artifact_id: "a", relative_path: "../a", utf8_text: "" }]],
  ["absolute POSIX", [{ artifact_id: "a", relative_path: "/a", utf8_text: "" }]],
  ["drive path", [{ artifact_id: "a", relative_path: "C:/a", utf8_text: "" }]],
  ["backslash", [{ artifact_id: "a", relative_path: "a\\b", utf8_text: "" }]],
  ["reserved device", [{ artifact_id: "a", relative_path: "CON/file", utf8_text: "" }]],
  ["invalid character", [{ artifact_id: "a", relative_path: "bad?.txt", utf8_text: "" }]],
] as const) {
  test(`blocks ${name}`, () => {
    const execution = run(request(artifact));
    try {
      assert.equal(execution.result.status, 1);
      const result = JSON.parse(readFileSync(join(execution.dir, "result.json"), "utf8"));
      assert.equal(result.result_status, "BLOCKED");
      assert.equal(result.effect_state, "NONE");
      assert.equal(existsSync(execution.output), false);
    } finally { cleanup(execution.dir); }
  });
}

test("blocks existing output, invalid JSON, and invalid contract without materializing", () => {
  const existing = run(request());
  try {
    rmSync(existing.output, { recursive: true, force: false });
    writeFileSync(existing.output, "already here");
    const second = spawnSync(process.execPath, [cli, "materialize", existing.input, "--out", existing.output, "--result", join(existing.dir, "existing-result.json")], { cwd: root, encoding: "utf8" });
    assert.equal(second.status, 1);
    assert.equal(JSON.parse(readFileSync(join(existing.dir, "existing-result.json"), "utf8")).effect_state, "NONE");
    const bad = spawnSync(process.execPath, [cli, "materialize", join(existing.dir, "missing.json"), "--out", join(existing.dir, "bad")], { cwd: root, encoding: "utf8" });
    assert.equal(bad.status, 1);
  } finally { cleanup(existing.dir); }
});

test("identity is unchanged by output and binding, and result/receipt validate", () => {
  const a = run(request(), ["--binding", "binding-a"]);
  const b = run(request(), ["--binding", "binding-b"]);
  try {
    const resultA = MatXformResultSchema.parse(JSON.parse(readFileSync(join(a.dir, "result.json"), "utf8")));
    const resultB = MatXformResultSchema.parse(JSON.parse(readFileSync(join(b.dir, "result.json"), "utf8")));
    const receipt = MatXformReceiptSchema.parse(JSON.parse(readFileSync(join(a.dir, "receipt.json"), "utf8")));
    assert.equal(resultA.request_identity, resultB.request_identity);
    assert.equal(receipt.request_identity, resultA.request_identity);
    assert.equal(receipt.Product_effect, "NONE");
    assert.equal(schemaResult.title, "MatXformResult");
    assert.equal(schemaReceipt.title, "MatXformReceipt");
  } finally { cleanup(a.dir); cleanup(b.dir); }
});

test("invalid JSON and contract produce no publication", () => {
  const dir = mkdtempSync(join(root, ".mat-xform-invalid-"));
  try {
    const invalid = join(dir, "invalid.json");
    writeFileSync(invalid, "not json");
    const json = spawnSync(process.execPath, [cli, "validate", invalid], { cwd: root, encoding: "utf8" });
    assert.equal(json.status, 1);
    const contract = join(dir, "contract.json");
    writeFileSync(contract, JSON.stringify({ ...request(), contract_version: "wrong" }));
    const output = spawnSync(process.execPath, [cli, "validate", contract], { cwd: root, encoding: "utf8" });
    assert.equal(output.status, 1);
    assert.equal(output.stdout, "");
  } finally { cleanup(dir); }
});

test("validate emits a result that passes the result schema", () => {
  const dir = mkdtempSync(join(root, ".mat-xform-validate-"));
  try {
    const input = join(dir, "request.json");
    writeFileSync(input, JSON.stringify(request()));
    const output = spawnSync(process.execPath, [cli, "validate", input], { cwd: root, encoding: "utf8" });
    assert.equal(output.status, 0);
    const result = MatXformResultSchema.parse(JSON.parse(output.stdout));
    assert.equal(result.result_status, "PASS");
    assert.equal(result.artifact_count, 0);
  } finally { cleanup(dir); }
});

test("preserves preexisting deterministic staging and does not create final output", () => {
  const execution = run(request());
  try {
    rmSync(execution.output, { recursive: true, force: true });
    const identity = JSON.parse(readFileSync(execution.input, "utf8"));
    const staging = `${execution.output}.staging-${requestIdentity(identity).slice(7)}`;
    mkdirSync(staging);
    writeFileSync(join(staging, "sentinel.txt"), "untouched");
    const retry = spawnSync(process.execPath, [cli, "materialize", execution.input, "--out", execution.output, "--result", join(execution.dir, "staging-result.json")], { cwd: root, encoding: "utf8" });
    const result = JSON.parse(readFileSync(join(execution.dir, "staging-result.json"), "utf8"));
    assert.equal(retry.status, 1);
    assert.equal(result.error.code, "STAGING_EXISTS");
    assert.equal(result.artifact_count, 0);
    assert.equal(existsSync(execution.output), false);
    assert.equal(readFileSync(join(staging, "sentinel.txt"), "utf8"), "untouched");
  } finally { cleanup(execution.dir); }
});

test("blocks preexisting and same-path publication targets", () => {
  const execution = run(request());
  try {
    rmSync(execution.output, { recursive: true, force: true });
    const resultPath = join(execution.dir, "existing-result.json");
    writeFileSync(resultPath, "existing");
    const existing = spawnSync(process.execPath, [cli, "materialize", execution.input, "--out", execution.output, "--result", resultPath], { cwd: root, encoding: "utf8" });
    assert.equal(existing.status, 1);
    assert.equal(readFileSync(resultPath, "utf8"), "existing");
    const same = join(execution.dir, "same.json");
    const collision = spawnSync(process.execPath, [cli, "materialize", execution.input, "--out", execution.output, "--result", same, "--receipt", same], { cwd: root, encoding: "utf8" });
    assert.equal(collision.status, 1);
    assert.equal(existsSync(execution.output), false);
    assert.equal(existsSync(same), false);
  } finally { cleanup(execution.dir); }
});

test("blocks publication paths inside final output or deterministic staging", () => {
  const dir = mkdtempSync(join(root, ".mat-xform-publication-scope-"));
  try {
    const input = join(dir, "request.json");
    const value = request();
    writeFileSync(input, JSON.stringify(value));
    const output = join(dir, "out");
    const insideResult = spawnSync(process.execPath, [cli, "materialize", input, "--out", output, "--result", join(output, "result.json")], { cwd: root, encoding: "utf8" });
    assert.equal(insideResult.status, 1);
    assert.equal(existsSync(output), false);

    const staging = `${output}.staging-${requestIdentity(value).slice(7)}`;
    const insideStage = spawnSync(process.execPath, [cli, "materialize", input, "--out", output, "--receipt", join(staging, "receipt.json")], { cwd: root, encoding: "utf8" });
    assert.equal(insideStage.status, 1);
    assert.equal(existsSync(output), false);
    assert.equal(existsSync(staging), false);
  } finally { cleanup(dir); }
});

test("matches the materialized-byte oracle and explicit v1 extension fixture", () => {
  const fixture = join(root, "experiments", "TS-DEVLAB-MAT-XFORM-V1-001", "fixtures");
  const execution = run(JSON.parse(readFileSync(join(fixture, "oracle-request.json"), "utf8")));
  try {
    const expected = JSON.parse(readFileSync(join(fixture, "oracle-expected.json"), "utf8")).artifacts;
    const result = MatXformResultSchema.parse(JSON.parse(readFileSync(join(execution.dir, "result.json"), "utf8")));
    assert.deepEqual(result.artifacts, expected);
    for (const artifact of expected) {
      const bytes = readFileSync(join(execution.output, ...artifact.relative_path.split("/")));
      assert.equal(bytes.length, artifact.bytes);
      assert.equal(hash(bytes), artifact.sha256);
    }
  } finally { cleanup(execution.dir); }
});
