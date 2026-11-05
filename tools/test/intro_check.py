# 11/5 はじめての人の最初の一手の点検（q：2段まで・左はし）：スキルなしで始まる・置ける所は上だけ・置けるのは上向きのまっすぐだけ・指がそれをさす・1歩で元どおり
# usage: python3 tools/test/intro_check.py [out.png]   … out.png を渡すと、はじめの画面と積み木をえらんだ画面を並べて1枚に
import asyncio, sys, os
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
TAP = """el=>{const r=el.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2,o={bubbles:true,cancelable:true,clientX:x,clientY:y,pointerId:7,pointerType:'touch',isPrimary:true,button:0};
  el.dispatchEvent(new PointerEvent('pointerdown',{...o,buttons:1}));document.dispatchEvent(new PointerEvent('pointerup',{...o,buttons:0}));}"""
ST = """()=>{const r=PQ.run,F=PQ.frontier(),f=document.querySelector('.finger');
  return {intro:r.intro|0,front:[...F.keys()],up:PQ.idOf(2,2),fit:r.hand.map(t=>PQ.anyFit(t,F)),dull:[...document.querySelectorAll('#hand .slot')].map(s=>s.classList.contains('dull')),
    last:r.hand.length-1,lastM:r.hand[0].m,finger:f?(f.closest('.slot')?'slot'+f.closest('.slot').dataset.i:f.closest('.cell')?'cell'+f.closest('.cell').dataset.i:'?'):null,
    sk:[...PQ.meta.sk.own],eq:[...PQ.meta.sk.eq],skillsNone:document.querySelectorAll('.skill.none').length}}"""

async def main():
    bad = []; shots = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
        await ctx.add_init_script("if(!sessionStorage.getItem('i')){try{localStorage.clear()}catch(e){}sessionStorage.setItem('i',1)}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(500)
        await pg.click('#t-new'); await pg.wait_for_timeout(1000)
        s = await pg.evaluate(ST); print('start', s)
        if s['sk'] or any(s['eq']): bad.append(f"a new player has skills {s['sk']} {s['eq']}")
        if s['front'] != [s['up']]: bad.append(f"places other than up {s['front']}")
        want = [True] + [False] * s['last']
        if s['fit'] != want or s['dull'][:s['last'] + 1] != [not x for x in want]: bad.append(f"fits {s['fit']} dull {s['dull']}")
        if s['lastM'] != 5: bad.append(f"the lesson block is not straight: {s['lastM']}")
        if s['finger'] != 'slot0': bad.append(f"finger on {s['finger']}")
        if len(sys.argv) > 1: await pg.screenshot(path='/tmp/_i0.png'); shots.append('/tmp/_i0.png')
        # a dull block cannot be chosen into the up cell
        await (await pg.query_selector(f'#hand .slot[data-i="{s["last"]}"]')).evaluate(TAP); await pg.wait_for_timeout(250)
        await (await pg.query_selector(f'.cell[data-i="{s["up"]}"]')).evaluate(TAP); await pg.wait_for_timeout(600)
        if await pg.evaluate("()=>PQ.run.top") != 1: bad.append('a dull block went down')
        # the straight one: the finger moves to the cell above, then it goes and the knight walks
        await (await pg.query_selector('#hand .slot[data-i="0"]')).evaluate(TAP); await pg.wait_for_timeout(300)
        s2 = await pg.evaluate(ST); print('chosen', s2['finger'])
        if s2['finger'] != f"cell{s['up']}": bad.append(f"finger after choosing on {s2['finger']}")
        if len(sys.argv) > 1: await pg.screenshot(path='/tmp/_i1.png'); shots.append('/tmp/_i1.png')
        await (await pg.query_selector(f'.cell[data-i="{s["up"]}"]')).evaluate(TAP); await pg.wait_for_timeout(1500)
        s3 = await pg.evaluate(ST); top = await pg.evaluate("()=>PQ.run.top"); print('after step', s3, 'top', top)
        if top != 2 or s3['intro'] or not any(s3['fit']): bad.append(f'after the first step {s3} top {top}')
        # a reroll ends the lesson
        await pg.evaluate("()=>{PQ.meta.far=0;PQ.saveMeta();PQ.newRun()}"); await pg.wait_for_timeout(600)
        await pg.evaluate("()=>PQ.reroll()"); await pg.wait_for_timeout(500)
        s4 = await pg.evaluate(ST)
        if s4['intro'] or len(s4['front']) < 2: bad.append(f'reroll did not end the lesson {s4}')
        # a player who has climbed 2 steps: no lesson
        await pg.evaluate("()=>{PQ.meta.far=2;PQ.saveMeta();PQ.newRun()}"); await pg.wait_for_timeout(600)
        s5 = await pg.evaluate(ST)
        if s5['intro'] or len(s5['front']) < 2: bad.append(f'lesson for a player past 2 steps {s5}')
        if errs: bad.append(f'errors {errs[:2]}')
        await b.close()
    print('problems', len(bad)); [print(' ', x) for x in bad]
    if shots:
        from PIL import Image
        ims = [Image.open(x) for x in shots]; W = sum(i.width for i in ims) + 30
        out = Image.new('RGB', (W, ims[0].height), (60, 40, 30)); x = 0
        for i in ims: out.paste(i, (x, 0)); x += i.width + 30
        out.resize((W // 2, out.height // 2)).save(sys.argv[1], quality=85)

asyncio.run(main())
