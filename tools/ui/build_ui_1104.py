# 11/4 Canva の木と紙で UI を作り直す（何度でも走らせてよい：印のあいだを入れかえる）
# 素材は Canva「PATH QUEST 素材（作業用）」(DAHZ0_Lb0zA) の 17〜19 ページを PNG で書き出したもの
#   17 UI 木の板（ふつう・ピンク・緑）→ planks.png   18 UI 木の額（中は紙）→ frame.png   19 UI 木の壁 → wall.png
# usage: python3 tools/ui/build_ui_1104.py <書き出したPNGのフォルダ> [games/path-quest/index.html]
import sys, os, io, base64, subprocess, tempfile
import numpy as np
from PIL import Image, ImageFilter
SRC = sys.argv[1]
P = sys.argv[2] if len(sys.argv) > 2 else 'games/path-quest/index.html'
HERE = os.path.dirname(os.path.abspath(__file__))

def b64(im, fmt='WEBP', **kw):
    b = io.BytesIO(); im.save(b, fmt, **kw); return base64.b64encode(b.getvalue()).decode()

def tight(im):
    a = np.asarray(im)[..., 3]; ys, xs = np.nonzero(a > 8)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

def erode(im):  # drops the light fringe the white background leaves on the cut edge
    a = im.getchannel('A').filter(ImageFilter.MinFilter(3))
    im = im.copy(); im.putalpha(a); return im

def tint(im, c):
    a = np.asarray(im).astype(np.float32); a[..., :3] *= np.array(c, np.float32)[None, None, :]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')

# ---------- planks: cut from white, deepen the pink and the green so white letters read ----------
cut = tempfile.mkdtemp()
subprocess.run([sys.executable, os.path.join(HERE, 'slice.py'), os.path.join(SRC, 'planks.png'), '1', '3',
                'plank,plank_pink,plank_green', cut, '26', '20'], check=True, stdout=subprocess.DEVNULL)
PH = 124  # 2x of a 62px board
planks = {}
for n, c in (('plank', None), ('plank_pink', (0.9, 0.62, 0.72)), ('plank_green', (0.55, 0.78, 0.6))):
    im = erode(Image.open(os.path.join(cut, n + '.png')).convert('RGBA'))
    if c: im = tint(im, c)
    im = tight(im); im = im.resize((round(im.width * PH / im.height), PH), Image.LANCZOS)
    planks[n] = b64(im, quality=84, alpha_quality=90, method=6)
CAP = 64  # the nail end, in the 124px-tall plank

