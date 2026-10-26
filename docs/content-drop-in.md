# Add your footage to Momentum Clips

The mountain, ride and transitions are ready for your files. Everything you
need to edit is in **app/experience/content.py**. Packages, prices, video titles
and customer quotes still come from your existing site admin.

1. Export your media using the sizes below.
2. Copy it into **app/static/experience/media/**.
3. In **app/experience/content.py**, replace the matching `None` with its path,
   starting with `experience/media/`. Keep the quotes around the path.
4. Increase `VERSION` (for example `bansko-2` → `bansko-3`) so visitors receive
   the new files. Save and deploy the branch through your normal preview flow.

**Video example — the first recent edit.** Find the `ring` cards list. Replace
the first card's media entry with:

```python
'media': {'type': 'video', 'src': 'experience/media/first-run.mp4'},
```

Use a 720×1280 portrait H.264 MP4, 4–8 seconds, no audio, under 4 MB. Videos
loop silently only while their card is at the front. `ring.source: 'videos'`
keeps titles/tags/YouTube links from the gallery database; each media index
still takes its file here. There are twelve positions; six DB edits repeat.
For your own titles and links, set `source` to `'manual'` and edit each card's
`title`, `tags`, `link` and `media`. `count` supports 8–12 positions.

**Image example — the first package gate.** In `gates.media`, set the first
entry to:

```python
{'type': 'image', 'src': 'experience/media/beginner-gate.webp'},
```

Use a 1200×1600 WebP under about 250 KB. The three gate positions follow the
three packages displayed by the existing database query. The portal accepts
the same image entry under `portal.media`. Beat slots accept either images
or videos under `beats[n].media`; edit their `label` alongside the media.

**3D rider example.** Replace the rider entry with:

```python
'rider': {
    'type': 'model', 'src': 'experience/media/rider.glb',
    'scale': 1.0, 'animation': 'Ride',
},
```

Ask your artist for a GLB under 3 MB, Y-up, metres, facing +Z, textures embedded,
without Draco compression. Put the feet/board at Y=0. `scale` adjusts its size.
If the animation name is missing, the first animation plays. A file that fails
to load restores the articulated snowboarder automatically.

**Opening background.** Set `hero.background_video.src` to a local H.264 MP4,
1920×1080 and under 8 MB. Set `poster` to an optional local WebP. Your video
appears over the 3D summit as a quiet full-screen layer. Headline and subline
are in `hero`; closing copy is in `finale`. Other labels live in the same file.

Leave any `src` as `None` to keep its named placeholder. The still view works
without WebGL, with reduced motion, and if the 3D cannot load. Real gallery
titles, packages, quote and booking links stay accessible in that view.
Mobile visitors receive smaller rendering settings automatically. Check your
preview on a phone after adding large videos; avoid loading all clips at once.


## Updated descent and rider (motion polish)

The default rider is now an original articulated placeholder with helmet, goggles,
jacket, gloves, boots, bindings and a shaped board. Its pose, edge lean, track and
spray follow the same progress-driven line as the camera. The terrain remains real
elevation data; the rider is deliberately larger than geographic scale so it reads
clearly in the cinematic shot. This is still a content slot, not a final athlete model.

A replacement GLB is centred at its base and fitted to `rider.height` (default 2.5
scene units). `scale` multiplies that fitted size. Keep `scale: 1.0` initially.
Use in-place animations: the camera/path own travel, so the clip must not move the
model across the mountain. Y remains up and the board's travel direction is +Z;
the snowboarder's body should stand sideways across the board.

Name the board mesh `Snowboard`, or set `board_node` to its mesh name in
`app/experience/content.py`. That lets the engine sample the actual board vertices
against the snow when it leans. Without that name, the base pivot is still aligned
to the slope, but exact edge contact needs checking in the preview.

One animation continues to work through `animation` as before. For an artist-supplied
three-pose rider, use names matching the GLB clips, for example:

```python
'rider': {
    'type': 'model', 'src': 'experience/media/rider.glb',
    'scale': 1.0, 'height': 2.5, 'board_node': 'Snowboard',
    'animation': 'Ride',
    'poses': {'neutral': 'Neutral', 'toe': 'Toe', 'heel': 'Heel'},
},
```

All three pose clips must exist to activate blending. Otherwise the named single
animation (or first clip) is used. Clip time and blend weights are sampled from scroll
progress, so stopping or reversing does not leave a half-finished timed transition.
Leave `poses` as `None` for the existing simple model contract.

The ring has rounded, soft rims, continuous front-card emphasis and a cheap faded
floor reflection on tiers 2/3. A small seeded particle morph adds depth in the portal;
there is no full post-processing stack. No third-party demo assets are included.

For review, add `?debug=1` to the homepage. `window.__experience.rider.bounds`
reports the projected rider rectangle as fractions of the viewport; `contactGap`
reports board clearance when a named board is available. The normal UI stays clean.
The runtime version is `bansko-3`; update `VERSION` and internal import query strings
together when modifying immutable experience assets. No npm build is needed.
