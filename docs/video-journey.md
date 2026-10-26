# The mountain-to-town journey

The homepage follows **hero → descent → Bansko arrival → floating films → packages → booking/contact**. The supplied film is generated alpine imagery, labelled honestly; it is not documentary footage of Bansko. Text, links and gallery controls are HTML. There is no terrain renderer, floor, podium or WebGL dependency in this mode.

## Timing and framing

Edit `journey` in `app/experience/content.py`. Cue pairs map **scroll distance from the hero's top to the arrival section's top** to fractions of the loaded video's duration. They are independent of gallery/package height. The first quarter holds the opening. At arrival the video holds its final usable frame; town has a separate section before films enter. Reversing scroll reverses this mapping. `video-clock.js` permits one seek in flight and replaces the destination during rapid movement.

The 9.041667-second, 1280×720 source shows open slope to about 2.4 seconds, trees from 2.4–6.8, camera lift around 6.8, and evening town through the end. The endpoint is duration minus .06 seconds. No independent background playback or looping occurs.

`framing` pairs video fractions with horizontal crop percentages. Phones start with a 53svh picture above readable text, then expand continuously into full-height town. Desktop uses cover framing. The source is native 720p; neither encode creates additional detail.

## Media delivery

`scripts/build_responsive_journey.py` creates silent H.264 files directly from the untouched source: 1280×720 CRF24 and 960×540 CRF23, 24fps, 12-frame keyframes, no B-frames, fast-start metadata. It verifies source hash, silence, metadata order and source similarity. The original sharp WebP poster is retained. `journey.src` and `mobile_src` select one file at startup. Each is below 4 MB for the existing Flask/Vercel path.

The poster and usable HTML arrive before motion. Gallery code/posters load near the gallery; only an explicitly opened film gets a playback decoder. Immutable caching requires new media names or updated VERSION; update changed internal import query strings too. No deployment build is needed.

## Still View and recovery

Still View releases the journey decoder and keeps every section accessible. Reduced motion starts there without requesting the film; Play the descent opts in. Slow or broken media keeps a poster and working navigation. The warm town poster is fetched near arrival. Neither journey nor gallery requires WebGL.

The previous implementation is recoverable in Git at `d04d6df`, with its template preserved as `index_video_legacy.html`. Older procedural modules/assets remain. Restoration requires coordinated template/manifest/runtime rollback; preserve unrelated work.

## Verification

Run `node scripts/check_homepage_refinement.mjs hero` (also journey, gallery, booking, accessibility), `node scripts/measure_homepage.mjs after`, and `.venv/Scripts/python.exe -m pytest -q tests`. Browser checks need development port 5000 and production CSP port 5001. Evidence: `.runs/2026-10-26-homepage-refinement/evidence/`.

Performance uses three cold Chrome contexts per profile: 4 Mbps, 80 ms latency, desktop CPU1 and phone viewport CPU4. Reports include raw requests and medians. Phone viewport checks are not physical Safari/iPhone certification. Preview, public delivery and independent review are separate acceptance steps.
