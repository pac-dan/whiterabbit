import fs from 'node:fs/promises';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {launch,until,base,out,views,save} from './refinement_browser.mjs';
const browser=await launch(),report={revision:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),clips:[],pass:false};
try{for(const viewport of [views[0],views[3]]){
 const context=await browser.newContext({viewport,recordVideo:{dir:path.join(out,'recordings'),size:viewport}}),page=await context.newPage();
 await page.goto(base);await until(page,()=>window.__experience?.video.ready);await page.waitForTimeout(1500);
 const range=await page.evaluate(()=>window.__experience.journeyRange);
 for(let i=0;i<=100;i++){await page.evaluate(y=>scrollTo({top:y,behavior:'instant'}),range*i/100);await page.waitForTimeout(60);}
 await page.waitForTimeout(1200);
 for(const i of [3,4,5,3,2,0]){await page.locator(`[data-go-chapter="${i}"]`).click();await until(page,i=>Math.abs(scrollY-document.querySelector(`[data-chapter="${i}"]`).offsetTop)<.1,i);await page.waitForTimeout(500);}
 const state=await page.evaluate(()=>window.__experience);if(state.video.current>.06||!state.video.paused)throw Error('Recording did not return to held opening');
 const video=page.video();await context.close();const destination=path.join(out,`${viewport.width}-refinement-scroll.webm`);await video.saveAs(destination);report.clips.push({viewport,file:destination,bytes:(await fs.stat(destination)).size,state});
}report.pass=true;}catch(e){report.failure=e.stack;process.exitCode=1;}finally{await browser.close();await save('recordings.json',report);console.log(JSON.stringify(report,null,2));}
