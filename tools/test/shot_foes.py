# 11/4 敵と騎士くんの見た目の点検：盤面に敵をならべてスマホの大きさで撮る
# usage: python3 tools/test/shot_foes.py out.png [敵の名前,…]
import asyncio, sys, os
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
OUT = sys.argv[1]
KINDS = (sys.argv[2] if len(sys.argv) > 2 else 'soldier,bugle,cannon,robot,imp,mouse,bear,shroom,duck,frog,peng,hedge').split(',')
POSE = sys.argv[3] if len(sys.argv) > 3 else ''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg = await b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(600)
        await pg.evaluate('()=>{try{localStorage.clear()}catch(e){}PQ.newRun()}'); await pg.wait_for_timeout(900)
        await pg.evaluate('''(kinds)=>{const r=PQ.run,r0=PQ.rowOf(r.at);let k=0;
          for(let dr=1;dr<=4&&k<kinds.length;dr++)for(let c=0;c<6&&k<kinds.length;c++){const i=PQ.idOf(r0+dr,c),x=PQ.cellAt(i);if(!x)continue;
            x.rock=0;x.tile=null;x.foe={k:'foe',t:kinds[k],name:kinds[k],hp:5,atk:2,gold:3,stand:1};k++}
          PQ.render()}''', KINDS)
        if POSE: await pg.evaluate(f'()=>PQ.heroPose("{POSE}")')
        await pg.wait_for_timeout(900)
        await pg.screenshot(path=OUT)
        print('errors', errs[:3])
        await b.close()
asyncio.run(main())
