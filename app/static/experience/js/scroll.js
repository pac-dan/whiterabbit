import Lenis from '../../vendor/lenis.mjs?v=bansko-3';
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
buttons.forEach(b=>b.addEventListener('click',()=>go(Number(b.dataset.goChapter))));
document.querySelectorAll('a[href="#drop"]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();go(1);}));
return {get progress(){return progress;},get range(){return range;},chapterProgress:i=>clamp((progress-CHAPTERS[i])/(CHAPTERS[i+1]-CHAPTERS[i])),
update(time){lenis.raf(time);read();},destroy(){lenis.destroy();removeEventListener('resize',measure);removeEventListener('scroll',read);},reset:measure};
}
