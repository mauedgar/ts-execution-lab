#!/usr/bin/env python3
"""Isolated TS EE synthetic Browser QA: no Product, credentials, or external requests."""
import argparse,hashlib,json,os,sys,threading,time
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from importlib.metadata import version
from playwright.sync_api import sync_playwright

WIDTHS=(320,375,768,1440)
SEEDS={'OVERFLOW','LABEL','HIDDEN_SKU','CONSOLE','HTTP'}
HTML='''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>E2 QA fixture</title>
<style>
*{box-sizing:border-box}body{margin:0;font:16px system-ui;background:#f5f7ff;color:#142040}
.shell{max-width:1000px;padding:20px;margin:auto}body.bad .shell{min-width:900px}
nav{display:flex;gap:16px;margin:0 0 18px}main{padding:18px;background:white;border:1px solid #ccd;border-radius:10px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:12px}
article{padding:14px;border:1px solid #ccc;border-radius:8px}
input{display:block;margin:6px 0 16px;padding:8px;max-width:100%}
@media(max-width:420px){.shell{padding:8px}}
</style></head><body class="VARIANT"><div class="shell">
<nav aria-label="Main"><a data-local href="/catalog?variant=VARIANT">Catalog</a>
<a data-local href="/about?variant=VARIANT">About</a></nav><main id="app"></main></div>
<script>
(function(){const bad=document.body.classList.contains('bad');
const items=[{sku:'PUBLIC-1',label:'Bottle 1 L',public:true},
{sku:'HIDDEN-9',label:'Confidential prototype',public:false}];
const app=document.getElementById('app');
function uri(path,sku){let u=new URL(path,location.origin);u.searchParams.set('variant',bad?'bad':'good');if(sku)u.searchParams.set('sku',sku);return u.pathname+u.search}
function draw(){const u=new URL(location.href);
if(u.pathname==='/about'){app.innerHTML='<h1>About</h1>';return}
if(u.pathname==='/product'){let p=items.find(x=>x.sku===u.searchParams.get('sku'));
if(!p||(!bad&&!p.public)){app.innerHTML='<h1>Not available</h1>';return}
app.innerHTML='<h1>'+p.label+'</h1><a data-local href="'+uri('/catalog')+'">Catalog</a>';return}
let allowed=items.filter(x=>bad||x.public);
app.innerHTML='<h1>Catalog</h1>'+(bad?'':'<label for="search">Search catalog</label>')
+'<input id="search" type="search" placeholder="Search">'
+'<section class="grid">'+allowed.map(x=>'<article><h2>'+x.label+'</h2><a data-local href="'+uri('/product',x.sku)+'">View '+x.sku+'</a></article>').join('')+'</section>'
+'<a id="contact" target="_blank" rel="noopener noreferrer">Contact via WhatsApp</a>';
let wa=new URL('https://wa.me/5493512345678');wa.searchParams.set('text','PUBLIC-1 & blue');
document.getElementById('contact').href=wa.toString()}
document.addEventListener('keydown',e=>{
  if(e.key==='Enter' && new URL(location.href).searchParams.get('keyboard')==='disabled'
     && e.target.closest('a[data-local]'))e.preventDefault();
},true);
document.addEventListener('click',e=>{const a=e.target.closest('a[data-local]');
if(!a)return;e.preventDefault();history.pushState({},'',a.href);draw()});
window.addEventListener('popstate',draw);draw();
if(bad){console.error('SEEDED_CONSOLE_FAILURE');fetch('/api/missing').catch(()=>{})}
})();
</script></body></html>'''

