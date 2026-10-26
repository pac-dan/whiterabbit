# Momentum Clips: homepage quality plan

Research and diagnostic review: 26 October 2026. This is a proposed next iteration, not a claim that the improvements below are implemented.

## Recommendation

Keep the real Bansko terrain, the six-chapter journey, Flask, local ES modules, content slots and graceful fallback. Build one excellent 10–15-second section first: a properly framed carving rider entering a refined card ring. Review that section with Dan before extending its treatment across the whole journey. The major gap is art direction, subject framing and believable motion, rather than another framework or more effects.

Implementation references: [reviewed public GitHub examples](2026-10-26-github-animation-references.md) map seven useful techniques to our existing modules, with pinned source links, licence checks and adaptation limits.

Recommended visual direction: a stylised but anatomically believable rider, dark technical outerwear, helmet/goggles, one cyan accent, crisp snow, cool rim light and a restrained violet ring. Photorealism is an alternative requiring a more demanding character/material/animation pipeline; it should be an explicit creative choice.

## Observed findings

Inspected current source and saved desktop/mobile chapter captures; also ran a fresh headless Chromium diagnostic against the local homepage at 1440×900 and 375×812. Raw results and four current captures are under `.runs/2026-10-26-homepage-art-direction/evidence/`.

* At progress .21 the rider's projected centre is approximately (1089,595) on desktop, but (520,537) on a 375px-wide mobile viewport: outside its right edge. At .18 it is outside both viewports. This is a framing defect, not merely a preference for a centred layout. Projection alone does not test terrain occlusion or HTML coverage.
* `camera.js` has independently authored position/look curves and world-axis offsets. `rider.js` follows a separate progress-to-path mapping. Only the ring gets a portrait camera pullback. The follow-cam does not continuously compose around the rider.
* `placeholderRider()` is a body box, head icosahedron and board box. There are no articulated limbs, bindings, clothing detail or terrain-normal pitch. Curvature only changes a whole-object roll.
* `terrain.js` scales horizontal metres by .1 and elevation by .145. Rider geometry is several scene units tall and replacement GLBs default to scale 1. Establish an explicit metres-to-scene contract before replacing the rider; do not simply drop a human-scale asset into the existing framing.
* `snow.js` places spray near the rider but along fixed axes; its spray phase is wall-clock driven. It does not emit from the board edge in the direction of travel, or reconstruct its trail from progress when reversing.
* `ring.js` makes a circular arrangement with line rims, broad rectangular glow planes and flat fake reflection planes. Active-card scale is a discrete 1.045 multiplier. A much clearer visual hierarchy is possible without a large post-processing stack.
* Existing browser checks prove rendering, links and fallback behaviours, but do not assert rider framing or text/subject separation. A screenshot file and passing functional test do not constitute visual approval.

## What to take from the references

The original brief is the visual description of these references. Research reopened their live pages, but text extraction cannot validate their current animated composition; a rendered, side-by-side reference review remains a first-phase deliverable. No reference code or assets should be copied.

