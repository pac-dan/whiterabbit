import * as T from '../../vendor/three.module.min.js?v=bansko-4';
export function placeholderRider() {
const group=new T.Group();group.name='Momentum rider';
const jacket=new T.MeshStandardMaterial({color:'#b8ccd6',roughness:.72});
const pants=new T.MeshStandardMaterial({color:'#142333',roughness:.9});
const black=new T.MeshStandardMaterial({color:'#07101e',roughness:.45});
const accent=new T.MeshStandardMaterial({color:'#00c5df',roughness:.4,metalness:.35});
const glass=new T.MeshStandardMaterial({color:'#76cbe0',metalness:.85,roughness:.18});
const mesh=(name,g,m,parent=group)=>{const o=new T.Mesh(g,m);o.name=name;parent.add(o);return o;};
const torso=mesh('Jacket',new T.CapsuleGeometry(.31,.48,3,7),jacket);torso.position.set(.07,1.5,0);torso.rotation.z=-.13;
const waist=mesh('Waist',new T.BoxGeometry(.48,.28,.72),pants);waist.position.set(0,1.03,0);
const head=new T.Group();head.name='Helmet pivot';head.position.set(.18,2.16,0);group.add(head);
mesh('Helmet',new T.SphereGeometry(.255,12,8),black,head).scale.set(1,.96,1.02);
const goggles=mesh('Goggles',new T.BoxGeometry(.13,.17,.42),glass,head);goggles.position.set(.235,.015,0);goggles.rotation.z=-.08;
const neck=mesh('Neck warmer',new T.CylinderGeometry(.15,.18,.2,8),black);neck.position.set(.13,1.96,0);
const zip=mesh('Jacket zip',new T.BoxGeometry(.025,.53,.025),accent);zip.position.set(.36,1.5,0);
const shape=new T.Shape();shape.moveTo(-.31,-.98);shape.quadraticCurveTo(-.3,-1.34,0,-1.36);shape.quadraticCurveTo(.3,-1.34,.31,-.98);shape.lineTo(.31,.98);shape.quadraticCurveTo(.3,1.34,0,1.36);shape.quadraticCurveTo(-.3,1.34,-.31,.98);shape.closePath();
const board=mesh('Snowboard',new T.ExtrudeGeometry(shape,{depth:.085,bevelEnabled:true,bevelSize:.025,bevelThickness:.025,bevelSegments:1,steps:1}),accent);board.rotation.x=-Math.PI/2;board.position.y=.11;
function limb(name,radius,material){return mesh(name,new T.CylinderGeometry(radius,radius*.85,1,7),material);}
function segment(o,a,b){o.position.copy(a).add(b).multiplyScalar(.5);o.scale.y=a.distanceTo(b);o.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),b.clone().sub(a).normalize());}
const legs=[-1,1].map(side=>{
const boot=mesh(side<0?'Rear boot':'Front boot',new T.BoxGeometry(.47,.21,.25),black);boot.position.set(.02,.26,side*.49);boot.rotation.y=side*.13;
const binding=mesh('Binding',new T.BoxGeometry(.52,.08,.31),pants);binding.position.set(.02,.17,side*.49);
const thigh=limb('Thigh',.15,pants),shin=limb('Shin',.125,pants);
const upper=limb('Jacket sleeve',.115,jacket),forearm=limb('Forearm',.095,jacket);
const glove=mesh('Glove',new T.SphereGeometry(.12,7,5),black);
return {side,boot,thigh,shin,upper,forearm,glove};
});
group.pose=({edge=0,compression=.5})=>{
const crouch=.18*compression;
torso.position.set(.08+Math.abs(edge)*.15,1.5-crouch,0);torso.rotation.z=-.16-edge*.25;
waist.position.y=1.03-crouch;head.position.set(.18,2.16-crouch,0);head.rotation.y=-edge*.35;neck.position.y=1.96-crouch;zip.position.y=1.5-crouch;
for(const l of legs){
const hip=new T.Vector3(0,1.05-crouch,l.side*.28),knee=new T.Vector3(.34+compression*.16,.65-crouch*.4,l.side*.42),ankle=l.boot.position.clone();ankle.y+=.07;
segment(l.thigh,hip,knee);segment(l.shin,knee,ankle);
const shoulder=new T.Vector3(.1,1.72-crouch,l.side*.33),elbow=new T.Vector3(.3,1.4-crouch,l.side*(.62+edge*.2)),hand=new T.Vector3(.55,1.34-crouch,l.side*.83);
segment(l.upper,shoulder,elbow);segment(l.forearm,elbow,hand);l.glove.position.copy(hand);
}
};
group.pose({});return group;
}
export async function createRider(scene,path,terrain,slots,config) {
const handle=await slots.model(config,placeholderRider),pivot=new T.Group(),content=new T.Group();
const box=new T.Box3().setFromObject(handle.object),centre=box.getCenter(new T.Vector3());
const fit=(config.height??2.5)/Math.max(.01,box.max.y-box.min.y)*(config.scale??1);
content.scale.setScalar(fit);handle.object.position.add(new T.Vector3(-centre.x,-box.min.y,-centre.z));content.add(handle.object);pivot.add(content);scene.add(pivot);
const board=handle.object.getObjectByName(config.board_node??'Snowboard'),contactPoint=new T.Vector3();let contactGap=0;
let frame=path.ride(0),last=-1;const bounds=new T.Box3();
return {pivot,handle,content,position:pivot.position,get frame(){return frame;},get contactGap(){return contactGap;},get bounds(){return bounds;},update(p) {
if(p===last)return;last=p;
frame=path.ride(path.rideProgress(p));
const basis=new T.Matrix4().makeBasis(frame.right,frame.normal,frame.forward);
pivot.position.copy(frame.position).addScaledVector(frame.normal,.09+Math.abs(Math.sin(frame.edge))*.3);
pivot.quaternion.setFromRotationMatrix(basis).multiply(new T.Quaternion().setFromAxisAngle(new T.Vector3(0,0,1),frame.edge));
pivot.visible=p>=.105&&p<.305;handle.update(p,{edge:frame.edge/.38,compression:frame.compression});handle.object.pose?.(frame);
pivot.updateMatrixWorld(true);
if(board?.geometry){
let clearance=Infinity;const points=board.geometry.attributes.position;
for(let i=0;i<points.count;i++){contactPoint.fromBufferAttribute(points,i).applyMatrix4(board.matrixWorld);clearance=Math.min(clearance,contactPoint.y-terrain.height(contactPoint.x,contactPoint.z));}
pivot.position.y+=.035-clearance;contactGap=.035;pivot.updateMatrixWorld(true);
}else contactGap=pivot.position.y-terrain.height(pivot.position.x,pivot.position.z);
bounds.setFromObject(pivot);
}};
}
