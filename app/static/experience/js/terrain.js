import * as T from '../../vendor/three.module.min.js?v=bansko-1';
export async function createTerrain(scene, quality, url, loaded) {
  const response = await fetch(url('experience/terrain/bansko-height.json'));
  if (!response.ok) throw Error('Terrain metadata unavailable');
  const meta = await response.json(); loaded();
  const size = quality.tier === 1 ? 256 : 512;
  const bin = await fetch(url(`experience/terrain/bansko-height${size === 256 ? '-256' : ''}.bin`));
  if (!bin.ok) throw Error('Elevation unavailable');
  const data = new Uint16Array(await bin.arrayBuffer()); loaded();
  const width = meta.metresPerPixelX * 511 * .1, depth = meta.metresPerPixelY * 511 * .1;
  const clamp = T.MathUtils.clamp;
  function height(x,z) {
    const u=clamp((x/width+.5)*(size-1),0,size-1), v=clamp((z/depth+.5)*(size-1),0,size-1);
    const a=Math.floor(u), b=Math.floor(v), c=Math.min(a+1,size-1), d=Math.min(b+1,size-1);
    return (T.MathUtils.lerp(T.MathUtils.lerp(data[b*size+a],data[b*size+c],u-a),T.MathUtils.lerp(data[d*size+a],data[d*size+c],u-a),v-b)-meta.minM)*.145;
  }
  function geo(lat,lon,offset=0) {
    const x=((lon-meta.bbox[0])/(meta.bbox[2]-meta.bbox[0])-.5)*width;
    const z=((meta.bbox[3]-lat)/(meta.bbox[3]-meta.bbox[1])-.5)*depth;
    return new T.Vector3(x,height(x,z)+offset,z);
  }
  const material = new T.MeshStandardMaterial({vertexColors:true,roughness:.82,metalness:.08});
  function geometry() {
    const g=new T.PlaneGeometry(width,depth,quality.segments,quality.segments);
    g.rotateX(-Math.PI/2);
    const p=g.attributes.position;
    for(let i=0;i<p.count;i++) p.setY(i,height(p.getX(i),p.getZ(i)));
    g.computeVertexNormals();
    const colors=new Float32Array(p.count*3), col=new T.Color();
    for(let i=0;i<p.count;i++) {
      const slope=1-Math.abs(g.attributes.normal.getY(i));
      const grain=(Math.sin(p.getX(i)*2.3+p.getZ(i)*1.7)*.5+.5)*.045;
      col.setRGB(.68-slope*.7+grain,.79-slope*.68+grain,.9-slope*.63+grain);
      col.toArray(colors,i*3);
    }
    g.setAttribute('color',new T.BufferAttribute(colors,3)); return g;
  }
  const mesh=new T.Mesh(geometry(),material);scene.add(mesh);
  const horizon=new T.Group();scene.add(horizon);
  for(let i=0;i<18;i++) {
    const a=i/18*Math.PI*2;
    const ridge=new T.Mesh(new T.ConeGeometry(220+(i%4)*45,130+(i%5)*45,5),new T.MeshStandardMaterial({color:'#26394f',roughness:1}));
    ridge.position.set(Math.sin(a)*1000,10,Math.cos(a)*1030);horizon.add(ridge);
  }
  return {meta,width,depth,height,geo,mesh,update(){},setQuality(){const old=mesh.geometry;mesh.geometry=geometry();old.dispose();}};
}
