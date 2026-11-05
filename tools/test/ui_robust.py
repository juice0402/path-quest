# PATH QUEST: reloads, corrupt saves, throwing storage, screen sizes, sound  (python3 tools/test/ui_robust.py [reload|corrupt|storage|sizes|sound])
import asyncio, json, sys, os
from ui_lib import *
from ui_run import play, take_reward, check
SHOT = os.environ.get('SHOT', '/tmp/pq_shots'); os.makedirs(SHOT, exist_ok=True)

async def state(S):
    return await S.pg.evaluate("()=>({sc:['s-title','s-reward','s-quit','s-over','s-shop'].filter(i=>!document.getElementById(i).hidden),run:!!PQ.run,busy:PQ.busy,ph:PQ.run&&PQ.run.phase,top:PQ.run&&PQ.run.top})")

async def reload_tests(S):
    pg = S.pg
    print('== reload')
    async def fresh():
        await S.goto(mt=meta(300, 30)); await S.click('#t-new'); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{PQ.run.maxHp=PQ.run.hp=999;PQ.run.def=50;PQ.run.atk=50;PQ.render()}")
        await play(S, 3, 'rl'); await S.idle()
    # build
    await fresh(); top = await pg.evaluate("PQ.run.top"); await S.reload(); st = await state(S); print(' build:', st)
    if st['sc'] != ['s-title'] or not st['run']: issue('wrong', f'reload in build: {st}')
    await S.click('#t-new'); await pg.wait_for_timeout(400); st = await state(S)
    if st['top'] != top or st['ph'] != 'build' or st['busy']: issue('wrong', f'resume after build reload {st} top was {top}')
    await play(S, 2, 'rl-resume'); await check(S, 'resume')
    # open reward
    await fresh(); await pg.evaluate("()=>{PQ.run.reward=true;PQ.openReward()}"); await pg.wait_for_timeout(300)
    cards = await pg.evaluate("JSON.stringify(PQ.run.rewards.map(x=>x.id||x.k))"); await S.reload(); st = await state(S); print(' reward:', st)
    await S.click('#t-new'); await pg.wait_for_timeout(500); st = await state(S); print('  after つづき', st)
    if st['sc'] != ['s-reward']: issue('wrong', f'reload with open reward -> {st}')
    cards2 = await pg.evaluate("JSON.stringify(PQ.run.rewards.map(x=>x.id||x.k))")
    if cards != cards2: issue('wrong', f'reward cards changed on reload {cards} -> {cards2} (reroll exploit)')
    await take_reward(S); st = await state(S)
    if st['sc'] or st['busy']: issue('wrong', f'after reward take {st}')
    # quit sheet
    await fresh(); await S.click('#quit'); await pg.wait_for_timeout(200); await S.reload(); st = await state(S); print(' quit:', st)
    if st['sc'] != ['s-title']: issue('wrong', f'reload in quit sheet {st}')
    # shop (title -> reload) and result screen
    await fresh(); await pg.evaluate("PQ.gameOver('quit')"); await pg.wait_for_timeout(300); await S.reload(); st = await state(S); print(' result:', st)
    if st['sc'] != ['s-title'] or st['run']: issue('wrong', f'reload at result {st}')
    # bank survived
    b = await pg.evaluate("PQ.meta.bank"); far = await pg.evaluate("PQ.meta.far"); print('  bank', b, 'far', far)
    await S.goto(mt=meta(300, 30)); await pg.evaluate("PQ.showShop('up')"); await pg.wait_for_timeout(200)
    await S.click('#sh-up .row-i[data-k="hp"]'); await pg.wait_for_timeout(300); await S.click('#sh-det [data-act="buy"]'); await pg.wait_for_timeout(300)
    await S.reload(); b2 = await pg.evaluate("[PQ.meta.bank,PQ.meta.up.hp]"); print(' shop reload', b2)
    if b2[1] != 1: issue('wrong', f'purchase lost on reload {b2}')
    # mid walk
    await fresh()
    for i in range(6):
        b = await pg.evaluate(PLACE_PICK)
        if not b: break
        await pg.evaluate("([j,k])=>PQ.place(j,k)", [b[1], b[0]])
        await pg.wait_for_timeout(160 + 60 * i)
        mid = await pg.evaluate("PQ.run&&[PQ.run.phase,PQ.run.at,PQ.run.target,PQ.busy]")
        await S.reload(); st = await state(S)
        await S.click('#t-new'); await pg.wait_for_timeout(300)
        for _ in range(60):
            st2 = await state(S)
            if not st2['busy']: break
            await pg.wait_for_timeout(100)
        st2 = await state(S)
        print(f'  mid-walk {mid} -> reload -> {st2}', await pg.evaluate("document.getElementById('o-head').textContent"))
        if not st2['run']: break
        if st2['busy'] or st2['ph'] != 'build' and not st2['sc']: issue('進行', f'mid-walk reload leaves {st2} (mid {mid})')
        await check(S, 'midwalk')
    # mid-walk with hp low (fight)
    print(' errs', S.errs[:4])

