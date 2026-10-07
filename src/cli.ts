#!/usr/bin/env node
import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { performance } from "node:perf_hooks";
import type { ZodError } from "zod";
import {
  ExecutionReceiptSchema,
  ExecutionRequestSchema,
  ExecutionResultSchema,
  RECEIPT_CONTRACT_VERSION,
  REQUEST_CONTRACT_VERSION,
  RESULT_CONTRACT_VERSION,
  recoverRequestIdentity,
  sha256Identity,
  type ExecutionReceipt,
  type ExecutionRequest,
  type ExecutionResult,
  type RecoverableRequestIdentity,
} from "./contracts.ts";
import { listProfiles, ProfileInputError, resolveProfile } from "./registry.ts";

type ResultStatus = ExecutionResult["result_status"];
type EffectState = ExecutionResult["effect_state"];

interface CliOptions {
  outDir: string;
  selectedBinding: string;
}

interface RequestParseSuccess {
  ok: true;
  request: ExecutionRequest;
  requestIdentity: string;
}

interface RequestParseFailure {
  ok: false;
  value?: unknown;
  requestIdentity?: string;
  identity?: RecoverableRequestIdentity;
  code: "INVALID_JSON" | "INVALID" | "UNSUPPORTED_VERSION";
  errors: Array<{ code: string; message: string; path?: string }>;
}

type RequestParse = RequestParseSuccess | RequestParseFailure;

async function main(args: string[]): Promise<number> {
  const [command, requestPath, ...rest] = args;
  if (command === "profiles" && requestPath === undefined) {
    process.stdout.write(`${JSON.stringify(listProfiles(), null, 2)}\n`);
    return 0;
  }
  if ((command !== "validate" && command !== "run") || !requestPath) {
    process.stderr.write("usage: ts-exec <validate|run> <request.json> [--out <dir>] [--binding <ref>]\n       ts-exec profiles\n");
    return 2;
  }

  let options: CliOptions;
  try {
    options = parseOptions(rest);
  } catch (error) {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    return 2;
  }

  const startedAt = new Date().toISOString();
  const validationStarted = performance.now();
  const parsed = await parseRequest(requestPath);
  const validationMs = elapsed(validationStarted);
  if (command === "validate") {
    if (parsed.ok) {
      process.stdout.write(`${JSON.stringify({ status: "PASS", request_identity: parsed.requestIdentity })}\n`);
      return 0;
    }
    process.stderr.write(`${JSON.stringify({ status: parsed.code, errors: parsed.errors })}\n`);
    return 1;
  }

  const totalStarted = validationStarted;
  if (!parsed.ok) {
    if (parsed.identity && parsed.requestIdentity) {
      await publishFailure(options, parsed.identity, parsed.requestIdentity, startedAt, validationMs,
        parsed.code, "BLOCKED", "NONE", parsed.errors);
    }
    process.stderr.write(`${JSON.stringify({ status: parsed.code, errors: parsed.errors })}\n`);
    return 1;
  }

  const registration = resolveProfile(parsed.request.execution_profile_ref);
  if (!registration) {
    await publishFailure(options, parsed.request, parsed.requestIdentity, startedAt, validationMs,
      "UNKNOWN_PROFILE", "UNAVAILABLE", "NONE", [{ code: "UNKNOWN_PROFILE", message: `unregistered profile: ${parsed.request.execution_profile_ref}` }]);
    return 1;
  }

  const profileStarted = performance.now();
  try {
    const execution = registration.execute(parsed.request.input);
    const profileMs = elapsed(profileStarted);
    const observation = makeObservation(options, parsed.request.execution_profile_ref, "SUCCESS", "NONE",
      validationMs, profileMs, elapsed(totalStarted), execution.subprocessCount);
    const semanticDigest = typeof execution.output.semantic_digest === "string" ? execution.output.semantic_digest : undefined;
    const result = ExecutionResultSchema.parse({
      contract_version: RESULT_CONTRACT_VERSION,
      ...pickIdentity(parsed.request),
      request_identity: parsed.requestIdentity,
      result_status: "PASS",
      effect_state: "NONE",
      ...(semanticDigest ? { semantic_digest: semanticDigest } : {}),
      profile_output: execution.output,
      observation,
    });
    const receipt = makeReceipt(options, parsed.request, parsed.requestIdentity, startedAt, result, observation);
    await publishArtifacts(options.outDir, result, receipt);
    process.stdout.write(`${JSON.stringify({ result: join(options.outDir, "result.json"), receipt: join(options.outDir, "receipt.json") })}\n`);
    return 0;
  } catch (error) {
    const profileMs = elapsed(profileStarted);
    const isInputError = error instanceof ProfileInputError;
    await publishFailure(options, parsed.request, parsed.requestIdentity, startedAt, validationMs,
      isInputError ? "PROFILE_INPUT_INVALID" : "PROFILE_ERROR", isInputError ? "BLOCKED" : "FAIL", "NONE",
      [{ code: isInputError ? "PROFILE_INPUT_INVALID" : "PROFILE_ERROR", message: error instanceof Error ? error.message : String(error) }],
      profileMs, elapsed(totalStarted));
    return 1;
  }
}

function parseOptions(args: string[]): CliOptions {
  let outDir = ".";
  let selectedBinding = process.env.TS_EXEC_SELECTED_BINDING_REF || "local-commander";
  for (let index = 0; index < args.length; index += 2) {
    const flag = args[index];
    const value = args[index + 1];
    if (!value || (flag !== "--out" && flag !== "--binding")) throw new Error(`invalid option: ${flag ?? ""}`);
    if (flag === "--out") outDir = value;
    if (flag === "--binding") selectedBinding = value;
  }
  if (!selectedBinding) throw new Error("selected binding must be non-empty");
  return { outDir: resolve(outDir), selectedBinding };
}

