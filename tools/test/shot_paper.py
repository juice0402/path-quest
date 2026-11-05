# 11/4 敵をタップした紙の点検：敵を1体立たせてタップし、紙を撮る
# usage: python3 tools/test/shot_paper.py out.png kind
import asyncio, sys, os
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
TAP = """el=>{const r=el.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2,o={bubbles:true,cancelable:true,clientX:x,clientY:y,pointerId:7,pointerType:'touch',isPrimary:true,button:0};
  el.dispatchEvent(new PointerEvent('pointerdown',{...o,buttons:1}));document.dispatchEvent(new PointerEvent('pointerup',{...o,buttons:0}));}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg = await b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
        await pg.goto(URL); await pg.wait_for_timeout(500)
        await pg.evaluate('()=>{try{localStorage.clear()}catch(e){}PQ.newRun()}'); await pg.wait_for_timeout(800)
        i = await pg.evaluate('''(t)=>{const r=PQ.run,i=PQ.idOf(PQ.rowOf(r.at)+2,PQ.colOf(r.at)),x=PQ.cellAt(i);x.rock=0;x.tile=null;
          x.foe={k:'foe',t,name:{bugle:'ラッパ兵',imp:'いたずら小僧',skel:'カタカタがいこつ'}[t]||t,hp:4,atk:2,gold:6,stand:1};PQ.render();return i}''', sys.argv[2])
        await pg.wait_for_timeout(600)
        el = await pg.query_selector(f'.cell[data-i="{i}"]'); await el.evaluate(TAP); await pg.wait_for_timeout(500)
        await pg.screenshot(path=sys.argv[1], clip={'x': 0, 'y': 330, 'width': 390, 'height': 514})
        await b.close()
asyncio.run(main())
