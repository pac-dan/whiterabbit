# Alpine surfaces

Generated with `scripts/build_alpine_textures.py`. Grain is original deterministic alpha noise; contours are derived from the committed Bansko heightmap. No third-party pattern images or site assets are copied. GitHub texture research and design rationale are in `.runs/2026-10-27-texture-smoothness/RESEARCH.md`.

Terrain: Mapzen / AWS Terrain Tiles. Produced using Copernicus data and information funded by the European Union — EU-DEM layers. Global SRTM and GMTED2010 courtesy of the U.S. Geological Survey. Elevations resampled. https://github.com/tilezen/joerd/blob/master/docs/attribution.md

Static, tiled grain avoids runtime SVG noise or animated grain repaints. Decorative layers do not intercept input or cover the video. CSS opacity controls their strength.
