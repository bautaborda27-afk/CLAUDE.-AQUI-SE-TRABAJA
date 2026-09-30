#!/usr/bin/env python3
"""motion-elegante — genera un proyecto HyperFrames de motion graphics lentos y
elegantes a partir de una marca (brand.json) y un guion de escenas (spec.json).

    python3 build.py <proyecto>/spec.json

Escribe index.html, fonts/, media/, vendor/ y master.m4a (si hay música) en la
misma carpeta del spec. Después: `npx hyperframes lint` y `npx hyperframes render`.

Sistema de movimiento (igual en todas las escenas):
  - ENTRADA lenta: máscara + desenfoque → nítido, expo.out, ~1.2 s, escalonada.
  - ÍCONOS que se dibujan solos (trazo 0→100 %), y se "desdibujan" al salir.
  - RESPIRACIÓN: la escena crece 3 % durante toda su duración (sine.inOut).
  - SALIDA: todo sube, se desenfoca y se apaga ~0.9 s antes del corte.
  - Fondo global continuo (color de marca + luz suave que se desplaza + grano).
"""
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
FONTS = SKILL / "assets/fonts"
ICONS = json.loads((SKILL / "assets/icons/tabler-outline.json").read_text())
GSAP = Path.home() / ".cache/hyperframes-vendor/gsap.min.js"
HF_VERSION = "0.8.97"

FORMATS = {"vertical": (1080, 1920), "horizontal": (1920, 1080), "cuadrado": (1080, 1080)}
DEFAULT_DUR = {"titulo": 4.0, "icono": 4.0, "iconos": 5.0, "pasos": 6.0, "dato": 4.0,
               "imagen": 4.5, "frase": 5.0, "cierre": 4.5}
EXIT = 0.9          # segundos de salida al final de cada escena
IN_EASE = "expo.out"


# ---------------------------------------------------------------- helpers
def esc(s):
    return html.escape(str(s))


def rich(s):
    """'Lujo *sin pagar* de más' -> la parte entre asteriscos en itálica y color de acento."""
    parts = re.split(r"\*(.+?)\*", str(s))
    return "".join(f'<em class="ac">{esc(p)}</em>' if i % 2 else esc(p) for i, p in enumerate(parts))


def lines(ls, cls="ln"):
    if isinstance(ls, str):
        ls = [ls]
    return "".join(f'<span class="mask"><span class="{cls}">{rich(l)}</span></span>' for l in ls)


def icon(name, cls="ic"):
    if name not in ICONS:
        close = [k for k in ICONS if name in k][:8]
        sys.exit(f"Ícono '{name}' no existe. Parecidos: {', '.join(close) or '—'}")
    body = re.sub(r"<(path|circle|line|rect|polyline|polygon|ellipse)\b",
                  r'<\1 pathLength="1" class="d"', ICONS[name])
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-linecap="round" stroke-linejoin="round">{body}</svg>')


def font_face(family, file, weight, style, brand_dir):
    for base in (brand_dir, FONTS):
        if (base / file).exists():
            return family, base / file, weight, style
    sys.exit(f"No encuentro la fuente {file} (ni en la carpeta de la marca ni en assets/fonts)")


