# 11/26 Game Center の点検：実績とさいこう記録を、アプリのとき（window.APP_* があるとき）だけ送るか
# usage: python3 tools/test/gc_check.py [out.png]   … out.png を渡すと、アプリのタイトル（ボタンあり）を撮る
#  1 ウェブ（APP_* なし）：エラーなし・タイトルのボタンは出ない・それでも取った実績は手元（pathquest.ach.v1）に残る
#  2 アプリ：前からの記録（55段・スキル3つ・装備10こ・★2）で、開いたときに実績と記録が送られる。サインインのあと（app-gamecenter）にボタンが出て、全部を送りなおす
#  3 冒険の中：おもちゃLv5・大進化・金貨200枚の持ち帰り
#  4 App Store のスクショの場面（#shot=）：実績を取らない・送らない
import asyncio, sys, os, json
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
FILE = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html'))
OUT = sys.argv[1] if len(sys.argv) > 1 else None

META = {'bank': 100, 'far': 55, 'seen': 1, 'up': {'hp': 10}, 'gear': {'own': ['w1', 's1', 'c1', 'w2', 's2', 'c2', 'w3', 's3', 'c3', 'w4'], 'eq': {}},
        'sk': {'own': ['turn', 'cross', 'clear'], 'eq': ['turn', 'cross', 'clear']}}
SEED = "if(!sessionStorage.getItem('g')){try{localStorage.clear();localStorage.setItem('pathquest.meta.v1',%s)}catch(e){}sessionStorage.setItem('g',1)}" % json.dumps(json.dumps(META))
STUB = """window.__gc=[];window.APP_GAMECENTER=false;
window.APP_SCORE=n=>__gc.push('score:'+n);window.APP_ACHIEVE=id=>__gc.push(id);
window.APP_RANKING=()=>__gc.push('open:ranking');window.APP_ACHIEVEMENTS=()=>__gc.push('open:achievements');"""
SIGNIN = "()=>{window.APP_GAMECENTER=true;window.__gc.length=0;window.dispatchEvent(new Event('app-gamecenter'))}"
GOT = "()=>JSON.parse(localStorage.getItem('pathquest.ach.v1')||'[]')"
OPEN = ['path_floor10', 'path_captain', 'path_floor40', 'path_king', 'path_skill3', 'path_up_max', 'path_gear10', 'path_star2']

async def main():
    bad = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])

        # 1 web
        ctx = await b.new_context(viewport={'width': 390, 'height': 844})
        await ctx.add_init_script(SEED)
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(FILE + '#fxtest'); await pg.wait_for_timeout(800)
        got = await pg.evaluate(GOT); hid = await pg.evaluate("()=>document.getElementById('t-gc').hidden")
        print('web', got, 'buttons hidden', hid)
        if not hid: bad.append('web: the buttons show')
        if sorted(got) != sorted(OPEN): bad.append(f'web: kept {got}')
        if errs: bad.append(f'web errors {errs[:2]}')
        await ctx.close()

        # 2 app
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
        await ctx.add_init_script(SEED); await ctx.add_init_script(STUB)
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(FILE + '#fxtest'); await pg.wait_for_timeout(800)
        sent = await pg.evaluate('()=>[...__gc]'); hid = await pg.evaluate("()=>document.getElementById('t-gc').hidden")
        print('app open', sent, 'hidden before sign-in', hid)
        if not hid: bad.append('app: the buttons show before sign-in')
        if sorted(x for x in sent if x.startswith('path_')) != sorted(OPEN) or 'score:55' not in sent: bad.append(f'app open sent {sent}')
        await pg.evaluate(SIGNIN); await pg.wait_for_timeout(300)
        sent = await pg.evaluate('()=>[...__gc]'); hid = await pg.evaluate("()=>document.getElementById('t-gc').hidden")
        print('after sign-in', sent, 'hidden', hid)
        if hid: bad.append('app: no buttons after sign-in')
        if sorted(x for x in sent if x.startswith('path_')) != sorted(OPEN) or 'score:55' not in sent: bad.append(f'sign-in resent {sent}')
        await pg.click('#t-rank'); await pg.click('#t-ach'); await pg.wait_for_timeout(200)
        sent = await pg.evaluate('()=>[...__gc]')
        if 'open:ranking' not in sent or 'open:achievements' not in sent: bad.append(f'buttons do not open {sent}')
        if OUT:
            await pg.wait_for_timeout(1200); await pg.screenshot(path=OUT)
            print('saved', OUT)

        # 3 in a climb
        await pg.evaluate('()=>{__gc.length=0}')
        await pg.click('#t-new'); await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{const r=PQ.run;r.it={plane:4,clover:1};r.rewards=[{k:'it',id:'plane',n:'',s:''}];r.phase='reward';PQ.takeReward(0)}")
        await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{const r=PQ.run;r.rewards=[{k:'evo',id:'plane',n:'',s:''}];r.phase='reward';PQ.takeReward(0)}")
        await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{PQ.run.gold=250;PQ.gameOver('quit')}")
        await pg.wait_for_timeout(500)
        sent = await pg.evaluate('()=>[...__gc]'); got = await pg.evaluate(GOT)
        print('climb', sent)
        for k in ['path_toy_lv5', 'path_evolve', 'path_rich']:
            if k not in sent or k not in got: bad.append(f'climb: {k} not earned')
        if not any(x.startswith('score:') for x in sent): bad.append('no score at the end of the climb')
        if errs: bad.append(f'app errors {errs[:2]}')
        await ctx.close()

        # 4 the screenshot scenes earn nothing
        ctx = await b.new_context(viewport={'width': 390, 'height': 844})
        await ctx.add_init_script("try{localStorage.clear()}catch(e){}"); await ctx.add_init_script(STUB)
        pg = await ctx.new_page()
        await pg.goto(FILE); await pg.evaluate("()=>{location.hash='shot=boss'}"); await pg.wait_for_timeout(2500)
        sent = await pg.evaluate('()=>[...__gc]'); got = await pg.evaluate(GOT)
        print('shot', sent, got)
        if sent or got: bad.append(f'shot scene earned {sent} {got}')
        await ctx.close()
        await b.close()
    print('ISSUES'); [print(' -', x) for x in bad]

asyncio.run(main())
