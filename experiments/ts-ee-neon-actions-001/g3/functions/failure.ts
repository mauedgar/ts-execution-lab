import { neon } from "@neondatabase/serverless";

/** Deliberately returns HTTP503 for first delivery and commits an idempotency key. */
export default {
  async fetch(request: Request): Promise<Response> {
    if (request.method !== "POST" || !request.headers.get("x-neon-trigger-invocation-id")) {
      return new Response("native trigger required", { status:403 });
    }
    let body: { data?: { scheduled_at?: unknown } };
    try { body=await request.json(); } catch { return new Response("invalid payload", {status:400}); }
    const scheduledAt=body?.data?.scheduled_at;
    if (typeof scheduledAt!=="string" || !Number.isFinite(Date.parse(scheduledAt))) {
      return new Response("scheduled_at missing", {status:400});
    }
    const url=process.env.DATABASE_URL;
    if (!url) return new Response("database unavailable", {status:503});
    const sql=neon(url);
    const rows=await sql`INSERT INTO ts_ee_g5.failure_events(scheduled_at,attempts,state)
       VALUES (${scheduledAt},1,'failed_once')
       ON CONFLICT (scheduled_at) DO UPDATE SET attempts=ts_ee_g5.failure_events.attempts+1
       RETURNING attempts`;
    const count=Number(rows[0]?.attempts??0);
    if (count===1) {
      console.warn("TS_EE_G5_INTENTIONAL_FIRST_HTTP503", {scheduled_at:scheduledAt});
      return new Response("synthetic first-attempt failure", {status:503});
    }
    await sql`UPDATE ts_ee_g5.failure_events SET state='recovered' WHERE scheduled_at=${scheduledAt} AND state='failed_once'`;
    console.info("TS_EE_G5_RECOVERY_IDEMPOTENT", {attempts:count,scheduled_at:scheduledAt});
    return Response.json({gate:"G5",result:"recovered"});
  },
};