# ---------------------------------------------------------------- composición
class Comp:
    def __init__(self, brand, fmt):
        self.brand, self.fmt = brand, fmt
        self.html, self.top, self.js, self.media = [], [], [], []
        self.n = 0

    # --- primitivas de movimiento
    def rise(self, sel, t, stagger=0.14, dur=1.3):
        """Líneas de texto que suben desde su máscara, desenfocadas → nítidas."""
        self.js.append(f'tl.fromTo("{sel} .ln", {{ yPercent: 105, opacity: 0, filter: "blur(10px)" }}, '
                       f'{{ yPercent: 0, opacity: 1, filter: "blur(0px)", duration: {dur}, ease: "{IN_EASE}", '
                       f'stagger: {stagger}, immediateRender: true }}, {t:.2f});')

    def fade(self, sel, t, y=36, dur=1.2, stagger=0.0, scale=1.0, x=0):
        self.js.append(f'tl.fromTo("{sel}", {{ x: {x}, y: {y}, scale: {scale}, opacity: 0, filter: "blur(8px)" }}, '
                       f'{{ x: 0, y: 0, scale: 1, opacity: 1, filter: "blur(0px)", duration: {dur}, ease: "{IN_EASE}", '
                       f'stagger: {stagger}, immediateRender: true }}, {t:.2f});')

    def draw(self, sel, t, dur=1.8, stagger=0.1):
        """Los trazos del ícono se dibujan solos."""
        self.js.append(f'tl.fromTo("{sel} .d", {{ strokeDashoffset: 1, opacity: 0 }}, '
                       f'{{ strokeDashoffset: 0, opacity: 1, duration: {dur}, ease: "power2.inOut", '
                       f'stagger: {stagger}, immediateRender: true }}, {t:.2f});')

    def line_in(self, sel, t, dur=1.2, origin="left"):
        self.js.append(f'tl.fromTo("{sel}", {{ scaleX: 0, transformOrigin: "{origin} center" }}, '
                       f'{{ scaleX: 1, duration: {dur}, ease: "expo.inOut", immediateRender: true }}, {t:.2f});')

    def exit(self, sid, t, d):
        """Salida común: bloques .out suben y se apagan; los íconos se desdibujan."""
        te = t + d - EXIT
        self.js.append(f'tl.fromTo("#{sid} .d", {{ strokeDashoffset: 0 }}, {{ strokeDashoffset: -1, '
                       f'duration: {EXIT - 0.1:.2f}, ease: "power2.in", immediateRender: false }}, {te:.2f});')
        self.js.append(f'tl.fromTo("#{sid} .out", {{ y: 0, opacity: 1, filter: "blur(0px)" }}, '
                       f'{{ y: -40, opacity: 0, filter: "blur(10px)", duration: {EXIT - 0.15:.2f}, ease: "power2.in", '
                       f'stagger: {{ each: 0.06, from: "end" }}, immediateRender: false }}, {te:.2f});')

    def scene(self, t, d, inner, kind):
        self.n += 1
        sid = f"s{self.n}"
        self.html.append(f'<section id="{sid}" class="clip scene {kind}" data-start="{t:.2f}" data-duration="{d:.2f}" '
                         f'data-track-index="{1 + self.n % 2}"><div class="inner">{inner}</div></section>')
        self.js.append(f'tl.fromTo("#{sid} .inner", {{ scale: 1 }}, {{ scale: 1.03, duration: {d:.2f}, '
                       f'ease: "sine.inOut", immediateRender: true }}, {t:.2f});')
        self.exit(sid, t, d)
        return sid

    def kicker(self, text):
        return f'<div class="out"><div class="kicker">{esc(text)}</div></div>' if text else ""

    # --- escenas
    def titulo(self, t, d, lineas, kicker="", sub=""):
        inner = (f'<div class="stack">{self.kicker(kicker)}<div class="out"><h1 class="h1">{lines(lineas)}</h1></div>'
                 f'<div class="out"><div class="rule"></div></div>'
                 + (f'<div class="out"><p class="sub">{rich(sub)}</p></div>' if sub else "") + '</div>')
        sid = self.scene(t, d, inner, "titulo")
        self.fade(f"#{sid} .kicker", t + 0.1, y=20)
        self.rise(f"#{sid} .h1", t + 0.3)
        self.line_in(f"#{sid} .rule", t + 0.9, origin="center")
        if sub:
            self.fade(f"#{sid} .sub", t + 1.2, y=24)

    def icono(self, t, d, icono, titulo, kicker="", sub=""):
        inner = (f'<div class="stack">{self.kicker(kicker)}'
                 f'<div class="out"><div class="badge">{self.ring()}{icon(icono)}</div></div>'
                 f'<div class="out"><h2 class="h2">{lines(titulo)}</h2></div>'
                 + (f'<div class="out"><p class="sub">{rich(sub)}</p></div>' if sub else "") + '</div>')
        sid = self.scene(t, d, inner, "icono")
        self.fade(f"#{sid} .kicker", t + 0.1, y=20)
        self.draw(f"#{sid} .badge .ring", t + 0.1, dur=1.6)
        self.draw(f"#{sid} .badge .ic", t + 0.4, dur=1.9, stagger=0.14)
        self.rise(f"#{sid} .h2", t + 0.9)
        if sub:
            self.fade(f"#{sid} .sub", t + 1.3, y=24)

    def iconos(self, t, d, titulo, items, kicker=""):
        its = "".join(f'<div class="out item i{j}"><div class="badge sm">{self.ring()}{icon(it["icono"])}</div>'
                      f'<p class="cap">{rich(it["texto"])}</p></div>' for j, it in enumerate(items))
        inner = (f'<div class="stack">{self.kicker(kicker)}<div class="out"><h2 class="h2">{lines(titulo)}</h2></div>'
                 f'<div class="items n{len(items)}">{its}</div></div>')
        sid = self.scene(t, d, inner, "iconos")
        self.fade(f"#{sid} .kicker", t + 0.1, y=20)
        self.rise(f"#{sid} .h2", t + 0.2)
        for j in range(len(items)):
            tj = t + 0.8 + j * 0.35
            self.draw(f"#{sid} .i{j} .ring", tj, dur=1.4)
            self.draw(f"#{sid} .i{j} .ic", tj + 0.25, dur=1.6)
            self.fade(f"#{sid} .i{j} .cap", tj + 0.6, y=18)

    def pasos(self, t, d, titulo, items, kicker=""):
        its = "".join(f'<div class="out step p{j}"><span class="num">{j + 1:02d}</span>'
                      f'<div class="badge xs">{icon(it["icono"])}</div><p class="stx">{rich(it["texto"])}</p></div>'
                      for j, it in enumerate(items))
        inner = (f'<div class="stack">{self.kicker(kicker)}<div class="out"><h2 class="h2">{lines(titulo)}</h2></div>'
                 f'<div class="steps"><div class="spine"></div>{its}</div></div>')
        sid = self.scene(t, d, inner, "pasos")
        self.fade(f"#{sid} .kicker", t + 0.1, y=20)
        self.rise(f"#{sid} .h2", t + 0.2)
        self.js.append(f'tl.fromTo("#{sid} .spine", {{ scaleY: 0, transformOrigin: "center top" }}, '
                       f'{{ scaleY: 1, duration: {min(2.4, d - 2.5):.2f}, ease: "power2.inOut", immediateRender: true }}, {t + 0.7:.2f});')
        span = max(0.5, min(0.7, (d - 3.2) / max(1, len(items))))
        for j in range(len(items)):
            tj = t + 0.8 + j * span
            self.fade(f"#{sid} .p{j} .num", tj, y=0, scale=0.6)
            self.draw(f"#{sid} .p{j} .ic", tj + 0.1, dur=1.4)
            self.fade(f"#{sid} .p{j} .stx", tj + 0.25, y=0, x=40)

    def dato(self, t, d, valor, texto, prefijo="", sufijo="", decimales=0, porcentaje=1.0, kicker=""):
        inner = (f'<div class="stack">{self.kicker(kicker)}<div class="out"><div class="dial">'
                 f'<svg class="dring" viewBox="0 0 100 100"><circle class="track" cx="50" cy="50" r="46"/>'
                 f'<circle class="arc" pathLength="1" cx="50" cy="50" r="46"/></svg>'
                 f'<div class="val"><span class="pre">{esc(prefijo)}</span><span class="n">0</span>'
                 f'<span class="suf">{esc(sufijo)}</span></div></div></div>'
                 f'<div class="out"><p class="sub big">{rich(texto)}</p></div></div>')
        sid = self.scene(t, d, inner, "dato")
        self.fade(f"#{sid} .kicker", t + 0.1, y=20)
        self.fade(f"#{sid} .dial", t + 0.1, y=0, scale=0.92, dur=1.4)
        self.js.append(f'tl.fromTo("#{sid} .arc", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: {1 - porcentaje:.3f}, '
                       f'duration: 2.0, ease: "power3.inOut", immediateRender: true }}, {t + 0.3:.2f});')
        self.js.append(f'(() => {{ const o = {{ v: 0 }}; const el = document.querySelector("#{sid} .n"); '
                       f'const f = (v) => v.toFixed({decimales}).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ".");'
                       f' tl.fromTo(o, {{ v: 0 }}, {{ v: {valor}, duration: 2.0, ease: "power3.inOut", immediateRender: true,'
                       f' onUpdate: () => {{ el.textContent = f(o.v); }} }}, {t + 0.3:.2f}); }})();')
        self.fade(f"#{sid} .sub", t + 1.4, y=24)

    def imagen(self, t, d, archivo, titulo="", sub="", kicker=""):
        src = self.add_media(archivo)
        is_video = src.lower().endswith((".mp4", ".mov", ".webm"))
        if is_video:
            # regla HyperFrames: un <video data-start> no puede ir dentro de otro elemento con data-start,
            # así que el video vive en una capa propia, fuera de la escena.
            vid = f"v{len(self.top) + 1}"
            vframe = (f'<div class="frame vframe"><div class="push"><video id="{vid}" class="clip" src="{src}" '
                      f'muted playsinline data-start="{t:.2f}" data-duration="{d:.2f}" data-track-index="5"></video></div></div>')
            media = '<div class="frame ghost"></div>'
            self.top.append(("VIDEO", vid, vframe))
        else:
            media = f'<div class="frame"><div class="push"><img src="{src}" alt=""/></div></div>'
        inner = (f'<div class="stack media">{self.kicker(kicker)}<div class="out fr">{media}</div>'
                 + (f'<div class="out"><h2 class="h2">{lines(titulo)}</h2></div>' if titulo else "")
                 + (f'<div class="out"><p class="sub">{rich(sub)}</p></div>' if sub else "") + '</div>')
        if is_video:
            # capa de video con el mismo esqueleto que la escena (copias invisibles) para que el cuadro coincida
            ghost = inner.replace('<div class="frame ghost"></div>', vframe).replace('class="out', 'class="ghost-copy')
            ghost = ghost.replace('class="ghost-copy fr"', 'class="fr"')
            self.top[-1] = f'<div class="media-layer inner" id="{vid}w">{ghost}</div>'
        sid = self.scene(t, d, inner, "imagen")
        target = f"#{vid}w .vframe" if is_video else f"#{sid} .frame"
        self.js.append(f'tl.fromTo("{target}", {{ clipPath: "inset(12% 12% 12% 12% round 2.2cqmin)", opacity: 0 }}, '
                       f'{{ clipPath: "inset(0% 0% 0% 0% round 2.2cqmin)", opacity: 1, duration: 1.6, ease: "expo.inOut", '
                       f'immediateRender: true }}, {t + 0.1:.2f});')
        self.js.append(f'tl.fromTo("{target} .push", {{ scale: 1.18 }}, {{ scale: 1.02, duration: {d:.2f}, '
                       f'ease: "power1.out", immediateRender: true }}, {t:.2f});')
        if is_video:
            self.js.append(f'tl.fromTo("#{vid}w", {{ scale: 1 }}, {{ scale: 1.03, duration: {d:.2f}, '
                           f'ease: "sine.inOut", immediateRender: true }}, {t:.2f});')
            te = t + d - EXIT
            self.js.append(f'tl.fromTo("#{vid}w .vframe", {{ opacity: 1, filter: "blur(0px)" }}, {{ opacity: 0, '
                           f'filter: "blur(10px)", duration: {EXIT - 0.15:.2f}, ease: "power2.in", immediateRender: false }}, {te + 0.1:.2f});')
        self.fade(f"#{sid} .kicker", t + 0.2, y=20)
        if titulo:
            self.rise(f"#{sid} .h2", t + 0.8)
        if sub:
            self.fade(f"#{sid} .sub", t + 1.2, y=24)

    def frase(self, t, d, texto, autor=""):
        words = str(texto).split()
        acc, out = False, []
        for w in words:
            start, end = w.startswith("*"), w.endswith("*")
            acc = acc or start
            core = w.strip("*")
            out.append(f'<span class="w{" ac" if acc else ""}">{esc(core)}</span>')
            if end:
                acc = False
        inner = (f'<div class="stack"><div class="out"><div class="quote-mark">“</div></div>'
                 f'<div class="out"><p class="quote">{" ".join(out)}</p></div>'
                 + (f'<div class="out"><div class="rule"></div></div><div class="out"><p class="kicker">{esc(autor)}</p></div>' if autor else "")
                 + '</div>')
        sid = self.scene(t, d, inner, "frase")
        self.fade(f"#{sid} .quote-mark", t + 0.1, y=0, scale=0.8, dur=1.6)
        each = min(0.16, (d - 3.0) / max(1, len(words)))
        self.js.append(f'tl.fromTo("#{sid} .quote .w", {{ opacity: 0, y: 14, filter: "blur(8px)" }}, '
                       f'{{ opacity: 1, y: 0, filter: "blur(0px)", duration: 1.0, ease: "power2.out", stagger: {each:.3f}, '
                       f'immediateRender: true }}, {t + 0.4:.2f});')
        if autor:
            ta = t + 0.6 + each * len(words)
            self.line_in(f"#{sid} .rule", ta, origin="center")
            self.fade(f"#{sid} p.kicker", ta + 0.3, y=16)

    def cierre(self, t, d, tagline="", cta=""):
        logo = self.brand.get("logo") or {"tipo": "texto", "texto": self.brand["nombre"]}
        kind = logo.get("tipo", "texto")
        if kind == "archivo":
            mark = f'<img class="logo-img" src="{self.add_media(logo["archivo"], brand=True)}" alt=""/>'
        elif kind == "icono":
            mark = f'<div class="badge">{self.ring()}{icon(logo["icono"])}</div>'
        else:
            mark = ""
        word = logo.get("texto", self.brand["nombre"])
        letters = "".join(f'<span class="L">{esc(c) if c != " " else "&nbsp;"}</span>' for c in word)
        inner = (f'<div class="stack">'
                 + (f'<div class="out"><div class="mark">{mark}</div></div>' if mark else "")
                 + f'<div class="out"><div class="wordmark">{letters}</div></div>'
                 + (f'<div class="out"><div class="rule"></div></div><div class="out"><p class="sub">{rich(tagline)}</p></div>' if tagline else "")
                 + (f'<div class="out"><div class="cta"><span>{esc(cta)}</span></div></div>' if cta else "")
                 + '</div>')
        sid = self.scene(t, d, inner, "cierre")
        tt = t + 0.1
        if kind == "archivo":
            self.fade(f"#{sid} .logo-img", tt, y=0, scale=0.9, dur=1.6)
            tt += 0.6
        elif kind == "icono":
            self.draw(f"#{sid} .mark .ring", tt, dur=1.5)
            self.draw(f"#{sid} .mark .ic", tt + 0.3, dur=1.8)
            tt += 0.8
        self.js.append(f'tl.fromTo("#{sid} .wordmark .L", {{ opacity: 0, y: 30, filter: "blur(10px)" }}, '
                       f'{{ opacity: 1, y: 0, filter: "blur(0px)", duration: 1.2, ease: "{IN_EASE}", stagger: 0.05, '
                       f'immediateRender: true }}, {tt:.2f});')
        tt += 0.6 + 0.05 * len(word)
        if tagline:
            self.line_in(f"#{sid} .rule", tt, origin="center")
            self.fade(f"#{sid} .sub", tt + 0.2, y=20)
            tt += 0.6
        if cta:
            self.fade(f"#{sid} .cta", tt, y=20)

    def ring(self):
        return ('<svg class="ring" viewBox="0 0 100 100" fill="none"><circle pathLength="1" class="d" '
                'cx="50" cy="50" r="48"/></svg>')

    def add_media(self, archivo, brand=False):
        base = self.brand_dir if brand else self.spec_dir
        src = (base / archivo).resolve()
        if not src.exists():
            sys.exit(f"No encuentro el archivo {src}")
        self.media.append(src)
        return f"media/{src.name}"


