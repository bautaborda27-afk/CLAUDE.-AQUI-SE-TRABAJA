"""Write edit/index.html: the poster building itself layer by layer.

Positions come from work/layers.json (build_layers.py); the motion is below.
The bus drives in from the left and brakes; the road is drawn behind it.
"""
import json

L = json.load(open("work/layers.json"))
letters = L.pop("letters")
DUR = 10.0
FPS = 30


def box(n):
    b = L[n]
    return f'left:{b["x"]}px;top:{b["y"]}px;width:{b["w"]}px;height:{b["h"]}px'


def img(n, z, extra=""):
    return f'<img id="{n}" class="layer" src="assets/{n}.png" alt="" style="{box(n)};z-index:{z}"{extra}>'


# ---------------------------------------------------------------- timing
BUS_IN, BUS_DUR = 3.55, 2.1          # drive-in, power3.out
BUS_STOP = BUS_IN + BUS_DUR
BUS_DX, BUS_DY = -1060, -18          # start offset (off-screen left)
FRONT = 800                          # bus nose x in the final frame
FINAL_IN = 6.85                      # cross to the untouched poster

rb = L["road"]
rx_end = FRONT - rb["x"]
rx_start = rx_end + BUS_DX
oval = L["oval"]
ocx, ocy = 550 - oval["x"], 655 - oval["y"]
rays = L["rays"]
rcx, rcy = 845 - rays["x"], 1052 - rays["y"]
PIVOT = (520, 1590)                  # braking pitch pivot (canvas px)

tw = []  # timeline lines


def add(s):
    tw.append("      " + s)


# frame + hatching sweep in diagonally
add('tl.fromTo("#frame", {"--p": "-14%"}, {"--p": "104%", duration: 0.85, ease: "power2.inOut"}, 0);')
# header
add('tl.fromTo("#logo", {opacity: 0, scale: 0.82, filter: "blur(8px)"}, {opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.5, ease: "power3.out"}, 0.15);')
add('tl.fromTo("#victoria", {clipPath: "inset(0% 100% 0% 0%)", x: -40}, {clipPath: "inset(0% 0% 0% 0%)", x: 0, duration: 0.6, ease: "power3.out"}, 0.35);')
add('tl.fromTo("#whynot", {clipPath: "inset(0% 0% 0% 100%)", x: 40}, {clipPath: "inset(0% 0% 0% 0%)", x: 0, duration: 0.6, ease: "power3.out"}, 0.5);')
add('tl.fromTo("#date-sab", {opacity: 0, x: -24, filter: "blur(6px)"}, {opacity: 1, x: 0, filter: "blur(0px)", duration: 0.45, ease: "power3.out"}, 0.85);')
add('tl.fromTo("#date-imperio", {opacity: 0, x: 24, filter: "blur(6px)"}, {opacity: 1, x: 0, filter: "blur(0px)", duration: 0.45, ease: "power3.out"}, 0.9);')
add('tl.fromTo("#date-rule", {scaleX: 0}, {scaleX: 1, duration: 0.5, ease: "power2.inOut"}, 0.95);')
# TRASLADO: letters stamp in, the oval draws around them
for i, n in enumerate(letters):
    t = 1.15 + i * 0.07
    add(f'tl.fromTo("#l-{n}", {{opacity: 0, scale: 1.7, rotation: -6, filter: "blur(10px)"}}, '
        f'{{opacity: 1, scale: 1, rotation: 0, filter: "blur(0px)", duration: 0.42, ease: "power4.out"}}, {t:.2f});')
add('tl.fromTo("#oval", {"--sweep": "0deg"}, {"--sweep": "372deg", duration: 0.9, ease: "power2.inOut"}, 1.45);')


def star(n, t):
    add(f'tl.fromTo("#{n}", {{opacity: 0, scale: 0, rotation: -90}}, '
        f'{{opacity: 1, scale: 1, rotation: 0, duration: 0.55, ease: "back.out(2.2)"}}, {t:.2f});')


star("star-tl", 1.9)
star("star-tb", 2.0)


def pin(n, t, drop=70):
    add(f'tl.fromTo("#{n}", {{opacity: 0, y: -{drop}}}, {{opacity: 1, y: 0, duration: 0.5, ease: "back.out(2.2)"}}, {t:.2f});')


def unroll(n, t, frm="inset(0% 100% 0% 0%)", dur=0.5, ease="power3.out"):
    add(f'tl.fromTo("#{n}", {{clipPath: "{frm}"}}, {{clipPath: "inset(0% 0% 0% 0%)", duration: {dur}, ease: "{ease}"}}, {t:.2f});')


# route
pin("pin-raf", 2.25)
unroll("tag-raf", 2.35)
pin("pin-sun", 2.45)
unroll("tag-sun", 2.55)
unroll("arrow1", 2.7, dur=0.6, ease="power2.inOut")
unroll("arrow2", 2.8, dur=0.6, ease="power2.inOut")
pin("pin-sf", 3.15, drop=90)
unroll("tag-sf", 3.3, frm="inset(0% 50% 0% 50%)")
add(f'tl.fromTo("#rays", {{clipPath: "circle(0px at {rcx}px {rcy}px)", opacity: 0}}, '
    f'{{clipPath: "circle(190px at {rcx}px {rcy}px)", opacity: 1, duration: 0.55, ease: "power3.out"}}, 3.4);')
star("star-r1", 3.5)
star("star-r2", 3.62)

