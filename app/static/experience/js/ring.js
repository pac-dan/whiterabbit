import * as T from '../../vendor/three.module.min.js?v=bansko-2';
export function createRing(scene,camera,path,slots,data) {
  const group=new T.Group();group.position.copy(path.shelf);scene.add(group);
  const floor=new T.Mesh(new T.CylinderGeometry(56,60,2,64),new T.MeshStandardMaterial({color:'#18364d',metalness:.65,roughness:.22}));floor.position.y=-1;group.add(floor);
  const edge=new T.Mesh(new T.TorusGeometry(55,.11,4,96),new T.MeshBasicMaterial({color:'#398199',transparent:true,opacity:.5}));edge.rotation.x=Math.PI/2;edge.position.y=.05;group.add(edge);
  const pivot=new T.Group();group.add(pivot);
  const cards=[],meshes=[],reflections=[];let ready=false,loading=false,active=0,hovered=false;
  const geometry=new T.PlaneGeometry(12,21);
  for(let i=0;i<data.cards.length;i++) {
    const a=i/data.cards.length*Math.PI*2,card=new T.Group();card.position.set(Math.sin(a)*37,13,Math.cos(a)*37);card.rotation.y=a;
    const face=new T.Mesh(geometry,new T.MeshBasicMaterial({color:'#193248',side:T.DoubleSide}));card.add(face);face.userData.index=i;meshes.push(face);
    const rim=new T.LineLoop(new T.BufferGeometry().setFromPoints([new T.Vector3(-6.2,-10.7,0),new T.Vector3(6.2,-10.7,0),new T.Vector3(6.2,10.7,0),new T.Vector3(-6.2,10.7,0)]),new T.LineBasicMaterial({color:i%2?'#8b5cf6':'#00d4ff'}));card.add(rim);
    const glow=new T.Mesh(new T.PlaneGeometry(14.4,23.4),new T.MeshBasicMaterial({color:i%2?'#8b5cf6':'#00d4ff',transparent:true,opacity:.055,blending:T.AdditiveBlending,depthWrite:false,side:T.DoubleSide}));glow.position.z=-.12;card.add(glow);
    const mirror=new T.Mesh(geometry,new T.ShaderMaterial({transparent:true,depthWrite:false,side:T.DoubleSide,uniforms:{map:{value:null}},vertexShader:'varying vec2 v;void main(){v=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'uniform sampler2D map;varying vec2 v;void main(){vec4 c=texture2D(map,vec2(v.x,1.-v.y));gl_FragColor=vec4(c.rgb, .28*(1.-v.y)*(1.-v.y));}'}));mirror.position.set(Math.sin(a)*48,.08,Math.cos(a)*48);mirror.rotation.set(-Math.PI/2,0,-a);reflections.push(mirror);pivot.add(mirror);
    cards.push({card,face,rim,handle:null});pivot.add(card);
  }
  async function load() {
    if(loading)return;loading=true;
    await Promise.all(cards.map(async(c,i)=>{c.handle=await slots.load(data.cards[i].media,data.cards[i].placeholder);c.face.material.map=c.handle.texture;c.face.material.color.set('#ffffff');c.face.material.needsUpdate=true;reflections[i].material.uniforms.map.value=c.handle.texture;}));ready=true;
  }
  const raycaster=new T.Raycaster(),pointer=new T.Vector2();
  function hit(e) {pointer.set(e.clientX/innerWidth*2-1,1-e.clientY/innerHeight*2);raycaster.setFromCamera(pointer,camera);return raycaster.intersectObjects(meshes).find(h=>h.object.userData.index===active);}
  const move=e=>{hovered=group.visible&&!!hit(e);document.getElementById('exp-canvas').style.cursor=hovered?'pointer':'';};
  const click=e=>{if(group.visible&&hit(e))location.assign(data.cards[active].link);};
  const canvas=document.getElementById('exp-canvas');canvas.addEventListener('pointermove',move);canvas.addEventListener('click',click);
  return {get active(){return active;},get ready(){return ready;},group,cards,load,
    update(p){if(p>=.12&&p<=.75&&!loading)load().catch(()=>{});group.visible=p>=.25&&p<.59;
      const t=T.MathUtils.clamp((p-.30)/.25,0,1);const turn=t*(data.cards.length-1);pivot.rotation.y=-turn/data.cards.length*Math.PI*2;active=Math.round(turn)%data.cards.length;
      cards.forEach((c,i)=>{c.card.position.y=13+(i===active&&hovered?1.3:0);c.card.scale.setScalar(i===active?1.045:1);c.handle?.activate(group.visible&&i===active);});
    },setQuality(tier){reflections.forEach(m=>m.visible=tier>=2);},dispose(){canvas.removeEventListener('pointermove',move);canvas.removeEventListener('click',click);}};
}