| Reference | Principle to adapt | Momentum implementation |
| --- | --- | --- |
| [Emotion projects](https://emotion-agency.com/projects) | A curated spatial collection, a clear featured work, restrained navigation | A dark ice shelf with one dominant front card, quieter neighbours, graduated light, aligned title/counter and convincing floor contact |
| [ESR Bespoke](https://www.esrbespoke.au/) | Large confident typography and cinematic media, with little competing chrome | Give text and action separate screen regions; introduce owner footage when available; reduce persistent labels when they distract |
| [Ascension](https://ascension.pegassi.be/) | A strong visual threshold between scenes, as described in the brief | Aim camera travel into a defined portal plane, mask the valley reveal at that crossing, then settle into the CTA |

Emotion's page lists Three.js among its project technologies. That supports staying with our existing rendering stack; it does not reveal how its ring is implemented or prove that its visual quality comes from a particular library.

## Phase 1 — Agree on composition before modelling

Deliver six chapter keyframes at desktop and mobile sizes, with safe regions for nav, text, CTA and scene subject. Include ring entry/exit and descent start/mid/end. These are design compositions for review, not another round of pass/fail screenshots alone.

Create two rider treatments on the same pose and lighting: stylised technical athlete (recommended), and a more realistic athlete. Create two ring settings: open alpine ice shelf (recommended for continuity), and a darker ice amphitheatre (closer to the first reference's enclosed feel). Dan chooses using side-by-side images. Obtain short riding references for stance, turn cadence, clothing and camera angle; Dan can identify the Bansko line/landmarks that should be recognisable.

Exit: approved rider treatment, three decisive shots (summit, follow-cam, ring), and a short storyboard. Keep creative choices separate from implementation progress.

## Phase 2 — Fix framing and path choreography

Extend existing `camera.js`, `path.js` and `overlay.js`; avoid a second scroll controller. Derive rider and chase-camera positions from the same ride distance. Use curve tangents and a local right/up frame for camera offsets, not fixed world X/Z offsets. Use arc-length sampling for a steadier descent and an explicit progress-to-distance mapping for intentional acceleration.

Author desktop and portrait composition anchors, field of view and subject size per chapter. Project rider/active-card bounds into screen space; fit into a safe rectangle that excludes HTML overlays. Recompute on viewport changes, with a deliberate portrait composition rather than cropping the desktop shot. Use smooth interpolation and terrain clearance across transitions; avoid abrupt Y clamps where a collision-safe path can be authored instead.

Add optional composition guides and a chapter/progress scrub control to the existing debug panel. Extend read-only debug telemetry with rider/card screen bounds. Allow Dan to report “Drop in at 18%, rider too far right” precisely. No public editing UI or new framework needed.

Exit: throughout the intended close follow shot, the rider's full projected bounds stay in the agreed safe rectangle and do not overlap text. Validate densely across progress, including .18 and .21, in both scroll directions. Deliberate wides need separately approved smaller subject sizes.

## Phase 3 — Build a convincing rider

Preferred asset: one original or explicitly licensed rigged GLB with helmet, goggles, jacket, gloves, trousers, boots, bindings and a shaped snowboard. Keep board travel direction distinct from the sideways snowboard stance. Root at board contact; Y-up; document metres, facing direction, scale conversion and clip names in the existing content manifest/drop-in guide. Do not replace the named model slot with hard-coded assets.

Prepare a neutral riding stance plus toe-edge, heel-edge and compression poses/actions. Rig hips, knees, ankles, shoulders and elbows; keep boots attached to bindings. Use controlled animation blending plus procedural terrain alignment: sample snow height/normal, orient the board, then add edge angle, knee flex, counter-rotation and restrained head/arm movement. Board contact must be checked during turns, not just at the root position. Treat cloth folds as authored geometry/material detail first; real-time cloth is unnecessary for this shot.

Sample pose and blend weights directly from progress/path curvature so rewind reconstructs the same motion. The existing `AnimationMixer.setTime` mechanism is useful, but `p*30` and a single selected clip are insufficient for the proposed multi-pose rider. Extend `slots.js` to expose named clips/weights while retaining simple one-clip and broken-file fallback behaviour. Do not rely on elapsed-time cross-fades for scroll-dependent actions.

Candidate starting asset budget (to validate): 15–30k triangles, at most roughly 50 bones, 1–2 material atlases at 1K, complete GLB ≤3MB. These are proposed limits, not measured results. If they cannot hold, simplify the asset before adding decoders.

Mixamo can accelerate humanoid rigging, but its documentation requires a neutral humanoid mesh without extra props. If used, rig the character separately and attach the snowboard afterwards. Generic humanoid animations still need snowboard-specific feet/board constraints and animation cleanup. A custom Blender animation pass remains the recommended route to convincing carving.

Exit: Dan approves silhouette and stance in a close shot; heel/toe changes look plausible; boots stay fixed, board stays on snow, scale reads correctly, and reverse scrubbing produces the same pose.

## Phase 4 — Give the rider physical presence

Extend `snow.js` with board-local emission from the trailing edge. Spray direction, spread and amount depend on turn curvature/edge angle and the authored ride speed; no floating cloud following a fixed world direction. Reconstruct the visible recent spray segment from seeded progress/path samples for reversible motion. Ambient snowfall may remain time-driven.

Add a modest contact shadow and a thin paired carved-track ribbon sampled from the same ride path. The ribbon's visible length is a function of progress, so tracks disappear correctly when rewinding. Use snow microdetail/normal variation, directional blue-hour light and rim lighting to separate the rider. Real elevation stays the base; artistic snow detail is not a claim of surveyed piste geometry.

Exit: board, shadow, tracks and spray agree in direction; the rider reads against bright and dark slopes; no texture leaks or uncontrolled draw-call increase.

## Phase 5 — Refine the ring and finish the journey

Extend `ring.js` with continuous prominence based on angular distance to the camera: featured card scale/brightness/vertical lift and adjacent-card quieting. Keep rotation continuous, links keyboard-accessible and the counter in sync. Author portrait spacing/camera independently. Replace flat glow rectangles with a controlled rounded-edge falloff; keep reflections attached to card positions with a soft fade and grounded platform edges.

Start by improving the fake reflection. Only prototype a low-resolution planar reflection at tier 3 after profiling; Three.js Reflector renders the scene from another camera, so it is a measurable extra render cost. Keep fake reflections on tier 2 and none on tier 1. A subtle icy alcove can provide contrast without turning the whole mountain into a dark room.

Then apply the approved lighting/framing to package gates; aim the portal along its actual camera approach instead of assuming a world-Z tunnel; stage the valley reveal with warm clustered town lights and a deliberate quiet finish. Keep the one-camera journey and make the deliberate portal crossing the only masked transition. Source actual owner clips for the ring to avoid a finished engine still looking like a repeated test collection.

Exit: featured card reads first, title/counter share its visual anchor, reflections and rims feel integrated, gates remain readable, portal crossing is intentional in both directions, finale gives the CTA clear space.

## Phase 6 — Review motion and measure the result

Extend `scripts/check_experience.mjs`; retain all existing functional/CSP/fallback checks. Capture fixed shots plus short screen recordings of slow, fast and reverse scroll. Validate 375×812 and 1440×900 each iteration, plus a tablet, a short-height laptop and an ultrawide during final framing review. Check chapter boundaries as well as midpoints; resize while inside a chapter. Keep the existing pause/resume and content-slot tests.

Automate frustum/safe-rectangle checks for authored subject shots; inspect actual pixels for occlusion and artistic quality. Compare captures side-by-side with approved keyframes. Passing tests alone is not visual sign-off.

Retain ≤900KB uncompressed runtime JS, ≤3MB rider GLB, ≤2.5s first rendered frame, desktop 60fps target and tier-2 physical-phone ≥30fps target. Record GPU/device, DPR, tier, frame-time percentiles, draw calls and loaded bytes for each chapter. A narrow desktop viewport is not a physical phone performance measurement. Preserve CSP, no-build deployment, local vendors, reduced-motion/static mode and single-file content slots. Optional Meshopt/KTX2 would add loaders/decoders and potentially CSP work; profile and check exact r170 support and remaining budget before adopting them.

Exit: approved motion recordings, no visual framing regressions, existing test baseline unchanged, production CSP clean, measured budgets documented, owner footage/model slots still swappable. Deploy a review preview only after the agreed slice is approved; authenticated preview checks remain subject to the existing Vercel login/protection limitation.

## Collaboration checkpoints

1. Dan chooses rider realism, clothing/board character and whether the ring stays outdoors or becomes an ice amphitheatre.
2. We review three keyframes before the full rider asset or whole-page polish.
3. We review the short descent-to-ring prototype and annotate precise progress positions.
4. We extend the approved treatment to all six chapters, then review recordings on desktop and a real phone.

Useful next inputs: the specific off-centre chapter/moment Dan noticed; a clip showing the desired carving/follow-camera feel; photos or a description of the rider kit. These refine art direction and do not require Dan to edit code.

## Primary research sources and limits

* [Three.js r170 PerspectiveCamera](https://github.com/mrdoob/three.js/blob/r170/docs/api/en/cameras/PerspectiveCamera.html): FOV, aspect, film offset and projection controls. Supports responsive composition; our safe-rectangle camera solver is a proposed implementation.
* [Three.js r170 AnimationMixer](https://github.com/mrdoob/three.js/blob/r170/docs/api/en/animation/AnimationMixer.html): exact animation-time sampling via setTime.
* [Three.js r170 AnimationAction](https://github.com/mrdoob/three.js/blob/r170/docs/api/en/animation/AnimationAction.html): animation weights and blending. Supports the proposed pose system; does not supply snowboard choreography.
* [Three.js r170 Reflector source](https://github.com/mrdoob/three.js/blob/r170/examples/jsm/objects/Reflector.js): extra reflected-camera render and resolution controls. Performance impact here still needs measurement.
* [Adobe Mixamo FAQ](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html): humanoid rigging requirements and permitted uses. No claim that a suitable snowboard clip/model has been sourced.
* [Khronos glTF overview](https://www.khronos.org/gltf/): delivery format and optional compressed textures. Runtime extension compatibility must be checked against our pinned loader before use.

The Blender manual fetch failed in this research environment, so it is not used as verification. The initial research pass did not inspect rendered reference animation; the follow-up below adds rendered Emotion observations. No model was purchased, commissioned, downloaded or approved. No homepage implementation, deployment, performance upgrade or new visual-fix completion is claimed by this plan.

## Follow-up: Emotion is the primary motion reference

Dan's direction: take substantially more inspiration from the full [Emotion homepage](https://emotion-agency.com/), extending beyond its project ring. Retain ESR/Ascension as supporting references. This raises the intended standard of the whole motion system; it does not approve any particular rider style from the outstanding creative choices.

### Rendered observations

A background Maestro research tab was opened and closed without changing focus. No usable Maestro CDP inspection port was available. An isolated headless Chromium capture then entered the reference without audio and recorded the opening plus 16 scroll steps at 1440×900 and 375×812. Captures and recordings are research evidence under `.runs/2026-10-26-homepage-art-direction/evidence/emotion/`, not application assets. The first diagnostic capture stopped at the site's entry gate; its observations are not treated as an animation study. The rerun explicitly selected entry without audio.

The desktop opening shows a luminous particle emblem above reflective water, with close vegetation, rocks and sky at different depths. Scroll steps 4, 7, 10 and 13 show the luminous subject in different forms, sizes and screen positions, composed alongside successive text groups. Step 10 has a heart-like form with a tree and building in the environment; step 13 returns to a ring-like form above the water. By step 16 the scene yields to a pale editorial section with text at different opacity levels. These are observed states; exact shader internals, morph algorithms, timing curves and performance are not established by screenshots.

The mobile capture has a compact bottom pill for menu/brand/utility controls, whereas the desktop capture has a sparse top navigation. Its opening makes the particle subject much larger within the portrait composition. These are useful precedents for designing a different portrait layout rather than shrinking desktop. For Momentum, review navigation and chapter progress together so separate bars do not consume the rider's screen space; keep booking easy to reach.

The important transferable principles are a recurring visual subject, designed foreground/middle/background layers, variation between wide and close compositions, coherent colour/light, text positioned as part of each shot, and a deliberate transition from immersive space to editorial content. Review the captured motion rather than interpreting this as a requirement to reproduce their scenery, particle shapes, typeface or loading gate.

### Revised Momentum motion direction

| Priority | Pattern to adapt | Original Momentum treatment | Review criterion |
| --- | --- | --- | --- |
| P0 | One recognisable visual subject across changing shots | The rider, curved carved line and luminous snow trail carry the journey; the trail's light hands off to ring rims, gate lights and the portal | Adjacent chapters feel causally connected, including when reversing |
| P0 | Designed framing, rather than camera movement alone | Compose wide summit, close chase, ring reveal and quiet town as distinct shots on the continuous camera path | Main subject and copy occupy intentional separate regions at both sizes |
| P0 | Layered scene depth | Foreground spindrift/snowbanks, middle-distance rider and terrain, distant peaks/clouds; sparse near-slope detail where it will actually be seen | A clear sense of travel without clutter or hiding Bansko terrain |
| P1 | Subject changes that accompany new text | Snow haze opens to reveal the drop; camera tightens as the rider commits; spray clears to reveal the ring | Each reveal has a readable beginning, focal moment and rest |
| P1 | Typography participates in the composition | Masked line reveals and restrained offsets for headline lines, sequenced with camera arrival; small labels follow | Text remains readable, selectable and in DOM order, with a static reduced-motion state |
| P1 | Material and light continuity | A consistent blue-hour key light, cool rim light, soft snow shading and controlled cyan/violet accents; warm light reserved for town | Character, floor and cards appear to share one environment |
| P1 | Transition from spectacle into clear content | Ring composition settles while visitors read the selected edit; gates hold a readable package before motion resumes; town becomes calmer for booking | Enough scroll distance to read and choose, with no snapping or forced delay |
| P2 | Carefully coordinated small interactions | A shared short hover/focus treatment for pills, links and cards; featured card lift, rim intensity and label response tuned together | Pointer and keyboard feedback are clear; touch does not depend on hover |

Micro-interactions in the last row are our proposed refinement, not a claim that specific hover effects on Emotion were tested. A snow-to-line-to-ring effect is an original design proposal, not an observed Emotion effect.

### First prototype: motion storyboard

Keep the existing six chapter ranges initially. Within the drop (.12–.30), compose the rider into frame before the close chase, show two legible edge changes, and begin revealing the shelf before the ring chapter. During ring entry (.30–.35), let the snow trail and lighting guide the eye toward one featured card; establish a readable composition before increasing rotation. Across .35–.55, alternate movement and readable positions through the progress mapping without scroll snapping. The visitor can stop or reverse anywhere.

Review three connected keyframes plus a continuous desktop/mobile recording. The quality question is whether eye direction, rider action, camera movement, text entrance and light change agree. A beautifully detailed rider alone will not resolve a poorly composed shot.

Start with the approved framing and an articulated temporary rider, so camera/choreography work does not wait for a finished GLB. Then substitute the approved character through the existing manifest. Show the same sequence with the temporary and final model to prove that content swapping has not become a bespoke one-off integration.

### Motion rules to agree and tune

Proposed initial UI ranges: roughly 160–240ms for hover/focus feedback and 450–700ms for deliberate text/element entrances; these are starting values to test, not measurements of Emotion. Scroll-controlled scene movement uses normalised progress windows, not elapsed-time delays. Use one progress-derived animation state for reveal, exit and reverse. Ambient wind/snow may remain independent.

Desktop pointer parallax, if added, is subtle and subordinate to scroll; disable it on touch/reduced-motion paths. Use transform/opacity for real HTML, preserve focus visibility, and never hide booking behind a mandatory intro. Keep audio silent by default. Do not add arbitrary cursor effects, an entire post-processing stack or a library migration as substitutes for composition. Optional high-tier reflection and particle work must fit the existing JS/download budget and be tested on a physical phone.

### What this changes in the next milestone

The milestone is now a short, directed film-like interaction: opening composition → credible descent → ring arrival. Its deliverable includes a motion storyboard, keyframes at both sizes, review recordings, a character brief and explicit frame-time/download measurements. Full-site page transitions and elaborate optional effects follow after this sequence is convincing. Continue using the original or licensed asset workflow and preserve all existing booking, accessibility, CSP and no-build constraints.

### Follow-up limits

This study covers the captured opening and scroll sequence, not every page, every hidden interaction or real-device performance of Emotion. Videos are captured for review; screenshots alone cannot establish exact interpolation quality. No reference implementation source was incorporated into Momentum. The proposed direction still needs Dan's visual review; application code remains unchanged.
