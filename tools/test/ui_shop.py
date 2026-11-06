# PATH QUEST: shop checks with seeded meta (python3 tools/test/ui_shop.py)
import asyncio, json, sys
from ui_lib import *

async def shop_state(S):
    return await S.pg.evaluate("()=>({bank:PQ.meta.bank,up:{...PQ.meta.up},own:[...PQ.meta.sk.own],eq:[...PQ.meta.sk.eq],newu:[...(PQ.meta.newu||[])],far:PQ.meta.far})")

async def buy_all(S, far):
    pg = S.pg
    await S.goto(mt=meta(99999, far))
    await pg.evaluate("PQ.showShop('up')"); await pg.wait_for_timeout(200)
    ups = await pg.evaluate("()=>PQ.UPS.map(u=>({k:u.k,deck:!!u.deck,max:u.max,sp:u.sp||null}))")
    for u in ups:
        tab = 'deck' if u['deck'] else 'up'
        await S.click('#tab-' + tab); await pg.wait_for_timeout(120)
        locked = await pg.evaluate("k=>PQ.isLocked('up',k)", u['k'])
        row = await pg.query_selector(f'#sh-{tab} .row-i[data-k="{u["k"]}"]')
        if not row: issue('wrong', f'far={far}: no row for up {u["k"]} in tab {tab}'); continue
        await S.click(f'#sh-{tab} .row-i[data-k="{u["k"]}"]'); await pg.wait_for_timeout(300)
        bank0 = (await shop_state(S))['bank']
        n = 0
        for _ in range(u['max'] + 2):
            btn = await pg.query_selector('#sh-det [data-act="buy"]')
            if not btn: break
            await S.click('#sh-det [data-act="buy"]'); await pg.wait_for_timeout(280); n += 1
        st = await shop_state(S)
        if locked:
            if n or st['up'][u['k']]: issue('進行', f'far={far}: LOCKED up {u["k"]} was buyable (bought {st["up"][u["k"]]})')
            # shopAct path directly
            await pg.evaluate("k=>{const b=document.querySelector('#sh-det');}", u['k'])
            continue
        if st['up'][u['k']] != u['max']: issue('wrong', f'far={far}: up {u["k"]} reached {st["up"][u["k"]]} of {u["max"]} (buy clicks {n})')
        if st['bank'] < 0: issue('wrong', f'bank negative {st["bank"]}')
        # past max: button is MAX/disabled
        extra = await pg.evaluate("()=>[...document.querySelectorAll('#sh-det .dt-btn')].map(b=>b.textContent+':'+b.disabled)")
        if tab == 'up':  # 11/7: a 能力 level stays once bought (no もどす, and an undo from code does nothing)
            if await pg.query_selector('#sh-det [data-act="undo"]'): issue('wrong', f'far={far}: 能力 paper {u["k"]} still has undo')
            await pg.evaluate("()=>{const b=document.createElement('button');b.dataset.act='undo';document.body.appendChild(b);b.click();b.remove()}"); await pg.wait_for_timeout(280)
            st2 = await shop_state(S)
            if st2['up'][u['k']] != u['max'] or st2['bank'] != st['bank']: issue('wrong', f'far={far}: 能力 {u["k"]} undone -> lvl {st2["up"][u["k"]]} bank {st2["bank"]}')
            continue
        # undo all (積み木の箱 only)
        for _ in range(u['max'] + 1):
            ub = await pg.query_selector('#sh-det [data-act="undo"]:not([disabled])')
            if not ub: break
            await S.click('#sh-det [data-act="undo"]'); await pg.wait_for_timeout(280)
        st2 = await shop_state(S)
        if st2['up'][u['k']] != 0 or st2['bank'] != bank0: issue('wrong', f'far={far}: undo of {u["k"]} -> lvl {st2["up"][u["k"]]} bank {st2["bank"]} (want 0/{bank0})')
        # buy again to max and keep, so costs are tested twice
        for _ in range(u['max']):
            await S.click('#sh-det [data-act="buy"]'); await pg.wait_for_timeout(280)
    st = await shop_state(S)
    print(f' far={far}: after buy-all bank={st["bank"]} errs={len(S.errs)}')

