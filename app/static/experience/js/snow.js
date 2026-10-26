import * as T from '../../vendor/three.module.min.js?v=bansko-3';
export function createSnow(scene,camera,quality,rider,path,terrain) {
const count=6000,a=new Float32Array(count*3);
for(let i=0;i<count;i++){a[i*3]=Math.sin(i*13.1)*155;a[i*3+1]=(i*17.71)%140;a[i*3+2]=Math.cos(i*4.7)*155;}
const g=new T.BufferGeometry();g.setAttribute('position',new T.BufferAttribute(a,3));
const pointMaterial=(size,alpha)=>new T.ShaderMaterial({transparent:true,depthWrite:false,uniforms:{size:{value:size},alpha:{value:alpha}},vertexShader:'uniform float size;void main(){vec4 v=modelViewMatrix*vec4(position,1.);gl_Position=projectionMatrix*v;gl_PointSize=clamp(size*500./-v.z,1.,12.);}',fragmentShader:'uniform float alpha;void main(){float d=length(gl_PointCoord-.5);gl_FragColor=vec4(.8,.94,1.,alpha*(1.-smoothstep(.12,.5,d)));}'});
const points=new T.Points(g,pointMaterial(.2,.48));scene.add(points);
const spray=new T.Points(new T.BufferGeometry(),pointMaterial(.12,.72));
const s=new Float32Array(240*3);spray.geometry.setAttribute('position',new T.BufferAttribute(s,3));scene.add(spray);
const trackPositions=new Float32Array(256*6),trackGeometry=new T.BufferGeometry();trackGeometry.setAttribute('position',new T.BufferAttribute(trackPositions,3));
const track=new T.LineSegments(trackGeometry,new T.LineBasicMaterial({color:'#58788e',transparent:true,opacity:.55}));scene.add(track);
const shadowGeometry=new T.CircleGeometry(1.25,24);shadowGeometry.rotateX(-Math.PI/2);
const shadow=new T.Mesh(shadowGeometry,new T.ShaderMaterial({transparent:true,depthWrite:false,vertexShader:'varying vec2 v;void main(){v=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'varying vec2 v;void main(){float d=length((v-.5)*2.);gl_FragColor=vec4(.02,.05,.09,.23*(1.-smoothstep(.08,1.,d)));}'}));scene.add(shadow);
let previous=-1;
return {spray,track,shadow,setQuality(){g.setDrawRange(0,quality.particles);spray.geometry.setDrawRange(0,quality.tier===1?80:240);},update(p) {
const time=performance.now()*.001;
points.position.set(camera.position.x,camera.position.y-45,camera.position.z);
for(let i=0;i<quality.particles;i++)a[i*3+1]=T.MathUtils.euclideanModulo(i*17.71-time*(1+i%4),140);
g.attributes.position.needsUpdate=true;g.setDrawRange(0,quality.particles);
spray.visible=shadow.visible=p>.12&&p<.3;track.visible=p>.12&&p<.32;
shadow.position.copy(rider.frame.position).addScaledVector(rider.frame.normal,.025);shadow.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),rider.frame.normal);
if(p===previous)return;previous=p;const q=path.rideProgress(p);
for(let i=0;i<240;i++){
const age=i/240,frame=path.ride(Math.max(0,q-age*.018)),side=Math.sign(frame.edge)||1;
const v=frame.position.clone().addScaledVector(frame.right,side*(.28+age*(.35+Math.abs(frame.edge)*3)));
v.addScaledVector(frame.normal,.12+Math.sin(age*Math.PI)*(.45+Math.abs(frame.edge)*2));v.addScaledVector(frame.forward,-age*.5);
v.x+=Math.sin(i*19.7)*age*.3;v.z+=Math.cos(i*12.1)*age*.3;v.toArray(s,i*3);
}
spray.geometry.attributes.position.needsUpdate=true;
for(let i=0;i<256;i++){
const frame=path.ride(i/255*q);
for(let side=0;side<2;side++){const v=frame.position.clone().addScaledVector(frame.right,(side-.5)*.44);v.y=terrain.height(v.x,v.z)+.035;v.toArray(trackPositions,i*6+side*3);}
}
const indices=[];for(let i=1;i<256;i++)for(let side=0;side<2;side++)indices.push((i-1)*2+side,i*2+side);
if(!trackGeometry.index)trackGeometry.setIndex(indices);
trackGeometry.attributes.position.needsUpdate=true;
spray.geometry.computeBoundingSphere();trackGeometry.computeBoundingSphere();
}};
}
