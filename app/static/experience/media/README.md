# Drop your media here

Edit **app/experience/content.py** after copying files into this directory.
All `src` values start at Flask's `static/` directory, for example
`experience/media/ring-01.mp4`. Leave `None` for the branded placeholder.
See **docs/content-drop-in.md** for worked examples.

| Slot | Recommended file |
| --- | --- |
| `ring.cards[0..11].media`, `beats[0..2].media` | 720×1280 portrait H.264 MP4, ≤4 MB, 4–8 second loop, no audio. WebM also works. |
| `gates.media[0..2]`, `portal.media` | 1200×1600 WebP. JPEG and PNG also work. |
| `rider` | GLB ≤3 MB, Y-up, metres, facing +Z, optional idle/ride animation. Embed textures; no Draco compression. |
| `hero.background_video` | 1920×1080 H.264 MP4 ≤8 MB; optional local `poster` image. |

Changing `type` from `image` to `video` works for all flat media slots.
Videos are muted, loop and play inline, and pause outside their active chapter.
GLB animations use the configured name, or the first clip if it is not found.
Missing/unreadable media resolve to the existing placeholder. Use local files
to avoid CORS and CSP changes. Keep originals elsewhere; these are web exports.
Increment `VERSION` in the same manifest when replacing a file without renaming it.
The terrain and generated placeholders are build assets, not owner media slots.

The current default rider is articulated and uses illustrative scene scale. GLB replacements are fitted to `rider.height` and multiplied by `scale`. Name the board mesh `Snowboard` (or set `board_node`); use in-place clips. Optional `poses` maps neutral/toe/heel clip names. See docs/content-drop-in.md for the complete example.
# Scroll-controlled journey

`bansko-journey-v1.mp4` is the owner's generated clip, optimised for seeking; the two `bansko-*-poster.webp` files are extracted from it. Timing, crop and recovery instructions: [docs/video-journey.md](../../../../docs/video-journey.md). Configure it under `journey` in `app/experience/content.py`. It replaces the procedural background while leaving gallery media slots independent.

