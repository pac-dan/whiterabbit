import {createScroll,chapterAt} from './scroll.js?v=bansko-video-2';
import {createOverlay} from './overlay.js?v=bansko-video-2';
import {createDebug} from './debug.js?v=bansko-video-2';
import {createVideoClock,interpolate} from './video-clock.js?v=bansko-video-2';

const root=document.getElementById('experience'),data=JSON.parse(document.getElementById('experience-data').textContent);
const config=data.journey,video=document.getElementById('journey-video'),stage=document.getElementById('exp-stage');
const loader=document.getElementById('exp-loader'),canvas=document.getElementById('exp-canvas');
const url=path=>{if(/^(https?:|blob:|data:)/.test(path))return path;const p=path.startsWith('/')?path:root.dataset.assetBase+path;return `${p}${p.includes('?')?'&':'?'}v=${root.dataset.version}`;};
let runtime=null,generation=0,state={mode:'static',tier:0,fps:0,chapter:0,progress:0,drawCalls:0,frames:0,slots:{}};
const debug=createDebug(()=>state);
function stop(){
    generation++;runtime?.dispose();runtime=null;loader.hidden=true;
    document.body.classList.remove('exp-running','exp-ended','video-running','video-gallery-fallback');
    document.querySelectorAll('[data-chapter],[data-package]').forEach(el=>el.inert=false);
    state={...state,mode:'static',drawCalls:0};debug.update();
}
async function boot(){
    if(runtime)return;
    const id=++generation;
    document.body.classList.add('exp-running','video-running','video-gallery-fallback');
    const scroll=createScroll(document.getElementById('exp-track'));
    let ring={active:0,update(){},dispose(){}},engine=null,quality=null,slots=null,raf=0,frames=0,last=0,disposed=false,resizeGallery=()=>{};
    const clock=createVideoClock(video,config,status=>{
        root.dataset.mediaStatus=status;
        if(status==='error')console.warn('[Momentum journey] Video unavailable; keeping the poster and live content.');
    });
    const overlay=createOverlay(data,scroll,{get active(){return ring.active;}},null,null,()=>0);
    root.dataset.mediaStatus='loading';
    video.src=url(config.src);video.load();
    const timeout=setTimeout(()=>{if(!clock.state.ready){root.dataset.mediaStatus='poster';console.warn('[Momentum journey] Slow media; poster remains available.');}},6000);
    runtime={dispose(){disposed=true;clearTimeout(timeout);cancelAnimationFrame(raf);scroll.destroy();overlay.reset();
        clock.dispose();ring.dispose();slots?.dispose();engine?.dispose();removeEventListener('resize',resizeGallery);canvas.hidden=true;}};
    loader.hidden=true;
    const tick=time=>{
        if(disposed)return;raf=requestAnimationFrame(tick);scroll.update(time);
        const p=scroll.progress,chapter=chapterAt(p),end=document.querySelector('footer').getBoundingClientRect().top<innerHeight-80;
        root.dataset.journeyChapter=String(chapter);
        document.body.classList.toggle('exp-ended',end);
        root.style.setProperty('--journey-x',`${interpolate(config.framing,interpolate(config.cues,p))}%`);
        root.dataset.town=String(p>=.88);stage.style.setProperty('--gallery-shade',chapter===2?'1':'0');
        if(!document.hidden&&!end){
            clock.update(p,time);ring.update(p);overlay.update(p);
            if(chapter!==2)slots?.pause();
            if(engine){engine.setPaused(chapter!==2);canvas.hidden=chapter!==2;}
            const dt=last?time-last:16.67;last=time;frames++;
            if(quality?.sample(dt/1000)){engine?.resize();ring.setQuality?.(quality.tier);}
            state={mode:'video',progress:p,chapter,tier:quality?.tier??0,fps:quality?.fps??1000/dt,frames,drawCalls:chapter===2?(engine?.renderer.info.render.calls??0):0,
                ringIndex:ring.active,ringAngle:ring.group?.children[2]?.rotation.y??0,video:clock.state,slots:{ring:ring.cards?.filter(c=>c.handle&&!c.handle.isPlaceholder).length??0},firstFrameMs:state.firstFrameMs??time};
            debug.update();
        }
    };
    raf=requestAnimationFrame(tick);
    // Only the existing gallery uses WebGL. Terrain/rider/sky/snow/town never load.
    try{
        const probe=document.createElement('canvas'),gl=probe.getContext('webgl2');
        if(!gl)return;gl.getExtension('WEBGL_lose_context')?.loseContext();
        const [T,{createRenderer},{createRing},{createSlots},{createQuality}]=await Promise.all([
            import('../../vendor/three.module.min.js?v=bansko-video-2'),import('./renderer.js?v=bansko-video-2'),
            import('./ring.js?v=bansko-video-2'),import('./slots.js?v=bansko-video-2'),import('./quality.js?v=bansko-video-2')]);
        if(disposed||id!==generation)return;
        quality=createQuality();
        engine=createRenderer(canvas,quality,()=>{engine?.dispose();engine=null;canvas.hidden=true;document.body.classList.add('video-gallery-fallback');},true);
        engine.scene.add(new T.HemisphereLight('#b9dffa','#15213d',2));
        resizeGallery=()=>{if(engine){engine.camera.position.set(innerWidth<768?0:10,25,innerWidth<768?118:91);engine.camera.lookAt(0,15,0);}};
        resizeGallery();addEventListener('resize',resizeGallery);
        slots=createSlots(url,()=>{});ring=createRing(engine.scene,engine.camera,{shelf:new T.Vector3()},slots,data.ring);
        ring.setQuality(quality.tier);canvas.hidden=true;
        document.body.classList.remove('video-gallery-fallback');
        engine.start(()=>{},()=>{if(document.hidden)slots.pause();});
    }catch(error){console.warn('[Momentum journey] Gallery grid fallback:',error.message);}
}
document.getElementById('static-toggle').addEventListener('click',()=>{stop();scrollTo({top:0,behavior:'instant'});});
document.getElementById('play-descent').textContent='Play the descent';
document.getElementById('play-descent').addEventListener('click',()=>{scrollTo({top:0,behavior:'instant'});boot();});
document.querySelectorAll('[data-dismiss-flash]').forEach(b=>b.addEventListener('click',()=>b.closest('#flash-messages > div')?.remove()));
const motion=matchMedia('(prefers-reduced-motion: reduce)');motion.addEventListener('change',e=>{if(e.matches)stop();});
if(!motion.matches)boot();else stop();
addEventListener('pagehide',stop,{once:true});
