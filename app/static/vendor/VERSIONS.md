# Vendored browser libraries

- `three.module.min.js`: https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.min.js
- `GLTFLoader.js`: https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/loaders/GLTFLoader.js
- `BufferGeometryUtils.js`: https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/utils/BufferGeometryUtils.js
- `lenis.mjs`: https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.mjs
- `lenis.css`: https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.css
- `THREE-LICENSE.txt`: https://cdn.jsdelivr.net/npm/three@0.170.0/LICENSE
- `LENIS-LICENSE.txt`: https://cdn.jsdelivr.net/npm/lenis@1.1.13/LICENSE

Three.js 0.170.0, Lenis 1.1.13, MIT licenses alongside. GLTFLoader and BufferGeometryUtils imports rewritten to sibling relative paths with the version query. No core dependency in this three.module.min.js build. GSAP deliberately omitted: all positions derive from one scroll progress.
