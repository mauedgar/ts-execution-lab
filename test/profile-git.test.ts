import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { resolve } from "node:path";
import test from "node:test";
import { ProfileInputError } from "../src/profiles/canonical-sha256.ts";
import { runGitExactSubject } from "../src/profiles/git-exact-subject.ts";

const root = resolve(import.meta.dirname, "..");

test("git profile reports exact commit, tree, and subject correspondence", () => {
  const commit = execFileSync("git", ["-C", root, "rev-parse", "HEAD"], { encoding: "utf8" }).trim();
  const tree = execFileSync("git", ["-C", root, "rev-parse", "HEAD^{tree}"], { encoding: "utf8" }).trim();
  const subject = execFileSync("git", ["-C", root, "log", "-1", "--format=%s"], { encoding: "utf8" }).trim();
  const execution = runGitExactSubject({ repository: root, ref: "HEAD", expected_subject: subject });
  assert.equal(execution.subprocessCount, 3);
  assert.equal(execution.output.commit, commit);
  assert.equal(execution.output.tree, tree);
  assert.equal(execution.output.subject_matches, true);
  assert.deepEqual(execution.output.correspondence, { commit_parseable: true, tree_parseable: true });
});

test("git profile rejects transported arguments and invalid refs before subprocesses", () => {
  assert.throws(() => runGitExactSubject({ repository: root, args: ["status"] }), ProfileInputError);
  assert.throws(() => runGitExactSubject({ repository: root, ref: "" }), ProfileInputError);
});
