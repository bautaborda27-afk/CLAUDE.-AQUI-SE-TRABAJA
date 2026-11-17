#!/usr/bin/env python3
"""Builder for "Inglés Reel" style reels (style pack: .claude/skills/video-editing/styles/ingles-reel).

    python3 build_reel.py <reel-dir>            # base + audio + comp
    python3 build_reel.py <reel-dir> comp       # only regenerate index.html

Reads <reel-dir>/reel.json:
  sources   {"B": "source/x.mp4", ...}            paths relative to this folder
  cuts      [[src, in, out, zoom, push], ...]     kept source ranges, in order (jump cuts)
  punch     [{"at": T, "scale": s}]                hard re-frame inside a cut
  bw        [[T_from, T_to]]                       black & white + muffled voice (common-mistake gag)
  transitions [T]                                  white-line swipe + blur + click
  beats     [...]                                  text / sticker events (see README.md)
Times T are either output seconds (number) or "SRC:seconds" in source time (mapped through the cuts).

Writes into <reel-dir>: base.mp4 (video, cut + fitted 1080x1920/30), master.wav (voice + SFX),
timeline.json (cut table) and index.html (HyperFrames composition), plus fonts/, stickers/, vendor/.
"""
import html
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STYLE = ROOT.parent / ".claude/skills/video-editing/styles/ingles-reel"
GSAP = Path.home() / ".cache/hyperframes-vendor/gsap.min.js"
FPS = 30
W, H = 1080, 1920
GRADE = "eq=contrast=1.06:saturation=1.06:brightness=0.01,unsharp=5:5:0.5:5:5:0.0"


def run(cmd):
    subprocess.run(cmd, check=True)


