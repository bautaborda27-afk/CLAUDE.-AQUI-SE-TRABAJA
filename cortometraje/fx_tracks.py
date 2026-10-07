"""Animation tracks for the film layer, compiled from plan.py.

Each property is a chain of non-overlapping steps (fromTo / set), evaluated with
GSAP's easing curves, so fx_film.py can compute any frame independently.
Layer model (outermost first), same as a nested DOM camera rig:

  tr  - transition moves: zoom-through scale, whip x/y (+ ghost still beside it)
  pu  - punch-ins on hits
  kb  - slow push per shot, toward the subject (origin per shot)
  sh  - camera shake (procedural, see shake_at)

Media-level values (exposure in stops, blur/pixelate 0..1) act on the footage
before the camera; overlays (white/black/red/pulse/bars) act on the screen.
"""
import math

from plan import (C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13, CHASE, FILM,
                  HEARTBEATS, HIT, NOTE1, NOTE2, SHAKES, SHOTS, STING, STING_END, TRANSITIONS,
                  WHIP_HALF)

W, H = 1920, 1080
BAR = 60          # letterbox bar height (px) -> ~2:1 picture


# ---- GSAP eases -------------------------------------------------------------
def _power(k, kind):
    if kind == "in":
        return lambda p: p ** k
    if kind == "out":
        return lambda p: 1 - (1 - p) ** k
    return lambda p: (2 * p) ** k / 2 if p < 0.5 else 1 - (2 * (1 - p)) ** k / 2


def ease_fn(name):
    if name in (None, "none", "linear"):
        return lambda p: p
    if name.startswith("steps("):
        n = int(name[6:-1])
        return lambda p: 1.0 if p >= 1 else math.floor(p * n) / n
    if name == "sine.inOut":
        return lambda p: -(math.cos(math.pi * p) - 1) / 2
    fam, kind = name.split(".")
    k = {"power1": 2, "power2": 3, "power3": 4, "power4": 5}[fam]
    return _power(k, kind)


class Track:
    def __init__(self, name, init):
        self.name, self.init, self.ev = name, init, []

    def to(self, t, v, d, ease="power2.out", frm=None):
        self.ev.append((round(t, 4), round(d, 4), v, ease, frm))

    def set(self, t, v):
        self.ev.append((round(t, 4), 0.0, v, None, None))

    def compile(self):
        self.ev.sort(key=lambda e: (e[0], e[1]))
        end = -1.0
        steps = []
        for t, d, v, ease, frm in self.ev:
            assert t >= end - 1e-3, f"{self.name}: step at {t} overlaps previous ending {end}"
            steps.append((t, d, v, ease_fn(ease), frm))
            end = t + d
        self.steps = steps

    def at(self, t):
        cur = self.init
        for t0, d, v, ez, frm in self.steps:
            if t < t0:
                return cur
            if d == 0:
                cur = v
                continue
            a = cur if frm is None else frm
            if t < t0 + d:
                return a + (v - a) * ez((t - t0) / d)
            cur = v
        return cur


exposure = Track("exposure", -2.0)    # stops
blur = Track("blur", 0.0)             # 0..1
pixel = Track("pixel", 0.9)           # 0..1
tr_s = Track("tr_s", 1.0)
tr_x = Track("tr_x", 0.0)
tr_y = Track("tr_y", 0.0)
pu = Track("pu", 1.0)
kb = Track("kb", 1.0)
white = Track("white", 0.0)
black = Track("black", 0.0)
red = Track("red", 0.0)
pulse = Track("pulse", 0.0)
bars = Track("bars", H / 2)
mbx = Track("mbx", 0.0)               # directional whip blur, px (std dev)
mby = Track("mby", 0.0)
TRACKS = [exposure, blur, pixel, tr_s, tr_x, tr_y, pu, kb, white, black, red, pulse, bars,
          mbx, mby]

KB_ORIGIN = []    # (start, (ox, oy)) per shot, fractions of the frame
WHIPS = []        # (cut, direction)