# ---------------------------------------------------------------- estilos
def css(brand, fmt, faces):
    c = brand["colores"]
    ff = "\n".join(f'@font-face {{ font-family: "{fam}"; src: url("fonts/{p.name}") format("woff2"); '
                   f'font-weight: {w}; font-style: {s}; font-display: block; }}' for fam, p, w, s in faces)
    caps = "uppercase" if brand.get("estilo", {}).get("titulos_mayuscula") else "none"
    vertical = fmt == "vertical"
    square = fmt == "cuadrado"
    return ff + f"""
:root {{ --bg: {c["fondo"]}; --surface: {c.get("superficie", c["fondo"])}; --ink: {c["texto"]};
  --accent: {c["acento"]}; --muted: {c.get("suave", c["texto"])}; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 100%; height: 100%; overflow: hidden; background: var(--bg); }}
#root {{ position: relative; width: 100%; height: 100%; overflow: hidden; container-type: size;
  background: var(--bg); color: var(--ink); font-family: "Body", sans-serif; }}
.glow {{ position: absolute; width: 120cqmax; height: 120cqmax; left: 50%; top: 50%; margin: -60cqmax 0 0 -60cqmax;
  background: radial-gradient(closest-side, color-mix(in srgb, var(--accent) 22%, transparent), transparent 70%);
  opacity: .55; }}
.vignette {{ position: absolute; inset: 0; background: radial-gradient(ellipse at center, transparent 45%,
  color-mix(in srgb, var(--bg) 85%, black) 100%); }}
.grain {{ position: absolute; inset: 0; opacity: .09; mix-blend-mode: overlay; background-size: 256px 256px;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='256' height='256'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' seed='7' stitchTiles='stitch'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>"); }}
.frame-line {{ position: absolute; inset: 3.2cqmin; border: 1px solid color-mix(in srgb, var(--muted) 35%, transparent); }}
.hud {{ position: absolute; left: 6cqmin; right: 6cqmin; top: 5.2cqmin; display: flex; justify-content: space-between;
  font: 600 {"2.1cqmin" if vertical else "1.7cqmin"} "Body"; letter-spacing: .45cqmin; text-transform: uppercase; color: var(--muted); z-index: 40; }}
.hud .dot {{ display: inline-block; width: 1cqmin; height: 1cqmin; border-radius: 50%; background: var(--accent);
  margin-right: 1.2cqmin; vertical-align: .15cqmin; }}
.prog {{ position: absolute; left: 6cqmin; right: 6cqmin; bottom: 5.2cqmin; height: 2px; background: var(--accent);
  transform-origin: left center; z-index: 40; opacity: .8; }}
.scene {{ position: absolute; inset: 0; z-index: 10; }}
.inner {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  padding: {"14cqmin 8cqmin" if vertical else "8cqmin 12cqmin"}; }}
.stack {{ display: flex; flex-direction: column; align-items: center; text-align: center; gap: {"4.5cqmin" if vertical else "3.2cqmin"};
  max-width: {"88cqw" if vertical else "70cqw"}; }}
.kicker {{ font: 600 {"2.7cqmin" if vertical else "2.1cqmin"} "Body"; letter-spacing: .7cqmin; text-transform: uppercase; color: var(--accent); }}
.mask {{ display: block; overflow: hidden; padding: .06em .1em .14em; margin: -.06em 0 -.14em; }}
.ln {{ display: block; will-change: transform; }}
.h1 {{ font: 500 {"17cqmin" if vertical else "11cqmin"}/1.02 "Display", serif; letter-spacing: -.02em;
  text-transform: {caps}; font-weight: 500; }}
.h2 {{ font: 500 {"11.5cqmin" if vertical else "7.4cqmin"}/1.05 "Display", serif; letter-spacing: -.015em; text-transform: {caps}; }}
.ac {{ font-style: italic; color: var(--accent); }}
.sub {{ font: 400 {"3.9cqmin" if vertical else "2.9cqmin"}/1.5 "Body"; color: var(--muted); max-width: {"80cqmin" if vertical else "64cqmin"}; }}
.sub.big {{ font-size: {"4.6cqmin" if vertical else "3.4cqmin"}; color: var(--ink); }}
.rule {{ width: {"18cqmin" if vertical else "14cqmin"}; height: 2px; background: var(--accent); }}
.badge {{ position: relative; width: {"42cqmin" if vertical else "30cqmin"}; height: {"42cqmin" if vertical else "30cqmin"}; display: flex; align-items: center; justify-content: center; color: var(--ink); }}
.badge .ring {{ position: absolute; inset: 0; width: 100%; height: 100%; stroke: var(--accent); stroke-width: .6; }}
.badge .ic {{ width: 48%; height: 48%; stroke-width: 1.1; }}
.badge.sm {{ width: {"23cqmin" if vertical else "19cqmin"}; height: {"23cqmin" if vertical else "19cqmin"}; flex: 0 0 auto; }}
.badge.sm .ring {{ stroke-width: .8; }}
.badge.xs {{ width: {"9cqmin" if vertical else "7.5cqmin"}; height: {"9cqmin" if vertical else "7.5cqmin"}; flex: 0 0 auto; }}
.badge.xs .ic {{ width: 100%; height: 100%; stroke-width: 1.3; color: var(--accent); }}
.d {{ stroke-dasharray: 1 1; stroke-dashoffset: 1; }}
.items {{ display: flex; flex-direction: {"column" if vertical else "row"}; flex-wrap: {"nowrap" if vertical else "wrap"}; justify-content: center; align-items: {"flex-start" if vertical else "center"}; gap: {"4.5cqmin" if vertical else "4cqmin 7cqmin"}; margin-top: 2cqmin; }}

.item {{ display: flex; flex-direction: {"row" if vertical else "column"}; align-items: center; gap: {"5cqmin" if vertical else "2.2cqmin"}; width: {"auto" if vertical else "24cqmin"}; text-align: {"left" if vertical else "center"}; }}
.cap {{ font: 600 {"3.3cqmin" if vertical else "2.3cqmin"}/1.35 "Body"; letter-spacing: .2cqmin; text-transform: uppercase; }}
.steps {{ position: relative; display: flex; flex-direction: column; gap: {"6.5cqmin" if vertical else "3.4cqmin"}; margin-top: 3cqmin; text-align: left; }}
.spine {{ position: absolute; left: {"4cqmin" if vertical else "3.1cqmin"}; top: 1cqmin; bottom: 1cqmin; width: 1px; background: color-mix(in srgb, var(--muted) 50%, transparent); }}
.step {{ position: relative; display: flex; align-items: center; gap: 3.2cqmin; }}
.num {{ position: relative; flex: 0 0 {"8cqmin" if vertical else "6.2cqmin"}; height: {"8cqmin" if vertical else "6.2cqmin"}; border-radius: 50%; background: var(--bg);
  border: 1px solid var(--accent); display: flex; align-items: center; justify-content: center;
  font: 600 {"2.5cqmin" if vertical else "1.9cqmin"} "Body"; color: var(--accent); letter-spacing: .1cqmin; }}
.stx {{ font: 400 {"5cqmin" if vertical else "3.8cqmin"}/1.3 "Display", serif; }}
.dial {{ position: relative; width: {"72cqmin" if vertical else "46cqmin"}; height: {"72cqmin" if vertical else "46cqmin"}; }}
.dring {{ position: absolute; inset: 0; width: 100%; height: 100%; transform: rotate(-90deg); fill: none; }}
.dring .track {{ stroke: color-mix(in srgb, var(--muted) 30%, transparent); stroke-width: .5; }}
.dring .arc {{ stroke: var(--accent); stroke-width: .9; stroke-linecap: round; stroke-dasharray: 1 1; stroke-dashoffset: 1; }}
.val {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  font: 500 {"21cqmin" if vertical else "12cqmin"} "Display", serif; font-variant-numeric: lining-nums tabular-nums; }}
.val .pre, .val .suf {{ font-size: .45em; color: var(--accent); font-style: italic; margin: 0 .08em; }}
.media .fr {{ width: {"78cqw" if vertical else "62cqw" if square else "40cqw"}; }}
.ghost-copy {{ visibility: hidden; }}
.frame {{ position: relative; width: 100%; aspect-ratio: {"4 / 5" if vertical else "4 / 3" if square else "16 / 10"}; overflow: hidden;
  border-radius: 2.2cqmin; background: var(--surface); }}
.frame.ghost {{ background: transparent; }}
.frame .push {{ position: absolute; inset: 0; }}
.frame img, .frame video {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.media-layer {{ position: absolute; inset: 0; z-index: 5; display: flex; align-items: center; justify-content: center; pointer-events: none; }}
.quote-mark {{ font: 500 {"32cqmin" if vertical else "24cqmin"}/.6 "Display", serif; color: var(--accent); height: 10cqmin; }}
.quote {{ font: 500 {"9.4cqmin" if vertical else "5.6cqmin"}/1.2 "Display", serif; letter-spacing: -.01em; }}
.quote .w {{ display: inline-block; }}
.quote .w.ac {{ font-style: italic; color: var(--accent); }}
.mark .badge {{ width: {"34cqmin" if vertical else "26cqmin"}; height: {"34cqmin" if vertical else "26cqmin"}; }}
.logo-img {{ height: {"26cqmin" if vertical else "20cqmin"}; width: auto; max-width: 60cqmin; object-fit: contain; display: block; }}
.wordmark {{ font: 500 {"12.5cqmin" if vertical else "9cqmin"}/1 "Display", serif; letter-spacing: .12em; text-transform: uppercase; white-space: nowrap; }}
.wordmark .L {{ display: inline-block; }}
.cta span {{ display: inline-block; padding: 1.8cqmin 5cqmin; border: 1px solid var(--accent); border-radius: 99cqmin;
  font: 600 {"3cqmin" if vertical else "2.2cqmin"} "Body"; letter-spacing: .6cqmin; text-transform: uppercase; color: var(--ink); }}
"""


