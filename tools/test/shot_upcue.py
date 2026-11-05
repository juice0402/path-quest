# 11/5 はじめての冒険の「上へ」の矢印の点検：出る・騎士くんの真上・歩くと消える・3段のぼったあとは出ない
# usage: python3 tools/test/shot_upcue.py [out.png]   … out.png を渡すと、矢印の2コマを並べて1枚に（騎士くんのまわりを切り出す）
import asyncio, sys, os
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
CUE = """()=>{const c=document.querySelector('.upcue'),h=document.querySelector('.hero');if(!c)return null;const a=c.getBoundingClientRect(),b=h.getBoundingClientRect();
  return {cx:Math.round(a.left+a.width/2),hx:Math.round(b.left+b.width/2),above:a.bottom<=b.top+b.height*.2,top:Math.round(a.top),bottom:Math.round(a.bottom),htop:Math.round(b.top)}}"""

async def main():
    bad = []; shots = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{try{localStorage.clear()}catch(e){}PQ.newRun()}"); await pg.wait_for_timeout(900)
        c = await pg.evaluate(CUE); print('cue', c)
        if not c: bad.append('no cue on the first climb')
        elif abs(c['cx'] - c['hx']) > 3 or not c['above']: bad.append(f'cue not over the knight {c}')
        if len(sys.argv) > 1 and c:
            for k, t in enumerate((350, 500)):
                await pg.wait_for_timeout(t)
                await pg.screenshot(path=f'/tmp/_u{k}.png', clip={'x': c['hx'] - 95, 'y': c['top'] - 20, 'width': 190, 'height': c['htop'] - c['top'] + 110})
                shots.append(f'/tmp/_u{k}.png')
        await pg.evaluate("()=>PQ.FXH.emit('step',{})"); await pg.wait_for_timeout(100)
        if await pg.evaluate(CUE): bad.append('cue stays while the knight walks')
        await pg.evaluate("()=>{PQ.meta.far=3;PQ.render()}"); await pg.wait_for_timeout(200)
        if await pg.evaluate(CUE): bad.append('cue after the record reached 3')
        await pg.evaluate("()=>{PQ.meta.far=2;PQ.render()}"); await pg.wait_for_timeout(200)
        if not await pg.evaluate(CUE): bad.append('no cue again at record 2')
        if errs: bad.append(f'errors {errs[:2]}')
        await b.close()
    print('problems', len(bad)); [print(' ', x) for x in bad]
    if shots:
        from PIL import Image
        ims = [Image.open(s) for s in shots]; W = sum(i.width for i in ims) + 20
        out = Image.new('RGB', (W, ims[0].height), (60, 40, 30)); x = 0
        for i in ims: out.paste(i, (x, 0)); x += i.width + 20
        out.save(sys.argv[1], quality=88)

asyncio.run(main())
