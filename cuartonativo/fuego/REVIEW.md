# Review: Cuarto Nativo, fire version (drawn on the burnt sheet)

13 s, 1080x1920, 30 fps, silent (music to be added in Instagram).

## How it is built
- `tools/build_layers.py` splits `../assets/original_fuego.webp` into a clean burnt sheet (`assets/paper.jpg`)
  and exact per-element layers (`assets/el/*.png`). Unlike the paper version, the lettering here is lighter
  than the sheet and carries a dark shadow, so ink is found as "lighter than a 25th-percentile paper estimate",
  glyph interiors are filled, regions are widened to take the shadow, and the alpha is solved both ways
  (lighter and darker than the sheet). Grain is borrowed only from the sheet's interior, never its torn edge.
- Lettering: gold pencil outline, then the gold ink with a glowing ember front, then the outline lifts.
- The 3D star ignites (flare + spin-in); dividers open from their star; light passes over the gold at the end.
- World motion: firelight drifting (soft-light) and embers rising (canvas, seeded, a function of time).

## Order
logo 0.4 · star 1.0 · "Con" 2.0 · "CUARTO NATIVO," 2.4 · "DESPEDIMOS" 3.6 · "EL AÑO." 4.9 · divider 6.0 ·
date 6.4 · lower line 7.3 · "Te invitamos a ser parte." 7.8-9.6 · shine over the gold 9.9-11.5; hold to 13 s.

## Measured
- `check` passes: no errors. Kept warning `duplicate_media_discovery_risk`: the ink and its ember edge
  deliberately use the same still image.
- Rendered MP4 probed: h264, 1080x1920, 30 fps, 13.000 s.

## Weakest point
- Under the headline the clean sheet is a smoother, darker band than the rest of the paper (it fills a
  large lettered area); it reads as scorch, and it is covered once the text is written.
