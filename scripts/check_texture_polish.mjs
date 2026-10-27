import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {spawnSync,execFileSync} from 'node:child_process';
process.env.REFINEMENT_RUN=path.resolve('.runs/2026-10-27-texture-smoothness');
const {launch,until,shot,save,base,out,views,root,run}=await import('./refinement_browser.mjs');
const group=process.argv[2],report={group,date:new Date().toISOString(),checks:[],pass:false};let browser;
const check=(name,ok,detail)=>{report.checks.push({name,pass:!!ok,detail});assert.ok(ok,name+': '+JSON.stringify(detail));};
const median=a=>a.slice().sort((a,b)=>a-b)[Math.floor(a.length/2)];
async function go(p,i){await p.locator(`[data-go-chapter="${i}"]`).click();await until(p,i=>Math.abs(scrollY-document.querySelector(`[data-chapter="${i}"]`).offsetTop)<1,i);await p.waitForTimeout(500);}
async function child(name){const r=spawnSync(process.execPath,[path.join(root,'scripts/check_homepage_refinement.mjs'),name],{encoding:'utf8',env:process.env,timeout:400000});await fs.writeFile(path.join(out,`command-${name}.txt`),r.stdout+r.stderr);const d=JSON.parse(await fs.readFile(path.join(out,name+'.json'),'utf8'));check(name,r.status===0&&d.pass,d.failure);}
try{
 await fs.mkdir(out,{recursive:true});
 if(group==='before'){
  browser=await launch();for(const v of [views[0],views[3]]){const p=await browser.newPage({viewport:v});await p.goto(base);await until(p,()=>window.__experience);for(const [i,n] of [[0,'hero'],[3,'gallery'],[4,'packages'],[5,'close']]){await go(p,i);await shot(p,'before',`${v.width}-${n}.png`);}await p.goto(base+'/packages');await shot(p,'before',`${v.width}-public.png`);await p.close();}
 }
 else if(group==='benchmark'){
  browser=await launch();report.conditions={browser:'installed Chrome headless',cpuThrottle:4,latencyMs:20,downloadBytesPerSecond:1250000,cache:'disabled',source:'unchanged 24 fps derivatives',method:'same page and media; intercept only video-clock for baseline; 3 cold runs per viewport/clock, alternating order; deterministic 3s forward + 3s reverse native scroll; presented-frame callbacks'};report.runs=[];
  const baseline=execFileSync('git',['show','36c89e51c09f9d9c72f71887fd37858b0c1ee356:app/static/experience/js/video-clock.js'],{encoding:'utf8'})+'\nexport const createCueCurve=points=>x=>interpolate(points,x);';
  for(const v of [views[0],views[3]])for(let n=0;n<3;n++)for(const phase of n%2?['after','before']:['before','after']){
   const c=await browser.newContext({viewport:v}),p=await c.newPage(),errors=[];
   if(phase==='before')await p.route('**/video-clock.js*',r=>r.fulfill({body:baseline,contentType:'text/javascript'}));
   p.on('pageerror',e=>errors.push(e.message));const cdp=await c.newCDPSession(p);
   await cdp.send('Network.enable');await cdp.send('Network.setCacheDisabled',{cacheDisabled:true});await cdp.send('Network.emulateNetworkConditions',{offline:false,latency:20,downloadThroughput:1250000,uploadThroughput:1250000});await cdp.send('Emulation.setCPUThrottlingRate',{rate:4});
   await p.goto(base,{waitUntil:'domcontentloaded'});await until(p,()=>window.__experience&&document.querySelector('#journey-video').readyState>=2);const readiness=await p.evaluate(()=>({ms:performance.now(),hero:document.querySelector('#summit-title').getBoundingClientRect().bottom<innerHeight,video:window.__experience.video}));
   await until(p,()=>{const v=document.querySelector('#journey-video');return v.buffered.length&&v.buffered.end(v.buffered.length-1)>v.duration-.1;});
   const trace=await p.evaluate(async()=>{
    const v=document.querySelector('#journey-video'),range=window.__experience.journeyRange,frames=[],seeks=[];let cb;
    const frame=(now,meta)=>{frames.push({at:now,time:meta.mediaTime});cb=v.requestVideoFrameCallback(frame);};cb=v.requestVideoFrameCallback(frame);
    let seekStart=0;const seeking=()=>{seekStart=performance.now();};const seeked=()=>seeks.push(performance.now()-seekStart);v.addEventListener('seeking',seeking);v.addEventListener('seeked',seeked);
    const start=performance.now();await new Promise(resolve=>{const step=now=>{const t=(now-start)/3000;scrollTo({top:range*Math.max(0,t<=1?t:2-t),behavior:'instant'});if(t<2)requestAnimationFrame(step);else resolve();};requestAnimationFrame(step);});
    const stop=performance.now();await new Promise(resolve=>{const poll=()=>{if(!v.seeking&&v.currentTime<.06)resolve();else requestAnimationFrame(poll);};poll();});const settled=performance.now();const held=v.currentTime;await new Promise(r=>setTimeout(r,300));
    v.cancelVideoFrameCallback(cb);v.removeEventListener('seeking',seeking);v.removeEventListener('seeked',seeked);
    return {frames,seeks,settleMs:settled-stop,held:held===v.currentTime,state:window.__experience.video,mediaBytes:performance.getEntriesByType('resource').filter(r=>r.name.includes('.mp4')).reduce((s,r)=>s+r.transferSize,0)};
   });
   const item={width:v.width,phase,n,readiness,uniqueFrames:trace.frames.filter((f,i,a)=>!i||f.time!==a[i-1].time).length,seekMedianMs:median(trace.seeks),seekP95Ms:trace.seeks.slice().sort((a,b)=>a-b)[Math.floor(trace.seeks.length*.95)],issued:trace.state.issued,settleMs:trace.settleMs,mediaBytes:trace.mediaBytes,held:trace.held,maxPending:trace.state.maxPending,errors};report.runs.push(item);await save(`trace-${v.width}-${phase}-${n}.json`,trace);check('bounded held error-free '+v.width+phase+n,trace.held&&trace.state.maxPending<=1&&!errors.length,item);await c.close();console.log(JSON.stringify(item));
  }
  report.medians=[];for(const v of [views[0],views[3]])for(const phase of ['before','after']){const a=report.runs.filter(x=>x.width===v.width&&x.phase===phase),m={width:v.width,phase};for(const k of ['uniqueFrames','seekMedianMs','seekP95Ms','issued','settleMs','mediaBytes'])m[k]=median(a.map(x=>x[k]));m.readyMs=median(a.map(x=>x.readiness.ms));report.medians.push(m);}
 }
 else if(group==='visual'){
  browser=await launch();for(const v of views){const c=await browser.newContext({viewport:v}),p=await c.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='error')errors.push(m.text());});await p.goto(base);await until(p,()=>window.__experience);
   for(const [i,n] of [[0,'hero'],[2,'town'],[3,'gallery'],[4,'packages'],[5,'close']]){await go(p,i);check(`${v.width} ${n} overflow`,await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await shot(p,'after',`${v.width}-${n}.png`);}
   check('texture applied '+v.width,await p.locator('.flow-sessions').evaluate(e=>getComputedStyle(e,'::before').backgroundImage.includes('alpine-grain')));check('no texture over film',await p.locator('.flow-stage').evaluate(e=>getComputedStyle(e,'::before').content==='none'));await go(p,3);await p.locator('#play-selected-film').click();await until(p,()=>document.querySelector('#film-player video')?.currentTime>.1);await p.keyboard.press('Escape');check('no relevant errors '+v.width,!errors.length,errors);
   for(const route of ['/packages','/gallery','/testimonials','/about','/faq','/contact']){const r=await p.goto(base+route);check(route+' 200',r.status()===200);check(route+' textured',await p.locator('.ap-intro').first().evaluate(e=>getComputedStyle(e,'::before').backgroundImage.includes('bansko-contours')));await shot(p,'public',`${v.width}-${route.slice(1)}.png`);}await c.close();
  }await browser.close();browser=null;await child('hero');await child('journey');await child('accessibility');
 }
 else if(group==='publicshots'){
  browser=await launch();for(const v of views){const p=await browser.newPage({viewport:v});for(const route of ['/packages','/gallery','/testimonials','/about','/faq','/contact']){const r=await p.goto(base+route);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(1100);check(route+' settled '+v.width,r.status()===200&&await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await shot(p,'public-settled',`${v.width}-${route.slice(1)}.png`);}await p.close();}
 }
 else if(group==='regressions'){
  const r=spawnSync(path.join(root,'.venv/Scripts/python.exe'),['-m','pytest','-q','tests'],{encoding:'utf8',timeout:180000});await fs.writeFile(path.join(out,'pytest.txt'),r.stdout+r.stderr);const failed=[...r.stdout.matchAll(/^FAILED (\S+)/gm)].map(m=>m[1]).sort(),known=['tests/test_models.py::TestPackageModel::test_create_package','tests/test_routes.py::TestAuthRoutes::test_register_page','tests/test_routes.py::TestBookingRoutes::test_booking_index','tests/test_routes.py::TestBookingRoutes::test_new_booking_requires_auth'].sort();check('same four known failures',r.status===1&&JSON.stringify(failed)===JSON.stringify(known),{failed,summary:r.stdout.split('\n').slice(-3)});await child('gallery');
  browser=await launch();const p=await browser.newPage();await p.goto(base);await until(p,()=>window.__experience);await go(p,4);const links=await p.locator('.flow-package a').evaluateAll(a=>a.map(x=>x.href));check('three package choices',links.length===3);for(const href of links)check('package detail '+href,(await p.request.get(href)).status()===200);
  await p.locator('.flow-package a').first().click();check('booking action preserved',await p.locator('.detail-aside a[href*="booking"],.detail-aside a[href*="checkout"],.detail-aside a[href^="/contact?subject="]').count()>0);
  for(const route of ['/packages','/gallery','/testimonials','/about','/faq','/contact','/auth/login'])check(route+' 200',(await p.request.get(base+route)).status()===200);
  for(const name of ['alpine-grain.png','bansko-contours.webp']){const r=await p.request.get(base+'/static/experience/textures/'+name+'?v=bansko-texture-1');check(name+' immutable local delivery',r.status()===200&&r.headers()['cache-control'].includes('immutable'),{status:r.status(),cache:r.headers()['cache-control'],bytes:(await r.body()).length});}
  await p.goto('http://127.0.0.1:5002/');await until(p,()=>window.__experience);await go(p,3);check('empty DB honest five concept moments',await p.locator('[data-film]').count()===5);await go(p,4);check('empty DB enquiry states',await p.getByRole('heading',{name:'Package coming soon'}).count()===3);
 }
 else if(group==='review'){
  const config=JSON.parse(await fs.readFile(path.join(run,'review-contract.json'),'utf8'));
  let status=null;try{status=JSON.parse(await fs.readFile(path.join(config.runDir,'latest.json'),'utf8'));}catch{}
  const {candidateFingerprint}=await import('file:///C:/Users/Dan/Documents/ChatGPT/maestro/src/review-loop.mjs');
  report.candidate=await candidateFingerprint(root,run);report.status=status;
  report.previousController=JSON.parse(await fs.readFile('C:/Users/Dan/Documents/ChatGPT/maestro/.runs/2026-10-26-homepage-refinement-loop/evidence/live/latest.json','utf8'));
  report.sessions=JSON.parse(await fs.readFile(path.join(out,'controller-sessions.json'),'utf8'));
  check('external candidate review available',!!status?.verdict&&status.candidate===report.candidate&&path.resolve(status.ledgerDir)===run,{status,required:'External controller assessment of this candidate; no substitute or self verdict.'});
 }
 else if(group==='delivery'){
  for(const url of ['https://white-rabbit-git-bansko-experience-devman-1a64abec.vercel.app/','https://white-rabbit-zeta.vercel.app/']){const r=await fetch(url,{redirect:'manual'}),s=await r.text();report.checks.push({name:url,pass:r.status===200&&s.includes('bansko-texture-1'),status:r.status,version:s.match(/data-version="([^"]+)"/)?.[1]});}check('preview and public revision',report.checks.every(x=>x.pass));
 }else throw Error('Unknown group '+group);
 report.pass=true;
}catch(e){report.failure=e.stack;process.exitCode=1;}finally{await browser?.close();await save(group+'.json',report);console.log(JSON.stringify(report,null,2));}

