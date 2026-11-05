# 騎士くんの動きのコマ撮り：ポーズの切りかわり（剣・盾・ばんざい）と歩き。1枚にならべて保存
import asyncio,os,sys
from playwright.async_api import async_playwright
from PIL import Image
URL='file://'+os.path.abspath(os.path.join(os.path.dirname(__file__),'../../games/path-quest/index.html'))+'#fxtest'
OUT=sys.argv[1] if len(sys.argv)>1 else 'motion.png'
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=await b.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto(URL);await pg.wait_for_timeout(700)
    await pg.evaluate("async()=>{PQ.newRun();await new Promise(f=>setTimeout(f,400));PQ.jump(3)}");await pg.wait_for_timeout(600)
    box=await pg.evaluate("(()=>{const r=document.querySelector('.hero').getBoundingClientRect();return [r.x,r.y,r.width,r.height]})()")
    x,y,w,h=box;clip={'x':x-w*.6,'y':y-h*.6,'width':w*2.2,'height':h*1.9}
    rows=[]
    for name,js in [('swing',"PQ.heroPose('swing',400,false)"),('block',"PQ.heroPose('block',400,true)"),('cheer',"PQ.heroPose('cheer',500)")]:
      await pg.evaluate("PQ.heroPose('front',0)");await pg.wait_for_timeout(300)
      fr=[]
      await pg.evaluate(js)
      for k in range(6):
        fr.append(await pg.screenshot(clip=clip,animations='allow'));await pg.wait_for_timeout(35)
      rows.append(fr)
    await pg.evaluate("document.querySelector('.hero').classList.add('walk')")
    fr=[]
    for k in range(6):
      fr.append(await pg.screenshot(clip=clip,animations='allow'));await pg.wait_for_timeout(55)
    rows.append(fr)
    print('errors',errs[:3]);await b.close()
  import io
  ims=[[Image.open(io.BytesIO(f)) for f in r] for r in rows];W,H=ims[0][0].size
  sheet=Image.new('RGB',(W*6,H*len(ims)),'white')
  for j,r in enumerate(ims):
    for i,im in enumerate(r):sheet.paste(im,(i*W,j*H))
  sheet.thumbnail((1400,1400));sheet.save(OUT)
asyncio.run(main())
