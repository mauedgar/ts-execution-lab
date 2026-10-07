import { runCanonicalSha256, ProfileInputError } from "./profiles/canonical-sha256.ts";
import { runGitExactSubject } from "./profiles/git-exact-subject.ts";

export interface ExecutionProfile {
  contract_version: "ts-execution-profile/v0.2";
  profile_ref: string;
  profile_id: string;
  input: { kind: "bounded-json"; max_bytes: number };
  effect_class: "READ_ONLY";
}

export interface ProfileExecution {
  output: Record<string, unknown>;
  subprocessCount: number;
}

export interface ProfileRegistration {
  profile: ExecutionProfile;
  execute: (input: Record<string, unknown>) => ProfileExecution;
}

const profiles: ProfileRegistration[] = [
  {
    profile: {
      contract_version: "ts-execution-profile/v0.2",
      profile_ref: "profile://ts-execution-lab/canonical-sha256/v0",
      profile_id: "canonical-sha256/v0",
      input: { kind: "bounded-json", max_bytes: 65536 },
      effect_class: "READ_ONLY",
    },
    execute: (input) => ({ output: runCanonicalSha256(input), subprocessCount: 0 }),
  },
  {
    profile: {
      contract_version: "ts-execution-profile/v0.2",
      profile_ref: "profile://ts-execution-lab/git-exact-subject/v0",
      profile_id: "git-exact-subject/v0",
      input: { kind: "bounded-json", max_bytes: 65536 },
      effect_class: "READ_ONLY",
    },
    execute: runGitExactSubject,
  },
];

export const registry = new Map(profiles.map((registration) => [registration.profile.profile_ref, registration]));

export function resolveProfile(ref: string): ProfileRegistration | undefined {
  return registry.get(ref);
}

export function listProfiles(): ExecutionProfile[] {
  return profiles.map(({ profile }) => profile);
}

export { ProfileInputError };
