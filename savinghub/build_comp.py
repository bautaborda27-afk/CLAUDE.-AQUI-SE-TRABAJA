#!/usr/bin/env python3
"""Generate the HyperFrames index.html for each Saving Hub reel.

Style: "Documental Reel" (user's house style) — giant Anton caps, red/white,
word-by-word entrances (fade + blur 15->0 + scale 1.1->1), slow Ken Burns per
shot, motion-blur whips on cuts, punch-ins on key words, plates for claims,
branded end card. Timings come from <reel>/shots.json (build_base.py).
"""
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GSAP = Path.home() / ".cache/hyperframes-vendor/gsap.min.js"

# Each phrase: start, end, lines (list of lists of words), red words, style.
# A word starting with "*" is the red key word. Optional per-word times via "at".
REELS = {
    "edit-jeanlowe": {
        "punch": [2.35],
        "risers": [13.1],
        "phrases": [
            {"t": 0.10, "end": 3.30, "lines": [["¿LUJO", "FRANCÉS"], ["A", "PRECIO"], ["*ÁRABE?"]],
             "at": [0.10, 0.45, 1.85, 2.05, 2.35]},
            {"t": 3.50, "end": 5.30, "lines": [["MAISON"], ["*ALHAMBRA"]]},
            {"t": 5.50, "end": 9.00, "lines": [["JEAN", "LOWE"], ["*IMMORTEL"]]},
            {"t": 9.20, "end": 11.20, "size": "num", "lines": [["*100", "ML"]],
             "sub": "EAU DE PARFUM"},
            {"t": 11.40, "end": 13.00, "lines": [["SUBÍ", "EL"], ["*VOLUMEN"]]},
            {"t": 13.20, "end": 15.20, "lines": [["MIRÁ"], ["ESE", "*COLOR"]]},
            {"t": 15.40, "end": 17.60, "lines": [["FRESCO."], ["CÍTRICO."], ["*ADICTIVO."]],
             "at": [15.40, 15.95, 16.50]},
            {"t": 17.80, "end": 19.45, "lines": [["EL", "QUE", "TODOS"], ["TE", "VAN", "A"], ["*PREGUNTAR"]]},
        ],
        "end": {"t": 19.60, "tag": ["LUJO SIN PAGAR", "DE *MÁS"], "cta": "PEDILO POR DM"},
    },
    "edit-bharara": {
        "punch": [0.75, 2.55],
        "phrases": [
            {"t": 0.10, "end": 1.72, "lines": [["¿GASTAR", "UNA"], ["*FORTUNA"]],
             "at": [0.10, 0.40, 0.75]},
            {"t": 1.85, "end": 3.30, "lines": [["EN", "UN"], ["FRASCO"], ["*ENTERO?"]],
             "at": [1.85, 2.00, 2.20, 2.55]},
            {"t": 3.50, "end": 6.40, "lines": [["BHARARA"], ["*KING"]]},
            {"t": 6.60, "end": 8.00, "lines": [["NO", "HACE"], ["*FALTA."]]},
            {"t": 8.20, "end": 9.80, "lines": [["PROBALO"], ["EN", "*DECANT"]]},
            {"t": 10.00, "end": 14.20, "plate": True,
             "lines": [["DIRECTO", "DEL"], ["FRASCO"], ["ORIGINAL"]]},
            {"t": 14.40, "end": 16.20, "lines": [["A", "TU"], ["*DECANT"]]},
            {"t": 16.40, "end": 19.80, "lines": [["LISTO", "PARA"], ["*LLEVAR"]]},
        ],
        "end": {"t": 20.00, "tag": ["PROBÁ ANTES", "DE *COMPRAR"], "cta": "PEDILO POR DM"},
    },
}

