# PATH QUEST のバランスの見はかり：ふつうの人くらいの考え方で何十回も続けて遊び、強化しながら どこまで行けるかを数える
# usage: python3 tools/test/sim.py [runs] [seqs] [--set JSON]
#   runs  1つの流れで遊ぶ回数（強化を引きつぐ）  seqs  ちがう乱数で何本ためすか（同時に動かす）
#   --set '{"name":value}'  ページの数値を上書きして試す（ない名前は無視）
import asyncio, json, sys, os, statistics
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
args = [a for a in sys.argv[1:] if not a.startswith('--')]
RUNS = int(args[0]) if args else 30
SEQS = int(args[1]) if len(args) > 1 else 3

# time runs 25x faster; Math.random gets a seed so a sequence can be repeated
INIT = """((seed,bal)=>{const st=window.setTimeout;window.setTimeout=(f,ms,...a)=>st(f,(ms||0)/25,...a);
  let x=seed>>>0||1;Math.random=()=>{x^=x<<13;x>>>=0;x^=x>>>17;x^=x<<5;x>>>=0;return x/4294967296};
  if(!sessionStorage.getItem('sim')){try{localStorage.clear()}catch(e){}sessionStorage.setItem('sim','1')}
  if(bal)localStorage.setItem('pq.bal',JSON.stringify(bal))})(%d,%s)"""

