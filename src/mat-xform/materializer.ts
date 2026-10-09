import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, renameSync, statSync, writeFileSync, rmSync } from "node:fs";
import { dirname, isAbsolute, join, resolve } from "node:path";
import { MatXformRequestSchema, MatXformResultSchema, MatXformReceiptSchema, requestIdentity, RESULT_CONTRACT_VERSION, RECEIPT_CONTRACT_VERSION } from "./contracts.ts";
import type { MatXformRequest, MatXformResult, MatXformReceipt } from "./contracts.ts";

export type MaterializeOptions = { outputRoot: string; resultPath?: string; receiptPath?: string; binding?: string };

function errorResult(request: MatXformRequest, identity: string, status: MatXformResult["result_status"], effect: MatXformResult["effect_state"], code: string, message: string, validationMs = 0): MatXformResult {
  return MatXformResultSchema.parse({ contract_version: RESULT_CONTRACT_VERSION, request_identity: identity, request_id: request.request_id, batch_id: request.batch_id, result_status: status, effect_state: effect, artifact_count: request.artifacts.length, artifacts: [], timings: { validation_ms: validationMs, materialization_ms: 0, total_ms: validationMs }, error: { code, message } });
}

function pathError(path: string): string | undefined {
  if (path.startsWith("/") || path.startsWith("\\") || /^[A-Za-z]:/.test(path)) return "absolute, drive-qualified, or rooted path";
  if (path.includes("\\")) return "backslash separator";
  const segments = path.split("/");
  if (segments.some((segment) => segment.length === 0 || segment === "." || segment === "..")) return "empty, dot, or traversal segment";
  for (const segment of segments) {
    if (/[\u0000-\u001f\u007f]/.test(segment)) return "control character";
    if (/[<>:\"|?*]/.test(segment)) return "invalid filename character";
    if (/[ .]$/.test(segment)) return "segment ends in space or dot";
    const device = segment.split(".", 1)[0].toUpperCase();
    if (/^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$/.test(device)) return "reserved Windows device segment";
  }
  return undefined;
}

function preflight(request: MatXformRequest): string | undefined {
  const ids = new Set<string>();
  const paths = new Set<string>();
  for (const artifact of request.artifacts) {
    if (ids.has(artifact.artifact_id)) return "duplicate artifact_id";
    ids.add(artifact.artifact_id);
    const pathErrorMessage = pathError(artifact.relative_path);
    if (pathErrorMessage) return `${artifact.relative_path}: ${pathErrorMessage}`;
    const key = artifact.relative_path.toLocaleLowerCase("en-US");
    if (paths.has(key)) return "case-insensitive duplicate relative_path";
    paths.add(key);
  }
  return undefined;
}

function digest(bytes: Buffer): string { return `sha256:${createHash("sha256").update(bytes).digest("hex")}`; }
function nowMs(): number { return Number(process.hrtime.bigint()) / 1_000_000; }

export function validateRequest(value: unknown): { request?: MatXformRequest; identity?: string; error?: string } {
  const parsed = MatXformRequestSchema.safeParse(value);
  if (!parsed.success) return { error: parsed.error.issues.map((issue) => issue.message).join("; ") };
  const preflightError = preflight(parsed.data);
  if (preflightError) return { request: parsed.data, identity: requestIdentity(parsed.data), error: preflightError };
  return { request: parsed.data, identity: requestIdentity(parsed.data) };
}

export function materialize(request: MatXformRequest, options: MaterializeOptions): { result: MatXformResult; receipt: MatXformReceipt } {
  const started = new Date();
  const totalStart = nowMs();
  const identity = requestIdentity(request);
  const outputRoot = resolve(options.outputRoot);
  const binding = options.binding ?? "mat-xform://typescript/v1";
  const validationStart = nowMs();
  const validationError = preflight(request);
  const validationMs = nowMs() - validationStart;
  let result: MatXformResult;
  if (validationError) {
    result = errorResult(request, identity, "BLOCKED", "NONE", "INVALID_PATH_OR_DUPLICATE", validationError, validationMs);
  } else if (statExists(outputRoot)) {
    result = errorResult(request, identity, "BLOCKED", "NONE", "OUTPUT_EXISTS", "final output root already exists", validationMs);
  } else {
    const stage = `${outputRoot}.staging-${identity.slice(7)}`;
    const materializationStart = nowMs();
    try {
      mkdirSync(stage);
      const expected = request.artifacts.map((artifact) => {
        const bytes = Buffer.from(artifact.utf8_text, "utf8");
        const destination = join(stage, ...artifact.relative_path.split("/"));
        mkdirSync(dirname(destination), { recursive: true });
        writeFileSync(destination, bytes, { flag: "wx" });
        return { artifact_id: artifact.artifact_id, relative_path: artifact.relative_path, bytes: bytes.length, sha256: digest(bytes) };
      });
      for (const artifact of expected) {
        const bytes = readFileSync(join(stage, ...artifact.relative_path.split("/")));
        if (bytes.length !== artifact.bytes || digest(bytes) !== artifact.sha256) throw new Error("staged bytes failed verification");
      }
      renameSync(stage, outputRoot);
      for (const artifact of expected) {
        const bytes = readFileSync(join(outputRoot, ...artifact.relative_path.split("/")));
        if (bytes.length !== artifact.bytes || digest(bytes) !== artifact.sha256) throw new Error("final bytes failed verification");
      }
      result = MatXformResultSchema.parse({ contract_version: RESULT_CONTRACT_VERSION, request_identity: identity, request_id: request.request_id, batch_id: request.batch_id, result_status: "PASS", effect_state: "CONFIRMED", artifact_count: expected.length, artifacts: expected, timings: { validation_ms: validationMs, materialization_ms: nowMs() - materializationStart, total_ms: nowMs() - totalStart } });
    } catch (error) {
      const targetExists = statExists(outputRoot);
      result = errorResult(request, identity, targetExists ? "UNAVAILABLE" : "FAIL", targetExists ? "UNKNOWN" : "NONE", "MATERIALIZATION_FAILED", error instanceof Error ? error.message : String(error), validationMs);
      if (!targetExists && statExists(stage)) rmSync(stage, { recursive: true, force: true });
    }
  }
  const completed = new Date();
  const receipt = MatXformReceiptSchema.parse({ contract_version: RECEIPT_CONTRACT_VERSION, request_identity: identity, request_id: request.request_id, batch_id: request.batch_id, selected_binding_ref: binding, started_at: started.toISOString(), completed_at: completed.toISOString(), result_status: result.result_status, effect_state: result.effect_state, output_root: outputRoot, artifacts: result.artifacts, authority_created: false, Product_effect: "NONE" });
  return { result, receipt };
}

function statExists(path: string): boolean { try { statSync(path); return true; } catch { return false; } }

export function writePublication(value: { result: MatXformResult; receipt: MatXformReceipt }, options: MaterializeOptions): void {
  if (options.resultPath) writeFileSync(resolve(options.resultPath), `${JSON.stringify(value.result, null, 2)}\n`, "utf8");
  if (options.receiptPath) writeFileSync(resolve(options.receiptPath), `${JSON.stringify(value.receipt, null, 2)}\n`, "utf8");
}
