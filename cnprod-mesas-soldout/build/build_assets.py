# Builds the assets for the "placa dibujándose" composition.
#
#   python3 build/build_assets.py source-placa.png assets/ [debug_dir]
#
# Outputs (all 1080x1920; photo layers JPEG, data maps lossless PNG):
#   placa.jpg    the poster itself (final frame)
#   papel.jpg    the same sheet of paper with no ink and no watercolor
#   violeta.jpg  the poster with the red ink lifted (purple layer underneath)
#   tiempo.png   when each pixel gets drawn: R,G = seconds (16 bit), B = ramp
#   tiempo-rojo.png  same, for the red layer
#   mascara.png  R = pixel changes over time, G = pixel has a red layer
import sys, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.graph import MCP_Geometric
from skimage.morphology import disk

SRC, OUT = sys.argv[1], sys.argv[2]
DBG = sys.argv[3] if len(sys.argv) > 3 else None
W, H = 1080, 1920
SRC_W = 941
K = W / SRC_W                      # source coords -> canvas coords
T_MAX = 12.0                       # seconds covered by the 16-bit time code
RAMP_UNIT = 0.005                  # seconds per unit of the B channel
LUMA = np.array([0.299, 0.587, 0.114], np.float32)
rng = np.random.default_rng(7)

img = Image.open(SRC).convert('RGB').resize((W, H), Image.LANCZOS)
orig = np.asarray(img).astype(np.float32)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def box_mask(boxes):
    m = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in boxes:
        m[int(y0 * K):int(np.ceil(y1 * K)), int(x0 * K):int(np.ceil(x1 * K))] = True
    return m


def smooth_noise(sigma, amp=1.0):
    n = ndi.gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), sigma)
    return n / (n.std() + 1e-6) * amp


def norm_fill(values, weight, sigma):
    num = ndi.gaussian_filter(values * weight[..., None], (sigma, sigma, 0))
    den = ndi.gaussian_filter(weight.astype(np.float32), sigma)[..., None]
    return num / np.maximum(den, 1e-6), den[..., 0]


# ---------------------------------------------------------------- ink masks
def paper_estimate(src, keep):
    """Local paper colour from the pixels in `keep`, filled in at growing scales."""
    est = np.zeros_like(src)
    have = np.zeros((H, W), bool)
    for s in (14, 40, 120, 400):
        f, den = norm_fill(src, keep, s)
        new = (den > 0.05) & ~have
        est[new] = f[new]
        have |= new
    return est


L = orig @ LUMA
redness = orig[..., 0] - np.maximum(orig[..., 1], orig[..., 2])
# first pass: anything clearly darker than the local bright level is ink
bright = ndi.percentile_filter(ndi.zoom(L, 0.25, order=1), 85, size=51)
bright = ndi.zoom(ndi.gaussian_filter(bright, 6), (H / bright.shape[0], W / bright.shape[1]), order=1)
dark0 = np.clip(bright - L, 0, None)
paper0 = (ndi.gaussian_filter(dark0, 2) < 7) & (redness < 25)
P = paper_estimate(orig, paper0)
dark = np.clip(P @ LUMA - L, 0, None)

red = (redness > 40) & (orig[..., 0] > 80)
red = ndi.binary_dilation(red, iterations=1) & (redness > 18)

# watercolor washes: only inside these regions (source coords)
WASH_REGIONS = {
    'wash_booth': [(185, 380, 580, 612)],
    'wash_vip': [(160, 1252, 735, 1492)],
    'wash_stain': [(778, 1186, 816, 1226)],
}
wash_zone = box_mask([b for v in WASH_REGIONS.values() for b in v])
# inside a wash, ink is what stands out from the wash itself
local_level = ndi.median_filter(dark, size=17)
ink_in_wash = ((dark - local_level) > 20) | (dark > 75)
# the corner hatching is fainter than the rest of the ink
HATCH_REGIONS = [(0, 0, 268, 440), (0, 440, 120, 1200), (0, 1180, 175, 1672), (838, 540, 941, 1260),
                 (735, 1250, 941, 1672)]
