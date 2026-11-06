# 11/6 重さの点検：ふつうの動きで冒険を遊び、場面ごと（組み立て・歩く・戦う・ごほうび）のコマの間かくと、重い処理を集める
# usage: python3 tools/test/perf_run.py [steps] [cpu の遅さ(倍)] [--prof] [--trace] [--iphone]
#   画面はふだん Android（412x915・2.625倍）。--iphone で 390x844・3倍。PQ_FILE=_old.html で前の版
#   --prof  関数ごとの時間（CPU プロファイル）も出す
import asyncio, json, random, sys, os, time, collections
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'bot.py'), encoding='utf-8').read()
exec(src[:src.index('async def main')].replace('GAMES = int', 'GAMES = 1 or int').replace('STEPS = int', 'STEPS = 1 or int'))  # TAP, STATE, PICK, wait_idle, tap
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/', os.environ.get('PQ_FILE', 'index.html'))) + '#fxtest'
args = [a for a in sys.argv[1:] if not a.startswith('--')]
NSTEP = int(args[0]) if args else 40
RATE = float(args[1]) if len(args) > 1 else 4
PROF = '--prof' in sys.argv
TRACE = '--trace' in sys.argv

# every frame: when it came and what was going on
REC = """()=>{window.__fr=[];window.__lt=[];
  const ph=()=>{const r=PQ.run,v=id=>{const e=document.getElementById(id);return e&&!e.hidden};
    if(v('s-reward'))return 'reward';if(v('s-over'))return 'over';if(!r)return 'title';
    if(performance.now()-window.__fx<700)return 'fight';if(performance.now()-window.__gold<900)return 'coins';return r.phase+(PQ.busy?'*':'')};
  window.__fx=-1e9;window.__gold=-1e9;for(const n of ['strike','hurt','toyhit'])PQ.FXH.add(n,()=>{window.__fx=performance.now()});PQ.FXH.add('kill',()=>{window.__fx=window.__gold=performance.now()});
  let last=performance.now();const loop=t=>{window.__fr.push([t-last,ph()]);last=t;requestAnimationFrame(loop)};requestAnimationFrame(loop);
  try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__lt.push([e.startTime,e.duration,ph()])}).observe({type:'longtask',buffered:true})}catch(e){}}"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox', '--enable-gpu-rasterization'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844} if '--iphone' in sys.argv else {'width': 412, 'height': 915}, device_scale_factor=3 if '--iphone' in sys.argv else 2.625, is_mobile=True, has_touch=True, reduced_motion='no-preference')
        await ctx.add_init_script("{let x=12345;Math.random=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return ((x>>>0)%1e6)/1e6}}")  # the same climb each time (old and new can be compared)
        await ctx.add_init_script("try{localStorage.clear();localStorage.setItem('pathquest.meta.v1',JSON.stringify({bank:0,best:12,far:12,seen:1,up:{hp:2,atk:2},sk:{own:['turn'],eq:['turn',null,null]}}))}catch(e){}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        cdp = await ctx.new_cdp_session(pg)
        await cdp.send('Performance.enable')
        await pg.goto(URL); await pg.wait_for_timeout(800)
        await tap(pg, '#t-new'); await pg.wait_for_timeout(600)
        await pg.evaluate("()=>{PQ.run.maxHp=PQ.run.hp=9999;PQ.renderStats&&PQ.renderStats()}")  # a long climb: fights, coins and rewards, no early end
        if TRACE: await b.start_tracing(page=pg, path='/tmp/pq_trace.json', categories=['devtools.timeline', 'disabled-by-default-devtools.timeline', 'disabled-by-default-devtools.timeline.frame', 'cc', 'viz'])
        await cdp.send('Emulation.setCPUThrottlingRate', {'rate': RATE})
        if PROF:
            await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval', {'interval': 200}); await cdp.send('Profiler.start')
        m0 = {m['name']: m['value'] for m in (await cdp.send('Performance.getMetrics'))['metrics']}
        await pg.evaluate(REC)
        rnd = random.Random(3); steps = 0; t0 = time.time()
        while steps < NSTEP and time.time() - t0 < 600:
            st = await wait_idle(pg, 15000)
            if st['over']:  # another climb (the same seed goes on)
                await tap(pg, '#o-again'); await pg.wait_for_timeout(700); await pg.evaluate("()=>{if(PQ.run){PQ.run.maxHp=PQ.run.hp=9999}}"); continue
            if st['reward']:
                n = await pg.evaluate("()=>document.querySelectorAll('#r-list .rrow').length")
                await pg.wait_for_timeout(700)
                await tap(pg, f'#r-list .rrow[data-i="{rnd.randrange(max(1, n))}"]'); await pg.wait_for_timeout(150)
                await tap(pg, '#r-go'); await pg.wait_for_timeout(900); continue
            if st['quit']: await tap(pg, '#q-no'); continue
            if not st['run'] or st['busy'] or st['phase'] != 'build': await pg.wait_for_timeout(100); continue
            mv = await pg.evaluate(PICK, 0.9)
            if not mv:
                if st['rolls']: await tap(pg, '#roll'); await pg.wait_for_timeout(300); continue
                break
            slot, cell, _ = mv
            await tap(pg, f'#hand .slot[data-i="{slot}"]'); await pg.wait_for_timeout(250)
            await tap(pg, f'#board .cell[data-i="{cell}"]'); await pg.wait_for_timeout(300)
            steps += 1
        fr = await pg.evaluate('window.__fr'); lt = await pg.evaluate('window.__lt')
        m1 = {m['name']: m['value'] for m in (await cdp.send('Performance.getMetrics'))['metrics']}
        prof = (await cdp.send('Profiler.stop'))['profile'] if PROF else None
        if TRACE: await b.stop_tracing()
        top = await pg.evaluate('()=>PQ.run&&PQ.run.top')
        nodes = await pg.evaluate("()=>[document.getElementsByTagName('*').length,document.getElementById('board').innerHTML.length]")
        await b.close()
    print(f'cpu x{RATE}  steps {steps}  top {top}  nodes {nodes[0]}  board html {nodes[1]//1024}KB  errors {len(errs)} {errs[:2]}')
    by = collections.defaultdict(list)
    for d, ph in fr[2:]: by[ph.rstrip('*') if ph else '?'].append(d)
    print('場面        コマ数  平均ms  95%ms  最大ms  落ちたコマ(>34ms)')
    for ph, ds in sorted(by.items(), key=lambda x: -len(x[1])):
        ds.sort(); n = len(ds)
        print(f'{ph:10s} {n:6d} {sum(ds)/n:7.1f} {ds[int(n*.95)]:6.1f} {ds[-1]:7.1f} {sum(1 for d in ds if d > 34):6d} ({100*sum(1 for d in ds if d > 34)/n:.0f}%)')
    lc = collections.Counter(); ls = collections.Counter()
    for _, d, ph in lt: lc[ph] += 1; ls[ph] += d
    print('長い処理(>50ms):', ', '.join(f'{k} {lc[k]}回 計{ls[k]:.0f}ms' for k in lc))
    for k in ('ScriptDuration', 'LayoutDuration', 'RecalcStyleDuration', 'TaskDuration'):
        print(f'{k:20s} {m1[k]-m0[k]:.2f}s')
    print('LayoutCount', m1['LayoutCount'] - m0['LayoutCount'], ' RecalcStyleCount', m1['RecalcStyleCount'] - m0['RecalcStyleCount'])
    if prof:
        nodes = {n['id']: n for n in prof['nodes']}; self_t = collections.Counter()
        dt = prof['timeDeltas'];
        for sid, d in zip(prof['samples'], dt):
            cf = nodes[sid]['callFrame']; self_t[(cf['functionName'] or '(anon)', cf['lineNumber'] + 1)] += d / 1000
        tot = sum(self_t.values())
        print('関数ごと（自分の時間）上位:')
        for (fn, ln), t in self_t.most_common(22): print(f'  {t:8.0f}ms {100*t/tot:4.1f}%  {fn} :{ln}')

def trace_sum():
    ev = json.load(open('/tmp/pq_trace.json'))
    ev = ev['traceEvents'] if isinstance(ev, dict) else ev
    th = {}
    for e in ev:
        if e.get('ph') == 'M' and e.get('name') == 'thread_name': th[(e['pid'], e['tid'])] = e['args']['name']
    agg = collections.defaultdict(lambda: collections.Counter())
    for e in ev:
        if e.get('ph') == 'X' and 'dur' in e:
            agg[th.get((e['pid'], e['tid']), '?')][e['name']] += e['dur'] / 1000
    for t in ('CrRendererMain', 'Compositor', 'CompositorTileWorker1', 'VizCompositorThread'):
        if t in agg:
            print(f'[{t}] ' + ', '.join(f'{n} {d:.0f}ms' for n, d in agg[t].most_common(12)))

asyncio.run(main())
if TRACE: trace_sum()
