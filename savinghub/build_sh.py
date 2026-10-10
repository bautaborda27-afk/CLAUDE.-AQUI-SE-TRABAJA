#!/usr/bin/env python3
"""Savings Hub house style (from the account's own reels, see referencias/).

Look: dark grid ground with the clip in a rounded card and a mono chapter pill
("LA APERTURA"); full-frame clips with sentence-case captions in dark bars
(keyword in gold); stacked split with a burgundy seam pill ("FRASCO + PAÑUELO");
cream paper end card with a tilted clip card, sans + burgundy serif-italic
headline, underline and the "ESCRIBINOS · SAVINGS.HUB" pill. Clean image, no grain.

Each video is a list of lines (one TTS call each):
  vo      what the voice says (phonetic spelling where Kokoro needs it)
  cap     caption, word-for-word with `vo`: "|" starts a new caption, "/" breaks
          a line, "*word" = gold keyword, "_word" = serif-italic headline word
  shots   source timestamps or [from, to] ranges for the main clip
  layout  "card" | "full" | "split" | "end"
  pill    chapter pill text (card)          grow  card grows to full after the 1st caption
  seam    [left, right] seam pill (split)   b_shots  bottom clip shots (split)

Pipeline: TTS -> timeline -> base.mp4 (+ base_b.mp4) -> index.html -> master.m4a.
Then `hyperframes render` and `GRAIN=0 ./finalize.sh <dir> <Output>`.
"""
import html
import json
import shutil
import subprocess
import sys
from pathlib import Path

import build_audio
import build_base
from build_vo import GAP, SFX, TAIL, duration, sh, tts, word_onsets

ROOT = Path(__file__).resolve().parent
GSAP = Path.home() / ".cache/hyperframes-vendor/gsap.min.js"
GRADE = "eq=contrast=1.04:saturation=1.05"
FONTS = ["SpaceGrotesk-500.woff2", "SpaceGrotesk-700.woff2", "InstrumentSerif-Italic.woff2",
         "JetBrainsMono-500.woff2", "JetBrainsMono-Bold.woff2"]

# frame geometry (px on the 1080x1920 frame)
SEAM = 920
GEOM = {
    "full": dict(left=0, top=0, width=1080, height=1920, borderRadius=0, rotation=0,
                 borderWidth=0, boxShadow="0px 0px 0px rgba(0,0,0,0)"),
    "card": dict(left=38, top=250, width=1004, height=940, borderRadius=36, rotation=0,
                 borderWidth=0, boxShadow="0px 24px 48px rgba(0,0,0,0.55)"),
    "split": dict(left=0, top=0, width=1080, height=SEAM, borderRadius=0, rotation=0,
                  borderWidth=0, boxShadow="0px 0px 0px rgba(0,0,0,0)"),
    "end": dict(left=151, top=204, width=788, height=846, borderRadius=22, rotation=-1.4,
                borderWidth=5, boxShadow="14px 14px 0px #110f0d"),
}

# ---- Round 5 in the Savings Hub style: unboxing a stock box
CAJA = {
    "src": "source/vid_caja.mp4",
    "end": {"head": "¿Cuál te _llevás?", "cta": "ESCRIBINOS · SAVINGS.HUB"},
    "lines": [
        {"vo": "Abrimos esta caja de perfumes... y hay uno que no te esperás.",
         "cap": "Abrimos esta caja / de *perfumes... | y hay uno que / no te *esperás.",
         "shots": [[0.5, 2.2], [2.2, 4.8]], "layout": "card", "pill": "LA APERTURA", "grow": True},
        {"vo": "Yara, de Latáfa.", "cap": "Yara, de *Lattafa.", "shots": [10.0], "layout": "full"},
        {"vo": "Un set de regalo.", "cap": "Un set de *regalo.", "shots": [75.5], "layout": "full"},
        {"vo": "Bajarára King.", "cap": "Bharara *King.", "shots": [106.8], "layout": "full"},
        {"vo": "Vélvet Úd. Jauás, de Rasási.", "cap": "*Velvet Oud. | *Hawas, de Rasasi.",
         "shots": [122.3], "b_shots": [130.9], "layout": "split", "seam": ["VELVET OUD", "HAWAS"]},
        {"vo": "Y el que no te esperabas: Yan Pol Goltié, Le Mal Elixír.",
         "cap": "Y el que no te / *esperabas: | Jean Paul Gaultier, | Le Male _Elixir",
         "shots": [[58.0, 60.6], 60.9, 64.9], "layout": "card", "pill": "LA SORPRESA"},
        {"vo": "Y la caja, vasía.", "cap": "Y la caja, *vacía.", "shots": [[141.6, 144.6]], "layout": "full"},
        {"vo": "Séivings Jab. ¿Cuál te llevás? Pedilo por mensaje.", "cap": None,
         "shots": [[19.8, 21.2]], "layout": "end"},
    ],
}