hatch_zone = box_mask(HATCH_REGIONS)
ink = np.where(wash_zone, ink_in_wash, dark > np.where(hatch_zone, 15, 30)) | red
ink = ndi.binary_opening(ink, structure=np.ones((2, 2))) | (ink & (dark > 60)) | red
wash = wash_zone & ~ndi.binary_dilation(ink, iterations=1) & (ndi.gaussian_filter(dark, 3) > 7)
wash = ndi.binary_closing(wash, iterations=3) & wash_zone
purple = ink & ~red

# -------------------------------------------------------------- blank paper
# everything that differs from clean paper gets replaced by paper texture
M = ndi.binary_dilation(ink, iterations=2) | wash_zone
Pl = paper_estimate(orig, ~M)
grain = orig - Pl
blank = orig.copy()
todo = M.copy()
offsets = [(0, 0)]
for _ in range(400):
    a = rng.uniform(0, 2 * np.pi)
    r = rng.uniform(90, 520)
    offsets.append((int(r * np.sin(a)), int(r * np.cos(a))))
for dy, dx in offsets[1:]:
    if not todo.any():
        break
    ys, xs = np.nonzero(todo)
    sy, sx = ys + dy, xs + dx
    ok = (sy >= 0) & (sy < H) & (sx >= 0) & (sx < W)
    ys, xs, sy, sx = ys[ok], xs[ok], sy[ok], sx[ok]
    good = ~M[sy, sx]
    ys, xs, sy, sx = ys[good], xs[good], sy[good], sx[good]
    blank[ys, xs] = Pl[ys, xs] + grain[sy, sx]
    todo[ys, xs] = False
if todo.any():
    blank[todo] = Pl[todo]
blank = np.clip(blank, 0, 255)
print('blank leftovers', int(todo.sum()))

# ------------------------------------------------------------- time fields
T = np.full((H, W), np.inf, np.float32)     # purple layer + wash
R = np.full((H, W), 0.06, np.float32)       # ramp (seconds)
T2 = np.full((H, W), np.inf, np.float32)    # red layer
R2 = np.full((H, W), 0.06, np.float32)
claimed = np.zeros((H, W), bool)
claimed_r = np.zeros((H, W), bool)
labels_dbg = np.zeros((H, W), np.int16)
names = []


def geodesic(mask, seeds, slit=None):
    """Geodesic distance inside `mask` from `seeds` (list of (y, x) in canvas px)."""
    cost = np.where(mask, 1.0, np.inf)
    if slit is not None:
        cost[slit] = np.inf
    starts = []
    for sy, sx in seeds:
        ys, xs = np.nonzero(mask & ~(slit if slit is not None else False))
        i = np.argmin((ys - sy) ** 2 + (xs - sx) ** 2)
        starts.append((ys[i], xs[i]))
    d, _ = MCP_Geometric(cost).find_costs(starts)
    return d


def per_component_geodesic(mask, seed_rule):
    """Normalised (0..1) geodesic order inside each connected component."""
    lab, n = ndi.label(mask, structure=np.ones((3, 3)))
    out = np.zeros((H, W), np.float32)
    if n == 0:
        return out, lab, 0
    seeds = []
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        i = np.argmin(seed_rule(ys, xs))
        seeds.append((ys[i], xs[i]))
    d, _ = MCP_Geometric(np.where(mask, 1.0, np.inf)).find_costs(seeds)
    d[~mask] = 0
    d[~np.isfinite(d)] = 0
    mx = ndi.maximum(d, lab, index=np.arange(1, n + 1))
    mx = np.concatenate([[1], np.maximum(mx, 1)])
    out = d / mx[lab]
    out[~mask] = 0
    return out.astype(np.float32), lab, n


def sweep(mask, direction, noise=0.0, along=0.0):
    ys, xs = np.nonzero(mask)
    dx, dy = direction
    nrm = np.hypot(dx, dy)
    dx, dy = dx / nrm, dy / nrm
    p = xx * dx + yy * dy
    q = -xx * dy + yy * dx
    lo, hi = p[mask].min(), p[mask].max()
    s = (p - lo) / max(hi - lo, 1)
    if along:
        qlo, qhi = q[mask].min(), q[mask].max()
        s = (1 - along) * s + along * (q - qlo) / max(qhi - qlo, 1)
    if noise:
        s = s + smooth_noise(6, noise)
    s = np.clip(s, 0, 1)
    return s