# ---------- the frame: crop to the wood, scale so the band is about 32px (16px on screen) ----------
fr = Image.open(os.path.join(SRC, 'frame.png')).convert('RGB'); A = np.asarray(fr).astype(int)
d = (255 - A).max(axis=2); H, W = d.shape
rows = np.where((d > 30).sum(axis=1) > W * 0.5)[0]; cols = np.where((d > 30).sum(axis=0) > H * 0.5)[0]
fr = fr.crop((cols.min() + 2, rows.min() + 2, cols.max() - 1, rows.max() - 1))
FW = 400; fr = fr.resize((FW, round(fr.height * FW / fr.width)), Image.LANCZOS)
g = np.asarray(fr).astype(int); mid = g[g.shape[0] // 2]
band = next(x for x in range(4, FW // 2) if mid[x].min() > 200)  # the first cream pixel from the left
SL = band + 1
frame = b64(fr, quality=86, method=6)
# the cream paper inside the frame doubles as the paper texture
big = Image.open(os.path.join(SRC, 'frame.png')).convert('RGB')
k = (cols.max() - cols.min()) / FW
ins = int((band + 6) * k)
pp = big.crop((cols.min() + ins, rows.min() + ins, cols.max() - ins, rows.max() - ins))
pp = pp.resize((640, round(pp.height * 640 / pp.width)), Image.LANCZOS)
paper = b64(pp, quality=80, method=6)

# ---------- the wooden wall ----------
wl = Image.open(os.path.join(SRC, 'wall.png')).convert('RGB'); wl = wl.resize((640, round(wl.height * 640 / wl.width)), Image.LANCZOS)
wall = b64(wl, quality=74, method=6)

U = lambda s: f'url("data:image/webp;base64,{s}")'
CSS = f'''/* ===== Canva UI 11/4 ===== */
/* wood planks, a wooden frame with paper inside, the wooden wall — made in Canva (「PATH QUEST 素材（作業用）」17〜19ページ), built by tools/ui/build_ui_1104.py */
:root{{--ui-plank:{U(planks['plank'])};--ui-plank-pink:{U(planks['plank_pink'])};--ui-plank-green:{U(planks['plank_green'])};--ui-frame:{U(frame)};--ui-paper:{U(paper)};--ui-wall:{U(wall)}}}
/* planks: the nail ends keep their shape and the middle stretches */
.btn.main,.dt-btn,.rw-go,.skn .sb-go,.sh-nav .go{{--capw:32px;box-sizing:border-box;clip-path:none;border-radius:0;background:none;box-shadow:none;
  border-style:solid;border-color:transparent;border-width:0 var(--capw);border-image-source:var(--ui-plank);border-image-slice:0 {CAP} fill;border-image-width:0 var(--capw);border-image-repeat:stretch;
  filter:drop-shadow(0 4px 0 rgba(58,28,8,.5))}}
.btn.main:active,.dt-btn:active,.rw-go:active,.skn .sb-go:active,.sh-nav .go:active{{transform:translateY(2px);box-shadow:none;filter:drop-shadow(0 1px 0 rgba(58,28,8,.45))}}
.btn.play::after{{display:none}}
.dt-btn,.rw-go,.skn .sb-go{{border-image-source:var(--ui-plank-green);color:#fff;text-shadow:0 2px 0 #1e5233,0 0 1px #1e5233}}
.dt-btn.alt{{border-image-source:var(--ui-plank);color:#fff6e6;text-shadow:0 2px 0 var(--wood-deep),0 0 1px var(--wood-deep)}}
.sh-nav{{grid-template-columns:1fr 1fr 1.9fr 1fr 1fr}}
.sh-nav .go{{border-image-source:var(--ui-plank-pink);--capw:18px;padding:0 2px;white-space:nowrap}}
.sh-nav .go-t{{font-size:18px;gap:5px}}
.dt-btn{{--capw:27px;padding:0 6px}}
.dt-btn:disabled{{filter:grayscale(.8) opacity(.6)}}
.rw-go{{--capw:28px}}
.rw-go:disabled{{filter:grayscale(.8) opacity(.6)}}
.skn .sb-go{{--capw:22px;padding:0 4px}}
.ov-sub .btn{{--capw:26px;padding:8px 4px}}
.ov .ov-go .mk{{position:static;align-self:flex-start;margin:6px 0 0 -2px;flex:none}}
/* paper: the cream paper from inside the frame */
.card,.sh-sheet,.rrow,.pill,.ibtn,.quit,.dt-sub,.skn .sb-x,.kit .skill,.btn:not(.main):not(.link),.sh-nav [role=tab][aria-selected=true]{{background-image:var(--ui-paper);background-size:cover;background-position:center}}
/* framed paper: the pinned paper of the shop, the message window and the skill paper on the field */
.sh-det,.say,.skn{{outline:0;background:none;box-shadow:none;border-style:solid;border-color:transparent;border-image-source:var(--ui-frame);border-image-slice:{SL} fill;border-image-repeat:stretch}}
.sh-det{{border-width:16px;border-image-width:16px;padding:2px 6px 6px;filter:drop-shadow(0 5px 0 rgba(48,22,6,.45))}}
.sh-det::before,.sh-det::after{{display:none}}
.say{{border-width:11px;border-image-width:11px;padding:2px 6px;filter:drop-shadow(0 3px 0 rgba(48,22,6,.4))}}
.skn{{border-width:12px;border-image-width:12px;padding:0 2px 0 0;filter:drop-shadow(0 4px 0 rgba(48,22,6,.4))}}
/* side by side in one row: one height and one depth (the paper's dark edge and the plank's shadow are both 4px) */
.sh-top .pill.bank{{box-sizing:border-box;height:44px;padding:0 14px 0 8px;box-shadow:0 4px 0 var(--frame)}}
.sh-top .pill.bank svg{{width:28px;height:28px}}
.dt-sub{{height:52px;box-shadow:0 4px 0 var(--frame)}}
.skn .sb-x{{box-shadow:0 4px 0 var(--frame)}}
/* the wooden wall behind the shop and under the field */
.sheet.shop{{background:#4a250d}}
.sh{{background:var(--ui-wall) center/cover,#b57336}}
.sh-nav{{background:linear-gradient(rgba(52,24,6,.5),rgba(52,24,6,.5)),var(--ui-wall) center/cover;box-shadow:0 -3px 0 #3d1d07}}
.tray{{background:var(--ui-wall) center/cover,#b57336}}
/* ===== end of Canva UI ===== */
'''
s = open(P, encoding='utf-8').read()
a, b = '/* ===== Canva UI 11/4 ===== */', '/* ===== end of Canva UI ===== */\n'
if a in s:
    i = s.index(a); j = s.index(b, i) + len(b); s = s[:i] + CSS + s[j:]
else:
    i = s.find('</style>'); s = s[:i] + CSS + s[i:]
open(P, 'w', encoding='utf-8').write(s)
print('ok band', band, 'slice', SL, 'sizes', {k: len(v) for k, v in planks.items()}, 'frame', len(frame), 'paper', len(paper), 'wall', len(wall), 'html', len(s))
