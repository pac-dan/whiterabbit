export function createQuality() {
  const mobile = matchMedia('(max-width: 767px)').matches;
  const forced = Number(new URLSearchParams(location.search).get('tier'));
  let tier = forced >= 1 && forced <= 3 ? forced : (navigator.deviceMemory <= 4 || navigator.hardwareConcurrency <= 4 ? 1 : mobile ? 2 : 3);
  let elapsed = 0, frames = 0, fps = 60, changed = false;
  const api = {
    mobile, get tier() { return tier; }, get fps() { return fps; },
    get dpr() { return Math.min(devicePixelRatio, tier === 1 ? 1 : mobile || tier === 2 ? 1.5 : 2); },
    get segments() { return tier === 3 ? 511 : tier === 2 ? 255 : 127; },
    get particles() { return tier === 3 ? 6000 : tier === 2 ? 2500 : 800; },
    sample(dt) {
      // Ignore suspension / shader compilation outliers, measure active frames only.
      if (dt <= 0 || dt > .5) return false;
      elapsed += dt; frames++;
      if (elapsed < 2) return false;
      fps = frames / elapsed; elapsed = 0; frames = 0;
      changed = fps < (mobile ? 28 : 45) && tier > 1;
      if (changed) tier--;
      return changed;
    },
    reset() { elapsed = 0; frames = 0; },
  };
  return api;
}
