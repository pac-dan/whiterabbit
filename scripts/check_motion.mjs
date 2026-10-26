/** Homepage motion acceptance; browser tooling only, no application build. */
import fs from 'node:fs/promises';
import {existsSync,readdirSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const run=path.join(root,'.runs/2026-10-26-homepage-motion-polish'),out=path.join(run,'evidence');
await fs.mkdir(path.join(out,'shots'),{recursive:true});
let pw;try{pw=await import('playwright');}catch{const cache=path.join(process.env.LOCALAPPDATA,'npm-cache/_npx');pw=await import(pathToFileURL(readdirSync(cache).map(x=>path.join(cache,x,'node_modules/playwright/index.mjs')).find(existsSync)));}
const csp=process.argv.includes('--csp'),inspect=process.argv.includes('--inspect');
const base=csp?'http://127.0.0.1:5001':'http://127.0.0.1:5000';
const browser=await pw.chromium.launch({headless:true,args:['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist']});
const report={date:new Date().toISOString(),base,errors:[],requests:[],violations:[],views:[],inspect};
async function until(page,fn,arg){for(let i=0;i<150;i++){if(await page.evaluate(fn,arg))return;await page.waitForTimeout(60);}throw Error('Browser condition timed out');}
async function progress(page,n){await page.evaluate(n=>{const t=document.getElementById('exp-track');scrollTo({top:t.offsetTop+(t.offsetHeight-innerHeight)*n,behavior:'instant'});},n);await until(page,n=>Math.abs(window.__experience.progress-n)<.001,n);await page.waitForTimeout(120);return page.evaluate(()=>window.__experience);}
try{
 for(const viewport of [{width:1440,height:900},{width:375,height:812}]){
  const context=await browser.newContext({viewport,extraHTTPHeaders:csp?{'X-Forwarded-Proto':'https'}:{}});
  await context.addInitScript(()=>{window.__violations=[];document.addEventListener('securitypolicyviolation',e=>window.__violations.push({directive:e.violatedDirective,url:e.blockedURI}));});
  const page=await context.newPage();page.on('pageerror',e=>report.errors.push(e.message));page.on('console',m=>{if(m.type()==='error')report.errors.push(m.text());});page.on('requestfailed',r=>report.requests.push({url:r.url(),reason:r.failure()?.errorText}));page.on('response',r=>{if(r.status()>=400)report.requests.push({url:r.url(),status:r.status()});});
  await page.goto(base+'/?debug=1',{waitUntil:'networkidle'});await until(page,()=>document.getElementById('exp-loader').hidden&&window.__experience);
  assert.equal((await page.evaluate(()=>window.__experience)).mode,'3d');
  const view={viewport,chapters:[],framing:[]};
  for(const [i,n] of [.06,.21,.42,.65,.82,.95].entries()){
   await progress(page,n);await page.waitForTimeout(900);const state=await page.evaluate(()=>window.__experience);
   const file=`${viewport.width}x${viewport.height}-ch${i+1}${csp?'-csp':''}.png`;await page.screenshot({path:path.join(out,'shots',file)});
   const overlay=await page.locator(`[data-chapter="${i}"]`).evaluate(e=>({opacity:getComputedStyle(e).opacity,overflow:document.documentElement.scrollWidth>innerWidth,heading:e.querySelector('h1,h2').textContent}));
   assert.equal(state.chapter,i);assert.ok(Number(overlay.opacity)>.9);assert.equal(overlay.overflow,false);
   view.chapters.push({file,state,overlay});
   if(i===3){
    view.gates=await page.evaluate(async()=>{
     const T=await import('/static/vendor/three.module.min.js?v=bansko-4');const {createTerrain}=await import('/static/experience/js/terrain.js?v=bansko-4');const {createPath}=await import('/static/experience/js/path.js?v=bansko-4');const {createCamera}=await import('/static/experience/js/camera.js?v=bansko-4');
     const scene=new T.Scene(),terrain=await createTerrain(scene,{tier:2,segments:1},s=>'/static/'+s,()=>{}),path=createPath(terrain),camera=new T.PerspectiveCamera(53,innerWidth/innerHeight,.25,5000),controller=createCamera(camera,path,terrain);
     const frames=[.58,.65,.72].map((p,i)=>{controller.update(p);camera.updateMatrixWorld();const v=path.gates[i].clone().add(new T.Vector3(0,14,0)).project(camera);return {p,x:(v.x+1)/2,y:(1-v.y)/2};});scene.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});return frames;
    });
    for(const gate of view.gates)assert.ok(Math.abs(gate.x-(viewport.width<768?.85:.74))<.06&&gate.y>.15&&gate.y<.7,`Gate composition ${JSON.stringify({viewport,gate})}`);
   }
  }
  const original=await progress(page,.21);await progress(page,.95);const reverse=await progress(page,.21);assert.deepEqual(reverse.rider,original.rider);
  await page.screenshot({path:path.join(out,'shots',`${viewport.width}x${viewport.height}-rider-reverse.png`)});view.reverse=true;
  await progress(page,.42);await page.screenshot({path:path.join(out,'shots',`${viewport.width}x${viewport.height}-ring-reverse.png`)});
  for(let i=0;i<=32;i++){
   const state=await progress(page,.12+i*.005),b=state.rider.bounds;
   view.framing.push({progress:state.progress,bounds:b});
   if(!inspect){assert.ok(b.left>.08&&b.right<.95,`Rider horizontal framing ${JSON.stringify({viewport,p:state.progress,b})}`);assert.ok(b.top>.12&&b.bottom<(viewport.width<768?.53:.8),`Rider vertical framing ${JSON.stringify({viewport,p:state.progress,b})}`);}
  }
  for(const n of [.145,.18,.25,.28]){await progress(page,n);await page.screenshot({path:path.join(out,'shots',`${viewport.width}x${viewport.height}-rider-${n}.png`)});}
  const angles=[];for(const n of [.31,.38,.46,.53]){const s=await progress(page,n);angles.push(s.ringAngle);assert.match(await page.locator('#ring-counter').textContent(),/^\d{2} \/ 12$/);}
  assert.equal(new Set(angles).size,4);view.ringRotates=true;
  const data=await page.evaluate(()=>JSON.parse(document.getElementById('experience-data').textContent));const index=(await page.evaluate(()=>window.__experience)).ringIndex;assert.equal(await page.locator('#active-card-link').getAttribute('href'),data.ring.cards[index].link);
  view.ringLink=true;
  if(!csp){
   view.moving=await page.evaluate(async()=>{
    const track=document.getElementById('exp-track'),range=track.offsetHeight-innerHeight;scrollTo({top:track.offsetTop+range*.12,behavior:'instant'});await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
    const start=performance.now(),initial=window.__experience.frames,samples=[];let last=start;
    await new Promise(resolve=>{function step(now){const q=Math.min(1,(now-start)/8000);samples.push(now-last);last=now;scrollTo({top:track.offsetTop+range*(.12+.43*q),behavior:'instant'});if(q<1)requestAnimationFrame(step);else resolve();}requestAnimationFrame(step);});
    const elapsed=performance.now()-start,frames=window.__experience.frames-initial,sorted=samples.slice().sort((a,b)=>a-b);
    return {seconds:elapsed/1000,frames,fps:frames/(elapsed/1000),p95Ms:sorted[Math.floor(sorted.length*.95)],tier:window.__experience.tier,note:'Unrecorded continuous descent-to-ring scroll on local GPU; viewport emulation, not physical-phone hardware.'};
   });
   assert.ok(view.moving.fps>=(viewport.width<768?30:45),`Moving render rate ${JSON.stringify({viewport,moving:view.moving})}`);
  }
  report.violations.push(...await page.evaluate(()=>window.__violations));report.views.push(view);await context.close();
 }
 if(!csp){
  const page=await browser.newPage({viewport:{width:1440,height:900}});await page.goto(base+'/',{waitUntil:'networkidle'});await until(page,()=>window.__experience?.mode==='3d');
  report.modules=await page.evaluate(async()=>{
   const T=await import('/static/vendor/three.module.min.js?v=bansko-4');
   const {createTerrain}=await import('/static/experience/js/terrain.js?v=bansko-4');
   const {createPath}=await import('/static/experience/js/path.js?v=bansko-4');
   const {createRider,placeholderRider}=await import('/static/experience/js/rider.js?v=bansko-4');
   const {createSnow}=await import('/static/experience/js/snow.js?v=bansko-4');
   const scene=new T.Scene(),terrain=await createTerrain(scene,{tier:2,segments:1},s=>'/static/'+s,()=>{}),path=createPath(terrain);
   const rider=await createRider(scene,path,terrain,{model:async()=>({object:placeholderRider(),update(){}})},{height:2.5,scale:1});
   const snow=createSnow(scene,new T.PerspectiveCamera(),{tier:2,particles:2500},rider,path,terrain);
   const sample=p=>{rider.update(p);snow.update(p);return {position:rider.position.toArray(),rotation:rider.pivot.quaternion.toArray(),spray:Array.from(snow.spray.geometry.attributes.position.array),tracks:Array.from(snow.track.geometry.attributes.position.array),joints:rider.handle.object.getObjectByName('Thigh').quaternion.toArray()};};
   const first=sample(.21),other=sample(.245),last=sample(.21),contact=[];
   for(let i=0;i<=40;i++){
    rider.update(.12+i*.004);const board=rider.handle.object.getObjectByName('Snowboard'),a=board.geometry.attributes.position,v=new T.Vector3();let min=Infinity;
    for(let j=0;j<a.count;j++){v.fromBufferAttribute(a,j).applyMatrix4(board.matrixWorld);min=Math.min(min,v.y-terrain.height(v.x,v.z));}contact.push(min);
   }
   let meshes=0;rider.handle.object.traverse(o=>{if(o.isMesh)meshes++;});
   const result={meshes,poseChanges:JSON.stringify(first.joints)!==JSON.stringify(other.joints),poseReverses:JSON.stringify(first.position)===JSON.stringify(last.position)&&JSON.stringify(first.joints)===JSON.stringify(last.joints),sprayReverses:JSON.stringify(first.spray)===JSON.stringify(last.spray),tracksReverse:JSON.stringify(first.tracks)===JSON.stringify(last.tracks),contact,boardShape:boardName()};
   function boardName(){return rider.handle.object.getObjectByName('Snowboard').geometry.type;}
   scene.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});return result;
  });
  assert.ok(report.modules.meshes>=20&&report.modules.poseChanges&&report.modules.poseReverses&&report.modules.sprayReverses&&report.modules.tracksReverse);
  assert.ok(report.modules.contact.every(n=>Math.abs(n-.035)<.0001));await page.close();
 }
 if(process.argv.includes('--record')){
  report.recordings=[];
  for(const viewport of [{width:1440,height:900},{width:375,height:812}]){
   const context=await browser.newContext({viewport,recordVideo:{dir:path.join(out,'videos'),size:viewport}}),page=await context.newPage();
   await page.goto(base+'/',{waitUntil:'networkidle'});await until(page,()=>window.__experience?.mode==='3d');
   await page.evaluate(async()=>{const track=document.getElementById('exp-track'),range=track.offsetHeight-innerHeight;const start=performance.now();await new Promise(resolve=>{function frame(now){const q=Math.min(1,(now-start)/15000);scrollTo({top:track.offsetTop+range*(.95*q),behavior:'instant'});if(q<1)requestAnimationFrame(frame);else resolve();}requestAnimationFrame(frame);});});
   await page.waitForTimeout(500);const video=await page.video().path();await context.close();report.recordings.push({viewport,file:video,seconds:15,note:'Visual review recording; capture overhead excludes it from performance measurements.'});
  }
 }
 assert.deepEqual(report.errors,[]);assert.deepEqual(report.requests,[]);assert.deepEqual(report.violations,[]);report.pass=true;
}catch(e){report.pass=false;report.failure=e.stack;process.exitCode=1;console.error(e.stack);}
finally{await fs.writeFile(path.join(out,csp?'motion-csp.json':inspect?'motion-inspect.json':'motion-browser.json'),JSON.stringify(report,null,2));await browser.close();}
console.log(JSON.stringify({pass:report.pass,views:report.views.length,errors:report.errors,requests:report.requests,failure:report.failure}));
