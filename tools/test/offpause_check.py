# 11/6 見えないところで止めた動きが、見えるところでは全部動いているかの点検（歩いてのぼりながら、毎回）
# usage: python3 tools/test/offpause_check.py [steps]
import asyncio, sys, os, random
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'bot.py'), encoding='utf-8').read()
exec(src[:src.index('async def main')].replace('GAMES = int', 'GAMES = 1 or int').replace('STEPS = int', 'STEPS = 1 or int'))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
CHECK = """()=>{const v=document.getElementById('view').getBoundingClientRect();let seenPaused=0,offRun=0,offPaused=0,on=0;
  for(const a of document.getElementById('board').getAnimations({subtree:true})){if(!(a instanceof CSSAnimation)||a.effect.getTiming().iterations!==Infinity)continue;
    const r=a.effect.target.getBoundingClientRect(),inView=r.bottom>v.top&&r.top<v.bottom;
    if(inView){on++;if(a.playState==='paused')seenPaused++}else{if(a.playState==='paused')offPaused++;else offRun++}}
  return {on,seenPaused,offPaused,offRun}}"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        ctx = await b.new_context(viewport={'width': 412, 'height': 915}, device_scale_factor=1, has_touch=True)
        await ctx.add_init_script("try{localStorage.clear();localStorage.setItem('pathquest.meta.v1',JSON.stringify({bank:0,best:12,far:12,seen:1,up:{hp:3,atk:3},sk:{own:['turn'],eq:['turn',null,null]}}))}catch(e){}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(600)
        await tap(pg, '#t-new'); await pg.wait_for_timeout(500)
        await pg.evaluate("()=>{PQ.run.maxHp=PQ.run.hp=99999;PQ.run.atk=999}")
        rnd = random.Random(2); bad = 0; steps = 0; tot = [0, 0, 0]
        while steps < N:
            st = await wait_idle(pg)
            if st['over']: await tap(pg, '#o-again'); await pg.wait_for_timeout(600); await pg.evaluate("()=>{PQ.run.maxHp=PQ.run.hp=99999;PQ.run.atk=999}"); continue
            if st['reward']: await pg.wait_for_timeout(500); await tap(pg, '#r-list .rrow[data-i="0"]'); await pg.wait_for_timeout(100); await tap(pg, '#r-go'); await pg.wait_for_timeout(800); continue
            if not st['run'] or st['busy'] or st['phase'] != 'build': await pg.wait_for_timeout(100); continue
            await pg.wait_for_timeout(300)
            c = await pg.evaluate(CHECK)
            tot[0] += c['on']; tot[1] += c['offPaused']; tot[2] += c['offRun']
            if c['seenPaused']: bad += 1; print('paused in sight at step', steps, c)
            mv = await pg.evaluate(PICK, rnd.random())
            if not mv:
                if st['rolls']: await tap(pg, '#roll'); await pg.wait_for_timeout(300); continue
                await pg.wait_for_timeout(1500); continue
            await tap(pg, f'#hand .slot[data-i="{mv[0]}"]'); await pg.wait_for_timeout(100)
            await tap(pg, f'#board .cell[data-i="{mv[1]}"]'); await pg.wait_for_timeout(150)
            steps += 1
        await b.close()
    print(f'steps {steps}  checks with a paused loop in sight: {bad}  (in sight {tot[0]}, out of sight paused {tot[1]}, out of sight running {tot[2]})  errors {errs[:2]}')

asyncio.run(main())