POLICY = r"""
window.SIM=(()=>{
  const W=6,wait=ms=>new Promise(f=>setTimeout(f,ms));
  const nb=(j,b)=>{const r=PQ.rowOf(j)+(b===1?1:b===4?-1:0),c=PQ.colOf(j)+(b===2?1:b===8?-1:0);return c<0||c>=W||r<0?-1:PQ.idOf(r,c)};
  const free=c=>c&&!c.rock&&!c.tile&&!c.start; // a standing toy can be fought, so it is a way on too
  async function idle(){for(let k=0;k<6000;k++){const r=PQ.run;if(!r)return 'over';if(r.phase==='reward'&&r.rewards)return 'reward';if(!PQ.busy&&r.phase==='build')return 'build';await wait(40)}return 'timeout'}
  function score(t,k,j,F){
    const r=PQ.run,c=PQ.cellAtSafe(j);let s=10*PQ.rowOf(j),open=0,two=0;
    const g=PQ.gateFrom(j,t.m);
    for(const b of [1,2,8]){if(!(t.m&b))continue;const q=nb(j,b);if(q<0)continue;const x=PQ.cellAtSafe(q);
      if(free(x)){open++;for(const [h,u] of r.hand.entries())if(u&&h!==k)for(const bb of [1,2,4,8])if(u.m&bb&&nb(q,bb)===j){two++;break}}}
    if(g>=0){const gc=PQ.cellAtSafe(g),bc=gc.tile.bi!=null?PQ.cellAtSafe(gc.tile.bi):gc,e=bc&&bc.tile&&bc.tile.e;
      if(e&&e.k==='foe'){const d=PQ.dmgFor(e);s+=d>=r.hp?-600:60-d*2}else s+=40}
    else if(!open)s-=1000;
    s+=open*4+Math.min(two,4)*2;
    if(c&&c.foe){const d=PQ.dmgFor(c.foe);s+=d>=r.hp?-500:-d*(r.hp<r.maxHp*.4?6:2.5)+c.foe.gold*.8} // the toy standing on that cell
    const e=t.e;
    if(e&&e.k==='foe'){const d=PQ.dmgFor(e);s+=d>=r.hp?-500:-d*(r.hp<r.maxHp*.4?6:2.5)+e.gold*.8}
    if(e&&e.k==='coin')s+=e.v*.6;
    if(e&&e.k==='potion')s+=Math.min(e.v,r.maxHp-r.hp)*2;
    if(e&&e.k==='gear')s+=3;
    if(c&&(c.coin||c.gem))s+=((c.coin|0)+(c.gem|0))*.5;
    if(t.sp)s+=4;
    return s+Math.random()*2;
  }
  function moves(){
    const r=PQ.run,F=PQ.frontier(),out=[];
    r.hand.forEach((t,k)=>{if(!t)return;const js=[...F.keys()].concat(F.rock?[...F.rock.keys()]:[]);for(const j of js)if(PQ.fits(t,j,F))out.push({k,j,t,s:score(t,k,j,F)})});
    out.sort((a,b)=>b.s-a.s);return out;
  }
  function trySkill(stuck){
    const r=PQ.run;
    for(const [k,s] of (r.sk||[]).entries()){
      if(!s||s.cd>0)continue;const d=PQ.SKILL_ID[s.id];
      if(s.id==='candy'&&r.hp<=r.maxHp*.5){PQ.useSkill(k,-1);return true}
      if(!stuck)continue;
      if(s.id==='box'||s.id==='cannon'){PQ.useSkill(k,-1);return true}
      if(d.aim){const ts=PQ.targets(d.aim);if(ts.length){PQ.useSkill(k,ts[Math.floor(Math.random()*ts.length)]);return true}}
    }
    return false;
  }
  async function playRun(){
    const t0=PQ.meta.bank;document.getElementById('t-new').click();await wait(100);
    let best=0,steps=0,foeGold=0,coinGold=0,kills=0,cap=null;
    for(let n=0;n<2000;n++){
      const st=await idle();
      if(st==='over'||st==='timeout'){const why=document.getElementById('o-head').textContent;
        const near=best%20>=17&&cap?(cap.d>=cap.hp?'cap-weak':'cap-path'):'';return {best,steps,gold:PQ.meta.bank-t0,foeGold,coinGold,kills,near,cap,why:st==='timeout'?'timeout':why.slice(-6)}}
      const r=PQ.run;best=Math.max(best,PQ.stepOf(r.top));
      cap=null;for(let q=r.top;q<=r.top+3;q++){const row=r.rows[q];const g=row&&row.find(c=>c.tile&&c.tile.anc);if(g&&g.tile.e&&g.tile.e.k==='foe'){cap={d:PQ.dmgFor(g.tile.e),hp:r.hp,max:r.maxHp,rolls:r.rolls,ehp:g.tile.e.hp,eatk:g.tile.e.atk,atk:r.atk,def:r.def};break}}
      if(st==='reward'){PQ.takeReward(Math.floor(Math.random()*r.rewards.length));await wait(20);continue}
      if(trySkill(false)){await wait(20);continue}
      const M=moves();
      if(!M.length||M[0].s<-400){
        if(r.rolls>0){PQ.reroll();await wait(20);continue}
        if(trySkill(true)){await wait(20);continue}
        if(!M.length){await wait(400);continue}
      }
      const m=M[0],e=m.t.e;
      if(e&&e.k==='foe'){foeGold+=e.gold;kills++}
      if(e&&e.k==='coin')coinGold+=e.v;
      const c=PQ.cellAtSafe(m.j);if(c&&(c.coin||c.gem))coinGold+=(c.coin|0)+(c.gem|0);
      if(c&&c.foe){foeGold+=c.foe.gold;kills++}
      const g=PQ.gateFrom(m.j,m.t.m);if(g>=0){const gc=PQ.cellAtSafe(g),bc=gc.tile.bi!=null?PQ.cellAtSafe(gc.tile.bi):gc,be=bc&&bc.tile&&bc.tile.e;if(be&&be.k==='foe'){foeGold+=be.gold;kills++}}
      PQ.place(m.j,m.k);steps++;await wait(10);
    }
    return {best,steps,why:'cap'};
  }
  function shop(){ // spread the gold over the basics, then a candy skill and the box
    const m=PQ.meta,U=PQ.UPS,core=['atk','hp','def','roll','bag','hand','dx','dt','dc','sg','sj'],bought=[];
    const fight=['atk','hp','def'],util=core.filter(k=>!fight.includes(k));
    for(let n=0;n<60;n++){ // two for the fight, then one for the road, the cheapest of each
      const set=n%3===2?util:fight;
      const pick=ks=>ks.map(k=>U.find(u=>u.k===k)).filter(u=>m.up[u.k]<u.max&&u.cost(m.up[u.k])<=m.bank&&!(PQ.isLocked&&PQ.isLocked('up',u.k))).sort((a,b)=>a.cost(m.up[a.k])-b.cost(m.up[b.k]))[0];
      const u=pick(set)||pick(core);if(!u)break;
      m.bank-=u.cost(m.up[u.k]);m.up[u.k]++;bought.push(u.k);
    }
    for(const id of ['candy','box','clear']){const k=PQ.SKILL_ID[id];if(!m.sk.own.includes(id)&&m.bank>=k.cost&&!(PQ.isLocked&&PQ.isLocked('sk',id))){m.bank-=k.cost;m.sk.own.push(id);const f=m.sk.eq.indexOf(null);if(f>=0)m.sk.eq[f]=id;bought.push(id)}}
    PQ.saveMeta();return bought;
  }
  return {playRun,shop};
})();
"""

