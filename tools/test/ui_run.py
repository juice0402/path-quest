# PATH QUEST: screen flow, skills, specials, toys, rewards with real taps  (python3 tools/test/ui_run.py [flow|skills|specials|toys])
import asyncio, json, sys, random
from ui_lib import *
NAN = """()=>{const r=PQ.run;if(!r)return null;const bad=[];for(const k of ['hp','maxHp','atk','def','gold','rolls','top','at','handSize'])if(typeof r[k]!=='number'||!isFinite(r[k]))bad.push(k+'='+r[k]);
  if(r.hp>r.maxHp+1e-9)bad.push('hp>max '+r.hp+'/'+r.maxHp);if(r.hp<0)bad.push('hp<0');if(r.rolls<0)bad.push('rolls<0');
  r.hand.forEach((t,i)=>{if(t&&(typeof t.m!=='number'))bad.push('hand'+i)});
  for(const e of document.querySelectorAll('.hud,#hand,#board'))if(/NaN|undefined|null|Infinity/.test(e.innerText))bad.push('text NaN in '+e.id+e.className);
  return bad}"""
async def check(S, tag):
    bad = await S.pg.evaluate(NAN)
    if bad: issue('error', f'{tag}: {bad}')
    return bad
async def play(S, n, tag='play'):
    done = 0
    for _ in range(n):
        st = await S.idle(9000)
        if st.get('stuck'): issue('進行', f'{tag}: busy stuck {st}'); return done
        sc = await S.screen()
        if sc:
            if 's-reward' in sc: await take_reward(S)
            elif 's-over' in sc: return done
            continue
        ok = await place_one(S)
        if not ok:
            return done
        done += 1; await S.pg.wait_for_timeout(40)
    return done
async def take_reward(S, want=None):
    pg = S.pg
    await pg.wait_for_timeout(120)
    n = await pg.evaluate("document.querySelectorAll('#r-list .rrow').length")
    if not n: issue('error', 'reward sheet with no cards'); await pg.evaluate("PQ.run.rewards=null;PQ.run.phase='build';PQ.render()"); return False
    i = 0
    if want:
        i = await pg.evaluate("w=>{const r=PQ.run.rewards.findIndex(x=>x.id===w);return r<0?0:r}", want)
    await S.click(f'#r-list .rrow[data-i="{i}"]'); await pg.wait_for_timeout(100)
    # go button is guarded by performance.now()<rReady
    for _ in range(30):
        await pg.wait_for_timeout(100)
        if not await pg.evaluate("document.getElementById('r-go').disabled"): 
            await S.click('#r-go'); break
    for _ in range(12):
        await pg.wait_for_timeout(100)
        if not await S.vis('s-reward') or await pg.evaluate("PQ.run&&PQ.run.rewards&&document.getElementById('r-list').classList.contains('picked')===false&&0"): break
    return True

