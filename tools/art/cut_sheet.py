# 11/4 Canva の白い背景のならび絵から、1体ずつ透明に切り出す（何度走らせても同じ）
# usage: python3 tools/art/cut_sheet.py sheet.png outdir name1,name2,...  （名前は上の段の左から、つぎの段の左から）
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, out, names = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
keepw = set(sys.argv[4].split(',')) if len(sys.argv) > 4 else set()   # white figures (a ghost): keep their pale insides
os.makedirs(out, exist_ok=True)
A = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
mx, mn = A.max(2), A.min(2)
bgish = (mn > 222) & ((mx - mn) < 22)                      # white and near-white
lab, n = ndi.label(bgish)
edge = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
bg = np.isin(lab, list(edge))
# white shut inside a figure (between legs, inside a bow): big pale patches not touching the edge go too
# only flat paper-white patches: a shine on a helmet or a ghost is near white too, but shaded
bgv = float(np.median(mn[:20, :20]))
flat = (mn >= bgv - 3) & ((mx - mn) <= 4)
inner = bgish & ~bg
lab3, n3 = ndi.label(inner)
if n3:
    sz3 = ndi.sum(inner, lab3, range(1, n3 + 1)); fl3 = ndi.sum(flat & inner, lab3, range(1, n3 + 1))
    bg |= np.isin(lab3, [i + 1 for i in range(n3) if sz3[i] > 400 and fl3[i] / sz3[i] > 0.5])
fg = ~bg
lab2, n2 = ndi.label(ndi.binary_dilation(fg, iterations=14))   # parts a few pixels apart stay with their figure
sz = ndi.sum(fg, lab2, range(1, n2 + 1))
objs = ndi.find_objects(lab2)
keep = [k for k in np.argsort(-sz)[:len(names)]]
H = A.shape[0]
rows = sorted(keep, key=lambda k: (objs[k][0].start + objs[k][0].stop) / 2)
# group into rows by their middle height, then left to right
groups, cur = [], []
for k in rows:
    m = (objs[k][0].start + objs[k][0].stop) / 2
    if cur and m - (objs[cur[0]][0].start + objs[cur[0]][0].stop) / 2 > H * 0.25: groups.append(cur); cur = []
    cur.append(k)
groups.append(cur)
order = [k for g in groups for k in sorted(g, key=lambda k: objs[k][1].start)]
for name, k in zip(names, order):
    sl = objs[k]; y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
    m = (lab2[y0:y1, x0:x1] == k + 1) & fg[y0:y1, x0:x1]
    if name in keepw: m = ndi.binary_fill_holes(m)
    rgb = A[y0:y1, x0:x1].copy()
    rim = m & ndi.binary_dilation(~m, iterations=2)
    a = np.where(m, 1.0, 0.0)
    a = np.where(rim, np.clip((255 - rgb.min(2)) / 40, 0, 1), a)
    al = np.maximum(a, 1e-3)[..., None]
    rgb = np.where(rim[..., None], np.clip((rgb - 255 * (1 - al)) / al, 0, 255), rgb)
    im = Image.fromarray(np.dstack([rgb, a * 255]).astype(np.uint8), 'RGBA')
    im = im.crop(im.getbbox()); im.save(os.path.join(out, name + '.png')); print(name, im.size)
