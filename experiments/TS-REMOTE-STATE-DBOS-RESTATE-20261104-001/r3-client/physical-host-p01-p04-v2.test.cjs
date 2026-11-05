'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const os=require('node:os');
const crypto=require('node:crypto');
const {input}=require('./physical-host-p01-p04-v2.cjs');
const goodHost='ep-ancient-flower-b6eb9w6c.c-2.sa-east-1.aws.neon.tech';
const fingerprint=crypto.createHash('sha256').update(os.hostname().toLowerCase()).digest('hex');
function withParams(host,phase,url,fn){
  const argv=process.argv.slice(),env={...process.env};
  try{
    process.argv=['node','physical-host',phase];
    process.env.TS_R3_HOST_LABEL=host;
    process.env.TS_R3_TEST_ID='R3-HOST-SYNTHETIC_20261105_011';
    process.env.TS_R3_ENROLLED_HOST_SHA256=fingerprint;
    process.env.TS_R3_ENROLLMENT_RECEIPT_REF='TS-R3-P01-'+host+'-20261105-001';
    process.env.TS_R3_DATABASE_URL=url;
    fn();
  }finally{process.argv=argv;process.env=env;}
}
test('F003: host A only write, B only reconcile with distinct role names',()=>{
  const a=`postgresql://tsr3_host_a_rw:fake-not-production-secret@${goodHost}/ts_remote_r3?sslmode=verify-full`;
  const b=a.replace('tsr3_host_a_rw','tsr3_host_b_rw');
  withParams('HOST_A','write',a,()=>assert.equal(input().config.user,'tsr3_host_a_rw'));
  withParams('HOST_B','replay',b,()=>assert.equal(input().config.user,'tsr3_host_b_rw'));
  withParams('HOST_B','write',b,()=>assert.throws(input,e=>e.code==='PHASE_ROLE_VIOLATION'));
  withParams('HOST_A','replay',a,()=>assert.throws(input,e=>e.code==='PHASE_ROLE_VIOLATION'));
  withParams('HOST_B','replay',a,()=>assert.throws(input,e=>e.code==='INVALID_DB_PRINCIPAL'));
});
test('A001: fail closed for wrong host, incorrect TLS mode and bad enrollment',()=>{
  const base=`postgresql://tsr3_host_b_rw:fake-not-production-secret@${goodHost}/ts_remote_r3?sslmode=verify-full`;
  for(const url of [base.replace('sa-east-1','us-east-1'),base.replace('verify-full','require'),base+'&sslmode=verify-full']){
    withParams('HOST_B','read',url,()=>assert.throws(input));
  }
  withParams('HOST_B','read',base,()=>{
    process.env.TS_R3_ENROLLED_HOST_SHA256='f'.repeat(64);
    assert.throws(input,e=>e.code==='HOST_ENROLLMENT_MISMATCH');
  });
});
test('Safe client configuration never includes the database URL string',()=>{
  const url=`postgresql://tsr3_host_b_rw:fake-not-production-secret@${goodHost}/ts_remote_r3?sslmode=verify-full`;
  withParams('HOST_B','read',url,()=>{
    const c=input().config;
    assert.equal(c.ssl.rejectUnauthorized,true);
    assert.equal(c.ssl.servername,goodHost);
    assert.equal(Object.hasOwn(c,'connectionString'),false);
  });
});
