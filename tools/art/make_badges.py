"""Game Center のバッジ（実績の絵）を作る（11/26）
usage: python3 tools/art/make_badges.py [見本.png]   → docs/kobo/achievements/<id>.png（1024×1024・RGB・文字なし）

- まん中の絵と地面は、ゲームと同じ Canva の AI の絵（A）。作業用デザイン DAHZ0_Lb0zA のページを書き出して切り出したもの（tools/art/badge_src/・どのページかは tools/ART.md）
- 木のふち・くぎ・星・夜の色はコード（C）。ふちは UI の木の板（assets/ui-plank*.webp）を輪に曲げたもの
- ふちの色は点の重さ：10 緑の板・25 木の板・50 ピンクの板・100 金色（木の板を金色に）
- Game Center は丸く切って見せるので、大事なものは丸の中に。角は紙の色
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
SRC = os.path.join(ROOT, 'tools/art/badge_src')
ASSET = os.path.join(ROOT, 'games/path-quest/assets')
OUT = os.path.join(ROOT, 'docs/kobo/achievements')
N = 1024; C = N / 2
R_OUT, R_IN = 500, 384            # the wooden ring
PAPER = (244, 231, 212)           # the app's background

# id → (picture, ground, how big, extra)
BADGES = {
    'path_floor10':  ('box',    'g-grass',  0.62, None),
    'path_captain':  ('boss',   'g-forest', 0.82, None),
    'path_floor40':  ('cheer',  'g-lake',   0.76, None),
    'path_king':     ('king',   'g-lake',   0.82, None),
    'path_castle':   ('castle', 'g-castle', 0.64, None),
    'path_night':    ('portal', 'night',    0.66, 'nightstars'),
    'path_skill3':   ('turn',   'g-grass',  0.62, None),
    'path_skill_all':('cross',  'g-snow',   0.68, None),
    'path_up_max':   ('lift',   'g-forest', 0.8, None),
    'path_gear10':   ('chest',  'g-grass',  0.64, None),
    'path_star2':    ('wand',   'g-snow',   0.62, 'twostars'),
    'path_toy_lv5':  ('boomer', 'g-castle', 0.62, None),
    'path_evolve':   ('plane',  'g-lake',   0.64, 'sparkle'),
    'path_rich':     ('coin',   'g-forest', 0.58, 'pile'),
}
PLANK = {10: 'ui-plank-green', 25: 'ui-plank', 50: 'ui-plank-pink', 100: 'gold'}
NAIL = {10: ((30, 82, 51), (196, 220, 180)), 25: ((94, 52, 23), (243, 226, 196)), 50: ((120, 34, 62), (250, 214, 222)), 100: ((128, 86, 20), (255, 240, 190))}

def load(p, mode='RGBA'): return Image.open(p).convert(mode)

def plank_strip(name):
    """the middle of a plank (no nail ends), as an array, mirrored so the tiles join without a seam"""
    base = 'ui-plank' if name == 'gold' else name
    im = load(os.path.join(ASSET, base + '.webp'))
    w, h = im.size; im = im.crop((int(w * .16), 0, int(w * .84), h))
    a = np.asarray(im).astype(float)
    if name == 'gold':  # the wood, coloured like the coins
        lum = (a[..., :3] @ [.3, .59, .11]) / 255
        lo, hi = np.array([170, 112, 24]), np.array([255, 222, 120])
        a[..., :3] = lo + (hi - lo) * np.clip((lum - .25) / .6, 0, 1)[..., None]
    return np.concatenate([a, a[:, ::-1]], axis=1)

def ring(name):
    """bend the plank into a ring: along the plank = around the circle, across the plank = outside → inside"""
    s = plank_strip(name); sh, sw = s.shape[:2]
    y, x = np.mgrid[0:N, 0:N].astype(float) + .5
    dx, dy = x - C, y - C; r = np.hypot(dx, dy); t = (np.arctan2(dy, dx) + math.pi) / (2 * math.pi)
    reps = max(1, round(2 * math.pi * (R_OUT + R_IN) / 2 / (sw * (R_OUT - R_IN) / sh)))
    u = ((t * reps * sw) % sw).astype(int)
    v = np.clip(((R_OUT - r) / (R_OUT - R_IN) * (sh - 1)), 0, sh - 1).astype(int)
    out = s[v, u].copy()
    # a soft edge on the outside and the inside (1.5px)
    a = np.clip(np.minimum(R_OUT - r, r - R_IN) / 1.5 + .5, 0, 1)
    out[..., 3] = out[..., 3] * a
    return Image.fromarray(out.astype(np.uint8), 'RGBA')

def ground(kind):
    if kind == 'night':  # the night dimension: the snow ground under its colour
        g = load(os.path.join(SRC, 'g-snow.webp'), 'RGB')
        a = np.asarray(g).astype(float) * np.array([70, 78, 135]) / 255
        g = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    else:
        g = load(os.path.join(SRC, kind + '.webp'), 'RGB')
    d = 2 * R_IN + 8
    return g.resize((d, d), Image.LANCZOS)

def star(d, cx, cy, r, fill=(255, 217, 94), line=(224, 161, 42), w=10):
    """the game's star (const STAR): four points"""
    k = r * .3; pts = [(cx, cy - r), (cx + k, cy - k), (cx + r, cy), (cx + k, cy + k), (cx, cy + r), (cx - k, cy + k), (cx - r, cy), (cx - k, cy - k)]
    d.polygon(pts, fill=fill, outline=line, width=w)