class Reel:
    def __init__(self, d: Path):
        self.dir = d
        self.cfg = json.loads((d / "reel.json").read_text())
        self.cuts = []
        t = 0.0
        for c in self.cfg["cuts"]:
            src, a, b = c[0], float(c[1]), float(c[2])
            zoom = float(c[3]) if len(c) > 3 else 1.0
            push = float(c[4]) if len(c) > 4 else 0.0
            self.cuts.append({"src": src, "in": a, "out": b, "start": round(t, 3), "zoom": zoom, "push": push})
            t += b - a
        self.duration = round(t, 3)

    def T(self, v):
        """Output time for a number (output s) or "SRC:sec" (source time)."""
        if isinstance(v, (int, float)):
            return float(v)
        src, s = v.split(":")
        s = float(s)
        for c in self.cuts:
            if c["src"] == src and c["in"] - 1e-3 <= s <= c["out"] + 1e-3:
                return round(c["start"] + min(max(s - c["in"], 0), c["out"] - c["in"]), 3)
        nxt = [c for c in self.cuts if c["src"] == src and c["in"] > s]
        if nxt:
            return min(nxt, key=lambda c: c["in"])["start"]
        raise ValueError(f"time {v} falls outside every cut")

    # ------------------------------------------------------------------ video
    def build_base(self):
        srcs = self.cfg["sources"]
        keys = list(srcs)
        cmd = ["ffmpeg", "-v", "error", "-y"]
        for k in keys:
            cmd += ["-i", str(ROOT / srcs[k])]
        parts, labels = [], []
        fit = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},setsar=1,fps={FPS}"
        for i, c in enumerate(self.cuts):
            n = keys.index(c["src"])
            parts.append(f"[{n}:v]trim=start={c['in']}:end={c['out']},setpts=PTS-STARTPTS,{fit},{GRADE}[v{i}]")
            labels.append(f"[v{i}]")
        graph = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(labels)}:v=1:a=0[v]"
        cmd += ["-filter_complex", graph, "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "14",
                "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart", str(self.dir / "base.mp4")]
        run(cmd)

    # ------------------------------------------------------------------ audio
    def build_audio(self):
        srcs = self.cfg["sources"]
        keys = list(srcs)
        work = self.dir / "work"
        work.mkdir(exist_ok=True)
        sfx = self.make_sfx(work)
        cmd = ["ffmpeg", "-v", "error", "-y"]
        for k in keys:
            cmd += ["-i", str(ROOT / srcs[k])]
        parts, labels = [], []
        for i, c in enumerate(self.cuts):
            n = keys.index(c["src"])
            d = c["out"] - c["in"]
            parts.append(f"[{n}:a]atrim=start={c['in']}:end={c['out']},asetpts=PTS-STARTPTS,aresample=48000,"
                         f"aformat=channel_layouts=mono,afade=t=in:d=0.015,afade=t=out:st={d - 0.015:.3f}:d=0.015[a{i}]")
            labels.append(f"[a{i}]")
        g = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(labels)}:v=0:a=1[cat];"
        # voice: clean + level; muffled (low-pass) inside the B&W gag ranges
        g += ("[cat]highpass=f=90,afftdn=nr=8:nf=-32,acompressor=threshold=-21dB:ratio=3:attack=6:release=90:makeup=2,"
              "asplit=2[dry][wet];")
        bw = [(self.T(a), self.T(b)) for a, b in self.cfg.get("bw", [])]
        if bw:
            ramp = "+".join(f"clip((t-{a:.3f})/0.03,0,1)*clip(({b:.3f}-t)/0.03,0,1)" for a, b in bw)
            g += (f"[wet]lowpass=f=1400,lowpass=f=1400,volume=0.8,volume='{ramp}':eval=frame[w2];"
                  f"[dry]volume='1-({ramp})':eval=frame[d2];[d2][w2]amix=inputs=2:normalize=0[voice];")
        else:
            g += "[wet]anullsink;[dry]anull[voice];"
        # SFX events
        ev = self.sfx_events()
        inputs = []
        n0 = len(keys)
        for j, (name, t, gain) in enumerate(ev):
            cmd += ["-i", str(sfx[name])]
            g += f"[{n0 + j}:a]volume={gain},adelay={int(t * 1000)}:all=1[s{j}];"
            inputs.append(f"[s{j}]")
        if inputs:
            g += "[voice]" + "".join(inputs) + f"amix=inputs={len(inputs) + 1}:normalize=0:duration=first[mix];"
        else:
            g += "[voice]anull[mix];"
        g += f"[mix]atrim=0:{self.duration},aformat=sample_rates=48000:channel_layouts=stereo[out]"
        cmd += ["-filter_complex", g, "-map", "[out]", "-c:a", "pcm_s16le", str(self.dir / "master.wav")]
        run(cmd)
        run(["ffmpeg", "-v", "error", "-y", "-i", str(self.dir / "master.wav"), "-c:a", "aac", "-b:a", "192k",
             str(self.dir / "master.m4a")])

    def make_sfx(self, work: Path):
        """Rights-free SFX synthesized with ffmpeg."""
        defs = {
            # short bright click for the white-line transition
            "click": "anoisesrc=d=0.05:c=white:a=0.9,highpass=f=2500,afade=t=out:st=0.0:d=0.045",
            # soft pop for keywords / stickers (fast upward chirp)
            "pop": "aevalsrc='0.8*sin(2*PI*(500*t+5200*t*t))*exp(-38*t)':d=0.12",
            # low thud for the common-mistake gag
            "thud": "aevalsrc='0.9*sin(2*PI*(150*t-180*t*t))*exp(-11*t)':d=0.32",
        }
        out = {}
        for k, f in defs.items():
            p = work / f"sfx_{k}.wav"
            run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f, "-ar", "48000", "-ac", "1", str(p)])
            out[k] = p
        return out

    def sfx_events(self):
        ev = []
        for t in self.cfg.get("transitions", []):
            ev.append(("click", max(0, self.T(t) - 0.03), 0.30))
        for a, _ in self.cfg.get("bw", []):
            ev.append(("thud", self.T(a), 0.45))
        for b in self.cfg["beats"]:
            if b["type"] in ("keyword", "big"):
                ev.append(("pop", self.T(b["from"]), 0.22))
            elif b["type"] == "sticker":
                for _, t in b["seq"]:
                    ev.append(("pop", self.T(t), 0.14))
        return sorted(ev, key=lambda e: e[1])

    # ------------------------------------------------------------------ comp
    def build_comp(self):
        d = self.dir
        for sub in ("fonts", "stickers", "vendor"):
            (d / sub).mkdir(exist_ok=True)
        for f in (STYLE / "fonts").glob("*.woff2"):
            shutil.copy(f, d / "fonts" / f.name)
        used = {img for b in self.cfg["beats"] if b["type"] == "sticker" for img, _ in b["seq"]}
        used |= {b["emoji"] for b in self.cfg["beats"] if b.get("emoji")}
        used |= {"x"}
        for name in used:
            shutil.copy(STYLE / "stickers" / f"{name}.png", d / "stickers" / f"{name}.png")
        shutil.copy(GSAP, d / "vendor/gsap.min.js")
        (d / "timeline.json").write_text(json.dumps({"duration": self.duration, "cuts": self.cuts}, indent=1))
        body, js = Comp(self).render()
        (d / "index.html").write_text(TEMPLATE.replace("%DUR%", f"{self.duration:.3f}")
                                      .replace("%BODY%", body).replace("%JS%", js)
                                      .replace("%BAND%", str(self.cfg.get("band_top", 57)))
                                      .replace("%ORIGIN%", self.cfg.get("face_origin", "50% 32%")))


