"""Split the poster into animatable layers.

Every layer is an RGBA cut-out "unmixed" against the paper plate, so stacking
all of them over plate.png gives the poster back. The bus is the exception: an
opaque cut-out, with its spot on the road filled so it can drive in.

Writes edit/assets/*.png and work/layers.json (positions in the 1080x1920 frame).
"""
import json
import os

import cv2
import numpy as np

W, H = 1080, 1920
OUT = "edit/assets"
os.makedirs(OUT, exist_ok=True)

poster = cv2.imread("work/poster1080.png").astype(np.float32) / 255
plate = cv2.imread("work/plate.png").astype(np.float32) / 255
cv2.imwrite(f"{OUT}/plate.png", (plate * 255).round().astype(np.uint8))
cv2.imwrite(f"{OUT}/poster.png", (poster * 255).round().astype(np.uint8))


def unmix(c, p):
    """Smallest alpha + colour so that a*F + (1-a)*p == c."""
    a_dark = ((p - c) / np.maximum(p, 1e-4)).max(axis=2)
    a_light = ((c - p) / np.maximum(1 - p, 1e-4)).max(axis=2)
    a = np.clip(np.maximum(a_dark, a_light), 0, 1)
    f = (c - (1 - a[..., None]) * p) / np.maximum(a[..., None], 1e-4)
    a[a < 1.5 / 255] = 0
    return np.clip(f, 0, 1), a


def poly(pts):
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.array(pts, np.int32)], 1)
    return m


def rect(x0, y0, x1, y1):
    return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def star(cx, cy, rv, rh, r=15):
    return poly([(cx, cy - rv), (cx + r, cy - r), (cx + rh, cy), (cx + r, cy + r),
                 (cx, cy + rv), (cx - r, cy + r), (cx - rh, cy), (cx - r, cy - r)])


def ellipse_zone(cx, cy, ax, ay, ang):
    m = np.zeros((H, W), np.uint8)
    cv2.ellipse(m, (cx, cy), (ax, ay), ang, 0, 360, 1, -1)
    return m


layout = {}


def save(name, f, a, mask, pad=6):
    """Write the masked RGBA layer cropped to its ink, record its box."""
    am = a * mask
    ys, xs = np.nonzero(am > 0)
    x0, y0 = max(xs.min() - pad, 0), max(ys.min() - pad, 0)
    x1, y1 = min(xs.max() + pad + 1, W), min(ys.max() + pad + 1, H)
    rgba = np.dstack([f[y0:y1, x0:x1], am[y0:y1, x0:x1]])
    cv2.imwrite(f"{OUT}/{name}.png", (rgba * 255).round().astype(np.uint8))
    layout[name] = dict(x=int(x0), y=int(y0), w=int(x1 - x0), h=int(y1 - y0))


# ---------------------------------------------------------------- bus
bus_pts = json.load(open("bus_poly.json"))
bus_hard = poly(bus_pts)
bus_hard = cv2.dilate(bus_hard, np.ones((5, 5), np.uint8))
bus_a = cv2.GaussianBlur(bus_hard.astype(np.float32), (0, 0), 1.0)
ys, xs = np.nonzero(bus_a > 0.01)
bx0, by0, bx1, by1 = xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3
bus_rgba = np.dstack([poster[by0:by1, bx0:bx1], bus_a[by0:by1, bx0:bx1]])
cv2.imwrite(f"{OUT}/bus.png", (bus_rgba * 255).round().astype(np.uint8))
layout["bus"] = dict(x=int(bx0), y=int(by0), w=int(bx1 - bx0), h=int(by1 - by0))

# Road under the bus: inpainted, so the few pixels the moving bus uncovers
# continue the sky and road around it.
hole = cv2.dilate(bus_hard, np.ones((7, 7), np.uint8))
road_img = poster.copy()
p8 = (poster * 255).round().astype(np.uint8)
inp = cv2.inpaint(p8, hole, 9, cv2.INPAINT_TELEA).astype(np.float32) / 255
road_img[hole > 0] = inp[hole > 0]

f_all, a_all = unmix(poster, plate)
f_road, a_road = unmix(road_img, plate)

# ---------------------------------------------------------------- regions
# Priority order: an ink pixel goes to the first region that claims it.
taken = np.zeros((H, W), np.uint8)
regions = []


def claim(name, mask, src="all"):
    m = mask * (1 - taken)
    taken[m > 0] = 1
    regions.append((name, m, src))


stars = {
    "star-tl": star(539, 490, 62, 58),
    "star-tb": star(540, 808, 62, 58),
    "star-r1": star(811, 910, 55, 52),
    "star-r2": star(947, 893, 58, 55),
    "star-bus": star(944, 1273, 58, 40),
    "star-bl": star(139, 1665, 62, 52),
}
for k, m in stars.items():
    claim(k, m)

