import * as T from '../../vendor/three.module.min.js?v=bansko-4';
export function createPortal(scene,path,slots,data) {
const group=new T.Group();group.position.copy(path.at(.91,16));scene.add(group);let handle=null,loading=false;
const direction=path.at(.97).sub(path.at(.86)).normalize();group.quaternion.setFromUnitVectors(new T.Vector3(0,0,-1),direction);
const material=new T.MeshBasicMaterial({color:'#40ddff',transparent:true,opacity:.18,side:T.DoubleSide,depthWrite:false});
const rings=[];
for(let i=0;i<9;i++){const m=new T.Mesh(new T.TorusGeometry(12,.12,5,64),material);m.position.z=-i*5;rings.push(m);group.add(m);}
const face=new T.Mesh(new T.PlaneGeometry(22,28),new T.MeshBasicMaterial({color:'#102843',transparent:true,opacity:.7,side:T.DoubleSide}));face.position.z=-43;group.add(face);
const geometry=new T.BufferGeometry(),positions=new Float32Array(1200*3),targets=new Float32Array(1200*3);
for(let i=0;i<1200;i++){const a=i*2.399963,r=11.5+Math.sin(i*17.3)*.65,z=-(i%9)*5;positions.set([Math.cos(a)*r,Math.sin(a)*r,z],i*3);const t=i/1199;targets.set([Math.cos(a+t*10)*(8+5*t),Math.sin(a+t*10)*(8+5*t),-t*55],i*3);}
geometry.setAttribute('position',new T.BufferAttribute(positions,3));geometry.setAttribute('target',new T.BufferAttribute(targets,3));
const shimmer=new T.ShaderMaterial({transparent:true,depthWrite:false,blending:T.AdditiveBlending,uniforms:{phase:{value:0},alpha:{value:0}},vertexShader:'attribute vec3 target;uniform float phase;varying float depth;void main(){vec3 p=mix(position,target,phase);vec4 v=modelViewMatrix*vec4(p,1.);depth=clamp(-p.z/55.,0.,1.);gl_Position=projectionMatrix*v;gl_PointSize=clamp(45./-v.z,1.,5.);}',fragmentShader:'varying float depth;uniform float alpha;void main(){float d=length(gl_PointCoord-.5);vec3 c=mix(vec3(0.,.83,1.),vec3(.55,.36,.96),depth);gl_FragColor=vec4(c,alpha*(1.-smoothstep(.05,.5,d)));}'});
const particles=new T.Points(geometry,shimmer);group.add(particles);geometry.computeBoundingSphere();
return {update(p){if(p>.55&&!loading){loading=true;slots.load(data.media,'experience/placeholders/portal.webp').then(h=>{handle=h;face.material.map=h.texture;face.material.color.set('#ffffff');face.material.needsUpdate=true;}).catch(()=>{});}
group.visible=p>.73&&p<.89;const t=T.MathUtils.clamp((p-.75)/.13,0,1);group.scale.setScalar(1+t*t*.8);material.opacity=.08+Math.sin(t*Math.PI)*.16;shimmer.uniforms.phase.value=t*t*(3-2*t);shimmer.uniforms.alpha.value=Math.sin(t*Math.PI)*.8;face.visible=!!data.media.src;handle?.activate(group.visible&&face.visible);
}};
}
