# 11/5 お店の点検：同じものをもう一度タップすると紙が閉じるか、横向きのスマホで一覧と紙が左右に並ぶか
# usage: python3 tools/test/shop_land.py [out.png]   … out.png を渡すと 横向き（紙あり・なし）と縦向きを並べて1枚に
import asyncio, sys, os, json
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
META = {'bank': 800, 'best': 25, 'far': 25, 'seen': 0, 'up': {'hp': 2},
        'sk': {'own': ['turn', 'candy'], 'eq': ['turn', 'candy', None]}, 'gear': {'own': ['w1'], 'eq': {}}}
DET = "()=>{const d=document.getElementById('sh-det');return !d.hidden}"
GEO = """()=>{const b=document.getElementById('sh-body').getBoundingClientRect(),d=document.getElementById('sh-det').getBoundingClientRect();
  return {body:[Math.round(b.left),Math.round(b.width),Math.round(b.height)],det:[Math.round(d.left),Math.round(d.width),Math.round(d.height)],scrollX:document.documentElement.scrollWidth>innerWidth}}"""

async def main():
    bad = []; shots = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        for w, h in [(844, 390), (390, 844), (667, 375)]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, reduced_motion='reduce')
            await ctx.add_init_script("try{localStorage.clear();localStorage.setItem('pathquest.meta.v1',%s)}catch(e){}" % json.dumps(json.dumps(META)))
            pg = await ctx.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(URL); await pg.wait_for_timeout(500)
            for tab, sel in [('up', '[data-k="atk"]'), ('skill', '[data-s="candy"]'), ('deck', '[data-k="sd"]'), ('gear', '[data-g="w1"]')]:
                await pg.evaluate(f"()=>PQ.showShop('{tab}')"); await pg.wait_for_timeout(300)
                await pg.click(sel); await pg.wait_for_timeout(350)
                if not await pg.evaluate(DET): bad.append(f'{w}x{h} {tab}: first tap did not open the paper')
                g1 = await pg.evaluate(GEO)
                if w > h and tab == 'skill' and len(sys.argv) > 1: await pg.screenshot(path='/tmp/_l1.png'); shots.append('/tmp/_l1.png')
                if w > h and (g1['det'][0] < g1['body'][0] + g1['body'][1] - 2 or g1['body'][2] < 150): bad.append(f'{w}x{h} {tab}: not side by side {g1}')
                if g1['scrollX']: bad.append(f'{w}x{h} {tab}: horizontal scroll')
                await pg.click(sel); await pg.wait_for_timeout(350)
                if await pg.evaluate(DET): bad.append(f'{w}x{h} {tab}: second tap did not close the paper')
                g2 = await pg.evaluate(GEO)
                if w > h and tab == 'skill' and len(sys.argv) > 1: await pg.screenshot(path='/tmp/_l2.png'); shots.append('/tmp/_l2.png')
                await pg.click(sel); await pg.wait_for_timeout(350)
                if not await pg.evaluate(DET): bad.append(f'{w}x{h} {tab}: third tap did not open again')
            # the set skill in a slot: the same slot twice closes too
            await pg.evaluate("()=>PQ.showShop('skill')"); await pg.wait_for_timeout(300)
            await pg.click('[data-peg="1"]'); await pg.wait_for_timeout(300); o1 = await pg.evaluate(DET)
            await pg.click('[data-peg="1"]'); await pg.wait_for_timeout(300); o2 = await pg.evaluate(DET)
            if not o1 or o2: bad.append(f'{w}x{h} slot tap open={o1} then {o2}')
            # buying still works right after opening (the tap guard)
            await pg.evaluate("()=>PQ.showShop('up')"); await pg.wait_for_timeout(300)
            await pg.click('[data-k="def"]'); await pg.wait_for_timeout(400)
            b0 = await pg.evaluate("PQ.meta.bank"); await pg.click('#sh-det [data-act="buy"]'); await pg.wait_for_timeout(300)
            if await pg.evaluate("PQ.meta.bank") >= b0: bad.append(f'{w}x{h} buy after open did not buy')
            if w == 390 and h == 844 and len(sys.argv) > 1:
                await pg.screenshot(path='/tmp/_l3.png'); shots.append('/tmp/_l3.png')
            if errs: bad.append(f'{w}x{h} errors {errs[:2]}')
            await ctx.close()
        await b.close()
    print('problems', len(bad)); [print(' ', x) for x in bad]
    if shots:
        from PIL import Image
        ims = [Image.open(s) for s in shots]; H = min(i.height for i in ims)
        ims = [i.resize((int(i.width * H / i.height), H)) if i.height != H else i for i in ims]
        W = sum(i.width for i in ims) + 30 * (len(ims) - 1)
        out = Image.new('RGB', (W, H), (60, 40, 30)); x = 0
        for i in ims: out.paste(i, (x, 0)); x += i.width + 30
        out.resize((W // 2, H // 2)).save(sys.argv[1], quality=85)

asyncio.run(main())
