"""Put the Canva art into games/path-quest/index.html.

usage: python3 build_art.py CUTDIR
Everything goes into one block right after <body>, between <!--ART--> and <!--/ART-->:
- sprites become <symbol id="a-NAME"> (bottom-centred, keeping their shape), drawn with <use>
- ground tiles and the title picture become CSS variables (--t-NAME) used as backgrounds
Re-running replaces the block, so the art can be swapped without touching the game code.
A picture with no PNG in CUTDIR keeps the one already in the page, so CUTDIR only needs the new or changed pictures.
"""
import sys, os, io, base64, re
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, 'games', 'path-quest', 'index.html')

SPRITES = {  # name: longest side in px
    'hero': 220, 'soldier': 200, 'bugle': 200, 'cannon': 200, 'robot': 200, 'boss': 240,
    **{k: 128 for k in 'w1 w2 w3 w4 w5 s1 s2 s3 s4 s5 c1 c2 c3 c4 c5 coin'.split()},
    **{k: 180 for k in 'house tree pond snowman wall fence box marble'.split()},
    **{k: 128 for k in 'candy heart bag dice door stack flag key'.split()},
    **{f'b{k}': 200 for k in range(5)},
    'king': 260, 'chest': 128, 'portal': 160,
    **{k: 128 for k in 'wst1 wbk1 wha1 wnd2 wbk2 wkn2 wst3 wnd3 wrp3 wbk4 wst4'.split()},  # p8
    **{k: 128 for k in 'rb1 sp1 mt1 mr2 rb2 cl2 ar3 rb3 mr3 mr4 rb4'.split()},  # p9
    **{k: 128 for k in 'cx1 cc2 cm2 ct2 cp3 cr3 cx3 ca3 ck4 cs4 cf4'.split()},  # p10
}
BACKS = {'g-grass': 180, 'g-forest': 180, 'g-lake': 180, 'g-snow': 180, 'g-castle': 180, 'title': 900}

def uri(path, side, q=80, alpha=True):
    im = Image.open(path).convert('RGBA' if alpha else 'RGB')
    s = side / max(im.size)
    if s < 1: im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'WEBP', quality=q, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode(), im.size, len(b.getvalue())

def main():
    cut = sys.argv[1]
    syms, css, total = [], [], 0
    s = open(GAME, encoding='utf-8').read()
    old_sym = {m.group(1): m.group(0) for m in re.finditer(r'<symbol id="a-([\w-]+)".*?</symbol>', s, flags=re.S)}
    old_css = {m.group(1): m.group(0) for m in re.finditer(r'--t-([\w-]+):url\("[^"]*"\);', s)}
    for n, side in SPRITES.items():
        p = os.path.join(cut, n + '.png')
        if not os.path.exists(p):
            if n in old_sym: syms.append(old_sym[n])
            continue
        u, (w, h), size = uri(p, side); total += size
        syms.append(f'<symbol id="a-{n}" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMax meet"><image href="{u}" width="{w}" height="{h}"/></symbol>')
    for n, side in BACKS.items():
        p = os.path.join(cut, n + '.png')
        if not os.path.exists(p):
            if n in old_css: css.append(old_css[n])
            continue
        u, _, size = uri(p, side, 78, alpha=n != 'title' and not n.startswith('g-')); total += size
        css.append(f'--t-{n}:url("{u}");')
    block = ('<!--ART-->\n<style>:root{' + ''.join(css) + '}</style>\n'
             '<svg class="art-defs" width="0" height="0" aria-hidden="true" focusable="false"><defs>' + ''.join(syms) + '</defs></svg>\n<!--/ART-->')
    if '<!--ART-->' in s:
        s = re.sub(r'<!--ART-->.*?<!--/ART-->', lambda m: block, s, flags=re.S)
    else:
        s = s.replace('<body>\n', '<body>\n' + block + '\n', 1)
    open(GAME, 'w', encoding='utf-8').write(s)
    print(f'{len(syms)} sprites, {len(css)} backgrounds, {total // 1024}KB of WebP')

if __name__ == '__main__':
    main()