# ---- Round 6: "así venimos este mes" — monthly recap stitched from several sources
CAJA_SRC, PEDIDO_SRC, DECANT_SRC = "source/vid_caja.mp4", "source/vid_pedido.mp4", "source/vid31.mp4"
REV_SRC, VELVET_SRC = "source/revendedor_30000.mp4", "source/velvet_oud.mp4"


def at(src, t, zoom=1.0, fy=0.5):
    """A shot from another source; zoom/fy punch in (keeps burned-in titles out)."""
    return {"src": src, "at": t, "zoom": zoom, "fy": fy}


def rev(t, zoom=1.4):     # revendedor reel: "PEDIDO / Revendedor: $30.000" burned in at the top
    return at(REV_SRC, t, zoom, 1.0)


def vel(t, zoom=1.5):     # velvet oud reel: "Unboxing / VELVET OUD" burned in at the top
    return at(VELVET_SRC, t, zoom, 1.0)


RESUMEN = {
    "src": CAJA_SRC,
    "end": {"head": "¿Qué _traemos?", "cta": "ESCRIBINOS · SAVINGS.HUB"},
    "lines": [
        {"vo": "Así venimos este mes en Séivings Jab.",
         "cap": "Así venimos / este *mes* | en Savings *Hub.*",
         "shots": [at(CAJA_SRC, 20.2), vel(14.3), at(DECANT_SRC, 64.0), at(PEDIDO_SRC, 75.6),
                   rev(4.2), at(CAJA_SRC, 61.0)],
         "layout": "card", "pill": "RESUMEN DEL MES", "grow": True},
        {"vo": "Llegó mercadería: Yara, Jauás, y hasta Le Mal Elixír.",
         "cap": "Llegó *mercadería:* | Yara, Hawas, / y hasta Le Male *Elixir.*",
         "shots": [at(CAJA_SRC, [2.2, 4.8]), at(CAJA_SRC, 10.0), at(CAJA_SRC, 130.9), at(CAJA_SRC, 60.9)],
         "layout": "card", "pill": "LLEGÓ MERCADERÍA", "grow": True},
        {"vo": "Armamos decánts, directo del frasco original.",
         "cap": "Armamos *decants,* | directo del frasco / *original.*",
         "shots": [at(DECANT_SRC, 57.0)], "b_shots": [at(DECANT_SRC, 76.0)],
         "layout": "split", "seam": ["FRASCO", "DECANT"]},
        {"vo": "Abrimos el Vélvet Úd... y mirá ese color.",
         "cap": "Abrimos el / *Velvet *Oud... | y mirá ese *color.*",
         "shots": [vel([4.0, 6.5], 1.2), vel(14.0, 1.2), vel(21.0, 1.2)],
         "layout": "card", "pill": "UNBOXING"},
        {"vo": "Armamos un pedido mayorista, lleno hasta arriba.",
         "cap": "Armamos un pedido / *mayorista,* | lleno hasta *arriba.*",
         "shots": [at(PEDIDO_SRC, [15.5, 19.5]), at(PEDIDO_SRC, [85.0, 90.0]), at(PEDIDO_SRC, [75.4, 77.3])],
         "layout": "full"},
        {"vo": "Y pedidos de revendedores, como este de treinta-mil.",
         "cap": "Y pedidos de / *revendedores,* | como este de / *$30.000.*",
         "shots": [rev([0.5, 3.5]), rev(4.2), rev([17.0, 24.0])],
         "layout": "card", "pill": "REVENDEDORES", "grow": True},
        {"vo": "Y el mes resién empiesa. Séivings Jab. ¿Qué traemos ahora?", "cap": None,
         "shots": [rev([28.95, 29.45], 1.15)], "layout": "end"},   # keeps the SH sticker on the bag
    ],
}

