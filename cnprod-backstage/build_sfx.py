"""Synthesize the sound design for the BACKSTAGE / SOLD OUT story (9 s).

Every sound sits on a visible action in fx/compositions/flyer.html:
  0.00  scan sweep           (blueprint scans in)
  0.38  marker scribble      (BACKSTAGE inks on)
  1.05  riser into the hit   (stamp falling)
  1.45  STAMP impact         (SOLD OUT lands, shake, splatter)
  1.90  neon buzz            (EXIT stutters on; again 4.60, 7.25)
  2.05  sparkle tings        (stars)
  2.55  shimmer              (sheens 2.55, 5.20, 7.00)
  3.90  glitch               (again 6.15, 8.05)
  4.85  four kicks           (stage spots fire)
Writes fx/assets/sfx.wav (48 kHz stereo).
"""
import os
import wave

import numpy as np
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fx", "assets", "sfx.wav")
SR = 48000
DUR = 9.0
N = int(SR * DUR)
rng = np.random.default_rng(2026)
L = np.zeros(N)
Rr = np.zeros(N)


def t_axis(d):
    return np.arange(int(d * SR)) / SR


def place(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    sig = sig[: max(0, N - i)]
    gl = gain * np.sqrt(0.5 * (1 - pan))
    gr = gain * np.sqrt(0.5 * (1 + pan))
    L[i : i + len(sig)] += sig * gl
    Rr[i : i + len(sig)] += sig * gr


def bp(x, lo, hi, order=2):
    sos = butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return sosfilt(sos, x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype="high", fs=SR, output="sos"), x)


def sweep_filter(x, f0, f1, bw=0.6, blocks=60):
    """Band-pass whose centre glides from f0 to f1 (block-wise)."""
    out = np.zeros_like(x)
    n = len(x)
    edges = np.linspace(0, n, blocks + 1).astype(int)
    for b in range(blocks):
        a, c = edges[b], edges[b + 1]
        f = f0 * (f1 / f0) ** (b / max(blocks - 1, 1))
        lo, hi = f * (1 - bw / 2), min(f * (1 + bw / 2), SR / 2 - 100)
        seg = bp(x[max(0, a - 2000) : c], lo, hi)
        out[a:c] = seg[-(c - a) :]
    return out


def env(n, attack, release, shape=3.0):
    e = np.ones(n)
    a = int(attack * SR)
    r = int(release * SR)
    if a:
        e[:a] = np.linspace(0, 1, a) ** 2
    if r:
        e[-r:] *= np.linspace(1, 0, r) ** shape
    return e


# 0.00 scan sweep ----------------------------------------------------------
d = 0.9
x = rng.normal(0, 1, int(d * SR))
x = sweep_filter(x, 900, 5200, 0.5)
x *= env(len(x), 0.02, 0.35)
hum = np.sin(2 * np.pi * 110 * t_axis(d)) * 0.25 * env(int(d * SR), 0.02, 0.4)
place(x * 0.55 + hum * 0.4, 0.0, 0.5)

# 0.38 marker scribble -------------------------------------------------------
d = 0.66
t = t_axis(d)
x = hp(rng.normal(0, 1, len(t)), 2200)
strokes = 0.5 + 0.5 * np.sin(2 * np.pi * 11 * t + 2 * np.sin(2 * np.pi * 3 * t))
x *= strokes ** 2 * env(len(t), 0.03, 0.12)
for k, at in enumerate(np.linspace(0, d, 8)):
    pan = -0.6 + 1.2 * at / d
    place(x[int(at * SR) : int((at + d / 8) * SR)], 0.38 + at, 0.35, pan)

# 1.05 riser ------------------------------------------------------------------
d = 0.42
x = rng.normal(0, 1, int(d * SR))
x = sweep_filter(x, 300, 7000, 0.7)
x *= np.linspace(0, 1, len(x)) ** 2.5
place(x, 1.45 - d, 0.75)

# 1.45 STAMP impact -----------------------------------------------------------
d = 1.4
t = t_axis(d)
f = 38 + 40 * np.exp(-t * 18)
sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.2)
body = lp(rng.normal(0, 1, len(t)), 900) * np.exp(-t * 16) * 1.4
click = hp(rng.normal(0, 1, len(t)), 3000) * np.exp(-t * 90)
slap = bp(rng.normal(0, 1, len(t)), 1200, 4200) * np.exp(-t * 28) * 0.8
tail = lp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t * 3.2) * 0.12
hit = sub * 1.25 + body + click * 0.6 + slap + tail
hit = np.tanh(hit * 1.6) / np.tanh(1.6)
place(hit, 1.45, 0.95)
# splatter: tiny wet ticks spreading out
for k in range(14):
    at = 1.47 + rng.uniform(0, 0.35)
    dd = 0.05
    tick = bp(rng.normal(0, 1, int(dd * SR)), 2500, 7000) * np.exp(-t_axis(dd) * 120)
    place(tick, at, 0.22, rng.uniform(-0.9, 0.9))