def assign(name, m, local, t0, t1, ramp, layer='p'):
    global claimed, claimed_r
    if layer == 'p':
        m = m & purple & ~claimed
        T[m] = t0 + (t1 - t0) * local[m]
        R[m] = ramp
        claimed |= m
    else:
        m = m & red & ~claimed_r
        T2[m] = t0 + (t1 - t0) * local[m]
        R2[m] = ramp
        claimed_r |= m
    names.append(name)
    labels_dbg[m] = len(names)
    return m


def el_sweep(name, boxes, t0, t1, direction=(1, 0.15), ramp=0.06, layer='p', noise=0.0, along=0.0):
    m = box_mask(boxes) & (purple if layer == 'p' else red) & ~(claimed if layer == 'p' else claimed_r)
    if not m.any():
        print('empty', name); return
    assign(name, m, sweep(m, direction, noise, along), t0, t1, ramp, layer)


def el_geo(name, boxes, t0, t1, seed=None, ramp=0.06, layer='p'):
    m = box_mask(boxes) & (purple if layer == 'p' else red) & ~(claimed if layer == 'p' else claimed_r)
    if not m.any():
        print('empty', name); return
    if seed is None:
        local, _, _ = per_component_geodesic(m, lambda ys, xs: xs + ys)
    else:
        sy, sx = seed[1] * K, seed[0] * K
        local, _, _ = per_component_geodesic(m, lambda ys, xs: (ys - sy) ** 2 + (xs - sx) ** 2)
    assign(name, m, local, t0, t1, ramp, layer)


def el_circle(name, cx, cy, r, t0, t1, ramp=0.05):
    cx, cy, r = cx * K, cy * K, r * K
    dist = np.hypot(xx - cx, yy - cy)
    m = (dist < r * 1.45) & purple & ~claimed
    # angle measured from the top, counter-clockwise like a hand-drawn circle
    ang = (np.arctan2(-(xx - cx), -(yy - cy)) / (2 * np.pi)) % 1.0
    ang = (ang + 0.97) % 1.0     # start just right of the top so the join overlaps
    assign(name, m, ang, t0, t1, ramp)


def el_radial(name, cx, cy, rad, t0, t1, ramp=0.05, layer='p'):
    cx, cy, rad = cx * K, cy * K, rad * K
    d = np.hypot(xx - cx, yy - cy)
    m = (d < rad) & (purple if layer == 'p' else red) & ~(claimed if layer == 'p' else claimed_r)
    assign(name, m, np.clip(d / rad, 0, 1), t0, t1, ramp, layer)


def el_arc(name, cx, cy, r, tol, t0, t1, start_angle, direction=1, ramp=0.05, clip=None):
    cx, cy, r = cx * K, cy * K, r * K
    d = np.hypot(xx - cx, yy - cy)
    m = (np.abs(d - r) < tol * K) & purple & ~claimed
    if clip is not None:
        m &= box_mask(clip)
    a = np.arctan2(yy - cy, xx - cx)
    rel = ((a - start_angle) * direction) % (2 * np.pi)
    lo, hi = rel[m].min(), rel[m].max()
    assign(name, m, (rel - lo) / max(hi - lo, 1e-6), t0, t1, ramp)


def hatch_fill(mask, across):
    """Fill order that lays the hatching stroke by stroke: the pen moves `across`
    the letter, each stroke runs along its own length, strokes land a bit out of order."""
    ax, ay = across
    nrm = np.hypot(ax, ay)
    ax, ay = ax / nrm, ay / nrm
    p = xx * ax + yy * ay            # across the strokes
    q = -xx * ay + yy * ax           # along a stroke
    pn = (p - p[mask].min()) / max(np.ptp(p[mask]), 1)
    qn = (q - q[mask].min()) / max(np.ptp(q[mask]), 1)
    lane = np.floor(p / 3.0).astype(np.int64)          # one lane per ~3 px stroke
    jitter = ndi.gaussian_filter1d(rng.standard_normal(lane.max() - lane.min() + 1), 1.5)
    jitter = jitter / (jitter.std() + 1e-6)
    j = jitter[lane - lane.min()]
    # strokes go back and forth: odd groups of lanes are drawn the other way
    flip = (np.floor(p / 18.0).astype(np.int64) % 2) == 1
    qd = np.where(flip, 1 - qn, qn)
    return np.clip(0.80 * pn + 0.14 * qd + 0.06 * j, 0, 1)