CSS = """
@font-face { font-family: "Anton"; src: url("fonts/Anton.woff2") format("woff2"); font-display: block; }
:root { --red: #E0201B; --white: #FFFFFF; --ink: #0b0b0b; --amber: #F5A623; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: var(--ink); }
#root { position: relative; width: 1080px; height: 1920px; overflow: hidden;
  container-type: size; font-family: "Anton"; }
#cam { position: absolute; inset: 0; will-change: transform, filter;
  backface-visibility: hidden; transform-origin: 50% 55%; }
#cam video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.scrim { position: absolute; left: 0; right: 0; top: 0; height: 62cqh; pointer-events: none;
  background: linear-gradient(180deg, rgba(0,0,0,.62) 0%, rgba(0,0,0,.38) 55%, rgba(0,0,0,0) 100%); }
.vig { position: absolute; inset: 0; pointer-events: none;
  background: radial-gradient(ellipse 75% 60% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,.55) 100%); }
.flash { position: absolute; inset: 0; background: #fff; opacity: 0; pointer-events: none; }
.phrase { position: absolute; left: 4cqw; right: 4cqw; top: 9cqh; text-align: center;
  color: var(--white); text-transform: uppercase; }
.phrase .ln { display: block; font-size: 16.5cqw; line-height: 0.9; letter-spacing: 0.1cqw;
  white-space: nowrap; }
.phrase.num .ln { font-size: 34cqw; line-height: 0.86; }
.phrase .sub { display: block; margin-top: 1.6cqh; font-size: 6.4cqw; letter-spacing: 0.8cqw; }
.w { display: inline-block; opacity: 0; margin: 0 1.1cqw;
  text-shadow: 0 0.6cqw 2.4cqw rgba(0,0,0,.65), 0 0 0.4cqw rgba(0,0,0,.35); }
.w.red { color: var(--red); }
.plate { display: inline-block; padding: 2.2cqw 4.2cqw 2.8cqw; transform: rotate(-3deg);
  background:
    linear-gradient(rgba(255,255,255,.10) 1px, transparent 1px) 0 0 / 3cqw 3cqw,
    linear-gradient(90deg, rgba(255,255,255,.10) 1px, transparent 1px) 0 0 / 3cqw 3cqw,
    var(--red);
  box-shadow: 0 1.2cqw 3cqw rgba(0,0,0,.45); }
.plate .ln { font-size: 13.5cqw; }
.plate .w { text-shadow: 0 0.3cqw 0.8cqw rgba(0,0,0,.35); }
.endcard { position: absolute; inset: 0; }
.endcard .shade { position: absolute; inset: 0; background: rgba(8,8,8,.58); opacity: 0; }
.endcard .brand { position: absolute; left: 0; right: 0; top: 30cqh; text-align: center;
  color: var(--white); font-size: 21cqw; line-height: 0.88; }
.endcard .brand .w { margin: 0 1.4cqw; }
.endcard .tag { position: absolute; left: 0; right: 0; top: 52cqh; text-align: center;
  color: var(--white); font-size: 10.5cqw; line-height: 0.92; }
.endcard .tag .ln { display: block; }
.endcard .cta { position: absolute; left: 0; right: 0; top: 71cqh; text-align: center; opacity: 0; }
.endcard .cta span { display: inline-block; padding: 1.6cqw 4cqw 2cqw; background: var(--white);
  color: var(--ink); font-size: 7.4cqw; transform: rotate(-2deg);
  box-shadow: 0 1cqw 2.6cqw rgba(0,0,0,.5); }
"""


def word_span(word, idx):
    red = word.startswith("*")
    text = html.escape(word.lstrip("*"))
    return f'<span class="w{" red" if red else ""}" data-i="{idx}">{text}</span>'