# neon buzz (EXIT) ---------------------------------------------------------------
def buzz(d):
    t = t_axis(d)
    s = np.sign(np.sin(2 * np.pi * 100 * t)) * 0.5 + np.sin(2 * np.pi * 200 * t) * 0.3
    s = bp(s, 120, 3200)
    return s


seq = [(1.9, 0.9), (1.97, 0), (2.03, 1), (2.1, 0.15), (2.17, 0), (2.27, 1),
       (4.6, 0.2), (4.65, 1), (4.73, 0), (4.8, 1),
       (7.25, 0), (7.32, 1), (7.36, 0.3), (7.42, 1)]
gate = np.zeros(N)
for (a, v), nxt in zip(seq, seq[1:] + [(DUR, 0)]):
    gate[int(a * SR) : int(nxt[0] * SR)] = v
# The buzz is loud only around the flickers, then sits very low.
loud = np.zeros(N)
for a, b in [(1.9, 2.55), (4.6, 5.0), (7.25, 7.65)]:
    loud[int(a * SR) : int(b * SR)] = 1
loud = np.convolve(loud, np.ones(2400) / 2400, mode="same")
g = gate * (0.06 + 0.5 * loud)
g = np.convolve(g, np.ones(96) / 96, mode="same")
bz = buzz(DUR)[:N] * g
L += bz * 0.32 * 0.8
Rr += bz * 0.32 * 1.1

# sparkle tings ---------------------------------------------------------------
def ting(freq):
    d = 0.7
    t = t_axis(d)
    s = (np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(2 * np.pi * freq * 2.76 * t)) * np.exp(-t * 7)
    return s * env(len(t), 0.002, 0.1)


stars = [(2.05, 2637, 0.1), (2.25, 3136, 0.6), (2.45, 2349, -0.5), (3.2, 3520, 0.2),
         (5.35, 3136, 0.6), (5.55, 2637, 0.1), (6.75, 3520, 0.2), (7.55, 2349, -0.5)]
for at, fr, pan in stars:
    place(ting(fr), at, 0.11, pan)

# shimmer on the sheens -------------------------------------------------------------
for at, dur in [(2.55, 0.75), (5.2, 0.8), (7.0, 0.75)]:
    x = rng.normal(0, 1, int(dur * SR))
    x = sweep_filter(x, 4000, 9000, 0.4)
    x *= np.sin(np.linspace(0, np.pi, len(x))) ** 2
    place(x, at, 0.16)

# glitch hits ---------------------------------------------------------------------
def glitch(d, seed):
    r = np.random.default_rng(seed)
    n = int(d * SR)
    out = np.zeros(n)
    i = 0
    while i < n:
        seg = int(r.uniform(0.012, 0.04) * SR)
        kind = r.integers(0, 3)
        tt = np.arange(seg) / SR
        if kind == 0:
            s = np.sign(np.sin(2 * np.pi * r.uniform(300, 1800) * tt))
        elif kind == 1:
            s = r.normal(0, 1, seg)
            step = r.integers(6, 30)
            s = np.repeat(s[::step], step)[:seg]
        else:
            s = np.zeros(seg)
        out[i : i + seg] = s[: n - i] * r.uniform(0.4, 1)
        i += seg
    return out * env(n, 0.003, 0.02)


for at, d, seed in [(3.9, 0.27, 7), (6.15, 0.33, 19), (8.05, 0.23, 31)]:
    place(glitch(d, seed), at, 0.3, 0.0)

# four kicks under the stage spots ----------------------------------------------
def kick():
    d = 0.45
    t = t_axis(d)
    f = 48 + 120 * np.exp(-t * 30)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    s += hp(rng.normal(0, 1, len(t)), 4000) * np.exp(-t * 200) * 0.3
    return s


for at in [4.85, 5.05, 5.25, 5.45]:
    place(kick(), at, 0.6)

# master -----------------------------------------------------------------------------
mix = np.stack([L, Rr], axis=1)
fade = np.ones(N)
fade[-int(0.25 * SR) :] = np.linspace(1, 0, int(0.25 * SR))
mix *= fade[:, None]
peak = np.abs(mix).max()
mix = mix / peak * 0.89
pcm = (mix * 32767).astype(np.int16)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with wave.open(OUT, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", OUT, f"peak before norm {peak:.2f}")
