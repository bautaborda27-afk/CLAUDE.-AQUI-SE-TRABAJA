#!/usr/bin/env python3
"""Write edit/index.html: the HyperFrames graphics layer of the short film.

Transparent 1920x1080 composition with the kinetic text over the two notes
("TE BUSQUÉ POR MUCHO TIEMPO", "¡YA TE ENCONTRÉ!") and the FIN card, in the
"Documental Reel" type style (Anton, white + red keyword, word by word with
fade + blur 15->0 + scale 110->100). It is rendered as an RGBA png sequence and
laid over the film layer (fx_film.py) by finalize.sh.

The footage itself is not a <video> here on purpose: on this GPU-less machine
HyperFrames captures video frames at ~15-20 s/frame (about 40 h for the film),
so every pixel operation on the footage lives in fx_film.py instead.
"""
import json
import shutil
from pathlib import Path

from plan import END_CARD, FILM, FIN_AT, NOTE1, NOTE2, TOTAL

ROOT = Path(__file__).resolve().parent
EDIT = ROOT / "edit"
GSAP = Path.home() / ".cache/hyperframes-vendor/gsap.min.js"
W, H = 1920, 1080


def n(v):
    return f"{v:.4f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


STYLE = """
  [data-composition-id] { position: relative; width: 1920px; height: 1080px; overflow: hidden;
    container-type: size; font-family: "Anton"; background: transparent; }
  .phrase, .shake, .inner { position: absolute; inset: 0; display: flex; flex-direction: column;
    align-items: center; justify-content: center; }
  .inner { text-align: center; color: #fff; text-transform: uppercase; font-family: "Anton"; }
  .ln { display: block; line-height: 0.9; letter-spacing: 0.06cqw; white-space: nowrap; }
  .w { display: inline-block; opacity: 0; margin: 0 1.1cqw;
    text-shadow: 0 0.35cqw 1.6cqw rgba(0,0,0,.7), 0 0 0.25cqw rgba(0,0,0,.4); }
  .w.red { color: #E0201B; text-shadow: 0 0.35cqw 1.8cqw rgba(0,0,0,.85); }
  .fin-word { font-family: "Anton"; color: #fff; font-size: 13cqw; line-height: 1; letter-spacing: 2.2cqw; margin-right: -2.2cqw; }
  .fin-word span { display: inline-block; opacity: 0; }
  .fin-rule { width: 16cqw; height: 0.55cqw; margin-top: 1.6cqw; background: #E0201B;
    transform: scaleX(0); transform-origin: left center; }
"""


def sub_comp(cid, dur, body, js):
    """A standalone sub-composition (local time 0 = its mount point)."""
    steps = "\n        ".join(js)
    return f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <script src="vendor/gsap.min.js"></script>
  </head>
  <body>
    <div id="{cid}-root" data-composition-id="{cid}" data-start="0" data-duration="{n(dur)}"
         data-width="{W}" data-height="{H}">
      <style>
  @font-face {{ font-family: "Anton"; src: url("fonts/Anton.woff2") format("woff2"); font-display: block; }}
{STYLE}
      </style>
      {body}
      <script>
      (() => {{
        const tl = gsap.timeline({{ paused: true }});
        {steps}
        window.__timelines = window.__timelines || {{}};
        window.__timelines["{cid}"] = tl;
      }})();
      </script>
    </div>
  </body>