def esc(s):
    return html.escape(s, quote=False)


class Comp:
    """Turns beats into HTML clips + one GSAP timeline."""

    def __init__(self, reel: Reel):
        self.r = reel
        self.T = reel.T
        self.html = []
        self.js = []
        self.tracks = {}  # track -> last end
        self.n = 0

    def track(self, pool, a, b):
        for tr in pool:
            if self.tracks.get(tr, -1) < a - 0.02:
                self.tracks[tr] = b
                return tr
        raise ValueError(f"no free track in {pool} for {a}-{b}")

    def clip(self, cls, a, b, pool, inner):
        self.n += 1
        cid = f"c{self.n}"
        tr = self.track(pool, a, b)
        self.html.append(f'<div id="{cid}" class="clip {cls}" data-start="{a:.3f}" data-duration="{b - a:.3f}" '
                         f'data-track-index="{tr}"><div class="inner">{inner}</div></div>')
        return cid

    def add(self, line):
        self.js.append(line)

    def words_html(self, words, cid, base_cls="w", pre=""):
        """words: [[text, T, (accent)]...]; '\n' as text forces a line break. Returns html + reveal js."""
        out = []
        for i, w in enumerate(words):
            if w[0] == "\n":
                out.append("<br>")
                continue
            text, t = w[0], self.T(w[1])
            acc = len(w) > 2 and w[2]
            cls = base_cls + (" acc" if acc else "")
            out.append(f'<span class="{cls}" data-i="{pre}{i}">{esc(text)}</span>')
            self.add(f'tl.fromTo("#{cid} [data-i=\\"{pre}{i}\\"]",{{opacity:0,scale:.7}},'
                     f'{{opacity:1,scale:1,duration:.15,ease:"back.out(1.7)",immediateRender:false}},{t:.3f});')
        return " ".join(out).replace(" <br> ", "<br>")

    def exit(self, cid, b, dy=-3):
        self.add(f'tl.to("#{cid} .inner",{{opacity:0,y:"{dy}cqh",duration:.12,ease:"power2.in"}},{b - 0.12:.3f});')

    def render(self):
        r = self.r
        # --- camera: per-cut framing (hard punch-ins) + eased push inside long cuts.
        # A punch inside a cut splits it, so no push tween is ever still running when a set fires.
        punches = sorted(((self.T(p["at"]), p["scale"], p.get("push", 0)) for p in r.cfg.get("punch", [])))
        for c in r.cuts:
            a, b = c["start"], c["start"] + c["out"] - c["in"]
            ev = [(a, c["zoom"], c["push"])] + [p for p in punches if a + 0.05 < p[0] < b - 0.05]
            for i, (t, scale, push) in enumerate(ev):
                end = ev[i + 1][0] if i + 1 < len(ev) else b
                self.add(f'tl.set("#cam",{{scale:{scale}}},{t:.3f});')
                if push and end - t > 0.3:
                    self.add(f'tl.to("#cam",{{scale:{scale + push:.3f},duration:{end - t - 0.06:.3f},'
                             f'ease:"sine.inOut"}},{t + 0.02:.3f});')
        # --- black & white gag
        for a, b in r.cfg.get("bw", []):
            a, b = self.T(a), self.T(b)
            self.add(f'tl.set("#bw",{{filter:"grayscale(1) contrast(1.12) brightness(1.04)"}},{a:.3f});')
            self.add(f'tl.set("#bw",{{filter:"grayscale(0) contrast(1) brightness(1)"}},{b:.3f});')
        # --- white-line transitions
        for i, t in enumerate(r.cfg.get("transitions", [])):
            t = self.T(t)
            cid = self.clip("tl-wrap", t - 0.14, t + 0.16, [20, 21], '<div class="tline"></div>')
            self.add(f'tl.fromTo("#{cid} .tline",{{x:"-30cqw"}},{{x:"125cqw",duration:.26,ease:"power2.inOut",'
                     f'immediateRender:false}},{t - 0.14:.3f});')
            self.add(f'tl.fromTo("#blur",{{filter:"blur(9px)"}},{{filter:"blur(0px)",duration:.16,ease:"power2.out",'
                     f'immediateRender:false}},{t:.3f});')
            self.add(f'tl.set("#blur",{{filter:"blur(0px)"}},{t + 0.17:.3f});')
        for b in r.cfg["beats"]:
            getattr(self, "beat_" + b["type"])(b)
        return "\n      ".join(self.html), "\n      ".join(self.js)

    # ---------------------------------------------------------------- beats
    def beat_title(self, b):
        a, e = self.T(b["from"]), self.T(b["to"])
        inner = (f'<div class="card"><div class="l1 t">{esc(b["l1"])}</div>'
                 f'<div class="l2 t">{esc(b["l2"])}</div></div>')
        cid = self.clip("band title", a, e, [2, 3], inner)
        if a > 0.05:
            self.add(f'tl.fromTo("#{cid} .card",{{scale:.6,opacity:0}},{{scale:1,opacity:1,duration:.22,'
                     f'ease:"back.out(2.2)",immediateRender:false}},{a:.3f});')
        self.add(f'tl.fromTo("#{cid} .card",{{rotation:0}},{{rotation:-1.5,duration:{e - a - 0.15:.3f},'
                 f'ease:"sine.inOut",immediateRender:false}},{a:.3f});')
        self.add(f'tl.to("#{cid} .inner",{{scale:.7,opacity:0,duration:.12,ease:"power2.in"}},{e - 0.12:.3f});')

    def beat_big(self, b):
        a, e = self.T(b["from"]), self.T(b["to"])
        lines, k = [], 0
        for ln in b["lines"]:
            chars = []
            for ch in ln:
                if ch == " ":
                    chars.append('<span class="sp"> </span>')
                else:
                    chars.append(f'<span class="ch" data-k="{k}">{esc(ch)}</span>')
                    k += 1
            lines.append(f'<div class="bl t">{"".join(chars)}</div>')
        cid = self.clip("band big", a, e, [2, 3], "".join(lines))
        span = float(b.get("span", 0.5))
        for j in range(k):
            t = a + span * j / max(k - 1, 1)
            self.add(f'tl.fromTo("#{cid} [data-k=\\"{j}\\"]",{{opacity:0,scale:.4,y:"2cqw"}},'
                     f'{{opacity:1,scale:1,y:0,duration:.14,ease:"back.out(3)",immediateRender:false}},{t:.3f});')
        self.exit(cid, e, 0)

    def beat_caption(self, b):
        a = self.T(b.get("from", b["words"][0][1]))
        e = self.T(b["to"])
        cid = self.clip("band cap", a, e, [4, 5], f'<div class="cap t">{self.words_html(b["words"], "@@")}</div>')
        self.fix_ids(cid)
        if b.get("exit", True):
            self.exit(cid, e)

    def beat_wrong(self, b):
        a, e = self.T(b["from"]), self.T(b["to"])
        inner = f'<div class="wrong t">{esc(b["text"])}<div class="strike"></div></div>'
        cid = self.clip("band wr", a, e, [6, 7], inner)
        self.add(f'tl.fromTo("#{cid} .wrong",{{scale:.5,opacity:0}},{{scale:1,opacity:1,duration:.2,'
                 f'ease:"back.out(2.5)",immediateRender:false}},{a:.3f});')
        self.add(f'tl.fromTo("#{cid} .wrong",{{x:0}},{{keyframes:[{{x:"-1.4cqw",duration:.05}},{{x:"1.4cqw",duration:.06}},'
                 f'{{x:"-.8cqw",duration:.05}},{{x:0,duration:.05}}],immediateRender:false}},{a + 0.2:.3f});')
        if b.get("strike"):
            t = self.T(b["strike"])
            self.add(f'tl.set("#{cid} .strike",{{scaleX:0,rotation:-3,transformOrigin:"0% 50%"}},{a:.3f});')
            self.add(f'tl.fromTo("#{cid} .strike",{{scaleX:0}},{{scaleX:1,duration:.14,ease:"power3.out",'
                     f'immediateRender:false}},{t:.3f});')
            sid = self.clip("stk xmark", t, e, [12, 13], '<img src="stickers/x.png" alt="">')
            self.add(f'tl.fromTo("#{sid} img",{{scale:0,rotation:-25}},{{scale:1,rotation:-6,duration:.2,'
                     f'ease:"back.out(2.4)",immediateRender:false}},{t:.3f});')
        self.exit(cid, e, 0)

    def beat_keyword(self, b):
        a, e = self.T(b["from"]), self.T(b["to"])
        inner = f'<div class="kw t">{esc(b["text"])}</div>'
        if b.get("meaning"):
            inner += f'<div class="mean t">{self.words_html(b["meaning"], "@@", "w m", "m")}</div>'
        elif b.get("meaning_lines"):
            inner += "".join(f'<div class="mean t ml" data-ml="{i}">{esc(x)}</div>'
                             for i, x in enumerate(b["meaning_lines"]))
        cid = self.clip("band key", a, e, [8, 9], inner)
        self.fix_ids(cid)
        self.add(f'tl.fromTo("#{cid} .kw",{{scale:.45,opacity:0,y:"-4cqh"}},{{scale:1,opacity:1,y:0,duration:.24,'
                 f'ease:"back.out(2.4)",immediateRender:false}},{a:.3f});')
        if b.get("meaning_lines"):
            for i, t in enumerate(b["meaning_at"]):
                self.add(f'tl.fromTo("#{cid} [data-ml=\\"{i}\\"]",{{opacity:0,scale:.6}},{{opacity:1,scale:1,'
                         f'duration:.18,ease:"back.out(2.4)",immediateRender:false}},{self.T(t):.3f});')
        self.exit(cid, e, -4)

    def beat_example(self, b):
        a = self.T(b["en"][0][1])
        e = self.T(b["to"])
        en = [list(w) for w in b["en"]]
        es = [list(w) for w in b["es"]]
        en[0][0] = "“" + en[0][0]
        en[-1][0] = en[-1][0] + "”"
        es[0][0] = "“" + es[0][0]
        es[-1][0] = es[-1][0] + "”"
        inner = (f'<div class="ex en t">{self.words_html(en, "@@", "w", "n")}</div>'
                 f'<div class="ex es t">{self.words_html(es, "@@", "w e", "s")}')
        if b.get("emoji"):
            inner += f' <img class="w emo" data-i="emo" src="stickers/{b["emoji"]}.png" alt="">'
        inner += "</div>"
        style = f' style="font-size:{b["size"]}cqw"' if b.get("size") else ""
        inner = inner.replace('class="ex en t"', f'class="ex en t"{style}').replace('class="ex es t"', f'class="ex es t"{style}')
        cid = self.clip("band exm", a, e, [10, 11], inner)
        self.fix_ids(cid)
        if b.get("emoji"):
            t = self.T(b.get("emoji_at", b["es"][-1][1]))
            self.add(f'tl.fromTo("#{cid} [data-i=\\"emo\\"]",{{opacity:0,scale:0,rotation:-30}},{{opacity:1,scale:1,'
                     f'rotation:0,duration:.22,ease:"back.out(2.6)",immediateRender:false}},{t:.3f});')
        self.exit(cid, e)

    def beat_sticker(self, b):
        a, e = self.T(b["seq"][0][1]), self.T(b["to"])
        pos = b.get("pos", "left")
        imgs = "".join(f'<img data-s="{i}" src="stickers/{img}.png" alt="">' for i, (img, _) in enumerate(b["seq"]))
        cid = self.clip(f"stk {pos}", a, e, [12, 13], imgs)
        grow = float(b.get("grow", 0))
        for i, (_, t) in enumerate(b["seq"]):
            t = self.T(t)
            s = 1 + grow * i
            self.add(f'tl.fromTo("#{cid} [data-s=\\"{i}\\"]",{{opacity:0,scale:0,rotation:-18}},{{opacity:1,'
                     f'scale:{s:.2f},rotation:-6,duration:.22,ease:"back.out(2.6)",immediateRender:false}},{t:.3f});')
            if i:
                self.add(f'tl.set("#{cid} [data-s=\\"{i - 1}\\"]",{{opacity:0}},{t + 0.04:.3f});')
        self.add(f'tl.fromTo("#{cid} .inner",{{y:0}},{{y:"-1cqh",duration:{e - a - 0.14:.3f},ease:"sine.inOut",'
                 f'immediateRender:false}},{a:.3f});')
        self.exit(cid, e, 0)

    def fix_ids(self, cid):
        """words_html emits selectors with a placeholder clip id; patch them to the real id."""
        self.html[-1] = self.html[-1]
        self.js = [j.replace('"#@@ ', f'"#{cid} ') for j in self.js]


