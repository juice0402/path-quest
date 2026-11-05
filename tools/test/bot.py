# PATH QUEST の自動プレイ点検（デバッグ用）。いろいろな手で何度も遊び、エラー・おかしな数字・止まり・残りもの を集める
# usage: python3 tools/test/bot.py [games] [steps] [--motion] [--jump]
#   --motion  ふつうの動き（ないときは動きを減らした設定で早く回す）
#   --jump    ときどき先の次元へとばして、後半の敵・大将・王さまも通る
import asyncio, json, random, sys, time, os
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
GAMES = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 20
STEPS = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 160
MOTION = '--motion' in sys.argv
JUMP = '--jump' in sys.argv
COV = '--cov' in sys.argv  # at the end: the functions that never ran

# in the page: one pointer tap on an element (the same path a finger takes)
TAP = """el=>{const r=el.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2,o={bubbles:true,cancelable:true,clientX:x,clientY:y,pointerId:7,pointerType:'touch',isPrimary:true,button:0};
  el.dispatchEvent(new PointerEvent('pointerdown',{...o,buttons:1}));document.dispatchEvent(new PointerEvent('pointerup',{...o,buttons:0}));}"""
STATE = """()=>{const r=PQ.run,vis=id=>{const e=document.getElementById(id);return !!e&&!e.hidden};
  return {run:!!r,busy:PQ.busy,phase:r&&r.phase,hp:r&&r.hp,max:r&&r.maxHp,gold:r&&r.gold,atk:r&&r.atk,def:r&&r.def,rolls:r&&r.rolls,top:r&&r.top,at:r&&r.at,
    reward:vis('s-reward'),over:vis('s-over'),title:vis('s-title'),shop:vis('s-shop'),quit:vis('s-quit'),
    ghosts:document.querySelectorAll('.ghost-tile').length,flies:document.querySelectorAll('.fly,.pop,.lf-flee').length,nodes:document.getElementsByTagName('*').length,
    hud:document.querySelector('.hud').innerText.replace(/\\s+/g,' ')}}"""
# a block and a panel that fit, the higher panel first, sometimes a random one
PICK = """(rand)=>{const r=PQ.run,F=PQ.frontier(),out=[];
  const open=(j,m)=>{let n=0,up=0;for(const b of [1,2,8]){if(!(m&b))continue;const q=PQ.rowOf(j)+(b===1?1:0),c=PQ.colOf(j)+(b===2?1:b===8?-1:0);if(c<0||c>5)continue;const x=PQ.cellAt(PQ.idOf(q,c));if(x&&!x.rock&&!x.foe&&!x.tile&&!x.start){n++;if(b===1)up=1}}return [n,up]};
  r.hand.forEach((t,k)=>{if(!t)return;const js=[...F.keys()].concat(F.rock?[...F.rock.keys()]:[]);for(const j of js)if(PQ.fits(t,j,F)){const [n,up]=open(j,t.m);const foe=t.e&&t.e.k==='foe'?1:0;out.push([k,j,PQ.rowOf(j)*4+n*3+up*4-foe*2+Math.random()*3,n])}});
  if(!out.length)return null;out.sort((a,b)=>b[2]-a[2]);const ok=out.filter(x=>x[3]>0);const L=ok.length?ok:out;
  const m=rand<.15?L[Math.floor(rand/.15*L.length)%L.length]:L[0];return [m[0],m[1],m[3]]}"""

async def wait_idle(pg, ms=9000):
    t0 = time.time()
    while time.time() - t0 < ms / 1000:
        s = await pg.evaluate(STATE)
        if s['reward'] or s['over'] or s['title'] or s['shop'] or s['quit']: return s
        if s['run'] and not s['busy'] and s['phase'] == 'build': return s
        await pg.wait_for_timeout(60)
    return await pg.evaluate(STATE)

async def tap(pg, sel):
    el = await pg.query_selector(sel)
    if not el: return False
    if sel.startswith('#board') or sel.startswith('#hand'): await pg.evaluate(TAP, el)  # the field and the hand listen to the finger itself
    else: await pg.evaluate('el=>el.click()', el)  # buttons listen to clicks
    return True