def el_letters(name, boxes, layer, guide_win, letter_start, stagger, dur, hatch_dir, n_letters, angle_deg,
               gap_points=None):
    col = purple if layer == 'p' else red
    cl = claimed if layer == 'p' else claimed_r
    m = box_mask(boxes) & col & ~cl
    # letter bodies are densely hatched; guide lines are thin and sparse
    body = ndi.gaussian_filter(m.astype(np.float32), 3) > 0.5
    lab0, n0 = ndi.label(body)
    areas = ndi.sum(body, lab0, np.arange(1, n0 + 1))
    body = np.isin(lab0, [k + 1 for k in range(n0) if areas[k] > 600])
    # split the word into letters at the gaps of its profile along the baseline
    a = np.deg2rad(angle_deg)
    u = xx * np.cos(a) + yy * np.sin(a)
    u0 = int(u[body].min())
    prof = np.bincount((u[body] - u0).astype(int))
    prof = ndi.gaussian_filter1d(prof.astype(float), 3)
    span = len(prof)
    mins = [i for i in range(2, span - 2) if prof[i] <= prof[i - 1] and prof[i] <= prof[i + 1]]
    mins.sort(key=lambda i: prof[i])
    cuts = []
    for i in mins:
        if all(abs(i - c) > 0.45 * span / n_letters for c in cuts) and 0.04 * span < i < 0.96 * span:
            cuts.append(i)
        if len(cuts) == n_letters - 1:
            break
    cuts = sorted(cuts)
    if gap_points:   # hand-picked gaps between letters (source coords) win
        cuts = sorted(int(px * K * np.cos(a) + py * K * np.sin(a) - u0) for px, py in gap_points)
    print(name, 'cuts', cuts, 'span', span)
    idx = np.searchsorted(np.array(cuts) + u0, u)       # 0..n_letters-1 per pixel
    lab = np.where(body, idx + 1, 0)
    order = list(range(1, n_letters + 1))
    letters = np.zeros((H, W), np.int16)
    near = ndi.binary_dilation(body, iterations=3)
    letters[near & m] = (idx + 1)[near & m]
    guides = m & (letters == 0)
    # guides first: thin construction lines, traced from their left end
    g_local, _, _ = per_component_geodesic(guides, lambda ys, xs: xs + 0.2 * ys)
    assign(name + '_guias', guides, g_local, guide_win[0], guide_win[1], 0.05, layer)
    for i in range(len(order)):
        lm = letters == (i + 1)
        b = lab == order[i]
        edge = lm & ~ndi.binary_erosion(b, structure=disk(4))
        inner = lm & ~edge
        loc = np.zeros((H, W), np.float32)
        e_local, _, _ = per_component_geodesic(edge, lambda ys, xs: xs + ys)
        loc[edge] = 0.55 * e_local[edge]
        if inner.any():
            loc[inner] = 0.3 + 0.7 * hatch_fill(inner, hatch_dir)[inner]
        t0 = letter_start + i * stagger
        assign(f'{name}_{i + 1}', lm, loc, t0, t0 + dur, 0.07, layer)
    return len(order)


# ---- timeline (seconds). Source-image coordinates (941 x 1672).
# 1. the sheet's frame and its stars
el_radial('estrella_sup', 484, 40, 26, 0.22, 0.40)
el_radial('estrella_inf', 480, 1622, 26, 0.70, 0.90)
el_geo('marco', [(18, 26, 930, 56), (33, 18, 62, 1662), (886, 18, 916, 1662), (22, 1606, 932, 1640)],
       0.0, 0.90, seed=(47, 40), ramp=0.05)
