# 11/5 細い画面の点検：帰還の画面・結果の画面のボタン、お店の紙のボタンが、はみ出したり字が切れたりしないか
# usage: python3 tools/test/narrow_check.py [out.png]   … out.png を渡すと 320 幅の3画面を並べて1枚に
import asyncio, sys, os, json
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
META = {'bank': 5000, 'best': 60, 'far': 60, 'seen': 0, 'up': {}, 'sk': {'own': ['turn'], 'eq': ['turn', None, None]}}
FIT = """(sel)=>{const out=[];for(const e of document.querySelectorAll(sel)){if(!e.offsetParent)continue;const r=e.getBoundingClientRect(),p=e.closest('.sh-det,.ov-card,.qv,.sheet');
  const pr=p?p.getBoundingClientRect():{left:0,right:innerWidth};
  const clip=[...e.querySelectorAll('*')].concat([e]).some(x=>x.scrollWidth>x.clientWidth+1&&getComputedStyle(x).overflow!=='visible')||e.scrollWidth>e.clientWidth+1;
  out.push({id:e.id||e.className.split(' ')[0],w:Math.round(r.width),text:Math.round(e.scrollWidth),out:Math.round(Math.max(0,r.right-Math.min(innerWidth,pr.right+2),Math.min(0,r.left-0)*-1)),clip})}return out}"""

async def main():
    shots = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        bad = 0
        for w, h in [(320, 568), (360, 640), (375, 667), (390, 844)]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, reduced_motion='reduce')
            await ctx.add_init_script("try{if(!sessionStorage.getItem('n')){localStorage.clear();sessionStorage.setItem('n',1)}localStorage.setItem('pathquest.meta.v1',%s)}catch(e){}" % json.dumps(json.dumps(META)))
            pg = await ctx.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(URL); await pg.wait_for_timeout(500)
            await pg.evaluate("()=>PQ.newRun()"); await pg.wait_for_timeout(700)
            await pg.click('#quit'); await pg.wait_for_timeout(500)
            q = await pg.evaluate(FIT, '#s-quit .ov-sub .btn')
            if w == 320 and len(sys.argv) > 1: await pg.screenshot(path=f'/tmp/_n1.png'); shots.append('/tmp/_n1.png')
            await pg.click('#q-yes'); await pg.wait_for_timeout(2500)
            o = await pg.evaluate(FIT, '#s-over .ov-sub .btn,#o-shop')
            if w == 320 and len(sys.argv) > 1: await pg.screenshot(path=f'/tmp/_n2.png'); shots.append('/tmp/_n2.png')
            res = {'quit': q, 'over': o}
            for tab, k in [('up', 'hp'), ('deck', 'dx'), ('skill', 'cross')]:
                await pg.evaluate(f"()=>PQ.showShop('{tab}')"); await pg.wait_for_timeout(300)
                await pg.click(f'[data-k="{k}"],[data-s="{k}"]'); await pg.wait_for_timeout(400)
                res['shop-' + tab] = await pg.evaluate(FIT, '#sh-det .dt-btn,#sh-det .dt-sub')
                if w == 320 and tab == 'up' and len(sys.argv) > 1: await pg.screenshot(path=f'/tmp/_n3.png'); shots.append('/tmp/_n3.png')
            for k, v in res.items():
                for x in v:
                    if x['out'] > 0 or x['clip']:
                        bad += 1; print(f'{w}x{h} {k}: {x}')
            if errs: print(w, 'errors', errs[:2])
            await ctx.close()
        await b.close()
    print('problems', bad)
    if shots:
        from PIL import Image
        ims = [Image.open(s) for s in shots]; W = sum(i.width for i in ims) + 30 * (len(ims) - 1)
        out = Image.new('RGB', (W, max(i.height for i in ims)), (60, 40, 30)); x = 0
        for i in ims: out.paste(i, (x, 0)); x += i.width + 30
        out.resize((W // 2, out.height // 2)).save(sys.argv[1], quality=85)

asyncio.run(main())
