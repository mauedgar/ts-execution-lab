import { Client, QueryResult } from 'pg';
export async function syntheticProbe(url: string): Promise<number> {
  const client: Client = new Client({connectionString:url});
  await client.connect();
  try {
    const value: QueryResult<{ n: number }> = await client.query<{n:number}>('SELECT 1::int AS n');
    return value.rows[0].n;
  } finally {
    await client.end();
  }
}
