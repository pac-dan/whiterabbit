# Alpine texture and film movement

The site's finish uses two small local images: original fine grain and contours drawn from the Bansko elevation map. They appear behind the collection, session cards, closing section and supporting-page headings. The footage remains untextured. Textures are static and cannot intercept clicks; Still View and reduced-motion users retain the same material design.

Adjust strength in `app/static/experience/css/textures.css`. Rebuild the deterministic images with `.venv/Scripts/python.exe scripts/build_alpine_textures.py`. The terrain's attribution is retained in the texture README and the expandable footer credit. Research used Transparent Textures, Subtle Patterns, Spatial Sites and Awwwards/Lusion as inspiration; no third-party pattern or template is shipped.

The film still follows the chapter cue points in `app/experience/content.py`. A continuous, monotone curve eases into and out of the opening/town holds without overshooting or rewinding on forward scroll. Source-frame-aligned seeks keep only the latest destination and let the browser present the decoded frame before replacing it. If a browser omits a presentation callback, a bounded fallback prevents a stall. No autonomous playback or new inertia layer is added.

The existing 720p desktop/540p mobile derivatives remain unchanged. The original footage is 24 fps; smoother scroll scheduling cannot create native detail or intermediate filmed frames. Verification and measured limitations are in `.runs/2026-10-27-texture-smoothness/PERFORMANCE.md` and `HANDOFF.md`.
