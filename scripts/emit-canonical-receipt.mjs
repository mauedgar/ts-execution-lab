import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const required = ["OPERATION_ID", "GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "RUNNER_OS", "ATTEMPT"];
const missing = required.filter((k) => !process.env[k]);
if (missing.length > 0) {
  console.error(`Missing environment variables: ${missing.join(", ")}`);
  process.exit(1);
}
const result = JSON.parse(readFileSync("out-result.json", "utf8"));
const receipt = {
  schema: "ts-execution-receipt/v0",
  operation_id: process.env.OPERATION_ID,
  provider: "github-actions",
  repository: process.env.GITHUB_REPOSITORY,
  head_sha: process.env.GITHUB_SHA,
  run_id: process.env.GITHUB_RUN_ID,
  run_attempt: process.env.GITHUB_RUN_ATTEMPT,
  runner_os: process.env.RUNNER_OS,
  status: "COMPLETE",
  authority_created: false,
  Product_effect_created: false,
  ExecutionAttempt_ref: process.env.ATTEMPT,
  execution_profile_ref: "profile://ts-execution-lab/canonical-sha256/v0",
  semantic_digest: result.semantic_digest,
};
mkdirSync(join(process.cwd(), "out"), { recursive: true });
writeFileSync(join(process.cwd(), "out", "canonical-receipt.json"), JSON.stringify(receipt, null, 2) + "\n");
console.log(JSON.stringify(receipt, null, 2));
