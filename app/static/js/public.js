/** Small, CSP-safe public-page interactions. Native scrolling; no 3D dependencies. */
import {createPageMotion} from '../experience/js/page-motion.js?v=bansko-films-2';
const pageMotion=createPageMotion(document.querySelector('.alpine-main'));
let motionFrame=0;
const updateMotion=()=>{if(!motionFrame)motionFrame=requestAnimationFrame(()=>{motionFrame=0;pageMotion.update();});};
addEventListener('scroll',updateMotion,{passive:true});addEventListener('resize',updateMotion);
matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change',updateMotion);
document.addEventListener('visibilitychange',updateMotion);
addEventListener('pagehide',e=>{if(!e.persisted){pageMotion.dispose();cancelAnimationFrame(motionFrame);}});
const nav = document.getElementById('mainNav');
const updateNav = () => nav?.classList.toggle('is-scrolled', scrollY > 20);
addEventListener('scroll', updateNav, {passive: true});
updateNav();

document.querySelectorAll('[data-dismiss-flash]').forEach(button => {
  button.addEventListener('click', () => button.closest('#flash-messages > div')?.remove());
});

document.querySelectorAll('img[data-fallback]').forEach(img => {
  img.addEventListener('error', () => { if (img.src !== img.dataset.fallback) img.src = img.dataset.fallback; }, {once: true});
});

const motion = matchMedia('(prefers-reduced-motion: reduce)');
document.querySelectorAll('.film-art').forEach(card => {
  const video = card.querySelector('[data-loop-src]');
  if (!video) return;
  const pause = () => { video.pause(); video.classList.remove('is-playing'); };
  card.addEventListener('pointerenter', () => {
    if (motion.matches || !matchMedia('(hover: hover)').matches) return;
    if (!video.src) video.src = video.dataset.loopSrc;
    video.play().then(() => video.classList.add('is-playing')).catch(pause);
  });
  card.addEventListener('pointerleave', pause);
  video.addEventListener('error', pause);
  document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
});

document.querySelectorAll('[data-embed]').forEach(button => {
  button.addEventListener('click', () => {
    const frame = document.createElement('iframe');
    frame.src = button.dataset.embed + '&autoplay=1';
    frame.title = button.dataset.videoTitle;
    frame.allow = 'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture';
    frame.allowFullscreen = true;
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    button.parentElement.append(frame);
    button.remove();
    frame.focus();
  }, {once: true});
});

const videoStatus = document.querySelector('[data-video-status]');
document.querySelector('[data-like-url]')?.addEventListener('click', async event => {
  const button = event.currentTarget;
  button.disabled = true;
  try {
    const response = await fetch(button.dataset.likeUrl, {method: 'POST', headers: {'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content}});
    if (!response.ok) throw Error('Like unavailable');
    const data = await response.json();
    if (!data.success) throw Error('Like unavailable');
    button.querySelector('[data-like-count]').textContent = data.like_count;
    videoStatus.textContent = 'Thanks for the love.';
  } catch {
    videoStatus.textContent = 'Couldn’t save that right now. Please try again.';
    button.disabled = false;
  }
});
document.querySelector('[data-copy-link]')?.addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(location.href); videoStatus.textContent = 'Film link copied.'; }
  catch { videoStatus.textContent = 'You can copy the film link from your browser’s address bar.'; }
});

const search = document.getElementById('faq-search');
search?.addEventListener('input', () => {
  const value = search.value.trim().toLowerCase();
  let count = 0;
  document.querySelectorAll('[data-faq]').forEach(item => {
    item.hidden = value && !item.textContent.toLowerCase().includes(value);
    if (!item.hidden) count++;
  });
  document.getElementById('faq-results').textContent = value ? `${count} matching answer${count === 1 ? '' : 's'}` : '';
  document.getElementById('faq-empty').hidden = count > 0;
});

document.getElementById('contact-form')?.addEventListener('submit', event => {
  event.preventDefault();
  const form = event.currentTarget, values = new FormData(form);
  const body = `From: ${values.get('name')} <${values.get('email')}>\n\n${values.get('message')}`;
  const draft = document.getElementById('contact-draft');
  draft.href = `mailto:${form.dataset.email}?subject=${encodeURIComponent(values.get('subject'))}&body=${encodeURIComponent(body)}`;
  draft.hidden = false;
  document.getElementById('contact-status').textContent = 'Your draft is ready. Open your email app to review and send.';
});
document.getElementById('contact-form')?.addEventListener('input', () => {
  document.getElementById('contact-draft').hidden = true;
  document.getElementById('contact-status').textContent = '';
});
