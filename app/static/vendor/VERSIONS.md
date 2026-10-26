# Vendored browser libraries

- `three.module.min.js`: https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.min.js
- `GLTFLoader.js`: https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/loaders/GLTFLoader.js
- `BufferGeometryUtils.js`: https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/utils/BufferGeometryUtils.js
- `lenis.mjs`: https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.mjs
- `lenis.css`: https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.css
- `THREE-LICENSE.txt`: https://cdn.jsdelivr.net/npm/three@0.170.0/LICENSE
- `LENIS-LICENSE.txt`: https://cdn.jsdelivr.net/npm/lenis@1.1.13/LICENSE

Three.js 0.170.0, Lenis 1.1.13, MIT licenses alongside. GLTFLoader and BufferGeometryUtils imports rewritten to sibling relative paths with the version query. No core dependency in this three.module.min.js build. GSAP deliberately omitted: all positions derive from one scroll progress.

## Existing brand fonts, locally served on the homepage

Latin variable WOFF2, SIL Open Font License 1.1 (licenses beside font files). Retrieved 2026-10-26 from Google Fonts; the remaining pages retain their existing Google stylesheet. No changes to brand typefaces.

- Inter: https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7.woff2 (48256 bytes); license: https://raw.githubusercontent.com/google/fonts/main/ofl/inter/OFL.txt
- Montserrat: https://fonts.gstatic.com/s/montserrat/v31/JTUSjIg1_i6t8kCHKm459Wlhyw.woff2 (37956 bytes); license: https://raw.githubusercontent.com/google/fonts/main/ofl/montserrat/OFL.txt
- Orbitron: https://fonts.gstatic.com/s/orbitron/v35/yMJRMIlzdpvBhQQL_Qq7dy0.woff2 (11800 bytes); license: https://raw.githubusercontent.com/google/fonts/main/ofl/orbitron/OFL.txt

Local module import cache key: bansko-2 (three/Lenis versions unchanged).
