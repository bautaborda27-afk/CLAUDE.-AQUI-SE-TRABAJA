---
# ============================================================================
# FRAME.md — savings.hub (Savings Hub, perfumes árabes y de diseñador)
# Taken from the account's own reels (screenshots in savinghub/referencias/).
# THIS is the Savings Hub editing style. Do NOT use the "Documental Reel" look
# (giant red/white Anton, grain) for Savings Hub videos.
# Implemented by savinghub/build_sh.py. Sizes in cqw/cqh (1cqw = 10.8px).
# ============================================================================

colors:
  bg: "#110f0d"            # dark ground (with faint cream grid)
  bg-paper: "#f2ece0"      # paper ground for the end card (with faint ink grid)
  surface: "#f6efe7"       # chapter pill
  fg: "#110f0d"            # ink: outlines, end-card text, hard shadows
  text-on-dark: "#f1ede5"  # captions on dark bars / dark ground
  emphasis: "#e1b857"      # gold keyword inside captions, serif accent on dark
  accent: "#842a36"        # burgundy serif-italic word + underline on paper
  accent-strong: "#8e1a2e" # burgundy seam pill

typography:
  caption:
    fontFamily: "Space Grotesk"   # fonts/SpaceGrotesk-700.woff2
    fontSize: "7cqw"              # bars; 6.6cqw plain under a card
    fontWeight: 700
    letterSpacing: "-0.15cqw"
    textTransform: "none"         # sentence case, never all caps
  display-headline:
    fontFamily: "Space Grotesk"
    fontSize: "10cqw"
    fontWeight: 700
  serif-accent:
    fontFamily: "Instrument Serif" # fonts/InstrumentSerif-Italic.woff2
    fontStyle: "italic"
    fontSize: "12.6cqw"            # ONE word per headline ("Listo para *regalar*")
  mono-label:
    fontFamily: "JetBrains Mono"   # pills: LA APERTURA, FRASCO + PAÑUELO, ESCRIBINOS · SAVINGS.HUB
    fontSize: "3.5cqw"
    fontWeight: 500                # 700 on the burgundy seam pill
    textTransform: "uppercase"
    letterSpacing: "0.3em-0.42em"

rounded:
  pill: "999px"
  card: "36px"        # clip card on the dark grid
  end-card: "22px"    # tilted clip card on paper
  bar: "1cqw"         # caption bars

grain: none            # clean image (finalize with GRAIN=0)
---

# savings.hub

## Layouts (the only five)

1. **Card on dark grid** — clip in a rounded card (93cqw wide, top 13cqh, 49cqh tall,
   soft drop shadow) on the dark grid. Cream mono **chapter pill** above it
   ("LA APERTURA", "LA SORPRESA"). Caption below the card, plain cream text, sentence case.
2. **Full frame** — the clip fills the frame; captions are **dark bars** (one bar per line,
   stacked), cream text, the keyword in gold. Upper third (top 15cqh).
3. **Stacked split** — two clips, top/bottom, seam at 48cqh, with a **burgundy seam pill**
   naming both ("FRASCO + PAÑUELO", second word gold). Caption bar in the bottom panel.
4. **Editorial headline** — sans + one serif-italic word + rounded underline
   ("Le Male *Elixir*" in gold on dark; "Listo para *regalar*" in burgundy on paper).
5. **End card on paper** — cream grid paper, the clip in a slightly tilted card (−1.4°, 5px ink
   border, hard 14px ink shadow), headline with a burgundy serif-italic word + underline,
   and the outlined mono pill **"ESCRIBINOS · SAVINGS.HUB"** with a hard shadow.

## Motion

- Calm and clean: hard cuts, soft whooshes, clicks on pills/captions. No whip blur, no
  flashes, no pixel reveals, no giant word-by-word caps.
- Captions appear per phrase (2–5 words), timed to the voice: rise 26px + fade, 0.28s,
  power3.out, 0.09s stagger between bars.
- Pills pop (scale 0→1, back.out(2)). The hook card may grow into full frame
  (power3.inOut, 0.55s). End card drops in (y +160, −7° → −1.4°, back.out).
- Slow eased push on every clip (scale 1.00↔1.05).

## Voice & copy

- Brand said as "Séivings Jab" (Kokoro ef_dora 1.08), written "savings.hub" / "Savings Hub".
- Captions are sentence case with normal punctuation ("Adentro venía un *pañuelo*").
- CTA: "ESCRIBINOS · SAVINGS.HUB".
