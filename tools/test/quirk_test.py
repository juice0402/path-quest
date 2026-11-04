# 11/4 敵のくせの点検：敵をタップした紙の「戦うと −○」(dmgFor) と、本当に戦ったときに減ったHPが同じかを、種類ごとにためす
# usage: python3 tools/test/quirk_test.py
import asyncio, os, json
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
KINDS = 'soldier bugle cannon robot imp mouse bear shroom duck frog peng hedge skel ghost boss king archer mage clown mason'.split()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg = await b.new_page(viewport={'width': 390, 'height': 844})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(500)
        await pg.evaluate('()=>{const st=window.setTimeout;window.setTimeout=(f,ms,...a)=>st(f,(ms||0)/20,...a)}')
        out = await pg.evaluate('''async(kinds)=>{const res=[];
          for(const t of kinds)for(const [atk,def,ehp,eatk] of [[2,0,9,2],[3,1,14,3],[5,2,30,6]]){
            try{localStorage.clear()}catch(e){};PQ.newRun();await new Promise(f=>setTimeout(f,40));
            const r=PQ.run;r.atk=atk;r.def=def;r.hp=r.maxHp=999;
            const i=PQ.idOf(PQ.rowOf(r.at)+1,PQ.colOf(r.at)),x=PQ.cellAt(i);x.rock=0;x.tile=null;
            const e={k:'foe',t,name:t,hp:ehp,atk:eatk,gold:10,stand:1};if(t==='boss')e.boss=true;if(t==='king'){e.boss=true;e.king=true}
            x.foe=e;PQ.render();
            const want=PQ.dmgFor(e),h0=r.hp,ok=await PQ.battle(e,r.at,i),got=h0-r.hp-(r.pz?0:0);
            res.push([t,atk,def,ehp,eatk,want,got,ok]);
          }
          return res}''', KINDS)
        bad = [x for x in out if x[5] != x[6]]
        for x in out: print(' '.join(map(str, x)), '' if x[5] == x[6] else '  <-- ちがう')
        print('mismatch', len(bad), 'errors', errs[:3])
        await b.close()
asyncio.run(main())
