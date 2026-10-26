// CSS perspective keeps films as accessible DOM controls; no WebGL floor/renderer.
export function createFloatingGallery(cards,asset){
 const region=document.getElementById('floating-gallery'),stage=document.getElementById('film-stage'),items=[...stage.querySelectorAll('[data-film]')];
 const dialog=document.getElementById('film-dialog'),player=document.getElementById('film-player');
 const previous=document.getElementById('film-prev'),next=document.getElementById('film-next');
 let active=0,invoker=null,startX=0,startY=0,playing=null,swipedAt=0,dragX=null,dragged=false;
 const listeners=[];const on=(el,type,fn,options)=>{el.addEventListener(type,fn,options);listeners.push(()=>el.removeEventListener(type,fn,options));};
 function load(index){const image=items[index]?.querySelector('img');if(image&&!image.src){image.src=image.dataset.src;image.addEventListener('error',()=>{if(image.src!==image.dataset.fallback)image.src=image.dataset.fallback;},{once:true});}}
 function select(index){active=(index+cards.length)%cards.length;const small=innerWidth<768,step=small?215:260;
  items.forEach((item,i)=>{let delta=i-active;if(delta>cards.length/2)delta-=cards.length;if(delta< -cards.length/2)delta+=cards.length;const near=Math.abs(delta)<=2;item.classList.toggle('is-selected',i===active);item.classList.toggle('is-near',near);
   item.style.setProperty('--card-x',`${delta*step}px`);item.style.setProperty('--card-y',`${Math.abs(delta)**2*-7}px`);item.style.setProperty('--card-z',`${-Math.abs(delta)*(small?100:135)}px`);item.style.setProperty('--card-angle',`${-delta*(small?16:22)}deg`);item.style.setProperty('--card-opacity',Math.abs(delta)===0?1:Math.abs(delta)===1?.94:.8);item.style.setProperty('--card-order',10-Math.abs(delta));item.style.setProperty('--float-delay',`${i*-.8}s`);
   const button=item.querySelector('button');button.tabIndex=i===active?0:-1;button.setAttribute('aria-label',`${i===active?'Play':'Select'} ${cards[i].title}`);button.setAttribute('aria-pressed',String(i===active));if(near)load(i);
  });
  previous.disabled=next.disabled=cards.length<2;
  document.getElementById('film-counter').textContent=`${String(active+1).padStart(2,'0')} / ${String(cards.length).padStart(2,'0')}`;
  document.getElementById('selected-film-title').textContent=cards[active].title;document.getElementById('selected-film-tags').textContent=cards[active].tags;
  region.style.setProperty('--film-accent',active%2?'#b79bff':'#58ddf4');
 }
 function close(){if(dialog.open)dialog.close();}
 function play(button){const card=cards[active];invoker=button;player.replaceChildren();document.getElementById('film-dialog-title').textContent=card.title;
  document.getElementById('film-source-link').href=card.link;dialog.showModal();
  if(card.src){const v=document.createElement('video');v.controls=true;v.playsInline=true;v.preload='metadata';v.src=asset(card.src);v.poster=asset(card.poster);v.setAttribute('aria-label',card.title);player.append(v);playing=v;
   if(card.start)v.addEventListener('loadedmetadata',()=>{v.currentTime=Math.min(card.start,Math.max(0,v.duration-.1));},{once:true});
   v.addEventListener('error',()=>{const p=document.createElement('p');p.textContent='This film is unavailable right now. You can still view its details or contact us.';player.replaceChildren(p);},{once:true});v.play().catch(()=>{});
  }else if(card.youtube_id){const frame=document.createElement('iframe');frame.src=`https://www.youtube-nocookie.com/embed/${encodeURIComponent(card.youtube_id)}?autoplay=1&rel=0`;frame.title=card.title;frame.allow='autoplay; fullscreen; picture-in-picture';frame.allowFullscreen=true;player.append(frame);playing=frame;
  }else{const p=document.createElement('p');p.textContent='This film will be available soon. Explore the collection or ask us about your session.';player.append(p);}
 }
 on(previous,'click',()=>select(active-1));on(next,'click',()=>select(active+1));on(document.getElementById('play-selected-film'),'click',e=>play(e.currentTarget));
 items.forEach((item,i)=>on(item.querySelector('button'),'click',e=>{if(performance.now()-swipedAt<400||dragged){dragged=false;return;}if(i===active)play(e.currentTarget);else select(i);}));
 on(region,'keydown',e=>{const cardFocus=e.target.classList.contains('film-select');if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();select(active+(e.key==='ArrowRight'?1:-1));}if(e.key==='Home'){e.preventDefault();select(0);}if(e.key==='End'){e.preventDefault();select(cards.length-1);}if(cardFocus&&['ArrowLeft','ArrowRight','Home','End'].includes(e.key))items[active].querySelector('button').focus({preventScroll:true});});
 on(stage,'pointerdown',e=>{if(e.pointerType==='mouse'){dragX=e.clientX;dragged=false;}});
 on(window,'pointerup',e=>{if(dragX!==null){const dx=e.clientX-dragX;if(Math.abs(dx)>55){dragged=true;swipedAt=performance.now();select(active+(dx<0?1:-1));}dragX=null;}});
 on(stage,'touchstart',e=>{startX=e.touches[0].clientX;startY=e.touches[0].clientY;},{passive:true});
 on(stage,'touchend',e=>{const dx=e.changedTouches[0].clientX-startX,dy=e.changedTouches[0].clientY-startY;if(Math.abs(dx)>45&&Math.abs(dx)>Math.abs(dy)*1.5){swipedAt=performance.now();select(active+(dx<0?1:-1));}},{passive:true});
 on(document.getElementById('close-film'),'click',close);on(dialog,'close',()=>{if(playing?.tagName==='VIDEO'){playing.pause();playing.removeAttribute('src');playing.load();}player.replaceChildren();playing=null;invoker?.focus({preventScroll:true});});
 on(window,'resize',()=>select(active));select(0);
 return {get active(){return active;},update(time,enabled){const r=stage.getBoundingClientRect(),visible=r.bottom>0&&r.top<innerHeight;region.classList.toggle('gallery-moving',enabled&&visible&&!dialog.open);if(enabled&&visible)stage.style.setProperty('--arc-tilt',`${Math.max(-2,Math.min(2,(r.top-innerHeight*.3)/160))}deg`);else stage.style.setProperty('--arc-tilt','0deg');},pause(){playing?.pause?.();},dispose(){close();listeners.forEach(off=>off());}};
}