async def flow(S):
    pg = S.pg
    print('== flow')
    await S.goto(mt=meta(300, 12))
    assert await S.screen() == ['s-title'], await S.screen()
    await S.tap('#t-new') if False else await S.click('#t-new'); await pg.wait_for_timeout(500)
    if await S.screen(): issue('wrong', f'after あそぶ sheets {await S.screen()}')
    await pg.evaluate("()=>{PQ.run.maxHp=PQ.run.hp=9999;PQ.run.def=99;PQ.run.atk=99;PQ.render()}")
    n = await play(S, 4, 'flow'); print(' placed', n)
    # input while busy: spam taps during walk
    b = await pg.evaluate(PLACE_PICK)
    if b:
        await pg.evaluate("([j,k])=>PQ.place(j,k)", [b[1], b[0]])
        busy = await pg.evaluate("PQ.busy")
        b2 = await pg.evaluate("()=>{const r=PQ.run,F=PQ.frontier();for(let k=0;k<r.hand.length;k++)for(const j of F.keys())if(r.hand[k]&&PQ.fits(r.hand[k],j,F))return [j,k]}")
        before = await pg.evaluate("JSON.stringify(PQ.run.hand.map(t=>t&&t.m))+PQ.run.at")
        if busy:
            await pg.evaluate("([j,k])=>PQ.place(j,k)", b2 or [0, 0]); await pg.evaluate("PQ.reroll()")
            rolls_busy = await pg.evaluate("PQ.run.rolls")
            q = await S.click('#quit'); 
            sc = await S.screen()
            if 's-quit' in sc: issue('wrong', 'quit sheet opened while busy (walking)')
        await S.idle()
    await check(S, 'flow'); await S.idle(); print(' errs a', S.errs); placed_top = await pg.evaluate('PQ.run&&[PQ.run.top,PQ.run.rolls,PQ.run.hp]')
    # quit sheet: つづける
    await S.click('#quit'); await pg.wait_for_timeout(300)
    if await S.screen() != ['s-quit']: issue('wrong', f'quit tap -> {await S.screen()} head={await pg.evaluate("document.getElementById('o-head').textContent")} top={placed_top}')
    qtxt = await pg.evaluate("document.getElementById('s-quit').innerText.replace(/\\s+/g,' ')"); print(' quit sheet:', qtxt[:120])
    await S.click('#q-no'); await pg.wait_for_timeout(200)
    if await S.screen(): issue('wrong', 'つづける did not close quit sheet')
    # input after closing
    n = await play(S, 1, 'flow2'); 
    await S.idle(); print(' errs b', S.errs)
    # long press quit = go home at once
    el = await pg.query_selector('#quit')
    await pg.evaluate("""el=>{const r=el.getBoundingClientRect(),o={bubbles:true,clientX:r.left+5,clientY:r.top+5,pointerId:3,pointerType:'touch',isPrimary:true};el.dispatchEvent(new PointerEvent('pointerdown',o))}""", el)
    await pg.wait_for_timeout(900)
    sc = await S.screen(); print(' long press ->', sc)
    if 's-over' not in sc: issue('wrong', f'long-press quit did not end the run: {sc}')
    await pg.evaluate("el=>{el.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerId:3,pointerType:'touch'}))}", el)
    await pg.wait_for_timeout(300)
    if 's-over' not in await S.screen(): issue('wrong', f'result screen vanished after the long-press release: {await S.screen()}')
    print(' errs c', S.errs)
    # fresh run, quit through sheet 帰還する
    await S.click('#o-again'); await pg.wait_for_timeout(400)
    await pg.evaluate("()=>{PQ.run.maxHp=PQ.run.hp=9999;PQ.run.def=99;PQ.run.atk=99;PQ.render()}")
    await play(S, 2, 'flow3'); await S.idle()
    await S.click('#quit'); await pg.wait_for_timeout(300); await S.click('#q-yes'); await pg.wait_for_timeout(1500)
    sc = await S.screen(); print(' after 帰還する', sc, await pg.evaluate("document.getElementById('o-head').textContent"))
    if sc != ['s-over']: issue('wrong', f'帰還する -> {sc}')
    if await pg.evaluate("localStorage.getItem('pathquest.run.v3')") : issue('wrong', 'run save remains after 帰還')
    # tap the result to flush animations, then 強化
    await pg.mouse.click(195, 100) if False else None
    await S.click('#o-shop'); await pg.wait_for_timeout(500)
    if await S.screen() != ['s-shop']: issue('wrong', f'強化 -> {await S.screen()}')
    for t in ('up', 'gear', 'skill', 'deck'):
        await S.click('#tab-' + t); await pg.wait_for_timeout(250)
        vis = await pg.evaluate("t=>[...document.querySelectorAll('[role=tabpanel]')].filter(e=>!e.hidden).map(e=>e.id)", t)
        if vis != ['sh-' + t]: issue('wrong', f'tab {t} -> panels {vis}')
        sel = await pg.evaluate("[...document.querySelectorAll('[role=tab]')].filter(e=>e.getAttribute('aria-selected')==='true').map(e=>e.id)")
        if sel != ['tab-' + t]: issue('wrong', f'aria-selected {sel} for {t}')
    # あそぶ from the shop
    await S.click('#sh-go'); await pg.wait_for_timeout(500)
    if await S.screen(): issue('wrong', f'sh-go left sheets {await S.screen()}')
    if not await pg.evaluate("!!PQ.run"): issue('進行', 'あそぶ from the shop did not start a run')
    await pg.evaluate("()=>{PQ.run.maxHp=PQ.run.hp=9999;PQ.run.def=99;PQ.run.atk=99;PQ.render()}")
    await play(S, 2, 'flow4'); await S.idle(); await check(S, 'flow4')
    # result -> home, home -> new
    await pg.evaluate("PQ.gameOver('quit')"); await pg.wait_for_timeout(400)
    await S.click('#o-title'); await pg.wait_for_timeout(300)
    if await S.screen() != ['s-title']: issue('wrong', 'ホーム failed')
    # shop → back (home)
    await S.click('#t-new'); await pg.wait_for_timeout(300); await pg.evaluate("PQ.gameOver('quit')"); await pg.wait_for_timeout(300)
    await S.click('#o-shop'); await pg.wait_for_timeout(300); await S.click('#sh-back'); await pg.wait_for_timeout(300)
    if await S.screen() != ['s-title']: issue('wrong', 'shop back failed')
    print(' errs d', S.errs)
    # run ending by HP
    await S.click('#t-new'); await pg.wait_for_timeout(300)
    await pg.evaluate("PQ.run.hp=1;PQ.run.def=0;PQ.render()")
    await pg.evaluate("()=>{PQ.jump(5);const r=PQ.run;const c=PQ.cellAt(PQ.idOf(PQ.rowOf(r.at)+1,PQ.colOf(r.at)));c.tile=null;c.rock=0;c.foe={t:'soldier',hp:999,mhp:999,atk:99,gold:1,name:'x'};PQ.render()}")
    print(' errs e', S.errs)
    ended = False
    for _ in range(12):
        await place_one(S); await S.idle(6000)
        if 's-over' in await S.screen(): ended = True; break
    print(' hp end:', ended, await pg.evaluate("document.getElementById('o-head').textContent"))
    if not ended: issue('wrong', 'could not end a run by HP (test setup?)')
    await S.click('#o-again'); await pg.wait_for_timeout(300)
    # stuck run: every cell ahead is a house, then the reroll leads to the dead end
    await pg.evaluate("()=>{const r=PQ.run;r.maxHp=r.hp=9999;r.rolls=1;r.sk=[null,null,null];for(const j of [...PQ.frontier().keys()]){PQ.cellAt(j).rock=1}PQ.render()}")
    await S.click('#roll'); await pg.wait_for_timeout(300)
    busy1 = await pg.evaluate("PQ.busy")
    await pg.evaluate("PQ.reroll()")  # a second reroll while the stuck timer runs must do nothing
    await pg.wait_for_timeout(1900)
    print(' stuck: busy during wait', busy1, 'screen', await S.screen(), await pg.evaluate("document.getElementById('o-head').textContent"))
    if await S.screen() != ['s-over']: issue('wrong', f'dead end did not end the run: {await S.screen()}')
    # nofit: hand cannot fit but the way is open
    await S.click('#o-again'); await pg.wait_for_timeout(300)
    await pg.evaluate("()=>{const r=PQ.run;r.maxHp=r.hp=9999;r.rolls=0;r.sk=[null,null,null];r.hand=r.hand.map(()=>({m:5,e:null,c:0}));PQ.render()}")
    n = 0
    for _ in range(40):
        ok = await place_one(S); n += ok; await S.idle(5000)
        if 's-over' in await S.screen(): break
    print(' nofit run placed', n, await S.screen(), await pg.evaluate("document.getElementById('o-head').textContent"))
    await check(S, 'flow-end')

