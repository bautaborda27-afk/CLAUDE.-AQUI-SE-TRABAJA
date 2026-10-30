"""Poster -> 1080x1920 frame, ink mask and an ink-free paper plate.

The plate equals the poster wherever there is no ink; under the ink it is the
smoothed paper tone plus paper grain borrowed from clean pixels nearby.
"""
import cv2
import numpy as np

W, H = 1080, 1920
src = cv2.imread("source/placa-traslado.png")
poster = cv2.resize(src, (W, H), interpolation=cv2.INTER_LANCZOS4)
cv2.imwrite("work/poster1080.png", poster)
img = poster.astype(np.float32)

# Ink: purple absorbs green, so green drop against the paper is the cue.
PAPER_G = 205.0
ink = (PAPER_G - img[:, :, 1]) > 17
ink = ink.astype(np.uint8)
n, lab, stats, _ = cv2.connectedComponentsWithStats(ink, connectivity=8)
small = stats[:, cv2.CC_STAT_AREA] < 6
ink[small[lab]] = 0
ink = cv2.dilate(ink, np.ones((5, 5), np.uint8))
cv2.imwrite("work/ink.png", ink * 255)

# Smooth paper tone, ignoring ink (normalized convolution).
clean = (1 - ink).astype(np.float32)
num = cv2.GaussianBlur(img * clean[:, :, None], (0, 0), 25)
den = cv2.GaussianBlur(clean, (0, 0), 25)[:, :, None]
smooth = num / np.maximum(den, 1e-3)
# Large ink blocks leave holes in the estimate: fall back to the global paper.
paper = np.array([196.0, 205.0, 221.0], np.float32)  # BGR
wgt = np.clip(den / 0.25, 0, 1)
smooth = smooth * wgt + paper * (1 - wgt)

# Grain: residual on clean pixels; under ink, borrow from shifted copies.
grain = (img - smooth) * clean[:, :, None]
have = clean.copy()
for dx, dy in [(37, 11), (-29, 23), (13, -41), (-47, -17), (61, 5), (-7, 67),
               (83, -31), (-91, 43), (120, 70), (-130, -90), (170, -150), (-200, 160)]:
    sh_g = np.roll(grain, (dy, dx), axis=(0, 1))
    sh_h = np.roll(have, (dy, dx), axis=(0, 1))
    take = (have == 0) & (sh_h > 0)
    grain[take] = sh_g[take]
    have[take] = 1
grain = np.clip(grain, -18, 18)
plate = np.clip(smooth + grain, 0, 255)
plate[clean > 0] = img[clean > 0]
cv2.imwrite("work/plate.png", plate.astype(np.uint8))
print("ink coverage %.1f%%" % (100 * ink.mean()), "unfilled", int((have == 0).sum()))