pin_shape = lambda x0, y0, x1, y1: poly([(x0, y0), (x1, y0), (x1, y1 - 28),
                                         ((x0 + x1) // 2, y1), (x0, y1 - 28)])
claim("pin-raf", pin_shape(214, 858, 288, 953))
claim("pin-sun", pin_shape(214, 1092, 288, 1193))
claim("pin-sf", pin_shape(800, 994, 888, 1111))
claim("tag-raf", rect(86, 903, 401, 1047))
claim("tag-sun", rect(90, 1130, 406, 1273))
claim("tag-sf", rect(652, 1048, 1021, 1224))
claim("rays", rect(722, 945, 968, 1088))
claim("arrow1", rect(395, 918, 716, 1052))
claim("arrow2", rect(395, 1053, 716, 1170))
claim("logo", rect(418, 58, 668, 174))
claim("victoria", rect(212, 190, 908, 291))
claim("whynot", rect(212, 291, 908, 389))
claim("date-sab", rect(226, 389, 452, 434))
claim("date-rule", rect(452, 389, 680, 434))
claim("date-imperio", rect(680, 389, 874, 434))
claim("rule", rect(168, 1676, 948, 1720))
claim("sp1", rect(213, 1724, 314, 1822))
claim("sp2", rect(336, 1722, 526, 1818))
claim("sp3", rect(553, 1738, 737, 1832))
claim("sp4", rect(737, 1710, 870, 1844))

# TRASLADO: thick strokes (opening kills the thin construction lines) are
# letters; split them by column, then hand each ink pixel near a letter to it.
g = (poster[:, :, 1] * 255)
zone = poly([(140, 600), (960, 500), (985, 700), (160, 820)])
dark = ((g < 120) * zone).astype(np.uint8)
op = cv2.morphologyEx(dark, cv2.MORPH_OPEN,
                      cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
n, lab, st, cen = cv2.connectedComponentsWithStats(op, 8)
bounds = [0, 264, 389, 476, 562, 648, 751, 855, W]
letters = ["T", "R", "A1", "S", "L", "A2", "D", "O"]
letter_map = np.zeros((H, W), np.int32)
for i in range(1, n):
    if st[i, cv2.CC_STAT_AREA] < 150:
        continue
    k = np.searchsorted(bounds, cen[i][0]) - 1
    letter_map[lab == i] = k + 1
# nearest letter for every pixel
inv = (letter_map == 0).astype(np.uint8)
dist, near = cv2.distanceTransformWithLabels(inv, cv2.DIST_L2, 5,
                                             labelType=cv2.DIST_LABEL_PIXEL)
# map label index -> letter id through the seed pixels
seed_ids = np.zeros(near.max() + 1, np.int32)
seed_ids[near[inv == 0]] = letter_map[inv == 0]
nearest_letter = seed_ids[near]
near_ok = (dist <= 7) & (zone > 0)
for k, name in enumerate(letters):
    claim(f"l-{name}", ((nearest_letter == k + 1) & near_ok).astype(np.uint8))

# The oval swoosh and construction lines around the word (not the border).
oval = ellipse_zone(550, 655, 552, 182, -9)
oval[:, 43:58] = 0
oval[:, 1021:1036] = 0
claim("oval", oval)

claim("road", poly([(57, 1270), (406, 1270), (406, 1172), (652, 1172), (652, 1226), (1021, 1226),
                    (1021, 1676), (57, 1676)]), src="road")
claim("frame", np.ones((H, W), np.uint8))

for name, m, src in regions:
    f, a = (f_road, a_road) if src == "road" else (f_all, a_all)
    if name == "frame":
        a = a.copy()
        a[bus_hard > 0] = 0  # bus pixels live only in bus.png
    if (a * m).max() == 0:
        print("empty layer", name)
        continue
    save(name, f, a, m)

layout["letters"] = letters
json.dump(layout, open("work/layers.json", "w"), indent=1)
print("layers:", len(layout) - 1)

# Motion-blurred bus for the fast first half of the drive-in (premultiplied).
k = np.ones((1, 41), np.float32) / 41
pm = bus_rgba[:, :, :3] * bus_rgba[:, :, 3:]
pad = 30
pm = cv2.copyMakeBorder(pm, 0, 0, pad, pad, cv2.BORDER_CONSTANT, value=0)
al = cv2.copyMakeBorder(bus_rgba[:, :, 3], 0, 0, pad, pad, cv2.BORDER_CONSTANT, value=0)
pm_b = cv2.filter2D(pm, -1, k)
al_b = cv2.filter2D(al, -1, k)
col = pm_b / np.maximum(al_b[..., None], 1e-4)
blur = np.dstack([np.clip(col, 0, 1), al_b])
cv2.imwrite(f"{OUT}/bus-blur.png", (blur * 255).round().astype(np.uint8))
b = layout["bus"]
json.dump(dict(layout, **{"bus-blur": dict(x=b["x"] - pad, y=b["y"], w=b["w"] + 2 * pad, h=b["h"])}),
          open("work/layers.json", "w"), indent=1)