class Server(BaseHTTPRequestHandler):
 def do_GET(self):
  u=urlsplit(self.path)
  if u.path=='/api/missing':code,body,ct=404,b'not found','text/plain'
  elif u.path in ('/','/catalog','/about','/product'):
   v=parse_qs(u.query).get('variant',['good'])[0]
   if v not in ('good','bad'):v='good'
   code,body,ct=200,HTML.replace('VARIANT',v).encode(),'text/html; charset=utf-8'
  else:code,body,ct=404,b'not found','text/plain'
  self.send_response(code);self.send_header('Content-Type',ct)
  self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def log_message(self,*args):pass
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def execute(dest):
 dest=Path(dest)
 if dest.exists():raise RuntimeError('BLOCKED_EXISTING_RESULT_PATH')
 dest.mkdir(parents=True)
 srv=ThreadingHTTPServer(('127.0.0.1',0),Server)
 th=threading.Thread(target=srv.serve_forever,daemon=True);th.start()
 base='http://127.0.0.1:'+str(srv.server_port)
 start=time.monotonic()
 result={'schema':'ts-ee-e2-browser-qa/v1','source_sha256':sha(__file__),
 'widths':list(WIDTHS),'a11y_scope':'BASIC_LABEL_ROLE_ONLY_NOT_WCAG',
 'network_scope':'LOCAL_ONLY_AND_EXTERNAL_ABORT','service_workers':'BLOCKED',
  'additional_checks':['DEEP_LINK_REFRESH','KEYBOARD_TAB_ENTER'],
  'seeded_negative_checks':['OVERFLOW','LABEL','HIDDEN_SKU','CONSOLE','HTTP'],
  'positive_only_checks':['ROUTE_HISTORY','DEEP_REFRESH','KEYBOARD_ACTIVATION','WA_URL_ENCODING','EXTERNAL_ROUTE_ABORT'],
  'network_observation_scope':'BROWSER_CONTEXT_OBSERVED_REQUESTS_ONLY_NOT_OS_ATTESTED',
  'screenshot_scope':'INITIAL_CATALOG_BEFORE_KEYBOARD_HISTORY_AND_REFRESH',
  'variants':{},'artifacts':[]}
 try:
  with sync_playwright() as p:
   kw={'headless':True}
   if os.getenv('E2_CHROMIUM_PATH'):kw['executable_path']=os.environ['E2_CHROMIUM_PATH']
   browser=p.chromium.launch(**kw)
   result['runtime']={'python':sys.version.split()[0],'playwright':version('playwright'),'chromium':browser.version}
   try:
    for kind in ('good','bad'):
     found=set();rows=[];blocked_count=0
     for width in WIDTHS:
      context=browser.new_context(viewport={'width':width,'height':800},device_scale_factor=1,service_workers='block')
      context.set_default_timeout(7000)
      context.tracing.start(screenshots=True,snapshots=True,sources=True)
      console=[];http=[];blocked=[]
      def guard(route):
       if route.request.url.startswith(base+'/'):route.continue_()
       else:blocked.append(route.request.url);route.abort()
      context.route('**/*',guard)
      page=context.new_page()
      page.on('console',lambda m:console.append(m.text) if m.type=='error' else None)
      page.on('pageerror',lambda e:console.append(str(e)))
      page.on('response',lambda r:http.append(r.status) if r.status>=400 else None)
      if kind=='bad':
       with page.expect_response(lambda response:response.status==404 and '/api/missing' in response.url,timeout=5000) as response_info:
        page.goto(base+'/catalog?variant='+kind,wait_until='load')
       bad_http_response=response_info.value
       if bad_http_response.status!=404:found.add('HTTP_RESPONSE_MISMATCH')
       if 404 not in http:http.append(404)
      else:
       page.goto(base+'/catalog?variant='+kind,wait_until='load')
      page.get_by_role('heading',name='Catalog',exact=True).wait_for()
      geom=page.evaluate('({viewport:innerWidth,scroll:document.documentElement.scrollWidth})')
      if geom['scroll']>geom['viewport']+1:found.add('OVERFLOW')
      label_ok=page.get_by_role('searchbox',name='Search catalog').count()==1
      if not label_ok:found.add('LABEL')
      pic=dest/(kind+'-'+str(width)+'.png');page.screenshot(path=str(pic),full_page=True)
      result['artifacts'].append({'file':pic.name,'bytes':pic.stat().st_size,'sha256':sha(pic)})
      page.goto(base+'/about?variant='+kind,wait_until='load')
      page.get_by_role('heading',name='About',exact=True).wait_for()
      page.keyboard.press('Tab')
      first_tab=page.evaluate("document.activeElement?.textContent?.trim()")
      keyboard_activated=False
      if first_tab!='Catalog':found.add('KEYBOARD_FOCUS')
      else:
       page.keyboard.press('Enter')
       page.wait_for_url('**/catalog?variant='+kind,timeout=5000)
       keyboard_activated=(page.get_by_role('heading',name='Catalog',exact=True).count()==1
                           and page.url==base+'/catalog?variant='+kind)
       if not keyboard_activated:found.add('KEYBOARD_ACTIVATION')
      page.goto(base+'/about?variant='+kind+'&keyboard=disabled',wait_until='load')
      page.keyboard.press('Tab')
      page.keyboard.press('Enter')
      keyboard_negative_rejected=page.url.startswith(base+'/about?')
      if not keyboard_negative_rejected:found.add('KEYBOARD_NEGATIVE_MISSED')
      page.goto(base+'/catalog?variant='+kind,wait_until='load')
      page.get_by_role('link',name='View PUBLIC-1').click()
      detail=page.get_by_role('heading',name='Bottle 1 L').count()==1
      page.go_back(wait_until='domcontentloaded')
      back=page.get_by_role('heading',name='Catalog',exact=True).count()==1
      page.go_forward(wait_until='domcontentloaded')
      forward=page.get_by_role('heading',name='Bottle 1 L').count()==1
      if not(detail and back and forward):found.add('ROUTE_HISTORY')
      page.goto(base+'/product?variant='+kind+'&sku=PUBLIC-1',wait_until='load')
      page.reload(wait_until='load')
      deep_refresh=page.get_by_role('heading',name='Bottle 1 L').count()==1
      if not deep_refresh:found.add('DEEP_REFRESH')
      page.goto(base+'/product?variant='+kind+'&sku=HIDDEN-9',wait_until='load')
      hidden=page.get_by_role('heading',name='Not available').count()==1
      if not hidden:found.add('HIDDEN_SKU')
      page.goto(base+'/catalog?variant='+kind,wait_until='load')
      link=page.get_by_role('link',name='Contact via WhatsApp')
      href=link.get_attribute('href') or ''
      if urlsplit(href).netloc!='wa.me' or parse_qs(urlsplit(href).query).get('text')!=['PUBLIC-1 & blue']:found.add('WA_URL_ENCODING')
      external=context.new_page()
      before_blocked=len(blocked)
      navigation_succeeded=False
      error_text=''
      try:
       response=external.goto(href,wait_until='commit',timeout=2000)
       navigation_succeeded=response is not None
      except Exception as err:
       error_text=str(err)
      external.close()
      new_blocked=blocked[before_blocked:]
      aborted_expected=(href in new_blocked and 'ERR_FAILED' in error_text
                        and not navigation_succeeded)
      if not aborted_expected:found.add('EXTERNAL_NOT_BLOCKED')
      blocked_count+=len(new_blocked)
      if console:found.add('CONSOLE')
      if http:found.add('HTTP')
      rows.append({'width':width,'overflow_px':max(0,geom['scroll']-geom['viewport']),
       'label':label_ok,
       'detail':detail,'back':back,'forward':forward,'deep_refresh':deep_refresh,
       'first_tab':first_tab,'keyboard_activated':keyboard_activated,
       'keyboard_negative_rejected':keyboard_negative_rejected,
       'external_navigation_rejected':aborted_expected,'hidden_rejected':hidden,
       'console_errors':len(console),'http_errors':len(http),'blocked_external':len(blocked)})
      trace=dest/(kind+'-'+str(width)+'.zip');context.tracing.stop(path=str(trace))
      result['artifacts'].append({'file':trace.name,'bytes':trace.stat().st_size,'sha256':sha(trace)})
      context.close()
     expected=set() if kind=='good' else SEEDS
     result['variants'][kind]={'detected':sorted(found),'expected':sorted(expected),
      'pass':found==expected,'rows':rows,'blocked_external_requests':blocked_count}
   finally:browser.close()
 finally:srv.shutdown();srv.server_close();th.join(timeout=2)
 result['duration_seconds']=round(time.monotonic()-start,3)
 result['pass']=all(v['pass'] for v in result['variants'].values())
 (dest/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
 print('E2_TERMINAL='+json.dumps({'pass':result['pass'],'detected':{k:v['detected'] for k,v in result['variants'].items()},'seconds':result['duration_seconds'],'source_sha256':result['source_sha256']}))
 return 0 if result['pass'] else 1
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',required=True)
 sys.exit(execute(a.parse_args().output))
