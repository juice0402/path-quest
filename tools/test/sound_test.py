# 音のたしかめ：曲の書き方のまちがい・効果音ぜんぶ・曲ごとの大きさ（音割れ）・場面ごとの曲の切りかわり
import asyncio,os,json
from playwright.async_api import async_playwright
URL='file://'+os.path.abspath(os.path.join(os.path.dirname(__file__),'../../games/path-quest/index.html'))+'#fxtest'
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--autoplay-policy=no-user-gesture-required'])
    pg=await b.new_page(viewport={'width':390,'height':844})
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
    await pg.goto(URL);await pg.wait_for_timeout(600)
    print('check',await pg.evaluate("PQ.AUD.check()"))
    songs=await pg.evaluate("async()=>{const o={};for(const k of PQ.AUD.songs())o[k]=await PQ.AUD.song1(k,k.length<5&&['win','quit','lose'].includes(k)?4:10);return o}")
    for k,v in songs.items():print('song',k,v)
    fx=await pg.evaluate("async()=>{const o={};for(const n of PQ.AUD.names())o[n]=await PQ.AUD.sfx1(n);return o}")
    loud=sorted(fx.items(),key=lambda kv:-(kv[1] or {}).get('peak',0))
    print('sfx peak max',loud[:4]);print('sfx quiet',[(k,v) for k,v in fx.items() if not v or v['peak']<.02])
    # scenes
    await pg.mouse.click(30,400);await pg.wait_for_timeout(900)
    r=[await pg.evaluate("[PQ.AUD.state,PQ.AUD.song]")]
    await pg.evaluate("async()=>{PQ.newRun();await new Promise(f=>setTimeout(f,300))}");await pg.wait_for_timeout(900)
    r.append(await pg.evaluate("PQ.AUD.song"))
    for st in [18,25,47,55]:
      await pg.evaluate(f"PQ.jump({st})");await pg.wait_for_timeout(700);r.append((st,await pg.evaluate("PQ.AUD.song")))
    await pg.evaluate("()=>PQ.gameOver('quit')");await pg.wait_for_timeout(700);r.append(('over',await pg.evaluate("PQ.AUD.song")))
    await pg.wait_for_timeout(5200);r.append(('after',await pg.evaluate("PQ.AUD.song")))
    print('scenes',r)
    print('errors',errs[:5])
    await b.close()
asyncio.run(main())
