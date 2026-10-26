import * as T from '../../vendor/three.module.min.js?v=bansko-1';
// [latitude, longitude], Todorka / Shiligarnika down the ski corridor to Bansko.
export const RIDE_LINE = [[41.765,23.466],[41.772,23.463],[41.778,23.46],[41.784,23.455],[41.789,23.451],[41.794,23.45],[41.798,23.455],[41.803,23.459],[41.808,23.465],[41.814,23.471],[41.821,23.477],[41.829,23.484],[41.838,23.488]];
export function createPath(terrain) {
  const curve=new T.CatmullRomCurve3(RIDE_LINE.map(([lat,lon])=>terrain.geo(lat,lon)),false,'centripetal');
  const at=(t,lift=0)=>{const v=curve.getPoint(T.MathUtils.clamp(t,0,1));v.y=terrain.height(v.x,v.z)+lift;return v;};
  const shelf=at(.43);
  // Lift the compacted snow shelf above the tallest local patch.
  for(let i=0;i<24;i++){const a=i/24*Math.PI*2;shelf.y=Math.max(shelf.y,terrain.height(shelf.x+Math.sin(a)*55,shelf.z+Math.cos(a)*55));}
  shelf.y+=4;
  const gates=[.64,.72,.8].map(t=>at(t,4));
  return {curve,at,shelf,gates};
}
