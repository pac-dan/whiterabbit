export function createDebug(read) {
Object.defineProperty(window,'__experience',{configurable:true,get:()=>Object.freeze({...read(),slots:Object.freeze({...read().slots})})});
let panel=null;
if(new URLSearchParams(location.search).get('debug')==='1') {panel=document.createElement('output');panel.className='exp-debug';panel.setAttribute('aria-label','Experience diagnostics');document.body.append(panel);}
let last=0;
return {update(){if(panel&&performance.now()-last>250){const s=read();panel.textContent=`M / C — ENGINE\nFPS       ${s.fps.toFixed(1)}\nPROGRESS  ${s.progress.toFixed(3)}\nCHAPTER   ${s.chapter+1}\nTIER      ${s.tier}\nDRAWS     ${s.drawCalls}`;last=performance.now();}},dispose(){panel?.remove();}};
}
