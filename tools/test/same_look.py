# 11/6 見た目が前と同じかの点検：前の版（PQ_OLD）と今の版を、同じ乱数で同じ場面にして、画面をくらべる
# usage: python3 tools/test/same_look.py <old.html> [out.png]
#   場面：タイトル・のぼりはじめ・積み木を置いたあと・5つ目の次元（虹色のマス）・ごほうび
import asyncio, sys, os
from playwright.async_api import async_playwright
from PIL import Image, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.abspath(os.path.join(HERE, '../../games/path-quest'))
OLD = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(G, '_old.html')
OUT = sys.argv[2] if len(sys.argv) > 2 else None
SEED = "{let x=777;Math.random=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return ((x>>>0)%1e6)/1e6}}"
META = "try{localStorage.clear();localStorage.setItem('pathquest.meta.v1',JSON.stringify({bank:0,best:12,far:12,seen:1,up:{hp:2,atk:2},sk:{own:['turn'],eq:['turn',null,null]}}))}catch(e){}"
CALM = "*,*::before,*::after{animation-play-state:paused!important;animation-delay:0s!important;transition:none!important;caret-color:transparent}"

async def scenes(b, path):
    ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, reduced_motion='reduce')
    await ctx.add_init_script(SEED); await ctx.add_init_script(META)
    pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('file://' + path + '#fxtest'); await pg.wait_for_timeout(700)
    await pg.add_style_tag(content=CALM)
    out = []
    async def shot(name):
        await pg.wait_for_timeout(250); p = f'/tmp/_look_{len(out)}_{os.path.basename(path)}.png'
        await pg.screenshot(path=p); out.append((name, p))
    await shot('title')
    await pg.click('#t-new'); await pg.wait_for_timeout(700); await shot('start')
    await pg.evaluate("()=>{const r=PQ.run;r.maxHp=r.hp=9e6;r.atk=9e5}")  # no early end
    for k in range(3):  # place three blocks the same way in both
        if not await pg.evaluate("()=>!!PQ.run&&PQ.run.phase==='build'"): break
        mv = await pg.evaluate("""()=>{const F=PQ.frontier();const r=PQ.run;for(let k=0;k<r.hand.length;k++){const t=r.hand[k];if(!t)continue;for(const j of F.keys())if(PQ.fits(t,j,F))return [k,j]}return null}""")
        if not mv: break
        await pg.evaluate(f"()=>PQ.place({mv[1]},{mv[0]})"); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{const v=id=>{const e=document.getElementById(id);return e&&!e.hidden};if(v('s-reward')){}}")
    await shot('placed')
    await pg.evaluate("()=>{if(!PQ.run){document.querySelectorAll('.sheet,.ov').forEach(x=>x.hidden=true);PQ.newRun()}const r=PQ.run;r.maxHp=r.hp=9e6;r.atk=9e5;PQ.jump(4*50+3)}"); await pg.wait_for_timeout(1500); await shot('dim5')
    await pg.evaluate("()=>{PQ.run.reward=true;PQ.openReward()}"); await pg.wait_for_timeout(900); await shot('reward')
    await ctx.close()
    return out, errs

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        a, ea = await scenes(b, OLD)
        n, en = await scenes(b, os.path.join(G, 'index.html'))
        await b.close()
    print('errors old', ea[:2], 'new', en[:2])
    rows = []
    for (name, pa), (_, pn) in zip(a, n):
        A = Image.open(pa).convert('RGB'); N = Image.open(pn).convert('RGB')
        d = ImageChops.difference(A, N); bb = d.getbbox()
        px = sum(1 for v in d.convert('L').getdata() if v > 24)
        print(f'{name:8s} different pixels {px:6d} {"box " + str(bb) if bb else "same"}')
        rows.append((A, N))
    if OUT:
        W, H = 390, 844; im = Image.new('RGB', (W * 2 + 10, (H + 10) * len(rows)), 'white')
        for k, (A, N) in enumerate(rows): im.paste(A, (0, k * (H + 10))); im.paste(N, (W + 10, k * (H + 10)))
        im.save(OUT)

asyncio.run(main())