# ---------------------------------------------------------------- build
def build(spec_path):
    spec_path = Path(spec_path).resolve()
    out = spec_path.parent
    spec = json.loads(spec_path.read_text())
    brand_path = (out / spec["marca"]).resolve()
    brand = json.loads(brand_path.read_text())
    fmt = spec.get("formato", "vertical")
    W, H = FORMATS[fmt]

    f = brand.get("fuentes", {})
    ft, fb = f.get("titulo", {}), f.get("texto", {})
    faces = [
        font_face("Display", ft.get("archivo", "cormorant-garamond-latin-500-normal.woff2"), 500, "normal", brand_path.parent),
        font_face("Display", ft.get("italica", "cormorant-garamond-latin-500-italic.woff2"), 500, "italic", brand_path.parent),
        font_face("Body", fb.get("archivo", "manrope-latin-400-normal.woff2"), 400, "normal", brand_path.parent),
        font_face("Body", fb.get("negrita", "manrope-latin-600-normal.woff2"), 600, "normal", brand_path.parent),
    ]

    c = Comp(brand, fmt)
    c.spec_dir, c.brand_dir = out, brand_path.parent
    t = 0.0
    for sc in spec["escenas"]:
        sc = dict(sc)
        kind = sc.pop("tipo")
        if kind not in DEFAULT_DUR:
            sys.exit(f"Tipo de escena desconocido: {kind}. Opciones: {', '.join(DEFAULT_DUR)}")
        d = float(sc.pop("duracion", DEFAULT_DUR[kind]))
        getattr(c, kind)(t, d, **sc)
        t += d
    dur = round(t, 2)

    # capa global: fondo que respira, HUD y barra de progreso
    c.js.insert(0, f'tl.fromTo(".glow", {{ xPercent: -18, yPercent: -10, scale: 0.9 }}, {{ xPercent: 18, yPercent: 10, '
                   f'scale: 1.1, duration: {dur}, ease: "sine.inOut", immediateRender: true }}, 0);')
    hud = ""
    if spec.get("hud", True):
        total = len(spec["escenas"])
        hud = (f'<div class="hud"><span><i class="dot"></i>{esc(brand["nombre"])}</span>'
               f'<span class="count">{esc(spec.get("etiqueta", ""))}</span></div><div class="prog"></div>')
        c.js.append(f'tl.fromTo(".prog", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {dur}, ease: "none", immediateRender: true }}, 0);')
        c.js.append(f'tl.fromTo(".hud, .frame-line", {{ opacity: 0 }}, {{ opacity: 1, duration: 1.2, ease: "power2.out", immediateRender: true }}, 0);')

    for sub in ("fonts", "media", "vendor"):
        (out / sub).mkdir(exist_ok=True)
    for _, p, _, _ in faces:
        shutil.copy(p, out / "fonts" / p.name)
    for m in c.media:
        shutil.copy(m, out / "media" / m.name)
    shutil.copy(GSAP, out / "vendor/gsap.min.js")

    audio = ""
    if spec.get("musica") == "ambiente":
        # colchón sonoro sintetizado (libre de derechos): acorde suave que respira + reverb
        notes = [110.0, 164.81, 220.0, 261.63, 329.63, 392.0, 493.88]
        def chan(detune):
            return "+".join(f"{0.06 / (1 + k * 0.35):.4f}*sin(2*PI*{f * detune:.3f}*t)*(0.55+0.45*sin(2*PI*{0.05 + k * 0.013:.3f}*t+{k}))"
                            for k, f in enumerate(notes))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                        f"aevalsrc={chan(1.0)}|{chan(1.003)}:s=48000:d={dur}",
                        "-af", f"lowpass=f=1600,aecho=0.8:0.6:180|340:0.3|0.2,afade=t=in:d=2,"
                               f"afade=t=out:st={max(0, dur - 2.5)}:d=2.5,loudnorm=I=-19:TP=-2:LRA=7,volume={spec.get('volumen', 1.0)}",
                        "-t", str(dur),
                        "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "192k", str(out / "master.m4a")], check=True)
    elif spec.get("musica"):
        music = (out / spec["musica"]).resolve()
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(music), "-t", str(dur),
                        "-af", f"afade=t=in:d=1.2,afade=t=out:st={max(0, dur - 2)}:d=2,volume={spec.get('volumen', 0.8)}",
                        "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "192k", str(out / "master.m4a")], check=True)
    if spec.get("musica"):
        audio = (f'<audio id="master" class="clip" src="master.m4a" data-start="0" data-duration="{dur}" '
                 f'data-track-index="9" data-volume="1"></audio>')

    doc = f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>{esc(brand["nombre"])} · motion elegante</title>
    <script src="vendor/gsap.min.js"></script>
    <style>{css(brand, fmt, faces)}</style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="{W}" data-height="{H}">
      <div class="glow"></div><div class="vignette"></div>
      {chr(10).join("      " + h for h in c.top)}
      {chr(10).join("      " + h for h in c.html)}
      <div class="frame-line"></div>{hud}<div class="grain"></div>
      {audio}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join("      " + j for j in c.js)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    (out / "index.html").write_text(doc)
    if not (out / "package.json").exists():
        (out / "package.json").write_text(json.dumps({
            "name": out.name, "private": True, "type": "module",
            "scripts": {k: f"npx --yes hyperframes@{HF_VERSION} {v}" for k, v in
                        (("dev", "preview"), ("check", "check"), ("render", "render"))}}, indent=2) + "\n")
    if not (out / "hyperframes.json").exists():
        (out / "hyperframes.json").write_text(json.dumps({
            "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
            "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
            "media": {"autoProxy": True}}, indent=2) + "\n")
    print(f"{out.name}: {dur}s, {len(spec['escenas'])} escenas, {fmt} {W}x{H}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for p in sys.argv[1:]:
        build(p)
