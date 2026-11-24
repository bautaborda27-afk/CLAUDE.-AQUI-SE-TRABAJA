#!/usr/bin/env python3
"""Build the Meli reel (style reference: @ingleswithjuli talking-head English reels).

Order: clip 2 (hook: "pareciera que tenés que saber un montón... Bueno, no")
       -> clip 3 (body: simple phrases, real English)
       -> clip 1 (CTA: "escribí CERO... Bye!").

Steps:
  1. cut the kept shots out of source/v*.mp4 -> edit/base.mp4 (video) + work/voice.wav
  2. synthesize SFX and mix voice + SFX -> edit/master.m4a
  3. write edit/index.html (captions, cards, stickers, zooms, B/W beats, streaks)
Then: cd edit && hyperframes render ; ./finalize.sh
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EDIT = ROOT / "edit"
WORK = ROOT / "work"
SFX = WORK / "sfx"
WORDS = json.loads((ROOT / "data/words.json").read_text())

# (clip, src_in, src_out, zoom_from, zoom_to)   pauses > ~0.35 s are cut out
SHOTS = [
    ("v2", 0.70, 2.82, 1.00, 1.05),
    ("v2", 3.02, 6.20, 1.12, 1.17),   # B/W myth beat
    ("v2", 6.62, 7.52, 1.04, 1.04),   # "Bueno, no." (punch handled below)
    ("v2", 7.92, 13.12, 1.10, 1.03),
    ("v3", 0.82, 5.40, 1.00, 1.06),
    ("v3", 5.70, 12.10, 1.12, 1.12),  # split by punch-ins below
    ("v3", 12.45, 13.23, 1.16, 1.18),
    ("v3", 13.47, 14.30, 1.00, 1.03),
    ("v3", 14.54, 15.78, 1.12, 1.15),
    ("v3", 16.13, 17.75, 1.02, 1.05),
    ("v3", 18.10, 20.66, 1.10, 1.04),
    ("v1", 0.70, 6.48, 1.00, 1.06),
    ("v1", 7.08, 7.91, 1.14, 1.18),
]
ORIGIN = {"v2": "48% 33%", "v3": "52% 30%", "v1": "68% 36%"}

# output offset of every shot
OFF, t = [], 0.0
for s in SHOTS:
    OFF.append(round(t, 3))
    t += s[2] - s[1]
DUR = round(t, 3)


def out_t(clip, ts, snap=True):
    """Source time in `clip` -> output time (snaps forward into the next kept shot)."""
    for (c, a, b, *_), o in zip(SHOTS, OFF):
        if c != clip:
            continue
        if a <= ts < b:
            return round(o + ts - a, 3)
        if snap and ts < a:
            return o
    return None


def run(cmd):
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------- 1. base cut
def build_base():
    WORK.mkdir(exist_ok=True)
    srcs = ["v2", "v3", "v1"]
    idx = {c: i for i, c in enumerate(srcs)}
    fc, labels = [], []
    for k, (c, a, b, *_) in enumerate(SHOTS):
        i, d = idx[c], b - a
        fc.append(f"[{i}:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=30,"
                  f"eq=contrast=1.06:saturation=1.10:brightness=0.005,format=yuv420p[v{k}]")
        fc.append(f"[{i}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,"
                  f"afade=t=in:d=0.012,afade=t=out:st={d - 0.015:.3f}:d=0.015[a{k}]")
        labels.append(f"[v{k}][a{k}]")
    fc.append(f"{''.join(labels)}concat=n={len(SHOTS)}:v=1:a=1[v][a0]")
    fc.append("[a0]highpass=f=85,afftdn=nf=-28,"
              "acompressor=threshold=-21dB:ratio=3:attack=5:release=90:makeup=2,"
              "alimiter=limit=0.92[a]")
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for c in srcs:
        cmd += ["-i", str(ROOT / f"source/{c}.mp4")]
    cmd += ["-filter_complex", ";".join(fc),
            "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
            "-g", "15", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(EDIT / "base.mp4"),
            "-map", "[a]", "-ac", "2", "-ar", "48000", str(WORK / "voice.wav")]
    run(cmd)


# ---------------------------------------------------------------- 2. SFX + master
def synth_sfx():
    SFX.mkdir(parents=True, exist_ok=True)
    defs = {
        "whoosh": ["-f", "lavfi", "-i", "anoisesrc=d=0.5:c=pink:r=48000:a=0.6",
                   "-af", "afade=t=in:d=0.18:curve=exp,afade=t=out:st=0.22:d=0.28,"
                          "highpass=f=400,lowpass=f=7000,volume=0.9"],
        "pop": ["-f", "lavfi", "-i",
                "aevalsrc='0.8*sin(2*PI*(500*t+5200*t*t))*exp(-38*t)':d=0.12:s=48000",
                "-af", "highpass=f=200"],
        "click": ["-f", "lavfi", "-i", "sine=f=2300:d=0.035:r=48000",
                  "-af", "afade=t=out:st=0.008:d=0.027,volume=0.7"],
        "thock": ["-f", "lavfi", "-i",
                  "aevalsrc='0.9*sin(2*PI*95*t)*exp(-14*t)+0.25*sin(2*PI*190*t)*exp(-22*t)':d=0.35:s=48000",
                  "-af", "lowpass=f=900"],
        "swish": ["-f", "lavfi", "-i", "anoisesrc=d=0.28:c=white:r=48000:a=0.5",
                  "-af", "afade=t=in:d=0.06,afade=t=out:st=0.08:d=0.2,"
                         "bandpass=f=3800:width_type=o:w=1.6,volume=0.8"],
    }
    for name, args in defs.items():
        run(["ffmpeg", "-v", "error", "-y", *args, "-ac", "2", str(SFX / f"{name}.wav")])


def mix_master(events):
    """events: list of (time, sfx_name, gain)."""
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(WORK / "voice.wav")]
    fc, labels = [], ["[0:a]"]
    for k, (tm, name, g) in enumerate(sorted(events)):
        cmd += ["-i", str(SFX / f"{name}.wav")]
        ms = max(int(tm * 1000), 0)
        fc.append(f"[{k + 1}:a]adelay={ms}|{ms},volume={g}[s{k}]")
        labels.append(f"[s{k}]")
    fc.append(f"{''.join(labels)}amix=inputs={len(labels)}:duration=first:normalize=0,"
              f"apad,atrim=0:{DUR}[m]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[m]", "-ar", "48000", "-ac", "2",
            "-c:a", "aac", "-b:a", "192k", str(EDIT / "master.m4a")]
    run(cmd)


# ---------------------------------------------------------------- 3. composition
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# words that become cards / big titles instead of word captions: (clip, phrase index)
EXCLUDE = {("v2", 3), ("v2", 4), ("v2", 7),
           ("v3", 2), ("v3", 3), ("v3", 4), ("v3", 10), ("v3", 11), ("v3", 12), ("v3", 13),
           ("v1", 2), ("v1", 4)}
RED = {("v2", 1), ("v2", 2)}          # myth beat: red captions on B/W
RED_FROM = {"v3": 11.05}              # "...que te llenes de reglas sin sentido"
RED_TO = {"v3": 13.20}
ACCENT = {"inglés", "inglés,", "cero,", "nada", "sencillas", "ayudar,", "construyendo"}
CAPTION_FROM = 1.02                   # hook card owns the first second


def caption_groups():
    groups = []
    for clip in ("v2", "v3", "v1"):
        cur = None
        for w in WORDS[clip]:
            if (clip, w["p"]) in EXCLUDE:
                cur = None
                continue
            s, e = out_t(clip, w["s"]), out_t(clip, w["e"])
            if s is None or s < CAPTION_FROM:
                continue
            e = max(e or s + 0.2, s + 0.12)
            red = (clip, w["p"]) in RED or (clip in RED_FROM and RED_FROM[clip] <= w["s"] < RED_TO[clip])
            txt = w["w"]
            brk = (cur is None or len(cur["w"]) >= 3 or cur["red"] != red
                   or len(" ".join(x["w"] for x in cur["w"]) + " " + txt) > 17
                   or cur["w"][-1]["w"][-1] in ",.?!" or s - cur["w"][-1]["e"] > 0.35)
            if brk:
                cur = {"w": [], "red": red}
                groups.append(cur)
            cur["w"].append({"w": txt, "s": s, "e": e})
    # captions never overlap a card / big title, and red captions stay inside their B/W beat
    blocks = sorted(out_t(c, ts) for c, ts in [("v2", 6.66), ("v2", 9.85), ("v3", 4.36), ("v3", 5.74),
                                                ("v3", 6.60), ("v3", 16.15), ("v1", 3.97), ("v1", 7.12)])
    bw_end = [out_t("v2", 6.19), out_t("v3", 13.22)]
    for i, g in enumerate(groups):
        start = g["w"][0]["s"] - 0.04
        end = g["w"][-1]["e"] + 0.30
        if i + 1 < len(groups):
            end = min(end, groups[i + 1]["w"][0]["s"] - 0.06)
        nxt = [b for b in blocks if b > start]
        if nxt:
            end = min(end, nxt[0] - 0.04)
        if g["red"]:
            end = min(end, min(b for b in bw_end if b > start) - 0.02)
        g["start"], g["dur"] = round(start, 3), round(max(end - start, 0.28), 3)
    return groups


def build_html():
    o = lambda c, ts: out_t(c, ts)
    groups = caption_groups()
    els, js, sfx = [], [], []
    trk = {"cap": 2}

    def T(x):
        return f"{x:.3f}"

    # --- camera: per-shot zoom drifts split by punch-ins (non-overlapping fromTo) ---
    js.append('tl.set("#cam", {force3D: true, filter: "grayscale(0) contrast(1)"}, 0);')
    punches = [  # (clip, src start, scale, src end, settle scale)
        ("v2", 7.22, 1.30, 7.50, 1.31),      # "no."
        ("v3", 8.30, 1.00, 11.0, 1.05),      # "Obvio que te voy a ayudar"
        ("v3", 11.02, 1.18, 12.10, 1.21),    # "...reglas" (B/W)
        ("v1", 3.98, 1.27, 4.72, 1.30),      # "escribí CERO"
        ("v1", 4.74, 1.06, 6.48, 1.09),
    ]
    for (c, a, b, z0, z1), off in zip(SHOTS, OFF):
        segs, cur_a, cur_z0, cur_z1 = [], a, z0, z1
        for pc, pa, sc, pb, settle in punches:
            if pc == c and a < pa < b:
                segs.append((cur_a, pa, cur_z0, cur_z1))
                cur_a, cur_z0, cur_z1 = pa, sc, settle
                if pb < b - 0.05:
                    segs.append((pa, pb, sc, settle))
                    cur_a, cur_z0, cur_z1 = pb, settle, settle + 0.02
        segs.append((cur_a, b, cur_z0, cur_z1))
        for sa, sb, f0, f1 in segs:
            t0 = off + sa - a
            js.append(f'tl.fromTo("#cam", {{transformOrigin: "{ORIGIN[c]}", scale: {f0}}}, '
                      f'{{transformOrigin: "{ORIGIN[c]}", scale: {f1}, duration: {sb - sa - 0.01:.3f}, '
                      f'ease: "power1.inOut", immediateRender: false}}, {T(t0)});')
    bw = [(o("v2", 3.02), o("v2", 6.19)), (o("v3", 11.02), o("v3", 13.22))]
    for a, b in bw:
        js.append(f'tl.set("#cam", {{filter: "grayscale(1) contrast(1.12)"}}, {T(a)});')
        js.append(f'tl.set("#cam", {{filter: "grayscale(0) contrast(1)"}}, {T(b)});')
        sfx.append((a, "swish", 0.35))

    # --- streak transitions between clips ------------------------------------
    for k in range(1, len(SHOTS)):
        if SHOTS[k][0] != SHOTS[k - 1][0]:
            tt = OFF[k]
            sid = f"st{k}"
            els.append(f'<div id="{sid}" class="clip streak" data-start="{T(tt - 0.16)}" data-duration="0.42" '
                       f'data-track-index="8"><div class="bar"></div><div class="glow"></div></div>')
            js.append(f'tl.fromTo("#{sid} .bar", {{xPercent: -260}}, {{xPercent: 330, duration: 0.36, ease: "power2.inOut"}}, {T(tt - 0.16)});')
            js.append(f'tl.fromTo("#{sid} .glow", {{opacity: 0}}, {{opacity: 0.75, duration: 0.08, ease: "power1.out", yoyo: true, repeat: 1}}, {T(tt - 0.06)});')
            sfx.append((tt - 0.20, "whoosh", 0.55))

    # --- hook card -----------------------------------------------------------
    els.append('<div id="hook" class="clip hook" data-start="0" data-duration="1.05" data-track-index="5">'
               '<div class="inner"><span class="l1">Inglés desde CERO</span>'
               '<span class="l2">¿Se puede?</span></div></div>')
    js.append('tl.fromTo("#hook .inner", {scale: 0.82, opacity: 0}, {scale: 1, opacity: 1, duration: 0.22, ease: "back.out(2)"}, 0.0);')
    js.append('tl.fromTo("#hook .inner", {scale: 1, opacity: 1}, {scale: 0.9, opacity: 0, duration: 0.12, ease: "power2.in", immediateRender: false}, 0.92);')
    sfx.append((0.02, "pop", 0.45))

    # --- word captions -------------------------------------------------------
    for i, g in enumerate(groups):
        cid = f"c{i}"
        spans = []
        for j, w in enumerate(g["w"]):
            cls = "w"
            if not g["red"] and w["w"] in ACCENT:
                cls += " acc"
            spans.append(f'<span class="{cls}">{esc(w["w"])}</span>')
            js.append(f'tl.fromTo("#{cid} .w:nth-child({j + 1})", {{opacity: 0, scale: 0.6, y: 12}}, '
                      f'{{opacity: 1, scale: 1, y: 0, duration: 0.13, ease: "back.out(2.2)"}}, {T(max(w["s"] - 0.02, g["start"]))});')
        cls = "clip cap red" if g["red"] else "clip cap"
        els.append(f'<div id="{cid}" class="{cls}" data-start="{T(g["start"])}" data-duration="{T(g["dur"])}" '
                   f'data-track-index="{2 + i % 2}"><div class="inner">{" ".join(spans)}</div></div>')

    # --- cards (English headline + Spanish meaning) --------------------------
    def card(cid, start, end, hl, sub, kind="card"):
        if kind == "card":
            inner = f'<span class="hl">{hl}</span><span class="sub">{sub}</span>'
        else:
            inner = f'<span class="q1">{hl}</span><span class="q2">{sub}</span>'
        els.append(f'<div id="{cid}" class="clip {kind}" data-start="{T(start)}" data-duration="{T(end - start)}" '
                   f'data-track-index="4"><div class="inner">{inner}</div></div>')
        js.append(f'tl.fromTo("#{cid} .inner > span:nth-child(1)", {{opacity: 0, scale: 0.7, y: 18}}, '
                  f'{{opacity: 1, scale: 1, y: 0, duration: 0.2, ease: "back.out(2)"}}, {T(start)});')
        js.append(f'tl.fromTo("#{cid} .inner > span:nth-child(2)", {{opacity: 0, y: 14}}, '
                  f'{{opacity: 1, y: 0, duration: 0.18, ease: "power3.out"}}, {T(start + 0.22)});')
        js.append(f'tl.fromTo("#{cid} .inner", {{opacity: 1, scale: 1}}, {{opacity: 0, scale: 0.94, duration: 0.1, ease: "power2.in", immediateRender: false}}, {T(end - 0.11)});')
        sfx.append((start, "pop", 0.4))

    blank = '<span class="blank"></span>'
    card("k1", o("v2", 9.85), o("v2", 13.10), "Start from zero", "No necesitás saber nada para arrancar")
    card("q1", o("v3", 4.36), o("v3", 5.39), f'“<b>My name is</b> {blank}”', f'“Me llamo {blank}”', "quote")
    card("q2", o("v3", 5.74), o("v3", 6.55), f'“<b>I’m</b> {blank} <b>years old</b>”', f'“Tengo {blank} años”', "quote")
    card("q3", o("v3", 6.60), o("v3", 8.20), '“<b>I love</b> coffee”', '“Me encanta el café”', "quote")
    card("k2", o("v3", 16.15), o("v3", 20.64), "Real English", "Frases útiles + vocabulario que te sirva")

    # --- big titles ----------------------------------------------------------
    def big(bid, start, end, l1, l2):
        els.append(f'<div id="{bid}" class="clip big" data-start="{T(start)}" data-duration="{T(end - start)}" '
                   f'data-track-index="6"><div class="inner"><span class="b1">{l1}</span><span class="b2">{l2}</span></div></div>')
        js.append(f'tl.fromTo("#{bid} .b1", {{opacity: 0, scale: 1.6}}, {{opacity: 1, scale: 1, duration: 0.16, ease: "power3.out"}}, {T(start)});')
        sfx.append((start, "thock", 0.55))

    def big2(bid, t2):
        js.append(f'tl.fromTo("#{bid} .b2", {{opacity: 0, scale: 1.8}}, {{opacity: 1, scale: 1, duration: 0.16, ease: "power3.out"}}, {T(t2)});')
        sfx.append((t2, "thock", 0.6))

    big("bn", o("v2", 6.66), o("v2", 7.51), "¡Bueno,", "NO!")
    big2("bn", o("v2", 7.22))
    big("bc", o("v1", 3.97), o("v1", 4.76), "Escribí", "CERO")
    big2("bc", o("v1", 4.43))
    js.append('tl.set("#bn .b2, #bc .b2", {opacity: 0}, 0);')

    # Bye caption (English, cream)
    by0, by1 = o("v1", 7.12), DUR
    els.append(f'<div id="bye" class="clip cap byecap" data-start="{T(by0)}" data-duration="{T(by1 - by0)}" '
               f'data-track-index="2"><div class="inner"><span class="w acc">Bye!</span></div></div>')
    js.append(f'tl.fromTo("#bye .w", {{opacity: 0, scale: 0.5}}, {{opacity: 1, scale: 1, duration: 0.18, ease: "back.out(2.5)"}}, {T(by0 + 0.04)});')

    # --- emoji stickers -------------------------------------------------------
    stickers = [  # (id, clip, src, emoji, left cqw, top cqh, rot, until src)
        ("e1", "v2", 5.04, "😩", 72, 30, 10, 6.19),
        ("e2", "v3", 7.15, "☕", 70, 33, -8, 8.20),
        ("e3", "v3", 9.15, "🤝", 70, 34, 8, 9.92),
        ("e4", "v3", 11.70, "🤯", 4, 30, -10, 13.22),
        ("e5", "v3", 17.14, "✅", 72, 31, 8, 20.62),
        ("e6", "v1", 4.42, "💬", 6, 30, -8, 4.76),
        ("e7", "v1", 7.14, "👋", 8, 34, -10, 7.91),
    ]
    for sid, c, ts, emo, x, y, rot, until in stickers:
        a = o(c, ts)
        b = o(c, until) if out_t(c, until, snap=False) is not None else DUR
        els.append(f'<div id="{sid}" class="clip sticker" data-start="{T(a)}" data-duration="{T(b - a)}" '
                   f'data-track-index="7" style="left:{x}cqw;top:{y}cqh"><div class="inner">{emo}</div></div>')
        js.append(f'tl.fromTo("#{sid} .inner", {{scale: 0, rotation: {rot - 25}}}, '
                  f'{{scale: 1, rotation: {rot}, duration: 0.28, ease: "back.out(2.4)"}}, {T(a)});')
        js.append(f'tl.fromTo("#{sid} .inner", {{rotation: {rot}}}, {{rotation: {-rot * 0.6:.1f}, duration: {min(0.9, b - a - 0.3):.3f}, ease: "sine.inOut", immediateRender: false}}, {T(a + 0.28)});')
        sfx.append((a, "pop", 0.5))

    for g in groups[::3]:
        sfx.append((g["start"], "click", 0.12))

    html = TEMPLATE.replace("%DUR%", T(DUR)).replace("%ELS%", "\n      ".join(els)) \
                   .replace("%JS%", "\n      ".join(js))
    (EDIT / "index.html").write_text(html)
    return sfx


TEMPLATE = """<!doctype html>
<html lang="es" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="vendor/gsap.min.js"></script>
    <style>
