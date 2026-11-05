# 11/5 手持ちの積み木をタップしたときの紙の点検：敵・装備・金貨・キャンディ・特別な積み木で紙が出る・ふつうの積み木は出ない・もう一度で閉じる・置けない積み木でも出る
# usage: python3 tools/test/slot_paper.py [out.png]   … out.png を渡すと、敵と装備と特別な積み木の紙を並べて1枚に
import asyncio, sys, os
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
TAP = """el=>{const r=el.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2,o={bubbles:true,cancelable:true,clientX:x,clientY:y,pointerId:7,pointerType:'touch',isPrimary:true,button:0};
  el.dispatchEvent(new PointerEvent('pointerdown',{...o,buttons:1}));document.dispatchEvent(new PointerEvent('pointerup',{...o,buttons:0}));}"""
SET = """()=>{PQ.meta.far=5;PQ.newRun();const r=PQ.run;
  r.hand=[{m:5,c:0,e:{k:'foe',t:'bugle',name:'ラッパ兵',hp:4,atk:2,gold:6}},{m:5,c:1,e:{k:'gear',g:'w1'}},{m:5,c:2,e:{k:'coin',v:3}},{m:5,c:3,e:{k:'potion',v:3}},{m:5,c:4,e:null,sp:'spring'},{m:5,c:0,e:null},{m:1,c:1,e:{k:'gear',g:'s1'}}];
  r.handSize=r.hand.length;PQ.render()}"""
BAR = "()=>{const b=document.getElementById('skbar');return b&&!b.hidden?b.innerText.replace(/\\s+/g,' ').trim():''}"
WANT = ['ラッパ兵', '武器', '金貨', 'キャンディ', 'ビヨヨン', '', '防具']

async def main():
    bad = []; shots = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{try{localStorage.clear()}catch(e){}}"); await pg.evaluate(SET); await pg.wait_for_timeout(500)
        for i, w in enumerate(WANT):
            el = await pg.query_selector(f'#hand .slot[data-i="{i}"]'); await el.evaluate(TAP); await pg.wait_for_timeout(300)
            t = await pg.evaluate(BAR); print(i, t[:90])
            if (w and w not in t) or (not w and t): bad.append(f'slot {i}: want {w!r} got {t!r}')
            if len(sys.argv) > 1 and i in (0, 1, 4):
                r = await pg.evaluate("()=>{const b=document.getElementById('skbar').getBoundingClientRect(),h=document.getElementById('hand').getBoundingClientRect();return {x:0,y:Math.round(b.top-8),width:390,height:Math.round(h.bottom-b.top+12)}}")
                f = f'/tmp/_s{i}.png'; await pg.screenshot(path=f, clip=r); shots.append(f)
            el = await pg.query_selector(f'#hand .slot[data-i="{i}"]'); await el.evaluate(TAP); await pg.wait_for_timeout(250)
            t2 = await pg.evaluate(BAR)
            if t2: bad.append(f'slot {i}: the second tap did not close ({t2[:40]})')
        # choose the gear block, then put it down: the paper goes
        el = await pg.query_selector('#hand .slot[data-i="1"]'); await el.evaluate(TAP); await pg.wait_for_timeout(250)
        up = await pg.evaluate("()=>PQ.idOf(2,2)")
        await (await pg.query_selector(f'.cell[data-i="{up}"]')).evaluate(TAP); await pg.wait_for_timeout(1200)
        if await pg.evaluate(BAR): bad.append('the paper stayed after the block went down')
        if errs: bad.append(f'errors {errs[:2]}')
        await b.close()
    print('problems', len(bad)); [print(' ', x) for x in bad]
    if shots:
        from PIL import Image
        ims = [Image.open(x) for x in shots]; H = sum(i.height for i in ims) + 12 * (len(ims) - 1)
        out = Image.new('RGB', (ims[0].width, H), (60, 40, 30)); y = 0
        for i in ims: out.paste(i, (0, y)); y += i.height + 12
        out.resize((out.width // 2, out.height // 2)).save(sys.argv[1], quality=88)

asyncio.run(main())
