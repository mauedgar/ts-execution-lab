import { createHash } from "node:crypto";
import { z } from "zod";

export const REQUEST_CONTRACT_VERSION = "ts-execution-request/v0.2" as const;
export const RESULT_CONTRACT_VERSION = "ts-execution-result/v0.2" as const;
export const RECEIPT_CONTRACT_VERSION = "ts-execution-receipt/v0.2" as const;
export const CONTEXT_MANIFEST_CONTRACT_VERSION = "ts-execution-context-manifest/v0.2" as const;

const NonEmptyString = z.string().min(1);
const JsonObject = z.record(z.string(), z.unknown());

export const ExecutionRequestSchema = z.object({
  contract_version: z.literal(REQUEST_CONTRACT_VERSION),
  request_id: NonEmptyString,
  Product_ref: NonEmptyString,
  Product_operation_ref: NonEmptyString,
  ExecutionAttempt_ref: NonEmptyString,
  execution_profile_ref: NonEmptyString,
  subject_ref: NonEmptyString,
  context_id: NonEmptyString,
  context_manifest_ref: NonEmptyString.optional(),
  input: JsonObject,
}).strict();

export type ExecutionRequest = z.infer<typeof ExecutionRequestSchema>;

export const ExecutionContextManifestSchema = z.discriminatedUnion("mode", [
  z.object({
    contract_version: z.literal(CONTEXT_MANIFEST_CONTRACT_VERSION),
    context_id: NonEmptyString,
    mode: z.literal("REF_ONLY"),
    refs: z.array(NonEmptyString).min(1),
  }).strict(),
  z.object({
    contract_version: z.literal(CONTEXT_MANIFEST_CONTRACT_VERSION),
    context_id: NonEmptyString,
    mode: z.literal("INLINE_SMALL"),
    inline: JsonObject,
  }).strict(),
  z.object({
    contract_version: z.literal(CONTEXT_MANIFEST_CONTRACT_VERSION),
    context_id: NonEmptyString,
    mode: z.literal("FROZEN_BUNDLE"),
    frozen_bundle: z.object({
      artifact_ref: NonEmptyString,
      sha256: z.string().regex(/^sha256:[0-9a-f]{64}$/),
      bytes: z.number().int().nonnegative(),
    }).strict(),
  }).strict(),
]);

export type ExecutionContextManifest = z.infer<typeof ExecutionContextManifestSchema>;

export const ResultStatusSchema = z.enum(["PASS", "PARTIAL", "FAIL", "BLOCKED", "UNAVAILABLE"]);
export const EffectStateSchema = z.enum(["NONE", "CONFIRMED", "UNKNOWN"]);

export const ObservationSchema = z.object({
  binding: NonEmptyString,
  profile: NonEmptyString,
  result_class: NonEmptyString,
  effect_state: EffectStateSchema,
  timings: z.object({
    validation_ms: z.number().nonnegative(),
    profile_ms: z.number().nonnegative(),
    total_ms: z.number().nonnegative(),
  }).strict(),
  subprocess_count: z.number().int().nonnegative(),
}).strict();

const ErrorDetailSchema = z.object({
  code: NonEmptyString,
  message: NonEmptyString,
  path: z.string().optional(),
}).strict();

const RequestIdentityFields = {
  request_id: NonEmptyString,
  Product_ref: NonEmptyString,
  Product_operation_ref: NonEmptyString,
  ExecutionAttempt_ref: NonEmptyString,
  execution_profile_ref: NonEmptyString,
  subject_ref: NonEmptyString,
  context_id: NonEmptyString,
};

export const ExecutionResultSchema = z.object({
  contract_version: z.literal(RESULT_CONTRACT_VERSION),
  ...RequestIdentityFields,
  request_identity: z.string().regex(/^sha256:[0-9a-f]{64}$/),
  result_status: ResultStatusSchema,
  effect_state: EffectStateSchema,
  semantic_digest: z.string().regex(/^sha256:[0-9a-f]{64}$/).optional(),
  profile_output: JsonObject.optional(),
  errors: z.array(ErrorDetailSchema).min(1).optional(),
  observation: ObservationSchema,
}).strict();

export type ExecutionResult = z.infer<typeof ExecutionResultSchema>;

export const ExecutionReceiptSchema = z.object({
  contract_version: z.literal(RECEIPT_CONTRACT_VERSION),
  Product_operation_ref: NonEmptyString,
  ExecutionAttempt_ref: NonEmptyString,
  request_identity: z.string().regex(/^sha256:[0-9a-f]{64}$/),
  selected_binding_ref: NonEmptyString,
  started_at: z.iso.datetime(),
  completed_at: z.iso.datetime(),
  result_status: ResultStatusSchema,
  effect_state: EffectStateSchema,
  exact_subject_ref: NonEmptyString.optional(),
  provider_native_refs: z.array(NonEmptyString),
  evidence_refs: z.array(NonEmptyString),
  result_ref: NonEmptyString,
  authority_created: z.literal(false),
  Product_effect_created: z.literal(false),
  observation: ObservationSchema,
}).strict();

export type ExecutionReceipt = z.infer<typeof ExecutionReceiptSchema>;

export type RecoverableRequestIdentity = Pick<ExecutionRequest,
  "request_id" | "Product_ref" | "Product_operation_ref" | "ExecutionAttempt_ref" |
  "execution_profile_ref" | "subject_ref" | "context_id"
>;

export function recoverRequestIdentity(value: unknown): RecoverableRequestIdentity | undefined {
  if (!isRecord(value)) return undefined;
  const recovered: Record<string, string> = {};
  for (const key of Object.keys(RequestIdentityFields)) {
    if (typeof value[key] !== "string" || value[key].length === 0) return undefined;
    recovered[key] = value[key];
  }
  return recovered as RecoverableRequestIdentity;
}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function canonicalize(value: unknown): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonicalize).join(",")}]`;
  const object = value as Record<string, unknown>;
  return `{${Object.keys(object).sort().map((key) => `${JSON.stringify(key)}:${canonicalize(object[key])}`).join(",")}}`;
}

export function sha256Identity(value: unknown): string {
  return `sha256:${createHash("sha256").update(canonicalize(value), "utf8").digest("hex")}`;
}

export function requestIdentity(value: unknown): string {
  if (!isRecord(value)) return sha256Identity(value);
  const { ExecutionAttempt_ref: _executionAttemptRef, ...mechanicalRequest } = value;
  return sha256Identity(mechanicalRequest);
}
