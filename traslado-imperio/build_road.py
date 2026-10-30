"""Rebuild the empty road the bus hides, so the road can be drawn first.

Below the guardrail the road texture is tiled from the visible road left and
right of the bus, following the road's perspective (lines of constant
v = (y - guardrail(x)) / scale(x)), so lane stripes keep running under it.
Above the guardrail: the hedge on the left tiled along, the trees on the
right mirrored a little into the gap, paper above. The speed lines go to
their own mask (they belong to the moving bus).

Writes work/road_clean.png, work/speed_mask.png, work/bus_hard.png.
"""
import json
import os

import cv2
import numpy as np

import exemplar_fill

W, H = 1080, 1920
PATCH, GW = int(os.environ.get("PATCH", 17)), float(os.environ.get("GW", 3.0))
RAIL = int(os.environ.get("RAIL", 46))
poster = cv2.imread("work/poster1080.png").astype(np.float32)
plate = cv2.imread("work/plate.png").astype(np.float32)

bus = np.zeros((H, W), np.uint8)
cv2.fillPoly(bus, [np.array(json.load(open("bus_poly.json")), np.int32)], 1)
bus_hard = cv2.dilate(bus, np.ones((5, 5), np.uint8))
cv2.imwrite("work/bus_hard.png", bus_hard * 255)
hole = cv2.dilate(bus, np.ones((15, 15), np.uint8))

speed = np.zeros((H, W), np.uint8)
for p in [[(57, 1240), (250, 1240), (250, 1468), (135, 1468), (135, 1428), (57, 1428)],
          [(250, 1172), (652, 1172), (652, 1245), (564, 1243), (479, 1270), (393, 1299),
           (307, 1334), (250, 1372)],
          [(790, 1226), (1021, 1226), (1021, 1330), (850, 1330), (790, 1300)]]:
    cv2.fillPoly(speed, [np.array(p)], 1)
speed[hole > 0] = 0
cv2.imwrite("work/speed_mask.png", speed * 255)

xs = np.arange(W, dtype=np.float32)
G = np.interp(xs, [40, 240, 830, 1030], [1511, 1517, 1542, 1545]).astype(np.float32)  # guardrail top
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
dg = yy - G[None, :]                     # px below the guardrail line


def strip(x0, x1, direction, offset=0.0):
    """Source x: the strip [x0, x1) repeated away from the bus (optionally half-shifted)."""
    P = x1 - x0
    x = xx + offset
    if direction > 0:
        return x0 + np.mod(x - x0, P)
    return x1 - 1 - np.mod(x1 - 1 - x, P)


def along_rail(x0, x1, direction):
    """Guardrail band: the strip slid along the guardrail, two layers cross-faded."""
    P = x1 - x0
    out = []
    for off in (0.0, P / 2):
        sx = strip(x0, x1, direction, direction * off).astype(np.float32)
        sy = (np.interp(sx, xs, G) + dg).astype(np.float32)
        out.append(cv2.remap(poster, sx, sy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT))
    ph = np.mod((xx - x0) / P if direction > 0 else (x1 - 1 - xx) / P, 1.0)
    w = np.clip((np.abs(ph - 0.5) * 2 - 0.7) / 0.3, 0, 1)[..., None]
    return out[0] * (1 - w) + out[1] * w


img = poster.copy()
img[speed > 0] = plate[speed > 0]
# guardrail + the road just under it: slid along the rail from the right side
# (clean, rail-parallel hatching), blending into the left side behind the bus
wl = (1 - np.clip((xx - 250) / 90, 0, 1))[..., None]
rail = along_rail(96, 206, +1) * wl + along_rail(856, 952, -1) * (1 - wl)
rail_band = (dg >= -5) & (dg < RAIL)
h = hole > 0
img[h & rail_band] = rail[h & rail_band]
img[h & (dg < -5)] = plate[h & (dg < -5)]
X0, Y0, X1, Y1 = 40, 1360, 1040, 1690
crop = (slice(Y0, Y1), slice(X0, X1))

# road surface: real patches from around, from a similar depth below the rail
src_ok = np.zeros((H, W), bool)
src_ok[1390:1676, 60:1018] = True
src_ok &= speed == 0
src_ok[1600:1740, 60:200] = False        # star, bottom left
src_ok[1580:1700, 950:1030] = False      # corner circle
# Tone and texture apart: the tone (blurred) is interpolated smoothly, the
# hatching (detail) is copied patch by patch, so copied patches leave no blocks.
unk = (h & (dg >= RAIL))[crop]
c = img[crop]
kn = (~unk).astype(np.float32)
low = cv2.GaussianBlur(c * kn[..., None], (0, 0), 7) / np.maximum(cv2.GaussianBlur(kn, (0, 0), 7), 1e-3)[..., None]
detail = np.clip(c - low + 128, 0, 255)
low_f = cv2.inpaint(np.clip(low, 0, 255).astype(np.uint8), unk.astype(np.uint8), 15, cv2.INPAINT_TELEA).astype(np.float32)
low_f = np.where(unk[..., None], cv2.GaussianBlur(low_f, (0, 0), 9), low)
detail_f = exemplar_fill.fill(detail, unk, src_ok[crop], patch=PATCH, search=(320, 70), guide=GW * dg[crop])
img[crop] = np.where(unk[..., None], low_f + detail_f - 128, c)

# the tree line on the right grows a rounded crown into the gap
bump = np.zeros((H, W), np.uint8)
cv2.ellipse(bump, (858, 1505), (64, 78), 0, 0, 360, 1, -1)
bump = (bump > 0) & h & (dg < -5)
tree_src = np.zeros((H, W), bool)
tree_src[1390:1548, 862:1016] = True
img[crop] = exemplar_fill.fill(img[crop], bump[crop], tree_src[crop], patch=13, search=(200, 90))
fill = img

road_clean = poster.copy()
road_clean[speed > 0] = plate[speed > 0]
# feather the hole edge into the untouched picture
hf = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), 2.0)
hf = np.maximum(hf, bus_hard.astype(np.float32))[..., None]
road_clean = fill * hf + road_clean * (1 - hf)
cv2.imwrite("work/road_clean.png", np.clip(road_clean, 0, 255).astype(np.uint8))
print("road rebuilt")
