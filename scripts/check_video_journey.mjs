/** Rerunnable real-browser acceptance; no application build or dependencies added. */
import fs from 'node:fs/promises';
import {existsSync,readdirSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'.runs/2026-10-26-video-journey/evidence');
await fs.mkdir(path.join(out,'shots'),{recursive:true});
const group=process.argv[process.argv.indexOf('--group')+1]||'seeking';
const base=process.env.JOURNEY_BASE||(group==='public'?'https://white-rabbit-zeta.vercel.app':'http://127.0.0.1:5000');
if(group==='public')assert.ok(new URL(base).hostname!=='127.0.0.1'&&new URL(base).hostname!=='localhost','Public check requires a remote deployment');
let pw;try{pw=await import('playwright');}catch{
 const cache=path.join(process.env.LOCALAPPDATA,'npm-cache/_npx');
 pw=await import(pathToFileURL(readdirSync(cache).map(x=>path.join(cache,x,'node_modules/playwright/index.mjs')).find(existsSync)));
}
const browser=await pw.chromium.launch({channel:'chrome',headless:true,args:['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist',...(process.env.NO_WEBGL?['--disable-webgl']:[])]});
const report={group,base,browser:'Installed Google Chrome (H.264 decoding); isolated headless context',date:new Date().toISOString(),views:[],errors:[],failed:[],expectedFailures:[],pass:false};
const views=[{width:1440,height:900},{width:375,height:812}];
async function open(viewport,options={},address=base){
 const context=await browser.newContext({viewport,...options});const page=await context.newPage();
 page.on('pageerror',e=>report.errors.push(e.message));
 page.on('console',m=>{if(m.type()==='error'){
  if(page.expectedMediaFailure&&m.text()==='Failed to load resource: net::ERR_FAILED')report.expectedFailures.push({console:m.text(),reason:'Deliberate media failure test'});
  else report.errors.push(m.text());
 }});
 page.on('requestfailed',r=>{const detail={url:r.url(),error:r.failure()?.errorText};
  if((r.url().includes('.mp4')&&r.failure()?.errorText==='net::ERR_ABORTED')||page.expectedMediaFailure&&r.url().includes('.mp4'))report.expectedFailures.push(detail);else report.failed.push(detail);
 });
 page.on('response',r=>{if(r.status()>=400)report.failed.push({url:r.url(),status:r.status()});});
 await context.addInitScript(()=>{window.__csp=[];document.addEventListener('securitypolicyviolation',e=>window.__csp.push({directive:e.violatedDirective,uri:e.blockedURI}));});
 return {context,page,address};
}
// Playwright 1.48 waitForFunction uses eval under Chrome's current CSP handling.
// CDP evaluate + polling preserves the production policy without unsafe-eval.
async function until(page,fn,arg){for(let i=0;i<300;i++){try{if(await page.evaluate(fn,arg))return;}catch(e){if(!e.message.includes('Execution context was destroyed'))throw e;}await page.waitForTimeout(70);}throw Error('Browser condition timed out: '+fn.toString());}
async function load(page,address=base){await page.goto(address,{waitUntil:'domcontentloaded'});await until(page,()=>window.__experience&&document.getElementById('exp-loader').hidden);}
async function ready(page){await until(page,()=>window.__experience?.video?.ready);}
async function at(page,p){
 await page.evaluate(p=>{const t=document.getElementById('exp-track');scrollTo({top:t.offsetTop+(t.offsetHeight-innerHeight)*p,behavior:'instant'});},p);
 await until(page,p=>{const s=window.__experience;return Math.abs(s.progress-p)<.001&&s.video?.ready&&!s.video.seeking&&Math.abs(s.video.current-s.video.desired)<.019;},p);
 await page.waitForTimeout(90);return page.evaluate(()=>window.__experience);
}
async function shot(page,name){await page.screenshot({path:path.join(out,'shots',name)});}
try{
 if(group==='seeking'||group==='public'){
  for(const viewport of views){
   const {context,page}=await open(viewport);const requested=[];page.on('request',r=>requested.push(r.url()));
   await load(page);
   assert.equal(await page.evaluate(()=>JSON.parse(document.getElementById('experience-data').textContent).journey?.mode),'video','Target deployment must serve the video integration');
   await ready(page);assert.equal((await page.evaluate(()=>window.__experience)).mode,'video');
   const start=await at(page,0);assert.ok(start.video.current<.02);assert.ok(start.video.duration>9&&start.video.duration<9.1);
   const view={viewport,start,chapters:[],slow:[],jumps:[]};
   for(const [i,p] of [.06,.21,.42,.65,.82,.95].entries()){
    const state=await at(page,p);await page.waitForTimeout(500);
    assert.equal(state.chapter,i);assert.equal(state.video.paused,true);assert.ok(state.video.maxPending<=1);
    assert.equal(await page.locator(`[data-chapter="${i}"]`).evaluate(e=>e.inert),false);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    const file=`${group}-${viewport.width}x${viewport.height}-ch${i+1}.png`;await shot(page,file);
    view.chapters.push({p,state,file});
   }
   for(let i=0;i<=30;i++){const s=await at(page,.12+i*.005);view.slow.push({p:s.progress,t:s.video.current});}
   for(let i=29;i>=0;i--){const s=await at(page,.12+i*.005);assert.ok(Math.abs(s.video.current-view.slow[i].t)<.019);}
   await at(page,.95);const reverse=await at(page,.42);await shot(page,`${group}-${viewport.width}x${viewport.height}-reverse.png`);view.reverse=reverse;
   for(const p of [.99,.02,.8,.31,.95,.21]){
    const before=Date.now();const s=await at(page,p);view.jumps.push({p,time:s.video.current,settleMs:Date.now()-before});assert.ok(s.video.maxPending<=1);
   }
   await page.evaluate(async()=>{for(let i=0;i<50;i++){const t=document.getElementById('exp-track');scrollTo({top:t.offsetTop+(t.offsetHeight-innerHeight)*(i%2?.92:.03),behavior:'instant'});await new Promise(r=>requestAnimationFrame(r));}});
   view.burst=await at(page,.95);assert.ok(view.burst.video.maxPending<=1);
   const held=await page.evaluate(()=>({time:document.getElementById('journey-video').currentTime,issued:window.__experience.video.issued}));
   const pixels=()=>{const v=document.getElementById('journey-video'),c=document.createElement('canvas');c.width=160;c.height=90;const x=c.getContext('2d');x.drawImage(v,0,0,160,90);return c.toDataURL();};
   const heldPixels=await page.evaluate(pixels);
   await page.waitForTimeout(1000);const heldAfter=await page.evaluate(()=>({time:document.getElementById('journey-video').currentTime,issued:window.__experience.video.issued}));
   assert.deepEqual(heldAfter,held);assert.equal(await page.evaluate(pixels),heldPixels);view.held={before:held,after:heldAfter,decodedPixelsStable:true};
   for(const p of [.88,.93,.99]){const s=await at(page,p);assert.ok(Math.abs(s.video.current-(s.video.duration-.06))<.019);}
   for(const i of [0,5,2,3,1,4]){
    await page.locator(`[data-go-chapter="${i}"]`).click();await until(page,i=>window.__experience.chapter===i,i);await page.waitForTimeout(1500);
    const s=await page.evaluate(()=>window.__experience);assert.equal(s.chapter,i);assert.ok(Math.abs(s.video.current-s.video.desired)<.019);
   }
   const forbidden=requested.filter(x=>/\/(terrain|path|rider|sky|snow|town|camera|procedural)\.js|height\.bin/.test(x));assert.deepEqual(forbidden,[]);view.noTerrainRequests=true;
   view.csp=await page.evaluate(()=>window.__csp);assert.deepEqual(view.csp,[]);report.views.push(view);await context.close();
  }
 }else if(group==='interactions'){
  for(const viewport of views){
   const {context,page}=await open(viewport);await load(page);await ready(page);
   const view={viewport,packages:[],ring:[]};
   await until(page,()=>!document.body.classList.contains('video-gallery-fallback'));
   for(const p of [.31,.38,.46,.53]){const s=await at(page,p);view.ring.push({angle:s.ringAngle,index:s.ringIndex,counter:await page.locator('#ring-counter').textContent()});}
   assert.equal(new Set(view.ring.map(x=>x.angle)).size,4);
   const data=await page.evaluate(()=>JSON.parse(document.getElementById('experience-data').textContent));
   const state=await at(page,.42);assert.equal(await page.locator('#active-card-link').getAttribute('href'),data.ring.cards[state.ringIndex].link);
   let destination=null;await page.route('**/*',route=>{if(route.request().isNavigationRequest()&&route.request().url()!==base+'/'){
    destination=route.request().url();return route.fulfill({status:200,contentType:'text/html',body:'<h1>Navigation verified</h1>'});}return route.continue();});
   await page.locator('#active-card-link').click();await page.waitForURL(url=>url.href.includes('youtube')||url.pathname==='/gallery');await page.waitForLoadState('domcontentloaded');assert.ok(destination);view.galleryDestination=destination;
   await page.unroute('**/*');await load(page);await ready(page);
   // Verify the front card itself remains interactive through the live WebGL canvas.
   await at(page,.30);await page.waitForTimeout(800);
   const pointer=await page.evaluate(async()=>{const T=await import('/static/vendor/three.module.min.js?v=bansko-video-1');const c=new T.PerspectiveCamera(53,innerWidth/innerHeight,.25,5000);c.position.set(innerWidth<768?0:10,25,innerWidth<768?118:91);c.lookAt(0,15,0);c.updateMatrixWorld();const v=new T.Vector3(0,14.1,37).project(c);return {x:(v.x+1)*innerWidth/2,y:(1-v.y)*innerHeight/2};});
   destination=null;await page.route('**/*',route=>{if(route.request().isNavigationRequest()) {destination=route.request().url();return route.fulfill({status:200,contentType:'text/html',body:'<h1>Card navigation verified</h1>'});}return route.continue();});
   await page.mouse.click(pointer.x,pointer.y);await until(page,()=>document.querySelector('h1')?.textContent==='Card navigation verified');assert.ok(destination);view.meshDestination=destination;
   await page.unroute('**/*');await load(page);await ready(page);
   for(const [i,p] of [.58,.65,.72].entries()){
    await at(page,p);const link=page.locator(`[data-package="${i}"] a`);assert.equal(await link.isVisible(),true);
    if(viewport.width<768){const rect=await page.locator(`[data-package="${i}"]`).boundingBox(),rail=await page.locator('#progress-rail').boundingBox(),film=await page.locator('#journey-video').boundingBox();assert.ok(rect.y>film.y+film.height&&rect.y+rect.height<rail.y);}
    const href=await link.getAttribute('href');const response=await context.request.get(new URL(href,base).href);assert.equal(response.status(),200);view.packages.push({href,status:response.status()});
   }
   await at(page,.95);assert.equal(await page.locator('.chapter-finale .exp-button').getAttribute('href'),'/packages');
   await page.locator('.chapter-finale .exp-button').click();await page.waitForURL('**/packages');assert.ok(await page.locator('body').textContent());view.booking=true;
   report.views.push(view);await context.close();
  }
 }else if(group==='fallback'){
  for(const viewport of views){
   const view={viewport};
   const {context,page}=await open(viewport,{reducedMotion:'reduce'});const requests=[];page.on('request',r=>requests.push(r.url()));
   await load(page);assert.equal((await page.evaluate(()=>window.__experience)).mode,'static');assert.equal(await page.locator('[data-chapter]').count(),6);
   assert.equal(requests.some(x=>x.includes('.mp4')||/terrain\.js|rider\.js/.test(x)),false);await shot(page,`fallback-${viewport.width}-reduced.png`);
   await page.locator('#play-descent').click();await ready(page);await at(page,.95);
   for(let i=0;i<2;i++){await page.locator('#static-toggle').click();assert.equal(await page.evaluate(()=>window.__experience.mode),'static');await page.locator('#play-descent').click();await ready(page);await at(page,.42);}
   await page.locator('[data-go-chapter="5"]').click();await until(page,()=>window.__experience.chapter===5);view.reducedAndStill=true;await context.close();
   const error=await open(viewport);error.page.expectedMediaFailure=true;await error.page.route('**/*.mp4*',r=>r.abort('failed'));
   await load(error.page);await until(error.page,()=>document.getElementById('experience').dataset.mediaStatus==='error');await error.page.waitForTimeout(200);
   assert.equal(await error.page.locator('.journey-opening').isVisible(),true);await shot(error.page,`fallback-${viewport.width}-error.png`);view.mediaErrorPoster=true;await error.context.close();
   const slow=await open(viewport);slow.page.expectedMediaFailure=true;await slow.page.route('**/*.mp4*',async r=>{await new Promise(resolve=>setTimeout(resolve,7200));try{await r.continue();}catch{}});
   await load(slow.page);await slow.page.waitForTimeout(6200);assert.equal(await slow.page.locator('#exp-loader').isHidden(),true);assert.equal(await slow.page.locator('.journey-opening').isVisible(),true);view.slowPoster=true;await slow.context.close();
   const secure=await open(viewport,{extraHTTPHeaders:{'X-Forwarded-Proto':'https'}});await load(secure.page,'http://127.0.0.1:5001');await ready(secure.page);await at(secure.page,.95);
   view.csp=await secure.page.evaluate(()=>window.__csp);assert.deepEqual(view.csp,[]);await shot(secure.page,`fallback-${viewport.width}-csp.png`);await secure.context.close();
   report.views.push(view);
  }
  const noGL=await pw.chromium.launch({channel:'chrome',headless:true,args:['--disable-webgl']});const page=await noGL.newPage({viewport:views[1]});await load(page);await ready(page);await at(page,.42);
  assert.equal(await page.evaluate(()=>document.body.classList.contains('video-gallery-fallback')),true);assert.equal(await page.locator('.fallback-grid').isVisible(),true);await shot(page,'fallback-no-webgl.png');report.noWebGL=true;await noGL.close();
 }else throw Error('Unknown group '+group);
 assert.deepEqual(report.errors,[]);assert.deepEqual(report.failed,[]);report.pass=true;
}catch(error){report.failure=error.stack;process.exitCode=1;}
finally{await browser.close();await fs.writeFile(path.join(out,`${group}.json`),JSON.stringify(report,null,2));console.log(JSON.stringify({group,pass:report.pass,views:report.views.length,errors:report.errors,failed:report.failed,failure:report.failure},null,2));}