# 2. big construction arcs (circles fitted on the ink: centre, radius)
el_arc('arco_izq', -14, 448, 190, 6, 0.10, 0.80, start_angle=-np.pi / 2 - 0.1, direction=1,
       clip=[(0, 240, 205, 662)])
el_arc('arco_der', 980, 1546, 220, 6, 0.30, 1.00, start_angle=-1.6, direction=-1,
       clip=[(735, 1290, 941, 1672)])
# 3. the floor plan
el_geo('escenario', [(118, 238, 852, 274), (126, 238, 160, 455), (118, 416, 632, 448),
                     (552, 238, 582, 312), (810, 238, 845, 610)], 0.85, 1.65, seed=(140, 258))
el_radial('estrella_med', 478, 190, 30, 1.00, 1.20)
el_geo('cabina', [(296, 412, 327, 558), (503, 412, 532, 558), (296, 528, 532, 558)], 1.45, 1.95, seed=(312, 432))
el_geo('columna', [(592, 402, 622, 612), (596, 998, 624, 1238), (826, 875, 858, 1248), (596, 1206, 872, 1242)],
       1.55, 2.35, seed=(607, 415))
el_geo('vip_caja', [(170, 1246, 748, 1278), (178, 1240, 212, 1495), (698, 1236, 732, 1495), (170, 1452, 748, 1488)],
       2.15, 2.85, seed=(180, 1262))
# 4. tables, numbers, little texts
for i, (cx, cy, nb, t) in enumerate([(336, 362, (322, 286, 352, 324), 1.55), (518, 362, (503, 286, 534, 324), 1.75),
                                       (714, 522, (701, 438, 730, 480), 1.95), (732, 1152, (720, 1073, 748, 1112), 2.15)]):
    el_circle(f'mesa_{i + 1}', cx, cy, 36, t, t + 0.42)
    el_sweep(f'numero_{i + 1}', [nb], t + 0.40, t + 0.62, direction=(0.25, 1))
el_sweep('cnprod', [(380, 58, 560, 136)], 1.10, 1.75, direction=(1, 0.12), ramp=0.07)
el_geo('exit_caja', [(688, 136, 858, 224)], 1.35, 1.85, seed=(695, 143))
el_sweep('booth_dj', [(370, 446, 460, 517)], 2.15, 2.55, direction=(0.6, 1))
el_sweep('sector_general', [(256, 1172, 530, 1226)], 2.45, 3.00, direction=(1, 0.1))
el_sweep('sector_general_linea', [(222, 1224, 568, 1248)], 2.95, 3.20, direction=(1, 0))
el_sweep('sector_vip', [(376, 1322, 562, 1381)], 2.70, 3.10, direction=(1, 0.1))
el_sweep('sector_vip_linea', [(362, 1379, 578, 1407)], 3.05, 3.25, direction=(1, -0.1))
# 5. MESAS: guide lines, then each letter outlined and hatched
el_radial('estrella_mesas', 258, 622, 30, 2.55, 2.75)
n_mesas = el_letters('mesas', [(40, 548, 870, 930)], 'p', (2.50, 3.10), 2.85, 0.27, 0.80, hatch_dir=(1, 0.55),
                     n_letters=5, angle_deg=-8.1)
# 6. SOLD OUT in red
el_radial('estrella_roja', 548, 1100, 32, 4.55, 4.75, layer='r')
n_sold = el_letters('soldout', [(10, 745, 935, 1205)], 'r', (4.40, 4.95), 4.75, 0.15, 0.60, hatch_dir=(1, 0.5),
                    n_letters=7, angle_deg=-12.9,
                    gap_points=[(188, 1030), (288, 1000), (378, 988), (535, 950), (662, 920), (783, 890)])
