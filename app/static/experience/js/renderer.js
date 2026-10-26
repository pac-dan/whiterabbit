import * as T from '../../vendor/three.module.min.js?v=bansko-3';
export function createRenderer(canvas,quality,onFailure) {
const renderer=new T.WebGLRenderer({canvas,antialias:quality.tier>=2,powerPreference:'high-performance',alpha:false});
renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.08;
const scene=new T.Scene(),camera=new T.PerspectiveCamera(53,innerWidth/innerHeight,.25,5000);
let running=true,visible=true,paused=false,raf=0,last=0,rendered=0;
function resize(){renderer.setPixelRatio(quality.dpr);renderer.setSize(innerWidth,innerHeight,false);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();}
resize();addEventListener('resize',resize);
function visibility(){last=0;quality.reset();}
document.addEventListener('visibilitychange',visibility);
canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();onFailure(Error('WebGL context lost'));});
const observer=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;last=0;quality.reset();});observer.observe(canvas);
return {renderer,scene,camera,resize,setPaused(value){paused=value;last=0;quality.reset();},get frames(){return rendered;},start(update,beforeFrame=()=>{}){
const tick=time=>{if(!running)return;raf=requestAnimationFrame(tick);beforeFrame(time);if(document.hidden||!visible||paused)return;
const dt=last?Math.min((time-last)/1000,.5):1/60;last=time;
try{update(time,dt);renderer.render(scene,camera);rendered++;}catch(e){onFailure(e);}
};raf=requestAnimationFrame(tick);
},dispose(){running=false;cancelAnimationFrame(raf);observer.disconnect();removeEventListener('resize',resize);document.removeEventListener('visibilitychange',visibility);scene.traverse(o=>{o.geometry?.dispose();if(o.material){const mats=Array.isArray(o.material)?o.material:[o.material];mats.forEach(m=>m.dispose());}});renderer.dispose();}};
}
