#!/usr/bin/env python3
"""Round 3 — motion-graphics reels for Saving Hub.

Every frame is a designed page: dark-grid / red grounds, Anton display type
with mask reveals, JetBrains Mono labels, product footage mounted in animated
cards with bracket callouts, comparison tables, step counters, spec sheets,
phone notifications, kinetic type + marquees, and an animated end-card logo.
Scenes cut on a 120 BPM grid (0.5 s) with a red wipe between scenes; the audio
is a synthesized beat + SFX (mg_assets.py).
"""
import html
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MG = ROOT / "mg"
SFX = ROOT / "sfx"
GSAP = Path.home() / ".cache/hyperframes-vendor/gsap.min.js"

CSS = """
@font-face { font-family: "Anton"; src: url("fonts/Anton.woff2") format("woff2"); font-display: block; }
@font-face { font-family: "JBM"; src: url("fonts/JetBrainsMono-Bold.woff2") format("woff2"); font-weight: 700; font-display: block; }
:root { --red: #E0201B; --white: #FFFFFF; --ink: #0b0b0b; --ink2: #171717; --amber: #F5A623; --mute: #8c8c8c; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: var(--ink); }
#root { position: relative; width: 1080px; height: 1920px; overflow: hidden; container-type: size;
  font-family: "Anton"; color: var(--white); background: var(--ink); }
.scene { position: absolute; inset: 0; overflow: hidden; }
.inner { position: absolute; inset: 0; }
.grid { position: absolute; inset: 0;
  background: linear-gradient(rgba(255,255,255,.06) 1px, transparent 1px) 0 0 / 6cqw 6cqw,
              linear-gradient(90deg, rgba(255,255,255,.06) 1px, transparent 1px) 0 0 / 6cqw 6cqw, var(--ink); }
.grid.red { background: linear-gradient(rgba(0,0,0,.10) 1px, transparent 1px) 0 0 / 6cqw 6cqw,
              linear-gradient(90deg, rgba(0,0,0,.10) 1px, transparent 1px) 0 0 / 6cqw 6cqw, var(--red); }
.mono { font-family: "JBM"; font-weight: 700; text-transform: uppercase; letter-spacing: .35cqw; }
.chip { display: inline-block; padding: 1.2cqw 2.4cqw; font-size: 3.1cqw; background: var(--red); color: var(--white); }
.chip.w { background: var(--white); color: var(--ink); }
.mask { display: block; overflow: hidden; padding: 5cqw 1cqw 0; margin-top: -5cqw; }
.ln { display: block; will-change: transform; }
.red { color: var(--red); }
.title { position: absolute; left: 6cqw; right: 6cqw; top: 34cqh; text-align: left; text-transform: uppercase; }
.title .ln { font-size: 19cqw; line-height: .92; }
.title .bar { height: 1.6cqw; width: 42cqw; background: var(--red); margin: 3cqh 0 0 1cqw; transform-origin: left center; }
.title .sub { margin: 3cqh 0 0 1cqw; font-size: 3.6cqw; color: var(--white); }
.tagpos { position: absolute; left: 7cqw; top: 26cqh; }
/* card with footage */
.card { position: absolute; left: 10cqw; width: 80cqw; top: 14cqh; height: 56cqh; border-radius: 3cqw;
  overflow: hidden; border: .7cqw solid var(--white); box-shadow: 0 3cqw 8cqw rgba(0,0,0,.6); background: #222; }
.card video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.card .push { position: absolute; inset: 0; will-change: transform; }
.card-label { position: absolute; left: 7cqw; top: 11cqh; z-index: 3; }
.caption { position: absolute; left: 6cqw; right: 6cqw; top: 73cqh; text-transform: uppercase; }
.caption .ln { font-size: 15.5cqw; line-height: .92; }
.callout { position: absolute; z-index: 2; }
.callout .br { position: absolute; width: 5cqw; height: 5cqw; border-color: var(--red); border-style: solid; border-width: 0; }
.callout .tl { left: 0; top: 0; border-left-width: .8cqw; border-top-width: .8cqw; }
.callout .tr { right: 0; top: 0; border-right-width: .8cqw; border-top-width: .8cqw; }
.callout .bl { left: 0; bottom: 0; border-left-width: .8cqw; border-bottom-width: .8cqw; }
.callout .brr { right: 0; bottom: 0; border-right-width: .8cqw; border-bottom-width: .8cqw; }
.callout .lab { position: absolute; left: 0; top: 100%; margin-top: 1cqw; white-space: nowrap; font-size: 2.8cqw; }
/* compare */
.cmp-head { position: absolute; top: 12cqh; left: 6cqw; right: 6cqw; text-align: center; }
.cmp-head .ln { font-size: 13cqw; line-height: .95; }
.cols { position: absolute; left: 5cqw; right: 5cqw; top: 29cqh; display: flex; gap: 3cqw; }
.col { flex: 1; border-radius: 2.4cqw; padding: 4cqw 3.4cqw 5cqw; min-height: 50cqh; }
.col.a { background: var(--ink2); border: .5cqw solid #333; }
.col.b { background: var(--red); }
.col.b .red { color: var(--white); }
.col h3 { font-weight: 400; font-size: 8.4cqw; line-height: .95; margin-bottom: 4cqh; }
.row { display: flex; align-items: flex-start; gap: 2.2cqw; margin-bottom: 4cqh; }
.row .ic { flex: 0 0 7.4cqw; height: 7.4cqw; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.col.a .ic { background: #3a3a3a; }
.col.b .ic { background: var(--white); }
.row .ic svg { width: 4.4cqw; height: 4.4cqw; }
.row .tx { font-size: 3.5cqw; line-height: 1.3; padding-top: .9cqw; }
.vs { position: absolute; left: 50%; top: 27.2cqh; width: 13cqw; height: 13cqw; margin-left: -6.5cqw; border-radius: 50%;
  background: var(--white); color: var(--ink); font-size: 6.4cqw; display: flex; align-items: center; justify-content: center; z-index: 3; }
/* steps */
.segs { position: absolute; left: 7cqw; right: 7cqw; top: 9cqh; display: flex; gap: 2cqw; }
.seg { flex: 1; height: 1.1cqw; background: #333; overflow: hidden; }
.seg i { display: block; height: 100%; background: var(--red); transform-origin: left center; }
.bignum { position: absolute; left: 5cqw; top: 11cqh; font-size: 44cqw; line-height: 1; color: transparent;
  -webkit-text-stroke: .6cqw var(--white); }
.step-title { position: absolute; left: 7cqw; right: 7cqw; top: 36cqh; text-transform: uppercase; }
.step-title .ln { font-size: 14cqw; line-height: .95; }
.step-title .mono { font-size: 3.2cqw; color: var(--mute); margin-top: 1.4cqh; }
.card.step { top: 52cqh; height: 40cqh; left: 7cqw; width: 86cqw; }
/* spec */
.card.spec { top: 15cqh; height: 38cqh; left: 7cqw; width: 86cqw; }
.spec-rows { position: absolute; left: 7cqw; right: 7cqw; top: 56cqh; }
.spec-row { position: relative; display: flex; justify-content: space-between; align-items: baseline; padding: 1.5cqh 0; }
.spec-row .k { font-size: 3.2cqw; color: var(--mute); }
.spec-row .v { font-size: 7.4cqw; line-height: 1; }
.spec-row .rule { position: absolute; left: 0; right: 0; bottom: 0; height: .3cqw; background: #3a3a3a; transform-origin: left center; }
/* notifications */
.bgclip { position: absolute; inset: -4cqw; }
.bgclip video { width: 100%; height: 100%; object-fit: cover; filter: blur(18px) brightness(.45) saturate(.8); }
.pov { position: absolute; left: 7cqw; right: 7cqw; top: 13cqh; text-transform: uppercase; }
.pov .ln { font-size: 15cqw; line-height: .92; }
.notifs { position: absolute; left: 6cqw; right: 6cqw; top: 42cqh; }
.notif { display: flex; gap: 3cqw; align-items: center; background: rgba(245,245,245,.96); color: var(--ink);
  border-radius: 4.2cqw; padding: 3.2cqw 3.6cqw; margin-bottom: 2.6cqh; box-shadow: 0 2cqw 6cqw rgba(0,0,0,.45); }
.notif .app { flex: 0 0 12cqw; height: 12cqw; border-radius: 2.8cqw; background: var(--ink); color: var(--white);
  font-size: 5.6cqw; display: flex; align-items: center; justify-content: center; }
.notif .app span { border-bottom: .8cqw solid var(--red); line-height: 1; padding-bottom: .4cqw; }
.notif .body { flex: 1; }
.notif .top { display: flex; justify-content: space-between; font-size: 2.6cqw; color: #666; }
.notif .t { font-family: "Anton"; font-size: 6.2cqw; line-height: 1.05; margin-top: .6cqw; text-transform: uppercase; }
.notif .d { font-size: 3cqw; color: #333; margin-top: .6cqw; letter-spacing: .1cqw; }
/* kinetic */
.marq { position: absolute; left: 0; white-space: nowrap; font-size: 22cqw; line-height: 1; color: transparent;
  -webkit-text-stroke: .35cqw rgba(0,0,0,.28); will-change: transform; }
.marq.lite { -webkit-text-stroke-color: rgba(255,255,255,.12); }
.kword { position: absolute; left: 4cqw; right: 4cqw; top: 50%; text-align: center; text-transform: uppercase;
  font-size: 30cqw; line-height: .9; transform: translateY(-50%); opacity: 0; }
/* counter */
.ring { position: absolute; left: 50%; top: 42%; width: 78cqw; height: 78cqw; margin: -39cqw 0 0 -39cqw; }
.ring svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.count { position: absolute; left: 0; right: 0; top: 42%; transform: translateY(-50%); text-align: center; }
.count .n { font-size: 36cqw; line-height: 1; }
.count .u { font-size: 5cqw; margin-top: 1cqh; }
.count-cap { position: absolute; left: 7cqw; right: 7cqw; top: 70cqh; text-align: center; text-transform: uppercase; }
.count-cap .ln { font-size: 11cqw; line-height: .95; }
/* end card */
.logo { position: absolute; left: 50%; top: 27cqh; width: 34cqw; height: 34cqw; margin-left: -17cqw; background: var(--red);
  border-radius: 3cqw; display: flex; align-items: center; justify-content: center; font-size: 19cqw; }
.logo span { border-bottom: 1.4cqw solid var(--white); line-height: .95; padding-bottom: 1cqw; }
.word { position: absolute; left: 0; right: 0; top: 50cqh; text-align: center; font-size: 17cqw; line-height: 1; }
.word .L { display: inline-block; }
.endtag { position: absolute; left: 0; right: 0; top: 63cqh; text-align: center; font-size: 3.8cqw; }
.cta { position: absolute; left: 0; right: 0; top: 71cqh; text-align: center; }
.cta span { display: inline-block; background: var(--white); color: var(--ink); font-size: 7.6cqw; padding: 1.8cqw 5cqw 2.2cqw; border-radius: 99cqw; }
/* HUD + wipe */
.hud { position: absolute; left: 6cqw; right: 6cqw; top: 3.4cqh; display: flex; justify-content: space-between; font-size: 2.6cqw; z-index: 50; }
.hud .dot { display: inline-block; width: 1.8cqw; height: 1.8cqw; background: var(--red); margin-right: 1.4cqw; vertical-align: -.1cqw; }
.prog { position: absolute; left: 0; bottom: 0; height: .9cqw; width: 100%; background: var(--red); transform-origin: left center; z-index: 50; }
.wipe { position: absolute; left: 0; right: 0; top: 0; height: 100%; background: var(--red); z-index: 60; }
.wipe2 { position: absolute; left: 0; right: 0; top: 0; height: 100%; background: var(--white); z-index: 59; }
"""