async def main():
    issues, stats = [], {'games': 0, 'steps': 0, 'rewards': 0, 'skills': 0, 'rerolls': 0, 'papers': 0, 'shop_buys': 0, 'best': 0, 'ends': {}}
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, reduced_motion='no-preference' if MOTION else 'reduce')
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
        pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' and 'ERR_' not in m.text else None)
        if COV:
            cdp = await ctx.new_cdp_session(pg); await cdp.send('Profiler.enable'); await cdp.send('Profiler.startPreciseCoverage', {'callCount': True, 'detailed': False})
        await pg.goto(URL); await pg.wait_for_timeout(600)
        rnd = random.Random(7)
        nodes0 = None
        for g in range(GAMES):
            stats['games'] += 1
            st = await pg.evaluate(STATE)
            if st['shop']: await tap(pg, '#sh-go')
            elif st['over']: await tap(pg, '#o-again')
            elif st['title'] or not st['run']: await tap(pg, '#t-new')
            await pg.wait_for_timeout(300)
            if JUMP and g % 3 == 1:  # straight into a later land with a stronger knight
                step = rnd.choice([45, 48, 95, 98, 145, 148, 195])
                await pg.evaluate(f"()=>{{const r=PQ.run;r.atk=Math.max(r.atk,4*Math.pow(2,{step//50}));r.maxHp=r.hp=Math.max(r.maxHp,30*Math.pow(2,{step//50}));PQ.jump({step})}}")
                await pg.wait_for_timeout(300)
            last = None
            for k in range(STEPS):
                st = await wait_idle(pg)
                stats['steps'] += 1
                # checks every step
                for key in ('hp', 'gold', 'atk', 'def', 'rolls'):
                    v = st.get(key)
                    if st['run'] and (v is None or v != v or (isinstance(v, (int, float)) and abs(v) > 1e12)):
                        issues.append(f'g{g} s{k}: {key} = {v}')
                if 'NaN' in (st['hud'] or '') or 'undefined' in (st['hud'] or ''): issues.append(f"g{g} s{k}: HUD {st['hud']}")
                if st['ghosts']: issues.append(f'g{g} s{k}: ghost tile left')
                if errs: issues.extend(f'g{g} s{k}: {e}' for e in errs); errs.clear()
                if st['over']:
                    head = await pg.evaluate("()=>document.getElementById('o-head').textContent")
                    end = head[-5:]; stats['ends'][end] = stats['ends'].get(end, 0) + 1
                    stats['best'] = max(stats['best'], (st['top'] or 0))
                    break
                if st['title'] or st['shop']: issues.append(f'g{g} s{k}: left the climb unexpectedly'); break
                if st['reward']:
                    n = await pg.evaluate("()=>document.querySelectorAll('#r-list .rrow').length")
                    if not n: issues.append(f'g{g} s{k}: reward with no cards'); break
                    await pg.wait_for_timeout(560)
                    await tap(pg, f'#r-list .rrow[data-i="{rnd.randrange(n)}"]'); await pg.wait_for_timeout(80)
                    await tap(pg, '#r-go'); stats['rewards'] += 1
                    await pg.wait_for_timeout(800); continue
                if st['quit']: await tap(pg, '#q-no'); continue
                if not st['run'] or st['busy'] or st['phase'] != 'build':
                    if last == ('stuck', st['phase']): issues.append(f"g{g} s{k}: stuck phase={st['phase']} busy={st['busy']}"); break
                    last = ('stuck', st['phase']); continue
                r = rnd.random()
                # now and then: a toy's paper, a skill, a tap on the ground
                if r < .06:
                    foe = await pg.evaluate("()=>{for(const el of document.querySelectorAll('#board .cell.stand, #board .cell.laid')){const i=+el.dataset.i,c=PQ.cellAt(i);const b=el.getBoundingClientRect();if(b.top>60&&b.bottom<innerHeight-160&&(c.foe||(c.tile&&c.tile.e&&c.tile.e.k==='foe')))return i}return -1}")
                    if foe >= 0:
                        await tap(pg, f'#board .cell[data-i="{foe}"]'); stats['papers'] += 1
                        txt = await pg.evaluate("()=>{const e=document.getElementById('skbar');return e.hidden?'':e.innerText}")
                        if not txt or 'undefined' in txt or 'NaN' in txt: issues.append(f'g{g} s{k}: toy paper {txt!r}')
                        await tap(pg, '#skbar [data-sb="x"]'); await pg.wait_for_timeout(60)
                    continue
                if r < .14:
                    ks = await pg.evaluate("()=>[...document.querySelectorAll('#drawer-in .skill')].map((b,k)=>b.classList.contains('none')?-1:k).filter(k=>k>=0)")
                    if ks:
                        await tap(pg, f'#drawer-in .skill[data-k="{rnd.choice(ks)}"]'); await pg.wait_for_timeout(120)
                        txt = await pg.evaluate("()=>{const e=document.getElementById('skbar');return e.hidden?'':e.innerText}")
                        if 'undefined' in txt or 'NaN' in txt: issues.append(f'g{g} s{k}: skill paper {txt!r}')
                        if await pg.query_selector('#skbar [data-sb="go"]'): await tap(pg, '#skbar [data-sb="go"]'); stats['skills'] += 1
                        else:
                            aim = await pg.evaluate("()=>{const a=document.querySelector('#hand .slot.aim')||document.querySelector('#board .cell.aim');return a?(a.classList.contains('slot')?'#hand .slot[data-i=\"'+a.dataset.i+'\"]':'#board .cell[data-i=\"'+a.dataset.i+'\"]'):null}")
                            if aim and rnd.random() < .7: await tap(pg, aim); stats['skills'] += 1
                            else: await tap(pg, '#skbar [data-sb="x"]')
                        await pg.wait_for_timeout(200)
                    continue
                mv = await pg.evaluate(PICK, rnd.random())
                if not mv:
                    if st['rolls'] and st['rolls'] > 0: await tap(pg, '#roll'); stats['rerolls'] += 1; await pg.wait_for_timeout(150); continue
                    await pg.wait_for_timeout(1600)  # the climb ends by itself
                    continue
                slot, cell, nopen = mv
                if nopen == 0 and st['rolls'] and st['rolls'] > 0:  # every fitting block leads into a wall: draw again first
                    await tap(pg, '#roll'); stats['rerolls'] += 1; await pg.wait_for_timeout(150); continue
                if rnd.random() < .5:  # tap the block, then the panel
                    await tap(pg, f'#hand .slot[data-i="{slot}"]'); await pg.wait_for_timeout(40)
                    ok = await tap(pg, f'#board .cell[data-i="{cell}"]')
                else:  # drag it there
                    s_el = await pg.query_selector(f'#hand .slot[data-i="{slot}"]'); c_el = await pg.query_selector(f'#board .cell[data-i="{cell}"]')
                    a = await s_el.bounding_box(); c = await c_el.bounding_box()
                    await pg.mouse.move(a['x'] + a['width'] / 2, a['y'] + 20); await pg.mouse.down()
                    await pg.mouse.move(c['x'] + c['width'] / 2, c['y'] + c['height'] / 2 + 53, steps=5); await pg.mouse.up()
                at0 = st['at']; st2 = await wait_idle(pg)
                if st2['run'] and st2['at'] == at0 and not (st2['reward'] or st2['over']):
                    issues.append(f'g{g} s{k}: a block that fits did not go down (slot {slot} -> {cell})')
                last = None
            # after a climb: sometimes the shop
            st = await pg.evaluate(STATE)
            if st['over'] and g % 2 == 0:
                await tap(pg, '#o-shop'); await pg.wait_for_timeout(250)
                for tab in ('up', 'deck', 'skill', 'gear'):
                    await tap(pg, f'#tab-{tab}'); await pg.wait_for_timeout(120)
                    rows = await pg.evaluate("()=>[...document.querySelectorAll('#sh-body .row-i,#sh-body [data-s],#sh-body [data-g]')].map((e,k)=>k)")
                    for _ in range(3):
                        if not rows: break
                        els = await pg.query_selector_all('#sh-body .row-i,#sh-body [data-s],#sh-body [data-g]')
                        e = rnd.choice(els); await pg.evaluate('el=>el.click()', e); await pg.wait_for_timeout(300)
                        det = await pg.evaluate("()=>{const d=document.getElementById('sh-det');return d.hidden?'':d.innerText}")
                        if 'undefined' in det or 'NaN' in det: issues.append(f'g{g} shop: {det!r}')
                        if await pg.query_selector('#sh-det [data-act="buy"]'): await tap(pg, '#sh-det [data-act="buy"]'); stats['shop_buys'] += 1
                        elif await pg.query_selector('#sh-det [data-act="set"]'): await tap(pg, '#sh-det [data-act="set"]')
                        await pg.wait_for_timeout(120)
            if nodes0 is None: nodes0 = st['nodes']
            stats.setdefault('nodes_each', []).append(st['nodes'])
            if errs: issues.extend(f'g{g} end: {e}' for e in errs); errs.clear()
        stats['nodes_first_last'] = [nodes0, (await pg.evaluate(STATE))['nodes']]
        stats['by_class'] = await pg.evaluate("()=>{const m={};for(const e of document.querySelectorAll('body *')){const k=e.tagName+'.'+(e.className&&e.className.baseVal!==undefined?e.className.baseVal:e.className||'').split(' ')[0];m[k]=(m[k]||0)+1}return Object.entries(m).sort((a,b)=>b[1]-a[1]).slice(0,12)}")
        if COV:
            cov = await cdp.send('Profiler.takePreciseCoverage'); src = open(URL[7:].split('#')[0], encoding='utf-8').read()
            never = []
            for sc in cov['result']:
                if not sc['url'].startswith('file:'): continue
                for f in sc['functions']:
                    r = f['ranges'][0]
                    if f['functionName'] and r['count'] == 0: never.append((f['functionName'], r['endOffset'] - r['startOffset']))
            never.sort(key=lambda x: -x[1]); stats['never_ran'] = never[:80]
        await b.close()
    print(json.dumps(stats, ensure_ascii=False))
    seen = set()
    for x in issues:
        key = x.split(': ', 1)[-1][:90]
        if key in seen: continue
        seen.add(key); print('ISSUE', x[:300])
    print('issues', len(issues), 'unique', len(seen))

asyncio.run(main())
