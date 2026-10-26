import * as T from '../../vendor/three.module.min.js?v=bansko-2';
export function createSnow(scene,camera,quality,rider) {
  const count=6000,a=new Float32Array(count*3);
  for(let i=0;i<count;i++){a[i*3]=Math.sin(i*13.1)*155;a[i*3+1]=(i*17.71)%140;a[i*3+2]=Math.cos(i*4.7)*155;}
  const g=new T.BufferGeometry();g.setAttribute('position',new T.BufferAttribute(a,3));
  const m=new T.PointsMaterial({color:'#dcefff',size:.2,transparent:true,opacity:.5,depthWrite:false});
  const points=new T.Points(g,m);scene.add(points);
  const spray=new T.Points(new T.BufferGeometry(),new T.PointsMaterial({color:'#e8f9ff',size:.18,transparent:true,opacity:.75,depthWrite:false}));
  const s=new Float32Array(180*3);spray.geometry.setAttribute('position',new T.BufferAttribute(s,3));scene.add(spray);
  return {setQuality(){g.setDrawRange(0,quality.particles);m.size=quality.tier===1?.28:.2;},update(p,dt){
    const time=performance.now()*.001;
    points.position.set(camera.position.x,camera.position.y-45,camera.position.z);
    for(let i=0;i<quality.particles;i++)a[i*3+1]=(i*17.71-time*(1+i%4))%140;
    g.attributes.position.needsUpdate=true;g.setDrawRange(0,quality.particles);
    spray.visible=p>.12&&p<.3;spray.position.copy(rider.position);
    for(let i=0;i<180;i++){const age=((i/180+time*.6)%1);s[i*3]=Math.sin(i*6.2)*age*6;s[i*3+1]=Math.sin(age*Math.PI)*2;s[i*3+2]=age*9;}
    spray.geometry.attributes.position.needsUpdate=true;
  }};
}