CHECK = '<svg viewBox="0 0 24 24"><path d="M4 12.5l5 5L20 6.5" fill="none" stroke="{c}" stroke-width="3.6" stroke-linecap="square"/></svg>'
CROSS = '<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="{c}" stroke-width="3.6" stroke-linecap="square"/></svg>'


def esc(s):
    return html.escape(s)


def rich(s):
    """'*WORD' -> red word."""
    out = []
    for w in s.split(" "):
        out.append(f'<span class="red">{esc(w[1:])}</span>' if w.startswith("*") else esc(w))
    return " ".join(out)


def mask_lines(lines, cls="ln"):
    return "".join(f'<span class="mask"><span class="{cls}">{rich(l)}</span></span>' for l in lines)


class Comp:
    def __init__(self):
        self.html, self.js, self.sfx = [], [], []
        self.n = 0

    def reveal_lines(self, sel, t, stagger=0.09):
        self.js.append(f'tl.fromTo("{sel} .ln", {{ yPercent: 110 }}, {{ yPercent: 0, duration: 0.5, '
                       f'ease: "power4.out", stagger: {stagger}, immediateRender: true }}, {t:.2f});')

    def pop(self, sel, t, dur=0.35, frm="scale: 0", ease="back.out(2)"):
        self.js.append(f'tl.fromTo("{sel}", {{ {frm}, opacity: 0 }}, {{ scale: 1, x: 0, y: 0, rotation: 0, opacity: 1, '
                       f'duration: {dur}, ease: "{ease}", immediateRender: true }}, {t:.2f});')

    def scene(self, t, d, inner, bg="grid"):
        self.n += 1
        sid = f"s{self.n}"
        self.html.append(f'<div id="{sid}" class="clip scene" data-start="{t}" data-duration="{d}" '
                         f'data-track-index="{1 + self.n % 2}"><div class="{bg}"></div><div class="inner">{inner}</div></div>')
        return sid

    def video(self, clip, t, d):
        self.vids = getattr(self, "vids", 0) + 1
        return (f'<video id="v{self.vids}" class="clip" src="clips/{clip}.mp4" muted playsinline data-start="{t}" '
                f'data-duration="{d}" data-track-index="{5 + self.n % 2}"></video>')

    # ---------------- scenes ----------------
    def title(self, t, d, tag, lines, sub, bg="grid"):
        inner = (f'<div class="tagpos"><span class="chip mono">{esc(tag)}</span></div>'
                 f'<div class="title">{mask_lines(lines)}<div class="bar"></div>'
                 f'<div class="sub mono">{esc(sub)}</div></div>')
        sid = self.scene(t, d, inner, bg)
        self.pop(f"#{sid} .chip", t + 0.05, frm="x: -60")
        self.reveal_lines(f"#{sid} .title", t + 0.1)
        self.js.append(f'tl.fromTo("#{sid} .bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, ease: "power3.inOut", immediateRender: true }}, {t + 0.45:.2f});')
        self.js.append(f'tl.fromTo("#{sid} .sub", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.6, ease: "steps(24)", immediateRender: true }}, {t + 0.7:.2f});')
        self.js.append(f'tl.fromTo("#{sid} .title", {{ scale: 1 }}, {{ scale: 1.05, duration: {d}, ease: "none", immediateRender: true }}, {t});')
        self.sfx += [("click", t + 0.05, 0.2), ("impact", t + 0.12, 0.35)]

    def card(self, t, d, clip, label, caption, callouts=(), top=14, height=56):
        co = ""
        for i, (x, y, w, h, lab) in enumerate(callouts):
            co += (f'<div class="callout c{i}" style="left:{x}%;top:{y}%;width:{w}%;height:{h}%">'
                   f'<i class="br tl"></i><i class="br tr"></i><i class="br bl"></i><i class="br brr"></i>'
                   f'<span class="lab chip mono">{esc(lab)}</span></div>')
        inner = (f'<div class="card" style="top:{top}cqh;height:{height}cqh"><div class="push">{self.video(clip, t, d)}</div>{co}</div>'
                 f'<div class="card-label" style="top:{top - 3}cqh"><span class="chip mono">{esc(label)}</span></div>'
                 f'<div class="caption">{mask_lines(caption)}</div>')
        sid = self.scene(t, d, inner)
        self.js.append(f'tl.fromTo("#{sid} .card", {{ y: 900, rotation: 7 }}, {{ y: 0, rotation: -1.5, duration: 0.6, ease: "back.out(1.3)", immediateRender: true }}, {t:.2f});')
        self.js.append(f'tl.fromTo("#{sid} .push", {{ scale: 1.0 }}, {{ scale: 1.1, duration: {d}, ease: "power1.inOut", immediateRender: true }}, {t});')
        self.pop(f"#{sid} .card-label", t + 0.45, frm="x: -80")
        self.reveal_lines(f"#{sid} .caption", t + 0.55)
        for i in range(len(callouts)):
            ct = t + 1.0 + i * 0.5
            self.pop(f"#{sid} .c{i}", ct, dur=0.4, frm="scale: 1.6")
            self.sfx.append(("click", ct, 0.22))
        self.sfx.append(("whoosh", t, 0.2))

    def compare(self, t, d, head, a_title, b_title, rows):
        def col(cls, title, items, good):
            rs = ""
            for j, txt in enumerate(items):
                icon = (CHECK if good else CROSS).format(c="#E0201B" if good else "#9a9a9a")
                rs += f'<div class="row r{j}"><div class="ic">{icon}</div><div class="tx mono">{esc(txt)}</div></div>'
            return f'<div class="col {cls}"><h3>{rich(title)}</h3>{rs}</div>'
        inner = (f'<div class="cmp-head">{mask_lines(head)}</div><div class="vs">VS</div>'
                 f'<div class="cols">{col("a", a_title, [r[0] for r in rows], False)}'
                 f'{col("b", b_title, [r[1] for r in rows], True)}</div>')
        sid = self.scene(t, d, inner)
        self.reveal_lines(f"#{sid} .cmp-head", t + 0.05)
        self.js.append(f'tl.fromTo("#{sid} .col.a", {{ x: -700 }}, {{ x: 0, duration: 0.5, ease: "power4.out", immediateRender: true }}, {t + 0.2:.2f});')
        self.js.append(f'tl.fromTo("#{sid} .col.b", {{ x: 700 }}, {{ x: 0, duration: 0.5, ease: "power4.out", immediateRender: true }}, {t + 0.3:.2f});')
        self.pop(f"#{sid} .vs", t + 0.7, frm="scale: 0, rotation: -180")
        self.sfx += [("whoosh", t + 0.2, 0.2), ("impact", t + 0.7, 0.3)]
        for j in range(len(rows)):
            rt = t + 1.5 + j * 1.0
            for c in ("a", "b"):
                off = 0 if c == "a" else 0.25
                self.pop(f"#{sid} .col.{c} .r{j} .ic", rt + off, frm="scale: 0, rotation: -90")
                self.js.append(f'tl.fromTo("#{sid} .col.{c} .r{j} .tx", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.3, ease: "power3.out", immediateRender: true }}, {rt + off + 0.05:.2f});')
                self.sfx.append(("click", rt + off, 0.2))
        self.js.append(f'tl.to("#{sid} .col.b", {{ scale: 1.04, duration: 0.3, ease: "power2.out", yoyo: true, repeat: 1 }}, {t + d - 1.0:.2f});')

    def step(self, t, d, num, total, title, sub, clip):
        segs = "".join(f'<div class="seg"><i class="g{k}"></i></div>' for k in range(total))
        inner = (f'<div class="segs">{segs}</div><div class="bignum">0{num}</div>'
                 f'<div class="step-title">{mask_lines([title])}<div class="mono">{esc(sub)}</div></div>'
                 f'<div class="card step"><div class="push">{self.video(clip, t, d)}</div></div>')
        sid = self.scene(t, d, inner)
        for k in range(total):
            if k < num - 1:
                self.js.append(f'tl.set("#{sid} .g{k}", {{ scaleX: 1 }}, {t});')
            elif k == num - 1:
                self.js.append(f'tl.fromTo("#{sid} .g{k}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {d - 0.2:.2f}, ease: "none", immediateRender: true }}, {t});')
            else:
                self.js.append(f'tl.set("#{sid} .g{k}", {{ scaleX: 0 }}, {t});')
        self.js.append(f'tl.fromTo("#{sid} .bignum", {{ x: -500, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.5, ease: "power4.out", immediateRender: true }}, {t + 0.05:.2f});')
        self.reveal_lines(f"#{sid} .step-title", t + 0.2)
        self.js.append(f'tl.fromTo("#{sid} .step-title .mono", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.5, ease: "steps(20)", immediateRender: true }}, {t + 0.5:.2f});')
        self.js.append(f'tl.fromTo("#{sid} .card", {{ y: 700 }}, {{ y: 0, duration: 0.55, ease: "power4.out", immediateRender: true }}, {t + 0.3:.2f});')
        self.js.append(f'tl.fromTo("#{sid} .push", {{ scale: 1.0 }}, {{ scale: 1.1, duration: {d}, ease: "power1.inOut", immediateRender: true }}, {t});')
        self.sfx += [("whoosh", t, 0.2), ("click", t + 0.2, 0.2)]

    def spec(self, t, d, clip, rows, callouts=()):
        co = ""
        for i, (x, y, w, h, lab) in enumerate(callouts):
            co += (f'<div class="callout c{i}" style="left:{x}%;top:{y}%;width:{w}%;height:{h}%">'
                   f'<i class="br tl"></i><i class="br tr"></i><i class="br bl"></i><i class="br brr"></i>'
                   f'<span class="lab chip mono">{esc(lab)}</span></div>')
        rs = "".join(f'<div class="spec-row r{j}"><span class="k mono">{esc(k)}</span><span class="v">{rich(v)}</span><i class="rule"></i></div>'
                     for j, (k, v) in enumerate(rows))
        inner = (f'<div class="card spec"><div class="push">{self.video(clip, t, d)}</div>{co}</div>'
                 f'<div class="card-label" style="top:13cqh"><span class="chip mono">FICHA</span></div>'
                 f'<div class="spec-rows">{rs}</div>')
        sid = self.scene(t, d, inner)
        self.js.append(f'tl.fromTo("#{sid} .card", {{ scale: 0.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.5, ease: "power4.out", immediateRender: true }}, {t:.2f});')
        self.js.append(f'tl.fromTo("#{sid} .push", {{ scale: 1.0 }}, {{ scale: 1.1, duration: {d}, ease: "power1.inOut", immediateRender: true }}, {t});')
        self.pop(f"#{sid} .card-label", t + 0.3, frm="x: -80")
        for j in range(len(rows)):
            rt = t + 0.6 + j * 0.5
            self.js.append(f'tl.fromTo("#{sid} .r{j} .rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.4, ease: "power3.inOut", immediateRender: true }}, {rt:.2f});')
            self.js.append(f'tl.fromTo("#{sid} .r{j} .k", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.3, ease: "steps(12)", immediateRender: true }}, {rt:.2f});')
            self.js.append(f'tl.fromTo("#{sid} .r{j} .v", {{ yPercent: 100, opacity: 0 }}, {{ yPercent: 0, opacity: 1, duration: 0.35, ease: "power4.out", immediateRender: true }}, {rt + 0.1:.2f});')
            self.sfx.append(("click", rt, 0.16))
        for i in range(len(callouts)):
            ct = t + 0.9 + i * 0.6
            self.pop(f"#{sid} .c{i}", ct, dur=0.4, frm="scale: 1.6")
        self.sfx.append(("whoosh", t, 0.2))

    def notif(self, t, d, clip, pov, cards):
        cs = "".join(
            f'<div class="notif n{j}"><div class="app"><span>SH</span></div><div class="body">'
            f'<div class="top mono"><span>{esc(a)}</span><span>{esc(tm)}</span></div>'
            f'<div class="t">{esc(ti)}</div><div class="d mono">{esc(de)}</div></div></div>'
            for j, (a, tm, ti, de) in enumerate(cards))
        inner = (f'<div class="bgclip">{self.video(clip, t, d)}</div>'
                 f'<div class="pov">{mask_lines(pov)}</div><div class="notifs">{cs}</div>')
        sid = self.scene(t, d, inner, bg="")
        self.reveal_lines(f"#{sid} .pov", t + 0.05)
        self.sfx.append(("impact", t + 0.1, 0.3))
        for j in range(len(cards)):
            nt = t + 0.8 + j * 1.0
            self.js.append(f'tl.fromTo("#{sid} .n{j}", {{ y: -700, opacity: 0, scale: 0.9 }}, {{ y: 0, opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.4)", immediateRender: true }}, {nt:.2f});')
            self.sfx += [("click", nt + 0.25, 0.28), ("click", nt + 0.33, 0.18)]

    def kinetic(self, t, d, words, bg="grid red", marquee="PERFUMES ÁRABES • DECANTS • SAVING HUB • "):
        lite = "" if "red" in bg else " lite"
        marq = "".join(f'<div class="marq{lite} m{k}" style="top:{8 + k * 24}cqh">{esc(marquee * 3)}</div>' for k in range(4))
        ws = "".join(f'<div class="kword k{j}">{rich(w)}</div>' for j, w in enumerate(words))
        sid = self.scene(t, d, marq + ws, bg=bg)
        for k in range(4):
            a, b = (0, -900) if k % 2 == 0 else (-900, 0)
            self.js.append(f'tl.fromTo("#{sid} .m{k}", {{ x: {a} }}, {{ x: {b}, duration: {d}, ease: "none", immediateRender: true }}, {t});')
        step = d / len(words)
        for j in range(len(words)):
            wt = t + j * step
            self.js.append(f'tl.fromTo("#{sid} .k{j}", {{ opacity: 0, scale: 1.5 }}, {{ opacity: 1, scale: 1, duration: 0.18, ease: "power4.out", immediateRender: true }}, {wt:.2f});')
            if j < len(words) - 1:
                self.js.append(f'tl.to("#{sid} .k{j}", {{ opacity: 0, duration: 0.01 }}, {wt + step - 0.01:.2f});')
            self.sfx.append(("impact" if j == len(words) - 1 else "click", wt, 0.3 if j == len(words) - 1 else 0.24))

    def counter(self, t, d, to, unit, caption):
        r, circ = 45, 2 * 3.14159 * 45
        inner = (f'<div class="ring"><svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="{r}" fill="none" stroke="#2a2a2a" stroke-width="3"/>'
                 f'<circle class="arc" cx="50" cy="50" r="{r}" fill="none" stroke="#E0201B" stroke-width="3" '
                 f'stroke-dasharray="{circ:.2f}" stroke-dashoffset="{circ:.2f}"/></svg></div>'
                 f'<div class="count"><div class="n">0</div><div class="u mono">{esc(unit)}</div></div>'
                 f'<div class="count-cap">{mask_lines(caption)}</div>')
        sid = self.scene(t, d, inner)
        self.js.append(f'tl.fromTo("#{sid} .arc", {{ attr: {{ "stroke-dashoffset": {circ:.2f} }} }}, {{ attr: {{ "stroke-dashoffset": 0 }}, duration: 1.2, ease: "power3.inOut", immediateRender: true }}, {t + 0.1:.2f});')
        self.js.append(f'(() => {{ const o = {{ v: 0 }}; const el = document.querySelector("#{sid} .n");'
                       f' tl.fromTo(o, {{ v: 0 }}, {{ v: {to}, duration: 1.2, ease: "power3.inOut", immediateRender: true,'
                       f' onUpdate: () => {{ el.textContent = Math.round(o.v); }} }}, {t + 0.1:.2f}); }})();')
        self.reveal_lines(f"#{sid} .count-cap", t + 0.9)
        self.sfx += [("riser", t, 0.2), ("impact", t + 1.3, 0.35)]

    def end(self, t, d, tag, cta="PEDILO POR DM"):
        letters = "".join(f'<span class="L{" red" if i >= 7 else ""}">{c if c != " " else "&nbsp;"}</span>'
                          for i, c in enumerate("SAVING HUB"))
        inner = (f'<div class="logo"><span>SH</span></div><div class="word">{letters}</div>'
                 f'<div class="endtag mono">{esc(tag)}</div><div class="cta"><span>{esc(cta)}</span></div>')
        sid = self.scene(t, d, inner)
        self.js.append(f'tl.fromTo("#{sid} .logo", {{ scale: 0, rotation: -120 }}, {{ scale: 1, rotation: 0, duration: 0.6, ease: "back.out(1.6)", immediateRender: true }}, {t + 0.05:.2f});')
        self.js.append(f'tl.fromTo("#{sid} .word .L", {{ yPercent: 120, opacity: 0 }}, {{ yPercent: 0, opacity: 1, duration: 0.4, ease: "power4.out", stagger: 0.04, immediateRender: true }}, {t + 0.4:.2f});')
        self.js.append(f'tl.fromTo("#{sid} .endtag", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.5, ease: "steps(22)", immediateRender: true }}, {t + 0.9:.2f});')
        self.pop(f"#{sid} .cta", t + 1.3, frm="scale: 0")
        self.js.append(f'tl.fromTo("#{sid} .cta span", {{ scale: 1 }}, {{ scale: 1.07, duration: 0.25, ease: "power2.out", yoyo: true, repeat: 3, immediateRender: true }}, {t + 1.8:.2f});')
        self.sfx += [("riser", t - 0.8, 0.2), ("impact", t + 0.1, 0.45), ("click", t + 1.3, 0.25)]


