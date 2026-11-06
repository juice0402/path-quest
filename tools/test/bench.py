# 11/6 重さのくらべ（毎回ほぼ同じ流れ）：同じ乱数で、戦い3回・歩き8回・ごほうび1回をして、場面ごとのコマと main thread の時間を出す
# usage: python3 tools/test/bench.py [cpu の遅さ(倍)] [回数]   PQ_FILE=_old.html で前の版  PQ_CSS='...' で試しの CSS
#   画面は Android（412x915・2.625倍）。歩きまわる虫はゆらぎが大きいので止める（虫の重さは frame_cost.py で）
import asyncio, os, sys, json, statistics
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/', os.environ.get('PQ_FILE', 'index.html'))) + '#fxtest'
RATE = float(sys.argv[1]) if len(sys.argv) > 1 else 4
REP = int(sys.argv[2]) if len(sys.argv) > 2 else 2
CSS = '.lf-roam{display:none!important}' + os.environ.get('PQ_CSS', '')

FLOW = """async()=>{const wait=ms=>new Promise(r=>setTimeout(r,ms));const fr=[];let ph='-',on=true,last=performance.now();
  const loop=t=>{fr.push([t-last,ph]);last=t;if(on)requestAnimationFrame(loop)};requestAnimationFrame(loop);
  const idle=async()=>{for(let k=0;k<200;k++){if(PQ.run&&!PQ.busy&&PQ.run.phase==='build')return;const v=document.getElementById('s-reward');if(v&&!v.hidden)return;await wait(50)}};
  const R=PQ.run;R.hp=R.maxHp=99999;R.atk=3;R.def=0;
  for(let k=0;k<3;k++){ /* a fight in front of the knight */
    const at=R.at,j=PQ.idOf(PQ.rowOf(at)+1,PQ.colOf(at)),c=PQ.cellAt(j);c.tile=null;c.rock=1;c.foe={k:'foe',t:['soldier','imp','mouse'][k],name:'toy',hp:9,atk:1,gold:5,v:3};PQ.render();await wait(400);
    ph='fight';await PQ.battle(c.foe,R.at,j);ph='coins';PQ.FXH&&0;c.foe=null;c.rock=0;PQ.updateCell?0:0;PQ.render();await wait(700);ph='-'}
  for(let k=0;k<8;k++){ /* walks: the first block that fits, the highest place */
    await idle();if(!PQ.run)break;const F=PQ.frontier();let best=null;
    PQ.run.hand.forEach((t,h)=>{if(!t)return;for(const j of F.keys())if(PQ.fits(t,j,F)&&(!best||PQ.rowOf(j)>PQ.rowOf(best[0])))best=[j,h]});
    if(!best){if(PQ.run.rolls>0){PQ.reroll();await wait(300);continue}break}
    ph='walk';PQ.place(best[0],best[1]);await wait(150);await idle();ph='-';await wait(200)}
  if(PQ.run){ph='reward';PQ.run.reward=true;PQ.openReward();await wait(1500);ph='-'}
  on=false;await wait(50);return fr}"""

async def one(b):
    ctx = await b.new_context(viewport={'width': 412, 'height': 915}, device_scale_factor=2.625, is_mobile=True, has_touch=True)
    # the same game every time: the roaming critters (they come on timers) draw from a stream of their own
    await ctx.add_init_script("{const G=s=>()=>{s^=s<<13;s^=s>>>17;s^=s<<5;return ((s>>>0)%1e6)/1e6};const A=G(4242),B=G(777);Math.random=()=>/roam/.test(new Error().stack)?B():A()}")
    await ctx.add_init_script("try{localStorage.clear();localStorage.setItem('pathquest.meta.v1',JSON.stringify({bank:0,best:12,far:12,seen:1,up:{hp:2,atk:2},sk:{own:['turn'],eq:['turn',null,null]}}))}catch(e){}")
    pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto(URL); await pg.wait_for_timeout(700)
    await pg.add_style_tag(content=CSS)
    await pg.click('#t-new'); await pg.wait_for_timeout(1200)
    cdp = await ctx.new_cdp_session(pg); await cdp.send('Performance.enable'); await cdp.send('Emulation.setCPUThrottlingRate', {'rate': RATE})
    m0 = {m['name']: m['value'] for m in (await cdp.send('Performance.getMetrics'))['metrics']}
    fr = await pg.evaluate(FLOW)
    m1 = {m['name']: m['value'] for m in (await cdp.send('Performance.getMetrics'))['metrics']}
    await ctx.close()
    return fr, {k: m1[k] - m0[k] for k in ('TaskDuration', 'RecalcStyleDuration', 'LayoutDuration', 'ScriptDuration')}, errs

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        res = [await one(b) for _ in range(REP)]
        await b.close()
    by = {}
    for fr, _, _ in res:
        for d, ph in fr[2:]:
            by.setdefault(ph, []).append(d)
    print(f"{os.environ.get('PQ_FILE', 'index.html')} x{RATE} {os.environ.get('PQ_CSS', '')[:60]}")
    for ph in ('walk', 'fight', 'coins', 'reward', '-'):
        ds = sorted(by.get(ph, []))
        if not ds: continue
        n = len(ds); drop = sum(1 for d in ds if d > 34)
        print(f'  {ph:7s} frames {n:5d}  avg {sum(ds)/n:5.1f}ms  95% {ds[int(n*.95)]:5.1f}  drops {drop:4d} ({100*drop/n:4.1f}%)')
    tot = {k: statistics.mean(r[1][k] for r in res) for k in res[0][1]}
    print('  main thread: ' + ', '.join(f'{k.replace("Duration","")} {v:.2f}s' for k, v in tot.items()), ' errors', sum(len(r[2]) for r in res))

asyncio.run(main())
