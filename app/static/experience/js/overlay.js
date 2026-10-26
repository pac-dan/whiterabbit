import {CHAPTERS,chapterAt,clamp} from './scroll.js?v=bansko-2';
export function createOverlay(data,scroll,ring,terrain,camera) {
  const sections=[...document.querySelectorAll('[data-chapter]')],rail=[...document.querySelectorAll('[data-go-chapter]')];
  const counter=document.getElementById('ring-counter'),title=document.getElementById('active-card-title'),link=document.getElementById('active-card-link'),tags=document.getElementById('active-card-tags');
  let last=-1;
  return {update(p) {
    const chapter=chapterAt(p),local=scroll.chapterProgress(chapter);
    sections.forEach((s,i)=>{const alpha=i===chapter?Math.min(1,i===0||i===5?1:local*12+.18,i===5?1:(1-local)*12+.12):0;s.style.setProperty('--alpha',alpha);s.classList.toggle('is-active',i===chapter);s.inert=i!==chapter;});
    rail.forEach((b,i)=>b.setAttribute('aria-current',String(i===chapter)));
    document.querySelectorAll('[data-beat]').forEach((b,i)=>b.classList.toggle('is-active',chapter===1&&i===Math.min(2,Math.floor(local*3))));
    document.querySelectorAll('[data-package]').forEach((b,i)=>{const show=chapter===3&&i===Math.min(2,Math.floor(local*3));b.classList.toggle('is-active',show);b.inert=!show;});
    if(last!==ring.active){last=ring.active;const card=data.ring.cards[last];counter.textContent=`${String(last+1).padStart(2,'0')} / ${String(data.ring.count).padStart(2,'0')}`;title.textContent=card.title;tags.textContent=card.tags;link.href=card.link;}
    document.getElementById('chapter-status').textContent=data.chapters[chapter].toUpperCase();
    document.getElementById('altitude-status').textContent=`${Math.round(camera.position.y/.145+terrain.meta.minM).toLocaleString('en')} M`;
    document.getElementById('mainNav').classList.toggle('is-scrolled',p>.015);
  },reset(){sections.forEach(s=>{s.inert=false;s.style.removeProperty('--alpha');});document.querySelectorAll('[data-package]').forEach(s=>s.inert=false);}};
}
