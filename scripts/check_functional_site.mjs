import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {launch,root,views,until} from './refinement_browser.mjs';
const out=path.join(root,'.runs/2026-10-27-functional-site/evidence');
await fs.mkdir(path.join(out,'shots'),{recursive:true});
const fixture=JSON.parse(await fs.readFile(path.join(out,'browser-fixture.json'),'utf8'));
const report={pass:false,base:fixture.base,providerScope:fixture.note,views:[],errors:[],network:[],csp:[]};
const browser=await launch();
try{
 for(const [i,viewport] of views.entries()){
  const context=await browser.newContext({viewport,ignoreHTTPSErrors:true,reducedMotion:'reduce'});
  await context.addInitScript(()=>{window.__csp=[];addEventListener('securitypolicyviolation',e=>window.__csp.push({directive:e.violatedDirective,uri:e.blockedURI}));});
  const page=await context.newPage();
  page.on('pageerror',e=>report.errors.push(e.message));
  page.on('console',e=>{if(e.type()==='error')report.errors.push(e.text());});
  page.on('requestfailed',r=>{if(!r.failure()?.errorText.includes('ERR_ABORTED'))report.network.push({url:r.url(),error:r.failure()?.errorText});});
  page.on('response',r=>{if(r.status()>=400)report.network.push({url:r.url(),status:r.status()});});
  const item={viewport,pages:[],actions:[]};report.views.push(item);
  async function visit(route,shot){
   const response=await page.goto(fixture.base+route,{waitUntil:'networkidle'});assert.equal(response.status(),200,route);
   assert.match(response.headers()['content-security-policy'],/script-src[^;]*nonce-/);
   assert.equal(await page.locator('h1').count(),1,route);
   assert.equal(await page.evaluate(()=>document.compatMode),'CSS1Compat','Standards-mode HTML '+route);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),true,'horizontal overflow '+route);
   assert.equal(await page.evaluate(()=>{const n=document.querySelector('.workflow-nav'),h=document.querySelector('h1');return !n||n.getBoundingClientRect().bottom<=h.getBoundingClientRect().top;}),true,'Admin menu/title overlap '+route);
   report.csp.push(...await page.evaluate(()=>window.__csp));item.pages.push({route,status:response.status()});
   if(shot)await page.screenshot({path:path.join(out,'shots',`${viewport.width}-${shot}.png`),fullPage:true});
  }
  for(const route of ['/packages','/packages/1','/gallery','/gallery/1','/about','/faq','/testimonials','/contact','/auth/login'])await visit(route,route==='/packages'?'packages':route==='/auth/login'?'login':null);
  await visit('/packages/1');await page.getByRole('link',{name:'Book this session',exact:true}).click();await page.waitForURL('**/contact?subject=*');
  assert.match(await page.locator('#flash-messages').innerText(),/Online payment is unavailable/);item.actions.push('Unconfigured payment goes to honest contact fallback');
  await page.locator('[name=name]').fill('Browser Rider '+i);await page.locator('[name=email]').first().fill(`browser${i}@example.test`);await page.locator('[name=subject]').fill('Browser fixture '+i);await page.locator('[name=message]').fill('Please arrange a filming session. Isolated browser verification.');
  await page.getByRole('button',{name:'Send your message'}).click();await page.waitForURL('**/contact');assert.match(await page.locator('#flash-messages').innerText(),/message is saved/);item.actions.push('Contact submitted with CSRF');
  await visit(fixture.waivers[i],'waiver');await page.locator('[name=email]').first().fill(`browser${i}@example.test`);await page.locator('[name=legal_name_typed]').fill('Browser Rider '+i);await page.locator('[name=agree_to_terms]').check();await page.getByRole('button',{name:'Sign waiver'}).click();await page.waitForURL('**/payment/book-time/**');
  assert.match(await page.locator('main, .workflow-shell').first().innerText(),/arranged directly/);await page.getByRole('link',{name:'View payment & waiver receipt'}).click();await page.waitForURL('**/payment/complete/**');assert.match(await page.locator('.workflow-shell').innerText(),/still needs confirmation/);await page.screenshot({path:path.join(out,'shots',`${viewport.width}-receipt.png`),fullPage:true});item.actions.push('Seeded paid order signs waiver and shows honest scheduling/receipt');
  await visit('/auth/login');await page.locator('[name=email]').first().fill('qa@example.test');await page.locator('[name=password]').fill('local-browser-only-123');await page.getByRole('button',{name:/^Sign in/}).click();await page.waitForURL('**/admin/');item.actions.push('Actual administrator login');
  for(const route of ['/admin/','/admin/packages','/admin/packages/1/edit','/admin/videos','/admin/videos/1/edit','/admin/testimonials','/admin/testimonials/new','/admin/bookings','/admin/bookings/'+(i+1),'/admin/users','/admin/users/1','/admin/waivers','/admin/inquiries','/admin/subscribers','/admin/social'])await visit(route,route==='/admin/'?'admin':route==='/admin/packages/1/edit'?'package-edit':null);
  await visit('/admin/packages/new');await page.locator('[name=name]').fill('Browser package '+i);await page.locator('textarea[name=description]').fill('Isolated browser fixture session');await page.locator('[name=price]').fill('178.90');await page.locator('[name=duration]').fill('3');await page.getByRole('button',{name:'Save package'}).click();await page.waitForURL('**/admin/packages');
  const row=page.locator('tr').filter({hasText:'Browser package '+i});assert.equal(await row.count(),1);await row.getByRole('link',{name:'Edit',exact:true}).click();await page.locator('[name=is_active]').uncheck();await page.getByRole('button',{name:'Save package'}).click();await page.waitForURL('**/admin/packages');assert.match(await page.locator('tr').filter({hasText:'Browser package '+i}).innerText(),/Hidden/);item.actions.push('Create package and unpublish persisted');
  await visit('/admin/bookings/'+(i+1));await page.locator('[name=status]').selectOption('scheduled');await page.locator('[name=scheduled_at]').fill('2027-01-15T10:00');await page.locator('[name=admin_notes]').fill('Confirmed by local QA fixture');await page.getByRole('button',{name:'Save details'}).click();await page.waitForLoadState('networkidle');assert.match(await page.locator('.workflow-shell').innerText(),/scheduled/);item.actions.push('Confirmed booking date saved');
  await page.locator('[name=video_links]').fill('https://example.test/local-film.mp4');await page.getByRole('button',{name:'Send films'}).click();await page.waitForLoadState('networkidle');assert.match(await page.locator('.workflow-shell').innerText(),/completed/);item.actions.push('Delivery with SMTP suppressed (no email sent)');
  await visit('/admin/inquiries');const inquiry=page.locator('.workflow-panel').filter({has:page.getByRole('heading',{name:'Browser fixture '+i,exact:true})});await inquiry.locator('[name=resolved]').check();await inquiry.getByRole('button',{name:'Update enquiry'}).click();await page.waitForLoadState('networkidle');item.actions.push('Enquiry resolved');
  await visit('/');assert.equal(await page.locator('h1').isVisible(),true);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),true);item.actions.push('Homepage reduced-motion HTML retained');
  await context.close();
 }
 assert.deepEqual(report.errors,[]);assert.deepEqual(report.network,[]);assert.deepEqual(report.csp,[]);report.pass=true;
}catch(error){report.failure=error.stack;process.exitCode=1;}finally{await browser.close();await fs.writeFile(path.join(out,'browser.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({pass:report.pass,views:report.views.length,failure:report.failure,errors:report.errors,network:report.network,csp:report.csp},null,2));}