VIDEOS = {"edit-v5-caja-sh": CAJA, "edit-v6-resumen-mes": RESUMEN}

CSS = """
@font-face { font-family: "SG"; src: url("fonts/SpaceGrotesk-500.woff2") format("woff2"); font-weight: 500; font-display: block; }
@font-face { font-family: "SG"; src: url("fonts/SpaceGrotesk-700.woff2") format("woff2"); font-weight: 700; font-display: block; }
@font-face { font-family: "IS"; src: url("fonts/InstrumentSerif-Italic.woff2") format("woff2"); font-style: italic; font-display: block; }
@font-face { font-family: "JBM"; src: url("fonts/JetBrainsMono-500.woff2") format("woff2"); font-weight: 500; font-display: block; }
@font-face { font-family: "JBM"; src: url("fonts/JetBrainsMono-Bold.woff2") format("woff2"); font-weight: 700; font-display: block; }
:root { --ink: #110f0d; --paper: #f2ece0; --cream: #f1ede5; --pill: #f6efe7; --pill-ink: #2a2622;
  --gold: #e1b857; --burg: #842a36; --seam: #8e1a2e; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: var(--ink); }
#root { position: relative; width: 1080px; height: 1920px; overflow: hidden; container-type: size;
  font-family: "SG"; background: var(--ink); }
.ground { position: absolute; inset: 0; }
#gd { background:
    linear-gradient(rgba(241,237,229,.055) 1px, transparent 1px) 0 0 / 5.5cqw 5.5cqw,
    linear-gradient(90deg, rgba(241,237,229,.055) 1px, transparent 1px) 0 0 / 5.5cqw 5.5cqw, var(--ink); }
#gp { background:
    linear-gradient(rgba(17,15,13,.07) 1px, transparent 1px) 0 0 / 5.5cqw 5.5cqw,
    linear-gradient(90deg, rgba(17,15,13,.07) 1px, transparent 1px) 0 0 / 5.5cqw 5.5cqw, var(--paper); }
.frame { position: absolute; overflow: hidden; border-style: solid; border-color: var(--ink);
  background: var(--ink); will-change: transform; backface-visibility: hidden; }
.cam { position: absolute; inset: 0; will-change: transform; backface-visibility: hidden;
  transform: translateZ(0); }
.cam video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.ov { position: absolute; inset: 0; pointer-events: none; }
.cap { position: absolute; left: 5cqw; right: 5cqw; text-align: center; }
.cap .ln { display: block; }
.cap.bars { top: 15cqh; }
.cap.bars.low { top: 66cqh; }
.bar { display: inline-block; margin: 0.3cqw 0; padding: 0.7cqw 2.4cqw 1.1cqw; border-radius: 1cqw;
  background: rgba(17,15,13,.93); color: var(--cream); font: 700 7cqw/1.1 "SG"; letter-spacing: -0.15cqw; }
.cap.plain { top: 65.5cqh; }
.cap.plain .ln { color: var(--cream); font: 700 6.6cqw/1.14 "SG"; letter-spacing: -0.15cqw; }
.kw { color: var(--gold); }
.cap.head { top: 64.6cqh; color: var(--cream); font-size: 9.6cqw; }
.cap.head .sans { font: 700 9.6cqw/1 "SG"; letter-spacing: -0.3cqw; }
.cap.head .serif { display: inline-block; font: italic 400 12.4cqw/1 "IS"; color: var(--gold); }
.ul { display: block; height: 0.8cqw; margin: 1.3cqw auto 0; border-radius: 999px; transform-origin: left center; }
.cap.head .ul { width: 46cqw; background: var(--gold); }
.pill { position: absolute; left: 0; right: 0; top: 8.4cqh; text-align: center; }
.pill span { display: inline-block; padding: 1.3cqw 2.6cqw 1.3cqw 4cqw; border-radius: 999px;
  background: var(--pill); color: var(--pill-ink); border: 0.3cqw solid var(--ink);
  font: 500 3.5cqw/1 "JBM"; letter-spacing: 0.42em; box-shadow: 0 0.5cqw 0 rgba(0,0,0,.4); }
.seam { position: absolute; left: 0; right: 0; top: calc(SEAMpx - 3.3cqw); text-align: center; }
.seam > span { display: inline-block; padding: 1.3cqw 2.8cqw 1.3cqw 3.8cqw; border-radius: 999px;
  background: var(--seam); color: var(--cream); border: 0.45cqw solid var(--ink);
  font: 700 3.5cqw/1 "JBM"; letter-spacing: 0.3em; }
.seam .g { color: var(--gold); }
.endhead { position: absolute; left: 0; right: 0; top: 57.4cqh; text-align: center; color: var(--ink); font-size: 10cqw; }
.endhead .sans { display: inline-block; font: 700 10cqw/1 "SG"; letter-spacing: -0.35cqw; }
.endhead .serif { display: inline-block; font: italic 400 12.6cqw/1 "IS"; color: var(--burg); }
.endhead .ul { width: 44cqw; background: var(--burg); }
.cta { position: absolute; left: 0; right: 0; top: 67.8cqh; text-align: center; }
/* entrance start states: every animated entrance begins hidden (no flash before its tween) */
.bar, .cap.plain .ln, .cap.head .sans, .cap.head .serif, .endhead .sans, .endhead .serif { opacity: 0; }
.ul { transform: scaleX(0); }
.pill span, .seam > span, .cta span { transform: scale(0); }
#fb, #gp { visibility: hidden; opacity: 0; }
.cta span { display: inline-block; padding: 1.5cqw 3cqw 1.5cqw 4.1cqw; border-radius: 999px;
  background: #faf3ec; color: var(--pill-ink); border: 0.35cqw solid var(--ink);
  font: 500 3.4cqw/1 "JBM"; letter-spacing: 0.32em; box-shadow: 0.55cqw 0.55cqw 0 var(--ink); }
""".replace("SEAMpx", f"{SEAM}px")


