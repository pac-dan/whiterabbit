/** Re-run after npx -y playwright@1.48.2 install chromium. No app build step. */
import fs from 'node:fs/promises';
import {existsSync,readdirSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const run=path.join(root,'.runs/2026-10-26-bansko-experience');
const evidence=path.join(run,'evidence'),shots=path.join(evidence,'shots'),fixtures=path.join(evidence,'fixtures');
await fs.mkdir(shots,{recursive:true});await fs.mkdir(fixtures,{recursive:true});
let pw;
try{pw=await import('playwright');}catch{
 const cache=path.join(process.env.LOCALAPPDATA??'', 'npm-cache/_npx');
 const found=existsSync(cache)&&readdirSync(cache).map(x=>path.join(cache,x,'node_modules/playwright/index.mjs')).find(x=>existsSync(x));
 if(!found)throw Error('Install browser tooling: npx -y playwright@1.48.2 install chromium');
 pw=await import(pathToFileURL(found).href);
}
const args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist'];
const base=process.env.EXPERIENCE_URL??'http://127.0.0.1:5000';
const production=process.argv.includes('--csp');
const browser=await pw.chromium.launch({headless:true,args});
const sizes=[{width:1440,height:900},{width:375,height:812}];
const report={date:new Date().toISOString(),base,errors:[],requests:[],violations:[],chapters:[],fallback:[],quality:[],content:[],slots:{},notes:[]};
async function until(p,fn,arg){const start=Date.now();while(Date.now()-start<12000){if(await p.evaluate(fn,arg))return;await new Promise(r=>setTimeout(r,80));}throw Error('Browser condition timed out');}
async function context(size,extra={}){
 const c=await browser.newContext({viewport:size,deviceScaleFactor:1,extraHTTPHeaders:production?{'X-Forwarded-Proto':'https'}:{},...extra});
 await c.addInitScript(()=>{window.__csp=[];document.addEventListener('securitypolicyviolation',e=>window.__csp.push({directive:e.violatedDirective,url:e.blockedURI}));});
 if(production)await c.route('https://**/*',r=>{const headers={...r.request().headers()};delete headers['x-forwarded-proto'];return r.continue({headers});});
 const p=await c.newPage();p.on('pageerror',e=>report.errors.push(e.message));
 p.on('console',m=>{if(m.type()==='error')report.errors.push(m.text());});
 p.on('requestfailed',r=>report.requests.push({url:r.url(),reason:r.failure()?.errorText}));
 p.on('response',r=>{if(r.status()>=400)report.requests.push({url:r.url(),status:r.status()});});
 return {c,p};
}
async function open(p,suffix=''){
 await p.goto(base+'/'+suffix,{waitUntil:'networkidle'});
 await until(p,()=>document.getElementById('exp-loader')?.hidden&&window.__experience);
 await p.waitForTimeout(300);
}
async function gotoProgress(p,n){
 await p.evaluate(n=>{const t=document.getElementById('exp-track');window.scrollTo({top:t.offsetTop+(t.offsetHeight-innerHeight)*n,behavior:'instant'});},n);
 await p.waitForTimeout(800);
 await until(p,n=>Math.abs(window.__experience.progress-n)<.006,n);
}
try{
 for(const size of sizes){
  const {c,p}=await context(size);await open(p);
  assert.equal((await p.evaluate(()=>window.__experience)).mode,'3d');
  const gpu=await p.evaluate(()=>{const g=document.getElementById('exp-canvas').getContext('webgl2');const e=g.getExtension('WEBGL_debug_renderer_info');return g.getParameter(e.UNMASKED_RENDERER_WEBGL);});
  report.notes.push({size,gpu});
  for(const [i,n] of [.06,.21,.42,.65,.82,.95].entries()){
   await gotoProgress(p,n);const state=await p.evaluate(()=>window.__experience);assert.equal(state.chapter,i);
   const file=`${size.width}x${size.height}-ch${i+1}.png`;await p.screenshot({path:path.join(shots,file)});
   const visible=await p.locator(`[data-chapter="${i}"]`).evaluate(e=>({alpha:getComputedStyle(e).opacity,heading:e.querySelector('h1,h2').textContent,overflow:document.documentElement.scrollWidth>innerWidth}));
   assert.ok(Number(visible.alpha)>.9);assert.equal(visible.overflow,false);
   report.chapters.push({size,shot:file,state,visible});
   console.log(`${size.width}x${size.height} chapter ${i+1}: tier ${state.tier}, ${state.fps.toFixed(1)} fps, ${state.drawCalls} draws`);
  }
  await gotoProgress(p,.42);await p.screenshot({path:path.join(shots,`${size.width}x${size.height}-ch3-reverse.png`)});
  report.chapters.push({size,reverse:true,state:await p.evaluate(()=>window.__experience)});
  const cards=await p.evaluate(()=>JSON.parse(document.getElementById('experience-data').textContent).ring.cards);
  const before=await p.evaluate(()=>window.__experience.ringAngle);await gotoProgress(p,.46);const after=await p.evaluate(()=>window.__experience.ringAngle);assert.notEqual(before,after);
  const card=await p.evaluate(()=>window.__experience.ringIndex);const href=await p.locator('#active-card-link').getAttribute('href');assert.equal(href,cards[card].link);
  assert.match(await p.locator('#ring-counter').textContent(),/^\d{2} \/ 12$/);
  // Front mesh hit test: temporarily route navigation so the target is observed safely.
  let clicked=null;await p.route('https://www.youtube.com/**',r=>{clicked=r.request().url();return r.fulfill({status:200,body:'Video destination verified'});});
  await p.locator('#active-card-link').click();await p.waitForTimeout(250);assert.ok(clicked||p.url().includes('/gallery'));
  report.content.push({size,ringCounter:true,ringRotates:before!==after,ringHref:href,ringClick:clicked||p.url()});
  report.violations.push(...await p.evaluate(()=>window.__csp??[]));await c.close();
  const reduced=await context(size,{reducedMotion:'reduce'});await open(reduced.p);
  assert.equal((await reduced.p.evaluate(()=>window.__experience)).mode,'static');
  for(let i=0;i<6;i++)assert.ok(await reduced.p.locator(`[data-chapter="${i}"]`).isVisible());
  assert.equal(await reduced.p.locator('.fallback-grid a').count(),12);
  await reduced.p.screenshot({path:path.join(shots,`${size.width}x${size.height}-reduced-motion.png`),fullPage:true});
  // Explicit reduced-motion opt-in starts 3D.
  await reduced.p.locator('#play-descent').click();await until(reduced.p,()=>window.__experience.mode==='3d');
  report.fallback.push({size,reducedMotion:true,allSixSections:true,optIn:true});await reduced.c.close();
 }
 if(!production){
  const noGL=await pw.chromium.launch({headless:true,args:['--disable-webgl']});
  for(const size of sizes){const p=await noGL.newPage({viewport:size});await open(p);assert.equal((await p.evaluate(()=>window.__experience)).mode,'static');for(let i=0;i<6;i++)assert.ok(await p.locator(`[data-chapter="${i}"]`).isVisible());await p.screenshot({path:path.join(shots,`${size.width}x${size.height}-no-webgl.png`),fullPage:true});report.fallback.push({size,noWebGL:true,allSixSections:true});await p.close();}await noGL.close();
  for(const size of sizes){const {c,p}=await context(size);await open(p,'?tier=1&debug=1');assert.equal((await p.evaluate(()=>window.__experience)).tier,1);
   const result=await p.evaluate(async()=>{const {createQuality}=await import('/static/experience/js/quality.js?v=bansko-1');history.replaceState({},'','?tier=3');const q=createQuality();let stepped=false;for(let i=0;i<65;i++)stepped=q.sample(.04)||stepped;return {start:3,after:q.tier,stepped};});assert.ok(result.stepped&&result.after===2);report.quality.push({size,forced:1,watchdog:result});
   await p.screenshot({path:path.join(shots,`${size.width}x${size.height}-tier1.png`)});await c.close();}
  await supplementProof();
  await slotProof();
  await otherPages();
 }
 assert.deepEqual(report.errors,[],'Browser console/page errors');assert.deepEqual(report.requests,[],'Failed requests');assert.deepEqual(report.violations,[],'CSP violations');
 report.pass=true;
} catch(e){report.pass=false;report.failure=e.stack;console.error(e.stack);process.exitCode=1;}
finally {await fs.writeFile(path.join(evidence,production?'csp-report.json':'browser-report.json'),JSON.stringify(report,null,2));await browser.close();}

async function slotProof(){
 const {c,p}=await context(sizes[0]);
 await p.route('**/__fixture/GLTFExporter.js',r=>r.fulfill({path:path.join(root,'scripts/fixtures/GLTFExporter.js'),contentType:'text/javascript'}));
 await open(p);
 const generated=await p.evaluate(async()=>{
  const T=await import('/static/vendor/three.module.min.js?v=bansko-1');const {placeholderRider}=await import('/static/experience/js/rider.js?v=bansko-1');const {GLTFExporter}=await import('/__fixture/GLTFExporter.js');
  const rider=placeholderRider();rider.name='proof-rider';rider.children[0].name='proof-body';rider.children[0].material.color.set('#ffb86b');
  const clip=new T.AnimationClip('Ride',1,[new T.QuaternionKeyframeTrack('proof-body.quaternion',[0,1],[0,0,0,1,0,0,.1,.995])]);
  const model=await new GLTFExporter().parseAsync(rider,{binary:true,animations:[clip]});
  const canvas=document.createElement('canvas');canvas.width=180;canvas.height=320;const ctx=canvas.getContext('2d');ctx.fillStyle='#00d4ff';ctx.fillRect(0,0,180,320);ctx.fillStyle='#061222';ctx.font='bold 24px sans-serif';ctx.fillText('REAL IMAGE',15,160);
  const png=await new Promise(r=>canvas.toBlob(r,'image/png'));
  const recorder=new MediaRecorder(canvas.captureStream(12),{mimeType:'video/webm;codecs=vp8'}),chunks=[];
  const video=await new Promise(resolve=>{recorder.ondataavailable=e=>chunks.push(e.data);recorder.onstop=()=>resolve(new Blob(chunks,{type:'video/webm'}));recorder.start();let i=0;const timer=setInterval(()=>{ctx.fillStyle=i%2?'#8b5cf6':'#ffb86b';ctx.fillRect(0,0,180,320);ctx.fillStyle='#061222';ctx.fillText('REAL VIDEO',12,160);if(++i===12){clearInterval(timer);recorder.stop();}},80);});
  return {model:Array.from(new Uint8Array(model)),png:Array.from(new Uint8Array(await png.arrayBuffer())),video:Array.from(new Uint8Array(await video.arrayBuffer()))};
 });
 await fs.writeFile(path.join(fixtures,'rider.glb'),Buffer.from(generated.model));await fs.writeFile(path.join(fixtures,'image.png'),Buffer.from(generated.png));await fs.writeFile(path.join(fixtures,'video.webm'),Buffer.from(generated.video));
 await p.route('**/__fixture/rider.glb*',r=>r.fulfill({path:path.join(fixtures,'rider.glb'),contentType:'model/gltf-binary'}));
 await p.route('**/__fixture/image.png*',r=>r.fulfill({path:path.join(fixtures,'image.png'),contentType:'image/png'}));
 await p.route('**/__fixture/video.webm*',r=>r.fulfill({path:path.join(fixtures,'video.webm'),contentType:'video/webm'}));
 await p.route('**/__fixture/corrupt*',r=>r.fulfill({status:200,body:'bad bytes',contentType:'application/octet-stream'}));
 // Override only manifest data in a test response, as if the owner had edited content.py.
 await p.route(base+'/',async route=>{const response=await route.fetch();let html=await response.text();html=html.replace(/(<script[^>]*id="experience-data"[^>]*>)(.*?)(<\/script>)/s,(_,a,b,z)=>{const d=JSON.parse(b);d.rider.src='/__fixture/rider.glb';d.rider.animation='Ride';d.ring.cards[0].media={type:'image',src:'/__fixture/image.png'};d.ring.cards[1].media={type:'video',src:'/__fixture/video.webm'};return a+JSON.stringify(d)+z;});await route.fulfill({response,body:html});});
 await open(p);await gotoProgress(p,.21);assert.ok((await p.evaluate(()=>window.__experience.slots)).rider);await p.screenshot({path:path.join(shots,'slot-model.png')});
 await gotoProgress(p,.3);await until(p,()=>window.__experience.slots.ring===2);await p.screenshot({path:path.join(shots,'slot-image.png')});
 await gotoProgress(p,.3+.25/11);await p.screenshot({path:path.join(shots,'slot-video.png')});
 const details=await p.evaluate(async()=>{
  const {createSlots}=await import('/static/experience/js/slots.js?v=bansko-1');const {placeholderRider}=await import('/static/experience/js/rider.js?v=bansko-1');const slots=createSlots(p=>p.startsWith('/')?p:'/static/'+p),placeholder='experience/placeholders/ring-01.webp';
  const image=await slots.load({type:'image',src:'/__fixture/image.png'},placeholder);const video=await slots.load({type:'video',src:'/__fixture/video.webm'},placeholder);video.activate(true);await new Promise(r=>setTimeout(r,200));const playing=!video.video.paused;video.activate(false);
  const model=await slots.model({src:'/__fixture/rider.glb',scale:2,animation:'Ride'},placeholderRider);model.update(.01);const rotation=model.object.getObjectByName('proof-body').quaternion.z;
  const badImage=await slots.load({type:'image',src:'/__fixture/corrupt.png'},placeholder);const badVideo=await slots.load({type:'video',src:'/__fixture/corrupt.webm'},placeholder);const badModel=await slots.model({src:'/__fixture/corrupt.glb'},placeholderRider);
  const result={image:{replaced:!image.isPlaceholder,width:image.texture.image.width},video:{replaced:!video.isPlaceholder,width:video.video.videoWidth,playing,paused:video.video.paused},model:{replaced:!model.isPlaceholder,name:model.object.name,scale:model.object.scale.x,animated:Math.abs(rotation)>0},brokenRecover:[badImage.isPlaceholder,badVideo.isPlaceholder,badModel.isPlaceholder]};slots.dispose();return result;
 });
 assert.ok(details.image.replaced&&details.video.replaced&&details.model.replaced);assert.ok(details.video.playing&&details.video.paused&&details.model.animated);assert.ok(details.brokenRecover.every(Boolean));
 await p.unroute(base+'/');await open(p);assert.equal((await p.evaluate(()=>window.__experience.slots)).rider,false);report.slots={...details,restoredToNone:true,fixtures:'evidence/fixtures/'};await c.close();
}
async function otherPages(){
 const {c,p}=await context(sizes[0]);
 // Existing pages have third-party embeds/scripts; track their noise separately.
 const oldErrors=report.errors.length,oldRequests=report.requests.length;
 for(const size of sizes){await p.setViewportSize(size);for(const name of ['packages','gallery','about','faq','contact','testimonials','auth/login']){
  const response=await p.goto(base+'/'+name,{waitUntil:'domcontentloaded'});assert.equal(response.status(),200);await p.waitForTimeout(200);
  assert.equal(await p.locator('#experience').count(),0);await p.screenshot({path:path.join(shots,`other-${size.width}-${name.replace('/','-')}.png`)});report.content.push({size,path:'/'+name,status:response.status(),homepageEngineAbsent:true});
 }}
 report.notes.push({legacyPageErrors:report.errors.splice(oldErrors),legacyPageFailedRequests:report.requests.splice(oldRequests)});await c.close();
}

async function supplementProof(){
 const proof={pass:false,content:[],quality:[]};
 for(const size of sizes){
  const {c,p}=await context(size);await open(p,'?tier=3&debug=1');
  const data=await p.evaluate(()=>JSON.parse(document.getElementById('experience-data').textContent));assert.equal(data.packages.length,3);
  for(const item of data.packages){const response=await c.request.get(base+item.link);assert.equal(response.status(),200);}
  await p.locator('[data-go-chapter="2"]').click();await p.waitForTimeout(1600);await until(p,()=>window.__experience.chapter===2);
  await gotoProgress(p,.3);
  const point=await p.evaluate(async()=>{
   const T=await import('/static/vendor/three.module.min.js?v=bansko-1');const {createTerrain}=await import('/static/experience/js/terrain.js?v=bansko-1');const {createPath}=await import('/static/experience/js/path.js?v=bansko-1');const {createCamera}=await import('/static/experience/js/camera.js?v=bansko-1');
   const scene=new T.Scene(),terrain=await createTerrain(scene,{tier:2,segments:1},p=>'/static/'+p,()=>{}),path=createPath(terrain),camera=new T.PerspectiveCamera(53,innerWidth/innerHeight,.25,5000);createCamera(camera,path,terrain).update(.3);camera.updateMatrixWorld();const v=path.shelf.clone().add(new T.Vector3(0,13,37)).project(camera);scene.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});return {x:(v.x*.5+.5)*innerWidth,y:(.5-v.y*.5)*innerHeight};
  });
  let target=null;await p.route('https://www.youtube.com/**',r=>{target=r.request().url();return r.fulfill({status:200,body:'Front mesh navigation verified'});});
  await p.mouse.move(point.x,point.y);await p.waitForTimeout(150);await p.mouse.click(point.x,point.y);await p.waitForTimeout(200);assert.equal(target,data.ring.cards[0].link);
  await open(p,'?tier=3&debug=1');await p.waitForTimeout(4500);
  const performanceState=await p.evaluate(()=>window.__experience);assert.ok(performanceState.firstFrameMs<2500);
  await p.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'));});
  const beforeHidden=await p.evaluate(()=>window.__experience.frames);await p.waitForTimeout(300);const afterHidden=await p.evaluate(()=>window.__experience.frames);assert.equal(afterHidden,beforeHidden);
  await p.evaluate(()=>{delete document.hidden;document.dispatchEvent(new Event('visibilitychange'));});await p.waitForTimeout(200);
  await p.evaluate(()=>scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'}));await p.waitForTimeout(700);
  const atFooter=await p.evaluate(()=>({top:document.querySelector('footer').getBoundingClientRect().top,frames:window.__experience.frames,ended:document.body.classList.contains('exp-ended')}));await p.waitForTimeout(300);const afterFooter=await p.evaluate(()=>window.__experience.frames);assert.ok(atFooter.ended&&atFooter.top<size.height);assert.equal(afterFooter,atFooter.frames);
  proof.quality.push({size,performanceState,hiddenPause:beforeHidden===afterHidden,footerPause:afterFooter===atFooter.frames});await c.close();
  const empty=await context(size);await empty.p.goto('http://127.0.0.1:5002/',{waitUntil:'networkidle'});await until(empty.p,()=>window.__experience?.mode==='3d');await gotoProgress(empty.p,.65);
  assert.equal(await empty.p.locator('.exp-package h3').filter({hasText:'Package coming soon'}).count(),3);
  await empty.p.screenshot({path:path.join(shots,`${size.width}x${size.height}-empty-db.png`)});
  const emptyData=await empty.p.evaluate(()=>JSON.parse(document.getElementById('experience-data').textContent));assert.equal(emptyData.packages.length,0);assert.equal(emptyData.ring.cards.length,12);
  proof.content.push({size,emptyDB:true,links:true,rail:true,meshClick:true,meshTarget:target});await empty.c.close();
 }
 proof.pass=true;await fs.writeFile(path.join(evidence,'supplement-report.json'),JSON.stringify(proof,null,2));
}
