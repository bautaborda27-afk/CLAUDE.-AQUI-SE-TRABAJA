# Review: Cuarto Nativo, paper version (drawn on the sheet)

15 s, 1080x1920, 30 fps, silent (music to be added in Instagram).

## How it is built
- `tools/build_layers.py` splits the supplied flyer (`../assets/original_papel.webp`) into a clean sheet
  (`assets/paper.jpg`: ink detected against the local paper colour, inpainted, real paper grain borrowed
  back into the filled areas) and one ink layer per element (`assets/el/*.png`), each exact over the
  clean sheet, so the last frame matches the original flyer.
- Lettering gets a pencil-outline pass first (`*_sketch.png`), then the ink chases it and the outline lifts.
- Ribbons are revealed by a soft brush that follows each ribbon (SVG masks `pp-b-*`); the disco ball is
  drawn round (conic sweep), its chain top-down, its rays outward; the oval is drawn round; the divider
  opens from its star; stars pop.

## Order
logo 0.3 · top-left ribbon 0.5 · chain / ball / rays 0.8-3.0 · "Con" 2.0 · "Cuarto Nativo," 2.6 ·
"despedimos" 3.9 · "el año." 5.0 · swash 6.1 · right ribbon 6.3 · oval 6.9 · date 7.6 · side stars 8.7 ·
tagline 9.0 · divider 10.3 · bottom ribbons 10.6-12.9 · glints on the ball and star twinkles 12.7-14.5;
complete flyer holds from 12.9 s to 15 s.

## Measured
- `check` passes with no errors or warnings (only the info note that there is no sound).
- Frame 0 is the bare sheet (checked: nothing drawn before its time).
- Rendered MP4 probed: h264, 1080x1920, 30 fps, 15.000 s.

## Weakest point
- The clean sheet loses the crease lines that ran under the inked areas (they come back as each element is drawn).
