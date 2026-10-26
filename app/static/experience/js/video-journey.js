import {createDocumentScroll,clamp} from './scroll.js?v=bansko-films-2';
import {createVideoClock,interpolate} from './video-clock.js?v=bansko-films-2';
import {createDebug} from './debug.js?v=bansko-video-2';
import {createPageMotion} from './page-motion.js?v=bansko-films-2';
const root=document.getElementById('experience'),data=JSON.parse(document.getElementById('experience-data').textContent),config=data.journey;
const video=document.getElementById('journey-video'),poster=document.getElementById('journey-poster'),town=document.getElementById('town-poster');
const sections=[...document.querySelectorAll('[data-chapter]')],rail=[...document.querySelectorAll('[data-go-chapter]')];
const asset=path=>{if(/^(https?:|blob:|data:)/.test(path))return path;const p=path.startsWith('/')?path:root.dataset.assetBase+path;return `${p}${p.includes('?')?'&':'?'}v=${root.dataset.version}`;};
const motion=matchMedia('(prefers-reduced-motion: reduce)'),mobile=matchMedia('(max-width:767px)').matches;
let clock=null,scroll=null,gallery=null,loadingGallery=false,raf=0,frames=0,last=0,enabled=false,closed=false,loadTimer=0,generation=0;
let state={mode:'static',tier:0,fps:0,progress:0,chapter:0,frames:0,drawCalls:0,slots:{}};
const debug=createDebug(()=>state);
const smooth=x=>{x=clamp(x);return x*x*(3-2*x);};
const pageMotion=createPageMotion(root,()=>enabled&&!motion.matches);
function loadTown(){if(!town.src)town.src=town.dataset.src;const still=document.querySelector('.arrival-still');if(still&&!still.src)still.src=town.dataset.src;}
function start(){
 if(enabled)return;const token=++generation;enabled=true;root.dataset.mediaStatus='loading';document.body.classList.remove('flow-still');
 scroll?.destroy();scroll=createDocumentScroll(document.getElementById('exp-track'),sections,true);
 clock=createVideoClock(video,config,status=>{root.dataset.mediaStatus=status;if(status==='error')console.warn('[Momentum] Film unavailable; the poster and booking remain available.');});
 let begun=false;const begin=()=>{if(!enabled||token!==generation||begun)return;begun=true;video.src=asset(mobile&&config.mobile_src?config.mobile_src:config.src);video.load();
  loadTimer=setTimeout(()=>{if(video.readyState<2){root.dataset.mediaStatus='poster';console.warn('[Momentum] Slow film; showing the poster.');}},6000);};
 // Prioritize the single sharp opening image over motion and portfolio downloads.
 if(poster.complete)requestAnimationFrame(()=>requestAnimationFrame(begin));else {poster.addEventListener('load',begin,{once:true});poster.addEventListener('error',begin,{once:true});}
 document.getElementById('static-toggle').hidden=false;document.getElementById('play-descent').hidden=true;
}
function still(){generation++;enabled=false;clearTimeout(loadTimer);clock?.dispose();clock=null;root.dataset.frame='false';root.dataset.mediaStatus='poster';document.body.classList.add('flow-still');
 scroll?.destroy();scroll=createDocumentScroll(document.getElementById('exp-track'),sections,false);
 document.getElementById('static-toggle').hidden=true;document.getElementById('play-descent').hidden=false;loadTown();}
video.addEventListener('loadeddata',()=>{if(enabled){root.dataset.frame='true';root.dataset.mediaStatus='ready';}});
document.getElementById('static-toggle').addEventListener('click',()=>{still();scrollTo({top:0,behavior:'instant'});});
document.getElementById('play-descent').addEventListener('click',()=>{scrollTo({top:0,behavior:'instant'});start();});
motion.addEventListener('change',e=>{if(e.matches)still();});
async function bootGallery(){if(loadingGallery||gallery)return;loadingGallery=true;
 try{const {createFloatingGallery}=await import('./floating-gallery.js?v=bansko-films-2');if(!closed)gallery=createFloatingGallery(data.films.cards,asset);}catch(e){console.warn('[Momentum] Open the collection to watch films.',e.message);}}
const galleryObserver=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)){bootGallery();galleryObserver.disconnect();}},{rootMargin:'450px'});
galleryObserver.observe(document.getElementById('ring'));
if(motion.matches)still();else start();
function tick(time){if(closed)return;raf=requestAnimationFrame(tick);scroll.update(time);if(document.hidden)return;
 const p=scroll.filmProgress,chapter=scroll.chapter,arrival=smooth((p-.78)/.22),galleryTop=scroll.tops[3];
 root.dataset.flowChapter=String(chapter);root.dataset.town=String(p>=.98);
 root.style.setProperty('--journey-x',`${interpolate(config.framing,interpolate(config.cues,p))}%`);
 root.style.setProperty('--arrival',arrival);root.style.setProperty('--frame-top',`${64*(1-arrival)}px`);root.style.setProperty('--frame-height',`${53+47*arrival}svh`);
 root.style.setProperty('--stage-alpha',1-smooth((scrollY-galleryTop)/(innerHeight*.6)));
 if(p>.65)loadTown();if(clock)clock.update(p,time);pageMotion.update();gallery?.update(time,enabled&&!motion.matches);
 rail.forEach((b,i)=>b.setAttribute('aria-current',String(i===chapter)));
 document.getElementById('chapter-status').textContent=data.chapters[chapter].toUpperCase();document.getElementById('mainNav').classList.toggle('is-scrolled',scrollY>30);
 const dt=last?time-last:16.67;last=time;frames++;
 state={mode:enabled?'video':'static',flow:true,progress:scroll.progress,filmProgress:p,journeyRange:scroll.journeyRange,chapter,tier:0,fps:1000/dt,frames,drawCalls:0,
  video:clock?.state??{ready:false,paused:true},galleryReady:!!gallery,galleryIndex:gallery?.active??0,slots:{},firstFrameMs:state.firstFrameMs??time};debug.update();
}
raf=requestAnimationFrame(tick);
document.addEventListener('visibilitychange',()=>{if(document.hidden){video.pause();gallery?.pause();gallery?.update(0,false);pageMotion.update();}});
addEventListener('pagehide',event=>{video.pause();gallery?.pause();if(!event.persisted){closed=true;cancelAnimationFrame(raf);clearTimeout(loadTimer);scroll?.destroy();clock?.dispose();gallery?.dispose();galleryObserver.disconnect();pageMotion.dispose();}});
addEventListener('pageshow',()=>{last=0;});
