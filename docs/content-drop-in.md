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
to load restores the little geometric rider automatically.

**Opening background.** Set `hero.background_video.src` to a local H.264 MP4,
1920×1080 and under 8 MB. Set `poster` to an optional local WebP. Your video
appears over the 3D summit as a quiet full-screen layer. Headline and subline
are in `hero`; closing copy is in `finale`. Other labels live in the same file.

Leave any `src` as `None` to keep its named placeholder. The still view works
without WebGL, with reduced motion, and if the 3D cannot load. Real gallery
titles, packages, quote and booking links stay accessible in that view.
Mobile visitors receive smaller rendering settings automatically. Check your
preview on a phone after adding large videos; avoid loading all clips at once.
