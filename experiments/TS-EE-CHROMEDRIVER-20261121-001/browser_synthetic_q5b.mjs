import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createServer} from 'node:http';
import {mkdtemp, mkdir, rm, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {performance} from 'node:perf_hooks';
import {createHash} from 'node:crypto';

const WIDTHS=new Set([320,375,768,1440]);
const width=Number(process.env.TS_EE_Q5B_WIDTH);
if(!WIDTHS.has(width))throw new Error('INVALID_Q4_WIDTH');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const elapsed=t=>Math.round(performance.now()-t);
const output=process.env.TS_EE_Q5B_OUTPUT_DIR||'q5b-evidence';
const events={home:0,product:0,deniedSku:0,notFound:0,serverError:0,scriptError:0};
const stage={identity:'PASS',server:'NOT_RUN',driver:'NOT_RUN',session:'NOT_RUN',browser:'NOT_RUN',cleanup:'NOT_RUN'};
const checks={width:'NOT_RUN',overflow:'NOT_RUN',semantic_heading:'NOT_RUN',button_label:'NOT_RUN',keyboard_tab:'NOT_RUN',keyboard_enter:'NOT_RUN',deep_link:'NOT_RUN',deep_link_refresh:'NOT_RUN',history_back:'NOT_RUN',sku_negative:'NOT_RUN',http_404:'NOT_RUN',http_500:'NOT_RUN',seeded_js_error:'NOT_RUN',screenshot:'NOT_RUN'};
const result={
  schema:'ts-ee/chromedriver-browser-q5b/v0',subject:'NONPRODUCT_SYNTHETIC',
  engine:'CHROMEDRIVER_NODE',requested_viewport_width:width,observed_viewport_width:null,
  network_mode:'OBSERVE_ONLY',os_egress_attested:false,product_accepted:false,
  provider_native_verified:false,attempt_kind:'ONE_REAL_SESSION',
  driver_ready_ms:null,session_create_ms:null,session_delete:'NOT_APPLICABLE',
  driver_termination:'NOT_RUN',descendant_termination:'NOT_ATTESTED',
  server_close:'NOT_RUN',profile_cleanup:'NOT_RUN',
  remote_session_state:'NOT_REQUESTED',stage,checks,
  screenshot:null,local_http_events:events,overall:'FAIL',error_class:'NONE'
};
const home=[
  '<!doctype html><html><head><meta charset="utf-8">',
  '<meta name="viewport" content="width=device-width, initial-scale=1">',
  '<title>TS EE Synthetic Browser Q4</title>',
  '<style>*{box-sizing:border-box}body{margin:0;font-family:sans-serif}main{max-width:100%;padding:12px}',
  'button,a{font-size:16px;margin:4px;padding:8px;display:inline-block}</style></head>',
  '<body><main tabindex="-1" id="start"><h1>Q5B Catalog</h1>',
  '<button id="focus-btn" onclick="document.body.dataset.clicked=\'yes\'">Use keyboard</button>',
  '<a id="product-link" href="/product/123">Product details</a>',
  '<p>Synthetic fixture only. No personal data.</p></main></body></html>'
].join('');
const product='<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head><body><main><h1>Q5B Product</h1><a href="/">Back to catalog</a></main></body></html>';
const scriptError='<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head><body><h1>Q5B Error Fixture</h1><script>window.__q5bErrorCaptured=false;window.addEventListener("error",function(){window.__q5bErrorCaptured=true});setTimeout(function(){throw new Error("SYNTHETIC_Q5B_JS_ERROR")},0)</script></body></html>';
let server=null,driver=null,driverExited=false,spawnFailed=false;
let driverEndedResolve;
const driverEnded=new Promise(r=>driverEndedResolve=r);
let sessionId=null;
let profile=null;
let tempDir=null;
let browserBase=null;
let screenshotData=null;
async function w3c(path,method='GET',body=null,timeout=5000) {
  const r=await fetch(browserBase+path,{
    method,headers:{'content-type':'application/json'},
    body:body===null?undefined:JSON.stringify(body),
    signal:AbortSignal.timeout(timeout)
  });
  let json=null;try{json=await r.json();}catch{}
  if(!r.ok||json?.value?.error||!json||!Object.hasOwn(json,'value'))throw new Error('WEBDRIVER_RESPONSE_NOT_OK');
  return json.value;
}
async function navigate(path) {
  await w3c('/session/'+encodeURIComponent(sessionId)+'/url','POST',
    {url:'http://127.0.0.1:'+server.address().port+path},7500);
}
async function execute(script) {
  return w3c('/session/'+encodeURIComponent(sessionId)+'/execute/sync','POST',{script,args:[]},5000);
}
async function key(value) {
  return w3c('/session/'+encodeURIComponent(sessionId)+'/actions','POST',{
    actions:[{type:'key',id:'kbd',actions:[{type:'keyDown',value},{type:'keyUp',value}]}]
  },5000);
}
async function waitReady() {
  const t=performance.now();
  while(elapsed(t)<6500) {
    if(driverExited)throw new Error('DRIVER_EXITED_EARLY');
    try { const v=await w3c('/status','GET',null,1100);if(v?.ready===true){result.driver_ready_ms=elapsed(t);return;} }
    catch { /* read-only bounded status observation; never retry POST/session */ }
    await sleep(100);
  }
  throw new Error('DRIVER_STATUS_TIMEOUT');
}
async function startServer() {
  server=createServer((req,res)=>{
    const path=String(req.url||'/').split('?')[0];
    res.setHeader('content-type','text/html; charset=utf-8');
    if(path==='/'){events.home++;res.end(home);}
    else if(path==='/product/123'){events.product++;res.end(product);}
    else if(path==='/product/denied'){events.deniedSku++;res.statusCode=404;res.end('<h1>Q5B SKU Denied</h1>');}
    else if(path==='/not-found'){events.notFound++;res.statusCode=404;res.end('<h1>Q4 not found</h1>');}
    else if(path==='/server-error'){events.serverError++;res.statusCode=500;res.end('<h1>Q4 server fault</h1>');}
    else if(path==='/script-error'){events.scriptError++;res.end(scriptError);}
    else {res.statusCode=404;res.end('<h1>Q4 unknown route</h1>');}
  });
  await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
  stage.server='PASS';
}
async function run() {
  tempDir=await mkdtemp(join(tmpdir(),'ts-ee-q5b-browser-'));
  profile=join(tempDir,'profile');
  await startServer();
  const portServer=createServer();
  await new Promise((resolve,reject)=>{portServer.once('error',reject);portServer.listen(0,'127.0.0.1',resolve);});
  const driverPort=portServer.address().port;
  await new Promise(resolve=>portServer.close(resolve));
  browserBase='http://127.0.0.1:'+driverPort;
  driver=spawn(process.env.CHROMEDRIVER_BIN||'chromedriver',
    ['--port='+driverPort,'--silent','--allowed-ips=127.0.0.1'],
    {detached:true,stdio:'ignore',shell:false});
  driver.once('exit',()=>{driverExited=true;driverEndedResolve();});
  driver.once('error',()=>{spawnFailed=true;driverExited=true;driverEndedResolve();});
  await waitReady();
  stage.driver='PASS';
  const t=performance.now();
  result.remote_session_state='UNKNOWN';
  let v=null;
  try {
    v=await w3c('/session','POST',{
      capabilities:{alwaysMatch:{
        browserName:'chrome',
        'goog:chromeOptions':{
          args:['--headless=new','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--no-first-run','--disable-background-networking','--user-data-dir='+profile],
          mobileEmulation:{deviceMetrics:{width,height:820,pixelRatio:1}}
        }
      }}
    },12000);
  } finally {result.session_create_ms=elapsed(t);}
  if(typeof v?.sessionId!=='string'||!v.sessionId)throw new Error('SESSION_CREATE_INVALID');
  sessionId=v.sessionId;
  result.remote_session_state='CREATED';
  stage.session='PASS';
  await navigate('/');
  let observed=await execute('return {width:window.innerWidth,scroll:document.documentElement.scrollWidth,title:document.querySelector("h1")?.textContent||"",href:document.getElementById("product-link")?.getAttribute("href")||""}');
  result.observed_viewport_width=observed.width;
  checks.width=observed.width===width?'PASS':'FAIL';
  checks.overflow=observed.scroll<=observed.width?'PASS':'FAIL';
  checks.semantic_heading=observed.title==='Q5B Catalog'&&observed.href==='/product/123'?'PASS':'FAIL';
  checks.button_label=(await execute('return document.getElementById("focus-btn")?.textContent?.trim()||""'))==='Use keyboard'?'PASS':'FAIL';

  await execute('document.getElementById("start").focus();return document.activeElement.id');
  await key('\uE004');
  const focused=await execute('return document.activeElement?.id||""');
  checks.keyboard_tab=focused==='focus-btn'?'PASS':'FAIL';
  await key('\uE007');
  const clicked=await execute('return document.body.dataset.clicked||""');
  checks.keyboard_enter=clicked==='yes'?'PASS':'FAIL';

  await navigate('/product/123');
  const deep=await execute('return {path:location.pathname,title:document.querySelector("h1")?.textContent||""}');
  checks.deep_link=deep.path==='/product/123'&&deep.title==='Q5B Product'?'PASS':'FAIL';
  await w3c('/session/'+encodeURIComponent(sessionId)+'/refresh','POST',{},5000);
  const afterRefresh=await execute('return {path:location.pathname,title:document.querySelector("h1")?.textContent||""}');
  checks.deep_link_refresh=afterRefresh.path==='/product/123'&&afterRefresh.title==='Q5B Product'?'PASS':'FAIL';
  await w3c('/session/'+encodeURIComponent(sessionId)+'/back','POST',{},5000);
  checks.history_back=(await execute('return location.pathname'))==='/'?'PASS':'FAIL';
  await navigate('/product/denied');
  const denied=await execute('return document.querySelector("h1")?.textContent||""');
  checks.sku_negative=events.deniedSku===1&&denied==='Q5B SKU Denied'?'PASS':'FAIL';

  await navigate('/not-found');
  checks.http_404=events.notFound===1?'PASS':'FAIL';
  await navigate('/server-error');
  checks.http_500=events.serverError===1?'PASS':'FAIL';

  await navigate('/script-error');
  await sleep(250);
  checks.seeded_js_error=(await execute('return window.__q5bErrorCaptured===true'))===true?'PASS':'FAIL';

  await navigate('/');
  const image=await w3c('/session/'+encodeURIComponent(sessionId)+'/screenshot','GET',null,7000);
  if(typeof image!=='string'||image.length>4*1024*1024)throw new Error('SCREENSHOT_INVALID_SIZE');
  const png=Buffer.from(image,'base64');
  if(png.length<100||png.length>2*1024*1024||png.subarray(0,8).toString('hex')!=='89504e470d0a1a0a')throw new Error('SCREENSHOT_INVALID_PNG');
  screenshotData=png;
  result.screenshot={filename:'q5b-'+width+'.png',bytes:png.length,sha256:createHash('sha256').update(png).digest('hex'),width};
  checks.screenshot='PASS';
  stage.browser=Object.values(checks).every(x=>x==='PASS')?'PASS':'FAIL';
  if(stage.browser!=='PASS')throw new Error('SYNTHETIC_BROWSER_CHECK_FAILED');
}
async function close() {
  if(sessionId!==null) {
    try {
      await w3c('/session/'+encodeURIComponent(sessionId),'DELETE',null,3000);
      result.session_delete='ACK';result.remote_session_state='DELETED_CONFIRMED';
    } catch {result.session_delete='FAIL';result.remote_session_state='UNKNOWN';}
  }
  if(driver) {
    if(!driverExited&&driver.pid){
      try {process.kill(-driver.pid,'SIGTERM');}catch{}
      await Promise.race([driverEnded,sleep(2500)]);
    }
    if(!driverExited&&driver.pid){
      try {process.kill(-driver.pid,'SIGKILL');}catch{}
      await Promise.race([driverEnded,sleep(2500)]);
    }
    result.driver_termination=spawnFailed?'NO_CHILD_SPAWNED':driverExited?'DIRECT_PROCESS_EXIT_OBSERVED':'UNVERIFIED';
  }
  if(server) {
    try {server.closeAllConnections();await new Promise(resolve=>server.close(resolve));result.server_close='CLOSED';}
    catch {result.server_close='FAIL';}
  }
  if(tempDir) {
    if(result.driver_termination==='DIRECT_PROCESS_EXIT_OBSERVED'||result.driver_termination==='NO_CHILD_SPAWNED') {
      try {await rm(tempDir,{recursive:true,force:true,maxRetries:0});result.profile_cleanup='PASS';}
      catch {result.profile_cleanup='FAIL';}
    } else result.profile_cleanup='UNVERIFIED';
  }
  stage.cleanup=(result.session_delete==='ACK'&&result.driver_termination==='DIRECT_PROCESS_EXIT_OBSERVED'&&result.server_close==='CLOSED'&&result.profile_cleanup==='PASS')?'PASS':'FAIL';
}
try{await run();}
catch(e){result.error_class=String(e?.name==='TimeoutError'?'TIMEOUT':e?.message||'RUNNER_FAILURE').replace(/[^A-Z_]/g,'').slice(0,48)||'RUNNER_FAILURE';if(stage.browser==='NOT_RUN')stage.browser='NOT_RUN';}
finally{await close();}
result.overall=(stage.identity==='PASS'&&stage.server==='PASS'&&stage.driver==='PASS'&&stage.session==='PASS'&&stage.browser==='PASS'&&stage.cleanup==='PASS'&&result.error_class==='NONE')?'PASS_BOUNDED_Q5B_BROWSER':'FAIL';
if(result.overall==='FAIL'&&result.error_class==='NONE')result.error_class='INCOMPLETE_Q5B';
await mkdir(output,{recursive:true});
if(screenshotData&&result.overall==='PASS_BOUNDED_Q5B_BROWSER')await writeFile(join(output,'q5b-'+width+'.png'),screenshotData,{flag:'wx'});
await writeFile(join(output,'Q5B_REPORT.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));
if(result.overall!=='PASS_BOUNDED_Q5B_BROWSER')process.exitCode=1;
