# 11/6 1コマの重さ：動いているあいだ（毎コマ描きなおすとき）の main thread の1コマぶんの時間を、中身ごとに出す
# usage: python3 tools/test/frame_cost.py [cpu の遅さ(倍)] ['試しの CSS']   JS='()=>…' で始める前にページで動かす  PQ_FILE=_old.html で前の版
#   画面は Android（412x915・2.625倍）。どれかの動きだけ動かす例: JS="()=>document.getAnimations().forEach(a=>{if(a.animationName!=='tw')a.pause()})"
import asyncio, json, sys, os, collections
from playwright.async_api import async_playwright
URL='file://'+os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../games/path-quest/'))+'/'+os.environ.get('PQ_FILE','index.html')+'#fxtest'
RATE=float(sys.argv[1]) if len(sys.argv)>1 else 4
CSS=sys.argv[2] if len(sys.argv)>2 else ''
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        ctx=await b.new_context(viewport={'width':412,'height':915},device_scale_factor=2.625,is_mobile=True,has_touch=True)
        await ctx.add_init_script("{let x=99;Math.random=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return ((x>>>0)%1e6)/1e6}}")
        await ctx.add_init_script("try{localStorage.clear();localStorage.setItem('pathquest.meta.v1',JSON.stringify({bank:0,best:12,far:12,seen:1,up:{hp:2,atk:2},sk:{own:['turn'],eq:['turn',null,null]}}))}catch(e){}")
        pg=await ctx.new_page();await pg.goto(URL);await pg.wait_for_timeout(700)
        await pg.click('#t-new');await pg.wait_for_timeout(1500)
        if CSS: await pg.add_style_tag(content=CSS)
        if os.environ.get('JS'): await pg.evaluate(os.environ['JS'])
        await pg.wait_for_timeout(300)
        lay=await pg.evaluate("()=>document.getAnimations().filter(a=>a.playState==='running').length")
        print('running',lay)
        cdp=await ctx.new_cdp_session(pg);await cdp.send('Emulation.setCPUThrottlingRate',{'rate':RATE})
        await pg.wait_for_timeout(300)
        await b.start_tracing(page=pg,path='/tmp/pq_frame.json',categories=['devtools.timeline','disabled-by-default-devtools.timeline'])
        n=await pg.evaluate("()=>new Promise(r=>{let n=0;const t0=performance.now();const f=()=>{n++;if(performance.now()-t0<2000)requestAnimationFrame(f);else r(n)};requestAnimationFrame(f)})")
        await b.stop_tracing()
        await b.close()
    ev=json.load(open('/tmp/pq_frame.json'));ev=ev['traceEvents'] if isinstance(ev,dict) else ev
    th={(e['pid'],e['tid']):e['args']['name'] for e in ev if e.get('ph')=='M' and e.get('name')=='thread_name'}
    agg=collections.Counter()
    for e in ev:
        if e.get('ph')=='X' and th.get((e['pid'],e['tid']))=='CrRendererMain' and 'dur' in e: agg[e['name']]+=e['dur']/1000/n
    print(f'frames {n}; per frame:',', '.join(f'{k} {v:.2f}' for k,v in agg.most_common(16)))
asyncio.run(main())