def esc(t):
    return html.escape(t)


def parse_cap(cap):
    """'a b / c | d' -> chunks [[['a','b'],['c']], [['d']]] (words keep */_ marks)."""
    chunks = []
    for part in cap.split("|"):
        lines = [ln.split() for ln in part.split("/")]
        chunks.append([ln for ln in lines if ln])
    return chunks


def word_html(w):
    if w.startswith("*"):
        return f'<span class="kw">{esc(w.strip("*"))}</span>'
    return esc(w)


def layout(cfg):
    """TTS every line and lay out shots, caption chunks, layout segments and SFX."""
    t, shots, b_shots, vo_events, segs, caps, sfx = 0.0, [], [], [], [], [], []
    for li, line in enumerate(cfg["lines"]):
        wav = tts(line["vo"])
        d = duration(wav)
        last = li == len(cfg["lines"]) - 1
        span = d + (TAIL if last else GAP)
        vo_events.append((wav, t))
        for key, out in (("shots", shots), ("b_shots", b_shots)):
            src = line.get(key) or line["shots"]
            for s in src:
                out.append((s, round(span / len(src), 3)))
        seg = {"layout": line["layout"], "t": t, "end": t + span, "pill": line.get("pill"),
               "seam": line.get("seam"), "grow": None}
        if line.get("cap"):
            chunks = parse_cap(line["cap"])
            nwords = sum(len(ln) for ch in chunks for ln in ch)
            onsets = word_onsets(line["vo"], nwords, d)
            assert onsets, f"caption words != voice words: {line['cap']!r}"
            wi = 0
            for ci, ch in enumerate(chunks):
                n = sum(len(ln) for ln in ch)
                st = t if ci == 0 else t + onsets[wi] - 0.04
                en = t + onsets[wi + n] - 0.04 if ci < len(chunks) - 1 else t + span
                kind = "bars"
                if seg["layout"] == "card" and not (line.get("grow") and ci > 0):
                    kind = "plain"
                if any(w.startswith("_") for ln in ch for w in ln):
                    kind = "head"
                caps.append({"t": round(st, 3), "end": round(en - 0.02, 3), "lines": ch, "kind": kind,
                             "low": seg["layout"] == "split"})
                if line.get("grow") and ci == 1:
                    seg["grow"] = round(st, 3)
                if kind == "head":
                    sfx.append(("impact", st, 0.22))
                else:
                    sfx.append(("click", st, 0.12))
                wi += n
        segs.append(seg)
        t += span
    return shots, b_shots, vo_events, segs, caps, sfx, t


