# 11/5 盤面のものをタップしたときの紙の点検：家（障害物）・かべ職人のかべ・大将の柵・毒・ビー玉・金貨・のせた装備・特別な積み木で紙が出る・
# 空き地とスタートは出ない・もう一度で閉じる・持っているもの（幽霊の積み木・おかたづけ）だけ書く・積み木をえらんでいても前の空き地には置ける
# usage: python3 tools/test/board_paper.py [out.png]   … out.png を渡すと、全部の紙を並べて1枚に
import asyncio, sys, os
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
TAP = """el=>{const r=el.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2,o={bubbles:true,cancelable:true,clientX:x,clientY:y,pointerId:7,pointerType:'touch',isPrimary:true,button:0};
  el.dispatchEvent(new PointerEvent('pointerdown',{...o,buttons:1}));document.dispatchEvent(new PointerEvent('pointerup',{...o,buttons:0}));}"""
# the start is row 1 col 2; the way up (row 2 col 2) stays open
SET = """(m)=>{PQ.meta.far=5;if(m)PQ.meta.up.sg=1;PQ.newRun();const r=PQ.run;r.intro=0;r.sk=m?[{id:'clear',cd:0},{id:'magnet',cd:0},null]:[null,null,null];r.hand[0]={m:5,c:0,e:null};
  const R=r.rows;[[2,0],[2,1],[2,2],[2,3],[2,4],[3,0],[3,1],[3,2],[3,3],[3,4],[3,5]].forEach(([y,x])=>Object.assign(R[y][x],{rock:0,foe:null,psn:0,gem:0,coin:0,tile:null}));R[2][0].tile={m:5,c:1,e:{k:'gear',g:'w1'}};R[2][4].tile={m:5,c:0,e:null,sp:'hammer'};
  R[3][0].rock=1;R[3][4].rock=3;R[3][1].foe=null;R[3][2].psn=2;R[3][3].gem=7;R[3][5].rock=0;R[3][5].coin=4;
  R[4].forEach(c=>{c.rock=2;c.foe=null});R[2][1].tile=null;R[2][1].rock=0;R[2][1].psn=0;R[2][1].gem=0;R[2][1].coin=0;R[2][1].foe=null;
  R[2][3].tile=null;R[2][3].rock=0;R[2][3].gem=3;R[2][3].foe=null;
  PQ.render()}"""
BAR = "()=>{const b=document.getElementById('skbar');return b&&!b.hidden?b.innerText.replace(/\\s+/g,' ').trim():''}"
SIZE = """()=>{const b=document.getElementById('skbar'),r=b.getBoundingClientRect();return {h:Math.round(r.height),top:Math.round(r.top)}}"""
# (row, col, want in the paper, must not be in it)
CASES = [((3, 0), '家', None), ((3, 4), 'かべ職人のかべ', None), ((4, 0), '大将の柵', None), ((3, 2), '毒の水たまり', None),
         ((3, 3), 'ビー玉', None), ((3, 5), '金貨', None), ((2, 0), '武器', None), ((2, 4), 'ハンマーの積み木', None),
         ((1, 2), '', None), ((2, 1), '', None)]

async def run(pg, more, bad, shots, w):
    await pg.evaluate(SET, more); await pg.wait_for_timeout(500)
    for (r, k), want, _ in CASES:
        i = await pg.evaluate(f"()=>PQ.idOf({r},{k})")
        el = await pg.query_selector(f'.cell[data-i="{i}"]')
        if not el: bad.append(f'{w} {more}: no panel {r},{k}'); continue
        await el.evaluate(TAP); await pg.wait_for_timeout(250)
        t = await pg.evaluate(BAR)
        if (want and want not in t) or (not want and t): bad.append(f'{w} {more}: {r},{k}: want {want!r} got {t!r}')
        if t:
            fs = await pg.evaluate(f"()=>!!document.querySelector('.cell.fsel[data-i=\"{i}\"]')")
            if not fs: bad.append(f'{w} {more}: {r},{k}: no frame on the panel')
            z = await pg.evaluate(SIZE); print(w, more, (r, k), z, t[:70])
            if z['h'] > 120: bad.append(f'{w} {more}: {r},{k}: the paper is too tall {z}')
            if shots is not None:
                f = f'/tmp/_b{w}_{int(more)}_{r}{k}.png'; await pg.screenshot(path=f, clip={'x': 0, 'y': z['top'] - 6, 'width': w, 'height': z['h'] + 12}); shots.append(f)
            el = await pg.query_selector(f'.cell[data-i="{i}"]'); await el.evaluate(TAP); await pg.wait_for_timeout(200)
            if await pg.evaluate(BAR): bad.append(f'{w} {more}: {r},{k}: the second tap did not close')
    t = ''
    if more:  # what this knight has is told; without them it is not
        i = await pg.evaluate("()=>PQ.idOf(3,0)"); await (await pg.query_selector(f'.cell[data-i="{i}"]')).evaluate(TAP); await pg.wait_for_timeout(200)
        t = await pg.evaluate(BAR)
        for x in ['幽霊なら', 'おかたづけ']:
            if x not in t: bad.append(f'{w}: the house paper lacks {x}: {t!r}')
        if 'ハンマー' in t: bad.append(f'{w}: hammer told though not bought: {t!r}')
        await (await pg.query_selector(f'.cell[data-i="{i}"]')).evaluate(TAP); await pg.wait_for_timeout(200)
    else:
        i = await pg.evaluate("()=>PQ.idOf(3,0)"); await (await pg.query_selector(f'.cell[data-i="{i}"]')).evaluate(TAP); await pg.wait_for_timeout(200)
        t = await pg.evaluate(BAR)
        for x in ['幽霊', 'ハンマー', 'おかたづけ']:
            if x in t: bad.append(f'{w}: {x} told without having it: {t!r}')
        await (await pg.query_selector(f'.cell[data-i="{i}"]')).evaluate(TAP); await pg.wait_for_timeout(200)
    # a chosen block still goes down on the open panel in front
    up = await pg.evaluate("()=>PQ.idOf(2,2)")
    k = 0  # a straight block (set above)
    if k >= 0:
        await (await pg.query_selector(f'#hand .slot[data-i="{k}"]')).evaluate(TAP); await pg.wait_for_timeout(200)
        await (await pg.query_selector(f'.cell[data-i="{up}"]')).evaluate(TAP); await pg.wait_for_timeout(1300)
        laid = await pg.evaluate(f"()=>!!PQ.run.rows[2][2].tile")
        if not laid: bad.append(f'{w} {more}: the chosen block did not go down on the open panel')

async def main():
    bad = []; cols = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        for w, h in [(390, 844)]:
            for more in [False, True]:
                pg = await b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2); errs = []
                pg.on('pageerror', lambda e: errs.append(str(e)))
                await pg.goto(URL); await pg.wait_for_timeout(400)
                await pg.evaluate("()=>{try{localStorage.clear()}catch(e){}}")
                shots = [] if len(sys.argv) > 1 else None
                await run(pg, more, bad, shots, w)
                if errs: bad.append(f'{w} {more}: errors {errs[:2]}')
                if shots: cols.append(shots)
                await pg.close()
        await b.close()
    print('problems', len(bad)); [print(' ', x) for x in bad]
    if len(sys.argv) > 1 and cols:
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

if __name__ == "__main__":
    asyncio.run(main())