async def corrupt(S):
    pg = S.pg
    print('== corrupt')
    cases = {
      'garbage meta': dict(mt='{{{not json'),
      'garbage run': dict(mt=meta(), run='}}}'),
      'meta array': dict(mt='[1,2,3]'),
      'meta null': dict(mt='null'),
      'meta strings': dict(mt=json.dumps(dict(bank='abc', far='x', up='no', gear=5, sk=7, newu='zz', newg=3))),
      'meta old (no newu/sk/gear)': dict(mt=json.dumps(dict(bank=50, best=3, far=3, up=dict(hp=2, undo=1)))),
      'meta negative/huge': dict(mt=json.dumps(dict(bank=-5, far=-3, up=dict(hp=999, atk=-4)))),
      'meta sk eq dup': dict(mt=json.dumps(dict(bank=5, sk=dict(own=['turn', 'zzz'], eq=['turn', 'turn', 'zzz'])))),
      'run no fields': dict(mt=meta(), run=json.dumps(dict(rows={}, hand=[], at=3))),
      'run old shape': dict(mt=meta(), run=json.dumps(dict(hp=5, maxHp=10, atk=2, gold=3, handSize=4, rolls=3, found=[], rows={'1': [{'rock': 0, 'gem': 0, 'tile': None, 'start': 1}] + [{'rock': 0, 'gem': 0, 'tile': None}] * 5}, made=1, spine=2, at=8, top=1, target=-1, phase='build', hand=[{'m': 5, 'e': None, 'c': 0}] * 4, **{'def': 0}))),
      'run phase walk bad target': dict(mt=meta(), run=json.dumps(dict(hp=5, maxHp=10, atk=2, gold=3, handSize=4, rolls=3, found=[], rows={}, made=-1, at=8, top=1, target=9999, phase='walk', hand=[], **{'def': 0}))),
    }
    for name, kw in cases.items():
        S.errs.clear()
        try:
            await S.goto(**kw)
        except Exception as e:
            issue('error', f'{name}: load threw {str(e)[:120]}'); continue
        st = await state(S) if await pg.evaluate("typeof PQ!=='undefined'") else {'sc': 'NO PQ'}
        res = {'sc': st['sc'], 'run': st.get('run')}
        # try to play: title -> あそぶ -> place; shop open
        try:
            await S.click('#t-new'); await pg.wait_for_timeout(500)
            s2 = await state(S); n = await play(S, 2, name) if s2['run'] and not s2['sc'] else -1
            await S.idle(); await pg.evaluate("PQ.gameOver&&PQ.run&&PQ.gameOver('quit')"); await pg.wait_for_timeout(300)
            await S.click('#o-shop'); await pg.wait_for_timeout(300)
            for t in ('up', 'gear', 'skill', 'deck'):
                await S.click('#tab-' + t); await pg.wait_for_timeout(120)
            m = await pg.evaluate("JSON.stringify([PQ.meta.bank,PQ.meta.far,PQ.meta.sk&&PQ.meta.sk.eq,Array.isArray(PQ.meta.newu)])")
            res['after'] = (n, m)
        except Exception as e:
            res['exc'] = str(e)[:140]; issue('error', f'{name}: flow threw {str(e)[:140]}')
        print(' ', name, '->', res, 'errs', S.errs[:2])
        if S.errs: issue('error', f'{name}: page errors {S.errs[:2]}')

