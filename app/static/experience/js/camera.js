import * as T from '../../vendor/three.module.min.js?v=bansko-2';
export function createCamera(camera,path,terrain) {
  const add=(v,x,y,z)=>v.clone().add(new T.Vector3(x,y,z));
  const s=path.shelf, g=path.gates, start=path.at(0), town=terrain.geo(41.838,23.488);
  const times=[0,.08,.12,.2,.29,.32,.42,.53,.56,.63,.7,.75,.82,.875,.9,1];
  const positions=[add(start,-155,140,180),add(start,-100,100,145),add(path.at(.03),-10,20,55),add(path.at(.2),-9,16,48),add(s,0,44,120),add(s,0,28,91),add(s,0,24,88),add(s,6,24,84),add(g[0],-24,25,70),add(g[1],-24,23,65),add(g[2],-24,24,65),add(path.at(.85),0,25,60),add(path.at(.88),0,14,18),add(town,0,18,40),add(town,-100,65,130),add(town,-95,48,110)];
  const targets=[add(start,50,-40,-250),add(start,50,-20,-160),path.at(.1,5),path.at(.3,4),add(s,0,16,0),add(s,0,17,0),add(s,0,16,0),add(s,0,16,0),add(g[0],0,12,0),add(g[1],0,12,0),add(g[2],0,12,0),path.at(.88,12),path.at(.92,9),add(town,0,6,-40),add(town,10,0,-50),add(town,0,4,-60)];
  const positionCurve=new T.CatmullRomCurve3(positions,false,'catmullrom',.3);
  const targetCurve=new T.CatmullRomCurve3(targets,false,'catmullrom',.3);
  return {update(p) {
    let i=times.findIndex((t,index)=>index<times.length-1&&p>=t&&p<=times[index+1]);if(i<0)i=times.length-2;
    const u=(i+(p-times[i])/(times[i+1]-times[i]))/(times.length-1);
    const pos=positionCurve.getPoint(T.MathUtils.clamp(u,0,1));
    if(camera.aspect<.8){const pull=T.MathUtils.smoothstep(p,.27,.32)*(1-T.MathUtils.smoothstep(p,.53,.57));pos.z+=70*pull;pos.y+=12*pull;}
    pos.y=Math.max(pos.y,terrain.height(pos.x,pos.z)+9);
    camera.position.copy(pos);camera.lookAt(targetCurve.getPoint(T.MathUtils.clamp(u,0,1)));
  }};
}
