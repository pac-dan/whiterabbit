import * as T from '../../vendor/three.module.min.js?v=bansko-2';
export function placeholderRider() {
  const group=new T.Group();
  const body=new T.Mesh(new T.BoxGeometry(1.05,1.6,.7),new T.MeshStandardMaterial({color:'#a7b8d6',roughness:.55}));body.position.set(.25,1.5,0);body.rotation.z=-.28;group.add(body);
  const head=new T.Mesh(new T.IcosahedronGeometry(.43,1),new T.MeshStandardMaterial({color:'#091629',metalness:.6,roughness:.3}));head.position.set(.48,2.65,.1);group.add(head);
  const board=new T.Mesh(new T.BoxGeometry(3.25,.16,.82),new T.MeshStandardMaterial({color:'#00d4ff',emissive:'#003344',metalness:.5}));board.position.y=.12;board.rotation.y=.15;group.add(board);
  return group;
}
export async function createRider(scene,path,terrain,slots,config) {
  const handle=await slots.model(config,placeholderRider),pivot=new T.Group();pivot.add(handle.object);scene.add(pivot);
  return {pivot,handle,position:pivot.position,update(p) {
    const t=T.MathUtils.clamp((p-.12)/.18*.43,0,.43),v=path.at(t,.25),ahead=path.at(Math.min(1,t+.006));
    const behind=path.at(Math.max(0,t-.006));
    const yaw=Math.atan2(ahead.x-v.x,ahead.z-v.z),previous=Math.atan2(v.x-behind.x,v.z-behind.z);
    const curvature=Math.atan2(Math.sin(yaw-previous),Math.cos(yaw-previous));
    pivot.position.copy(v);pivot.rotation.set(0,yaw,T.MathUtils.clamp(curvature*2,-.32,.32));
    pivot.visible=p>=.105&&p<.305;handle.update(p);
  }};
}
