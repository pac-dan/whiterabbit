# GitHub animation references for Momentum Clips

Reviewed 26 October 2026. These are public technique references, not Emotion's implementation and not proof of its internal technology. Source files and licence texts were fetched and inspected. Demos were not run or performance-tested in this pass. No dependencies were installed or runtime application code changed.

## Recommended shortlist

### 1. Circular gallery arrangement and movement

[bizarro/infinite-circular-webgl-gallery](https://github.com/bizarro/infinite-circular-webgl-gallery) · [Demo listed by its author](https://codrops.com/Tutorials/InfiniteCircularGallery/)

Inspect [app/Media.js](https://github.com/bizarro/infinite-circular-webgl-gallery/blob/3db485819df63550f9872b0ca5e6961a9fe517e4/app/Media.js) and `app/index.js`. The media update maps scroll to X position, cosine-based Y position and rotation; scroll delta also drives a shader speed uniform. Resize logic accounts for viewport and image dimensions.

Use for our card spacing, curved presentation, scroll response and image fitting in `ring.js`/`slots.js`. This is an OGL curved gallery, not a ready-made 3D ring with reflective floor. Port the useful maths into our existing Three.js ring. Do not add OGL, lodash, its wheel handler or its webpack setup. Keep our single Lenis progress and finite 12-card collection; do not adopt its wrap history as a second source of state.

Code licence: MIT, full licence file inspected. Reviewed commit `3db485819df63550f9872b0ca5e6961a9fe517e4`. Bundled photos/fonts are not proposed for reuse.

### 2. Scroll-driven particle morphing

[GeeAI/Interactive-3D-Particle-Morphing](https://github.com/GeeAI/Interactive-3D-Particle-Morphing) · [Demo listed by its authors](https://geeai.github.io/Interactive-3D-Particle-Morphing/)

Inspect [src/ParticleAnimation.jsx](https://github.com/GeeAI/Interactive-3D-Particle-Morphing/blob/5a454ef01f8975d10bbd17c947089aefd6d23cd5/src/ParticleAnimation.jsx). Its custom vertex shader blends current and target positions with a morph-progress uniform. A scroll section calculation selects the two shape buffers and local interpolation progress. This is an actual shader implementation, rather than a README-only effect claim.

Use as a starting study for snow particles resolving into our own mark or a transition shape. Extract the buffer-generation and GLSL ideas into a plain module; keep the effect secondary to the rider. The source uses React 18, Vite and Three.js `^0.162.0`. It is not a drop-in dependency for our no-build r170 app. Check shader compatibility, deterministic progress, cleanup, point-size limits and fill-rate on a physical phone before adopting it. Its default particle count and claimed performance are not our budget or a verified result.

Code licence: complete MIT text inspected. Reviewed commit `5a454ef01f8975d10bbd17c947089aefd6d23cd5`. No model/texture assets proposed for reuse.

### 3. One subject carried across several scroll compositions

[codrops/OneElementScroll](https://github.com/codrops/OneElementScroll) · [Demo listed by Codrops](https://tympanus.net/Development/OneElementScroll/)

Inspect [js/index.js](https://github.com/codrops/OneElementScroll/blob/feb7ad7fbc602b8cdbb5109da83442ff5995cdaf/js/index.js). It captures waypoint layout states with `Flip.getState`, then sequences `Flip.fit` in a scrubbed ScrollTrigger timeline.

This is a DOM continuity study, not a 3D camera system. Adapt its compositional idea: a single signature subject has deliberately different roles and screen positions across chapters. Use it to storyboard our rider/trail/ring handoff. Keep our existing scene controller; there is no need to add Flip or replace our progress engine. The repository's MIT licence does not relicense its bundled GSAP plugins; do not vendor its dependency files wholesale.

Demo code licence: MIT, full licence file inspected. Reviewed commit `feb7ad7fbc602b8cdbb5109da83442ff5995cdaf`.

### 4. Scroll-linked typography and masked reveals

[codrops/TextClipScroll](https://github.com/codrops/TextClipScroll) · [Demo listed by Codrops](https://tympanus.net/Development/TextClipScroll/)

Inspect [js/index.js](https://github.com/codrops/TextClipScroll/blob/79327102f7bd2e04d1b0e4786d744794b5320d0b/js/index.js). It contains scroll-linked GSAP timelines for clip-path/text treatments and explicit Lenis/ScrollTrigger synchronisation.

Use as a visual/implementation reference for readable line reveals in `overlay.js` and `experience.css`, starting with transform/opacity and simple masks. Keep headline copy in real HTML and restore it fully in static/reduced-motion mode. Select a restrained treatment that agrees with camera arrival. Do not bring its CDN fonts, demo images, inline boot code or vendored library versions into our CSP-sensitive page. A complicated SVG treatment must earn its complexity over a simple CSS mask.

Demo code licence: MIT, full licence file inspected. Reviewed commit `79327102f7bd2e04d1b0e4786d744794b5320d0b`. Third-party dependencies remain separately licensed.

### 5. Following a spline with stable look direction

[Official Three.js r170 spline camera example](https://github.com/mrdoob/three.js/blob/r170/examples/webgl_geometry_extrude_splines.html)

The example samples position with `getPointAt`, direction with `getTangentAt`, and a forward look target along the same curve. It demonstrates the path-relative approach relevant to fixing `camera.js` and coordinating it with `path.js`/`rider.js`.

Use arc-length progress and local travel directions for the follow-cam, with separately authored portrait framing. Remove the demo's elapsed-time loop and looping modulo for our finite, reversible descent. The example's orientation strategy is a starting point, not a complete terrain-contact/camera-collision solution.

Code licence: Three.js MIT, licence inspected at tag `r170`, matching our pinned Three.js 0.170.0. Its HTML import map/inline module must not be copied into Flask; use our existing relative modules.

### 6. Rigged character animation and pose weights

[Official Three.js r170 skinning/blending example](https://github.com/mrdoob/three.js/blob/r170/examples/webgl_animation_skinning_blending.html)

Shows `AnimationMixer`, action weights and transitions between a rigged character's animation clips. Use the action/weight structure to extend `slots.js` and the rider's neutral/toe-edge/heel-edge/compression poses.

The demo's walking/running motions are not snowboard animations. Its elapsed-time crossfades are also not the reversible scroll controller we need: sample action times and weights from our progress/curvature. A properly rigged snowboarder asset, foot/binding constraints and board-to-snow alignment still need to be authored. Do not treat the code licence as a licence to use every example model.

Code licence: Three.js MIT at `r170`; model licences separate. This is a code reference, not an acquired rider asset.

### 7. Optional reflected floor

[Official Three.js r170 Reflector](https://github.com/mrdoob/three.js/blob/r170/examples/jsm/objects/Reflector.js)

Inspectable implementation of a reflected camera and render target with texture-resolution controls. It renders the scene again through a virtual camera; the performance cost needs profiling.

Use for a bounded tier-3 experiment on the ring shelf if improving our fake reflection is insufficient. Tier 2 keeps the cheaper mirror and tier 1 none. Vendor only if the prototype justifies it, rewrite the bare `three` import to our local version, record the licence/edit in VERSIONS.md and recheck the ≤900KB runtime JS budget.

Code licence: Three.js MIT at `r170`.

## Selection and reuse decision

Start with the official spline and animation examples to fix the visible rider/framing shortcomings. Refine the ring using Bizarro's presentation ideas; use the Codrops examples to choreograph continuity and text. Particle morphing is a later visual enhancement, not a substitute for a convincing rider or clean composition. Reflector is optional and subject to profiling.

The shortlisted source-code licences have complete MIT texts; preserve copyright/licence notices for adapted code. This does not clear bundled models, photos, fonts, or third-party libraries. No reference assets are approved for inclusion. A separate candidate, `Kshitij978/Three.js-Point-cloud-morphing-effect`, advertises MIT but its licence file omits the substantive list of granted rights; it is excluded from the recommended code-reuse shortlist pending clarification.

Maintain Flask/Jinja, pinned Three.js r170, the existing Lenis instance, external modules/relative imports, CSP, named content slots, reduced-motion fallback and no JS build. These examples supply specific techniques to adapt; their complete application scaffolding is not a proposed replacement for Momentum.

## Evidence

Fetched source/licence snapshots and a URL/ref/path manifest are under `.runs/2026-10-26-homepage-art-direction/evidence/github/`. Research checked 19 files from five repositories; three separate official Three.js examples cover camera, rider and reflection. These files are isolated research artifacts, not additions to the runtime payload. No demo execution, compatibility proof, benchmark or newly completed homepage feature is claimed.
