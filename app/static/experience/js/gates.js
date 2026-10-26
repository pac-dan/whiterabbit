import * as T from '../../vendor/three.module.min.js?v=bansko-2';
export function createGates(scene,path,slots,data) {
  const group=new T.Group();scene.add(group);const handles=[];let loading=false;
  const faces=path.gates.map((v,i)=>{
    const gate=new T.Group();gate.position.copy(v);group.add(gate);
    const mat=new T.MeshBasicMaterial({color:i===1?'#8b5cf6':'#00d4ff'});
    for(const x of [-7.2,7.2]){const pole=new T.Mesh(new T.BoxGeometry(.32,27,.32),mat);pole.position.set(x,13,0);gate.add(pole);}
    const top=new T.Mesh(new T.BoxGeometry(14.7,.32,.32),mat);top.position.y=26.5;gate.add(top);
    const face=new T.Mesh(new T.PlaneGeometry(13,21),new T.MeshBasicMaterial({color:'#162945',side:T.DoubleSide}));face.position.y=14;gate.add(face);return face;
  });
  async function load(){if(loading)return;loading=true;await Promise.all(faces.map(async(f,i)=>{const h=await slots.load(data.media[i],`experience/placeholders/gate-${i+1}.webp`);handles[i]=h;f.material.map=h.texture;f.material.color.set('#ffffff');f.material.needsUpdate=true;}));}
  return {update(p){if(p>=.3&&p<=.88&&!loading)load().catch(()=>{});group.visible=p>=.53&&p<.79;const active=Math.min(2,Math.floor(T.MathUtils.clamp((p-.55)/.2,0,1)*3));handles.forEach((h,i)=>h.activate(group.visible&&active===i));}};
}
