import { createHash } from "node:crypto";
import { canonicalize, isRecord } from "../contracts.ts";

export const MAX_BYTES = 65536;

export interface ProfileOutput {
  profile: "canonical-sha256/v0";
  input_bytes: number;
  canonical_bytes: number;
  semantic_digest: string;
}

export function runCanonicalSha256(input: Record<string, unknown>): ProfileOutput {
  if (!isRecord(input) || !isRecord(input.payload_json)) {
    throw new ProfileInputError("input.payload_json must be a JSON object");
  }
  const payload = input.payload_json;
  const canonical = canonicalize(payload);
  const canonicalBytes = Buffer.byteLength(canonical, "utf8");
  if (canonicalBytes > MAX_BYTES) {
    throw new ProfileInputError(`payload exceeds ${MAX_BYTES} bytes: ${canonicalBytes}`);
  }
  const raw = JSON.stringify(payload);
  return {
    profile: "canonical-sha256/v0",
    input_bytes: Buffer.byteLength(raw, "utf8"),
    canonical_bytes: canonicalBytes,
    semantic_digest: "sha256:" + createHash("sha256").update(canonical, "utf8").digest("hex"),
  };
}

export class ProfileInputError extends Error {}