async def storage(S):
    print('== throwing storage')
    pg = S.pg
    await pg.add_init_script("""(()=>{const th=()=>{throw new DOMException('denied','SecurityError')};
      Storage.prototype.setItem=th;Storage.prototype.getItem=th;Storage.prototype.removeItem=th;})()""")
    S.errs.clear()
    await pg.goto(URL); await pg.wait_for_timeout(600)
    st = await state(S); print(' start', st)
    await S.click('#t-new'); await pg.wait_for_timeout(500)
    await play(S, 3, 'private'); await S.idle(); await check(S, 'private')
    await S.click('#t-snd') if False else None
    await pg.evaluate("PQ.gameOver('quit')"); await pg.wait_for_timeout(300)
    await S.click('#o-shop'); await pg.wait_for_timeout(300)
    await S.click('#tab-skill'); await pg.wait_for_timeout(200)
    await S.click('#sh-back'); await pg.wait_for_timeout(300)
    await S.click('#t-snd'); await pg.wait_for_timeout(200)
    print(' errs', S.errs[:4]); 
    if S.errs: issue('error', f'throwing storage: {S.errs[:3]}')
    if (await state(S))['sc'] != ['s-title']: issue('wrong', 'private mode: not home after shop back')

async def sizes(S):
    pg = S.pg
    print('== sizes')
    sizes_ = [(320, 568), (375, 667), (390, 844), (430, 932), (844, 390), (820, 1180)]
    OVER = """()=>{const W=innerWidth,H=innerHeight,out=[];const de=document.documentElement;
      if(de.scrollWidth>W+1)out.push('hscroll '+de.scrollWidth+'>'+W);if(document.body.scrollWidth>W+1)out.push('body hscroll '+document.body.scrollWidth);
      const vis=e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(e).visibility!=='hidden'};
      for(const e of document.querySelectorAll('button,.btn,.rrow,.row-i,.sk2,.gi2,.slot,.peg,.tag,.dt-btn')){if(!vis(e)||e.closest('[hidden]'))continue;const r=e.getBoundingClientRect();
        if(r.right>W+2||r.left<-2)out.push('x-off '+(e.id||e.className).toString().slice(0,30)+' '+Math.round(r.left)+'..'+Math.round(r.right));
        if(r.bottom>H+2&&!e.closest('.sh-body,.sh-sheet,.case,.book,#r-list,.rw-cards,.ov-card,.sheet'))out.push('y-off '+(e.id||e.className).toString().slice(0,30)+' bottom '+Math.round(r.bottom));}
      for(const e of document.querySelectorAll('.sheet:not([hidden]) *')){if(e.children.length||!e.textContent.trim()||!vis(e))continue;if(e.scrollWidth>e.clientWidth+2&&getComputedStyle(e).overflow!=='visible'&&e.clientWidth>0)out.push('clip '+(e.className||e.tagName).toString().slice(0,24)+' "'+e.textContent.trim().slice(0,12)+'" '+e.scrollWidth+'>'+e.clientWidth)}
      // overflow of text beyond own box
      for(const e of document.querySelectorAll('.sheet:not([hidden]) .rrow, .sheet:not([hidden]) .rrow *, .dt-body, .dt-body *, .row-i *, .sk2 *')){if(!vis(e))continue;const p=e.parentElement.getBoundingClientRect(),r=e.getBoundingClientRect();if(e.children.length===0&&e.textContent.trim()&&(r.right>p.right+3||r.left<p.left-3)&&e.closest('.rrow,.dt-body,.row-i,.sk2')){out.push('spill '+(e.className||e.tagName).toString().slice(0,20)+' "'+e.textContent.trim().slice(0,14)+'"')}}
      const sh=document.querySelector('.sheet:not([hidden])');if(sh){const b=[...sh.querySelectorAll('button')].filter(vis).map(e=>e.getBoundingClientRect());for(let i=0;i<b.length;i++)for(let j=i+1;j<b.length;j++){const a=b[i],c=b[j];const ox=Math.min(a.right,c.right)-Math.max(a.left,c.left),oy=Math.min(a.bottom,c.bottom)-Math.max(a.top,c.top);if(0)out.push('')}}
      return out.slice(0,12)}"""
    seen = set()
    for (w, h) in sizes_:
        await pg.set_viewport_size({'width': w, 'height': h})
        S.errs.clear()
        await S.goto(mt=meta(5000, 60, up=dict(sg=3, sh=2, ds=2), gear=dict(own=['w1', 'w2', 's1'], eq={}), sk=dict(own=['turn', 'cross', 'clear', 'box'], eq=['turn', 'cross', 'clear'])))
        shots = []
        async def probe(tag):
            o = await pg.evaluate(OVER)
            if o: issue('visual', f'{w}x{h} {tag}: {o}')
            return o
        await probe('title')
        await S.click('#t-new'); await pg.wait_for_timeout(500)
        await pg.evaluate("()=>{PQ.run.maxHp=PQ.run.hp=999;PQ.run.def=50;PQ.run.atk=50;PQ.render()}")
        await play(S, 2, 'size'); await S.idle()
        await probe('game')
        # hud / hand / skill bar inside viewport
        g = await pg.evaluate("""()=>{const o=[];for(const s of ['.hud','#hand','#roll','#quit','#drawer-in','.view']){const e=document.querySelector(s);if(!e)continue;const r=e.getBoundingClientRect();if(r.width&&(r.bottom>innerHeight+1||r.right>innerWidth+1||r.left<-1||r.top<-1))o.push(s+' '+[r.left,r.top,r.right,r.bottom].map(Math.round))}return o}""")
        if g: issue('visual', f'{w}x{h} game layout off-screen: {g}')
        sl = await pg.evaluate("[...document.querySelectorAll('#drawer-in .skill')].length")
        # skill paper
        await S.click('#drawer-in .skill[data-k="2"]'); await pg.wait_for_timeout(200); await probe('skillbar')
        sb = await pg.evaluate("(()=>{const r=document.getElementById('skbar').getBoundingClientRect();return [r.left,r.top,r.right,r.bottom].map(Math.round)})()"); 
        if sb[2] > w + 1 or sb[3] > h + 1: issue('visual', f'{w}x{h} skill bar off-screen {sb}')
        await S.click('#skbar [data-sb="x"]')
        # reward with long names
        await pg.evaluate("()=>{PQ.run.reward=true;PQ.openReward()}"); await pg.wait_for_timeout(500)
        await probe('reward')
        if (w, h) in [(320, 568), (390, 844), (844, 390)]:
            await pg.screenshot(path=f'{SHOT}/reward_{w}x{h}.png')
        # worst case: evolution card text
        await pg.evaluate("()=>{PQ.run.it={plane:5,top:5,bomb:5,clover:1,spring:1,cat:1};PQ.run.chest=true;PQ.run.reward=false;PQ.run.rewards=null;PQ.openReward()}"); await pg.wait_for_timeout(500)
        await probe('evo-reward')
        await pg.evaluate("()=>{PQ.run.rewards=null;PQ.run.power=true;PQ.openReward()}"); await pg.wait_for_timeout(500); await probe('power-reward')
        await pg.evaluate("()=>{PQ.run.rewards=null;PQ.run.phase='build';document.getElementById('s-reward').hidden=true;PQ.render()}")
        await S.click('#quit'); await pg.wait_for_timeout(300); await probe('quit'); await S.click('#q-yes'); await pg.wait_for_timeout(1800)
        await probe('result')
        if (w, h) in [(320, 568), (844, 390)]: await pg.screenshot(path=f'{SHOT}/result_{w}x{h}.png')
        await S.click('#o-shop'); await pg.wait_for_timeout(500)
        for t in ('up', 'gear', 'skill', 'deck'):
            await S.click('#tab-' + t); await pg.wait_for_timeout(250)
            # open a detail paper for the first row
            row = {'up': '#sh-up .row-i', 'gear': '#sh-gear .gi2', 'skill': '#sh-skill .sk2', 'deck': '#sh-deck .row-i'}[t]
            await S.click(row); await pg.wait_for_timeout(300)
            await probe('shop-' + t)
            if t == 'skill':
                await S.click('#sh-skill .sk2.lk'); await pg.wait_for_timeout(250); await probe('shop-skill-locked')
            if (w, h) in [(320, 568), (844, 390)] and t in ('skill', 'deck'): await pg.screenshot(path=f'{SHOT}/shop_{t}_{w}x{h}.png')
            # detail paper must not cover the whole list: its height share
            sh = await pg.evaluate("(()=>{const d=document.getElementById('sh-det').getBoundingClientRect(),b=document.getElementById('sh-body').getBoundingClientRect();return [Math.round(d.height),Math.round(b.height),innerHeight]})()")
            if sh[1] < 90: issue('visual', f'{w}x{h} shop-{t}: list area only {sh[1]}px with the paper open (paper {sh[0]}px)')
        print(f' {w}x{h} done errs {len(S.errs)}')
        if S.errs: issue('error', f'{w}x{h}: {S.errs[:2]}')

