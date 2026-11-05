# PATH QUEST 完走テスト：強いナイトで 6つの次元ぜんぶ（STEP 320 以上）をのぼり、大将・王さま・ポータル・ごほうび・次元の力 をぜんぶ通る。
# 途中でランダムにリロード（ごほうび／次元の力を開いている最中も）してセーブからつづけ、エラー・止まり・NaN・DOM/保存の増えすぎ・「手がないのに終わらない」を見張る。
# usage: python3 tools/test/full_run.py [seeds] [target_step] [--weak] [--noreload]
#   --weak  強化なし・手札1枚・リロール0で、行き止まりで ちゃんと結果画面になるか（ハングしないか）を見る
import asyncio, json, sys, os, re, random
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
args = [a for a in sys.argv[1:] if not a.startswith('--')]
SEEDS = int(args[0]) if args else 4
TARGET = int(args[1]) if len(args) > 1 else 330
WEAK = '--weak' in sys.argv
NORELOAD = '--noreload' in sys.argv

SIMSRC = open(os.path.join(HERE, 'sim.py'), encoding='utf-8').read()
POLICY = re.search(r'POLICY = r"""(.*?)"""', SIMSRC, re.S).group(1)

# seeded random + 25x time; the seed changes at each reload (sessionStorage counter) so a reload does not replay the same dice
INIT = """((seed)=>{const st=window.setTimeout;window.setTimeout=(f,ms,...a)=>st(f,(ms||0)/25,...a);
  let n=0;try{n=+sessionStorage.getItem('frn')||0;sessionStorage.setItem('frn',String(n+1))}catch(e){}
  let x=((seed+n*7919)>>>0)||1;Math.random=()=>{x^=x<<13;x>>>=0;x^=x>>>17;x^=x<<5;x>>>=0;return x/4294967296}})(%d)"""

# one action of the player per call. reports what it saw. boost: keep the knight strong (not for --weak)
ACT = r"""
window.FR=(()=>{
  const wait=ms=>new Promise(f=>setTimeout(f,ms));
  const W=6;
  const dimOf=()=>PQ.run?Math.floor(Math.max(0,PQ.stepOf(PQ.run.top)-1)/50):0;
  function boost(){ const r=PQ.run;if(!r||%(weak)s)return;const d=Math.floor(Math.max(0,PQ.stepOf(r.top)-1)/50),x=Math.pow(3,d);
    r.atk=Math.max(r.atk,60*x);r.def=Math.max(r.def,6*x);r.maxHp=Math.max(r.maxHp,600*x);if(r.hp<r.maxHp*.6)r.hp=r.maxHp; }
  async function idle(){ // returns [state, loops waited]; a loop is 40ms of game time
    let k=0;for(;k<2000;k++){const r=PQ.run;if(!r)return ['over',k];if(r.phase==='reward'&&r.rewards)return ['reward',k];if(!PQ.busy&&r.phase==='build')return ['build',k];await wait(40)}
    return ['timeout',k]; }
  function nofitNow(){const r=PQ.run,F=PQ.frontier();return !r.hand.some(t=>t&&PQ.anyFit(t,F))&&!PQ.rescue(F)}
  async function act(hold){
    const [st,k]=await idle();const r=PQ.run;
    const info={st,wait:k,step:r?PQ.stepOf(r.top):-1,phase:r&&r.phase,rk:r&&r.rk,dim:dimOf()};
    if(st==='over'||st==='timeout')return info;
    if(st==='reward'){ // pick at random, but the dimension power / evolutions too
      info.n=r.rewards.length;if(hold){info.held=1;return info}PQ.takeReward(Math.floor(Math.random()*r.rewards.length));await wait(20);return info}
    boost();
    if(%(weak)s)r.rolls=0;
    if(r.__rf===undefined)r.__rf=0;
    if(!%(weak)s)for(let q=r.top;q<=r.top+6;q++){const row=r.rows[q];if(row)row.forEach(c=>{if(c.rock===1||c.rock===3)c.rock=0})} // strong run: obstacles ahead are cleared so the climb can go through all six lands (walls are covered by bot.py/sim.py)
    const M=SIM_moves();
    if(!M.length||M[0].s<-400){
      if(r.rolls>0&&(r.__st!==r.top?(r.__st=r.top,r.__n=0,true):++r.__n<=6)){PQ.reroll();await wait(20);info.did='reroll';return info}
      if(SIM_trySkill(true)){await wait(20);info.did='skill';return info}
      if(!M.length){ // no move at all: the game must end the run by itself
        info.did='nomove';info.nofit=nofitNow();await wait(400);return info}
      if(!%(weak)s){ // strong run: the policy walked into a pocket (every fitting block leads into a wall). carve a way out and go on; counted
        for(let q=r.top;q<=r.top+4;q++){const row=r.rows[q];if(row)row.forEach(c=>{if(c.rock===1)c.rock=0})}
        window.CARVED=(window.CARVED||0)+1;info.carved=1}
    }
    const M2=info.carved?SIM_moves():M;const m=M2[0];PQ.place(m.j,m.k);await wait(10);info.did='place';return info }
  return {act};
})();
"""
# borrow moves()/trySkill() from the sim policy: expose them
# the sim policy does not head for the captain's gap: add a pull toward it (so a strong knight is not lost in the yard in front of every captain)
POLICY = POLICY.replace('return s+Math.random()*2;', '''for(let q=PQ.run.top;q<=PQ.run.top+4;q++){const row=PQ.run.rows[q],g=row&&row.findIndex(x=>x.tile&&x.tile.anc);if(g>=0){s-=14*Math.abs(PQ.colOf(j)-g);break}}
    return s+Math.random()*2;''')