async def skills(S):
    pg = S.pg
    print('== skills')
    await S.goto(mt=meta(0, 99))
    ids = await pg.evaluate("Object.keys(PQ.SKILL_ID)")
    groups = [ids[i:i + 3] for i in range(0, 12, 3)]
    for g in groups:
        await S.goto(mt=meta(0, 99, sk=dict(own=ids, eq=g)))
        await S.click('#t-new'); await pg.wait_for_timeout(500)
        await play(S, 3, 'skills-warm')
        for slot, sid in enumerate(g):
            for variant in ('no-target-or-use', 'again-cooldown', 'tapNoTarget'):
                st = await S.idle(); 
                if await S.screen(): break
                errs0 = len(S.errs); S.label = f'{sid}/{variant}'
                d = await pg.evaluate("s=>{const b=document.querySelector('#drawer-in .skill[data-k=\"'+s+'\"]');return !!b}", slot)
                if not d: issue('visual', f'skill button {sid} slot {slot} missing'); break
                await S.click(f'#drawer-in .skill[data-k="{slot}"]'); await pg.wait_for_timeout(150)
                bar = await pg.evaluate("()=>{const b=document.getElementById('skbar');return b.hidden?null:b.innerText.replace(/\\s+/g,' ')}")
                cd = await pg.evaluate("s=>PQ.run.sk[s]&&PQ.run.sk[s].cd", slot)
                if variant == 'no-target-or-use':
                    if bar is None: issue('wrong', f'{sid}: tapping skill shows no bar'); continue
                    kind = await pg.evaluate("s=>PQ.SKILL_ID[s].aim||''", sid)
                    if cd == 0 and not kind:
                        await S.click('#skbar [data-sb="go"]'); await pg.wait_for_timeout(300)
                    elif cd == 0 and kind in ('tile', 'free', 'foe'):
                        tg = await pg.evaluate("k=>PQ.targets(k)", kind)
                        if tg:
                            await S.tap(f'#hand .slot[data-i="{tg[0]}"]'); await pg.wait_for_timeout(300)
                        else: await S.click('#skbar [data-sb="x"]')
                    elif cd == 0 and kind == 'rock':
                        tg = await pg.evaluate("PQ.targets('rock')")
                        if tg: await S.tap(f'#board .cell[data-i="{tg[0]}"]'); await pg.wait_for_timeout(300)
                        else: await S.click('#skbar [data-sb="x"]')
                    else: await S.click('#skbar [data-sb="x"]')
                elif variant == 'again-cooldown':
                    cdn = await pg.evaluate("s=>PQ.run.sk[s].cd", slot)
                    if cdn > 0 and bar and ('あと' not in bar): issue('wrong', f'{sid} on cooldown {cdn} but bar says: {bar}')
                    if cdn > 0 and await pg.query_selector('#skbar [data-sb="go"]'): issue('wrong', f'{sid}: 使う button during cooldown')
                    # force use on cooldown through the API
                    try:
                        before = await pg.evaluate("s=>PQ.run.sk[s].cd", slot)
                        await pg.evaluate("s=>PQ.useSkill(s,-1)", slot)
                        after = await pg.evaluate("s=>PQ.run.sk[s].cd", slot)
                        if before > 0 and after >= before and 0: pass
                    except Exception as e: issue('error', f'{sid}: useSkill on cooldown threw {str(e)[:150]}')
                    await S.click('#skbar [data-sb="x"]')
                else:
                    # tap a non-target slot while aiming
                    await S.click(f'#drawer-in .skill[data-k="{slot}"]'); await pg.wait_for_timeout(120)
                    await S.tap('#hand .slot[data-i="0"]'); await pg.wait_for_timeout(250)
                    await pg.evaluate("document.getElementById('skbar').hidden||document.querySelector('#skbar [data-sb=x]').click()")
                await S.idle()
                if len(S.errs) > errs0: issue('error', f'{sid} {variant}: {S.errs[errs0:]}'); 
                bad = await check(S, f'skill {sid} {variant}')
                # aim state must not stay stuck
            # after use, can we still place?
            await play(S, 2, 'skills-after-' + sid)
        print(' group', g, 'ok; errs', len(S.errs))
        await S.idle(); await S.click('#quit'); await pg.wait_for_timeout(100); await S.click('#q-yes'); await pg.wait_for_timeout(500)
    # skills with no valid target: empty hand, nothing visible
    await S.goto(mt=meta(0, 99, sk=dict(own=ids, eq=['clear', 'bugle', 'treasure'])))
    await S.click('#t-new'); await pg.wait_for_timeout(400)
    for slot in range(3):
        await S.click(f'#drawer-in .skill[data-k="{slot}"]'); await pg.wait_for_timeout(150)
        bar = await pg.evaluate("()=>document.getElementById('skbar').innerText.replace(/\\s+/g,' ')"); print('  no-target bar:', bar)
        await S.click('#skbar [data-sb="x"]')
    await pg.evaluate("()=>{const r=PQ.run;r.hand=r.hand.map(()=>null);PQ.render()}")
    for sid in ids:
        # force the use path with a bad target index / empty hand
        r = await pg.evaluate("""s=>{try{const r=PQ.run;r.sk=[{id:s,cd:0},null,null];PQ.useSkill(0,0);return 'ok'}catch(e){return 'THROW '+e.message}}""", sid)
        if r != 'ok': issue('error', f'useSkill({sid}) with empty hand / target 0: {r}')
        await pg.evaluate("PQ.render()")
    await check(S, 'skills-empty')