# ---- slow push per shot (amount, origin toward the subject) -----------------
PUSH = [(1.07, (.50, .50)), (1.12, (.72, .40)), (1.05, (.50, .40)), (1.06, (.60, .50)),
        (1.07, (.45, .50)), (1.10, (.50, .55)), (1.05, (.50, .40)), (1.04, (.50, .50)),
        (1.05, (.50, .40)), (1.07, (.50, .45)), (1.08, (.45, .45)), (1.04, (.50, .50)),
        (1.04, (.50, .50)), (1.08, (.50, .50))]
for (s, e), (amt, origin) in zip(zip(SHOTS, SHOTS[1:]), PUSH):
    KB_ORIGIN.append((s, origin))
    kb.to(s, amt, round(e - s - 0.001, 4), "sine.inOut", frm=1.0)


# ---- transitions -------------------------------------------------------------
def zoom(c, white_peak=0.3):
    tr_s.to(c - 0.2, 1.4, 0.2, "power2.in")
    tr_s.to(c, 1.0, 0.32, "power3.out")
    blur.to(c - 0.2, 0.7, 0.2, "power2.in")
    blur.to(c, 0.0, 0.35, "power2.out")
    white.to(c - 0.08, white_peak, 0.08, "power1.in")
    white.to(c, 0.0, 0.3, "power2.out")


def pixel_reveal(c):
    blur.to(c - 0.15, 0.8, 0.15, "power2.in")
    blur.to(c, 0.0, 0.3, "power2.out")
    pixel.to(c, 0.0, 0.5, "steps(5)", frm=0.6)
    white.to(c - 0.05, 0.2, 0.05, "none")
    white.to(c, 0.0, 0.25, "power2.out")


def whip(c, direction):
    h = WHIP_HALF
    sign = 1 if direction in ("left", "up") else -1
    vertical = direction == "up"
    span = (H if vertical else W) / 2
    axis, mb = (tr_y, mby) if vertical else (tr_x, mbx)
    axis.to(c - h, -sign * span, h, "power3.in")
    axis.to(c, 0, h, "power3.out", frm=sign * span)
    mb.to(c - h, 70, h, "power3.in")
    mb.to(c, 0, h, "power3.out")
    WHIPS.append((c, direction))


def flash(c):
    exposure.to(c - 0.18, 1.6, 0.18, "power2.in")
    exposure.to(c, 0.0, 0.45, "power2.out")
    white.to(c - 0.12, 0.85, 0.12, "power2.in")
    white.to(c, 0.0, 0.45, "power2.out")
    blur.to(c - 0.15, 0.5, 0.15, "power2.in")
    blur.to(c, 0.0, 0.35, "power2.out")


def glitch_cut(c, with_red=False):
    black.set(c, 1)
    black.set(c + 2 / 30, 0)
    pu.to(c, 1.0, 0.25, "power3.out", frm=1.06)
    if with_red:
        red.to(c, 0.0, 0.5, "power2.out", frm=0.75)


def dip(c):
    exposure.to(c - 0.25, -1.6, 0.25, "power2.in")
    exposure.to(c, 0.0, 0.45, "power2.out")
    pu.to(c, 1.0, 0.45, "power3.out", frm=1.18)
    blur.to(c, 0.0, 0.4, "power2.out", frm=0.5)


def slam(c):
    pu.to(c, 1.0, 0.4, "power3.out", frm=1.16)
    red.to(c, 0.0, 0.35, "power2.out", frm=0.6)
    exposure.to(c, 0.0, 0.3, "power2.out")
    blur.to(c, 0.0, 0.3, "power2.out")


def open_eyes():
    bars.to(0.15, BAR, 1.5, "power3.inOut")
    exposure.to(0.0, 0.0, 1.0, "power2.out")
    pixel.to(0.0, 0.0, 0.9, "steps(6)")


def close_eyes():
    bars.to(FILM - 0.5, H / 2, 0.5, "power3.in")


