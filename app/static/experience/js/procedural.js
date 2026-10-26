import {createQuality} from './quality.js?v=bansko-video-2';
import {chapterAt,createScroll} from './scroll.js?v=bansko-video-2';
import {createDebug} from './debug.js?v=bansko-video-2';
const root=document.getElementById('experience'),loader=document.getElementById('exp-loader');
const data=JSON.parse(document.getElementById('experience-data').textContent);
const url=path=>{if(/^(https?:|blob:|data:)/.test(path))return path;const p=path.startsWith('/')?path:root.dataset.assetBase+path;return `${p}${p.includes('?')?'&':'?'}v=${root.dataset.version}`;};
let runtime=null,booting=false,state={mode:'static',tier:0,fps:0,chapter:0,progress:0,drawCalls:0,frames:0,slots:{}};
const debug=createDebug(()=>state);
function fallback(error) {
if(error)console.warn('[Momentum descent] Static view:',error.message);
runtime?.dispose();runtime=null;booting=false;loader.hidden=true;
document.body.classList.remove('exp-running','exp-ended');
document.querySelectorAll('[data-chapter],[data-package]').forEach(s=>s.inert=false);
state={...state,mode:'static',drawCalls:0};debug.update();
}
async function boot() {
if(booting||runtime)return;booting=true;loader.hidden=false;
let abandoned=false,engine=null,slots=null,scroll=null,overlay=null,ring=null;
const timer=setTimeout(()=>{abandoned=true;fallback(Error('Loading exceeded six seconds'));},6000);
const dispose=()=>{engine?.dispose();scroll?.destroy();overlay?.reset();ring?.dispose();slots?.dispose();};
try {
const probe=document.createElement('canvas');
const gl=probe.getContext('webgl2');if(!gl)throw Error('WebGL 2 is unavailable');gl.getExtension('WEBGL_lose_context')?.loseContext();
const [T,{createRenderer},{createTerrain},{createPath},{createCamera},{createSky},{createSnow},{createRider},{createRing},{createGates},{createPortal},{createTown},{createSlots},{createOverlay}]=await Promise.all([
import('../../vendor/three.module.min.js?v=bansko-video-2'),import('./renderer.js?v=bansko-video-2'),import('./terrain.js?v=bansko-video-2'),import('./path.js?v=bansko-video-2'),import('./camera.js?v=bansko-video-2'),import('./sky.js?v=bansko-video-2'),import('./snow.js?v=bansko-video-2'),import('./rider.js?v=bansko-video-2'),import('./ring.js?v=bansko-video-2'),import('./gates.js?v=bansko-video-2'),import('./portal.js?v=bansko-video-2'),import('./town.js?v=bansko-video-2'),import('./slots.js?v=bansko-video-2'),import('./overlay.js?v=bansko-video-2')]);
if(abandoned)return;
const quality=createQuality();engine=createRenderer(document.getElementById('exp-canvas'),quality,fallback);
let completed=0;const loaded=()=>{document.getElementById('asset-progress').value=++completed/3;};
slots=createSlots(url,()=>{});
const terrain=await createTerrain(engine.scene,quality,url,loaded);
const path=createPath(terrain),camera=createCamera(engine.camera,path,terrain),sky=createSky(engine.scene);
const rider=await createRider(engine.scene,path,terrain,slots,data.rider);
ring=createRing(engine.scene,engine.camera,path,slots,data.ring);
const gates=createGates(engine.scene,path,slots,data.gates),portal=createPortal(engine.scene,path,slots,data.portal),town=createTown(engine.scene,terrain),snow=createSnow(engine.scene,engine.camera,quality,rider,path,terrain);
const beatPanels=data.beats.map(()=>new T.Mesh(new T.PlaneGeometry(8,14),new T.MeshBasicMaterial({color:'#193248',side:T.DoubleSide})));
beatPanels.forEach(m=>engine.scene.add(m));let beatHandles=[],beatsLoading=false,heroHandle=null,heroLoading=false;
const initial=await slots.load({},'experience/placeholders/ring-01.webp');initial.dispose();loaded();
if(abandoned){dispose();return;}
document.body.classList.add('exp-running');
scroll=createScroll(document.getElementById('exp-track'));overlay=createOverlay(data,scroll,ring,terrain,engine.camera);
ring.setQuality(quality.tier);snow.setQuality();
const pauseMedia=()=>{if(document.hidden)slots.pause();};document.addEventListener('visibilitychange',pauseMedia);
let footerPaused=false;
const footerScroll=()=>{const end=document.querySelector('footer').getBoundingClientRect().top<innerHeight-80;document.body.classList.toggle('exp-ended',end);if(end!==footerPaused){footerPaused=end;engine.setPaused(end);if(end)slots.pause();}};
addEventListener('scroll',footerScroll,{passive:true});
runtime={dispose(){document.removeEventListener('visibilitychange',pauseMedia);removeEventListener('scroll',footerScroll);dispose();}};
engine.start((time,dt)=>{
const p=scroll.progress;
[camera,terrain,sky,rider,ring,gates,portal,town,snow].forEach(m=>m.update(p,dt));overlay.update(p);
if(quality.sample(dt)){engine.resize();terrain.setQuality();ring.setQuality(quality.tier);snow.setQuality();}
if(p<.55&&!beatsLoading){beatsLoading=true;Promise.all(data.beats.map((b,i)=>slots.load(b.media,`experience/placeholders/beat-${i+1}.webp`))).then(h=>{beatHandles=h;h.forEach((v,i)=>{beatPanels[i].material.map=v.texture;beatPanels[i].material.color.set('#ffffff');beatPanels[i].material.needsUpdate=true;});}).catch(()=>{});}
const beat=Math.min(2,Math.floor(scroll.chapterProgress(1)*3));
beatPanels.forEach((m,i)=>{m.visible=p>.12&&p<.3&&beat===i&&!!data.beats[i].media.src;m.position.copy(rider.position).addScaledVector(rider.frame.right,5).addScaledVector(rider.frame.normal,3);m.scale.setScalar(.25);m.lookAt(engine.camera.position);beatHandles[i]?.activate(m.visible);});
if(data.hero.background_video.src&&!heroLoading&&p<.3){heroLoading=true;slots.load(data.hero.background_video,'experience/placeholders/portal.webp').then(h=>{heroHandle=h;if(h.video){h.video.className='exp-hero-video';if(data.hero.background_video.poster)h.video.poster=url(data.hero.background_video.poster);document.getElementById('exp-stage').append(h.video);}}).catch(()=>{});}
if(heroHandle){heroHandle.activate(p<.12);if(heroHandle.video)heroHandle.video.hidden=p>=.12;}
const bounds=rider.bounds,min=new T.Vector3(Infinity,Infinity,Infinity),max=new T.Vector3(-Infinity,-Infinity,-Infinity);
engine.camera.updateMatrixWorld();
for(let i=0;i<8;i++){const v=new T.Vector3(i&1?bounds.max.x:bounds.min.x,i&2?bounds.max.y:bounds.min.y,i&4?bounds.max.z:bounds.min.z).project(engine.camera);min.min(v);max.max(v);}
state={mode:'3d',tier:quality.tier,fps:quality.fps,progress:p,chapter:chapterAt(p),drawCalls:engine.renderer.info.render.calls,frames:engine.frames,ringIndex:ring.active,ringAngle:ring.group.children[2]?.rotation.y??0,rider:{visible:rider.pivot.visible,position:rider.position.toArray(),quaternion:rider.pivot.quaternion.toArray(),edge:rider.frame.edge,compression:rider.frame.compression,contactGap:rider.contactGap,bounds:{left:(min.x+1)/2,right:(max.x+1)/2,top:(1-max.y)/2,bottom:(1-min.y)/2}},slots:{rider:!rider.handle.isPlaceholder,ring:ring.cards.filter(c=>c.handle&&!c.handle.isPlaceholder).length,beats:beatHandles.filter(h=>!h.isPlaceholder).length},firstFrameMs:state.firstFrameMs??performance.now()};debug.update();
},time=>scroll.update(time));
clearTimeout(timer);loader.hidden=true;booting=false;
} catch(error){clearTimeout(timer);dispose();fallback(error);}
}
document.getElementById('play-descent').addEventListener('click',()=>{scrollTo({top:0,behavior:'instant'});boot();});
document.getElementById('static-toggle').addEventListener('click',()=>{fallback();scrollTo({top:0,behavior:'instant'});});
document.querySelectorAll('[data-dismiss-flash]').forEach(b=>b.addEventListener('click',()=>b.closest('#flash-messages > div')?.remove()));
const motion=matchMedia('(prefers-reduced-motion: reduce)');motion.addEventListener('change',e=>{if(e.matches)fallback();});
if(!motion.matches)boot();else fallback();
addEventListener('pagehide',()=>runtime?.dispose(),{once:true});