@font-face { font-family: "Poppins"; font-weight: 500; src: url("fonts/Poppins-500.woff2") format("woff2"); font-display: block; }
@font-face { font-family: "Poppins"; font-weight: 700; src: url("fonts/Poppins-700.woff2") format("woff2"); font-display: block; }
@font-face { font-family: "Poppins"; font-weight: 800; src: url("fonts/Poppins-800.woff2") format("woff2"); font-display: block; }
@font-face { font-family: "Poppins"; font-weight: 900; src: url("fonts/Poppins-900.woff2") format("woff2"); font-display: block; }
@font-face { font-family: "ReelEmoji"; src: url("fonts/NotoColorEmoji-subset.ttf") format("truetype"); font-display: block; }
:root { --cream: #F7DDB3; --white: #FFFFFF; --ink: #111111; --red: #E3201B; --card: #FFFDF8; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: #000; }
#root { position: relative; width: 1080px; height: 1920px; overflow: hidden; container-type: size;
  font-family: "Poppins", "ReelEmoji", sans-serif; }
#cam { position: absolute; inset: 0; will-change: transform, filter; backface-visibility: hidden;
  transform: translateZ(0); }
#cam video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.topshade { position: absolute; left: 0; right: 0; top: 0; height: 30cqh; pointer-events: none;
  background: linear-gradient(180deg, rgba(0,0,0,.30) 0%, rgba(0,0,0,.12) 55%, rgba(0,0,0,0) 100%); }
