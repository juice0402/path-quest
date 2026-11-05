# 11/4 敵20体（黒っぽい衣装のいたずら顔のおもちゃ）と騎士くんの12ポーズを、ページの絵（symbol）と影（-sh）に入れる。何度走らせても同じ
# 元の絵：Canva「PATH QUEST 素材（作業用）」DAHZ0_Lb0zA の 25〜28 ページ。書き出して tools/art/cut_sheet.py で切り出したもの
#   25: soldier,bugle,cannon,robot,archer,mage,clown,imp,mason,skel,ghost   26: boss,king,mouse,bear
#   27: shroom,duck,frog,peng,hedge   28: front,back,side,swing,block,jump,hurt,cheer,ko,eat,lift,raise（騎士くん）
# usage: python3 tools/art/build_foes_1104.py <切り出した敵のフォルダ> <切り出した騎士くんのフォルダ> [games/path-quest/index.html]
import sys, re, io, base64
import numpy as np
from PIL import Image, ImageFilter
FD, HD = sys.argv[1], sys.argv[2]
P = sys.argv[3] if len(sys.argv) > 3 else 'games/path-quest/index.html'
FOES = 'soldier bugle cannon robot archer mage clown mason boss king imp mouse bear shroom duck frog peng hedge skel ghost'.split()
TALL = {'boss': 240, 'king': 260}          # the captain and the king are drawn bigger
HERO = {'front': 'hero', 'back': 'hback', 'side': 'hside', 'swing': 'hswing', 'block': 'hblock', 'jump': 'hjump', 'hurt': 'hhurt',
        'cheer': 'hcheer', 'ko': 'hko', 'eat': 'heat', 'lift': 'hlift', 'raise': 'hraise'}

def enc(im, q=84, aq=90):
    b = io.BytesIO(); im.save(b, 'WEBP', quality=q, alpha_quality=aq, method=6); return base64.b64encode(b.getvalue()).decode()

def shadow(im):  # the same soft shadow the other toys have, from the outline
    w, h = im.size
    al = im.getchannel('A').resize((max(8, w // 2), max(8, h // 2)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.6))
    A = (np.asarray(al).astype(np.float32) * 0.4).astype(np.uint8)
    return Image.fromarray(np.dstack([np.full_like(A, 56), np.full_like(A, 30), np.full_like(A, 46), A]), 'RGBA')

def anchor(im, wide=False):  # where the body stands, as a share of the width: the middle of the head and shoulders
    if wide: return 0.5
    a = np.asarray(im.getchannel('A')).astype(np.float32); h = a.shape[0]
    band = a[int(h * .15):int(h * .45)]; xs = np.arange(a.shape[1])
    s = band.sum()
    return float((band.sum(0) * xs).sum() / s / a.shape[1]) if s else 0.5

def sym(n, im, ax=None):
    w, h = im.size; extra = f' data-ax="{ax:.3f}"' if ax is not None else ''
    return (f'<symbol id="a-{n}" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMax meet"{extra}><image href="data:image/webp;base64,{enc(im)}" width="{w}" height="{h}"/></symbol>',
            f'<symbol id="a-{n}-sh" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMax meet"><image href="data:image/webp;base64,{enc(shadow(im), 50, 60)}" width="{w}" height="{h}"/></symbol>')

s = open(P, encoding='utf-8').read()
def put(n, art, sh):
    global s
    for sid, new in ((n, art), (n + '-sh', sh)):
        m = re.search(r'<symbol id="a-' + re.escape(sid) + r'"[^>]*>.*?</symbol>', s)
        if m: s = s[:m.start()] + new + s[m.end():]
        else:  # a new one goes next to the hero's (the picture) or the hero's shadow
            anchor_id = 'a-hero' if not sid.endswith('-sh') else 'a-hero-sh'
            k = s.index('<symbol id="' + anchor_id + '"'); s = s[:k] + new + s[k:]

for n in FOES:
    im = Image.open(f'{FD}/{n}.png').convert('RGBA'); H = TALL.get(n, 200)
    im = im.resize((max(1, round(im.width * H / im.height)), H), Image.LANCZOS)
    put(n, *sym(n, im, anchor(im)))
# the knight: every pose at the same scale as the front one, so he keeps his size
fr = Image.open(f'{HD}/front.png'); k = 220 / fr.height
for p, n in HERO.items():
    im = Image.open(f'{HD}/{p}.png').convert('RGBA')
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    put(n, *sym(n, im, anchor(im, p == 'ko')))
open(P, 'w', encoding='utf-8').write(s)
print('ok', len(FOES), 'toys', len(HERO), 'poses', len(s), 'bytes')
