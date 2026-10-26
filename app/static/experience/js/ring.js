import * as T from '../../vendor/three.module.min.js?v=bansko-video-2';
export function createRing(scene,camera,path,slots,data) {
const group=new T.Group();group.position.copy(path.shelf);scene.add(group);
const floor=new T.Mesh(new T.CylinderGeometry(56,60,2,64),new T.MeshStandardMaterial({color:'#0a172a',metalness:.72,roughness:.24}));floor.position.y=-1;group.add(floor);
const edge=new T.Mesh(new T.TorusGeometry(55,.07,4,96),new T.MeshBasicMaterial({color:'#276179',transparent:true,opacity:.4}));edge.rotation.x=Math.PI/2;edge.position.y=.05;group.add(edge);
const pivot=new T.Group();group.add(pivot);
const cards=[],meshes=[],reflections=[];let ready=false,loading=false,active=0,hovered=false;
const geometry=new T.PlaneGeometry(12,21);
const maskCanvas=document.createElement('canvas');maskCanvas.width=128;maskCanvas.height=224;const ctx=maskCanvas.getContext('2d');ctx.fillStyle='black';ctx.fillRect(0,0,128,224);ctx.fillStyle='white';ctx.beginPath();ctx.roundRect(0,0,128,224,7);ctx.fill();const mask=new T.CanvasTexture(maskCanvas);
for(let i=0;i<data.cards.length;i++) {
const a=i/data.cards.length*Math.PI*2,card=new T.Group();card.position.set(Math.sin(a)*37,13,Math.cos(a)*37);card.rotation.y=a;
const face=new T.Mesh(geometry,new T.MeshBasicMaterial({color:'#193248',alphaMap:mask,transparent:true,side:T.DoubleSide}));card.add(face);face.userData.index=i;meshes.push(face);
const rim=new T.Mesh(new T.PlaneGeometry(14,23),new T.ShaderMaterial({transparent:true,depthWrite:false,side:T.DoubleSide,blending:T.AdditiveBlending,uniforms:{color:{value:new T.Color(i%2?'#8b5cf6':'#00d4ff')},strength:{value:.5}},vertexShader:'varying vec2 v;void main(){v=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'varying vec2 v;uniform vec3 color;uniform float strength;void main(){vec2 q=abs((v-.5)*vec2(14.,23.))-vec2(5.7,10.2);float d=length(max(q,0.))+min(max(q.x,q.y),0.)-.35;float line=exp(-abs(d)*18.);float halo=exp(-abs(d)*2.3)*.22;gl_FragColor=vec4(color,(line+halo)*strength);}'}));rim.position.z=.025;card.add(rim);
const mirror=new T.Mesh(geometry,new T.ShaderMaterial({transparent:true,depthWrite:false,side:T.DoubleSide,uniforms:{map:{value:null},strength:{value:.2}},vertexShader:'varying vec2 v;void main(){v=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'uniform sampler2D map;uniform float strength;varying vec2 v;void main(){vec2 uv=vec2(v.x,1.-v.y);vec4 c=texture2D(map,uv);float edge=smoothstep(0.,.12,v.x)*smoothstep(0.,.12,1.-v.x);gl_FragColor=vec4(c.rgb,strength*(1.-v.y)*(1.-v.y)*edge);}'}));mirror.position.set(Math.sin(a)*48,.09,Math.cos(a)*48);mirror.rotation.set(-Math.PI/2,0,-a);reflections.push(mirror);pivot.add(mirror);
cards.push({card,face,rim,angle:a,handle:null,prominence:0});pivot.add(card);
}
async function load() {
if(loading)return;loading=true;
await Promise.all(cards.map(async(c,i)=>{c.handle=await slots.load(data.cards[i].media,data.cards[i].placeholder);c.face.material.map=c.handle.texture;c.face.material.needsUpdate=true;reflections[i].material.uniforms.map.value=c.handle.texture;}));ready=true;
}
const raycaster=new T.Raycaster(),pointer=new T.Vector2();
function hit(e){pointer.set(e.clientX/innerWidth*2-1,1-e.clientY/innerHeight*2);raycaster.setFromCamera(pointer,camera);return raycaster.intersectObjects(meshes).find(h=>h.object.userData.index===active);}
const canvas=document.getElementById('exp-canvas');
const move=e=>{hovered=group.visible&&!!hit(e);canvas.style.cursor=hovered?'pointer':'';};
const click=e=>{if(group.visible&&hit(e))location.assign(data.cards[active].link);};
canvas.addEventListener('pointermove',move);canvas.addEventListener('click',click);
return {get active(){return active;},get ready(){return ready;},group,cards,load,
update(p){if(p>=.12&&p<=.75&&!loading)load().catch(()=>{});group.visible=p>=.25&&p<.59;
const t=T.MathUtils.clamp((p-.30)/.25,0,1),turn=t*(data.cards.length-1);pivot.rotation.y=-turn/data.cards.length*Math.PI*2;active=Math.round(turn)%data.cards.length;
cards.forEach((c,i)=>{
const front=Math.pow(Math.max(0,Math.cos(c.angle+pivot.rotation.y)),7);c.prominence=front;
c.card.position.y=13+front*1.1+(i===active&&hovered?.65:0);c.card.scale.setScalar(.82+front*.3+(i===active&&hovered?.025:0));
c.face.material.color.setScalar(.24+front*.76);c.rim.material.uniforms.strength.value=.13+front*.72;
reflections[i].material.uniforms.strength.value=.05+front*.3;reflections[i].scale.setScalar(c.card.scale.x);
c.handle?.activate(group.visible&&i===active);
});
if(!group.visible)canvas.style.cursor='';
},setQuality(tier){reflections.forEach(m=>m.visible=tier>=2);},dispose(){canvas.removeEventListener('pointermove',move);canvas.removeEventListener('click',click);mask.dispose();}};
}
