import * as T from '../../vendor/three.module.min.js?v=bansko-1';
export function createTown(scene,terrain) {
  const origin=terrain.geo(41.838,23.488),count=650;
  const geometry=new T.BufferGeometry(),positions=new Float32Array(count*3),sizes=new Float32Array(count);
  const houses=new T.InstancedMesh(new T.BoxGeometry(1.6,1.7,2),new T.MeshStandardMaterial({color:'#17253a',roughness:1}),200),matrix=new T.Matrix4();scene.add(houses);
  for(let i=0;i<count;i++){const a=i*2.39996,r=Math.sqrt(i/count)*130,x=origin.x+Math.cos(a)*r,z=origin.z+Math.sin(a)*r*.7;positions.set([x,terrain.height(x,z)+1.4,z],i*3);sizes[i]=i%7;if(i<200){matrix.makeTranslation(x,terrain.height(x,z)+.75,z);houses.setMatrixAt(i,matrix);}}
  geometry.setAttribute('position',new T.BufferAttribute(positions,3));geometry.setAttribute('phase',new T.BufferAttribute(sizes,1));
  const material=new T.ShaderMaterial({transparent:true,depthWrite:false,blending:T.AdditiveBlending,uniforms:{time:{value:0},alpha:{value:0}},vertexShader:'attribute float phase;varying float v;uniform float time;void main(){v=.7+.3*sin(time*.5+phase);vec4 mv=modelViewMatrix*vec4(position,1.);gl_Position=projectionMatrix*mv;gl_PointSize=clamp(330./-mv.z,1.,8.);}',fragmentShader:'varying float v;uniform float alpha;void main(){float d=length(gl_PointCoord-.5);gl_FragColor=vec4(1.,.6,.25,(1.-smoothstep(0.,.5,d))*v*alpha);}'});
  const lights=new T.Points(geometry,material);scene.add(lights);
  return {update(p){material.uniforms.time.value=performance.now()*.001;material.uniforms.alpha.value=T.MathUtils.smoothstep(p,.78,.91);houses.visible=p>.8;}};
}