async function parseRequest(path: string): Promise<RequestParse> {
  let text: string;
  try {
    text = await readFile(path, "utf8");
  } catch (error) {
    return { ok: false, code: "INVALID_JSON", errors: [{ code: "READ_ERROR", message: error instanceof Error ? error.message : String(error) }] };
  }
  let value: unknown;
  try {
    value = JSON.parse(text);
  } catch (error) {
    return { ok: false, code: "INVALID_JSON", errors: [{ code: "INVALID_JSON", message: error instanceof Error ? error.message : String(error) }] };
  }
  const identity = recoverRequestIdentity(value);
  const requestIdentity = sha256Identity(value);
  if (typeof value === "object" && value !== null && "contract_version" in value &&
      (value as { contract_version?: unknown }).contract_version !== REQUEST_CONTRACT_VERSION) {
    return {
      ok: false, value, identity, requestIdentity, code: "UNSUPPORTED_VERSION",
      errors: [{ code: "UNSUPPORTED_VERSION", message: `contract_version must be ${REQUEST_CONTRACT_VERSION}`, path: "contract_version" }],
    };
  }
  const result = ExecutionRequestSchema.safeParse(value);
  if (!result.success) {
    return { ok: false, value, identity, requestIdentity, code: "INVALID", errors: zodErrors(result.error) };
  }
  return { ok: true, request: result.data, requestIdentity };
}

function zodErrors(error: ZodError): Array<{ code: string; message: string; path?: string }> {
  return error.issues.map((issue) => ({ code: issue.code, message: issue.message, ...(issue.path.length ? { path: issue.path.join(".") } : {}) }));
}

async function publishFailure(
  options: CliOptions,
  identity: RecoverableRequestIdentity,
  requestIdentity: string,
  startedAt: string,
  validationMs: number,
  resultClass: string,
  resultStatus: ResultStatus,
  effectState: EffectState,
  errors: Array<{ code: string; message: string; path?: string }>,
  profileMs = 0,
  totalMs = validationMs,
): Promise<void> {
  const observation = makeObservation(options, identity.execution_profile_ref, resultClass, effectState,
    validationMs, profileMs, totalMs, 0);
  const result = ExecutionResultSchema.parse({
    contract_version: RESULT_CONTRACT_VERSION,
    ...identity,
    request_identity: requestIdentity,
    result_status: resultStatus,
    effect_state: effectState,
    errors,
    observation,
  });
  const receipt = makeReceipt(options, identity, requestIdentity, startedAt, result, observation);
  await publishArtifacts(options.outDir, result, receipt);
}

function makeObservation(
  options: CliOptions,
  profile: string,
  resultClass: string,
  effectState: EffectState,
  validationMs: number,
  profileMs: number,
  totalMs: number,
  subprocessCount: number,
) {
  return {
    binding: options.selectedBinding,
    profile,
    result_class: resultClass,
    effect_state: effectState,
    timings: { validation_ms: validationMs, profile_ms: profileMs, total_ms: totalMs },
    subprocess_count: subprocessCount,
  };
}

function makeReceipt(
  options: CliOptions,
  identity: RecoverableRequestIdentity,
  requestIdentity: string,
  startedAt: string,
  result: ExecutionResult,
  observation: ExecutionResult["observation"],
): ExecutionReceipt {
  return ExecutionReceiptSchema.parse({
    contract_version: RECEIPT_CONTRACT_VERSION,
    Product_operation_ref: identity.Product_operation_ref,
    ExecutionAttempt_ref: identity.ExecutionAttempt_ref,
    request_identity: requestIdentity,
    selected_binding_ref: options.selectedBinding,
    started_at: startedAt,
    completed_at: new Date().toISOString(),
    result_status: result.result_status,
    effect_state: result.effect_state,
    exact_subject_ref: identity.subject_ref,
    provider_native_refs: [],
    evidence_refs: [],
    result_ref: "result.json",
    authority_created: false,
    Product_effect_created: false,
    observation,
  });
}

function pickIdentity(request: ExecutionRequest): RecoverableRequestIdentity {
  const { request_id, Product_ref, Product_operation_ref, ExecutionAttempt_ref, execution_profile_ref, subject_ref, context_id } = request;
  return { request_id, Product_ref, Product_operation_ref, ExecutionAttempt_ref, execution_profile_ref, subject_ref, context_id };
}

async function publishArtifacts(outDir: string, result: ExecutionResult, receipt: ExecutionReceipt): Promise<void> {
  await mkdir(outDir, { recursive: true });
  await writeJsonAtomic(join(outDir, "result.json"), ExecutionResultSchema.parse(result));
  await writeJsonAtomic(join(outDir, "receipt.json"), ExecutionReceiptSchema.parse(receipt));
}

async function writeJsonAtomic(path: string, value: unknown): Promise<void> {
  await mkdir(dirname(path), { recursive: true });
  const temporary = `${path}.${process.pid}.tmp`;
  await writeFile(temporary, `${JSON.stringify(value, null, 2)}\n`, "utf8");
  await rename(temporary, path);
}

function elapsed(start: number): number {
  return Math.max(0, Number((performance.now() - start).toFixed(3)));
}

process.exitCode = await main(process.argv.slice(2));
