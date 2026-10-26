# Browser-only proof tooling

GLTFExporter.js is three.js **0.170.0**, MIT (see app/static/vendor/THREE-LICENSE.txt).
Source: https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/exporters/GLTFExporter.js
Its `three` import is rewritten to the locally vendored module. This test-only
file is served by Playwright route interception; the homepage never loads it.
The check exports the actual placeholder rider, adds a named animation, and
saves a GLB, PNG and recorded WebM under the run's evidence/fixtures/ directory.
