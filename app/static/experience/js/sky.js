import * as T from '../../vendor/three.module.min.js?v=bansko-2';
export function createSky(scene) {
  const mat=new T.ShaderMaterial({side:T.BackSide,depthWrite:false,uniforms:{night:{value:0}},vertexShader:'varying vec3 v; void main(){v=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'varying vec3 v;uniform float night;void main(){float h=normalize(v).y;vec3 c=mix(vec3(.17,.24,.36),vec3(.012,.025,.065),smoothstep(-.1,.8,h));c=mix(c,c*.4,night);gl_FragColor=vec4(c,1.);}' });
  const dome=new T.Mesh(new T.SphereGeometry(2800,24,16),mat);scene.add(dome);
  const ambient=new T.HemisphereLight('#d5eaff','#1b2345',2.1);scene.add(ambient);
  const sun=new T.DirectionalLight('#d1c9ff',3.1);sun.position.set(-350,260,-200);scene.add(sun);
  scene.fog=new T.FogExp2('#23334b',.0011);
  const clouds=new T.Group();scene.add(clouds);
  const cg=new T.PlaneGeometry(200,28), cm=new T.MeshBasicMaterial({color:'#b9d3ed',transparent:true,opacity:.025,depthWrite:false,side:T.DoubleSide});
  for(let i=0;i<9;i++){const m=new T.Mesh(cg,cm);m.position.set((i%3-1)*210,190+(i%4)*12,(i-4)*130);m.rotation.x=-Math.PI/2;clouds.add(m);}
  return {update(p,dt){const n=T.MathUtils.smoothstep(p,.76,.96);mat.uniforms.night.value=n;ambient.intensity=2.1-n*.85;sun.intensity=3.1-n*1.8;scene.fog.color.set('#23334b').lerp(new T.Color('#080f25'),n);clouds.position.x=Math.sin(performance.now()*.00003)*12;}};
}
