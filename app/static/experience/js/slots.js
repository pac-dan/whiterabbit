import * as T from '../../vendor/three.module.min.js?v=bansko-video-2';
export function createSlots(url,loaded=()=>{}) {
const handles=new Set(),loader=new T.TextureLoader();let disposed=false;
async function image(path) {const t=await loader.loadAsync(url(path));t.colorSpace=T.SRGBColorSpace;t.anisotropy=2;return t;}
async function load(slot={},placeholder) {
let texture,video=null,isPlaceholder=true,kind='image';
try {
if(slot.src && slot.type==='video') {
video=document.createElement('video');video.muted=true;video.loop=true;video.playsInline=true;video.preload='metadata';video.crossOrigin='anonymous';
await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Video timeout')),4500);video.onloadeddata=()=>{clearTimeout(timer);resolve();};video.onerror=()=>{clearTimeout(timer);reject(Error('Video unavailable'));};video.src=url(slot.src);video.load();});
texture=new T.VideoTexture(video);texture.colorSpace=T.SRGBColorSpace;isPlaceholder=false;kind='video';
} else if(slot.src) {texture=await image(slot.src);isPlaceholder=false;}
} catch {if(video){video.pause();video.removeAttribute('src');video.load();video=null;}}
if(!texture) texture=await image(placeholder);
if(disposed){texture.dispose();if(video){video.pause();video.removeAttribute('src');video.load();}throw Error('Slot loader disposed');}
loaded();
let active=false;
const handle={texture,video,isPlaceholder,kind,activate(show){
if(!video || show===active)return;active=show;
if(show) video.play().catch(()=>{});else video.pause();
},dispose(){texture.dispose();if(video){video.pause();video.removeAttribute('src');video.load();video.remove();}handles.delete(handle);}};
handles.add(handle);return handle;
}
async function model(slot,factory) {
let object,mixer=null,isPlaceholder=true;const poses={};
try{
if(slot.src){const {GLTFLoader}=await import('../../vendor/GLTFLoader.js?v=bansko-video-2');const gltf=await new GLTFLoader().loadAsync(url(slot.src));object=gltf.scene;object.scale.setScalar(slot.scale??1);isPlaceholder=false;
if(gltf.animations.length){mixer=new T.AnimationMixer(object);const clip=gltf.animations.find(a=>a.name===slot.animation)||gltf.animations[0];
if(slot.poses){for(const key of ['neutral','toe','heel']){const pose=gltf.animations.find(a=>a.name===slot.poses[key]);if(pose)poses[key]=mixer.clipAction(pose).play();}}
if(!poses.neutral||!poses.toe||!poses.heel){Object.keys(poses).forEach(k=>{poses[k].stop();delete poses[k];});mixer.clipAction(clip).play();}}}
}catch{/* A broken replacement always resolves to the named placeholder. */}
if(!object)object=factory();
const handle={object,isPlaceholder,kind:'model',update(p,pose={}){if(poses.neutral){const edge=T.MathUtils.clamp(pose.edge??0,-1,1);poses.neutral.setEffectiveWeight(1-Math.abs(edge));poses.toe.setEffectiveWeight(Math.max(0,edge));poses.heel.setEffectiveWeight(Math.max(0,-edge));}mixer?.setTime(p*30);},dispose(){mixer?.stopAllAction();mixer?.uncacheRoot(object);object.traverse(o=>{o.geometry?.dispose();if(o.material){(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>{Object.values(m).forEach(v=>{if(v?.isTexture)v.dispose();});m.dispose();});}});object.removeFromParent();handles.delete(handle);}};
if(disposed){handle.dispose();throw Error('Slot loader disposed');}handles.add(handle);return handle;
}
return {load,model,pause(){handles.forEach(h=>h.activate?.(false));},dispose(){disposed=true;[...handles].forEach(h=>h.dispose());}};
}
