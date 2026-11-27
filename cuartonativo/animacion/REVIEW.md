# Review: Cuarto Nativo story animation

12 s, 1080x1920, 30 fps, silent (meant to get music from Instagram's own library).

## Creative calls
- One continuous reveal of the static flyer (`../historia.html`), no scene cuts: an invitation reads as one object being unveiled.
- Order: gold frame draws from the top star (0-2 s) -> logo blurs in -> "Con Cuarto Nativo," word by word -> "despedimos / el año." written in with a left-to-right mask -> swash -> date cartouche opens from the centre, month tracks in -> invitation line -> glasses bloom from the centre (6.7 s), sparks burst at the clink (7.9 s) -> ribbon shimmer, second foil shimmer, star twinkles; full flyer holds from ~8.4 s to 12 s.
- Continuous world motion instead of moving titles: satin light drifts, gold glitter rises, champagne fizz rises from the glasses after the clink. Titles are still once landed.

## Measured
- `check` passes: no errors; one warning kept (composition file over the line budget; a single 380-line scene is still readable).
- Phone sheet at 360 px: every line readable.
- Rendered MP4 probed: h264, 1080x1920, 30 fps, 12.000 s.

## Weakest shot / with more time
- Frame 0 is only the satin ground and the first stroke of the frame (stories autoplay, so no thumbnail hook needed).
- The glasses illustration is a single engraving, so the clink is sold by the spark burst and glow, not by the glasses moving.
