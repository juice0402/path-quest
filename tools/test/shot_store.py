# 11/24 App Store のスクショの場面（ゲームの #shot=）を、ios-kobo の shots.py と同じ流れで撮って並べる
# usage: python3 tools/test/shot_store.py [out.png] [iphone|ipad]
#   場面：title・climb・foe・reward・boss・shop（ページの「App Store screenshots」のまとまり。navigator.webdriver のときだけ動く）
import asyncio, sys, os
from playwright.async_api import async_playwright
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
GAME = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html'))
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/pq_store.png'
KIND = sys.argv[2] if len(sys.argv) > 2 else 'iphone'
VIEW = {'iphone': (440, 956), 'ipad': (1032, 1376)}[KIND]
SCENES = [('title', 3), ('climb', 4), ('foe', 4), ('reward', 5), ('boss', 4), ('shop', 3)]
SEED = "(function(){var s=7;Math.random=function(){s=s*16807%2147483647;return(s-1)/2147483646};location.hash='shot=NAME'})();"

async def main():
    shots = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox', '--autoplay-policy=no-user-gesture-required'])
        for name, wait in SCENES:
            ctx = await b.new_context(viewport={'width': VIEW[0], 'height': VIEW[1]}, device_scale_factor=1, is_mobile=True, has_touch=True, locale='ja')
            pg = await ctx.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(GAME); await pg.wait_for_timeout(400)
            await pg.evaluate(SEED.replace('NAME', name)); await pg.wait_for_timeout(wait * 1000)
            path = f'/tmp/pq_store_{name}.png'; await pg.screenshot(path=path); shots.append(path)
            print(name, 'errors:', errs[:1] if errs else 'none')
            await ctx.close()
        await b.close()
    W, H = VIEW; cols = 3; im = Image.new('RGB', ((W + 10) * cols, (H + 10) * 2), 'white')
    for k, s in enumerate(shots): im.paste(Image.open(s).convert('RGB'), ((k % cols) * (W + 10), (k // cols) * (H + 10)))
    im.thumbnail((1800, 1800)); im.save(OUT); print('saved', OUT)

asyncio.run(main())
