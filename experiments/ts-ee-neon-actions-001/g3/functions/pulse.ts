import { neon } from "@neondatabase/serverless";

/** G3 synthetic Neon schedule handler: no external requests or Product data. */
export default {
  async fetch(request: Request): Promise<Response> {
    if (request.method !== "POST" || !request.headers.get("x-neon-trigger-invocation-id")) {
      return new Response("schedule trigger required", { status: 403 });
    }
    let data: unknown;
    try {
      data = await request.json();
    } catch {
      return new Response("invalid JSON", { status: 400 });
    }
    const body = data as { data?: { scheduled_at?: unknown } };
    const scheduledAt = body?.data?.scheduled_at;
    if (typeof scheduledAt !== "string" || !Number.isFinite(Date.parse(scheduledAt))) {
      return new Response("invalid schedule payload", { status: 400 });
    }
    const db = process.env.DATABASE_URL;
    if (!db) {
      console.error("TS_EE_G3_DATABASE_URL_MISSING");
      return new Response("database unavailable", { status: 503 });
    }
    const started = performance.now();
    const sql = neon(db);
    await sql\`INSERT INTO ts_ee_g3.pulse(scheduled_at, occurrence)
               VALUES (\${scheduledAt}, 1)
               ON CONFLICT (scheduled_at) DO NOTHING\`;
    const elapsedMs = Math.round(performance.now() - started);
    console.info("TS_EE_G3_TRIGGER_SQL_COMMIT_CONFIRMED", { elapsed_ms: elapsedMs });
    return Response.json({ gate: "G3", ok: true });
  },
};
