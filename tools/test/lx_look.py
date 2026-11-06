# 11/6 宝物・きらきら・敵を自分の箱に出した版（lx）が、前の版と同じに見えるかの点検
# 同じ乱数で同じ場面にして、動きをある時刻で止めて（0秒・0.3秒・0.7秒・1.2秒）画面をくらべる
# usage: python3 tools/test/lx_look.py <前の版.html> [out.png] [jump の段]
import asyncio, sys, os
from playwright.async_api import async_playwright
from PIL import Image, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.abspath(os.path.join(HERE, '../../games/path-quest'))
OLD = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(G, '_old.html')
OUT = sys.argv[2] if len(sys.argv) > 2 else None
JUMP = int(sys.argv[3]) if len(sys.argv) > 3 else 0
TIMES = [0, .3, .7, 1.2]

async def scenes(b, path):
    ctx = await b.new_context(viewport={'width': 412, 'height': 915}, device_scale_factor=1)
    await ctx.add_init_script("{let x=55;Math.random=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return ((x>>>0)%1e6)/1e6}}")
    await ctx.add_init_script("try{localStorage.clear();localStorage.setItem('pathquest.meta.v1',JSON.stringify({bank:0,best:12,far:12,seen:1,up:{hp:2,atk:2},sk:{own:['turn'],eq:['turn',null,null]}}))}catch(e){}")
    pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('file://' + path + '#fxtest'); await pg.wait_for_timeout(600)
    await pg.click('#t-new'); await pg.wait_for_timeout(900)
    if JUMP: await pg.evaluate(f"()=>{{const r=PQ.run;r.maxHp=r.hp=9e6;r.atk=9e5;PQ.jump({JUMP})}}"); await pg.wait_for_timeout(1200)
    out = []
    for t in TIMES:
        css = f"*,*::before,*::after{{animation-play-state:paused!important;animation-delay:-{t}s!important;transition:none!important}}.weather,.lf-roam,.lf-sky,#notes,.say{{visibility:hidden!important}}"
        h = await pg.add_style_tag(content=css)
        await pg.evaluate("()=>document.getAnimations().forEach(a=>{if(!(a instanceof CSSAnimation))a.cancel()})")
        await pg.wait_for_timeout(200)
        p = f'/tmp/_lx_{t}_{os.path.basename(path)}.png'; await pg.screenshot(path=p); out.append((t, p))
        await h.evaluate('e=>e.remove()')
    n = await pg.evaluate("()=>[document.querySelectorAll('#board .lxp').length,document.querySelectorAll('#hand .lxp').length]")
    await ctx.close()
    return out, errs, n

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        a, ea, na = await scenes(b, OLD)
        n, en, nn = await scenes(b, os.path.join(G, 'index.html'))
        await b.close()
    print('errors old', ea[:2], 'new', en[:2], ' boxes (field, hand):', nn)
    pairs = []
    for (t, pa), (_, pn) in zip(a, n):
        A = Image.open(pa).convert('RGB'); N = Image.open(pn).convert('RGB')
        d = ImageChops.difference(A, N).convert('L'); data = list(d.getdata())
        big = sum(1 for v in data if v > 40); some = sum(1 for v in data if v > 12)
        print(f'time {t:.1f}s: pixels off >12: {some:6d}  >40: {big:5d}  max {max(data)}  box {d.getbbox()}')
        pairs.append((A, N, d))
    if OUT:
        A, N, d = pairs[1]
        im = Image.new('RGB', (A.width * 3 + 20, A.height), 'white'); im.paste(A, (0, 0)); im.paste(N, (A.width + 10, 0))
        im.paste(d.point(lambda v: 255 if v > 12 else 0).convert('RGB'), (A.width * 2 + 20, 0)); im.save(OUT)

asyncio.run(main())
