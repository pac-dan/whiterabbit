// The manifest selects the background; the previous engine stays recoverable.
const data=JSON.parse(document.getElementById('experience-data').textContent);
if(data.journey?.mode==='video') import('./video-journey.js?v=bansko-video-2');
else import('./procedural.js?v=bansko-video-2');
