# 11/4 リザルト画面の「新記録」はんこの朱肉の輪（何度でも走らせてよい：印のあいだを入れかえる）
# 素材は Canva「PATH QUEST 素材（作業用）」(DAHZ0_Lb0zA) の 23 ページ「新記録はんこ」を PNG で書き出したもの → stamp.png
#   白い紙の上の赤い輪 → 白をすきとおらせ、インクのかすれはそのまま残す。文字はページの側で重ねる
# usage: python3 tools/ui/build_stamp_1104.py <書き出したPNGのフォルダ> [games/path-quest/index.html]
import sys, os, io, base64
import numpy as np
from PIL import Image
SRC = sys.argv[1]
P = sys.argv[2] if len(sys.argv) > 2 else 'games/path-quest/index.html'

im = np.asarray(Image.open(os.path.join(SRC, 'stamp.png')).convert('RGB')).astype(np.float32)
inkc = 255 - im[..., 1]                 # red ink: the green channel drops the most
a = np.clip((inkc - 18) / 190, 0, 1)
strong = a > .9
col = np.median(im[strong], axis=0) if strong.any() else np.array([205, 40, 40])
out = np.zeros(im.shape[:2] + (4,), np.uint8)
out[..., :3] = col.astype(np.uint8)
out[..., 3] = (a * 255).astype(np.uint8)
o = Image.fromarray(out, 'RGBA')
ys, xs = np.nonzero(out[..., 3] > 10)
o = o.crop((xs.min() - 4, ys.min() - 4, xs.max() + 5, ys.max() + 5)).resize((256, 256), Image.LANCZOS)
b = io.BytesIO(); o.save(b, 'WEBP', quality=82, method=6)
uri = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

A, B = '/* ===== Canva stamp 11/4 ===== */', '/* ===== end of Canva stamp ===== */\n'
CSS = A + f'\n:root{{--ui-stamp:url({uri})}}\n' + B
s = open(P, encoding='utf-8').read()
if A in s:
    i = s.index(A); j = s.index(B, i) + len(B); s = s[:i] + CSS + s[j:]
else:
    i = s.find('</style>'); s = s[:i] + CSS + s[i:]
open(P, 'w', encoding='utf-8').write(s)
print('ok stamp', len(uri), 'ink', col.astype(int).tolist(), 'html', len(s))
