import fs from 'node:fs/promises';import path from 'node:path';import assert from 'node:assert/strict';
import {launch,until,root} from './refinement_browser.mjs';
const out=path.join(root,'.runs/2026-10-27-functional-site/evidence');const base='https://127.0.0.1:5003';
const result={pass:false,views:[],errors:[]};const browser=await launch();
try{for(const viewport of [{width:1440,height:900},{width:375,height:812}]){
 const c=await browser.newContext({viewport,ignoreHTTPSErrors:true}),p=await c.newPage();p.on('pageerror',e=>result.errors.push(e.message));p.on('console',e=>{if(e.type()==='error')result.errors.push(e.text());});
 await p.goto(base);await until(p,()=>window.__experience&&document.querySelector('#journey-video').readyState>=2);
 const navigate=async i=>{await p.locator(`[data-go-chapter="${i}"]`).click();await until(p,i=>Math.abs(scrollY-document.querySelector(`[data-chapter="${i}"]`).offsetTop)<2,i);await p.waitForTimeout(900);};
 await navigate(1);const descent=await p.locator('#journey-video').evaluate(v=>v.currentTime);
 await navigate(2);const town=await p.locator('#journey-video').evaluate(v=>v.currentTime);assert.ok(town>descent);
 await p.waitForTimeout(500);assert.ok(Math.abs(await p.locator('#journey-video').evaluate(v=>v.currentTime)-town)<.05);
 await navigate(0);assert.ok(await p.locator('#journey-video').evaluate(v=>v.currentTime)<descent);
 await navigate(3);await until(p,()=>window.__experience.galleryReady);await p.screenshot({path:path.join(out,'shots',`${viewport.width}-home-gallery.png`)});
 await p.locator('#play-selected-film').click();await until(p,()=>document.querySelector('#film-player video')?.currentTime>.1);await p.keyboard.press('Escape');
 await navigate(4);assert.ok(await p.getByRole('link',{name:/Mountain Session|Choose|Explore/}).count()>0);await p.screenshot({path:path.join(out,'shots',`${viewport.width}-home-packages.png`)});
 result.views.push({viewport,descent,town,forward:true,reverse:true,held:true,galleryPlayback:true,debug:await p.evaluate(()=>window.__experience)});await c.close();
}assert.deepEqual(result.errors,[]);result.pass=true;}catch(e){result.error=e.stack;process.exitCode=1;}finally{await browser.close();await fs.writeFile(path.join(out,'home-preservation.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));}
