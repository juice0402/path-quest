# PATH QUEST: lock order / NEW / marks / gear / deck effects  (python3 tools/test/ui_shop2.py)
import asyncio, json
from ui_lib import *

ORDER = """(tab)=>{const sel=tab==='skill'?'#sh-skill .sk2':'#sh-deck .row-i';return [...document.querySelectorAll(sel)].map(e=>({k:e.dataset.s||e.dataset.k,lk:e.classList.contains('lk'),nw:!!e.querySelector('.nw'),txt:e.innerText.replace(/\\s+/g,' ').slice(0,30)}))}"""

async def lock_flow(S):
    pg = S.pg
    await S.goto(mt=meta(500, 0))
    await pg.evaluate("PQ.showShop('skill')"); await pg.wait_for_timeout(250)
    o = await pg.evaluate(ORDER, 'skill'); print(' far0 skill order', [(x['k'], 'L' if x['lk'] else '') for x in o])
    lk = await pg.evaluate("()=>PQ.LOCK")
    # open before locked; within locked smallest step first (11/6 a)
    seen_lock = False; prev = 0
    for x in o:
        if x['lk']:
            seen_lock = True; st = lk['sk'][x['k']]
            if st < prev: issue('wrong', f'locked skills not smallest-first: {x["k"]} {st} after {prev}')
            prev = st
            if x['txt'].find('？？？') < 0: issue('visual', f'locked skill label shows name: {x["txt"]}')
        elif seen_lock: issue('wrong', f'open skill {x["k"]} after locked ones')
    # locked: tapping shows silhouette paper; buy button absent
    lkk = [x['k'] for x in o if x['lk']][0]
    await S.click(f'#sh-skill .sk2[data-s="{lkk}"]'); await pg.wait_for_timeout(300)
    d = await pg.evaluate("()=>document.getElementById('sh-det').innerText.replace(/\\s+/g,' ')+'|btn:'+document.querySelectorAll('#sh-det button').length")
    print(' locked paper:', d)
    # go to home, play: reach step 10
    await S.click('#sh-go'); await pg.wait_for_timeout(500)
    await pg.evaluate("PQ.jump(8)"); await pg.wait_for_timeout(200)
    for _ in range(10):
        st = await S.idle(); await place_one(S); await pg.wait_for_timeout(100)
        await S.idle()
        if await S.vis('s-reward'): break
        if await S.vis('s-over'): break
    far = await pg.evaluate("PQ.meta.far"); nu = await pg.evaluate("[...(PQ.meta.newu||[])]")
    print(' after step: far', far, 'newu', nu, 'reward', await S.vis('s-reward'))
    if far >= 10:
        want = {'sk:clear', 'sk:rain', 'up:sd'}
        if set(nu) != want: issue('wrong', f'newu after far={far}: {nu} want {sorted(want)}')
    else: issue('wrong', 'could not reach step 10 in lock test')
    toasts = await pg.evaluate("()=>[...document.querySelectorAll('.note,.toast,#notes *')].map(e=>e.innerText).filter(Boolean).join('|')")
    print(' notes:', toasts[:200])
    # finish run, result dot, shop marks
    await pg.evaluate("PQ.gameOver('quit')"); await pg.wait_for_timeout(400)
    dot = await pg.evaluate("()=>!document.getElementById('o-dot').hidden")
    if not dot: issue('wrong', 'result screen: 強化 dot hidden although NEW items exist')
    await S.click('#o-shop'); await pg.wait_for_timeout(400)
    marks = await pg.evaluate("()=>['up','gear','skill','deck'].map(t=>{const m=document.querySelector('#tab-'+t+' .mk');return t+':'+m.className+':'+m.textContent})")
    print(' marks', marks)
    if not any(m.startswith('skill:mk new:2') for m in marks): issue('wrong', f'skill tab NEW mark {marks}')  # clear と rain の2つ
    if not any(m.startswith('deck:mk new:1') for m in marks): issue('wrong', f'deck tab NEW mark {marks}')
    # tab order for skills: open, NEW, locked
    await S.click('#tab-skill'); await pg.wait_for_timeout(300)
    o = await pg.evaluate(ORDER, 'skill'); print(' order', [(x['k'], 'L' if x['lk'] else 'N' if x['nw'] else '') for x in o])
    ks = ['L' if x['lk'] else 'N' if x['nw'] else 'O' for x in o]
    if ''.join(ks) != ''.join(sorted(ks, key={'O': 0, 'N': 1, 'L': 2}.get)): issue('wrong', f'skill order not open->NEW->locked: {ks}')
    # tap NEW -> clears; order stays until shop closes
    await S.click('#sh-skill .sk2[data-s="clear"]'); await pg.wait_for_timeout(300)
    nu = await pg.evaluate("[...(PQ.meta.newu||[])]")
    if 'sk:clear' in nu: pass
    else: print(' NEW cleared after tap ok')
    if 'sk:clear' in nu: issue('wrong', 'NEW not cleared after tap')
    o2 = await pg.evaluate(ORDER, 'skill'); 
    if [x['k'] for x in o2] != [x['k'] for x in o]: issue('wrong', 'order jumped right after tapping NEW')
    mk = await pg.evaluate("()=>document.querySelector('#tab-skill .mk').textContent+'/'+document.querySelector('#tab-skill .mk').className"); print(' skill mark after tap', mk)
    # buy NEW clear skill; far stays
    for t in ('deck',):
        await S.click('#tab-' + t); await pg.wait_for_timeout(300)
        o = await pg.evaluate(ORDER, t); print(' deck order', [(x['k'], 'L' if x['lk'] else 'N' if x['nw'] else '') for x in o])
        await S.click('#sh-deck .row-i[data-k="sd"]'); await pg.wait_for_timeout(300)
        n0 = await pg.evaluate("[...(PQ.meta.newu||[])]"); print(' newu after tapping sd', n0)
    # leave shop and re-enter: NEW gone
    await S.click('#sh-back'); await pg.wait_for_timeout(300)
    await pg.evaluate("PQ.showShop('skill')"); await pg.wait_for_timeout(300)
    o = await pg.evaluate(ORDER, 'skill')
    print(' re-enter order', [(x['k'], 'L' if x['lk'] else 'N' if x['nw'] else '') for x in o])
    # bought skill stays open although record lower? (record can't go down, but meta.far reset)
    await S.goto(mt=meta(500, 0, sk=dict(own=['turn', 'treasure'], eq=['turn', None, None])))
    await pg.evaluate("PQ.showShop('skill')"); await pg.wait_for_timeout(250)
    o = await pg.evaluate(ORDER, 'skill')
    tr = [x for x in o if x['k'] == 'treasure'][0]
    if tr['lk']: issue('wrong', 'owned skill shown as locked at far 0')
    # newu holding stale ids / done-ids garbage
    await S.goto(mt=meta(500, 0, newu=['sk:nonexist', 'up:zzz', 'sk:cannon']))
    await pg.evaluate("PQ.showShop('skill')"); await pg.wait_for_timeout(250)
    print(' stale newu ->', await pg.evaluate("[...(PQ.meta.newu||[])]"))
    # far crossing multiple lock levels at once (0 -> 60) + gear etc
    await S.goto(mt=meta(500, 0))
    await pg.evaluate("()=>{const a=PQ.meta.far;PQ.meta.far=60;PQ.opened(a,60)}"); 
    nu = await pg.evaluate("[...(PQ.meta.newu||[])]"); print(' opened(0,60):', nu)
    if len(nu) != 13: issue('wrong', f'opened(0,60) gave {len(nu)} NEW (expected 7 sk +6 up =13)')

