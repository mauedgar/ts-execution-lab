import assert from "node:assert/strict";
import test from "node:test";
import { runTecnotronPromotionGrade } from "../src/profiles/tecnotron-promotion-grade.ts";
import { ProfileInputError } from "../src/profiles/canonical-sha256.ts";

const sha = "7f33fedcb97c00355e253ac64237f734f99e7a15";
const good = {
  repository: "../product",
  expected_commit: sha,
  expected_tree: "a8ec296f737defaac7cf1dbcb88ab2f82b1f21c4",
  expected_parent: "fb820d97bd480281ba7bab8cf752897aebdf5fb7",
};

test("rejects missing identity before any commands", () => {
  assert.throws(() => runTecnotronPromotionGrade({ ...good, expected_tree: undefined }), ProfileInputError);
});
test("rejects extra caller-controlled commands", () => {
  assert.throws(() => runTecnotronPromotionGrade({ ...good, commands: ["echo bypass"] }), ProfileInputError);
});
test("rejects non-SHA exact subject", () => {
  assert.throws(() => runTecnotronPromotionGrade({ ...good, expected_commit: "HEAD" }), ProfileInputError);
});
test("disallows invocation outside qualified Actions workspace", () => {
  const originalActions = process.env.GITHUB_ACTIONS;
  const originalWorkspace = process.env.GITHUB_WORKSPACE;
  try {
    delete process.env.GITHUB_ACTIONS;
    delete process.env.GITHUB_WORKSPACE;
    assert.throws(() => runTecnotronPromotionGrade(good), ProfileInputError);
  } finally {
    if (originalActions === undefined) delete process.env.GITHUB_ACTIONS;
    else process.env.GITHUB_ACTIONS = originalActions;
    if (originalWorkspace === undefined) delete process.env.GITHUB_WORKSPACE;
    else process.env.GITHUB_WORKSPACE = originalWorkspace;
  }
});
