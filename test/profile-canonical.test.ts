import assert from "node:assert/strict";
import test from "node:test";
import { ProfileInputError, runCanonicalSha256 } from "../src/profiles/canonical-sha256.ts";

test("canonical profile preserves v0.1 semantic digest", () => {
  const first = runCanonicalSha256({ payload_json: { hello: "world", n: 1 } });
  const reordered = runCanonicalSha256({ payload_json: { n: 1, hello: "world" } });
  assert.equal(first.semantic_digest, "sha256:32b769982a3a6e2df120530b06dcbaf1e8f75e004ceea92ac3e91bd7a248d728");
  assert.equal(reordered.semantic_digest, first.semantic_digest);
  assert.equal(first.canonical_bytes, 23);
});

test("canonical profile rejects non-object and oversized payloads", () => {
  assert.throws(() => runCanonicalSha256({ payload_json: "text" }), ProfileInputError);
  assert.throws(() => runCanonicalSha256({ payload_json: { value: "x".repeat(65536) } }), ProfileInputError);
});