POLICY2 = POLICY.replace('return {playRun,shop};', 'window.SIM_moves=moves;window.SIM_trySkill=trySkill;return {playRun,shop};')

STATS = """()=>{const r=PQ.run,bad=[];
  if(r){for(const k of ['atk','def','maxHp','hp','gold','rolls','top','at']){const v=r[k];if(typeof v!=='number'||!isFinite(v))bad.push(k+'='+v)}
        if(r.hp>r.maxHp+1e-9)bad.push('hp>max '+r.hp+'/'+r.maxHp); if(r.hp<=0&&r.phase==='build')bad.push('hp<=0 in build')
        if(r.gold<0)bad.push('gold<0 '+r.gold); if(r.rolls<0)bad.push('rolls<0 '+r.rolls)}
  const m=PQ.meta;for(const k of ['bank','far']){if(typeof m[k]!=='number'||!isFinite(m[k])||m[k]<0)bad.push('meta.'+k+'='+m[k])}
  let ls=0;try{for(const k of Object.keys(localStorage))ls+=k.length+localStorage.getItem(k).length}catch(e){}
  const vis=id=>{const e=document.getElementById(id);return !!e&&!e.hidden};
  return {bad,nodes:document.getElementsByTagName('*').length,ls,over:vis('s-over'),reward:vis('s-reward'),title:vis('s-title'),shop:vis('s-shop'),
    hud:document.querySelector('.hud')?document.querySelector('.hud').innerText.replace(/\\s+/g,' ').slice(0,120):''}}"""

SETUP_STRONG = """()=>{const m=PQ.meta;for(const u of PQ.UPS)m.up[u.k]=u.max;m.far=Math.max(m.far,999);m.bank=Math.max(m.bank,1e6);PQ.saveMeta()}"""

