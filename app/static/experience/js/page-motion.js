// Progressive enhancement: HTML is readable before JS and in every motion mode.
export function createPageMotion(root, allowed=()=>true){
 const preference=matchMedia('(prefers-reduced-motion: reduce)'),visible=new Set(),animations=new Map();
 const nodes=[...root.querySelectorAll('.flow-section-head,.flow-package,.flow-close>div,.flow-review,.session-card,.film-card,.review-card,.story-image,.ap-section-head,.ap-process article,.ap-closing,.detail-section,.ap-value')];
 let enabled=false;
 const observer=new IntersectionObserver(entries=>{for(const e of entries){
  if(e.isIntersecting){visible.add(e.target);if(enabled){animations.get(e.target)?.cancel();const a=e.target.animate([{opacity:.72,translate:'0 26px'},{opacity:1,translate:'0 0'}],{duration:800,delay:Math.min(160,Number(e.target.dataset.motionOrder)*55),easing:'cubic-bezier(.2,.7,.2,1)'});animations.set(e.target,a);}}
  else visible.delete(e.target);
 }},{threshold:.08});
 nodes.forEach((el,i)=>{el.dataset.motionOrder=i%3;observer.observe(el);});
 function update(){const next=allowed()&&!preference.matches&&!document.hidden;
  if(next!==enabled){enabled=next;root.classList.toggle('motion-enabled',enabled);if(!enabled){animations.forEach(a=>a.cancel());nodes.forEach(el=>el.style.setProperty('--image-shift','0px'));}}
  if(!enabled)return;
  const positions=[...visible].map(el=>[el,el.getBoundingClientRect()]);
  positions.forEach(([el,r])=>el.style.setProperty('--image-shift',`${Math.max(-12,Math.min(12,(innerHeight/2-r.top-r.height/2)*.035))}px`));
 }
 update();
 return {update,dispose(){observer.disconnect();animations.forEach(a=>a.cancel());root.classList.remove('motion-enabled');}};
}