TEMPLATE = """<!doctype html>
<html lang="es" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="vendor/gsap.min.js"></script>
    <style>
@font-face { font-family: "Poppins"; src: url("fonts/Poppins-ExtraBold.woff2") format("woff2"); font-weight: 800; font-display: block; }
@font-face { font-family: "Poppins"; src: url("fonts/Poppins-Bold.woff2") format("woff2"); font-weight: 700; font-display: block; }
@font-face { font-family: "Roboto"; src: url("fonts/Roboto-Medium.woff2") format("woff2"); font-weight: 500; font-display: block; }
:root { --ink: #111111; --white: #ffffff; --cream: #FADEB2; --wrong: #E3262E; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: #000; }
#root { position: relative; width: 1080px; height: 1920px; overflow: hidden; container-type: size;
  background: #000; font-family: "Poppins", sans-serif; color: var(--white); }
#blur, #bw, #cam { position: absolute; inset: 0; }
#cam { transform-origin: %ORIGIN%; will-change: transform; backface-visibility: hidden; }
#cam video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.band { position: absolute; left: 6cqw; right: 6cqw; top: %BAND%cqh; text-align: center; }
.inner { position: relative; }
.t { paint-order: stroke fill; -webkit-text-stroke: var(--sw) var(--ink);
  text-shadow: 0 0.5cqw 1.2cqw rgba(0,0,0,.35); }
.w { display: inline-block; opacity: 0; margin: 0 0.04em; }
.acc { color: var(--cream); }
/* title card */
.title .inner { display: flex; justify-content: center; }
.card { display: inline-block; background: rgba(255,255,255,.94); border-radius: 4.4cqw;
  padding: 2.6cqw 5.2cqw 3cqw; box-shadow: 0 1cqw 3cqw rgba(0,0,0,.25); transform-origin: 50% 50%; }
.card .t { --sw: 1.3cqw; font-weight: 800; font-size: 8.6cqw; line-height: 1.08; letter-spacing: -0.01em;
  white-space: nowrap; text-shadow: none; }
.card .l1 { color: var(--cream); }
/* giant phrase */
.big { top: calc(%BAND%cqh - 1.5cqh); }
.big .bl { --sw: 2.1cqw; font-weight: 800; font-size: 16cqw; line-height: 0.98; letter-spacing: -0.02em; white-space: nowrap; }
.big .ch { display: inline-block; opacity: 0; transform-origin: 50% 80%; }
/* captions */
.cap { --sw: 1.2cqw; font-weight: 700; font-size: 8.2cqw; line-height: 1.04; letter-spacing: -0.04em; }
/* keyword + meaning */
.kw { --sw: 1.7cqw; font-weight: 800; font-size: 11.5cqw; line-height: 1.0; letter-spacing: -0.02em;
  color: var(--cream); white-space: nowrap; }
.mean { --sw: 1.1cqw; font-family: "Roboto", sans-serif; font-weight: 500; font-size: 7cqw; line-height: 1.06;
  letter-spacing: -0.01em; margin-top: 0.6cqh; }
.mean.ml { opacity: 0; }
/* example pair */
.ex { --sw: 1.0cqw; font-weight: 700; font-size: 6cqw; line-height: 1.14; letter-spacing: -0.045em; }
.ex.es { margin-top: 0.8cqh; }
.emo { height: 1.25em; vertical-align: -0.28em; margin-left: 0.2em; -webkit-text-stroke: 0; }
/* wrong answer */
.wr .inner { display: flex; justify-content: center; }
.wrong { --sw: 1.0cqw; position: relative; display: inline-block; font-weight: 800; font-size: 7.8cqw; line-height: 1.04;
  letter-spacing: -0.03em; color: var(--wrong); -webkit-text-stroke: var(--sw) #fff; }
.strike { position: absolute; left: -2%; right: -2%; top: 52%; height: 1.1cqw; background: var(--wrong);
  border: 0.35cqw solid #fff; border-radius: 1cqw; transform-origin: 0 50%; }
/* stickers */
.stk { position: absolute; width: 23cqw; }
.stk.left { left: 3cqw; top: calc(%BAND%cqh - 13.5cqh); }
.stk.right { right: 7cqw; top: calc(%BAND%cqh - 13.5cqh); }
.stk.xmark { right: 8cqw; top: calc(%BAND%cqh - 12cqh); width: 17cqw; }
.stk img { position: absolute; left: 0; top: 0; width: 100%; filter: drop-shadow(0 1cqw 1.4cqw rgba(0,0,0,.35)); }
.xmark img { opacity: 1; }
.stk.left img, .stk.right img { opacity: 0; }
/* white-line transition */
.tl-wrap { position: absolute; inset: 0; overflow: hidden; pointer-events: none; }
.tline { position: absolute; left: 0; top: -40cqh; width: 1.1cqw; height: 180cqh; background: #fff;
  box-shadow: 0 0 2.4cqw 0.6cqw rgba(255,255,255,.85); transform: rotate(-24deg); }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="%DUR%"
         data-width="1080" data-height="1920">
      <div id="blur"><div id="bw"><div id="cam">
        <video id="base" class="clip" src="base.mp4" muted playsinline
               data-start="0" data-duration="%DUR%" data-track-index="0"></video>
      </div></div></div>
      %BODY%
      <audio id="master" class="clip" src="master.m4a" data-start="0" data-duration="%DUR%"
             data-track-index="30" data-volume="1"></audio>
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
      tl.set("#cam", { force3D: true, scale: 1 }, 0);
      %JS%
      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""


def main():
    d = (ROOT / sys.argv[1]).resolve()
    what = sys.argv[2:] or ["base", "audio", "comp"]
    r = Reel(d)
    print(f"{d.name}: {len(r.cuts)} cuts, {r.duration:.2f}s")
    if "base" in what:
        r.build_base()
    if "audio" in what:
        r.build_audio()
    if "comp" in what:
        r.build_comp()
    print("ok:", ", ".join(what))


if __name__ == "__main__":
    main()