</html>
"""


def phrase(cid, note, exit_d, sizes):
    start, end = note["start"], note["end"]
    rows, js, i = [], [], 0
    for line, size in zip(note["lines"], sizes):
        words = []
        for word, t, is_red in line:
            t = t - start
            words.append(f'<span class="w{" red" if is_red else ""}" data-i="{i}">{word}</span>')
            sel = f'#{cid}-root .w[data-i="{i}"]'
            if is_red:
                js.append(f"tl.fromTo('{sel}', {{ opacity: 0, scale: 1.6, filter: \"blur(15px)\" }}, "
                          f"{{ opacity: 1, scale: 1, filter: \"blur(0px)\", duration: 0.14, ease: \"power4.out\", "
                          f"immediateRender: false }}, {n(t)});")
                # three-frame landing shake on the red keyword
                js.append(f'tl.to("#{cid}-root .shake", {{ keyframes: [{{ x: -12, duration: 0.0333 }}, '
                          f'{{ x: 9, duration: 0.0333 }}, {{ x: -4, duration: 0.0333 }}, {{ x: 0, duration: 0.0333 }}], '
                          f'ease: "none" }}, {n(t + 0.1)});')
            else:
                js.append(f"tl.fromTo('{sel}', {{ opacity: 0, scale: 1.1, filter: \"blur(15px)\" }}, "
                          f"{{ opacity: 1, scale: 1, filter: \"blur(0px)\", duration: 0.15, ease: \"power2.out\", "
                          f"immediateRender: false }}, {n(t)});")
            i += 1
        rows.append(f'<span class="ln" style="font-size:{size}cqw">{"".join(words)}</span>')
    dur = round(end - start, 4)
    x0 = round(dur - exit_d, 4)
    js.append(f'tl.fromTo("#{cid}-root .inner", {{ scale: 1 }}, {{ scale: 1.04, duration: {n(x0)}, '
              f'ease: "sine.inOut", immediateRender: false }}, 0);')
    js.append(f'tl.fromTo("#{cid}-root .w", {{ opacity: 1, y: 0, filter: "blur(0px)" }}, {{ opacity: 0, y: -40, '
              f'filter: "blur(14px)", duration: {n(exit_d)}, ease: "power2.in", immediateRender: false }}, {n(x0)});')
    body = f'<div class="phrase"><div class="shake"><div class="inner">{"".join(rows)}</div></div></div>'
    return sub_comp(cid, dur, body, js), start, dur


def fin():
    t0 = round(FIN_AT - FILM, 4)
    js = [f'tl.fromTo("#fin-root .fin-word span", {{ opacity: 0, scale: 1.25, filter: "blur(15px)" }}, '
          f'{{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.2, stagger: 0.1, ease: "power3.out", '
          f'immediateRender: false }}, {n(t0)});',
          f'tl.fromTo("#fin-root .fin-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, ease: "power3.out", '
          f'immediateRender: false }}, {n(t0 + 0.4)});',
          f'tl.fromTo("#fin-root .phrase", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.5, ease: "power1.in", '
          f'immediateRender: false }}, {n(END_CARD - 0.55)});']
    body = ('<div class="phrase"><div class="fin-word"><span>F</span><span>I</span><span>N</span></div>'
            '<div class="fin-rule"></div></div>')
    return sub_comp("fin", END_CARD, body, js), FILM, END_CARD


def build():
    (EDIT / "compositions").mkdir(exist_ok=True)
    subs = [("note-1",) + phrase("note-1", NOTE1, 0.25, [12.5, 12.5, 16.5]),
            ("note-2",) + phrase("note-2", NOTE2, 0.12, [12, 18]),
            ("fin",) + fin()]
    hosts = []
    for k, (cid, html, start, dur) in enumerate(subs):
        (EDIT / f"compositions/{cid}.html").write_text(html)
        hosts.append(f'<div id="{cid}" class="clip" data-composition-id="{cid}" '
                     f'data-composition-src="compositions/{cid}.html" data-start="{n(start)}" '
                     f'data-duration="{n(dur)}" data-track-index="{k + 1}"></div>')
    page = f"""<!doctype html>
<html lang="es" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <link rel="preload" href="fonts/Anton.woff2" as="font" type="font/woff2" crossorigin />
    <script src="vendor/gsap.min.js"></script>
    <style>
@font-face {{ font-family: "Anton"; src: url("fonts/Anton.woff2") format("woff2"); font-display: block; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: transparent; }}
#root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: transparent; }}
.font-warm {{ position: absolute; left: 0; top: 0; font-family: "Anton"; font-size: 20px; opacity: 0; }}
</style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{n(TOTAL)}"
         data-width="{W}" data-height="{H}">
      <span class="font-warm" aria-hidden="true">TE BUSQUÉ ¡YA ENCONTRÉ! FIN</span>
      {chr(10).join("      " + h for h in hosts).strip()}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
    (EDIT / "vendor").mkdir(exist_ok=True)
    shutil.copy(GSAP, EDIT / "vendor/gsap.min.js")
    (EDIT / "index.html").write_text(page)
    (EDIT / "overlays.json").write_text(json.dumps(
        [{"id": cid, "start": start, "duration": dur} for cid, _, start, dur in subs], indent=1))
    print("index.html + " + ", ".join(f"{c} @{s}s" for c, _, s, _ in subs))


if __name__ == "__main__":
    build()