async def gear_test(S):
    pg = S.pg
    ids = ['w1', 'w2', 's1', 'c1']
    await S.goto(mt=meta(100, 30, gear=dict(own=ids, eq={}), newg=['w1', 'c1']))
    await pg.evaluate("PQ.showShop('gear')"); await pg.wait_for_timeout(300)
    marks = await pg.evaluate("document.querySelector('#tab-gear .mk').textContent"); print(' gear mark', marks)
    if marks != '2': issue('wrong', f'gear tab mark {marks} want 2')
    for g in ['w1']:
        await S.click(f'#sh-gear .gi2[data-g="{g}"]'); await pg.wait_for_timeout(300)
        await S.click('#sh-det [data-act="on"]'); await pg.wait_for_timeout(300)
        eq = await pg.evaluate("({...PQ.meta.gear.eq})"); print(' eq', eq)
        if eq.get('wpn') != 'w1': issue('wrong', 'gear on failed')
        await S.click('#sh-det [data-act="off"]'); await pg.wait_for_timeout(300)
        if (await pg.evaluate("PQ.meta.gear.eq.wpn")) is not None: issue('wrong', 'gear off failed')
    # locked (not owned) gear 'on' forced
    await S.click('#sh-gear .gi2.lock'); await pg.wait_for_timeout(300)
    r = await pg.evaluate("""async()=>{const d=document.getElementById('sh-det');d.insertAdjacentHTML('beforeend','<button class=zz data-act=on>z</button>');d.querySelector('.zz').click();await new Promise(x=>setTimeout(x,300));return {...PQ.meta.gear.eq}}""")
    print(' forced on for unowned', r)
    if any(r.get(k) for k in ('wpn',)) and r.get('wpn') not in ('w1',None): issue('wrong', f'unowned gear equipped {r}')
    # gear equipped goes into the run
    await S.click(f'#sh-gear .gi2[data-g="w2"]'); await pg.wait_for_timeout(300)
    await S.click('#sh-det [data-act="on"]'); await pg.wait_for_timeout(300)
    await S.click('#sh-go'); await pg.wait_for_timeout(500)
    atk = await pg.evaluate("PQ.run.atk"); print(' atk with w2', atk)
    # corrupted gear own
    await S.goto(mt=meta(100, 0, gear=dict(own=['bogus', 'w1'], eq=dict(wpn='bogus', shd='w1'))))
    print(' gear bogus ->', await pg.evaluate("JSON.stringify(PQ.meta.gear)"))

