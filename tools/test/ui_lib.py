# shared helpers for the PATH QUEST screen/shop checks (ui_check.py)
import os, json, asyncio
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.abspath(os.path.join(HERE, '../../games/path-quest/index.html')) + '#fxtest'
TAP = """el=>{const r=el.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2,o={bubbles:true,cancelable:true,clientX:x,clientY:y,pointerId:7,pointerType:'touch',isPrimary:true,button:0};
  el.dispatchEvent(new PointerEvent('pointerdown',{...o,buttons:1}));document.dispatchEvent(new PointerEvent('pointerup',{...o,buttons:0}));}"""
VIS = "id=>{const e=document.getElementById(id);return !!e&&!e.hidden}"
ISSUES = []
def issue(sev, msg):
    ISSUES.append((sev, msg)); print('  !!', sev, msg, flush=True)
def meta(bank=99999, far=0, **kw):
    m = dict(bank=bank, best=far, far=far, seen=0, up={}, gear=dict(own=[], eq={}), sk=dict(own=['turn'], eq=['turn', None, None]), newg=[], newu=[])
    m.update(kw); return m
class Sess:
    def __init__(s): s.errs = []
    async def start(s, w=390, h=844, reduced='reduce', audio=False, touch=True):
        s.p = await async_playwright().start()
        a = ['--no-sandbox'] + (['--autoplay-policy=no-user-gesture-required'] if audio else [])
        s.b = await s.p.chromium.launch(executable_path='/usr/bin/google-chrome', args=a)
        s.ctx = await s.b.new_context(viewport={'width': w, 'height': h}, has_touch=touch, reduced_motion=reduced)
        s.pg = await s.ctx.new_page(); s.hook(s.pg); return s
    def hook(s, pg):
        pg.on('pageerror', lambda e: s.errs.append('pageerror[' + getattr(s, 'label', '') + ']: ' + (str(getattr(e, 'stack', '') or e)[:420])))
        pg.on('console', lambda m: s.errs.append('console: ' + m.text[:300]) if m.type == 'error' and 'ERR_' not in m.text else None)
    async def goto(s, run=None, mt=None, snd=None, extra=None):
        """open, seed localStorage, reload (same page object, so callers can keep `pg`)"""
        pg = s.pg
        await pg.goto(URL); await pg.evaluate("()=>{try{localStorage.clear()}catch(e){}}")
        seed = {}
        if mt is not None: seed['pathquest.meta.v1'] = mt if isinstance(mt, str) else json.dumps(mt)
        if run is not None: seed['pathquest.run.v3'] = run if isinstance(run, str) else json.dumps(run)
        if snd is not None: seed['pq.snd'] = snd
        if extra: seed.update(extra)
        await pg.evaluate("s=>{for(const k in s)localStorage.setItem(k,s[k])}", seed)
        await pg.reload(); await pg.wait_for_timeout(500); return pg
    async def reload(s):
        await s.pg.reload(); await s.pg.wait_for_timeout(500)
    async def click(s, sel):
        el = await s.pg.query_selector(sel)
        if not el: return False
        await s.pg.evaluate('el=>el.click()', el); return True
    async def tap(s, sel):
        el = await s.pg.query_selector(sel)
        if not el: return False
        await s.pg.evaluate(TAP, el); return True
    async def vis(s, id): return await s.pg.evaluate(VIS, id)
    async def screen(s):
        return await s.pg.evaluate("()=>['s-title','s-reward','s-quit','s-over','s-shop'].filter(i=>!document.getElementById(i).hidden)")
    async def idle(s, ms=8000):
        for _ in range(ms // 60):
            st = await s.pg.evaluate("()=>({busy:PQ.busy,ph:PQ.run&&PQ.run.phase})")
            if not st['busy']: return st
            await s.pg.wait_for_timeout(60)
        return await s.pg.evaluate("()=>({busy:PQ.busy,ph:PQ.run&&PQ.run.phase,stuck:1})")
    async def stop(s):
        await s.b.close(); await s.p.stop()

# one real placement: tap the hand slot then the cell (the page's own pointer path); returns True if a block was put
PLACE_PICK = """()=>{const r=PQ.run;if(!r||r.phase!=='build'||PQ.busy)return null;const F=PQ.frontier(),out=[];
  const open=(j,m)=>{let n=0,up=0;for(const b of [1,2,8]){if(!(m&b))continue;const q=PQ.rowOf(j)+(b===1?1:0),c=PQ.colOf(j)+(b===2?1:b===8?-1:0);if(c<0||c>5)continue;const x=PQ.cellAt(PQ.idOf(q,c));if(x&&!x.rock&&!x.foe&&!x.tile&&!x.start){n++;if(b===1)up=1}}return [n,up]};
  r.hand.forEach((t,k)=>{if(!t)return;const js=[...F.keys()].concat(F.rock?[...F.rock.keys()]:[]);for(const j of js)if(PQ.fits(t,j,F)){const [n,up]=open(j,t.m);const foe=t.e&&t.e.k==='foe'?1:0;out.push([k,j,PQ.rowOf(j)*4+n*3+up*4-foe*2+Math.random()*3,n])}});
  if(!out.length)return null;out.sort((a,b)=>b[2]-a[2]);const ok=out.filter(x=>x[3]>0);const L=ok.length?ok:out;return [L[0][0],L[0][1],L[0][2]]}"""
async def place_one(S):
    pg = S.pg
    b = await pg.evaluate(PLACE_PICK)
    for _ in range(3):
        if b: break
        if not await pg.evaluate("!!PQ.run&&PQ.run.phase==='build'&&!PQ.busy&&PQ.run.rolls>0"): return False
        await S.click('#roll'); await pg.wait_for_timeout(350); b = await pg.evaluate(PLACE_PICK)
    if not b: return False
    k, j, _ = b
    await pg.evaluate("([k,j])=>{const s=document.querySelector('#hand .slot[data-i=\"'+k+'\"]');const c=document.querySelector('#board .cell[data-i=\"'+j+'\"]');window.__s=s;window.__c=c}", [k, j])
    ok = await pg.evaluate("()=>!!(window.__s&&window.__c)")
    if not ok:
        await pg.evaluate("([j,k])=>PQ.place(j,k)", [j, k]); return True
    await pg.evaluate("el=>el", None)
    await pg.evaluate(TAP, await pg.evaluate_handle("window.__s")); await pg.wait_for_timeout(60)
    await pg.evaluate(TAP, await pg.evaluate_handle("window.__c"))
    return True
