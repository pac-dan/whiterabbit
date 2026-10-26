import * as T from '../../vendor/three.module.min.js?v=bansko-video-1';
export const RIDE_LINE = [[41.765,23.466],[41.772,23.463],[41.778,23.46],[41.784,23.455],[41.789,23.451],[41.794,23.45],[41.798,23.455],[41.803,23.459],[41.808,23.465],[41.814,23.471],[41.821,23.477],[41.829,23.484],[41.838,23.488]];
export function createPath(terrain) {
const curve=new T.CatmullRomCurve3(RIDE_LINE.map(([lat,lon])=>terrain.geo(lat,lon)),false,'centripetal');
const at=(t,lift=0)=>{const v=curve.getPointAt(T.MathUtils.clamp(t,0,1));v.y=terrain.height(v.x,v.z)+lift;return v;};
function ride(q) {
q=T.MathUtils.clamp(q,0,1);
const point=u=>{
const t=T.MathUtils.clamp(u,0,1)*.43,v=at(t);
const heading=at(Math.min(1,t+.001)).sub(at(Math.max(0,t-.001)));heading.y=0;heading.normalize();
const side=new T.Vector3(heading.z,0,-heading.x);
v.addScaledVector(side,Math.sin(u*Math.PI*6)*Math.sin(u*Math.PI)*2.4);
v.y=terrain.height(v.x,v.z);return v;
};
const position=point(q),forward=point(Math.min(1,q+.001)).sub(point(Math.max(0,q-.001))).normalize();
const normal=terrain.normal(position.x,position.z),right=new T.Vector3().crossVectors(normal,forward).normalize();
forward.crossVectors(right,normal).normalize();
return {position,forward,normal,right,edge:-Math.sin(q*Math.PI*6)*Math.sin(q*Math.PI)*.38,compression:.5+.5*Math.cos(q*Math.PI*12)};
}
const rideProgress=p=>T.MathUtils.clamp((p-.12)/.18,0,1);
const shelf=at(.43);
for(let i=0;i<24;i++){const a=i/24*Math.PI*2;shelf.y=Math.max(shelf.y,terrain.height(shelf.x+Math.sin(a)*55,shelf.z+Math.cos(a)*55));}
shelf.y+=4;
const gates=[.64,.72,.8].map(t=>at(t,4));
return {curve,at,ride,rideProgress,shelf,gates};
}