for _tr in TRANSITIONS:
    kind, c = _tr[0], _tr[1]
    if kind == "open":
        open_eyes()
    elif kind == "close":
        close_eyes()
    elif kind == "zoom":
        zoom(c, 0.55 if c == C13 else 0.3)
    elif kind == "pixel":
        pixel_reveal(c)
    elif kind == "whip":
        whip(c, _tr[2])
    elif kind == "flash":
        flash(c)
    elif kind == "glitch":
        glitch_cut(c, with_red=(c == C10))
    elif kind == "dip":
        dip(c)
    elif kind == "slam":
        slam(c)

# ---- moments inside shots ----------------------------------------------------
pu.to(STING, 1.07, 0.12, "power3.out")
pu.to(STING_END, 1.0, 1.4, "power2.inOut")

# note 1: dim + soften the plate under the words, red hit on TIEMPO
exposure.to(NOTE1["start"], -1.0, 0.25, "power2.out")
blur.to(NOTE1["start"], 0.25, 0.25, "power2.out")
exposure.to(NOTE1["end"], 0.0, 0.4, "power2.inOut")
blur.to(NOTE1["end"], 0.0, 0.4, "power2.inOut")
_t_red1 = NOTE1["lines"][-1][-1][1]
red.to(_t_red1, 0.0, 0.35, "power2.out", frm=0.45)
pu.to(_t_red1, 1.0, 0.5, "power3.out", frm=1.06)

# heartbeat build before the second note
for _hb in HEARTBEATS:
    pulse.to(_hb, 0.6, 0.06, "power2.out")
    pulse.to(_hb + 0.06, 0.0, 0.42, "power2.out")
    pu.to(_hb, 1.014, 0.06, "power2.out")
    pu.to(_hb + 0.06, 1.0, 0.3, "power2.out")

# note 2: dim, then the red ENCONTRÉ slam (restored on the jump cut, see slam)
exposure.to(NOTE2["start"], -0.9, 0.25, "power2.out")
blur.to(NOTE2["start"], 0.2, 0.25, "power2.out")
_t_red2 = NOTE2["lines"][-1][-1][1]
red.to(_t_red2, 0.0, 0.6, "power2.out", frm=0.85)
pu.to(_t_red2, 1.04, 0.5, "power3.out", frm=1.12)

# chase music hit
pu.to(HIT, 1.1, 0.07, "power3.out")
pu.to(HIT + 0.07, 1.0, 0.6, "power2.out")
white.to(HIT, 0.0, 0.3, "power2.out", frm=0.55)
red.to(HIT, 0.0, 0.45, "power2.out", frm=0.5)

for _t in TRACKS:
    _t.compile()


def kb_origin(t):
    o = KB_ORIGIN[0][1]
    for s, org in KB_ORIGIN:
        if t >= s:
            o = org
    return o


def active_whip(t):
    """(cut, direction, before_cut) when t is inside a whip window."""
    for c, d in WHIPS:
        if c - WHIP_HALF <= t < c + WHIP_HALF:
            return c, d, t < c
    return None


# ---- camera shake (deterministic sum of sines with burst envelopes) ----------
def _wave(t, f, p):
    tau = 2 * math.pi
    return (math.sin(tau * f[0] * t + p) * 0.55 + math.sin(tau * f[1] * t + p * 2.3) * 0.3 +
            math.sin(tau * f[2] * t + p * 3.7) * 0.35)


def shake_at(t):
    x = y = r = 0.0
    for s, d, a, rot in SHAKES:
        if s <= t <= s + d:
            u = t - s
            e = min(1.0, u / 0.03) * (1 - u / d) ** 2
            f = (6.3, 9.7, 12.1)
            x += a * e * _wave(t, f, 0.4)
            y += a * e * _wave(t, f, 1.9)
            r += rot * e * _wave(t, f, 3.1)
    cs, ce, ca, cr = CHASE
    if cs <= t <= ce:
        e = min(1.0, (t - cs) / 0.5) * min(1.0, (ce - t) / 0.3)
        f = (1.3, 2.9, 4.1)
        x += ca * e * _wave(t, f, 0.7)
        y += ca * e * _wave(t, f, 2.2)
        r += cr * e * _wave(t, f, 1.3)
    s = 1.002 + 2 * max(abs(x) / W, abs(y) / H) + abs(r) * 0.012
    return x, y, r, s
