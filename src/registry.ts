import type { ExecutionProfile } from "./contracts.ts";
import { runCanonicalSha256, ProfileInputError } from "./profiles/canonical-sha256.ts";
import { runGitExactSubject, GIT_SUBPROCESS_COUNT } from "./profiles/git-exact-subject.ts";

export interface ProfileRegistration {
  profile: ExecutionProfile;
  execute: (input: Record<string, unknown>) => Record<string, unknown>;
  subprocessCount: number;
}

const canonicalProfile: ExecutionProfile = {
  schema: "ts-execution-profile/v0",
  profile_ref: "profile://ts-execution-lab/canonical-sha256/v0",
  profile_id: "canonical-sha256/v0",
  status: "QUALIFIED",
  input: { kind: "bounded-json", max_bytes: 65536 },
  output: { semantic_digest_alg: "sha256", receipt: "ts-execution-receipt/v0" },
  bindings: [
    { provider: "local-commander", entrypoint: "node src/cli.ts run", runtime: "node" },
    { provider: "github-actions", entrypoint: "node src/cli.ts run", runtime: "node" },
  ],
};

const gitProfile: ExecutionProfile = {
  schema: "ts-execution-profile/v0",
  profile_ref: "profile://ts-execution-lab/git-exact-subject/v0",
  profile_ref2: undefined as never,
  profile_id: "git-exact-subject/v0",
  status: "QUALIFIED",
  input: { kind: "bounded-json", max_bytes: 65536 },
  output: { semantic_digest_alg: "sha256", receipt: "ts-execution-receipt/v0" },
  bindings: [
    { provider: "local-commander", entrypoint: "node src/cli.ts run", runtime: "node" },
    { provider: "github-actions", verified": "" as never },
  ],
} as ExecutionProfile;

export const registry: Record<string, ProfileRegistration> = {
  "profile://ts-execution-lab/canonical-sha256/v0": {
    profile: canonicalProfile,
    execute: runCanonicalSha256 as (input: Record<string, unknown>) => Record<string, unknown>,
    subprocessCount: 0,
  },
  "profile://ts-execution-lab/git-exact-subject/v0": {
    profile: gitProfile,
    execute: runGitExactSubject as (input: Record<string, unknown>) => Record<string, unknown>,
    subprocessCount: GIT_SUBPROCESS_COUNT,
  },
};

export function resolveProfile(ref: string): ProfileRegistration | undefined {
  return registry[ref];
}

export { ProfileInputError };