async def seed_run(p, seed, sem, log):
    async with sem:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce')
        await ctx.add_init_script(INIT % seed)
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
        pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' and 'ERR_' not in m.text else None)
        rnd = random.Random(seed)
        res = {'seed': seed, 'issues': [], 'maxstep': 0, 'reloads': 0, 'reload_in_reward': 0, 'reload_in_power': 0, 'acts': 0, 'maxwait': 0, 'dims': 0, 'end': None, 'runs': 0}
        iss = res['issues']
        def note(s):
            if len(iss) < 40 and s not in iss: iss.append(s)
        async def install():
            await pg.evaluate(POLICY2); await pg.evaluate(ACT % {'weak': 'true' if WEAK else 'false'})
        await pg.goto(URL); await pg.wait_for_timeout(400)
        if not WEAK: await pg.evaluate(SETUP_STRONG)
        await install()
        await pg.evaluate("()=>document.getElementById('t-new').click()"); await pg.wait_for_timeout(150)
        res['runs'] = 1
        laststep = 0; nodes0 = ls0 = None; same = 0; lastkey = None; nomove = 0; nodes_hist = []
        for n in range(6000):
            hold = rnd.random() < 0.35 and not NORELOAD
            try:
                info = await asyncio.wait_for(pg.evaluate('()=>FR.act(%s)' % ('true' if hold else 'false')), 120)
            except Exception as e:
                note(f'act exception/timeout at act {n}: {str(e)[:120]}'); st = None
                try: st = await pg.evaluate(STATS)
                except Exception: pass
                res['end'] = 'act-timeout'; res['last_state'] = st; break
            if info['step'] >= 0: laststep = info['step']
            res['acts'] += 1; res['maxstep'] = max(res['maxstep'], info['step']); res['dims'] = max(res['dims'], info['dim'])
            res['maxwait'] = max(res['maxwait'], info['wait']); res['carved'] = res.get('carved', 0) + (info.get('carved') or 0)
            if info['wait'] >= 250: note(f"busy/not-idle {info['wait']*40/1000:.0f}s game time at step {info['step']} phase={info['phase']} (act {n})")
            if errs: [note(f"step {info['step']}: {e[:200]}") for e in errs]; errs.clear()
            s = await pg.evaluate(STATS)
            for bd in s['bad']: note(f"step {info['step']}: bad stat {bd}")
            if 'NaN' in s['hud'] or 'undefined' in s['hud'] or 'Infinity' in s['hud']: note(f"step {info['step']}: HUD {s['hud']}")
            if n % 50 == 0:
                if nodes0 is None: nodes0, ls0 = s['nodes'], s['ls']
                nodes_hist.append((info['step'], s['nodes'], s['ls']))
            if s['nodes'] > 6000: note(f"DOM nodes {s['nodes']} at step {info['step']}")
            if s['ls'] > 400000: note(f"localStorage {s['ls']} chars at step {info['step']}")
            if info['st'] == 'timeout':
                note(f"STALL: never idle (phase={info['phase']} step={info['step']} rk={info['rk']} act {n})"); res['end'] = 'timeout'; res['last_state'] = s; break
            if info['st'] == 'over':
                await pg.wait_for_timeout(100)
                s = await pg.evaluate(STATS)
                if not s['over']: note(f"run is gone but the result screen is not shown (step {info['step']})")
                head = await pg.evaluate("()=>document.getElementById('o-head').textContent")
                res['end'] = 'over:' + head[-8:]; res['end_step'] = laststep
                if WEAK or laststep >= TARGET: break
                # strong run died on a wall the simple policy walked into: count it, start again and jump back to the same step (the captains/kings still get crossed)
                res.setdefault('deaths', []).append([laststep, head[-6:]]); res['runs'] += 1
                if res['runs'] > 40: break
                await pg.evaluate("()=>document.getElementById('o-again').click()"); await pg.wait_for_timeout(150)
                await pg.evaluate("()=>document.getElementById('t-new').click()") if not (await pg.evaluate(STATS))['reward'] and not await pg.evaluate("()=>!!PQ.run") else None
                await pg.wait_for_timeout(150)
                await pg.evaluate("(s)=>{const r=PQ.run;if(!r)return;const d=Math.floor(Math.max(0,s-1)/50),x=Math.pow(3,d);r.dp=d;r.atk=60*x;r.def=6*x;r.maxHp=r.hp=600*x;PQ.jump(Math.max(1,s-1));for(let q=r.top+1;q<=r.top+5;q++){const row=r.rows[q],g=row&&row.findIndex(c=>c.tile&&c.tile.anc);if(g>=0){PQ.jump(q-2,g);break}}}", laststep)
                res['end'] = None; continue
            if info.get('did') == 'nomove':
                nomove += 1
                if nomove > 6: note(f"NO MOVE but run not ended after {nomove} tries (step {info['step']}, nofit={info.get('nofit')}, act {n})"); res['end'] = 'nomove-hang'; res['last_state'] = s; break
            else: nomove = 0
            key = (info['st'], info['phase'], info['step'], info.get('did'))
            same = same + 1 if key == lastkey and info.get('did') in (None, 'reroll', 'skill') else 0; lastkey = key
            if same > 40: note(f"phase not changing: {key} x{same}"); res['end'] = 'static'; break
            if info['step'] >= TARGET and not WEAK:
                res['end'] = 'reached'; break
            # random reload (also when a reward / the dimension pick is open)
            if not NORELOAD:
                in_rw = info['st'] == 'reward'
                if in_rw and not info.get('held'): in_rw = False
                p_rl = 1.0 if in_rw else 0.02
                if rnd.random() < p_rl:
                    res['reloads'] += 1; res['reload_in_reward'] += in_rw; res['reload_in_power'] += (in_rw and info.get('rk') == 'power')
                    pre = await pg.evaluate("()=>({step:PQ.stepOf(PQ.run.top),hp:PQ.run.hp,atk:PQ.run.atk,rw:PQ.run.rewards&&PQ.run.rewards.length,phase:PQ.run.phase,power:PQ.run.power,reward:PQ.run.reward,chest:PQ.run.chest})")
                    lsk = await pg.evaluate("()=>{const v=localStorage.getItem('pathquest.run.v3');return v?v.length:null}")
                    await pg.reload(); await pg.wait_for_timeout(300)
                    post = await pg.evaluate("()=>PQ.run?({step:PQ.stepOf(PQ.run.top),hp:PQ.run.hp,atk:PQ.run.atk,rw:PQ.run.rewards&&PQ.run.rewards.length,phase:PQ.run.phase,power:PQ.run.power,reward:PQ.run.reward,chest:PQ.run.chest}):null")
                    if not post: note(f"reload lost the run (pre {pre}; save length before reload {lsk}; ls after {await pg.evaluate('()=>Object.keys(localStorage).join()')})"); res['end'] = 'lost-on-reload'; break
                    if pre['phase'] != 'walk' and (post['step'] != pre['step'] or post['atk'] != pre['atk'] or (pre['rw'] or 0) != (post['rw'] or 0)):
                        note(f"reload changed saved state: pre {pre} post {post}")
                    await install()
                    await pg.evaluate("()=>document.getElementById('t-new').click()"); await pg.wait_for_timeout(250)
                    # after continuing: reward screen should be showing again if one was open
                    if in_rw:
                        s2 = await pg.evaluate(STATS)
                        if not s2['reward']: 
                            await pg.wait_for_timeout(600); s2 = await pg.evaluate(STATS)
                            if not s2['reward']: note(f"reload during {info.get('rk')} reward: the reward screen did not come back (step {info['step']}); phase={post['phase']}")
        if nodes_hist:
            res['nodes_first_last'] = [nodes_hist[0][1], nodes_hist[-1][1]]; res['ls_first_last'] = [nodes_hist[0][2], nodes_hist[-1][2]]
            res['nodes_max'] = max(h[1] for h in nodes_hist)
        if errs: [note('late: ' + e[:200]) for e in errs]
        await b.close()
        log.append(res)

async def main():
    log = []
    sem = asyncio.Semaphore(3)
    async with async_playwright() as p:
        await asyncio.gather(*[seed_run(p, 1000 + 131 * k, sem, log) for k in range(SEEDS)])
    for r in sorted(log, key=lambda r: r['seed']):
        iss = r.pop('issues'); ls = r.pop('last_state', None)
        print(json.dumps(r, ensure_ascii=False))
        for i in iss: print('   ISSUE', i)
        if ls: print('   last_state', json.dumps(ls, ensure_ascii=False)[:300])
    print('seeds', len(log), 'reached', sum(1 for r in log if r['end'] == 'reached'), 'with issues', sum(1 for r in log if r.get('issues') or r['end'] in ('timeout', 'act-timeout', 'static', 'nomove-hang', 'lost-on-reload')))

asyncio.run(main())
