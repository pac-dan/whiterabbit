# Media drop-in

Configure files in `app/experience/content.py`; paths start at static/, for example `experience/media/first-run.mp4`. See [the owner guide](../../../../docs/content-drop-in.md).

* Journey: bansko-descent-720-v3.mp4 and bansko-descent-540-v3.mp4 are silent responsive derivatives of the owner's generated 720p source. Only one loads. Sharp opening/town WebP posters remain from the source. See [timing and delivery](../../../../docs/video-journey.md).
* Floating films: ring.cards[i].media supplies local src and optional poster for the corresponding featured database film. Prefer portrait 720×1280 H.264 MP4 under 4 MB and WebP poster under 250 KB. Playback is explicit.
* Images: portrait WebP/JPEG/PNG; use an honest frame from the actual film. Missing posters are labelled unavailable.
* Retained procedural slots: GLB under 3 MB, Y-up/metres/+Z, embedded textures and in-place animation; gate/portal images 1200×1600 WebP. These are not rendered by the current video homepage.

Keep originals elsewhere. Use new filenames and increment VERSION for changed media. Older bansko-journey-v2.mp4 remains for recovery; the refinement does not request it.