/* text outline used everywhere: hard black stroke + soft drop */
.cap, .card, .quote, .big, .hook .l1 { paint-order: stroke fill; }
.cap { position: absolute; left: 3cqw; right: 3cqw; top: 8.6cqh; text-align: center; }
.cap .w { display: inline-block; font-weight: 800; font-size: 8.6cqw; line-height: 1.05; color: var(--white);
  letter-spacing: -0.03em; -webkit-text-stroke: 0.55cqw var(--ink); paint-order: stroke fill;
  text-shadow: 0 0.5cqw 1.6cqw rgba(0,0,0,.45); margin: 0 0.6cqw; }
.cap .w.acc { color: var(--cream); }
.cap.red .w { color: var(--red); -webkit-text-stroke: 0.6cqw var(--white); text-shadow: 0 0.5cqw 1.8cqw rgba(0,0,0,.35); }
.byecap { top: 8.6cqh; } .byecap .w { font-size: 13cqw; }
.card { position: absolute; left: 3cqw; right: 3cqw; top: 6.8cqh; text-align: center; }
.card .inner, .quote .inner, .big .inner, .hook .inner { will-change: transform, opacity; }
.card .hl { display: block; font-weight: 900; font-size: 10.4cqw; line-height: 1.02; color: var(--cream);
  letter-spacing: -0.02em; -webkit-text-stroke: 0.75cqw var(--ink); paint-order: stroke fill;
  text-shadow: 0 0.6cqw 1.8cqw rgba(0,0,0,.4); }
