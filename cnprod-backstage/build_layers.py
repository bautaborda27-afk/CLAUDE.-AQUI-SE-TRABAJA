"""Split the flat BACKSTAGE / SOLD OUT flyer into animatable layers.

Outputs (1080x1920) into fx/assets/:
  paper.png     paper only, ink removed (faint pencil may remain)
  plan.png      paper + blueprint linework, without BACKSTAGE and SOLD OUT
  backstage.png BACKSTAGE letters only (RGBA)
  soldout.png   red SOLD OUT ink incl. scribbles and splatter (RGBA)
  soldout-cyan.png / soldout-violet.png  tinted copies for the RGB split
  exit.png      the EXIT sign ink only (RGBA), for the neon flicker
  grain.png     grayscale noise tile for the animated film grain

Layers are unmixed against the inpainted base, so plan + backstage + soldout
recomposes to the original flyer.
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source", "flyer-original.png")
OUT = os.path.join(HERE, "fx", "assets")
DEBUG = os.path.join(HERE, "source", "debug")
W, H = 1080, 1920


def save_rgba(path, rgb, alpha):
    a = (np.clip(alpha, 0, 1) * 255).astype(np.uint8)
    img = np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), a])
    Image.fromarray(img, "RGBA").save(path, optimize=True)


def unmix(px, base, alpha, fallback):
    """Colour C such that alpha*C + (1-alpha)*base == px."""
    a = alpha[..., None]
    with np.errstate(divide="ignore", invalid="ignore"):
        c = (px - (1 - a) * base) / np.maximum(a, 1e-3)
    c = np.clip(c, 0, 255)
    weak = alpha < 0.12
    c[weak] = fallback
    return c


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(DEBUG, exist_ok=True)

    pil = Image.open(SRC).convert("RGB").resize((W, H), Image.LANCZOS)
    pil = pil.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
    img = np.asarray(pil).astype(np.float32)
    R, G, B = img[..., 0], img[..., 1], img[..., 2]
    luma = 0.299 * R + 0.587 * G + 0.114 * B

    # Local paper estimate: ink is dark, so a max filter wipes it out.
    lu8 = luma.astype(np.uint8)
    paper_l = cv2.dilate(lu8, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (51, 51)))
    paper_l = cv2.GaussianBlur(paper_l, (0, 0), 15).astype(np.float32)
    dark = np.clip(paper_l - luma, 0, 255)

    # --- red ink -----------------------------------------------------------
    redness = R - (G + B) / 2
    # Paper itself is pinkish (redness ~25), so red ink starts above ~34.
    red_a = np.clip((redness - 34) / 110.0, 0, 1) * (R > 110)
    red_a = cv2.GaussianBlur(red_a.astype(np.float32), (0, 0), 0.6)
    red_mask = (red_a > 0.04).astype(np.uint8)
    red_mask = cv2.dilate(red_mask, np.ones((3, 3), np.uint8))
    # Only the SOLD OUT mass and its splatter, not stray red specks elsewhere.
    reach = cv2.dilate(red_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (71, 71)))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(reach, 8)
    main_id = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    red_mask &= (lab == main_id).astype(np.uint8)
    red_a = red_a * red_mask

    # --- purple ink ----------------------------------------------------------
    # The title sits on grey watercolour clouds (dark ~30-50), so only really
    # dark ink (dark > 70) counts as a letter stroke.
    strong = ((dark > 70) & (red_a < 0.1)).astype(np.uint8)

    # BACKSTAGE letters: the thick strokes in the title band.
    thick = cv2.morphologyEx(
        strong, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    )
    band = np.zeros_like(thick)
    band[690:1130, 60:1040] = 1
    thick &= band
    near_red = cv2.dilate(red_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(thick, 8)
    letters = np.zeros_like(thick)
    for i in range(1, n):
        comp = lab == i
        area = stats[i, cv2.CC_STAT_AREA]
        if area > 350 and near_red[comp].mean() < 0.3:
            letters[comp] = 1
    letters_core = letters.copy()
    # Generous on purpose: whatever the mask takes is unmixed into the letter
    # layer, so the recomposite stays exact and no dark halo is left behind.
    grow = cv2.dilate(letters, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    letters = (grow & ((dark > 26) | (letters_core > 0)).astype(np.uint8))
    letters = cv2.dilate(letters, np.ones((5, 5), np.uint8))

    # --- bases ---------------------------------------------------------------
    def normconv(src, mask, sigma):
        m = mask.astype(np.float32)
        num = cv2.GaussianBlur(src * m[..., None], (0, 0), sigma)
        den = cv2.GaussianBlur(m, (0, 0), sigma)[..., None]
        return num / np.maximum(den, 1e-4)

    # What sits behind the titles: paper + watercolour, without linework.
    behind = (dark < 55) & (red_mask == 0) & (letters == 0) & (redness < 30)
    bg_fill = normconv(img, behind, 9)
    # Wider passes for the centres of big holes.
    for sig in (28, 80):
        cover = cv2.GaussianBlur(behind.astype(np.float32), (0, 0), sig / 3)[..., None]
        bg_fill = np.where(cover > 0.05, bg_fill, normconv(img, behind, sig))
    # Strip the pink cast the red haze leaves on the fill.
    paper_ref = np.median(img[(dark < 12) & (redness < 30)], axis=0)
    fl = bg_fill.mean(axis=2, keepdims=True)
    neutral = paper_ref * (fl / paper_ref.mean())
    bg_fill = 0.45 * bg_fill + 0.55 * neutral

    rng = np.random.default_rng(3)
    tex = rng.normal(0, 3.2, (H, W, 1)).astype(np.float32)
    bg_fill = np.clip(bg_fill + tex, 0, 255)

    hole = ((red_mask > 0) | (letters > 0)).astype(np.float32)
    hole = np.clip(cv2.GaussianBlur(hole, (0, 0), 1.2) * 1.5, 0, 1)[..., None]
    plan_rgb = img * (1 - hole) + bg_fill * hole

    # Blank paper for the scan-in: smooth, no ghost of the linework.
    blank = (dark < 22) & (red_mask == 0) & (redness < 30)
    tmp = img.copy()
    tmp[~blank] = paper_ref
    paper_fill = cv2.GaussianBlur(tmp, (0, 0), 60)
    paper_rgb = np.clip(paper_fill + tex * 1.4, 0, 255).astype(np.uint8)

    # --- RGBA layers, unmixed against the plan base ------------------------
    # SOLD OUT: alpha from how far the pixel moved toward red ink.
    red_ink = np.array([214, 26, 28], np.float32)
    base_g = plan_rgb[..., 1]
    red_alpha = np.clip((base_g - G) / np.maximum(base_g - red_ink[1], 1), 0, 1)
    red_alpha *= (red_mask > 0)
    red_alpha = np.maximum(red_alpha, red_a) * (red_mask > 0)
    red_rgb = unmix(img, plan_rgb, red_alpha, red_ink)

    # BACKSTAGE: alpha from darkness against the base.
    purple_ink = np.array([44, 28, 92], np.float32)
    base_l = 0.299 * plan_rgb[..., 0] + 0.587 * plan_rgb[..., 1] + 0.114 * plan_rgb[..., 2]
    ink_l = 0.299 * 44 + 0.587 * 28 + 0.114 * 92
    let_alpha = np.clip((base_l - luma) / np.maximum(base_l - ink_l, 1) * 1.08, 0, 1)
    let_alpha *= (letters > 0)
    let_rgb = unmix(img, plan_rgb, let_alpha, purple_ink)

    # EXIT sign ink (box + word + arrow).
    ex = np.zeros((H, W), np.float32)
    y0, y1, x0, x1 = 150, 262, 780, 1000
    ex_dark = np.clip((paper_l - luma) / 150.0, 0, 1)
    ex[y0:y1, x0:x1] = ex_dark[y0:y1, x0:x1]
    ex[ex < 0.12] = 0

    Image.fromarray(paper_rgb).save(os.path.join(OUT, "paper.png"), optimize=True)
    Image.fromarray(plan_rgb.astype(np.uint8)).save(os.path.join(OUT, "plan.png"), optimize=True)
    save_rgba(os.path.join(OUT, "soldout.png"), red_rgb, red_alpha)
    save_rgba(os.path.join(OUT, "backstage.png"), let_rgb, let_alpha)
    save_rgba(os.path.join(OUT, "soldout-cyan.png"), np.full((H, W, 3), (0, 205, 235), np.float32), red_alpha)
    save_rgba(os.path.join(OUT, "soldout-violet.png"), np.full((H, W, 3), (88, 40, 255), np.float32), red_alpha)
    save_rgba(os.path.join(OUT, "exit.png"), np.full((H, W, 3), 255, np.float32), ex)

    # Film grain tile (seeded).
    rng = np.random.default_rng(7)
    g = rng.normal(128, 38, (720, 720)).astype(np.float32)
    g = cv2.GaussianBlur(g, (0, 0), 0.7)
    Image.fromarray(np.clip(g, 0, 255).astype(np.uint8), "L").save(
        os.path.join(OUT, "grain.png"), optimize=True
    )

    # Debug: recomposite and diff against the source.
    a1 = let_alpha[..., None]
    a2 = red_alpha[..., None]
    comp = plan_rgb * (1 - a1) + let_rgb * a1
    comp = comp * (1 - a2) + red_rgb * a2
    diff = np.abs(comp - img).mean()
    Image.fromarray(comp.astype(np.uint8)).save(os.path.join(DEBUG, "recomposite.png"))
    Image.fromarray((letters * 255).astype(np.uint8)).save(os.path.join(DEBUG, "letters_mask.png"))
    Image.fromarray((red_mask * 255).astype(np.uint8)).save(os.path.join(DEBUG, "red_mask.png"))
    print(f"mean abs diff recomposite vs source: {diff:.2f}")


if __name__ == "__main__":
    sys.exit(main())