# 7. sponsors
el_sweep('logo_ii', [(204, 1518, 284, 1598)], 6.00, 6.40, direction=(1, 0.2))
el_sweep('logo_mesf', [(320, 1516, 458, 1594)], 6.15, 6.60, direction=(1, 0.25))
el_sweep('logo_nydity', [(484, 1512, 624, 1602)], 6.30, 6.75, direction=(1, 0.1))
el_sweep('logo_analoca', [(644, 1502, 742, 1602)], 6.45, 6.90, direction=(0.2, 1))
# 8. hatching in the corners
el_sweep('trama_sup_izq', [(0, 0, 268, 440)], 0.25, 1.40, direction=(1.5, 1), noise=0.05, along=0.12, ramp=0.09)
el_sweep('trama_izq', [(0, 440, 120, 1200)], 0.60, 1.50, direction=(1.2, 1), noise=0.05, ramp=0.09)
el_sweep('trama_inf_izq', [(0, 1180, 175, 1672)], 0.70, 1.50, direction=(1.2, 1), noise=0.05, ramp=0.09)
el_sweep('trama_der', [(838, 540, 941, 1260)], 0.90, 1.70, direction=(1, 1.2), noise=0.05, ramp=0.09)
el_sweep('trama_inf_der', [(735, 1250, 941, 1672)], 0.45, 1.40, direction=(1, 1.2), noise=0.05, ramp=0.09)

# ---- everything left over: thin curves, splatter, stray marks
def residual(layer):
    col = purple if layer == 'p' else red
    cl = claimed if layer == 'p' else claimed_r
    TT = T if layer == 'p' else T2
    rest = col & ~cl
    lab, n = ndi.label(rest, structure=np.ones((3, 3)))
    if n == 0:
        return
    areas = ndi.sum(rest, lab, np.arange(1, n + 1))
    big = np.isin(lab, [k + 1 for k in range(n) if areas[k] >= 90])
    small = rest & ~big
    # small marks pop right after the nearest drawn ink
    if small.any():
        _, (iy, ix) = ndi.distance_transform_edt(~cl, return_indices=True)
        base = TT[iy, ix]
        base = np.where(np.isfinite(base), base, 3.0)
        lab_s, ns = ndi.label(small, structure=np.ones((3, 3)))
        jit = np.concatenate([[0], rng.uniform(0.08, 0.30, ns)])[lab_s]
        local = np.zeros((H, W), np.float32)
        assign(f'salpicado_{layer}', small, local, 0, 0, 0.04, layer)
        TT[small] = (base + jit)[small]
    if big.any():
        g, lb, nb = per_component_geodesic(big, lambda ys, xs: xs + 0.3 * ys)
        cy = np.array(ndi.center_of_mass(big, lb, np.arange(1, nb + 1)))[:, 0]
        lens = np.array(ndi.maximum(np.where(big, g, 0), lb, np.arange(1, nb + 1)))
        sizes = np.array(ndi.sum(big, lb, np.arange(1, nb + 1)))
        if layer == 'p':
            start = 0.25 + 2.2 * (cy / H)
        else:
            start = 4.45 + 0.4 * rng.uniform(size=nb)
        dur = np.clip(np.sqrt(sizes) / 90, 0.15, 0.7)
        t0 = np.concatenate([[0], start])[lb]
        du = np.concatenate([[0], dur])[lb]
        assign(f'resto_{layer}', big, np.zeros((H, W), np.float32), 0, 0, 0.05, layer)
        TT[big] = (t0 + du * g)[big]


residual('p')
residual('r')

# ---- watercolor washes bloom outward from their middle, last
wash_order = {'wash_booth': (6.30, 7.35, (400, 470)), 'wash_vip': (6.50, 7.55, (450, 1365)),
              'wash_stain': (6.90, 7.20, (797, 1206))}
for wname, (t0, t1, (cx, cy)) in wash_order.items():
    wm = box_mask(WASH_REGIONS[wname]) & M & ~ink
    d = np.hypot(xx - cx * K, yy - cy * K)
    d = d / max(d[wm].max(), 1) + smooth_noise(14, 0.10)
    d = np.clip(d, 0, 1)
    T[wm] = t0 + (t1 - t0) * d[wm]
    R[wm] = 0.45
    names.append(wname)
    labels_dbg[wm] = len(names)

# ---- halo pixels (in M but not ink/wash): take the time of the nearest ink pixel
known = np.isfinite(T)
_, (iy, ix) = ndi.distance_transform_edt(~known, return_indices=True)
halo = M & ~known
T[halo] = T[iy, ix][halo]
R[halo] = R[iy, ix][halo]