.card .sub { display: block; margin-top: 0.8cqh; font-weight: 500; font-size: 6.6cqw; line-height: 1.12;
  color: var(--white); -webkit-text-stroke: 0.42cqw var(--ink); paint-order: stroke fill;
  text-shadow: 0 0.4cqw 1.2cqw rgba(0,0,0,.45); padding: 0 4cqw; }
.quote { position: absolute; left: 2cqw; right: 2cqw; top: 8cqh; text-align: center; }
.quote .q1, .quote .q2 { display: block; font-weight: 800; font-size: 7.4cqw; line-height: 1.12; color: var(--white);
  letter-spacing: -0.035em; -webkit-text-stroke: 0.5cqw var(--ink); paint-order: stroke fill;
  text-shadow: 0 0.5cqw 1.4cqw rgba(0,0,0,.45); }
.quote b { font-weight: 800; color: var(--cream); }
.quote .blank { display: inline-block; width: 11cqw; height: 0.9cqw; margin: 0 0.6cqw 0.2cqw; vertical-align: baseline;
  background: var(--white); border-radius: 1cqw; box-shadow: 0 0 0 0.45cqw var(--ink); }
.big { position: absolute; left: 0; right: 0; top: 57cqh; text-align: center; }
.big span { display: block; font-weight: 900; line-height: 0.95; letter-spacing: -0.03em;
  -webkit-text-stroke: 1.1cqw var(--ink); paint-order: stroke fill; text-shadow: 0 1cqw 3cqw rgba(0,0,0,.55); }
