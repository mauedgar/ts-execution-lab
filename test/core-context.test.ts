import assert from "node:assert/strict";
import test from "node:test";
import { ExecutionContextManifestSchema } from "../src/contracts.ts";

test("context manifest preserves REF_ONLY, INLINE_SMALL, and FROZEN_BUNDLE without packaging", () => {
  const manifests = [
    {
      contract_version: "ts-execution-context-manifest/v0.2",
      context_id: "ctx-ref-only",
      mode: "REF_ONLY",
      refs: ["git://mauedgar/ts-execution-lab@HEAD"],
    },
    {
      contract_version: "ts-execution-context-manifest/v0.2",
      context_id: "ctx-inline-small",
      mode: "INLINE_SMALL",
      inline: { delta: "bounded", bytes: 23 },
    },
    {
      contract_version: "ts-execution-context-manifest/v0.2",
      context_id: "ctx-frozen-bundle",
      mode: "FROZEN_BUNDLE",
      frozen_bundle: {
        artifact_ref: "artifact://synthetic/frozen-context",
        sha256: "sha256:e4fde89f39bc53b90e9935a8015b80dd6e4135485e894094a3517fa250e344ae",
        bytes: 2048,
      },
    },
  ];

  for (const manifest of manifests) {
    assert.equal(ExecutionContextManifestSchema.safeParse(manifest).success, true);
  }
});

test("context manifest fails closed when a mode carries the wrong payload shape", () => {
  const invalid = {
    contract_version: "ts-execution-context-manifest/v0.2",
    context_id: "ctx-invalid",
    mode: "REF_ONLY",
    inline: { should_not_exist: true },
  };
  assert.equal(ExecutionContextManifestSchema.safeParse(invalid).success, false);
});
