import * as T from '../../vendor/three.module.min.js?v=bansko-2';
export function createPortal(scene,path,slots,data) {
  const group=new T.Group();group.position.copy(path.at(.91,16));scene.add(group);let handle=null,loading=false;
  const material=new T.MeshBasicMaterial({color:'#40ddff',transparent:true,opacity:.5,side:T.DoubleSide});
  const rings=[];
  for(let i=0;i<9;i++){const m=new T.Mesh(new T.TorusGeometry(12,.12,5,64),material);m.position.z=-i*5;rings.push(m);group.add(m);}
  const face=new T.Mesh(new T.PlaneGeometry(22,28),new T.MeshBasicMaterial({color:'#102843',transparent:true,opacity:.7,side:T.DoubleSide}));face.position.z=-43;group.add(face);
  return {update(p){if(p>.55&&!loading){loading=true;slots.load(data.media,'experience/placeholders/portal.webp').then(h=>{handle=h;face.material.map=h.texture;face.material.color.set('#ffffff');face.material.needsUpdate=true;}).catch(()=>{});}
    group.visible=p>.73&&p<.89;const t=T.MathUtils.clamp((p-.75)/.13,0,1);group.scale.setScalar(1+t*t*1.8);material.opacity=.25+Math.sin(t*Math.PI)*.5;handle?.activate(group.visible);
  }};
}
