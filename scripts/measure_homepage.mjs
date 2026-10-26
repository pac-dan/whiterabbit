import fs from 'node:fs/promises';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {launch,until,shot,save,base,out,views} from './refinement_browser.mjs';
const phase=process.argv[2];if(!['before','after'].includes(phase))throw Error('Use before or after');
const browser=await launch();
const report={phase,date:new Date().toISOString(),revision:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),
 conditions:{browser:await browser.version(),downloadBytesPerSecond:500000,uploadBytesPerSecond:500000,latencyMs:80,coldHTTP:true,initialWindowMs:12000},profiles:[],pass:false};
try{
 for(const viewport of [views[0],views[3]]){
  const cpu=viewport.width<768?4:1,profile={viewport,cpu,runs:[]};
  for(let n=0;n<3;n++){
   const context=await browser.newContext({viewport});const page=await context.newPage();const cdp=await context.newCDPSession(page);
   await cdp.send('Network.enable');await cdp.send('Network.setCacheDisabled',{cacheDisabled:true});
   await cdp.send('Network.emulateNetworkConditions',{offline:false,latency:80,downloadThroughput:500000,uploadThroughput:500000});await cdp.send('Emulation.setCPUThrottlingRate',{rate:cpu});
   const requests=new Map();cdp.on('Network.requestWillBeSent',e=>requests.set(e.requestId,{url:e.request.url,type:e.type,bytes:0}));cdp.on('Network.loadingFinished',e=>{const r=requests.get(e.requestId);if(r)r.bytes=e.encodedDataLength;});
   await context.addInitScript(()=>{
    window.__loadMetrics={heroMs:null,posterMs:null,motionMs:null};
    const tick=()=>{const m=window.__loadMetrics,h=document.querySelector('#summit-title'),v=document.querySelector('#journey-video'),poster=document.querySelector('#journey-poster,.journey-opening');
     if(poster?.complete&&poster.naturalWidth&&!m.posterMs)m.posterMs=performance.now();
     if(v?.readyState>=2&&v.videoWidth&&!m.motionMs)m.motionMs=performance.now();
     if(h){const s=getComputedStyle(h),r=h.getBoundingClientRect(),sub=document.querySelector('.chapter-summit .exp-subline,.flow-hero .exp-subline'),action=document.querySelector('#hero-book');
      if(s.clipPath==='none'&&s.visibility!=='hidden'&&r.top>=0&&r.bottom<=innerHeight&&r.left>=0&&r.right<=innerWidth&&sub?.getBoundingClientRect().bottom<innerHeight&&action?.getBoundingClientRect().bottom<innerHeight&&!m.heroMs)m.heroMs=performance.now();}
     if(performance.now()<16000)requestAnimationFrame(tick);};requestAnimationFrame(tick);
   });
   await page.goto(base,{waitUntil:'domcontentloaded'});await page.waitForTimeout(Math.max(0,12000-await page.evaluate(()=>performance.now())));
   const metrics=await page.evaluate(()=>({...window.__loadMetrics,heading:{clip:getComputedStyle(document.getElementById('summit-title')).clipPath,text:document.getElementById('summit-title').textContent},version:document.getElementById('experience').dataset.version,video:document.querySelector('video')?.currentSrc}));
   const initial=[...requests.values()].filter(x=>x.url.startsWith(base));
   const entry={...metrics,resources:initial,mediaBytes:initial.filter(x=>/\.mp4/.test(x.url)).reduce((s,x)=>s+x.bytes,0),totalBytes:initial.reduce((s,x)=>s+x.bytes,0),seekMs:[]};
   await until(page,()=>document.getElementById('journey-video')?.readyState>=2,undefined,25000);
   for(const fraction of [.15,.7,.35]){
    const start=Date.now();
    await page.evaluate(q=>{const d=JSON.parse(document.getElementById('experience-data').textContent),points=d.journey.cues;let p=0;
     for(let i=1;i<points.length;i++)if(q<=points[i][1]){const a=points[i-1],b=points[i];p=a[0]+(b[0]-a[0])*(q-a[1])/(b[1]-a[1]);break;}
     const t=document.getElementById('exp-track'),range=window.__experience.journeyRange??(t.offsetHeight-innerHeight);scrollTo({top:t.offsetTop+p*range,behavior:'instant'});},fraction);
    await until(page,q=>{const v=document.getElementById('journey-video');return !v.seeking&&Math.abs(v.currentTime-v.duration*q)<.06;},fraction);
    entry.seekMs.push(Date.now()-start);
   }
   profile.runs.push(entry);await context.close();
  }
  const median=a=>a.slice().sort((a,b)=>a-b)[Math.floor(a.length/2)];
  profile.medians={heroMs:profile.runs.every(r=>r.heroMs!==null)?median(profile.runs.map(r=>r.heroMs)):null,posterMs:median(profile.runs.map(r=>r.posterMs)),motionMs:median(profile.runs.map(r=>r.motionMs)),mediaBytes:median(profile.runs.map(r=>r.mediaBytes)),totalBytes:median(profile.runs.map(r=>r.totalBytes)),seekMs:median(profile.runs.flatMap(r=>r.seekMs))};
  report.profiles.push(profile);
 }
 for(const viewport of views){const context=await browser.newContext({viewport});const page=await context.newPage();await page.goto(base);await until(page,()=>window.__experience);
  for(const [name,p,id] of [['hero',0,'summit'],['town',.95,'arrival'],['transition',.3,'ring'],['gallery',.42,'ring'],['close',.95,'bansko']]){
   if(phase==='before')await page.evaluate(p=>{const t=document.getElementById('exp-track');scrollTo({top:t.offsetTop+(t.offsetHeight-innerHeight)*p,behavior:'instant'});},p);
   else await page.evaluate(({id,name})=>{const el=document.getElementById(id);scrollTo({top:el.offsetTop+(name==='transition'?-innerHeight*.65:0),behavior:'instant'});},{id,name});
   await page.waitForTimeout(600);await shot(page,phase,`${viewport.width}x${viewport.height}-${name}.png`);
  }await context.close();
 }
 if(phase==='after'){
  const before=JSON.parse(await fs.readFile(path.join(out,'performance-before.json'),'utf8'));
  report.comparison=report.profiles.map((p,i)=>({viewport:p.viewport,before:before.profiles[i].medians,after:p.medians}));
  if(report.profiles.some((p,i)=>p.medians.heroMs===null||p.medians.totalBytes>=before.profiles[i].medians.totalBytes))throw Error('Hero visibility or transfer improvement not demonstrated');
 }
 report.pass=true;
}catch(e){report.failure=e.stack;process.exitCode=1;}finally{await browser.close();await save(`performance-${phase}.json`,report);console.log(JSON.stringify({pass:report.pass,phase,profiles:report.profiles.map(p=>({viewport:p.viewport,medians:p.medians})),failure:report.failure},null,2));}
