# 11/6 のこしたマスが、作りなおしたマスと同じかの点検
# ふつうの動きで遊びながら、ときどき：動きを止めて画面をとる → 盤面を全部作りなおす → もう一度とる → くらべる
# usage: python3 tools/test/keep_same.py [checks] [out.png]
import asyncio, sys, os, random
from playwright.async_api import async_playwright
from PIL import Image, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'bot.py'), encoding='utf-8').read()
exec(src[:src.index('async def main')].replace('GAMES = int', 'GAMES = 1 or int').replace('STEPS = int', 'STEPS = 1 or int'))  # TAP, STATE, PICK, wait_idle, tap
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
N = int(sys.argv[1]) if len(sys.argv) > 1 else 12
OUT = sys.argv[2] if len(sys.argv) > 2 else None
STILL = "*,*::before,*::after{animation:none!important;transition:none!important}.lf-roam,.pop,.fly,.bit,.note,#notes{visibility:hidden!important}"

async def snap(pg, p):
    await pg.evaluate("()=>document.getAnimations().forEach(a=>a.cancel())"); await pg.wait_for_timeout(120)
    await pg.screenshot(path=p, clip={'x': 0, 'y': 0, 'width': 390, 'height': 700})

async def main():
    bad = []; pairs = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, has_touch=True)
        await ctx.add_init_script("try{localStorage.clear();localStorage.setItem('pathquest.meta.v1',JSON.stringify({bank:0,best:12,far:12,seen:1,up:{hp:3,atk:3},sk:{own:['turn'],eq:['turn',null,null]}}))}catch(e){}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(700)
        await tap(pg, '#t-new'); await pg.wait_for_timeout(500)
        await pg.evaluate("()=>{PQ.run.maxHp=PQ.run.hp=9999}")
        rnd = random.Random(5); done = 0; steps = 0
        while done < N and steps < 400:
            st = await wait_idle(pg)
            if st['over']: await tap(pg, '#o-again'); await pg.wait_for_timeout(600); await pg.evaluate("()=>{PQ.run.maxHp=PQ.run.hp=9999}"); continue
            if st['shop']: await tap(pg, '#sh-go'); await pg.wait_for_timeout(600); continue
            if st['reward']:
                await pg.wait_for_timeout(600); await tap(pg, '#r-list .rrow[data-i="0"]'); await pg.wait_for_timeout(100); await tap(pg, '#r-go'); await pg.wait_for_timeout(900); continue
            if not st['run'] or st['busy'] or st['phase'] != 'build': await pg.wait_for_timeout(100); continue
            if steps % 3 == 2:  # a check
                await pg.wait_for_timeout(450)  # the knight turns to the front 260ms after a walk
                h = await pg.add_style_tag(content=STILL)
                a = f'/tmp/_ks_a{done}.png'; c = f'/tmp/_ks_b{done}.png'
                await snap(pg, a)
                await pg.evaluate("()=>{document.getElementById('board').innerHTML='';PQ.render()}")
                await snap(pg, c)
                await h.evaluate('e=>e.remove()')
                A = Image.open(a).convert('RGB'); B = Image.open(c).convert('RGB')
                d = ImageChops.difference(A, B); px = sum(1 for v in d.convert('L').get_flattened_data() if v > 24) if hasattr(d, 'get_flattened_data') else sum(1 for v in d.convert('L').getdata() if v > 24)
                print(f'check {done}: step {steps} different pixels {px} {d.getbbox()}')
                if px > 40: bad.append((done, px)); pairs.append((A, B))
                done += 1
            mv = await pg.evaluate(PICK, rnd.random())
            if not mv:
                if st['rolls']: await tap(pg, '#roll'); await pg.wait_for_timeout(300); continue
                await pg.wait_for_timeout(1500); continue
            slot, cell, _ = mv
            await tap(pg, f'#hand .slot[data-i="{slot}"]'); await pg.wait_for_timeout(120)
            await tap(pg, f'#board .cell[data-i="{cell}"]'); await pg.wait_for_timeout(200)
            steps += 1
        await b.close()
    print('errors', errs[:3]); print('checks', done, 'different', bad)
    if OUT and pairs:
        im = Image.new('RGB', (790, 710 * len(pairs[:3])), 'white')
        for k, (A, B) in enumerate(pairs[:3]): im.paste(A, (0, k * 710)); im.paste(B, (400, k * 710))
        im.save(OUT)

asyncio.run(main())
