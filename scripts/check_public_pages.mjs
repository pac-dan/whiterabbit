/** Browser QA: npx -y playwright@1.48.2 install chromium, then node this file. */
import fs from 'node:fs/promises';
import {existsSync,readdirSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const evidence=process.env.PUBLIC_EVIDENCE??path.join(root,'.runs/2026-10-26-alpine-pages/evidence');
const shots=path.join(evidence,'shots');await fs.mkdir(shots,{recursive:true});
let pw;
try {pw=await import('playwright');} catch {
  const cache=path.join(process.env.LOCALAPPDATA??'','npm-cache/_npx');
  const found=existsSync(cache)&&readdirSync(cache).map(x=>path.join(cache,x,'node_modules/playwright/index.mjs')).find(existsSync);
  if(!found)throw Error('Run npx -y playwright@1.48.2 install chromium first.');
  pw=await import(pathToFileURL(found).href);
}
const production=process.argv.includes('--csp');
const base=production?'http://127.0.0.1:5001':'http://127.0.0.1:5000';
const browser=await pw.chromium.launch({headless:true,args:['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist']});
const report={pass:false,base,pages:[],interactions:[],errors:[],failed:[],violations:[],empty:[],home:[]};
const sizes=[{width:1440,height:900},{width:375,height:812}];
async function until(p,fn){for(let i=0;i<100;i++){if(await p.evaluate(fn))return;await p.waitForTimeout(80);}throw Error('Browser condition timed out');}
async function context(size,extra={}){
  const c=await browser.newContext({viewport:size,deviceScaleFactor:1,extraHTTPHeaders:production?{'X-Forwarded-Proto':'https'}:{},...extra});
  await c.addInitScript(()=>{window.__csp=[];document.addEventListener('securitypolicyviolation',e=>window.__csp.push({directive:e.violatedDirective,url:e.blockedURI}));});
  if(production)await c.route('https://**/*',r=>{const headers={...r.request().headers()};delete headers['x-forwarded-proto'];return r.continue({headers});});
  const p=await c.newPage();
  p.on('pageerror',e=>report.errors.push(e.message));p.on('console',m=>{if(m.type()==='error')report.errors.push(m.text());});
  p.on('requestfailed',r=>report.failed.push({url:r.url(),failure:r.failure()}));
  p.on('response',r=>{if(r.status()>=400)report.failed.push({url:r.url(),status:r.status()});});
  return {c,p};
}
async function open(p,route){const response=await p.goto(base+route,{waitUntil:'networkidle'});assert.equal(response.status(),200,route);await p.evaluate(()=>document.fonts.ready);return response;}
async function capture(p,size,name){
  // Visit the bottom before capturing so native lazy images are present in full-page shots.
  await p.evaluate(()=>scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'}));await p.waitForTimeout(120);
  await p.evaluate(()=>scrollTo({top:0,behavior:'instant'}));await p.waitForTimeout(100);
  const metrics=await p.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,h1:document.querySelector('h1')?.textContent,skin:document.body.classList.contains('alpine-page'),three:performance.getEntriesByType('resource').some(r=>r.name.includes('three.module')),images:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src)}));
  assert.equal(metrics.scrollWidth,metrics.width,`${name} horizontal overflow`);assert.ok(metrics.skin&&metrics.h1&&!metrics.three);assert.deepEqual(metrics.images,[],`${name} images`);
  const file=`${size.width}x${size.height}-${name}${production?'-csp':''}.png`;await p.screenshot({path:path.join(shots,file),fullPage:true});
  report.pages.push({size,name,shot:file,metrics});report.violations.push(...await p.evaluate(()=>window.__csp));
  console.log(`${size.width}x${size.height} ${name}: layout, assets and HTML passed`);
}
try {
  for(const size of sizes){
    const {c,p}=await context(size);
    await open(p,'/packages');await capture(p,size,'packages');
    const detail=await p.locator('.session-actions .exp-button').first().getAttribute('href');assert.ok(detail.startsWith('/packages/'));
    const prices=await p.locator('.session-price').allTextContents();assert.ok(prices.length>=3);
    await p.locator('.session-actions .exp-button').first().click();await p.waitForLoadState('networkidle');await capture(p,size,'package-detail');
    const enquiry=await p.locator('.detail-aside .exp-button').getAttribute('href');assert.ok(enquiry.startsWith('/contact')||enquiry.startsWith('/payment/checkout/'));
    report.interactions.push({size,packages:true,detail,enquiry,prices});
    await open(p,'/gallery');await capture(p,size,'gallery');
    const initialCount=await p.locator('.film-card').count();const videoLink=await p.locator('.film-art').first().getAttribute('href');
    const filterValue=await p.locator('#filter-style option').nth(1).getAttribute('value');await p.locator('#filter-style').selectOption(filterValue);
    await p.locator('.film-filters button').click();await p.waitForLoadState('networkidle');
    assert.ok(new URL(p.url()).searchParams.get('style')===filterValue);assert.ok(await p.locator('.film-card').count()>0);
    await p.locator('.active-filters a').click();await p.waitForLoadState('networkidle');assert.equal(await p.locator('.film-card').count(),initialCount);
    await open(p,videoLink);await capture(p,size,'video-detail');
    let embedRequested=false;
    await c.route('https://www.youtube-nocookie.com/embed/**',r=>{embedRequested=true;return r.fulfill({status:200,contentType:'text/html',body:'<title>Test film player</title>Player loaded on request'});});
    assert.equal(await p.locator('iframe').count(),0);await p.locator('[data-embed]').first().click();await until(p,()=>document.querySelector('iframe'));
    await p.waitForTimeout(100);assert.ok(embedRequested);assert.ok((await p.locator('iframe').getAttribute('title')).length>0);
    await p.route('**/api/video/*/like',r=>{assert.equal(r.request().method(),'POST');assert.ok(r.request().headers()['x-csrftoken']);return r.fulfill({status:200,contentType:'application/json',body:JSON.stringify({success:true,like_count:41})});});
    await p.locator('[data-like-url]').click();await until(p,()=>document.querySelector('[data-like-count]').textContent==='41');
    report.interactions.push({size,galleryFilter:true,clearFilter:true,embedOnDemand:true,csrfLike:true});
    report.violations.push(...await p.evaluate(()=>window.__csp));
    await open(p,'/testimonials');await capture(p,size,'testimonials');
    assert.ok(await p.locator('.review-card').count()>=3);await p.locator('.rating-details summary').click();assert.ok(await p.locator('meter').first().isVisible());
    report.interactions.push({size,testimonials:true,ratingDetails:true});
    await open(p,'/about');await capture(p,size,'about');
    await open(p,'/faq');await capture(p,size,'faq');
    assert.equal(await p.locator('[data-faq]').count(),13);await p.locator('[data-faq] summary').first().click();assert.ok(await p.locator('[data-faq]').first().getAttribute('open')!==null);
    await p.locator('#faq-search').fill('drone');assert.ok(await p.locator('[data-faq]:visible').count()>0);assert.ok(await p.locator('[data-faq]:visible').count()<13);
    await p.locator('#faq-search').fill('no-match-987');assert.ok(await p.locator('#faq-empty').isVisible());await p.locator('#faq-search').fill('');assert.equal(await p.locator('[data-faq]:visible').count(),13);
    await open(p,'/contact?subject=Session%20enquiry');await capture(p,size,'contact');
    assert.equal(await p.locator('#contact-subject').inputValue(),'Session enquiry');assert.ok(!await p.locator('#contact-draft').isVisible());
    await p.locator('#contact-name').fill('Demo Rider');await p.locator('#contact-email').fill('rider@example.test');await p.locator('#contact-message').fill('We would love a session in Bansko.');await p.locator('#contact-form button').click();
    assert.ok(await p.locator('#contact-draft').isVisible());const draft=await p.locator('#contact-draft').getAttribute('href');assert.ok(draft.startsWith('mailto:')&&draft.includes('rider%40example.test'));
    report.interactions.push({size,faqNativeToggle:true,faqSearch:true,emailDraft:true,draft});
    if(size.width<768){await p.locator('.alpine-menu summary').click();assert.ok(await p.locator('.alpine-menu-panel').isVisible());await p.locator('.alpine-menu-panel a[href="/gallery"]').click();await p.waitForLoadState('networkidle');assert.ok(p.url().endsWith('/gallery'));report.interactions.push({size,mobileNavigation:true});}
    await c.close();
    if(!production){
      const empty=await context(size);await empty.p.goto('http://127.0.0.1:5002/packages',{waitUntil:'networkidle'});assert.ok(await empty.p.locator('.ap-empty').isVisible());
      for(const name of ['packages','gallery','testimonials']){await empty.p.goto('http://127.0.0.1:5002/'+name,{waitUntil:'networkidle'});assert.ok(await empty.p.locator('.ap-empty').isVisible());await empty.p.screenshot({path:path.join(shots,`${size.width}x${size.height}-empty-${name}.png`),fullPage:true});report.empty.push({size,name,status:200});}await empty.c.close();
      const home=await context(size);await open(home.p,'/');await until(home.p,()=>window.__experience?.mode==='3d');assert.equal(await home.p.locator('#exp-canvas').getAttribute('aria-hidden'),'true');report.home.push({size,state:await home.p.evaluate(()=>window.__experience)});await home.p.screenshot({path:path.join(shots,`${size.width}x${size.height}-homepage.png`)});await home.c.close();
      const reduced=await context(size,{reducedMotion:'reduce'});await open(reduced.p,'/gallery');assert.ok(await reduced.p.locator('h1').isVisible());await reduced.c.close();
    }
  }
  assert.deepEqual(report.errors,[]);assert.deepEqual(report.failed,[]);assert.deepEqual(report.violations,[]);report.pass=true;
} catch(e){report.failure=e.stack;console.error(e.stack);process.exitCode=1;}
finally {await fs.writeFile(path.join(evidence,production?'csp-report.json':'browser-report.json'),JSON.stringify(report,null,2));await browser.close();}