.big .b1 { font-size: 15cqw; color: var(--white); }
.big .b2 { font-size: 24cqw; color: var(--cream); }
.hook { position: absolute; left: 4.5cqw; top: 5.4cqh; }
.hook .inner { display: inline-block; background: var(--card); border-radius: 3.4cqw; padding: 2.2cqw 4.4cqw 2.6cqw;
  box-shadow: 0 1.2cqw 3.6cqw rgba(0,0,0,.28); transform-origin: 0% 0%; text-align: center; }
.hook span { display: block; font-weight: 900; letter-spacing: -0.02em; line-height: 1.08; }
.hook .l1 { font-size: 7.4cqw; color: var(--cream); -webkit-text-stroke: 0.6cqw var(--ink); }
.hook .l2 { font-size: 6.2cqw; color: var(--ink); font-weight: 800; }
.sticker { position: absolute; width: 24cqw; height: 24cqw; }
.sticker .inner { font-family: "ReelEmoji"; font-size: 19cqw; line-height: 24cqw; text-align: center;
  filter: drop-shadow(0 0 0.5cqw #fff) drop-shadow(0 0 0.4cqw #fff) drop-shadow(0 1.2cqw 1.6cqw rgba(0,0,0,.35)); }
.streak { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
.streak .bar { position: absolute; top: -20cqh; left: 0; width: 26cqw; height: 140cqh;
  background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,.95) 45%, #fff 50%, rgba(255,255,255,.95) 55%, rgba(255,255,255,0) 100%);
  transform: rotate(16deg); filter: blur(0.4cqw); }
.streak .glow { position: absolute; inset: 0; background: #fff; opacity: 0; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="%DUR%"
         data-width="1080" data-height="1920">
      <div id="cam">
        <video id="base" class="clip" src="base.mp4" muted playsinline
               data-start="0" data-duration="%DUR%" data-track-index="0"></video>
      </div>
      <div class="topshade"></div>
      %ELS%
      <audio id="master" class="clip" src="master.m4a" data-start="0" data-duration="%DUR%"
             data-track-index="9" data-volume="1"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      %JS%
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""


if __name__ == "__main__":
    import sys
    steps = sys.argv[1:] or ["base", "sfx", "html"]
    print(f"duration {DUR}s, shots at", OFF)
    if "base" in steps:
        build_base()
    if "sfx" in steps:
        synth_sfx()
    if "html" in steps:
        events = build_html()
        mix_master(events)
        print(f"{len(events)} sfx events")