def build(name, cfg):
    out = ROOT / name
    shots = json.loads((out / "shots.json").read_text())
    dur = shots["duration"]
    (out / "fonts").mkdir(exist_ok=True)
    shutil.copy(ROOT / "fonts/Anton.woff2", out / "fonts/Anton.woff2")
    (out / "vendor").mkdir(exist_ok=True)
    shutil.copy(GSAP, out / "vendor/gsap.min.js")

    body, js = [], []
    # --- camera: Ken Burns per shot + whip on each cut (alternating direction)
    js.append('tl.set("#cam", { force3D: true, scale: 1, x: 0, y: 0, filter: "blur(0px)" }, 0);')
    for i, s in enumerate(shots["shots"]):
        st, d = s["start"], s["duration"]
        zin = i % 2 == 0
        a, b = (1.0, 1.08) if zin else (1.08, 1.02)
        js.append(f'tl.fromTo("#cam", {{ scale: {a} }}, {{ scale: {b}, duration: {d - 0.02:.2f}, '
                  f'ease: "power1.inOut", immediateRender: false }}, {st});')
        if i > 0:
            dy = -90 if i % 2 else 90
            js.append(f'tl.fromTo("#cam", {{ y: {dy}, filter: "blur(18px)" }}, '
                      f'{{ y: 0, filter: "blur(0px)", duration: 0.2, ease: "power3.out", '
                      f'immediateRender: false }}, {st});')
    # punch-ins on key hits (quick zoom bump on top of the drift)
    for p in cfg["punch"]:
        js.append(f'tl.to("#root .punch", {{ scale: 1.1, duration: 0.07, ease: "power2.out" }}, {p});')
        js.append(f'tl.to("#root .punch", {{ scale: 1.0, duration: 0.35, ease: "power2.out" }}, {p + 0.07:.2f});')
        js.append(f'tl.fromTo(".flash", {{ opacity: 0.55 }}, {{ opacity: 0, duration: 0.18, '
                  f'ease: "power2.out", immediateRender: false }}, {p});')

    # --- phrases
    for n, ph in enumerate(cfg["phrases"]):
        pid = f"p{n}"
        t0, t1 = ph["t"], ph["end"]
        words, lines_html, k = [], [], 0
        for line in ph["lines"]:
            spans = []
            for w in line:
                spans.append(word_span(w, k))
                words.append(w)
                k += 1
            chars = sum(len(w.lstrip("*")) for w in line) + len(line) - 1
            fit = min(16.5, 88 / (chars * 0.47)) if ph.get("size") != "num" and not ph.get("plate") else None
            style = f' style="font-size:{fit:.2f}cqw"' if fit and fit < 16.5 else ""
            lines_html.append(f'<span class="ln"{style}>{"".join(spans)}</span>')
        inner = "".join(lines_html)
        if ph.get("plate"):
            inner = f'<div class="plate">{inner}</div>'
        if ph.get("sub"):
            inner += f'<span class="sub"><span class="w" data-i="{k}">{html.escape(ph["sub"])}</span></span>'
            words.append(ph["sub"])
        cls = "phrase" + (" num" if ph.get("size") == "num" else "")
        body.append(f'<div id="{pid}" class="clip {cls}" data-start="{t0}" '
                    f'data-duration="{t1 - t0:.2f}" data-track-index="{2 + n % 2}">'
                    f'<div class="inner">{inner}</div></div>')
        times = ph.get("at") or [t0 + 0.13 * j for j in range(len(words))]
        if len(times) < len(words):
            last = times[-1]
            times = times + [last + 0.13 * (j + 1) for j in range(len(words) - len(times))]
        for j, wt in enumerate(times):
            sel = f'#{pid} .w[data-i="{j}"]'
            js.append(f'tl.fromTo(\'{sel}\', {{ opacity: 0, scale: 1.1, filter: "blur(15px)" }}, '
                      f'{{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.15, '
                      f'ease: "power2.out", immediateRender: false }}, {wt:.2f});')
        if ph.get("plate"):
            js.append(f'tl.fromTo("#{pid} .plate", {{ scale: 0.6, rotation: -9, opacity: 0 }}, '
                      f'{{ scale: 1, rotation: -3, opacity: 1, duration: 0.3, ease: "back.out(2)", '
                      f'immediateRender: false }}, {t0:.2f});')
        # slow settle zoom on the whole phrase while it holds
        js.append(f'tl.fromTo("#{pid} .inner", {{ scale: 1 }}, {{ scale: 1.04, duration: {t1 - t0:.2f}, '
                  f'ease: "none", immediateRender: false }}, {t0:.2f});')

    # --- end card
    e = cfg["end"]
    et = e["t"]
    ed = dur - et
    tag_lines, k = [], 0
    for line in e["tag"]:
        spans = []
        for w in line.split(" "):
            spans.append(word_span(w, k))
            k += 1
        tag_lines.append(f'<span class="ln">{"".join(spans)}</span>')
    body.append(
        f'<div id="end" class="clip endcard" data-start="{et}" data-duration="{ed:.2f}" data-track-index="4">'
        f'<div class="shade"></div>'
        f'<div class="brand"><span class="w" data-b="0">SAVING</span><span class="w red" data-b="1">HUB</span></div>'
        f'<div class="tag">{"".join(tag_lines)}</div>'
        f'<div class="cta"><span>{html.escape(e["cta"])}</span></div></div>')
    js.append(f'tl.fromTo("#end .shade", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25, ease: "power2.out", immediateRender: false }}, {et});')
    js.append(f'tl.fromTo("#end .brand .w", {{ opacity: 0, scale: 1.25, filter: "blur(15px)" }}, '
              f'{{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.18, stagger: 0.14, ease: "power3.out", immediateRender: false }}, {et + 0.1:.2f});')
    js.append(f'tl.fromTo("#end .tag .w", {{ opacity: 0, scale: 1.1, filter: "blur(15px)" }}, '
              f'{{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.15, stagger: 0.1, ease: "power2.out", immediateRender: false }}, {et + 0.55:.2f});')
    js.append(f'tl.fromTo("#end .cta", {{ opacity: 0, y: 40, rotation: -6 }}, '
              f'{{ opacity: 1, y: 0, rotation: 0, duration: 0.3, ease: "back.out(2)", immediateRender: false }}, {et + 1.25:.2f});')
    js.append(f'tl.fromTo(".flash", {{ opacity: 0.5 }}, {{ opacity: 0, duration: 0.2, ease: "power2.out", immediateRender: false }}, {et});')

    doc = f"""<!doctype html>
<html lang="es" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="vendor/gsap.min.js"></script>
    <style>{CSS}</style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}"
         data-width="1080" data-height="1920">
      <div class="punch" style="position:absolute;inset:0;transform-origin:50% 50%;">
        <div id="cam">
          <video id="base" class="clip" src="base.mp4" muted playsinline
                 data-start="0" data-duration="{dur}" data-track-index="0"></video>
        </div>
      </div>
      <div class="scrim"></div>
      <div class="vig"></div>
      {chr(10).join("      " + b for b in body)}
      <div class="flash"></div>
      <audio id="master" class="clip" src="master.m4a" data-start="0" data-duration="{dur}"
             data-track-index="9" data-volume="1"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join("      " + j for j in js)}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
    (out / "index.html").write_text(doc)
    print(f"{name}: index.html written ({dur}s, {len(cfg['phrases'])} phrases)")


if __name__ == "__main__":
    for name, cfg in REELS.items():
        build(name, cfg)
