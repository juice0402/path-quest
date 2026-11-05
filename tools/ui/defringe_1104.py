# 11/4 敵の透過のやり直し：切り抜きのときに残った白っぽいふち・紫のもや・すきまの背景を消す（何度走らせても同じになる）
# usage: python3 tools/ui/defringe_1104.py [games/path-quest/index.html]
import sys, re, io, base64
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
FOES = ['soldier', 'bugle', 'cannon', 'robot', 'boss', 'king', 'archer', 'mage', 'clown', 'mason']
K = np.ones((3, 3), bool)

def clean(im):
    A = np.asarray(im.convert('RGBA')).astype(np.float32); rgb = A[..., :3]; a = A[..., 3].copy()
    mx, mn = rgb.max(2), rgb.min(2); lum = rgb.mean(2); r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    rim = (lum > 150) & ((mx - mn) < 55) & (b >= g - 4)            # the pale pink-lavender rim of the old cut
    glow = (b > g + 12) & (r > g - 6) & (lum > 120) & (sat < 0.42)  # the light purple glow painted behind
    gone = a < 12
    def grow(gone, n):
        for _ in range(n):
            e = ndi.binary_dilation(gone, K) & ~gone; rm = e & (rim | glow)
            if not rm.any(): break
            gone = gone | rm
        return gone
    gone = grow(gone, 12)
    # background shut in between an arm and a spear, inside a bow, between the legs: pale patches of the same colour
    pale = (lum > 150) & ((mx - mn) < 60) & (b >= g - 4) & ~gone
    lab, n = ndi.label(pale)
    if n:
        sz = ndi.sum(pale, lab, range(1, n + 1))
        gone = gone | np.isin(lab, [i + 1 for i, s in enumerate(sz) if s >= 50])
        gone = grow(gone, 8)
    a[gone] = 0
    # one pixel of soft edge, coloured from the solid pixels next to it (no light fringe)
    solid = a > 0; edge = solid & ndi.binary_dilation(~solid, K); inner = solid & ~edge
    w = ndi.uniform_filter(inner.astype(np.float32), 3)
    for c in range(3):
        s = ndi.uniform_filter(rgb[..., c] * inner, 3)
        rgb[..., c] = np.where(edge & (w > 0), s / np.maximum(w, 1e-6), rgb[..., c])
    a[edge] *= 0.55
    return Image.fromarray(np.dstack([rgb, a]).clip(0, 255).astype(np.uint8), 'RGBA')

def shadow(im):  # the same soft shadow build_assets.py made, from the new outline
    w, h = im.size
    al = im.getchannel('A').resize((max(8, w // 2), max(8, h // 2)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.6))
    A = (np.asarray(al).astype(np.float32) * 0.4).astype(np.uint8)
    return Image.fromarray(np.dstack([np.full_like(A, 56), np.full_like(A, 30), np.full_like(A, 46), A]), 'RGBA')

def enc(im, q=84, aq=90):
    b = io.BytesIO(); im.save(b, 'WEBP', quality=q, alpha_quality=aq, method=6); return base64.b64encode(b.getvalue()).decode()

s = open(P, encoding='utf-8').read()
for n in FOES:
    m = re.search(r'(<symbol id="a-' + n + r'" viewBox="[^"]+" preserveAspectRatio="[^"]+"><image href="data:image/webp;base64,)([^"]+)(")', s)
    assert m, n
    im = clean(Image.open(io.BytesIO(base64.b64decode(m.group(2)))))
    s = s[:m.start(2)] + enc(im) + s[m.end(2):]
    ms = re.search(r'(<symbol id="a-' + n + r'-sh" viewBox="[^"]+" preserveAspectRatio="[^"]+"><image href="data:image/webp;base64,)([^"]+)(")', s)
    if ms: s = s[:ms.start(2)] + enc(shadow(im), 50, 60) + s[ms.end(2):]
    print(n, 'ok', 'shadow' if ms else 'no shadow')
open(P, 'w', encoding='utf-8').write(s)
print('html', len(s))
