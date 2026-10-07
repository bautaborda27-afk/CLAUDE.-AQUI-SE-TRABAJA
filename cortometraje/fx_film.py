#!/usr/bin/env python3
"""Render the film layer: edit/base.mp4 -> work/film_fx.mp4 (1920x1080, 30 fps).

Applies, frame by frame and deterministically, everything that touches the
footage pixels: B/W film grade, exposure flashes and dips, pixel reveals,
focus blur, digital glitch, the camera rig (zoom-through, whip pans with the
neighbouring shot's still, punch-ins, slow pushes, shake), directional whip
blur, vignette and heartbeat pulse, red/white/black flashes, dust and
scratches, and the letterbox bars. Timing comes from fx_tracks.py / plan.py.

  python3 fx_film.py                     # whole film
  python3 fx_film.py --from 97 --to 101 --out work/test.mp4   # a range, for checks
"""
import argparse
import math
import subprocess
from collections import deque
from pathlib import Path

import cv2
import numpy as np

import fx_tracks as fx
from plan import FILM, FPS, GLITCHES, TOTAL

ROOT = Path(__file__).resolve().parent
EDIT = ROOT / "edit"
W, H = fx.W, fx.H
CX, CY = W / 2, H / 2
GLITCH_STRENGTH = [0.9, 0.7, 0.8, 1.0, 0.6, 1.0]
RED_BGR = np.array([0x1B, 0x20, 0xE0], np.float32) / 255

# ---- film grade: contrast S, deeper blacks --------------------------------------
_x = np.arange(256) / 255
_y = np.clip(0.5 + (_x - 0.5) * 1.22 - 0.035 * (1 - _x) ** 3, 0, 1) ** 1.04
LUT = (_y * 255 + 0.5).astype(np.uint8)

_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.sqrt(((_xx - CX) / (W * 0.5)) ** 2 + ((_yy - CY) / (H * 0.5)) ** 2)
VIG = (1 - 0.42 * np.clip((_r - 0.55) / 0.8, 0, 1) ** 1.6).astype(np.float32)
# heartbeat pulse: radial-gradient(ellipse 70% 62%, transparent 35%, black .92 100%)
_rp = np.sqrt(((_xx - CX) / (0.70 * W)) ** 2 + ((_yy - CY) / (0.62 * H)) ** 2)
PULSE = (0.92 * np.clip((_rp - 0.35) / 0.65, 0, 1)).astype(np.float32)
del _yy, _xx, _r, _rp


def aff(o, s=1.0, rot=0.0, tx=0.0, ty=0.0):
    """CSS-style transform about origin o: p' = o + t + R*S*(p - o)."""
    c, sn = math.cos(math.radians(rot)) * s, math.sin(math.radians(rot)) * s
    return np.array([[c, -sn, o[0] + tx - c * o[0] + sn * o[1]],
                     [sn, c, o[1] + ty - sn * o[0] - c * o[1]],
                     [0, 0, 1]], np.float64)


def mul(img, mask):
    return (img * (mask if img.ndim == 2 else mask[..., None])).astype(np.uint8)


def glitch(g, i, strength):
    rng = np.random.default_rng(1000 + i)
    img = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
    for _ in range(rng.integers(3, 9)):                      # horizontal line tears
        y0, hh = int(rng.integers(0, H - 10)), int(rng.integers(6, 70))
        img[y0:y0 + hh] = np.roll(img[y0:y0 + hh], int(rng.integers(-90, 90) * strength), axis=1)
    for _ in range(rng.integers(1, 4)):                      # displaced blocks
        bw, bh = int(rng.integers(80, 320)), int(rng.integers(30, 140))
        x0, y0 = int(rng.integers(0, W - bw)), int(rng.integers(0, H - bh))
        sx = int(np.clip(x0 + rng.integers(-150, 150), 0, W - bw))
        sy = int(np.clip(y0 + rng.integers(-60, 60), 0, H - bh))
        img[y0:y0 + bh, x0:x0 + bw] = img[sy:sy + bh, sx:sx + bw]
    dx = int(rng.integers(6, 18) * strength)                 # RGB channel split
    img[..., 2] = np.roll(img[..., 2], dx, axis=1)
    img[..., 0] = np.roll(img[..., 0], -dx, axis=1)
    if rng.random() < 0.35:                                  # scanline frame
        img[::3] = (img[::3] * 0.7).astype(np.uint8)
    return img


def scratches(seed=7):
    """Deterministic film scratches: (start frame, length, x, drift)."""
    rng = np.random.default_rng(seed)
    out, f = [], int(rng.integers(40, 120))
    while f < FILM * FPS:
        out.append((f, int(rng.integers(8, 22)), int(rng.integers(80, W - 80)), float(rng.uniform(-2, 2))))
        f += int(rng.integers(90, 220))
    return out


SCRATCHES = scratches()
STILLS = {}


def still(frame, tag):
    key = (frame, tag)
    if key not in STILLS:
        g = cv2.imread(str(EDIT / f"assets/stills/cut{frame}_{tag}.jpg"), cv2.IMREAD_GRAYSCALE)
        STILLS[key] = LUT[g]
    return STILLS[key]


def paste(dst, src, dx, dy):
    """Draw src on dst at integer offset (dx, dy), clipped to the frame."""
    x0, y0 = max(0, dx), max(0, dy)
    x1, y1 = min(W, dx + W), min(H, dy + H)
    if x1 > x0 and y1 > y0:
        dst[y0:y1, x0:x1] = src[y0 - dy:y1 - dy, x0 - dx:x1 - dx]