async def deck_test(S):
    pg = S.pg
    for lv in (1, 2):
        await S.goto(mt=meta(0, 60, up=dict(ds=lv)))
        await pg.wait_for_timeout(200)
        await S.click('#t-new'); await pg.wait_for_timeout(500)
        n = await pg.evaluate("PQ.run.hand.filter(t=>t.m===15).length"); print(f' ds={lv}: crosses in hand {n} of {await pg.evaluate("PQ.run.hand.length")}')
        if n < lv: issue('wrong', f'はじめの十字 level {lv}: only {n} crosses')
        dom = await pg.evaluate("document.querySelectorAll('#hand .slot').length")
    # special blocks: fraction by level
    kinds = ['ghost', 'spring', 'gold', 'hammer', 'heal', 'guard']
    keys = {'ghost': 'sg', 'spring': 'sj', 'gold': 'sm', 'hammer': 'sh', 'heal': 'sr', 'guard': 'sd'}
    await S.goto(mt=meta(0, 60)); 
    for kind in kinds:
        res = []
        for lv in (0, 1, 3):
            await S.goto(mt=meta(0, 60, up={keys[kind]: lv}))
            await S.click('#t-new'); await pg.wait_for_timeout(300)
            r = await pg.evaluate("""()=>{let c={},n=2000;for(let i=0;i<n;i++){const t=PQ.QKtile?0:0}return 0}""")
            cnt = await pg.evaluate("""()=>{const o={};for(let i=0;i<1500;i++){PQ.reroll&&0}return 0}""")
            # draw tiles through the real path: newRun hands
            c = await pg.evaluate("""()=>{const o={};for(let i=0;i<400;i++){PQ.newRun();PQ.run.hand.forEach(t=>{const k=t.sp||'-';o[k]=(o[k]||0)+1})}return o}""")
            tot = sum(c.values()); res.append((lv, round(100 * c.get(kind, 0) / tot, 1), {k: v for k, v in c.items() if k not in ('-', kind)}))
        print(f' {kind}:', res)
        if res[0][1] != 0 or any(res[0][2]): issue('wrong', f'{kind}: appears at level 0 {res[0]}')
        if not (res[1][1] > 0 and res[2][1] > res[1][1]): issue('wrong', f'{kind}: lv1 {res[1][1]}% lv3 {res[2][1]}% not increasing')
    # special tile rendering in hand: check the hand shows a label
    await S.goto(mt=meta(0, 60, up=dict(sg=3, sj=3, sm=3, sh=3, sr=3, sd=3)))
    await S.click('#t-new'); await pg.wait_for_timeout(300)
    print(' errs', S.errs[:5])

async def main():
    S = await Sess().start()
    try:
        await lock_flow(S)
        await gear_test(S)
        await deck_test(S)
    finally:
        print('ERRS', S.errs[:10])
        await S.stop()
    print('\nISSUES'); [print(i) for i in ISSUES]
asyncio.run(main())