async def specials(S):
    pg = S.pg
    print('== specials')
    for sp in ['ghost', 'spring', 'gold', 'hammer', 'heal', 'guard']:
        for dmg in (0, 1):
            await S.goto(mt=meta(0, 99))
            await S.click('#t-new'); await pg.wait_for_timeout(400)
            await pg.evaluate("PQ.jump(5)")
            await pg.evaluate("""([sp,dmg])=>{const r=PQ.run;if(dmg)r.hp=Math.max(1,r.maxHp-5);
              r.hand[0]={m:sp==='spring'?5:15,e:null,c:1,sp};
              // an obstacle just ahead for hammer/ghost
              const a=PQ.rowOf(r.at)+(sp==='spring'?2:1);for(let c=0;c<6;c++){if(sp!=='spring'&&c>3)continue;const x=PQ.cellAt(PQ.idOf(a,c));if(x&&!x.tile){x.rock=1;x.foe=null}}
              window.__rocks=()=>{let n=0;for(let rr=1;rr<=PQ.run.made;rr++)for(let c=0;c<6;c++){const x=PQ.cellAt(PQ.idOf(rr,c));if(x&&x.rock===1)n++}return n};window.__r0=window.__rocks();window.__at0=PQ.run.at;
              PQ.render()}""", [sp, dmg])
            hp0 = await pg.evaluate("PQ.run.hp"); g0 = await pg.evaluate("PQ.run.gold")
            ok = await pg.evaluate("""()=>{const r=PQ.run,F=PQ.frontier(),t=r.hand[0],js=[...F.keys()].concat(F.rock?[...F.rock.keys()]:[]);for(const j of js)if(PQ.fits(t,j,F)){PQ.place(j,0);return [j,PQ.rowOf(j)-PQ.rowOf(r.at)]}return null}""")
            if not ok: issue('wrong', f'special {sp}: no cell fits (rocks all around, F.rock?)'); continue
            st = await S.idle(); 
            if st.get('stuck'): issue('進行', f'special {sp}: busy stuck')
            if not await pg.evaluate("!!PQ.run"): print('   run ended:', await S.screen(), await pg.evaluate("document.getElementById('o-head').textContent")); continue
            info = await pg.evaluate("({rocks0:window.__r0,rocks1:window.__rocks&&window.__rocks(),dr:PQ.rowOf(PQ.run.at)-PQ.rowOf(window.__at0)})"); print('   ', sp, info)
            hp1 = await pg.evaluate("PQ.run&&PQ.run.hp"); g1 = await pg.evaluate("PQ.run&&PQ.run.gold")
            fx = await pg.evaluate("PQ.run&&JSON.stringify(PQ.run.fx)")
            if sp == 'spring':
                fr = await pg.evaluate("()=>{const r=PQ.run;if(!r)return null;const F=PQ.frontier();return [...F.keys()].map(j=>PQ.rowOf(j)-PQ.rowOf(r.at))}"); print('    spring frontier rel rows', fr)
                if fr is not None and 2 not in fr: issue('wrong', f'spring: after standing on the spring no cell 2 rows up in frontier {fr}')
            print(f'  {sp} dmg={dmg} placed at {ok}: hp {hp0}->{hp1} gold {g0}->{g1} fx {fx}')
            if sp == 'gold' and not g1 > g0: issue('wrong', 'gold block gave no gold')
            if sp == 'heal' and dmg and not hp1 > hp0: issue('wrong', 'heal block gave no HP')
            if sp == 'heal' and not dmg: pass
            await check(S, 'special ' + sp)
            for _ in range(2):
                if await S.screen() == ['s-reward']: await take_reward(S)
            await play(S, 2, 'special-after')
    print(' errs', S.errs[:5])