def build(name, spec):
    out = ROOT / name
    if not (out / "index.html").exists():
        subprocess.run(["hyperframes", "init", name, "--non-interactive", "--example", "blank",
                        "--resolution", "portrait"], cwd=ROOT, check=True, stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for sub in ("fonts", "vendor", "clips"):
        (out / sub).mkdir(exist_ok=True)
    shutil.copy(ROOT / "fonts/Anton.woff2", out / "fonts/Anton.woff2")
    shutil.copy(ROOT / "fonts/JetBrainsMono-Bold.woff2", out / "fonts/JetBrainsMono-Bold.woff2")
    shutil.copy(GSAP, out / "vendor/gsap.min.js")

    c = Comp()
    t = 0.0
    bounds = []
    vo_lines = spec.get("vo") or [None] * len(spec["scenes"])
    vo_events = []
    for (kind, d, kw), line in zip(spec["scenes"], vo_lines):
        if line:
            # AI voiceover: the scene stretches (0.5 s grid) to fit its line
            import build_vo
            wav = build_vo.tts(line)
            lead = 0.45 if kind == "end" else 0.15
            need = lead + build_vo.duration(wav) + 0.35
            d = max(d, -(-need * 2 // 1) / 2)
            vo_events.append((wav, t + lead))
        getattr(c, kind)(t, d, **kw)
        t += d
        bounds.append(t)
    dur = t
    used = set()
    for h in c.html:
        for part in h.split('src="clips/')[1:]:
            used.add(part.split(".mp4")[0])
    for clip in used:
        shutil.copy(MG / "clips" / f"{clip}.mp4", out / "clips" / f"{clip}.mp4")

    # scene-boundary wipes (red + white trailing), HUD, progress bar
    for b in bounds[:-1]:
        c.js.append(f'tl.fromTo(".wipe2", {{ yPercent: 100 }}, {{ yPercent: -100, duration: 0.42, ease: "power3.inOut", immediateRender: true }}, {b - 0.24:.2f});')
        c.js.append(f'tl.fromTo(".wipe", {{ yPercent: 100 }}, {{ yPercent: -100, duration: 0.42, ease: "power3.inOut", immediateRender: true }}, {b - 0.2:.2f});')
        c.sfx.append(("whoosh", b - 0.2, 0.26))
    c.js.insert(0, 'tl.set(".wipe, .wipe2", { yPercent: 100 }, 0);')
    c.js.append(f'tl.fromTo(".prog", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {dur}, ease: "none", immediateRender: true }}, 0);')
    hud = (f'<div class="hud mono"><span><i class="dot"></i>SAVING HUB</span><span>{esc(spec["hud"])}</span></div>'
           f'<div class="prog"></div><div class="wipe2"></div><div class="wipe"></div>')

    doc = f"""<!doctype html>
<html lang="es" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="vendor/gsap.min.js"></script>
    <style>{CSS}</style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
      {chr(10).join("      " + h for h in c.html)}
      {hud}
      <audio id="master" class="clip" src="master.m4a" data-start="0" data-duration="{dur}" data-track-index="9" data-volume="1"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join("      " + j for j in c.js)}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
    (out / "index.html").write_text(doc)
    mix(out, c.sfx, dur, vo_events)
    (out / "timeline.json").write_text(json.dumps({"duration": dur, "bounds": bounds,
                                                   "vo": [[str(w), round(t, 3)] for w, t in vo_events]}, indent=1))
    print(f"{name}: {dur}s, {len(spec['scenes'])} scenes, {len(c.sfx)} sfx")


def mix(out, sfx, dur, vo_events=()):
    """Beat + SFX; with a voiceover the beat is dropped (voice + SFX only)."""
    if vo_events:
        inputs = ["-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo"]
        chains = ["[0]anull[beat]"]
    else:
        inputs = ["-i", str(MG / "beat.wav")]
        chains = [f"[0]atrim=0:{dur},volume=0.5,afade=t=in:d=0.05,afade=t=out:st={dur - 0.8}:d=0.8[beat]"]
    labels = ["[beat]"]
    k = 1
    vo_labels = []
    for wav, t in vo_events:
        inputs += ["-i", str(wav)]
        ms = int(round(t * 1000))
        chains.append(f"[{k}]aresample=48000,adelay={ms}[v{k}]")
        vo_labels.append(f"[v{k}]")
        k += 1
    if vo_labels:
        chains.append("".join(vo_labels) + f"amix=inputs={len(vo_labels)}:normalize=0,highpass=f=80,"
                      "acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-15:TP=-2,"
                      "aresample=48000,aformat=channel_layouts=stereo[vo]")
        labels.append("[vo]")
    for f, t, vol in sfx:
        inputs += ["-i", str(SFX / f"{f}.wav")]
        ms = max(0, int(round(t * 1000)))
        g = vol * (0.8 if vo_events else 1.4)
        chains.append(f"[{k}]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms},volume={g:.2f}[e{k}]")
        labels.append(f"[e{k}]")
        k += 1
    fc = ";".join(chains) + ";" + "".join(labels) + \
        f"amix=inputs={len(labels)}:duration=first:normalize=0,alimiter=limit=0.95,apad,atrim=0:{dur}[mix]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[mix]",
                    "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "192k", str(out / "master.m4a")], check=True)


VIDEOS = {
    "mg-01-decant-vs-frasco": {
        "hud": "COMPARATIVA",
        "scenes": [
            ("title", 2.5, dict(tag="PREGUNTA SERIA", lines=["¿FRASCO", "ENTERO O", "*DECANT?"], sub="COMPARAMOS LAS DOS OPCIONES")),
            ("compare", 6.0, dict(head=["¿QUÉ TE *CONVIENE?"], a_title="FRASCO ENTERO", b_title="*DECANT",
                                  rows=[("PAGÁS TODO DE UNA", "PAGÁS UNA FRACCIÓN"),
                                        ("NO LO PROBASTE", "LO PROBÁS EN TU PIEL"),
                                        ("UN SOLO AROMA", "VARIOS PARA ELEGIR")])),
            ("card", 3.0, dict(clip="bh_syringe", label="DIRECTO DEL ORIGINAL", caption=["DEL FRASCO", "A TU *DECANT"],
                               callouts=[(38, 22, 30, 40, "JERINGA")])),
            ("end", 3.0, dict(tag="PROBÁ ANTES DE COMPRAR")),
        ],
    },
    "mg-02-tres-pasos": {
        "hud": "TUTORIAL",
        "scenes": [
            ("title", 2.0, dict(tag="TUTORIAL", lines=["ASÍ SE ARMA", "UN *DECANT"], sub="3 PASOS · BHARARA KING")),
            ("step", 3.0, dict(num=1, total=3, title="*EXTRAEMOS", sub="DEL FRASCO ORIGINAL, CON JERINGA", clip="bh_syringe")),
            ("step", 3.0, dict(num=2, total=3, title="*TRASVASAMOS", sub="A UN ATOMIZADOR DE VIDRIO", clip="bh_fill")),
            ("step", 3.0, dict(num=3, total=3, title="*SELLAMOS", sub="Y QUEDA LISTO PARA USAR", clip="bh_cap")),
            ("end", 3.0, dict(tag="TU DECANT, LISTO PARA LLEVAR")),
        ],
    },
    "mg-03-ficha-jean-lowe": {
        "hud": "FICHA TÉCNICA",
        "scenes": [
            ("title", 2.0, dict(tag="FICHA TÉCNICA", lines=["JEAN LOWE", "*IMMORTEL"], sub="MAISON ALHAMBRA")),
            ("spec", 4.5, dict(clip="jl_bottle", rows=[("CASA", "MAISON ALHAMBRA"), ("TIPO", "EAU DE PARFUM"),
                                                       ("TAMAÑO", "*100 ML"), ("PERFIL", "FRESCO · CÍTRICO"),
                                                       ("ORIGEN", "EMIRATOS ÁRABES")])),
            ("card", 3.5, dict(clip="jl_holo", label="CHECK DE ORIGINALIDAD", caption=["HOLOGRAMA", "Y *SELLO"],
                               callouts=[(52, 14, 36, 22, "HOLOGRAMA")])),
            ("counter", 2.5, dict(to=100, unit="MILILITROS", caption=["FRASCO *COMPLETO"])),
            ("end", 3.0, dict(tag="LUJO SIN PAGAR DE MÁS")),
        ],
    },
    "mg-04-llego-tu-pedido": {
        "hud": "POV",
        "scenes": [
            ("notif", 5.5, dict(clip="bh_final", pov=["POV: LLEGÓ", "TU *DECANT"], cards=[
                ("SAVING HUB", "AHORA", "PEDIDO CONFIRMADO", "DECANT · BHARARA KING"),
                ("SAVING HUB", "AHORA", "TU DECANT ESTÁ LISTO", "SACADO DEL FRASCO ORIGINAL"),
                ("SAVING HUB", "AHORA", "¡LLEGÓ!", "ABRILO Y PROBALO EN TU PIEL")])),
            ("card", 3.5, dict(clip="bh_spray", label="BHARARA KING", caption=["LISTO PARA", "*USAR"],
                               callouts=[(30, 30, 40, 45, "DECANT")])),
            ("end", 3.0, dict(tag="PEDILO HOY")),
        ],
    },
    "mg-05-perfumes-arabes": {
        "hud": "PERFUMES ÁRABES",
        "scenes": [
            ("kinetic", 3.0, dict(words=["LUJO", "SIN", "PAGAR", "DE *MÁS"])),
            ("card", 3.0, dict(clip="jl_reveal", label="JEAN LOWE IMMORTEL", caption=["MAISON", "*ALHAMBRA"])),
            ("card", 3.0, dict(clip="bh_box", label="BHARARA KING", caption=["BHARARA", "*KING"])),
            ("kinetic", 2.0, dict(words=["FRASCOS", "Y *DECANTS"], bg="grid")),
            ("end", 3.0, dict(tag="PERFUMES ÁRABES · DECANTS")),
        ],
    },
}

if __name__ == "__main__":
    for name in sys.argv[1:] or VIDEOS:
        build(name, VIDEOS[name])
