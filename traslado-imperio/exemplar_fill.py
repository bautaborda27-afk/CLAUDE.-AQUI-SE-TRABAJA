"""Exemplar-based inpainting (Criminisi et al. 2004), patch search with OpenCV.

Fills the unknown pixels with real patches from nearby known ones, most
confident and most structured fronts first, so lines run on into the hole.
"""
import cv2
import numpy as np


def fill(img, unknown, src_ok, patch=11, search=(260, 110), guide=None, log_every=0):
    """img: HxWx3 float32; unknown: HxW bool (to fill); src_ok: HxW bool (may be copied).

    guide: optional HxW float map known everywhere (e.g. depth below a line);
    it joins the match so patches come from places with a similar guide value.
    """
    img = img.copy()
    g4 = guide.astype(np.float32) if guide is not None else None
    h = patch // 2
    H, W = unknown.shape
    unk = unknown.copy()
    conf = (~unk).astype(np.float32)
    # a source patch must be entirely copyable
    valid = cv2.erode((src_ok & ~unk).astype(np.uint8), np.ones((patch, patch), np.uint8)) > 0
    gray = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
    it = 0
    while unk.any():
        it += 1
        um = unk.astype(np.uint8)
        front = um.astype(bool) & (cv2.dilate((~unk).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
        ys, xs = np.nonzero(front)
        # confidence term: mean confidence of the patch
        c_sum = cv2.boxFilter(conf, -1, (patch, patch), normalize=True, borderType=cv2.BORDER_CONSTANT)
        C = c_sum[ys, xs]
        # data term: isophote strength across the front normal
        g = gray.copy()
        g[unk] = 0
        gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
        kn = (~unk).astype(np.float32)
        kn = cv2.erode(kn, np.ones((3, 3), np.uint8))  # ignore gradients touching the hole
        gx *= kn
        gy *= kn
        gxm = cv2.dilate(np.abs(gx), np.ones((5, 5), np.uint8))
        gym = cv2.dilate(np.abs(gy), np.ones((5, 5), np.uint8))
        mf = cv2.GaussianBlur(unk.astype(np.float32), (5, 5), 0)
        nx = cv2.Sobel(mf, cv2.CV_32F, 1, 0, ksize=3)
        ny = cv2.Sobel(mf, cv2.CV_32F, 0, 1, ksize=3)
        nn = np.sqrt(nx ** 2 + ny ** 2) + 1e-6
        Dt = np.abs(-gym[ys, xs] * nx[ys, xs] + gxm[ys, xs] * ny[ys, xs]) / nn[ys, xs] / 255.0
        P = C * (Dt + 0.001)
        k = int(np.argmax(P))
        py, px = ys[k], xs[k]
        y0, y1 = max(py - h, 0), min(py + h + 1, H)
        x0, x1 = max(px - h, 0), min(px + h + 1, W)
        tmask = (~unk[y0:y1, x0:x1]).astype(np.float32)
        if g4 is not None:
            work = np.dstack([img, g4])
        else:
            work = img
        tpl = work[y0:y1, x0:x1]
        th, tw = tpl.shape[:2]
        # search window
        sy0, sy1 = max(py - search[1], 0), min(py + search[1] + 1, H)
        sx0, sx1 = max(px - search[0], 0), min(px + search[0] + 1, W)
        region = work[sy0:sy1, sx0:sx1]
        if region.shape[0] < th or region.shape[1] < tw:
            break
        m3 = np.repeat(tmask[..., None], 3, axis=2)
        if g4 is not None:
            m3 = np.dstack([m3, np.ones_like(tmask)])
        res = cv2.matchTemplate(region, tpl, cv2.TM_SQDIFF, mask=m3)
        # candidate top-left -> centre validity (centre at +offset)
        oy, ox = py - y0, px - x0
        vwin = valid[sy0 + oy: sy0 + oy + res.shape[0], sx0 + ox: sx0 + ox + res.shape[1]]
        if vwin.shape != res.shape:
            vfull = np.zeros(res.shape, bool)
            vfull[:vwin.shape[0], :vwin.shape[1]] = vwin
            vwin = vfull
        # the patch fully inside the window and copyable
        res = np.where(vwin & np.isfinite(res), res, np.inf)
        if not np.isfinite(res).any():
            # widen the search to the whole image once
            region = work
            res = cv2.matchTemplate(region, tpl, cv2.TM_SQDIFF, mask=m3)
            sy0 = sx0 = 0
            vwin = valid[oy: oy + res.shape[0], ox: ox + res.shape[1]]
            vfull = np.zeros(res.shape, bool)
            vfull[:vwin.shape[0], :vwin.shape[1]] = vwin
            res = np.where(vfull, res, np.inf)
            if not np.isfinite(res).any():
                raise RuntimeError("no source patch available")
        by, bx = np.unravel_index(int(np.argmin(res)), res.shape)
        src = img[sy0 + by: sy0 + by + th, sx0 + bx: sx0 + bx + tw]
        fillm = unk[y0:y1, x0:x1]
        img[y0:y1, x0:x1][fillm] = src[fillm]
        gray[y0:y1, x0:x1][fillm] = cv2.cvtColor(src.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)[fillm]
        conf[y0:y1, x0:x1][fillm] = C[k]
        unk[y0:y1, x0:x1][fillm] = False
        if log_every and it % log_every == 0:
            print(it, int(unk.sum()), flush=True)
    return img