async def poor_test(S):
    """bank small: buying must stop, never negative"""
    pg = S.pg
    await S.goto(mt=meta(50, 60))
    await pg.evaluate("PQ.showShop('up')"); await pg.wait_for_timeout(200)
    for _ in range(20):
        await S.click('#sh-up .row-i[data-k="hp"]'); await pg.wait_for_timeout(280)
        if not await S.click('#sh-det [data-act="buy"]'): break
        await pg.wait_for_timeout(280)
    st = await shop_state(S)
    if st['bank'] < 0: issue('wrong', f'poor: bank {st["bank"]}')
    print(' poor bank', st['bank'], 'hp lvl', st['up']['hp'])
    # undo order: buy hp twice then undo -> refund
    # shopAct bypass: directly call via a synthetic button for a locked skill / up
    await S.goto(mt=meta(99999, 0))
    await pg.evaluate("PQ.showShop('skill')"); await pg.wait_for_timeout(200)
    # choose a locked skill, then force-inject a buy button into the det paper
    res = await pg.evaluate("""async()=>{
      const out={};
      const sh=document.getElementById('sh-body');
      const r=sh.querySelector('.sk2.lk');if(!r)return {err:'no locked skill'};
      r.click();await new Promise(x=>setTimeout(x,300));
      const d=document.getElementById('sh-det');
      for(const act of ['buy','set','on','undo']){
        d.insertAdjacentHTML('beforeend','<button class="zz" data-act="'+act+'">z</button>');
        d.querySelector('.zz').click();await new Promise(x=>setTimeout(x,300));d.querySelectorAll('.zz').forEach(e=>e.remove());
      }
      out.sk=PQ.meta.sk;out.bank=PQ.meta.bank;return out}""")
    print(' forced acts on locked skill', json.dumps(res)[:200])
    if res.get('sk') and (len(res['sk']['own']) > 1 or any(x not in (None, 'turn') for x in res['sk']['eq'])):
        issue('wrong', f'forced shopAct on LOCKED skill changed state: {res["sk"]} (act "set" has no own/lock check; UI cannot reach it)')
    await S.goto(mt=meta(99999, 0))
    await pg.evaluate("PQ.showShop('deck')"); await pg.wait_for_timeout(200)
    res = await pg.evaluate("""async()=>{
      const r=document.querySelector('#sh-deck .row-i.lk');if(!r)return {err:'no locked up'};
      r.click();await new Promise(x=>setTimeout(x,300));
      const d=document.getElementById('sh-det');
      d.insertAdjacentHTML('beforeend','<button class="zz" data-act="buy">z</button>');d.querySelector('.zz').click();await new Promise(x=>setTimeout(x,300));
      return {k:r.dataset.k,lv:PQ.meta.up[r.dataset.k],bank:PQ.meta.bank}}""")
    print(' forced buy on locked up', res)
    if res.get('lv'): issue('進行', f'forced buy on locked up {res} succeeded')