def five(d, cx, cy, r, fill=(255, 217, 94), line=(224, 161, 42), w=9):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5; rr = r if i % 2 == 0 else r * .45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill, outline=line, width=w)

def outlined(sp, w=12, col=(255, 250, 240)):
    """a cream edge around the picture (thick colour under it, as in the game)"""
    a = sp.split()[3]
    big = a.filter(ImageFilter.MaxFilter(w * 2 + 1)).filter(ImageFilter.GaussianBlur(1))
    base = Image.new('RGBA', sp.size, col + (0,)); base.putalpha(big)
    base.alpha_composite(sp); return base

def picture(name, size, extra):
    sp = load(os.path.join(SRC, name + '.webp'))
    if extra == 'pile':  # three coins
        w, h = sp.size; cv = Image.new('RGBA', (int(w * 2.1), int(h * 1.7)), (0, 0, 0, 0))
        cv.alpha_composite(sp, (0, int(h * .7))); cv.alpha_composite(sp, (int(w * 1.1), int(h * .7))); cv.alpha_composite(sp, (int(w * .55), 0))
        sp = cv.crop(cv.getbbox())
    sp = sp.crop(sp.getbbox())
    box = int(2 * R_IN * size); s = box / max(sp.size)
    sp = sp.resize((max(1, int(sp.width * s)), max(1, int(sp.height * s))), Image.LANCZOS)
    pad = 24; cv = Image.new('RGBA', (sp.width + 2 * pad, sp.height + 2 * pad), (0, 0, 0, 0)); cv.alpha_composite(sp, (pad, pad))
    return outlined(cv)

def badge(bid, pts):
    name, gk, size, extra = BADGES[bid]
    im = Image.new('RGBA', (N, N), PAPER + (255,))
    g = ground(gk); m = Image.new('L', g.size, 0); ImageDraw.Draw(m).ellipse((0, 0, g.width - 1, g.height - 1), fill=255)
    im.paste(g, (int(C - g.width / 2), int(C - g.height / 2)), m)
    d = ImageDraw.Draw(im)
    if extra == 'nightstars':
        for x, y, r in [(330, 300, 18), (690, 310, 24), (300, 610, 14), (720, 640, 16), (520, 255, 12)]: star(d, x, y, r, w=5)
    sp = picture(name, size, extra)
    im.alpha_composite(sp, (int(C - sp.width / 2), int(C - sp.height / 2 + 14)))
    if extra == 'twostars':
        five(d, 640, 300, 58); five(d, 735, 395, 46)
    if extra == 'sparkle':
        for x, y, r in [(300, 330, 40), (705, 300, 30), (690, 650, 34), (330, 660, 22)]: star(d, x, y, r)
    im.alpha_composite(ring(PLANK[pts]))
    dark, light = NAIL[pts]
    for k in range(4):  # nails like the planks' ends
        a = math.pi / 4 + k * math.pi / 2; rr = (R_OUT + R_IN) / 2
        x, y = C + rr * math.cos(a), C + rr * math.sin(a)
        d.ellipse((x - 15, y - 15, x + 15, y + 15), fill=dark); d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=light)
    return im.convert('RGB')

def main():
    gc = json.load(open(os.path.join(ROOT, 'docs/kobo/gamecenter.json'), encoding='utf-8'))
    os.makedirs(OUT, exist_ok=True); made = []
    for a in gc['achievements']:
        im = badge(a['id'], a['points'])
        p = os.path.join(ROOT, 'docs/kobo', a['image']); im.save(p, optimize=True); made.append((a['id'], im))
    print('made', len(made))
    if len(sys.argv) > 1:  # one sheet to look at, cut round like Game Center
        W = 5; c = 220; sh = Image.new('RGB', (W * c, ((len(made) + W - 1) // W) * c), (60, 60, 66))
        m = Image.new('L', (c - 20, c - 20), 0); ImageDraw.Draw(m).ellipse((0, 0, c - 21, c - 21), fill=255)
        for i, (bid, im) in enumerate(made):
            sh.paste(im.resize((c - 20, c - 20), Image.LANCZOS), ((i % W) * c + 10, (i // W) * c + 10), m)
        sh.save(sys.argv[1]); print('saved', sys.argv[1])

if __name__ == '__main__':
    main()