async def sound(S):
    print('== sound')
    pg = S.pg
    # toggle persists
    await S.goto(mt=meta())
    pre = await pg.evaluate("localStorage.getItem('pq.snd')")
    await S.click('#t-snd'); await pg.wait_for_timeout(200)
    v1 = await pg.evaluate("[localStorage.getItem('pq.snd'),document.getElementById('t-snd').getAttribute('aria-pressed'),PQ.AUD.on]")
    await S.reload(); v2 = await pg.evaluate("[localStorage.getItem('pq.snd'),document.getElementById('t-snd').getAttribute('aria-pressed'),PQ.AUD.on]")
    await S.click('#t-snd'); await pg.wait_for_timeout(200); await S.reload()
    v3 = await pg.evaluate("[localStorage.getItem('pq.snd'),document.getElementById('t-snd').getAttribute('aria-pressed'),PQ.AUD.on]")
    print(' toggle', pre, v1, v2, v3)
    if v1[0] != '0' or v2[0] != '0' or v2[1] != 'false' or v3[0] != '1' or v3[1] != 'true': issue('wrong', f'sound toggle persistence {v1} {v2} {v3}')
    # play with sound on while "blocked" (no gesture flag): fine
    await S.click('#t-new'); await pg.wait_for_timeout(400); await play(S, 4, 'snd'); await S.idle()
    # off: during play stays silent
    await S.click('#quit'); await S.click('#q-yes'); await pg.wait_for_timeout(1500)
    print(' audio state', await pg.evaluate("({on:PQ.AUD.on,song:PQ.AUD.song,state:typeof PQ.AUD.state})"))
    print(' errs', S.errs[:4])
    if S.errs: issue('error', f'sound (blocked) errs {S.errs[:3]}')
    # AudioContext constructor throwing / absent
    await S.goto(mt=meta())
    await pg.add_init_script("window.AudioContext=undefined;window.webkitAudioContext=undefined")
    S.errs.clear(); await pg.goto(URL); await pg.wait_for_timeout(400)
    await S.click('#t-snd'); await S.click('#t-new'); await pg.wait_for_timeout(300); await play(S, 3, 'noaudio')
    await S.idle(); await pg.evaluate("PQ.gameOver('quit')"); await pg.wait_for_timeout(500)
    print(' no AudioContext errs', S.errs[:3])
    if S.errs: issue('error', f'no AudioContext: {S.errs[:3]}')

async def main():
    which = sys.argv[1:] or ['reload_tests', 'corrupt', 'storage', 'sizes', 'sound']
    alias = {'reload': 'reload_tests'}
    for w in which:
        w = alias.get(w, w)
        S = await Sess().start(audio=(w == 'sound'))
        try: await globals()[w](S)
        except Exception as e:
            import traceback; traceback.print_exc(); issue('error', f'{w} crashed: {str(e)[:200]}')
        finally: await S.stop()
    print('\nISSUES'); [print(i) for i in ISSUES]
if __name__ == '__main__': asyncio.run(main())
