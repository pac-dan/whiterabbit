# The mountain-to-town film

The homepage now uses the owner's generated snowboard film as a **paused, scroll-controlled video**. Text, navigation, the rotating WebGL gallery, packages and booking links are still live elements. The geographic terrain and procedural athlete are not loaded in video mode. The footage is an artistic alpine scene, not verified footage of Bansko.

## Change the timing or framing

Edit only `app/experience/content.py`, under `journey`. `cues` pairs page progress (0–1) with a fraction of the **loaded clip's duration**. Existing chapter boundaries are 0, .12, .30, .55, .75, .88 and 1. The gallery uses approximately 2.5–2.9 seconds of this film, leaving enough scroll distance to rotate all twelve cards. Packages take the tree descent from about 2.9 to 6.7 seconds. The portal takes the rising reveal; the final chapter holds just before the video ends.

Source inspection: open slope until about 2.4 seconds; trees from 2.4–6.8; camera lift around 6.8; rider leaves view around 7.05; wide evening town from 7.1 through 9 seconds. These are visual cues, not cuts. The browser clamps the endpoint to duration minus .06 seconds so it holds a usable decoded frame rather than an ended/blank frame. There is no independent autoplay or loop.

`framing` pairs video fractions with horizontal crop percentages. Desktop uses a full-screen cover. Phones use a 58-viewport-height picture above a lower text area, reducing horizontal crop and keeping both the rider and warm town reveal visible. Tune these pairs after changing the clip. Do not compensate by heavily darkening the whole ending.

## Replace the film

Copy a web-ready H.264 MP4 into `app/static/experience/media/`. Set `journey.src`, `poster` and `town_poster` in the manifest to their static-relative paths. Change `VERSION` and the version strings on changed module imports when publishing changed cached assets. Prefer a new media filename for each revision. No Windows source path is used by the website.

`scripts/build_journey_video.py --source "C:/path/to/source.mp4"` creates the committed silent derivative and two WebP posters. Set `FFMPEG` to an ffmpeg executable if it is not on PATH. This is a one-time content operation, not a deployment build. Current derivative: H.264/yuv420p, original 1280×720 at 24 fps, CRF 22, six-frame GOP (.25 s), no B-frames, no audio, fast-start moov metadata. It trades some download size for fast accurate reverse seeking. The original file is never modified. Rerun with `--verify` to check source hash, silence, metadata ordering and keyframe spacing.

## Fallbacks and recovery

Still View releases the video and WebGL runtime and shows all six HTML sections normally. Reduced-motion starts in this mode without fetching the movie; its Play button opts in. Loading is never blocked by the movie: the poster appears immediately. After six seconds without metadata it remains the background; a late successful load can recover. A media error retains the opening or town poster, live copy, gallery and booking. Without WebGL the movie still scrolls and the gallery becomes a grid.

To restore the previous procedural background, set `journey.mode` to `procedural`. Its entry is `app/static/experience/js/procedural.js`; terrain and rider assets remain in Git. The full pre-film implementation is also recoverable at commit `81a6c48`. Avoid overwriting unrelated page work when reverting.

## Verify

With the local development server on 5000 and the production CSP check server on 5001, run:

```powershell
node scripts/check_video_journey.mjs --group seeking
node scripts/check_video_journey.mjs --group interactions
node scripts/check_video_journey.mjs --group fallback
./.venv/Scripts/python.exe -m pytest -q tests
```

Reports and screenshots go to `.runs/2026-10-26-video-journey/evidence/`. Set `JOURNEY_BASE` to a deployed preview/public URL and use `--group public` for the seeking/layout smoke check there. Desktop Chromium with a phone viewport checks composition and logic; it does not establish physical iPhone/Safari performance. Browser codecs and bandwidth affect seek latency.
