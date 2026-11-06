"""Minimal sound for the BACKSTAGE / SOLD OUT story (7 s).

Two sounds, each on a visible action in fx/compositions/flyer.html:
  0.25  soft pen stroke   (BACKSTAGE wipes on, 0.8 s)
  1.50  one stamp thud    (SOLD OUT touches the paper)
Writes fx/assets/sfx.wav (48 kHz stereo).
"""
import os
import wave

import numpy as np
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fx", "assets", "sfx.wav")
SR = 48000
DUR = 7.0
N = int(SR * DUR)
rng = np.random.default_rng(2026)
L = np.zeros(N)
R = np.zeros(N)


def t_axis(d):
    return np.arange(int(d * SR)) / SR


def place(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    sig = sig[: max(0, N - i)]
    L[i : i + len(sig)] += sig * gain * np.sqrt(0.5 * (1 - pan))
    R[i : i + len(sig)] += sig * gain * np.sqrt(0.5 * (1 + pan))


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x)


# 0.25 pen stroke: band-limited paper friction, panned left to right with the wipe.
d = 0.8
t = t_axis(d)
x = filt(rng.normal(0, 1, len(t)), "band", [1800, 6500])
x *= np.sin(np.pi * t / d) ** 1.5 * (0.75 + 0.25 * np.sin(2 * np.pi * 5 * t))
for k in range(8):
    a, b = int(k * len(t) / 8), int((k + 1) * len(t) / 8)
    place(x[a:b], 0.25 + a / SR, 0.18, -0.5 + k / 7)

# 1.50 stamp: a short low thud with a dry paper slap, no tail.
d = 0.6
t = t_axis(d)
f = 52 + 50 * np.exp(-t * 25)
thud = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
slap = filt(rng.normal(0, 1, len(t)), "band", [900, 3500]) * np.exp(-t * 45) * 0.55
hit = np.tanh((thud + slap) * 1.3) / np.tanh(1.3)
place(hit, 1.5, 0.9)

mix = np.stack([L, R], axis=1)
mix = mix / np.abs(mix).max() * 0.89
pcm = (mix * 32767).astype(np.int16)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with wave.open(OUT, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", OUT)