# the bus: drives in from the left, the road is drawn behind its nose
add(f'tl.fromTo("#bus-move", {{x: {BUS_DX}, y: {BUS_DY}}}, {{x: 0, y: 0, duration: {BUS_DUR}, ease: "power3.out"}}, {BUS_IN});')
add(f'tl.fromTo("#road", {{"--rx": "{rx_start}px"}}, {{"--rx": "{rx_end}px", duration: {BUS_DUR}, ease: "power3.out"}}, {BUS_IN});')
add(f'tl.fromTo("#road", {{"--rx": "{rx_end}px"}}, {{"--rx": "{rb["w"] + 140}px", duration: 0.6, ease: "power2.out", immediateRender: false}}, {BUS_STOP:.2f});')
add(f'tl.fromTo("#bus-blur", {{opacity: 0.95}}, {{opacity: 0, duration: 1.1, ease: "power2.out"}}, {BUS_IN});')
# road rumble while moving, fading out as it brakes
t, i, prev = BUS_IN, 0, 0.0
while t < BUS_STOP - 0.1:
    amp = 1.8 * (1 - (t - BUS_IN) / BUS_DUR) ** 1.5 + 0.2
    y = amp if i % 2 else -amp
    add(f'tl.fromTo("#bus-jit", {{y: {prev:.2f}}}, {{y: {y:.2f}, duration: 0.07, ease: "sine.inOut", immediateRender: false}}, {t:.3f});')
    t, i, prev = t + 0.07, i + 1, y
add(f'tl.fromTo("#bus-jit", {{y: {prev:.2f}}}, {{y: 0, duration: 0.1, ease: "sine.out", immediateRender: false}}, {t:.3f});')
# braking: nose dips, then rocks back and settles
add(f'tl.fromTo("#bus-pitch", {{rotation: 0}}, {{rotation: 0.7, duration: 0.9, ease: "sine.inOut"}}, {BUS_STOP - 0.9:.2f});')
for a, b, d, e, t0 in [(0.7, -0.35, 0.22, "power2.out", 0), (-0.35, 0.12, 0.2, "sine.inOut", 0.22), (0.12, 0, 0.25, "sine.out", 0.42)]:
    add(f'tl.fromTo("#bus-pitch", {{rotation: {a}}}, {{rotation: {b}, duration: {d}, ease: "{e}", immediateRender: false}}, {BUS_STOP + t0:.2f});')
star("star-bus", 5.8)

# footer
unroll("rule", 5.95, dur=0.55, ease="power2.inOut")
star("star-bl", 6.05)
for i in range(4):
    add(f'tl.fromTo("#sp{i + 1}", {{opacity: 0, y: 26}}, {{opacity: 1, y: 0, duration: 0.5, ease: "power3.out"}}, {6.15 + i * 0.09:.2f});')
add(f'tl.fromTo("#final", {{opacity: 0}}, {{opacity: 1, duration: 0.3, ease: "none"}}, {FINAL_IN});')

# ---------------------------------------------------------------- markup
z = 1
body = [f'<img id="plate" class="layer" src="assets/plate.png" alt="" style="left:0;top:0;width:1080px;height:1920px;z-index:{z}">']
z += 1
body.append(img("frame", z)); z += 1
body.append(img("road", z)); z += 1
bus = L["bus"]
blur = L["bus-blur"]
body.append(
    f'<div id="bus-move" class="stage" style="z-index:{z}">'
    f'<div id="bus-pitch" class="stage" style="transform-origin:{PIVOT[0]}px {PIVOT[1]}px">'
    f'<div id="bus-jit" class="stage">'
    f'<img id="bus" class="layer" src="assets/bus.png" alt="" style="{box("bus")}">'
    f'<img id="bus-blur" class="layer" src="assets/bus-blur.png" alt="" style="{box("bus-blur")}">'
    f'</div></div></div>')
z += 1
for n in ["oval"] + [f"l-{x}" for x in letters] + ["logo", "victoria", "whynot", "date-sab", "date-rule", "date-imperio",
                                                   "arrow1", "arrow2", "rays", "tag-raf", "tag-sun", "tag-sf",
                                                   "pin-raf", "pin-sun", "pin-sf", "rule", "sp1", "sp2", "sp3", "sp4",
                                                   "star-tl", "star-tb", "star-r1", "star-r2", "star-bus", "star-bl"]:
    body.append(img(n, z)); z += 1

final_dur = DUR - FINAL_IN
html = f"""<!doctype html>
<html lang="es" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="vendor/gsap.min.js"></script>
    <style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #ddcdc4; }}
#root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #ddcdc4; }}
.layer {{ position: absolute; display: block; }}
.stage {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }}
#frame {{
  --p: -14%;
  -webkit-mask-image: linear-gradient(125deg, #000 var(--p), transparent calc(var(--p) + 14%));
  mask-image: linear-gradient(125deg, #000 var(--p), transparent calc(var(--p) + 14%));
}}
#oval {{
  --sweep: 0deg;
  -webkit-mask-image: conic-gradient(from 235deg at {ocx}px {ocy}px, #000 0deg, #000 calc(var(--sweep) - 12deg), transparent var(--sweep));
  mask-image: conic-gradient(from 235deg at {ocx}px {ocy}px, #000 0deg, #000 calc(var(--sweep) - 12deg), transparent var(--sweep));
}}
#road {{
  --rx: {rx_start}px;
  -webkit-mask-image: linear-gradient(90deg, #000 calc(var(--rx) - 90px), transparent var(--rx));
  mask-image: linear-gradient(90deg, #000 calc(var(--rx) - 90px), transparent var(--rx));
}}
#final {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: {z}; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
      {chr(10).join("      " + b for b in body).lstrip()}
      <img id="final" class="clip" src="assets/poster.png" alt="" data-start="{FINAL_IN}" data-duration="{final_dur:.2f}" data-track-index="2">
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tw)}
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open("edit/index.html", "w").write(html)
print("wrote edit/index.html,", len(tw), "tweens")
