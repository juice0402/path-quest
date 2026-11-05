# 11/5 鍵の点検：記録12段のお店（スキル・積み木の箱）と、のぼっている途中の知らせを並べて1枚に
# usage: python3 tools/test/shot_lock.py out.png [order] [meta の上書き JSON]  … order: 並び順だけ（スキル全体・積み木の箱の上と下）
import asyncio, sys, os, json
from playwright.async_api import async_playwright
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
META = {'bank': 480, 'best': 12, 'far': 12, 'seen': 0, 'up': {'hp': 2, 'atk': 1},
        'sk': {'own': ['turn', 'candy'], 'eq': ['turn', 'candy', None]}, 'newu': ['sk:clear', 'sk:rain', 'up:sd']}
if len(sys.argv) > 3: META.update(json.loads(sys.argv[3]))  # 例: '{"far":25,"newu":["sk:cross"]}'
TMP = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), '_lock_%d.png')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, reduced_motion='reduce')
        await ctx.add_init_script("try{localStorage.clear();localStorage.setItem('pathquest.meta.v1',%s)}catch(e){}" % json.dumps(json.dumps(META)))
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(600)
        shots = []
        if len(sys.argv) > 2 and sys.argv[2] == 'order':
            await pg.evaluate("()=>PQ.showShop('skill')"); await pg.wait_for_timeout(400)
            await pg.screenshot(path=TMP % 1); shots.append(TMP % 1)
            await pg.evaluate("()=>PQ.showShop('deck')"); await pg.wait_for_timeout(400)
            await pg.screenshot(path=TMP % 2); shots.append(TMP % 2)
            await pg.evaluate("()=>{const b=document.getElementById('sh-body');b.scrollTop=b.scrollHeight}"); await pg.wait_for_timeout(300)
            await pg.screenshot(path=TMP % 3); shots.append(TMP % 3)
        else:
            # 1: the skill book, a locked one chosen
            await pg.evaluate("()=>PQ.showShop('skill')"); await pg.wait_for_timeout(400)
            await pg.click('.sk2[data-s="cross"]'); await pg.wait_for_timeout(500)
            await pg.screenshot(path=TMP % 1); shots.append(TMP % 1)
            # 2: the toy box, scrolled to the special blocks, a locked one chosen
            await pg.evaluate("()=>PQ.showShop('deck')"); await pg.wait_for_timeout(400)
            await pg.click('.row-i[data-k="sg"]'); await pg.wait_for_timeout(500)
            await pg.evaluate("()=>{const e=document.querySelector('.row-i[data-k=\"sd\"]');e&&e.scrollIntoView({block:'center'})}"); await pg.wait_for_timeout(300)
            await pg.screenshot(path=TMP % 2); shots.append(TMP % 2)
            # 3: on the road, the record passes 20: the note
            await pg.evaluate("()=>{PQ.newRun()}"); await pg.wait_for_timeout(900)
            await pg.evaluate("()=>{PQ.meta.far=19;PQ.meta.newu=[];PQ.opened(19,20)}"); await pg.wait_for_timeout(700)
            await pg.screenshot(path=TMP % 3); shots.append(TMP % 3)
        info = await pg.evaluate("()=>({newu:PQ.meta.newu,lockedSk:Object.keys(PQ.LOCK.sk).filter(k=>PQ.isLocked('sk',k))})")
        await b.close()
    ims = [Image.open(x) for x in shots]
    w = sum(i.width for i in ims) + 40 * (len(ims) - 1); h = max(i.height for i in ims)
    out = Image.new('RGB', (w, h), (60, 40, 30)); x = 0
    for i in ims: out.paste(i, (x, 0)); x += i.width + 40
    out = out.resize((w // 2, h // 2))
    out.save(sys.argv[1], quality=85)
    for s in shots: os.remove(s)
    print('errors', len(errs), errs[:2]); print(info)

asyncio.run(main())