async def seq(p, seed, sets):
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    ctx = await b.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce')
    await ctx.add_init_script(INIT % (seed, json.dumps(sets) if sets else 'null'))
    pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto(URL); await pg.wait_for_timeout(400)
    await pg.evaluate(POLICY)
    out = []
    for i in range(RUNS):
        r = await pg.evaluate("()=>SIM.playRun()")
        r['up'] = await pg.evaluate("()=>({...PQ.meta.up})")
        r['bought'] = await pg.evaluate("()=>SIM.shop()")
        out.append(r)
        await pg.evaluate("()=>{document.getElementById('o-title')&&document.getElementById('o-title').click()}")
    await b.close()
    return out, errs

async def main():
    sets = None
    if '--set' in sys.argv: sets = json.loads(sys.argv[sys.argv.index('--set') + 1])
    async with async_playwright() as p:
        res = await asyncio.gather(*[seq(p, 101 + 37 * k, sets) for k in range(SEQS)])
    allr = [r for r, _ in res]
    for k, (r, e) in enumerate(res):
        print(f'seq{k}', ' '.join(str(x['best']) for x in r), '| errors', len(e), e[:2])
    # how many runs until each 20-step land is passed (the captain at 20, 40, 60 ...)
    for goal in (10, 20, 40, 60, 80, 100):
        firsts = []
        for r in allr:
            f = next((i + 1 for i, x in enumerate(r) if x['best'] >= goal), None)
            firsts.append(f)
        print(f'first run reaching {goal:3d}:', firsts)
    print('run1 best', [r[0]['best'] for r in allr])
    tot = lambda key: sum(x.get(key, 0) or 0 for r in allr for x in r)
    print('gold total', tot('gold'), 'from toys(est)', tot('foeGold'), 'from coins(est)', tot('coinGold'), 'kills', tot('kills'))
    ends = {}
    for r in allr:
        for x in r: ends[x['why']] = ends.get(x['why'], 0) + 1
    print('ends', ends)
    print('final upgrades', [r[-1]['up'] for r in allr][:1])
    near = {}
    for r in allr:
        for x in r:
            if x.get('near'): near[x['near']] = near.get(x['near'], 0) + 1
    print('ended at a captain', near)
    ex = [x['cap'] for r in allr for x in r if x.get('near') == 'cap-weak'][:4]
    print('weak examples', ex)
    print('path examples', [(x['best'],x['why'],x['cap']) for r in allr for x in r if x.get('near') == 'cap-path'][:6])
    gold_per_run = [round(statistics.mean(x['gold'] for x in r[i:i+10])) for r in allr[:1] for i in range(0, len(r), 10)]
    print('gold per run (seq0, by 10s)', gold_per_run)

asyncio.run(main())
