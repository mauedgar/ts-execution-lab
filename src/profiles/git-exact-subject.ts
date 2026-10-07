import { execFileSync } from "node:child_process";
import { isRecord } from "../contracts.ts";
import { ProfileInputError } from "./canonical-sha256.ts";

export interface GitExactSubjectOutput {
  profile: "git-exact-subject/v0";
  repository: string;
  commit: string;
  tree: string;
  subject: string;
  expected_subject?: string;
  subject_matches?: boolean;
  correspondence: { commit_parseable: boolean; tree_parseable: boolean };
}

export const GIT_SUBPROCESS_COUNT = 3;

export function runGitExactSubject(input: Record<string, unknown>): GitExactSubjectOutput {
  if (!isRecord(input) || typeof input.repository !== "string" || input.repository.length === 0) {
    throw new ProfileInputError("input.repository must be a non-empty path string");
  }
  if (input.expected_subject !== undefined && typeof input.expected_subject !== "string") {
    throw new ProfileInputError("input.expected_subject must be a string when present");
  }
  if (input.ref !== undefined && typeof input.ref !== "string") {
    throw new ProfileInputError("input.ref must be a string when present");
  }
  const repo = input.repository;
  const rev = typeof input.ref === "string" && input.ref.length > 0 ? input.ref : "HEAD";
  const log = git(repo, ["log", "-1", "--format=%H%x00%T%x00%s", rev]);
  const parts = log.split("\0");
  if (parts.length < 3) throw new ProfileInputError("unexpected git log output");
  const [commit, tree, subject] = parts;
  const revParsed = git(repo, ["rev-parse", rev, "^{commit}"]);
  const treeParsed = git(repo, ["rev-parse", rev, "^{tree}"]);
  const out: GitExactSubjectOutput = {
    profile: "git-exact-subject/v0",
    repository: repo,
    commit,
    tree,
    subject,
    correspondence: {
      commit_parseable: revParsed.trim() === commit,
      tree_parseable: treeParsed.trim() === tree,
    },
  };
  if (typeof input.expected_subject === "string") {
    out.expected_subject = input.expected_subject;
    out.subject_matches = subject === input.expected_subject;
  }
  return out;
}

function git(repo: string, args: string[]): string {
  return execFileSync("git", ["-C", repo, ...args], { encoding: "utf8" }).trim();
}

export { ProfileInputError };
