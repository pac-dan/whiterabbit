import * as T from '../../vendor/three.module.min.js?v=bansko-1';
// Each returned handle owns its resources, including its fallback texture.
export function createSlots(url,loaded=()=>{}) {
  const handles=new Set(),loader=new T.TextureLoader();
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
    loaded();
    let active=false;
    const handle={texture,video,isPlaceholder,kind,activate(show){
      if(!video || show===active)return;active=show;
      if(show) video.play().catch(()=>{});else video.pause();
    },dispose(){texture.dispose();if(video){video.pause();video.removeAttribute('src');video.load();video.remove();}handles.delete(handle);}};
    handles.add(handle);return handle;
  }
  async function model(slot,factory) {
    let object,mixer=null,isPlaceholder=true;
    try{
      if(slot.src){const {GLTFLoader}=await import('../../vendor/GLTFLoader.js?v=bansko-1');const gltf=await new GLTFLoader().loadAsync(url(slot.src));object=gltf.scene;object.scale.setScalar(slot.scale??1);isPlaceholder=false;
        if(gltf.animations.length){mixer=new T.AnimationMixer(object);const clip=gltf.animations.find(a=>a.name===slot.animation)||gltf.animations[0];mixer.clipAction(clip).play();}}
    }catch{/* A broken replacement always resolves to the named placeholder. */}
    if(!object)object=factory();
    const handle={object,isPlaceholder,kind:'model',update(p){mixer?.setTime(p*30);},dispose(){mixer?.stopAllAction();mixer?.uncacheRoot(object);object.traverse(o=>{o.geometry?.dispose();if(o.material){(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>{Object.values(m).forEach(v=>{if(v?.isTexture)v.dispose();});m.dispose();});}});object.removeFromParent();handles.delete(handle);}};
    handles.add(handle);return handle;
  }
  return {load,model,dispose(){[...handles].forEach(h=>h.dispose());}};
}
