import { createHash } from "node:crypto";
import { z } from "zod";

export const REQUEST_CONTRACT_VERSION = "ts-mat-xform-request/v1" as const;
export const RESULT_CONTRACT_VERSION = "ts-mat-xform-result/v1" as const;
export const RECEIPT_CONTRACT_VERSION = "ts-mat-xform-receipt/v1" as const;

const NonEmptyString = z.string().min(1);
const Sha256 = z.string().regex(/^sha256:[0-9a-f]{64}$/);

export const ArtifactSchema = z.object({
  artifact_id: NonEmptyString,
  relative_path: NonEmptyString,
  utf8_text: z.string(),
}).strict();

export const MatXformRequestSchema = z.object({
  contract_version: z.literal(REQUEST_CONTRACT_VERSION),
  request_id: NonEmptyString,
  batch_id: NonEmptyString,
  artifacts: z.array(ArtifactSchema).min(1),
}).strict();
export type MatXformRequest = z.infer<typeof MatXformRequestSchema>;

export const ResultArtifactSchema = z.object({
  artifact_id: NonEmptyString,
  relative_path: NonEmptyString,
  bytes: z.number().int().nonnegative(),
  sha256: Sha256,
}).strict();

export const ResultStatusSchema = z.enum(["PASS", "BLOCKED", "FAIL", "UNAVAILABLE"]);
export const EffectStateSchema = z.enum(["NONE", "CONFIRMED", "UNKNOWN"]);
const ErrorSchema = z.object({ code: NonEmptyString, message: NonEmptyString }).strict();
const TimingsSchema = z.object({ validation_ms: z.number().nonnegative(), materialization_ms: z.number().nonnegative(), total_ms: z.number().nonnegative() }).strict();

export const MatXformResultSchema = z.object({
  contract_version: z.literal(RESULT_CONTRACT_VERSION),
  request_identity: Sha256,
  request_id: NonEmptyString,
  batch_id: NonEmptyString,
  result_status: ResultStatusSchema,
  effect_state: EffectStateSchema,
  artifact_count: z.number().int().nonnegative(),
  artifacts: z.array(ResultArtifactSchema),
  timings: TimingsSchema,
  error: ErrorSchema.optional(),
}).strict();
export type MatXformResult = z.infer<typeof MatXformResultSchema>;

export const MatXformReceiptSchema = z.object({
  contract_version: z.literal(RECEIPT_CONTRACT_VERSION),
  request_identity: Sha256,
  request_id: NonEmptyString,
  batch_id: NonEmptyString,
  selected_binding_ref: NonEmptyString,
  started_at: z.iso.datetime(),
  completed_at: z.iso.datetime(),
  result_status: ResultStatusSchema,
  effect_state: EffectStateSchema,
  output_root: NonEmptyString,
  artifacts: z.array(ResultArtifactSchema),
  authority_created: z.literal(false),
  Product_effect: z.literal("NONE"),
}).strict();
export type MatXformReceipt = z.infer<typeof MatXformReceiptSchema>;

export function canonicalize(value: unknown): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonicalize).join(",")}]`;
  const object = value as Record<string, unknown>;
  return `{${Object.keys(object).sort().map((key) => `${JSON.stringify(key)}:${canonicalize(object[key])}`).join(",")}}`;
}

export function requestIdentity(request: MatXformRequest): string {
  return `sha256:${createHash("sha256").update(canonicalize(request), "utf8").digest("hex")}`;
}