def render_frame(i, g, history):
    t = i / FPS
    g = LUT[g]
    e = fx.exposure.at(t)
    if abs(e) > 1e-3:
        g = cv2.convertScaleAbs(g, alpha=2 ** e)
    pv = fx.pixel.at(t)
    if pv > 0.005:
        b = int(round(4 + 60 * pv))
        g = cv2.resize(cv2.resize(g, (W // b, H // b), interpolation=cv2.INTER_AREA), (W, H),
                       interpolation=cv2.INTER_NEAREST)
    bv = fx.blur.at(t)
    if bv > 0.005:
        k = int(2 * round(2.5 * 36 * bv) + 1)
        g = cv2.stackBlur(g, (k, k))

    img = g
    for gi, (s, e2) in enumerate(GLITCHES):
        if s <= t < e2:
            rng = np.random.default_rng(5000 + i)
            src = LUT[history[0]] if (len(history) == history.maxlen and rng.random() < 0.25) else g
            img = glitch(src, i, GLITCH_STRENGTH[gi])
            break

    # camera rig: tr > pu > kb > sh
    shx, shy, shr, shs = fx.shake_at(t)
    ox, oy = fx.kb_origin(t)
    trx, try_ = fx.tr_x.at(t), fx.tr_y.at(t)
    m = (aff((CX, CY), fx.tr_s.at(t), 0, trx, try_) @ aff((CX, CY), fx.pu.at(t)) @
         aff((ox * W, oy * H), fx.kb.at(t)) @ aff((CX, CY), shs, shr, shx, shy))
    if not np.allclose(m, np.eye(3), atol=1e-6):
        img = cv2.warpAffine(img, m[:2], (W, H), flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=0)

    wh = fx.active_whip(t)
    if wh:
        c, direction, before = wh
        frame = int(round(c * FPS))
        sign = 1 if direction in ("left", "up") else -1
        off = sign if before else -sign
        gs = still(frame, "b" if before else "a")
        if img.ndim == 3:
            gs = cv2.cvtColor(gs, cv2.COLOR_GRAY2BGR)
        if direction == "up":
            paste(img, gs, 0, int(round(off * H + try_)))
        else:
            paste(img, gs, int(round(off * W + trx)), 0)
    vx, vy = fx.mbx.at(t), fx.mby.at(t)
    if vx > 0.5:
        img = cv2.blur(img, (int(vx * 2.5) | 1, 1))
    if vy > 0.5:
        img = cv2.blur(img, (1, int(vy * 2.5) | 1))

    # screen space
    if t < FILM:
        sc = [s for s in SCRATCHES if s[0] <= i < s[0] + s[1]]
        for f0, n, x, drift in sc:
            xx = int(x + drift * (i - f0))
            if 0 <= xx < W:
                img[:, xx] = (img[:, xx] * 0.72 + 255 * 0.28).astype(np.uint8)
        rng = np.random.default_rng(90000 + i)
        for _ in range(rng.poisson(0.6)):
            col = 35 if rng.random() < 0.6 else 220
            cv2.circle(img, (int(rng.integers(0, W)), int(rng.integers(0, H))), int(rng.integers(1, 4)),
                       (col, col, col) if img.ndim == 3 else col, -1, cv2.LINE_AA)
    mask = VIG
    p = fx.pulse.at(t)
    if p > 0.003:
        mask = VIG * (1 - p * PULSE)
    img = mul(img, mask)
    a = fx.red.at(t)
    if a > 0.003:
        if img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        img = np.clip(img * ((1 - a) + a * RED_BGR), 0, 255).astype(np.uint8)
    a = fx.white.at(t)
    if a > 0.003:
        img = cv2.addWeighted(img, 1 - a, np.full_like(img, 255), a, 0)
    a = fx.black.at(t)
    if a > 0.003:
        img = cv2.convertScaleAbs(img, alpha=1 - a)
    b = int(round(fx.bars.at(t)))
    if b > 0:
        img[:b] = 0
        img[H - b:] = 0
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float, default=TOTAL)
    ap.add_argument("--out", default=str(ROOT / "work/film_fx.mp4"))
    ap.add_argument("--crf", default="12")
    a = ap.parse_args()
    f0, f1 = int(round(a.t0 * FPS)), int(round(a.t1 * FPS))
    n_base = int(round(FILM * FPS))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)

    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{max(0, f0 - 3) / FPS:.4f}", "-i",
                            str(EDIT / "base.mp4"), "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                           stdout=subprocess.PIPE, bufsize=W * H * 4)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                            "-preset", "veryfast", "-crf", a.crf, "-pix_fmt", "yuv420p", a.out],
                           stdin=subprocess.PIPE)
    history = deque(maxlen=3)
    black = np.zeros((H, W), np.uint8)
    i = max(0, f0 - 3)
    while i < f1:
        buf = dec.stdout.read(W * H) if i < n_base else b""
        g = np.frombuffer(buf, np.uint8).reshape(H, W) if len(buf) == W * H else black
        if i >= f0:
            enc.stdin.write(render_frame(i, g, history).tobytes())
        history.append(g)
        i += 1
        if i % 300 == 0:
            print(f"  {i / FPS:7.1f}s", flush=True)
    enc.stdin.close()
    enc.wait()
    dec.kill()
    print(f"wrote {a.out} ({(f1 - f0) / FPS:.2f}s)")


if __name__ == "__main__":
    main()