async def toys(S):
    pg = S.pg
    print('== toys/rewards')
    ids = await pg.evaluate("1")
    toyset = [['plane', 'top', 'bomb'], ['boomer', 'bubble', 'bomb'], ['plane', 'bubble', 'boomer']]
    items = await pg.evaluate("()=>{const o=[];return 1}")
    kinds = set()
    for gi, want in enumerate(toyset):
        await S.goto(mt=meta(0, 99))
        await S.click('#t-new'); await pg.wait_for_timeout(400)
        for cyc in range(24):
            await S.idle()
            if 's-over' in await S.screen(): print('  run ended early at cycle', cyc); break
            await pg.evaluate("()=>{PQ.run.hp=PQ.run.maxHp;PQ.run.reward=true;PQ.openReward()}")
            await pg.wait_for_timeout(250)
            if not await S.vis('s-reward'): issue('wrong', 'openReward did not show the sheet'); break
            cards = await pg.evaluate("PQ.run.rewards.map(x=>x.k+':'+(x.id||''))")
            kinds.update(c.split(':')[0] for c in cards)
            it = await pg.evaluate("()=>PQ.run.it||{}")
            pick = None
            for w in want + ['spring', 'block', 'cat', 'dice', 'clover', 'cookie', 'clock', 'honey']:
                if w in [c.split(':')[1] for c in cards]: pick = w; break
            await take_reward(S, pick)
            await pg.wait_for_timeout(150)
            await check(S, f'toy cycle {cyc}')
            # evolution chest
            if await pg.evaluate("PQ.run.it&&Object.keys(PQ.run.it).length"):
                await pg.evaluate("()=>{PQ.run.chest=true;}")
                ev = await pg.evaluate("()=>{try{return PQ.run.chest}catch(e){return 0}}")
        it = await pg.evaluate("()=>({it:PQ.run.it,evo:PQ.run.evo})"); print(f'  group {gi} toys:', json.dumps(it)[:240])
        # chest evolution
        await pg.evaluate("()=>{PQ.run.chest=true;PQ.run.reward=false;PQ.run.power=false;PQ.openReward()}")
        await pg.wait_for_timeout(300)
        if await S.vis('s-reward'):
            cards = await pg.evaluate("PQ.run.rewards.map(x=>x.k+':'+(x.id||''))"); print('  chest cards', cards)
            await take_reward(S)
        # a few steps with those toys: act every step
        await play(S, 8, 'toys-play'); await check(S, 'toys-play')
        # power sheet (dimension)
        await pg.evaluate("()=>{if(PQ.run){PQ.run.power=true;PQ.run.reward=false;PQ.openReward()}}"); await pg.wait_for_timeout(300)
        if await S.vis('s-reward'): 
            kinds.update(c.split(':')[0] for c in await pg.evaluate("PQ.run.rewards.map(x=>x.k+':')"))
            await take_reward(S)
        await check(S, 'power')
    print(' reward kinds seen', sorted(kinds), 'errs', S.errs[:5])

async def main():
    which = sys.argv[1:] or ['flow', 'skills', 'specials', 'toys']
    S = await Sess().start()
    try:
        for w in which:
            try: await globals()[w](S)
            except Exception as e:
                import traceback; traceback.print_exc(); issue('error', f'{w} crashed: {str(e)[:200]}')
            print(' errs so far', S.errs[:6])
    finally:
        await S.stop()
    print('\nISSUES'); [print(i) for i in ISSUES]
if __name__ == "__main__": asyncio.run(main())
