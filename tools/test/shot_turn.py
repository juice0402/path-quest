# 11/5 くるっと回すの点検：えらぶ間は回る積み木に↻と回る道、タップで右に1/4回る。コマ撮りを1枚に並べる
# usage: python3 tools/test/shot_turn.py [out.png]
import asyncio, sys, os
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
TAP = """el=>{const r=el.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2,o={bubbles:true,cancelable:true,clientX:x,clientY:y,pointerId:7,pointerType:'touch',isPrimary:true,button:0};
  el.dispatchEvent(new PointerEvent('pointerdown',{...o,buttons:1}));document.dispatchEvent(new PointerEvent('pointerup',{...o,buttons:0}));}"""

async def main():
    bad = []; shots = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{try{localStorage.clear()}catch(e){}PQ.meta.far=5;PQ.meta.sk.eq[0]='turn';PQ.newRun()}"); await pg.wait_for_timeout(900)
        await pg.evaluate("()=>{const h=PQ.run.hand;h[0].m=5;h[1].m=3;h[2].m=7;h[3].m=15;PQ.meta.far=5;PQ.render()}"); await pg.wait_for_timeout(300)
        box = await pg.evaluate("()=>{const r=document.getElementById('hand').getBoundingClientRect();return {x:r.left,y:r.top-30,width:r.width,height:r.height+36}}")
        async def shot(tag):
            if len(sys.argv) > 1:
                f = f'/tmp/_t{len(shots)}.png'; await pg.screenshot(path=f, clip=box); shots.append(f)
        await pg.evaluate("()=>document.querySelector('.skill[data-k=\"0\"]').click()"); await pg.wait_for_timeout(250)
        st = await pg.evaluate("()=>[...document.querySelectorAll('#hand .slot')].map(s=>(s.classList.contains('turnable')?'T':'-')+(s.querySelector('.turnmk')?'↻':''))")
        print('choosing', st)
        if st[:4] != ['T↻', 'T↻', 'T↻', '-']: bad.append(f'turnable marks wrong {st}')
        await shot('aim0'); await pg.wait_for_timeout(850); await shot('aim1')
        el = await pg.query_selector('#hand .slot[data-i="1"]'); await el.evaluate(TAP)
        for t in (90, 160, 450):
            await pg.wait_for_timeout(t); await shot('turn')
        r = await pg.evaluate("()=>({m:PQ.run.hand[1].m,cd:PQ.run.sk[0].cd,turnable:document.querySelectorAll('#hand .turnable').length,fx:document.querySelectorAll('.turnfx').length})")
        print('after', r)
        if r['m'] != 6 or r['cd'] <= 0 or r['turnable']: bad.append(f'after the tap {r}')
        if errs: bad.append(f'errors {errs[:2]}')
        await b.close()
    print('problems', len(bad)); [print(' ', x) for x in bad]
    if shots:
        from PIL import Image
        ims = [Image.open(s) for s in shots]; H = sum(i.height for i in ims) + 12 * (len(ims) - 1)
        out = Image.new('RGB', (ims[0].width, H), (60, 40, 30)); y = 0
        for i in ims: out.paste(i, (0, y)); y += i.height + 12
        out.resize((out.width // 2, out.height // 2)).save(sys.argv[1], quality=88)

asyncio.run(main())
