# 11/5 q はじめての冒険の指の点検：行き止まりになる置き方はささない・上に開く置き方をえらぶ・どこに置いても行き止まりならサイコロをさす・2段で消える
# usage: python3 tools/test/hint_check.py [out.png]   … out.png を渡すと、指がサイコロをさす画面を1枚に
import asyncio, sys, os
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
# the knight at the left edge, 4 steps up; the cells around are cleared; hand = the given exits
SET = """(ms)=>{PQ.meta.far=1;PQ.newRun();const r=PQ.run;r.intro=0;const at=PQ.jump(4,0),R=PQ.rowOf(at);
  for(const [y,x] of [[R+1,0],[R,1],[R+2,0],[R+1,1],[R,2],[R+1,2]]){const c=PQ.cellAt(PQ.idOf(y,x));c.rock=0;c.foe=null;c.tile=null;c.psn=0;c.gem=0;c.coin=0}
  r.hand=ms.map(m=>({m,e:null,c:0}));PQ.render();return at}"""
WHERE = """()=>{const f=document.querySelector('.finger');if(!f)return null;const s=f.closest('.slot'),c=f.closest('.cell');
  return s?'slot'+s.dataset.i:c?'cell'+c.dataset.i:f.closest('#roll')?'roll':'?'}"""
TAP = """el=>{const r=el.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2,o={bubbles:true,cancelable:true,clientX:x,clientY:y,pointerId:7,pointerType:'touch',isPrimary:true,button:0};
  el.dispatchEvent(new PointerEvent('pointerdown',{...o,buttons:1}));document.dispatchEvent(new PointerEvent('pointerup',{...o,buttons:0}));}"""

async def main():
    bad = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
        await ctx.add_init_script("if(!sessionStorage.getItem('i')){try{localStorage.clear()}catch(e){}sessionStorage.setItem('i',1)}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(500)
        await pg.click('#t-new'); await pg.wait_for_timeout(900)
        # 12 = down+left: up it ends at the left edge, right it ends back at the knight → every place ends the way → the die
        at = await pg.evaluate(SET, [12, 12, 12, 12]); await pg.wait_for_timeout(300)
        w = await pg.evaluate(WHERE); print('all dead ends ->', w)
        if w != 'roll': bad.append(f'all dead ends: finger on {w}')
        if not await pg.evaluate("()=>document.getElementById('roll').closest('.open,[open]')!==null||getComputedStyle(document.getElementById('roll')).visibility!=='hidden'"):
            bad.append('the die is hidden')
        if len(sys.argv) > 1: await pg.wait_for_timeout(500); await pg.screenshot(path=sys.argv[1])
        # a dead end and a straight that goes up: the straight
        await pg.evaluate(SET, [12, 5, 12, 12]); await pg.wait_for_timeout(300)
        w = await pg.evaluate(WHERE); print('one way on ->', w)
        if w != 'slot1': bad.append(f'with a way on: finger on {w}')
        await (await pg.query_selector('#hand .slot[data-i="1"]')).evaluate(TAP); await pg.wait_for_timeout(300)
        up = await pg.evaluate("(at)=>PQ.idOf(PQ.rowOf(at)+1,0)", at)
        w = await pg.evaluate(WHERE); print('chosen ->', w)
        if w != f'cell{up}': bad.append(f'after choosing: finger on {w} (want cell{up})')
        # a chosen block that only ends the way: the finger goes back to the good block
        await (await pg.query_selector('#hand .slot[data-i="0"]')).evaluate(TAP); await pg.wait_for_timeout(300)
        w = await pg.evaluate(WHERE); print('bad block chosen ->', w)
        if w != 'slot1': bad.append(f'a dead-end block chosen: finger on {w}')
        # up first: a right turn (up+... ) vs a straight up — 3 = up+right placed right of the knight, 5 = straight up
        await pg.evaluate(SET, [10, 5, 10, 10]); await pg.wait_for_timeout(300)
        w = await pg.evaluate(WHERE); print('up first ->', w)
        if w != 'slot1': bad.append(f'up first: finger on {w}')
        # no reroll left and every place ends the way: no finger on the die
        await pg.evaluate(SET, [12, 12, 12, 12]); await pg.evaluate("()=>{PQ.run.rolls=0;PQ.render()}"); await pg.wait_for_timeout(200)
        w = await pg.evaluate(WHERE); print('no rerolls ->', w)
        if w == 'roll': bad.append('finger on an empty die')
        # 2 steps: no finger
        await pg.evaluate(SET, [5, 5, 5, 5]); await pg.evaluate("()=>{PQ.meta.far=2;PQ.render()}"); await pg.wait_for_timeout(200)
        w = await pg.evaluate(WHERE)
        if w: bad.append(f'finger after 2 steps: {w}')
        if errs: bad.append(f'errors {errs[:2]}')
        await b.close()
    print('problems', len(bad)); [print(' ', x) for x in bad]

asyncio.run(main())
