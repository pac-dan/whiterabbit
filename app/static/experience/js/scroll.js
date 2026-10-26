import Lenis from '../../vendor/lenis.mjs?v=bansko-video-2';
export const CHAPTERS=[0,.12,.30,.55,.75,.88,1];
export const clamp=x=>Math.max(0,Math.min(1,x));
export const chapterAt=p=>Math.min(5,CHAPTERS.findIndex((v,i)=>i<6&&p>=v&&p<CHAPTERS[i+1]) < 0 ? 5 : CHAPTERS.findIndex((v,i)=>i<6&&p>=v&&p<CHAPTERS[i+1]));
export function createScroll(track) {
const lenis=new Lenis({duration:1.05,smoothWheel:true,syncTouch:false});
let progress=0,range=1;
const measure=()=>range=Math.max(1,track.offsetHeight-innerHeight);
const read=()=>{progress=clamp((scrollY-track.offsetTop)/range);};
addEventListener('resize',measure);addEventListener('scroll',read,{passive:true});measure();read();
const buttons=[...document.querySelectorAll('[data-go-chapter]')];
const go=i=>lenis.scrollTo(track.offsetTop+Math.min(.99,CHAPTERS[i]+.035)*range);
const listeners=[];
const listen=(el,type,fn)=>{el.addEventListener(type,fn);listeners.push(()=>el.removeEventListener(type,fn));};
buttons.forEach(b=>listen(b,'click',()=>go(Number(b.dataset.goChapter))));
document.querySelectorAll('a[href="#drop"]').forEach(a=>listen(a,'click',e=>{e.preventDefault();go(1);}));
return {get progress(){return progress;},get range(){return range;},chapterProgress:i=>clamp((progress-CHAPTERS[i])/(CHAPTERS[i+1]-CHAPTERS[i])),
update(time){lenis.raf(time);read();},destroy(){listeners.forEach(off=>off());lenis.destroy();removeEventListener('resize',measure);removeEventListener('scroll',read);},reset:measure};
}
// Natural-flow homepage. Chapter anchors come from rendered layout, so enlarged
// text and stacked mobile packages do not leave navigation pointing at old ranges.
export function createDocumentScroll(track,sections,smooth=true){
const lenis=smooth?new Lenis({duration:1.05,smoothWheel:true,syncTouch:false}):null;
let tops=[],range=1;
const measure=()=>{tops=sections.map(el=>el.getBoundingClientRect().top+scrollY);range=Math.max(1,track.offsetHeight-innerHeight);};
const observer=new ResizeObserver(measure);observer.observe(track);addEventListener('resize',measure);measure();
const go=i=>{const y=tops[i];if(lenis)lenis.scrollTo(y);else scrollTo({top:y,behavior:'instant'});};
const handlers=[];const listen=(el,fn)=>{el.addEventListener('click',fn);handlers.push(()=>el.removeEventListener('click',fn));};
document.querySelectorAll('[data-go-chapter]').forEach(b=>listen(b,()=>go(Number(b.dataset.goChapter))));
document.querySelectorAll('a[href="#drop"]').forEach(a=>listen(a,e=>{e.preventDefault();go(1);}));
return {get progress(){return clamp((scrollY-track.offsetTop)/range);},get chapter(){let i=0;tops.forEach((y,n)=>{if(y<=scrollY+innerHeight*.28)i=n;});return i;},get journeyRange(){return tops[2]-tops[0];},get filmProgress(){return clamp((scrollY-tops[0])/(tops[2]-tops[0]));},get tops(){return tops;},update(time){lenis?.raf(time);},destroy(){lenis?.destroy();observer.disconnect();removeEventListener('resize',measure);handlers.forEach(fn=>fn());}};
}
