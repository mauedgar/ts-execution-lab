import { createHash } from "node:crypto";
import { readFileSync, statSync } from "node:fs";

const MAX_BYTES = 65536;

function canonicalize(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return "[" + value.map(canonicalize).join(",") + "]";
  const keys = Object.keys(value).sort();
  return "{" + keys.map((k) => JSON.stringify(k) + ":" + canonicalize(value[k])).join(",") + "}";
}

const inputPath = process.argv[2];
if (!inputPath) {
  console.error("usage: node canonical-sha256.mjs <payload.json>");
  process.exit(2);
}
const size = statSync(inputPath).size;
if (size > MAX_BYTES) {
  console.error(`payload exceeds ${MAX_BYTES} bytes: ${size}`);
  process.exit(3);
}
const raw = readFileSync(inputPath, "utf8");
let parsed;
try {
  parsed = JSON.parse(raw);
} catch {
  console.error("payload is not valid JSON");
  process.exit(4);
}
const canonical = canonicalize(parsed);
const digest = "sha256:" + createHash("sha256").update(canonical, "utf8").digest("hex");
const result = {
  profile: "canonical-sha256/v0",
  input_bytes: Buffer.byteLength(raw, "utf8"),
  canonical_bytes: Buffer.byteLength(canonical, "utf8"),
  semantic_digest: digest,
};
console.log(JSON.stringify(result, null, 2));