def geom_js(state, extra=""):
    g = GEOM[state]
    parts = [f"{k}: {json.dumps(v)}" for k, v in g.items()]
    return "{ " + ", ".join(parts) + (", " + extra if extra else "") + " }"


def build_html(name, cfg, segs, caps, shots_a, shots_b, dur):
    out = ROOT / name
    body, js = [], []
    js.append('tl.set(["#fa .cam", "#fb .cam"], { force3D: true }, 0);')
    g0 = GEOM[segs[0]["layout"]]
    fa_style = (f'left:{g0["left"]}px;top:{g0["top"]}px;width:{g0["width"]}px;height:{g0["height"]}px;'
                f'border-radius:{g0["borderRadius"]}px;border-width:{g0["borderWidth"]}px;box-shadow:{g0["boxShadow"]}')

    # --- layout segments
    cur = None   # geometry #fa is in (a grown card is "full")
    track_pill = 4
    for i, s in enumerate(segs):
        lay, t0, t1 = s["layout"], s["t"], s["end"]
        if lay != "end":
            if cur is not None and lay != cur:
                js.append(f'tl.set("#fa", {geom_js(lay)}, {t0:.3f});')
            js.append(f'tl.set("#fb", {{ autoAlpha: {1 if lay == "split" else 0} }}, {t0:.3f});')
        if s["grow"]:
            g = s["grow"]
            js.append(f'tl.to("#fa", {{ ...{geom_js("full")}, duration: 0.55, ease: "power3.inOut" }}, {g:.3f});')
        if s["pill"]:
            pend = (s["grow"] or t1) - 0.02
            pid = f"pill{i}"
            body.append(f'<div id="{pid}" class="clip ov" data-start="{t0:.3f}" data-duration="{pend - t0:.3f}" '
                        f'data-track-index="{track_pill}"><div class="pill"><span>{esc(s["pill"])}</span></div></div>')
            js.append(f'tl.fromTo("#{pid} .pill span", {{ scale: 0 }}, {{ scale: 1, duration: 0.35, '
                      f'ease: "back.out(2)", immediateRender: false }}, {t0 + 0.05:.3f});')
        if s["seam"]:
            a, b = s["seam"]
            sid = f"seam{i}"
            body.append(f'<div id="{sid}" class="clip ov" data-start="{t0:.3f}" data-duration="{t1 - t0 - 0.02:.3f}" '
                        f'data-track-index="5"><div class="seam"><span>{esc(a)} + <span class="g">{esc(b)}</span>'
                        f'</span></div></div>')
            js.append(f'tl.fromTo("#{sid} .seam > span", {{ scale: 0 }}, {{ scale: 1, duration: 0.35, '
                      f'ease: "back.out(2)", immediateRender: false }}, {t0 + 0.08:.3f});')
        if lay == "end":
            js.append(f'tl.set("#gp", {{ autoAlpha: 1 }}, {t0:.3f});')
            js.append(f'tl.set("#fb", {{ autoAlpha: 0 }}, {t0:.3f});')
            js.append(f'tl.set("#fa", {geom_js("end")}, {t0:.3f});')
            js.append(f'tl.fromTo("#fa", {{ y: 160, rotation: -7, autoAlpha: 0 }}, {{ y: 0, rotation: -1.4, '
                      f'autoAlpha: 1, duration: 0.6, ease: "back.out(1.3)", immediateRender: false }}, {t0:.3f});')
            head = cfg["end"]["head"].split()
            sans = " ".join(w for w in head if not w.startswith("_"))
            serif = " ".join(w[1:] for w in head if w.startswith("_"))
            body.append(f'<div id="endtxt" class="clip ov" data-start="{t0:.3f}" data-duration="{dur - t0:.3f}" '
                        f'data-track-index="6"><div class="endhead"><span class="sans">{esc(sans)}</span> '
                        f'<span class="serif">{esc(serif)}</span><span class="ul"></span></div>'
                        f'<div class="cta"><span>{esc(cfg["end"]["cta"])}</span></div></div>')
            js.append(f'tl.fromTo("#endtxt .sans", {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.35, '
                      f'ease: "power3.out", immediateRender: false }}, {t0 + 0.45:.3f});')
            js.append(f'tl.fromTo("#endtxt .serif", {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4, '
                      f'ease: "power3.out", immediateRender: false }}, {t0 + 0.65:.3f});')
            js.append(f'tl.fromTo("#endtxt .ul", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, '
                      f'ease: "power3.out", immediateRender: false }}, {t0 + 0.95:.3f});')
            js.append(f'tl.fromTo("#endtxt .cta span", {{ scale: 0 }}, {{ scale: 1, duration: 0.4, '
                      f'ease: "back.out(2)", immediateRender: false }}, {t0 + 1.3:.3f});')
        cur = "full" if s["grow"] else lay

    # --- slow, eased push on every shot (alternating), main and bottom clip
    for sel, shots in (("#fa .cam", shots_a), ("#fb .cam", shots_b)):
        for i, sh_ in enumerate(shots):
            a, b = (1.0, 1.05) if i % 2 == 0 else (1.05, 1.01)
            js.append(f'tl.fromTo("{sel}", {{ scale: {a} }}, {{ scale: {b}, duration: {sh_["duration"] - 0.02:.3f}, '
                      f'ease: "power1.inOut", immediateRender: false }}, {sh_["start"]:.3f});')

    # --- captions
    for n, c in enumerate(caps):
        cid = f"c{n}"
        if c["kind"] == "head":
            words = [w for ln in c["lines"] for w in ln]
            sans = " ".join(word_html(w) for w in words if not w.startswith("_"))
            serif = " ".join(esc(w[1:]) for w in words if w.startswith("_"))
            inner = (f'<div class="cap head"><span class="sans">{sans}</span> <span class="serif">{serif}</span>'
                     f'<span class="ul"></span></div>')
        elif c["kind"] == "plain":
            inner = '<div class="cap plain">' + "".join(
                f'<span class="ln">{" ".join(word_html(w) for w in ln)}</span>' for ln in c["lines"]) + "</div>"
        else:
            inner = f'<div class="cap bars{" low" if c["low"] else ""}">' + "".join(
                f'<span class="ln"><span class="bar">{" ".join(word_html(w) for w in ln)}</span></span>'
                for ln in c["lines"]) + "</div>"
        body.append(f'<div id="{cid}" class="clip ov" data-start="{c["t"]:.3f}" '
                    f'data-duration="{c["end"] - c["t"]:.3f}" data-track-index="{2 + n % 2}">{inner}</div>')
        t0 = c["t"]
        if c["kind"] == "head":
            js.append(f'tl.fromTo("#{cid} .sans", {{ y: 30, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.3, '
                      f'ease: "power3.out", immediateRender: false }}, {t0:.3f});')
            js.append(f'tl.fromTo("#{cid} .serif", {{ y: 30, opacity: 0, scale: 0.92 }}, {{ y: 0, opacity: 1, '
                      f'scale: 1, duration: 0.4, ease: "power3.out", immediateRender: false }}, {t0 + 0.18:.3f});')
            js.append(f'tl.fromTo("#{cid} .ul", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.4, ease: "power3.out", '
                      f'immediateRender: false }}, {t0 + 0.4:.3f});')
        else:
            sel = f"#{cid} .bar" if c["kind"] == "bars" else f"#{cid} .ln"
            js.append(f'tl.fromTo("{sel}", {{ y: 26, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.28, '
                      f'ease: "power3.out", stagger: 0.09, immediateRender: false }}, {t0:.3f});')

    doc = f"""<!doctype html>
<html lang="es" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="vendor/gsap.min.js"></script>
    <style>{CSS}</style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.3f}"
         data-width="1080" data-height="1920">
      <div id="gd" class="ground"></div>
      <div id="gp" class="ground"></div>
      <div id="fb" class="frame" style="left:0;top:{SEAM}px;width:1080px;height:{1920 - SEAM}px;border-width:0">
        <div class="cam">
          <video id="vb" class="clip" src="base_b.mp4" muted playsinline
                 data-start="0" data-duration="{dur:.3f}" data-track-index="1"></video>
        </div>
      </div>
      <div id="fa" class="frame" style="{fa_style}">
        <div class="cam">
          <video id="va" class="clip" src="base.mp4" muted playsinline
                 data-start="0" data-duration="{dur:.3f}" data-track-index="0"></video>
        </div>
      </div>
      {chr(10).join("      " + b for b in body)}
      <audio id="master" class="clip" src="master.m4a" data-start="0" data-duration="{dur:.3f}"
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


def mix(name, vo_events, events, dur):
    """One master track: AI voice bus (no original sound) + edit SFX."""
    out = ROOT / name
    inputs, chains, vo_labels = [], [], []
    for i, (wav, t) in enumerate(vo_events):
        inputs += ["-i", str(wav)]
        chains.append(f"[{i}]aresample=48000,adelay={int(round(t * 1000))},volume=1.0[v{i}]")
        vo_labels.append(f"[v{i}]")
    base, sfx_labels = len(vo_events), []
    for j, (f, t, vol) in enumerate(events):
        inputs += ["-i", str(SFX / f"{f}.wav")]
        ms = max(0, int(round(t * 1000)))
        chains.append(f"[{base + j}]aresample=48000,adelay={ms}|{ms},volume={vol}[e{j}]")
        sfx_labels.append(f"[e{j}]")
    # aresample after loudnorm, before going stereo: avoids the doubled-voice bug (see edit-report)
    chains.append("".join(vo_labels) + f"amix=inputs={len(vo_labels)}:normalize=0,"
                  "highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,"
                  "loudnorm=I=-15:TP=-2,aresample=48000,aformat=channel_layouts=stereo[vo]")
    fc = ";".join(chains) + ";[vo]" + "".join(sfx_labels) + \
        f"amix=inputs={1 + len(sfx_labels)}:duration=longest:normalize=0,alimiter=limit=0.95," \
        f"apad,atrim=0:{dur},afade=t=out:st={dur - 0.4:.2f}:d=0.4[mix]"
    sh("ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[mix]",
       "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "192k", str(out / "master.m4a"))


def build(name, cfg):
    out = ROOT / name
    if not (out / "index.html").exists():
        sh("hyperframes", "init", name, "--non-interactive", "--example", "blank",
           "--resolution", "portrait", cwd=ROOT, stdin=subprocess.DEVNULL,
           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shots, b_shots, vo_events, segs, caps, sfx, total = layout(cfg)
    base = {"src": cfg["src"], "grade": GRADE, "pixel_reveal": False}
    build_base.build(name, {**base, "shots": shots})
    build_base.build(name, {**base, "shots": b_shots, "basename": "base_b"})
    shots_a = json.loads((out / "shots.json").read_text())
    shots_b = json.loads((out / "base_b_shots.json").read_text())
    dur = shots_a["duration"]
    (out / "fonts").mkdir(exist_ok=True)
    for f in FONTS:
        shutil.copy(ROOT / "fonts" / f, out / "fonts" / f)
    for f in (out / "fonts").glob("*.woff2"):
        if f.name not in FONTS:
            f.unlink()
    (out / "vendor").mkdir(exist_ok=True)
    shutil.copy(GSAP, out / "vendor/gsap.min.js")
    build_html(name, cfg, segs, caps, shots_a["shots"], shots_b["shots"], dur)
    # SFX: soft whoosh on every layout change and cut, click per caption/pill, riser into the end card
    events = list(sfx)
    for s in shots_a["shots"][1:]:
        events.append(("whoosh", s["start"] - 0.06, 0.07))
    for i, s in enumerate(segs):
        if i and s["layout"] != segs[i - 1]["layout"]:
            events.append(("whoosh", s["t"] - 0.06, 0.16))
        if s["grow"]:
            events.append(("whoosh", s["grow"] - 0.04, 0.18))
        if s["pill"] or s["seam"]:
            events.append(("click", s["t"] + 0.08, 0.16))
        if s["layout"] == "end":
            events += [("riser", s["t"] - 0.8, 0.16), ("impact", s["t"] + 0.12, 0.3),
                       ("click", s["t"] + 1.3, 0.16)]
    mix(name, vo_events, events, dur)
    (out / "vo.json").write_text(json.dumps([[str(w), round(t, 3)] for w, t in vo_events], indent=1))
    print(f"{name}: {dur:.2f}s, {len(caps)} captions, {len(segs)} segments")


if __name__ == "__main__":
    if not (SFX / "rewind.wav").exists():
        build_audio.make_sfx()
    for name in sys.argv[1:] or VIDEOS:
        build(name, VIDEOS[name])
