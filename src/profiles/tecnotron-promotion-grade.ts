import { execFileSync, spawnSync } from "node:child_process";
import { realpathSync } from "node:fs";
import { resolve, join } from "node:path";
import { isRecord } from "../contracts.ts";
import { ProfileInputError } from "./canonical-sha256.ts";
import type { ProfileExecution } from "../registry.ts";

const SHA = /^[0-9a-f]{40}$/;
const SUITE: ReadonlyArray<readonly [string, string[]]> = [
  ["npm-ci", ["ci"]],
  ["npm-rebuild", ["rebuild"]],
  ["workspace-verify", ["run", "workspace:verify"]],
  ["typecheck", ["run", "typecheck"]],
  ["build", ["run", "build"]],
  ["full-tests", ["test"]],
  ["contracts-check", ["run", "contracts:check"]],
];

export function runTecnotronPromotionGrade(input: Record<string, unknown>): ProfileExecution {
  if (!isRecord(input) ||
      Object.keys(input).sort().join(",") !== "expected_commit,expected_parent,expected_tree,repository" ||
      typeof input.repository !== "string" ||
      typeof input.expected_commit !== "string" || !SHA.test(input.expected_commit) ||
      typeof input.expected_parent !== "string" || !SHA.test(input.expected_parent) ||
      typeof input.expected_tree !== "string" || !SHA.test(input.expected_tree)) {
    throw new ProfileInputError("requires only repository, expected_commit, expected_parent, expected_tree (40-char lowercase Git SHAs)");
  }

  // Only disposable Actions checkouts; npm commands modify temporary workspace files.
  // No canonical Product repository ref, Product lifecycle, or Product state is modified.
  if (process.env.GITHUB_ACTIONS !== "true" || !process.env.GITHUB_WORKSPACE) {
    throw new ProfileInputError("tecnotron promotion profile requires isolated GitHub Actions workspace");
  }
  const workspace = realpathSync(process.env.GITHUB_WORKSPACE);
  const expectedLocation = join(workspace, "product");
  let repository: string;
  try {
    repository = realpathSync(resolve(input.repository));
  } catch {
    throw new ProfileInputError("repository checkout not found");
  }
  if (repository !== expectedLocation) {
    throw new ProfileInputError("repository must be the isolated Actions product/ checkout");
  }

  let subprocessCount = 0;
  const git = (...args: string[]): string => {
    subprocessCount++;
    return execFileSync("git", ["-C", repository, ...args], {
      encoding: "utf8", timeout: 30000,
    }).trim();
  };
  const commit = git("rev-parse", "--verify", "HEAD^{commit}");
  const tree = git("rev-parse", "--verify", "HEAD^{tree}");
  const parents = git("rev-list", "--parents", "-n", "1", "HEAD").split(" ");
  if (commit !== input.expected_commit || tree !== input.expected_tree ||
      parents.length !== 2 || parents[0] !== commit || parents[1] !== input.expected_parent) {
    throw new ProfileInputError("exact candidate commit/tree/parent mismatch");
  }
  const origin = git("remote", "get-url", "origin");
  if (!/^https:\/\/github\.com\/mauedgar\/tecnotron-ai(?:\.git)?\/?$/.test(origin)) {
    throw new ProfileInputError("unexpected Product repository origin");
  }
  if (git("status", "--porcelain", "--untracked-files=no") !== "") {
    throw new ProfileInputError("Product checkout contains tracked modifications");
  }

  const stages: Array<{ stage: string; status: "PASS"; duration_ms: number }> = [];
  for (const [name, args] of SUITE) {
    const start = performance.now();
    const execution = spawnSync("npm", args, {
      cwd: repository, encoding: "utf8",
      env: { ...process.env, CI: "true" },
      timeout: 600000, maxBuffer: 16 * 1024 * 1024, shell: false,
    });
    subprocessCount++;
    if (execution.error || execution.status !== 0) {
      const detail = (execution.stderr || execution.stdout || "").slice(-1200).replace(/[\r\n]+/g, " ");
      throw new Error(`validation stage ${name} failed (exit=${execution.status}, signal=${execution.signal}): ${execution.error?.message || detail}`);
    }
    stages.push({ stage: name, status: "PASS", duration_ms: Math.round(performance.now() - start) });
  }
  return {
    output: {
      profile: "tecnotron-promotion-grade/v0",
      repository: "mauedgar/tecnotron-ai",
      commit, tree, parent: parents[1],
      subject_correspondence: "EXACT",
      stages,
      promotion_grade_validation: "PASS",
      Product_effect: "NONE",
    },
    subprocessCount,
  };
}
