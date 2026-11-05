# 11/4 騎士くんのポーズの点検：盤面の上で1ポーズずつ撮って、横にならべた1枚にする
# usage: python3 tools/test/shot_hero.py out.png
import asyncio, sys, os, io
from playwright.async_api import async_playwright
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
POSES = 'front back side side/r swing block jump hurt cheer ko eat lift raise'.split()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg = await b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2, reduced_motion='reduce')
        await pg.goto(URL); await pg.wait_for_timeout(500)
        await pg.evaluate('()=>{try{localStorage.clear()}catch(e){}PQ.newRun()}'); await pg.wait_for_timeout(800)
        ims = []
        for ps in POSES:
            n, _, f = ps.partition('/')
            await pg.evaluate(f'()=>PQ.heroPose("{n}",0,{"true" if f else "false"})'); await pg.wait_for_timeout(120)
            bb = await pg.evaluate('()=>{const r=document.querySelector(".hero").getBoundingClientRect();return [r.left,r.top,r.width,r.height]}')
            x, y, w, h = bb
            png = await pg.screenshot(clip={'x': max(0, x - w * .35), 'y': max(0, y - h * .6), 'width': w * 1.7, 'height': h * 1.75})
            ims.append(Image.open(io.BytesIO(png)).convert('RGB'))
        W = sum(i.width for i in ims); H = max(i.height for i in ims)
        out = Image.new('RGB', (W, H), (255, 255, 255)); x = 0
        for i in ims: out.paste(i, (x, 0)); x += i.width
        out.save(sys.argv[1]); print(out.size)
        await b.close()
asyncio.run(main())
