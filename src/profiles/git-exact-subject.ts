import { execFileSync } from "node:child_process";
import { isRecord } from "../contracts.ts";
import { ProfileInputError } from "./canonical-sha256.ts";
import type { ProfileExecution } from "../registry.ts";

export interface GitExactSubjectOutput extends Record<string, unknown> {
  profile: "git-exact-subject/v0";
  repository: string;
  commit: string;
  tree: string;
  subject: string;
  expected_subject?: string;
  subject_matches?: boolean;
  correspondence: { commit_parseable: boolean; tree_parseable: boolean };
}

export function runGitExactSubject(input: Record<string, unknown>): ProfileExecution {
  if (!isRecord(input) || typeof input.repository !== "string" || input.repository.length === 0) {
    throw new ProfileInputError("input.repository must be a non-empty path string");
  }
  if (input.expected_subject !== undefined && typeof input.expected_subject !== "string") {
    throw new ProfileInputError("input.expected_subject must be a string when present");
  }
  if (input.ref !== undefined && (typeof input.ref !== "string" || input.ref.length === 0)) {
    throw new ProfileInputError("input.ref must be a non-empty string when present");
  }
  for (const key of Object.keys(input)) {
    if (!new Set(["repository", "expected_subject", "ref"]).has(key)) {
      throw new ProfileInputError(`unexpected git profile input: ${key}`);
    }
  }

  const repository = input.repository;
  const ref = typeof input.ref === "string" ? input.ref : "HEAD";
  let subprocessCount = 0;
  const git = (args: string[]): string => {
    subprocessCount += 1;
    return execFileSync("git", ["-C", repository, ...args], { encoding: "utf8" }).trim();
  };

  const log = git(["log", "-1", "--format=%H%x00%T%x00%s", "--end-of-options", ref]);
  const [commit, tree, subject, ...extra] = log.split("\0");
  if (!commit || !tree || subject === undefined || extra.length > 0) {
    throw new ProfileInputError("unexpected git log output");
  }
  const parsedCommit = git(["rev-parse", "--verify", "--end-of-options", `${ref}^{commit}`]);
  const parsedTree = git(["rev-parse", "--verify", "--end-of-options", `${ref}^{tree}`]);
  const output: GitExactSubjectOutput = {
    profile: "git-exact-subject/v0",
    repository,
    commit,
    tree,
    subject,
    correspondence: {
      commit_parseable: parsedCommit === commit,
      tree_parseable: parsedTree === tree,
    },
  };
  if (typeof input.expected_subject === "string") {
    output.expected_subject = input.expected_subject;
    output.subject_matches = subject === input.expected_subject;
  }
  return { output, subprocessCount };
}
