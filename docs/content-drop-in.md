# Add your footage to Momentum Clips

Copy files into **app/static/experience/media/** and edit **app/experience/content.py**. Packages, prices, film titles and testimonials continue to come from the existing admin. No JavaScript build is required.

## Add a film and poster

The floating collection starts with five labelled moments from the supplied **Generated concept film**. Each has an extracted portrait poster and a start time in `films.moments`. They are chapters of one film, not five client projects. Featured database films with a supplied poster or local media join this collection once. Unillustrated database records remain on the existing gallery page, where temporary images are labelled **Concept artwork / preview pending**.

For the first database film, change `ring.cards[0].media`:

```python
{'type': 'video', 'src': 'experience/media/first-run.mp4',
 'poster': 'experience/media/first-run.webp'}
```

Use portrait 720×1280 H.264 MP4 and a matching WebP poster. Keep files under 4 MB with current Flask hosting. The poster appears on the card; the film plays with controls only when selected. Concept cards start at their configured moment and continue to the end; player controls can replay the complete film. Without local video, an existing database YouTube ID opens its player after a click. Check that the ID is a real, playable business film before publishing; seeded IDs are not proof of client work.

## Change a card image

For a poster retaining the database film destination:

```python
{'type': 'image', 'src': 'experience/media/first-run.webp'}
```

A portrait WebP around 720×1080 and under 250 KB works well. Genuine custom database thumbnails are also used. Titles/tags stay in the database. The current homepage uses featured database entries; the old manual twelve-slot ring belongs to the recoverable procedural implementation.

## Replace the journey

Set `journey.src`, `mobile_src`, `poster` and `town_poster` to new static-relative filenames. Edit its cues for timing and framing for crop. See [video-journey.md](video-journey.md). A sharper original would improve full-screen desktop quality more than upscaling the current 720p source.

## Retained model slot

The procedural rider is retained for recovery and is not loaded by the filmed journey. Its replacement contract remains:

```python
'rider': {'type': 'model', 'src': 'experience/media/rider.glb',
          'scale': 1.0, 'height': 2.5, 'animation': 'Ride',
          'board_node': 'Snowboard', 'poses': None}
```

Use GLB under 3 MB, Y-up, metres, facing +Z, embedded textures, in-place animation. Changing this slot does not add a 3D rider over the film.

Increase VERSION after content changes, deploy a preview, and check actual cards/playback on desktop and phone. Keep original footage elsewhere; this folder contains web exports.