async def skills(S):
    pg = S.pg
    await S.goto(mt=meta(99999, 60))
    await pg.evaluate("PQ.showShop('skill')"); await pg.wait_for_timeout(200)
    ids = await pg.evaluate("()=>PQ.SKILL_ID&&Object.keys(PQ.SKILL_ID)")
    for k in ids:
        await S.click(f'#sh-skill .sk2[data-s="{k}"]'); await pg.wait_for_timeout(300)
        await S.click('#sh-det [data-act="buy"]'); await pg.wait_for_timeout(300)
    st = await shop_state(S)
    if len(st['own']) != 12: issue('wrong', f'skills owned {len(st["own"])} != 12')
    # set all -> swap flow
    for k in ids:
        await S.click(f'#sh-skill .sk2[data-s="{k}"]'); await pg.wait_for_timeout(300)
        if await S.click('#sh-det [data-act="set"]'): await pg.wait_for_timeout(300)
    st = await shop_state(S); print(' eq after set all', st['eq'])
    if None in st['eq']: issue('wrong', 'slots not full after set all')
    # swap flow: select a not-set skill, set -> asks which peg
    other = [k for k in ids if k not in st['eq']][0]
    await S.click(f'#sh-skill .sk2[data-s="{other}"]'); await pg.wait_for_timeout(300)
    await S.click('#sh-det [data-act="set"]'); await pg.wait_for_timeout(300)
    sw = await pg.evaluate("()=>({swap:!!document.querySelector('.pegs.swap'),foot:document.querySelector('#sh-det .note')?.textContent})")
    print(' swap mode', sw)
    if not sw['swap']: issue('wrong', 'swap mode did not start with 3 full slots')
    await S.click('#sh-skill .peg[data-peg="1"]'); await pg.wait_for_timeout(300)
    st2 = await shop_state(S)
    if st2['eq'][1] != other or other not in st2['eq'] or len(set(st2['eq'])) != 3: issue('wrong', f'swap result {st2["eq"]} want {other} at 1')
    # swap with a skill that is already set (in slot 0) -> move to slot 2
    sk0 = st2['eq'][0]
    await S.click(f'#sh-skill .sk2[data-s="{sk0}"]'); await pg.wait_for_timeout(300)
    det = await pg.evaluate("()=>[...document.querySelectorAll('#sh-det [data-act]')].map(b=>b.dataset.act)"); print(' det acts for set skill', det)
    # swap then cancel
    await S.click('#sh-det [data-act="unset"]'); await pg.wait_for_timeout(300)
    st3 = await shop_state(S)
    if st3['eq'][0] is not None: issue('wrong', 'unset failed')
    # tap a different tab during swap; swap must reset
    await S.click(f'#sh-skill .sk2[data-s="{[k for k in ids if k not in st3["eq"]][0]}"]'); await pg.wait_for_timeout(300)
    await S.click('#sh-det [data-act="set"]'); await pg.wait_for_timeout(300)  # fills the empty slot
    # make full again then start swap and press cancel
    other2 = [k for k in ids if k not in (await shop_state(S))['eq']][0]
    await S.click(f'#sh-skill .sk2[data-s="{other2}"]'); await pg.wait_for_timeout(300)
    await S.click('#sh-det [data-act="set"]'); await pg.wait_for_timeout(300)
    await S.click('#sh-det [data-act="cancel"]'); await pg.wait_for_timeout(300)
    if await pg.evaluate("()=>!!document.querySelector('.pegs.swap')"): issue('wrong', 'cancel did not end swap')
    # 11/7: a skill paper has no もどす
    if await pg.query_selector('#sh-det [data-act="undo"]'): issue('wrong', 'skill paper still has undo')
    # swap mode then tab change
    await S.click(f'#sh-skill .sk2[data-s="{other2}"]'); await pg.wait_for_timeout(300)
    await S.click('#sh-det [data-act="set"]'); await pg.wait_for_timeout(300)
    await S.click('#tab-gear'); await pg.wait_for_timeout(200); await S.click('#tab-skill'); await pg.wait_for_timeout(200)
    if await pg.evaluate("()=>!!document.querySelector('.pegs.swap')"): issue('wrong', 'swap mode survived tab change')
    # leave and come back: duplicates in eq?
    st = await shop_state(S)
    if len([x for x in st['eq'] if x]) != len(set(x for x in st['eq'] if x)): issue('wrong', f'dup in eq {st["eq"]}')
    # 11/7: a skill just bought stays learned (no もどす on the paper, and an undo from code does nothing)
    await S.goto(mt=meta(99999, 60))
    await pg.evaluate("PQ.showShop('skill')"); await pg.wait_for_timeout(200)
    await S.click('#sh-skill .sk2[data-s="cannon"]'); await pg.wait_for_timeout(300)
    if await pg.query_selector('#sh-det [data-act="undo"]'): issue('wrong', 'unbought skill paper has undo')
    await S.click('#sh-det [data-act="buy"]'); await pg.wait_for_timeout(300)
    await S.click('#sh-det [data-act="set"]'); await pg.wait_for_timeout(300)
    if await pg.query_selector('#sh-det [data-act="undo"]'): issue('wrong', 'bought skill paper has undo')
    bank1 = (await shop_state(S))['bank']
    await pg.evaluate("()=>{const b=document.createElement('button');b.dataset.act='undo';document.body.appendChild(b);b.click();b.remove()}"); await pg.wait_for_timeout(300)
    st = await shop_state(S); print(' bought+set+undo', st['own'], st['eq'], st['bank'])
    if 'cannon' not in st['own'] or 'cannon' not in st['eq'] or st['bank'] != bank1: issue('wrong', f'skill undone: {st}')

async def gear(S):
    pg = S.pg
    g = meta(99999, 60)
    ids = ['c1', 's3']
    allg = await (await S.goto(mt=meta())).evaluate("()=>PQ.meta.gear&&1")
    gl = await S.pg.evaluate("()=>{const o=[];for(const t of document.querySelectorAll('x'))o.push(1);return typeof GEAR}")
    print(' GEAR visible?', gl)

async def main():
    S = await Sess().start()
    try:
        for far in (0, 12, 25, 60): await buy_all(S, far)
        await poor_test(S)
        await skills(S)
    finally:
        print('ERRS', S.errs[:10]); 
        await S.stop()
    print('\nISSUES'); [print(i) for i in ISSUES]
asyncio.run(main())