# ---- the purple layer under the red ink
red_zone = np.isfinite(T2)
red_dil = ndi.binary_dilation(red_zone, iterations=2)
_, (ry, rx) = ndi.distance_transform_edt(~red_zone, return_indices=True)
T2[red_dil & ~red_zone] = T2[ry, rx][red_dil & ~red_zone]
R2[red_dil & ~red_zone] = R2[ry, rx][red_dil & ~red_zone]
red_zone = red_dil
under = purple & ~red_zone
fillP, _ = norm_fill(orig, under, 3)
cov_num = ndi.gaussian_filter(under.astype(np.float32), 3)
cov_den = ndi.gaussian_filter((~red_zone).astype(np.float32), 3)
cov = cov_num / np.maximum(cov_den, 1e-3)
w = np.clip((cov - 0.35) / 0.3, 0, 1)[..., None]
violet = orig.copy()
violet[red_zone] = (blank + (fillP - blank) * w)[red_zone]
# under the red, the purple appears with the nearest purple stroke
_, (py, px) = ndi.distance_transform_edt(~(purple & np.isfinite(T) & ~red_zone), return_indices=True)
cover = red_zone & (w[..., 0] > 0.01)
T[cover] = T[py, px][cover]
R[cover] = 0.06
T[red_zone & ~cover] = T2[red_zone & ~cover]
R[red_zone & ~cover] = R2[red_zone & ~cover]

# ---- sanity + encode
dyn = M | red_zone
T[~dyn] = 0
T[~np.isfinite(T)] = 0.0
T2[~red_zone] = 0
T2[~np.isfinite(T2)] = 0.0
print('dynamic px', int(dyn.sum()), 'red px', int(red_zone.sum()), 'T max', float(T.max()), float(T2.max()))


def encode(t, r, mask):
    code = np.round(np.clip(t, 0, T_MAX) / T_MAX * 65535).astype(np.uint32)
    out = np.zeros((H, W, 3), np.uint8)
    out[..., 0] = code >> 8
    out[..., 1] = code & 255
    out[..., 2] = np.clip(np.round(r / RAMP_UNIT), 1, 255).astype(np.uint8)
    out[~mask] = 0
    return out


def save(a, name):
    # photo layers as full-chroma JPEG so each stays under the 2 MB inline limit
    Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8)).save(
        f'{OUT}/{name}', quality=95, subsampling=0, optimize=True)


save(orig, 'placa.jpg')
save(blank, 'papel.jpg')
save(violet, 'violeta.jpg')
Image.fromarray(encode(T, R, dyn)).save(f'{OUT}/tiempo.png', optimize=True)
Image.fromarray(encode(T2, R2, red_zone)).save(f'{OUT}/tiempo-rojo.png', optimize=True)
# flag: R channel 255 where the pixel is dynamic, G 255 where red layer applies
flag = np.zeros((H, W, 3), np.uint8)
flag[..., 0] = dyn * 255
flag[..., 1] = red_zone * 255
Image.fromarray(flag).save(f'{OUT}/mascara.png', optimize=True)

if DBG:
    np.savez_compressed(f'{DBG}/fields.npz', T=T, R=R, T2=T2, dyn=dyn, red_zone=red_zone,
                        labels=labels_dbg, ink=ink, wash=wash, M=M)
    json.dump(names, open(f'{DBG}/names.json', 'w'))
    pal = rng.integers(40, 255, (len(names) + 1, 3)).astype(np.uint8)
    pal[0] = 255
    vis = pal[labels_dbg]
    vis[(labels_dbg == 0) & purple] = (0, 0, 0)
    vis[(labels_dbg == 0) & red & ~claimed_r] = (255, 0, 255)
    Image.fromarray(vis).save(f'{DBG}/labels.png')
    tv = np.where(dyn, 255 - np.clip(np.maximum(T, T2) / 8 * 255, 0, 255), 255).astype(np.uint8)
    Image.fromarray(tv).save(f'{DBG}/time.png')
