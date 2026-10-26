import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {launch,until,shot,save,base,out,views,scroll} from './refinement_browser.mjs';
const group=process.argv[2];
const browser=await launch();
const report={group,date:new Date().toISOString(),base,checks:[],pass:false};
const check=(name,result,detail)=>{report.checks.push({name,pass:!!result,detail});assert.ok(result,name+': '+JSON.stringify(detail));};
async function open(view=views[0],options={}){
 const context=await browser.newContext({viewport:view,...options}),page=await context.newPage();
 const errors=[],requests=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});page.on('requestfailed',r=>errors.push(r.url()+' '+r.failure()?.errorText));page.on('request',r=>requests.push(r.url()));
 await page.goto(base);await until(page,()=>window.__experience);return {context,page,errors,requests};
}
async function anchor(page,id){const i=await page.locator('#'+id).getAttribute('data-chapter');await page.locator(`[data-go-chapter="${i}"]`).click();await until(page,id=>Math.abs(scrollY-document.getElementById(id).offsetTop)<.1,id);await page.waitForTimeout(300);}
async function hero(page){return page.evaluate(()=>{
 const selectors=['#summit-title','.flow-hero .exp-subline','#hero-book','.flow-explore'];
 return selectors.map(sel=>{const e=document.querySelector(sel),r=e.getBoundingClientRect(),s=getComputedStyle(e);return{sel,text:e.textContent.trim(),rect:r.toJSON(),clip:s.clipPath,visible:r.top>=65&&r.bottom<innerHeight-65&&r.left>=0&&r.right<=innerWidth&&s.clipPath==='none'&&s.visibility!=='hidden'};});
});}
async function noOverflow(page){return page.evaluate(()=>({width:innerWidth,document:document.documentElement.scrollWidth}));}
try{
 if(group==='hero')for(const v of views){
  const {context,page,errors,requests}=await open(v);
  for(const mode of ['arrival','refresh','back','top']){
   if(mode==='refresh'){await page.reload();await until(page,()=>window.__experience);}
   if(mode==='back'){await page.locator('#hero-book').click();await page.waitForURL('**/packages');await page.goBack();await until(page,()=>window.__experience);}
   if(mode==='top'){await anchor(page,'bansko');await page.locator('[data-go-chapter="0"]').click();await until(page,()=>scrollY<2);}
   await page.waitForTimeout(300);const result=await hero(page);check(`${v.width} ${mode} full hero`,result.every(r=>r.visible),result);
  }
  check(`${v.width} no initial terrain`,!requests.some(u=>/three|terrain\.js|ring\.js|rider\.js/.test(u)),requests.filter(u=>/experience|vendor/.test(u)));
  check(`${v.width} no errors`,!errors.length,errors);await shot(page,'after',`${v.width}x${v.height}-hero.png`);await context.close();
 }
 else if(group==='journey')for(const v of views){
  const {context,page,errors}=await open(v,{recordVideo:{dir:path.join(out,'recordings'),size:v}});
  await until(page,()=>window.__experience.video.ready&&document.querySelector('#journey-video').readyState>=2);
  const range=await page.evaluate(()=>window.__experience.journeyRange),samples=[];
  for(const p of [0,.2,.4,.6,.8,1,.8,.6,.4,.2,0]){
   await scroll(page,p*range);await until(page,()=>{const s=window.__experience.video;return !s.seeking&&Math.abs(s.current-s.desired)<.06;});
   const s=await page.evaluate(()=>window.__experience);samples.push({p,...s.video});
  }
  check(`${v.width} forward and reverse`,samples[5].current>8.9&&samples[2].current<samples[3].current&&samples[8].current<samples[7].current&&samples.at(-1).current<.06,samples);
  for(let i=0;i<=55;i++){await page.evaluate(y=>scrollTo({top:y,behavior:'instant'}),range*i/55);await page.waitForTimeout(45);}
  await until(page,()=>!window.__experience.video.seeking&&window.__experience.video.current>8.9);
  const a=await page.evaluate(()=>document.querySelector('#journey-video').currentTime);await page.waitForTimeout(1100);const b=await page.evaluate(()=>document.querySelector('#journey-video').currentTime);
  check(`${v.width} held town frame`,Math.abs(a-b)<.001,{a,b});
  const order=await page.evaluate(()=>[...document.querySelectorAll('[data-chapter]')].map(e=>({id:e.id,top:e.offsetTop,height:e.offsetHeight})));
  check(`${v.width} town before films`,order[2].id==='arrival'&&order[3].id==='ring'&&order[3].top>=order[2].top+v.height*.6,order);
  for(const i of [3,0,5,2,4,1,3]){await page.locator(`[data-go-chapter="${i}"]`).click();await until(page,i=>Math.abs(scrollY-document.querySelector(`[data-chapter="${i}"]`).offsetTop)<.1,i);await until(page,()=>!window.__experience.video.seeking&&Math.abs(window.__experience.video.current-window.__experience.video.desired)<.06);check(`${v.width} chapter ${i} landing`,await page.evaluate(i=>window.__experience.chapter===i,i));}
  await page.evaluate(r=>{for(const p of [.1,.9,.3,1,.4,.95])scrollTo({top:r*p,behavior:'instant'});},range);
  await until(page,()=>!window.__experience.video.seeking&&Math.abs(window.__experience.video.current-window.__experience.video.desired)<.06);
  check(`${v.width} bounded seeks`,await page.evaluate(()=>window.__experience.video.maxPending<=1&&document.querySelector('#journey-video').paused));
  for(const [name,id,offset] of [['town','arrival',0],['transition','ring',-.65*v.height],['gallery','ring',0],['close','bansko',0]]){await anchor(page,id);if(offset)await scroll(page,await page.evaluate(()=>scrollY)+offset);await shot(page,'after',`${v.width}x${v.height}-${name}.png`);}
  check(`${v.width} no errors`,!errors.length,errors);await context.close();
 }
 else if(group==='gallery')for(const v of [views[0],views[3]]){
  const {context,page,errors,requests}=await open(v,{hasTouch:true});await anchor(page,'ring');await until(page,()=>window.__experience.galleryReady);
  check(`${v.width} no podium renderer`,await page.locator('canvas').count()===0&&!requests.some(u=>/three|ring\.js/.test(u)));
  await page.locator('#film-next').click();await page.waitForTimeout(60);check('mouse next',await page.evaluate(()=>window.__experience.galleryIndex===1));
  await page.locator('#film-prev').focus();await page.keyboard.press('ArrowLeft');await page.waitForTimeout(60);check('keyboard previous',await page.evaluate(()=>window.__experience.galleryIndex===0));
  await page.keyboard.press('ArrowLeft');const count=await page.locator('[data-film]').count();await page.waitForTimeout(60);check('wrap previous',await page.evaluate(n=>window.__experience.galleryIndex===n-1,count));
  await page.keyboard.press('Home');
  const cdp=await context.newCDPSession(page),box=await page.locator('#film-stage').boundingBox(),y=box.y+150,x=v.width/2;
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:x+65,y}]});await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:x-65,y}]});await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await page.waitForTimeout(500);
  check('touch selection',await page.evaluate(()=>window.__experience.galleryIndex===1&&!document.querySelector('dialog').open));
  await page.locator('#film-next').focus();await page.keyboard.press('Home');await page.locator('#play-selected-film').click();
  await until(page,()=>document.querySelector('#film-player video')?.currentTime>.3);
  check('explicit film playback',await page.locator('#film-player video').evaluate(v=>!v.paused&&v.currentTime>.3));await shot(page,'after',`${v.width}-film-playing.png`);
  await page.keyboard.press('Escape');await until(page,()=>!document.querySelector('#film-player video'));check('dialog releases decoder and restores focus',await page.evaluate(()=>!document.querySelector('dialog').open&&!document.querySelector('#film-player video')&&document.activeElement.id==='play-selected-film'));
  const y0=await page.evaluate(()=>scrollY);await page.mouse.move(v.width/2,400);await page.mouse.wheel(0,350);await page.waitForTimeout(1200);check('vertical scrolling retained',await page.evaluate(y=>scrollY>y+100,y0));
  check('no errors',!errors.length,errors);await context.close();
 }
 else if(group==='booking'){
  const {context,page,errors}=await open();await anchor(page,'sessions');
  const links=await page.locator('.flow-package a').evaluateAll(a=>a.map(e=>({title:e.textContent,href:e.getAttribute('href')})));
  check('three genuine packages',links.length===3&&links.every(a=>/^\/packages\/\d+$/.test(a.href)),links);
  for(const link of links){const r=await context.request.get(base+link.href);check(link.href,r.status()===200);}
  await page.locator('.flow-package a').first().click();check('package detail action',await page.locator('.detail-aside a[href*="booking"],.detail-aside a[href*="checkout"],.detail-aside a[href^="/contact?subject="]').count()>0,await page.locator('a').evaluateAll(a=>a.map(x=>x.getAttribute('href'))));
  for(const route of ['/packages','/gallery','/testimonials','/about','/faq','/contact','/auth/login']){const r=await page.goto(base+route);check(route,r.status()===200);}
  // Leaving the homepage intentionally cancels its paused background request.
  // Keep these receipts visible; HTTP failures and all other errors still fail.
  const cancelled=errors.filter(e=>/bansko-descent-.*\.mp4.*net::ERR_ABORTED$/.test(e));
  check('supporting pages no relevant errors',errors.length===cancelled.length,{errors,expectedNavigationCancellations:cancelled});await context.close();
  for(const v of [views[0],views[3]]){const c=await browser.newContext({viewport:v}),p=await c.newPage();const r=await p.goto('http://127.0.0.1:5002/');check('empty database 200',r.status()===200);await until(p,()=>window.__experience);await anchor(p,'ring');await until(p,()=>window.__experience.galleryReady);check('empty database honest concept',await p.locator('[data-film]').count()===1);await shot(p,'after',`${v.width}-empty-gallery.png`);await anchor(p,'sessions');check('empty packages enquiry',await p.getByRole('heading',{name:'Package coming soon'}).count()===3);await shot(p,'after',`${v.width}-empty-packages.png`);await c.close();}
 }
 else if(group==='accessibility'){
  for(const v of views){const {context,page,errors}=await open(v);for(const id of ['summit','drop','arrival','ring','sessions','bansko']){await anchor(page,id);const w=await noOverflow(page);check(`${v.width} ${id} no overflow`,w.document<=w.width,w);}
   await page.addStyleTag({content:'html{font-size:125%!important}'});await anchor(page,'summit');const w=await noOverflow(page);check(`${v.width} enlarged text no overflow`,w.document<=w.width,w);check('heading not masked',await page.locator('h1').evaluate(e=>getComputedStyle(e).clipPath==='none'));await shot(page,'after',`${v.width}-large-text.png`);
   await page.locator('#static-toggle').click();await until(page,()=>window.__experience.mode==='static');check('Still View stops video',await page.evaluate(()=>window.__experience.mode==='static'&&!document.querySelector('#journey-video').getAttribute('src')));await anchor(page,'arrival');check('Still View town image',await page.locator('.arrival-still').evaluate(e=>e.complete&&e.naturalWidth>0));check('no errors',!errors.length,errors);await context.close();}
  for(const reducedMotion of ['reduce']){const {context,page,requests}=await open(views[3],{reducedMotion});check('reduced motion no film download',!requests.some(u=>u.includes('.mp4')));check('all static chapters',await page.locator('[data-chapter]').count()===6);await page.locator('#play-descent').click();await until(page,()=>window.__experience.video.ready);check('explicit motion opt-in',await page.evaluate(()=>window.__experience.mode==='video'&&getComputedStyle(document.querySelector('.flow-stage')).position==='fixed'));await context.close();}
  for(const failure of ['slow','error']){const context=await browser.newContext({viewport:views[3]}),page=await context.newPage();await page.route('**/*.mp4*',async r=>{if(failure==='slow')await new Promise(res=>setTimeout(res,7000));await r.abort('failed');});await page.goto(base,{waitUntil:'domcontentloaded'});await page.waitForTimeout(failure==='slow'?6500:800);check(`${failure} usable hero`,(await hero(page)).every(x=>x.visible));check(`${failure} poster remains`,await page.locator('#journey-poster').evaluate(e=>e.complete&&e.naturalWidth>0));await shot(page,'after',`375-${failure}.png`);await context.close();}
  const context=await browser.newContext({viewport:views[0],extraHTTPHeaders:{'X-Forwarded-Proto':'https'}}),page=await context.newPage(),violations=[];
  await context.addInitScript(()=>{window.__csp=[];document.addEventListener('securitypolicyviolation',e=>window.__csp.push({directive:e.violatedDirective,url:e.blockedURI}));});page.on('pageerror',e=>violations.push(e.message));
  const response=await page.goto('http://127.0.0.1:5001/');await until(page,()=>window.__experience);await anchor(page,'ring');await until(page,()=>window.__experience.galleryReady);await page.locator('#play-selected-film').click();await until(page,()=>document.querySelector('#film-player video')?.currentTime>.2);const csp=await page.evaluate(()=>window.__csp);check('production CSP',!csp.length&&!violations.length,{header:response.headers()['content-security-policy'],violations:csp,errors:violations});await context.close();
 }
 else if(group==='delivery'){
  const expected='bansko-refine-1',urls=[process.env.REFINEMENT_PREVIEW||'https://white-rabbit-git-bansko-experience-devman-1a64abec.vercel.app/','https://white-rabbit-zeta.vercel.app/'];
  for(const url of urls){const r=await fetch(url,{redirect:'manual'}),html=await r.text(),version=html.match(/data-version="([^"]+)"/)?.[1];report.checks.push({name:url,pass:r.status===200&&version===expected,status:r.status,version,location:r.headers.get('location'),expected});}
  const context=await browser.newContext({viewport:views[0]}),page=await context.newPage();await page.goto(urls[1]);await page.waitForTimeout(1000);await shot(page,'delivery','public-current.png');await context.close();
  check('preview and public candidate delivery',report.checks.every(c=>c.pass),report.checks.slice());
 }
 else throw Error('Unknown group: '+group);
 report.pass=true;
}catch(e){report.failure=e.stack;process.exitCode=1;}finally{await browser.close();await save(group+'.json',report);console.log(JSON.stringify(report,null,2));}

