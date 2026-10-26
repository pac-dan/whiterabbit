import * as T from '../../vendor/three.module.min.js?v=bansko-4';
export function createCamera(camera,path,terrain) {
const add=(v,x,y,z)=>v.clone().add(new T.Vector3(x,y,z));
const s=path.shelf, g=path.gates, start=path.at(0), town=terrain.geo(41.838,23.488);
const times=[0,.08,.12,.2,.29,.32,.42,.53,.56,.63,.7,.75,.82,.875,.9,1];
const positions=[add(start,-155,140,180),add(start,-100,100,145),add(path.at(.03),-10,20,55),add(path.at(.2),-9,16,48),add(s,0,44,120),add(s,0,28,91),add(s,0,24,88),add(s,6,24,84),add(g[0],-24,25,70),add(g[1],-24,23,65),add(g[2],-24,24,65),add(path.at(.85),0,25,60),add(path.at(.88),0,14,18),add(town,0,18,40),add(town,-100,65,130),add(town,-95,48,110)];
const targets=[add(start,50,-40,-250),add(start,50,-20,-160),path.at(.1,5),path.at(.3,4),add(s,0,16,0),add(s,0,17,0),add(s,0,16,0),add(s,0,16,0),add(g[0],0,12,0),add(g[1],0,12,0),add(g[2],0,12,0),path.at(.88,12),path.at(.92,9),add(town,0,6,-40),add(town,10,0,-50),add(town,0,4,-60)];
const positionCurve=new T.CatmullRomCurve3(positions,false,'catmullrom',.3);
const targetCurve=new T.CatmullRomCurve3(targets,false,'catmullrom',.3);
let last=-1,width=0,height=0;
return {update(p) {
if(p===last&&width===innerWidth&&height===innerHeight)return;last=p;width=innerWidth;height=innerHeight;
let i=times.findIndex((t,index)=>index<times.length-1&&p>=t&&p<=times[index+1]);if(i<0)i=times.length-2;
const u=(i+(p-times[i])/(times[i+1]-times[i]))/(times.length-1);
const pos=positionCurve.getPoint(T.MathUtils.clamp(u,0,1));
const target=targetCurve.getPoint(T.MathUtils.clamp(u,0,1));
const portrait=camera.aspect<.8;
const ring=T.MathUtils.smoothstep(p,.285,.32)*(1-T.MathUtils.smoothstep(p,.53,.57));
pos.lerp(add(s,0,25,portrait?118:91),ring);target.lerp(add(s,0,15,0),ring);
pos.y=Math.max(pos.y,terrain.height(pos.x,pos.z)+9);
const follow=T.MathUtils.smoothstep(p,.095,.12)*(1-T.MathUtils.smoothstep(p,.28,.305));
const ride=path.ride(path.rideProgress(p));
const chase=ride.position.clone().addScaledVector(ride.forward,-(portrait?13:14)).addScaledVector(ride.normal,5.5);
chase.y=Math.max(chase.y,terrain.height(chase.x,chase.z)+1.4);
pos.lerp(chase,follow);target.lerp(ride.position.clone().addScaledVector(ride.normal,1.3),follow);
const gates=T.MathUtils.smoothstep(p,.53,.555)*(1-T.MathUtils.smoothstep(p,.74,.765));
const step=T.MathUtils.clamp((p-.55)*15,0,2),index=Math.floor(step),gate=g[index].clone().lerp(g[Math.min(2,index+1)],T.MathUtils.smoothstep(step-index,.72,1));
pos.lerp(add(gate,-15,24,portrait?100:80),gates);target.lerp(add(gate,0,13,0),gates);
const anchorX=portrait?.5:.73,anchorY=portrait?.31:.47;
camera.setViewOffset(innerWidth,innerHeight,innerWidth*((.5-anchorX)*follow+(.5-(portrait?.85:.74))*gates),innerHeight*((.5-anchorY)*follow+.04*gates),innerWidth,innerHeight);
camera.position.copy(pos);camera.lookAt(target);
}};
}
