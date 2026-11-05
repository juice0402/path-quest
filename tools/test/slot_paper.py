# 11/5 手持ちの積み木をタップしたときの紙の点検：敵・装備（まだ／もう持っている）・金貨・キャンディ・特別な積み木で紙が出る・ふつうの積み木は出ない・
# もう一度で閉じる・置けない積み木でも出る・紙の中の絵が大きくならない（スマホの幅と iPad の幅）
# usage: python3 tools/test/slot_paper.py [out.png]   … out.png を渡すと、全部の紙を2つの幅で並べて1枚に
import asyncio, sys, os
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
TAP = """el=>{const r=el.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2,o={bubbles:true,cancelable:true,clientX:x,clientY:y,pointerId:7,pointerType:'touch',isPrimary:true,button:0};
  el.dispatchEvent(new PointerEvent('pointerdown',{...o,buttons:1}));document.dispatchEvent(new PointerEvent('pointerup',{...o,buttons:0}));}"""
SET = """()=>{PQ.meta.far=5;PQ.meta.gear.own=['s1'];PQ.newRun();const r=PQ.run;
  r.hand=[{m:5,c:0,e:{k:'foe',t:'bugle',name:'ラッパ兵',hp:4,atk:2,gold:6}},{m:5,c:1,e:{k:'gear',g:'w1'}},{m:5,c:2,e:{k:'coin',v:3}},{m:5,c:3,e:{k:'potion',v:3}},{m:5,c:4,e:null,sp:'spring'},{m:5,c:0,e:null},{m:1,c:1,e:{k:'gear',g:'s1'}}];
  r.handSize=r.hand.length;PQ.render()}"""
BAR = "()=>{const b=document.getElementById('skbar');return b&&!b.hidden?b.innerText.replace(/\\s+/g,' ').trim():''}"
SIZE = """()=>{const b=document.getElementById('skbar'),r=b.getBoundingClientRect();let big=0;
  b.querySelectorAll('.sb-t svg').forEach(s=>{const q=s.getBoundingClientRect();big=Math.max(big,q.width,q.height)});
  const ic=b.querySelector('.sb-ic').getBoundingClientRect();return {h:Math.round(r.height),big:Math.round(big),ic:Math.round(Math.max(ic.width,ic.height)),top:Math.round(r.top)}}"""
WANT = ['ラッパ兵', '武器', '金貨', 'キャンディ', 'ビヨヨン', '', 'もう持っている']

async def main():
    bad = []; cols = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        for w, h in [(390, 844), (520, 700)]:
            pg = await b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(URL); await pg.wait_for_timeout(400)
            await pg.evaluate("()=>{try{localStorage.clear()}catch(e){}}"); await pg.evaluate(SET); await pg.wait_for_timeout(500)
            shots = []
            for i, want in enumerate(WANT):
                el = await pg.query_selector(f'#hand .slot[data-i="{i}"]'); await el.evaluate(TAP); await pg.wait_for_timeout(300)
                t = await pg.evaluate(BAR)
                if (want and want not in t) or (not want and t): bad.append(f'{w}: slot {i}: want {want!r} got {t!r}')
                if t:
                    z = await pg.evaluate(SIZE); print(w, i, z, t[:60])
                    if z['big'] > 24 or z['ic'] > 50 or z['h'] > 110: bad.append(f'{w}: slot {i}: the paper is too big {z}')
                    if len(sys.argv) > 1:
                        f = f'/tmp/_s{w}_{i}.png'; await pg.screenshot(path=f, clip={'x': 0, 'y': z['top'] - 6, 'width': w, 'height': z['h'] + 12}); shots.append(f)
                el = await pg.query_selector(f'#hand .slot[data-i="{i}"]'); await el.evaluate(TAP); await pg.wait_for_timeout(250)
                if await pg.evaluate(BAR): bad.append(f'{w}: slot {i}: the second tap did not close')
            el = await pg.query_selector('#hand .slot[data-i="1"]'); await el.evaluate(TAP); await pg.wait_for_timeout(250)
            up = await pg.evaluate("()=>PQ.idOf(2,2)")
            await (await pg.query_selector(f'.cell[data-i="{up}"]')).evaluate(TAP); await pg.wait_for_timeout(1200)
            if await pg.evaluate(BAR): bad.append(f'{w}: the paper stayed after the block went down')
            if errs: bad.append(f'{w}: errors {errs[:2]}')
            cols.append(shots); await pg.close()
        await b.close()
    print('problems', len(bad)); [print(' ', x) for x in bad]
    if len(sys.argv) > 1 and cols and cols[0]:
        from PIL import Image
        col_ims = []
        for shots in cols:
            ims = [Image.open(x) for x in shots]; H = sum(i.height for i in ims) + 10 * (len(ims) - 1)
            c = Image.new('RGB', (max(i.width for i in ims), H), (60, 40, 30)); y = 0
            for i in ims: c.paste(i, (0, y)); y += i.height + 10
            col_ims.append(c)
        W = sum(c.width for c in col_ims) + 30; H = max(c.height for c in col_ims)
        out = Image.new('RGB', (W, H), (60, 40, 30)); x = 0
        for c in col_ims: out.paste(c, (x, 0)); x += c.width + 30
        out.resize((W // 2, H // 2)).save(sys.argv[1], quality=88)

asyncio.run(main())
