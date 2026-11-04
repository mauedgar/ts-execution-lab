"use strict";
// R2 direct Node pg driver proof against an isolated synthetic PostgreSQL service.
const assert=require('node:assert/strict');
const {Client}=require('pg');
async function main(){
  const url=process.env.R1_DATABASE_URL;
  assert.match(url||'',/^postgresql:\/\/.*@127\.0\.0\.1:5432\//);
  const client=new Client({connectionString:url});
  await client.connect();
  try{
    await client.query('BEGIN');
    await client.query('CREATE TABLE IF NOT EXISTS ts_r2_pg_probe(id int PRIMARY KEY, n int NOT NULL)');
    await client.query('INSERT INTO ts_r2_pg_probe VALUES (1, 4)');
    const r=await client.query('SELECT n FROM ts_r2_pg_probe WHERE id=1');
    assert.equal(r.rows[0].n,4);
    await client.query('ROLLBACK');
    const present=await client.query("SELECT to_regclass('public.ts_r2_pg_probe') AS table_name");
    assert.equal(present.rows[0].table_name,null);
    console.log('PASS|R2|pg_real_postgresql|transaction=rollback|synthetic_only=true');
  }finally{await client.end();}
}
main().catch(e=>{console.error('FAIL|R2|pg_real_postgresql',e);process.exitCode=1;});
