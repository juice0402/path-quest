"""Cut sprites out of a Canva grid image (white background).

usage: python3 slice_art.py SRC.png OUTDIR ROWS COLS name1,name2,...  [--lo 226] [--tol 18] [--holes]
--lo/--tol: how white the background must be (raise lo for white subjects like a snowman)
--holes: also clear pure-white holes inside a figure (a key's bows)

- the white background is removed only where it touches the image border, so white
  inside a figure (belts, eyes) stays
- each grid cell becomes one sprite: every piece whose centre falls in the cell,
  cropped tight with a small margin, saved as RGBA PNG
- a name of "-" skips that cell
"""
import sys, os
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

def bg_mask(a, tol=18, lo=226):
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    mn = np.minimum(np.minimum(r, g), b); mx = np.maximum(np.maximum(r, g), b)
    whiteish = (mn >= lo) & (mx - mn <= tol)
    lab, n = ndimage.label(whiteish)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    return np.isin(lab, list(edge)), mn

def main():
    args = sys.argv[1:]
    opt = lambda k, d: type(d)(args[args.index(k) + 1]) if k in args else d
    lo, tol, holes = opt('--lo', 226), opt('--tol', 18), '--holes' in args
    src, out, rows, cols, names = args[0], args[1], int(args[2]), int(args[3]), args[4].split(',')
    os.makedirs(out, exist_ok=True)
    im = Image.open(src).convert('RGB'); a = np.asarray(im)
    H, W = a.shape[:2]
    bg, mn = bg_mask(a, tol, lo)
    if holes:
        r, g, b = (a[..., i].astype(int) for i in range(3))
        bg |= (np.minimum(np.minimum(r, g), b) >= 244) & (np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b) <= 8)
    fg = ~bg
    fg = ndimage.binary_opening(fg, iterations=1)
    lab, n = ndimage.label(fg)
    sizes = ndimage.sum(fg, lab, range(1, n + 1))
    coms = ndimage.center_of_mass(fg, lab, range(1, n + 1))
    # soft edge: light pixels at the rim fade out
    rim = fg & ndimage.binary_dilation(bg, iterations=2)
    alpha = np.where(fg, 255, 0).astype(np.float32)
    soft = np.clip((250 - mn) / 34.0, 0, 1) * 255
    alpha[rim] = np.minimum(alpha[rim], soft[rim])
    alpha = np.asarray(Image.fromarray(alpha.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)))
    alpha = np.where(fg | rim, alpha, 0).astype(np.uint8)
    rgba = np.dstack([a, alpha])
    ch, cw = H / rows, W / cols
    for k, name in enumerate(names):
        if name == '-' or not name: continue
        r, c = divmod(k, cols)
        keep = [i + 1 for i, (cy, cx) in enumerate(coms) if sizes[i] > (ch * cw) * 0.002 and int(cy // ch) == r and int(cx // cw) == c]
        if not keep:
            print('EMPTY', name); continue
        m = np.isin(lab, keep)
        m = ndimage.binary_dilation(m, iterations=3) & (alpha > 0)
        ys, xs = np.nonzero(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        piece = rgba[y0:y1, x0:x1].copy()
        piece[..., 3] = np.where(m[y0:y1, x0:x1], piece[..., 3], 0)
        pad = 4
        canvas = np.zeros((y1 - y0 + 2 * pad, x1 - x0 + 2 * pad, 4), np.uint8)
        canvas[pad:-pad, pad:-pad] = piece
        Image.fromarray(canvas).save(os.path.join(out, name + '.png'))
        print(name, canvas.shape[1], 'x', canvas.shape[0])

if __name__ == '__main__':
    main()
