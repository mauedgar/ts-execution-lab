export type Provider = "local-commander" | "github-actions";

export interface Binding {
  provider: Provider;
  repository?: string;
  workflow?: string;
  ref?: string;
}

export interface ExecutionRequest {
  schema: "ts-execution-request/v0";
  request_id: string;
  Product_ref: string;
  Product_operation_ref: string;
  ExecutionAttempt_ref: string;
  execution_profile_ref: string;
  subject_ref: string;
  context_id: string;
  input: Record<string, unknown>;
  binding: Binding;
}

export interface ProfileBinding {
  provider: Provider;
  entrypoint: string;
  runtime?: string;
}

export interface ExecutionProfile {
  schema: "ts-execution-profile/v0";
  profile_ref: string;
  profile_id: string;
  status: "QUALIFIED" | "CANDIDATE" | "RETIRED";
  input: { kind: string; max_bytes: number };
  output: { semantic_digest_alg: string; receipt: string };
  bindings: ProfileBinding[];
}

export interface ContextMaterialization {
  class: "REF_ONLY" | "INLINE_SMALL" | "FROZEN_BUNDLE";
  ref: string;
  bytes?: number;
  required?: boolean;
  reason?: string;
}

export interface ExecutionContextManifest {
  schema: "ts-execution-context-manifest/v0";
  context_id: string;
  Product_ref: string;
  cutoff: string;
  baseline_refs: string[];
  delta_refs: string[];
  unknowns: string[];
  materializations: ContextMaterialization[];
}

export type ResultClass = "SUCCESS" | "REJECTED_REQUEST" | "PROFILE_ERROR" | "PROFILE_FAILURE";
export type EffectState = "SUCCESS" | "EFFECT_NONE" | "FAILURE" | "EFFECT_UNKNOWN";

export interface Observation {
  binding: string;
  profile: string;
  result_class: ResultClass;
  effect_state: EffectState;
  timings: { validation_ms: number; profile_ms: number; total_ms: number };
  subprocess_count: number;
}

export interface ExecutionResult {
  schema: "ts-execution-result/v0";
  request_id: string;
  profile: string;
  result_class: ResultClass;
  effect_state: EffectState;
  semantic_digest?: string;
  profile_output?: Record<string, unknown>;
  errors?: string[];
  observation: Observation;
}

export interface ExecutionReceipt {
  schema: "ts-execution-receipt/v0";
  operation_id: string;
  provider: Provider;
  repository: string;
  head_sha: string;
  run_id: string;
  run_attempt: string;
  runner_os: string;
  status: "COMPLETE";
  authority_created: false;
  Product_effect_created: false;
  ExecutionAttempt_ref: string;
  execution_profile_ref: string;
  semantic_digest?: string;
  result_artifact_id?: string;
  result_artifact_digest?: string;
  observation?: Observation;
}

export function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === "object" && v !== null && !Array.isArray(v);
}

export function validateRequest(v: unknown): string[] {
  const errors: string[] = [];
  if (!isRecord(v)) return ["request must be a JSON object"];
  const req = v as Record<string, unknown>;
  if (req.schema !== "ts-execution-request/v0") errors.push("schema must be ts-execution-request/v0");
  for (const key of ["request_id", "Product_ref", "Product_operation_ref", "ExecutionAttempt_ref", "execution_profile_ref", "subject_ref", "context_id"]) {
    if (typeof req[key] !== "string" || req[key].length === 0) errors.push(`${key} must be a non-empty string`);
  }
  const allowed = new Set(["schema", "request_id", "Product_ref", "Product_operation_ref", "ExecutionAttempt_ref", "execution_profile_ref", "subject_ref", "context_id", "input", "binding"]);
  for (const key of Object.keys(req)) if (!allowed.has(key)) errors.push(`unexpected property: ${key}`);
  if (!isRecord(req.input)) errors.push("input must be an object");
  if (!isRecord(req.binding)) {
    errors.push("binding must be an object");
  } else {
    if (req.binding.provider !== "local-commander" && req.binding.provider !== "github-actions") {
      errors.push("binding.provider must be local-commander or github-actions");
    }
    for (const key of Object.keys(req.binding)) if (!["provider", "repository", "workflow", "ref"].includes(key)) errors.push(`unexpected binding property: ${key}`);
    for (const key of ["repository", "workflow", "ref"] as const) if (req.binding[key] !== undefined && typeof req.binding[key] !== "string") errors.push(`binding.${key} must be a string`);
  }
  return errors;
}

export function validateContextManifest(v: unknown): string[] {
  const errors: string[] = [];
  if (!isRecord(v)) return ["manifest must be a JSON object"];
  if (v.schema !== "ts-execution-context-manifest/v0") errors.push("schema must be ts-execution-context-manifest/v0");
  if (typeof v.context_id !== "string" || !v.context_id) errors.push("context_id required");
  if (typeof v.Product_ref !== "string" || !v.Product_ref) errors.push("Product_ref required");
  if (typeof v.cutoff !== "string" || !v.cutoff) errors.push("cutoff required");
  for (const k of ["baseline_refs", "delta_refs", "unknowns"]) if (!Array.isArray(v[k]) || (v[k] as unknown[]).some((x) => typeof x !== "string")) errors.push(`${k} must be string[]`);
  if (!Array.isArray(v.materializations)) errors.push("materializations must be an array");
  else for (const m of v.materializations) {
    if (!isRecord(m) || !["REF_ONLY", "INLINE_SMALL", "FROZEN_BUNDLE"].includes(m.class as string) || typeof m.ref !== "string" || !m.ref) errors.push("invalid materialization entry");
  }
  return errors;
}

export function canonicalize(value: unknown): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return "[" + value.map(canonicalize).join(",") + "]";
  const keys = Object.keys(value as Record<string, unknown>).sort();
  return "{" + keys.map((k) => JSON.stringify(k) + ":" + canonicalize((value as Record<string, unknown>)[k])).join(",") + "}";
}
