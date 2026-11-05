# 11/4 敵の待ちの動きの点検：敵をならべて少しずつ撮り、GIF にする
# usage: python3 tools/test/gif_foes.py out.gif
import asyncio, sys, os, io
from playwright.async_api import async_playwright
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
KINDS = 'soldier,bugle,cannon,robot,clown,frog,imp,mouse,bear,shroom,peng,skel'.split(',')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg = await b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=1)
        await pg.goto(URL); await pg.wait_for_timeout(500)
        await pg.evaluate('()=>{try{localStorage.clear()}catch(e){}PQ.newRun()}'); await pg.wait_for_timeout(800)
        await pg.evaluate('''(kinds)=>{const r=PQ.run,r0=PQ.rowOf(r.at);let k=0;
          for(let dr=1;dr<=2;dr++)for(let c=0;c<6&&k<kinds.length;c++){const i=PQ.idOf(r0+dr,c),x=PQ.cellAt(i);if(!x)continue;
            x.rock=0;x.tile=null;x.foe={k:'foe',t:kinds[k],name:kinds[k],hp:5,atk:2,gold:3,stand:1};k++}
          PQ.render()}''', KINDS)
        await pg.wait_for_timeout(700)
        bb = await pg.evaluate('()=>{const r=document.querySelector(".hero").getBoundingClientRect();return [r.top,r.height]}')
        top = max(0, bb[0] - bb[1] * 2.6); clip = {'x': 0, 'y': top, 'width': 390, 'height': bb[1] * 3.4}
        fr = []
        for k in range(26):
            fr.append(Image.open(io.BytesIO(await pg.screenshot(clip=clip))).convert('RGB'))
            await pg.wait_for_timeout(90)
        fr[0].save(sys.argv[1], save_all=True, append_images=fr[1:], duration=110, loop=0, optimize=True)
        print(len(fr), fr[0].size)
        await b.close()
asyncio.run(main())
