import { readFileSync } from "node:fs";
import { materialize, validateRequest, writePublication } from "./materializer.ts";
import { MatXformResultSchema } from "./contracts.ts";

function usage(): never { console.error("usage: node src/mat-xform/cli.ts validate <request.json> | materialize <request.json> --out <path> [--result <path>] [--receipt <path>] [--binding <ref>]"); process.exit(2); }
function option(args: string[], name: string): string | undefined { const index = args.indexOf(name); return index < 0 ? undefined : args[index + 1]; }
function load(path: string): unknown { return JSON.parse(readFileSync(path, "utf8")); }

const [command, requestPath, ...args] = process.argv.slice(2);
if (!command || !requestPath) usage();
let value: unknown;
try { value = load(requestPath); } catch (error) { console.error(error instanceof Error ? error.message : String(error)); process.exit(1); }
const checked = validateRequest(value);
if (!checked.request || !checked.identity) {
  console.error(checked.error ?? "invalid request");
  process.exit(1);
}
if (command === "validate") {
  const result = MatXformResultSchema.parse({ contract_version: "ts-mat-xform-result/v1", request_identity: checked.identity, request_id: checked.request.request_id, batch_id: checked.request.batch_id, result_status: checked.error ? "BLOCKED" : "PASS", effect_state: "NONE", artifact_count: 0, artifacts: [], timings: { validation_ms: 0, materialization_ms: 0, total_ms: 0 }, ...(checked.error ? { error: { code: "INVALID_PATH_OR_DUPLICATE", message: checked.error } } : {}) });
  console.log(JSON.stringify(result));
  process.exit(checked.error ? 1 : 0);
}
if (command !== "materialize") usage();
const outputRoot = option(args, "--out");
if (!outputRoot) usage();
const publication = materialize(checked.request, { outputRoot, resultPath: option(args, "--result"), receiptPath: option(args, "--receipt"), binding: option(args, "--binding") });
console.log(JSON.stringify(publication.result));
try { writePublication(publication, { outputRoot, resultPath: option(args, "--result"), receiptPath: option(args, "--receipt") }); } catch (error) { console.error(`PUBLICATION_FAILED: ${error instanceof Error ? error.message : String(error)}`); process.exit(1); }
if (publication.result.result_status !== "PASS") process.exit(1);
