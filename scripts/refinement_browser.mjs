import fs from 'node:fs/promises';
import {existsSync,readdirSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
export const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
export const run=process.env.REFINEMENT_RUN?path.resolve(process.env.REFINEMENT_RUN):path.join(root,'.runs/2026-10-26-homepage-refinement');
export const out=path.join(run,'evidence');
export const base=process.env.REFINEMENT_BASE||'http://127.0.0.1:5000';
export const views=[{width:1440,height:900},{width:1366,height:768},{width:390,height:844},{width:375,height:812}];
let pw;try{pw=await import('playwright');}catch{
 const cache=path.join(process.env.LOCALAPPDATA,'npm-cache/_npx');
 pw=await import(pathToFileURL(readdirSync(cache).map(x=>path.join(cache,x,'node_modules/playwright/index.mjs')).find(existsSync)));
}
export const launch=()=>pw.chromium.launch({channel:'chrome',headless:true,args:['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist']});
export async function until(page,fn,arg,ms=20000){const end=Date.now()+ms;while(Date.now()<end){try{if(await page.evaluate(fn,arg))return;}catch(e){if(!e.message.includes('Execution context was destroyed'))throw e;}await page.waitForTimeout(50);}throw Error('Timed out: '+fn.toString());}
export async function save(name,data){await fs.mkdir(out,{recursive:true});await fs.writeFile(path.join(out,name),JSON.stringify(data,null,2));}
export async function scroll(page,y){await page.evaluate(y=>scrollTo({top:y,behavior:'instant'}),y);await page.waitForTimeout(180);}
export async function shot(page,phase,name){await fs.mkdir(path.join(out,phase),{recursive:true});await page.screenshot({path:path.join(out,phase,name)});}
