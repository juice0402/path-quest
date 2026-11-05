# 11/4 リザルト画面（ゲームオーバー）の作り直し（build_stamp_1104.py のあとに1回だけ）
#  - 盤面の上にじかに白い字 → 木の額に入った紙のカードにまとめる。ふちに木の札（力つきた：ピンク / 帰還：緑）、その上に騎士
#  - 段：紙の上に大きな数字。下に「つぎの大将までの道」（1段1マス、たおれた所に騎士、さいこうの所に旗、はしに大将）と「兵隊長まで あと○段」
#  - 金貨の四角 → 「さいこう ……… 17段」「金貨 ……… +86」の点線の帳面
#  - 見つけた装備：お店と同じ色わくのマス。ぜんぶ新しいので NEW の札はなし。なければ出さない
#  - 新記録：Canva の朱肉の輪に「新記録」のはんこが ドンと押される（カードがゆれて紙ふぶき）
#  - 順番に動く：カードが落ちる → 騎士がたおれる → 段が数え上がり道がのびる → はんこ → 金貨 → 装備。画面をタップするとすぐ全部出る
#  - グラデーションと光はなし。動きを減らす設定では動かない
import sys, re
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)

# ---------- markup ----------
rep('''  <div class="ov" id="ov">
    <div class="ov-hero" id="o-hero"></div>
    <div class="ov-why" id="o-head"></div>
    <div class="ov-big"><b id="o-step">0</b><span>段</span></div>
    <div class="ov-new" id="o-new" hidden>NEW RECORD!</div>
    <div class="ov-best" id="o-best"></div>
    <div class="ov-row"><span class="pill" id="o-gold"></span></div>
    <div class="ov-found" id="o-found"></div>
''', '''  <svg class="ov-defs" width="0" height="0" aria-hidden="true"><filter id="ov-ink" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="2" result="d"/><feComponentTransfer in="n" result="m"><feFuncA type="discrete" tableValues="1 1 1 1 1 1 0 1"/></feComponentTransfer><feComposite in="d" in2="m" operator="in"/></filter></svg>
  <div class="ov" id="ov">
    <div class="ov-card" id="o-card">
      <div class="ov-hero" id="o-hero"></div>
      <div class="ov-head" id="o-head"></div>
      <div class="ov-main">
        <div class="ov-big"><b id="o-step">0</b><span>段</span></div>
        <div class="ov-stamp" id="o-new" hidden><span>新記録</span></div>
      </div>
      <div class="ov-road" id="o-road"></div>
      <div class="ov-to" id="o-to"></div>
      <div class="ov-led">
        <p><span>さいこう</span><i></i><b id="o-best"></b></p>
        <p><span>金貨</span><i></i><b id="o-gold"></b></p>
      </div>
      <div class="ov-found" id="o-foundw" hidden><div class="ov-cap">見つけた装備</div><div class="ov-gear" id="o-found"></div></div>
    </div>
''')

# ---------- the old styles of the result screen go (the buttons stay) ----------
PRE = ('.sheet.over{', '.ov{', '.ov-hero{', '.ov-hero svg{', '.ov-hero.home svg{', '.ov-why{', '.ov-big{', '.ov-big span{', '.ov-new{',
       '.ov-best{', '.ov-row{', '.ov-row .pill{', '.ov-row .pill b{', '.ov-found{', '.ov-found i{', '.ov-found i svg{', '.ov-found i::after{',
       '.ov-best svg{', '.ov-hero .ov-sh{')
L = s.split('\n'); keep = [l for l in L if not l.startswith(PRE)]
assert len(L) - len(keep) == 20, len(L) - len(keep)
s = '\n'.join(keep)

CSS = '''/* the result: a framed paper card with a plank sign on its edge and the knight on the sign (11/4) */
.sheet.over{background:rgba(36,20,28,.62);-webkit-backdrop-filter:blur(2px);backdrop-filter:blur(2px);animation:ovDim .25s both}
@keyframes ovDim{from{background-color:rgba(36,20,28,0)}}
.ov-defs{position:absolute;width:0;height:0}
.ov{position:relative;width:min(100%,360px);display:flex;flex-direction:column;align-items:center;gap:12px;color:var(--ink);text-align:center}
.ov-card{position:relative;box-sizing:border-box;width:100%;margin-top:92px;padding:34px 10px 12px;display:flex;flex-direction:column;align-items:center;
  border-style:solid;border-color:transparent;border-width:18px;border-image-source:var(--ui-frame);border-image-slice:30 fill;border-image-width:18px;border-image-repeat:stretch;
  filter:drop-shadow(0 6px 0 rgba(40,18,6,.45));animation:ovDrop .45s cubic-bezier(.3,1.35,.5,1) both}
@keyframes ovDrop{from{transform:translateY(-70px);opacity:0}}
.ov.rec .ov-card{animation:ovDrop .45s cubic-bezier(.3,1.35,.5,1) both,ovThud .24s 1.42s ease-out}
@keyframes ovThud{35%{transform:translateY(5px)}}
.ov-head{position:absolute;top:-31px;left:50%;transform:translateX(-50%);box-sizing:border-box;height:44px;min-width:210px;max-width:calc(100% + 8px);display:flex;align-items:center;justify-content:center;padding:0 6px;white-space:nowrap;
  border-style:solid;border-color:transparent;border-width:0 26px;border-image-source:var(--ui-plank-pink);border-image-slice:0 64 fill;border-image-width:0 26px;border-image-repeat:stretch;
  font:800 17px/1 var(--round);color:#fff;text-shadow:0 2px 0 #8e2f57,0 0 1px #8e2f57;filter:drop-shadow(0 3px 0 rgba(58,28,8,.45))}
.ov.home .ov-head{border-image-source:var(--ui-plank-green);text-shadow:0 2px 0 #1e5233,0 0 1px #1e5233}
.ov-hero{position:absolute;left:50%;top:-104px;width:112px;height:84px;margin-left:-56px}
.ov-hero svg{width:100%;height:100%;overflow:visible;transform:rotate(-80deg) translate(-8%,6%);filter:grayscale(.35);animation:ovFall .42s .38s cubic-bezier(.55,0,.85,.4) both}
@keyframes ovFall{0%{transform:none}78%{transform:rotate(-86deg) translate(-8%,6%)}}
.ov-hero .ov-sh{position:absolute;left:14%;right:14%;bottom:4%;height:14%;border-radius:50%;background:rgba(30,14,24,.4);animation:ovSh .42s .38s both}
@keyframes ovSh{from{transform:scaleX(.4)}}
.ov-hero.home svg{transform:none;filter:none;animation:floaty 1.6s ease-in-out infinite}
.ov-hero.home{top:-101px}
#ov .ov-sub .btn{white-space:nowrap}
.ov-main{position:relative;width:100%;display:flex;justify-content:center;margin-top:4px}
.ov-big{display:flex;align-items:baseline;gap:4px;font:400 66px/1 var(--disp);color:var(--ink);font-variant-numeric:tabular-nums;text-shadow:0 3px 0 rgba(176,111,60,.22)}
.ov-big span{font-size:24px}
.ov-stamp{position:absolute;right:0;top:-12px;width:86px;height:86px;display:grid;place-items:center;background:var(--ui-stamp) center/contain no-repeat;transform:rotate(-14deg);opacity:.9;mix-blend-mode:multiply;pointer-events:none;animation:ovStamp .2s 1.25s cubic-bezier(.5,0,.9,.5) both}
.ov-stamp[hidden]{display:none}
.ov-stamp span{font:400 19px/1 var(--disp);color:#c42a2e;filter:url(#ov-ink)}
@keyframes ovStamp{from{transform:rotate(-14deg) scale(2.6);opacity:0}}
.ov-road{display:flex;align-items:flex-end;gap:6px;width:100%;box-sizing:border-box;padding:0 2px 0 6px;margin-top:22px}
.rd-pips{position:relative;flex:1;display:flex;gap:2px;height:12px;margin-bottom:5px}
.rd-pips i{flex:1;border-radius:2px;background:rgba(74,53,65,.12)}
.rd-pips i.on{background:#e4a24f;box-shadow:inset 0 -3px 0 #b06a2c;animation:pipOn .2s calc(.5s + var(--d)) both}
@keyframes pipOn{from{background:rgba(74,53,65,.12);box-shadow:none;transform:scaleY(.4)}}
.rd-pips u{position:absolute;bottom:9px;width:30px;height:30px;transform:translateX(-50%);animation:ovPop .25s calc(.5s + var(--d)) cubic-bezier(.3,1.6,.5,1) both}
.rd-pips s{position:absolute;bottom:10px;width:22px;height:22px;transform:translateX(-25%)}
.rd-pips u svg,.rd-pips s svg{display:block;width:100%;height:100%}
@keyframes ovPop{from{transform:translateX(-50%) scale(0)}}
.rd-boss{flex:none;width:38px;height:46px}
.rd-boss svg{display:block;width:100%;height:100%;overflow:visible}
.ov-to{margin-top:6px;font:800 13px/1.2 var(--round);color:rgba(74,53,65,.66)}
.ov-led{width:100%;box-sizing:border-box;margin-top:14px;padding:0 6px;display:flex;flex-direction:column;gap:8px}
.ov-led p{display:flex;align-items:center;margin:0;font:800 15px/1 var(--round);color:rgba(74,53,65,.75);animation:ovIn .3s .85s both}
.ov-led p+p{animation-delay:.95s}
.ov-led p>i{flex:1;height:0;margin:4px 8px 0;border-bottom:3px dotted rgba(74,53,65,.25)}
.ov-led b{display:flex;align-items:center;gap:3px;font:800 22px/1 var(--round);color:var(--ink);font-variant-numeric:tabular-nums}
.ov-led small{font-size:14px;margin-left:1px}
.ov-led svg{width:24px;height:24px}
#o-gold b{color:var(--gold)}
@keyframes ovIn{from{opacity:0;transform:translateY(8px)}}
.ov-found{width:100%;margin-top:16px}
.ov-found[hidden]{display:none}
.ov-cap{display:flex;align-items:center;gap:8px;margin-bottom:8px;font:800 13px/1 var(--round);color:rgba(74,53,65,.66)}
.ov-cap::before,.ov-cap::after{content:"";flex:1;height:2px;background:rgba(74,53,65,.16)}
.ov-gear{display:flex;flex-wrap:wrap;justify-content:center;gap:6px}
.ov-gear i{position:relative;width:46px;height:46px;border-radius:3px;background:#f6ede1;box-shadow:inset 0 0 0 2px var(--rc,#b9a998),0 2px 0 rgba(74,53,65,.18);animation:ovPop2 .3s calc(1.2s + var(--k) * .1s) cubic-bezier(.3,1.6,.5,1) both}
.ov-gear i svg{position:absolute;inset:3px;width:40px;height:40px}
.ov-gear .r1{--rc:#b9a998}.ov-gear .r2{--rc:#5f97de}.ov-gear .r3{--rc:#e0a12a}.ov-gear .r4{--rc:#c4467a}
@keyframes ovPop2{from{transform:scale(0) rotate(-12deg)}}
#ov .ov-go,#ov .ov-sub{animation:ovIn .3s .55s both}
#ov .ov-sub{animation-delay:.62s}
.sheet.over{overflow-y:auto;align-items:safe center}
/* a short phone: a smaller knight, number and gear so the card and the planks fit */
@media (max-height:760px){
  .ov{gap:10px}.ov-card{margin-top:72px;padding:30px 8px 10px}
  .ov-hero{top:-84px;width:90px;height:68px;margin-left:-45px}.ov-hero.home{top:-81px}
  .ov-big{font-size:52px}.ov-big span{font-size:20px}.ov-stamp{width:76px;height:76px;top:-10px}.ov-stamp span{font-size:17px}
  .ov-road{margin-top:16px}.ov-led{margin-top:10px;gap:6px}.ov-led b{font-size:19px}.ov-led svg{width:21px;height:21px}
  .ov-found{margin-top:10px}.ov-cap{margin-bottom:6px}.ov-gear i{width:40px;height:40px}.ov-gear i svg{width:34px;height:34px}
  .ov .ov-go{min-height:54px}.ov-sub .btn,.ov .ov-sub .btn.play{min-height:46px}
}
/* a tap shows everything at once */
#ov.fin .ov-card,#ov.fin .ov-card *,#ov.fin .ov-go,#ov.fin .ov-sub{animation:none}
#ov.fin .ov-hero.home svg{animation:floaty 1.6s ease-in-out infinite}
@media (prefers-reduced-motion:reduce){#ov .ov-card,#ov .ov-card *,#ov .ov-go,#ov .ov-sub,.sheet.over{animation:none!important}}
'''
rep('/* ===== end of 11/4 ===== */', CSS + '/* ===== end of 11/4 ===== */')

# ---------- the result in order ----------
m = re.search(r"function gameOver\(why\)\{.*?\n  if\(best\)setTimeout\(confetti,REDUCED\?0:500\);\n\}\n", s, re.S)
assert m and s.count('function gameOver(why){') == 1
s = s[:m.start()] + r'''let ovQ=[]; // what the result screen still has to show; a tap shows it all at once
function ovAt(ms,f,show){if(REDUCED)return f();const j={f,show};j.t=setTimeout(()=>{ovQ=ovQ.filter(x=>x!==j);f()},ms);ovQ.push(j)}
function ovFlush(){const q=ovQ;ovQ=[];q.forEach(j=>{clearTimeout(j.t);if(!j.show)j.f()});skipCount();$('ov').classList.add('fin')}
const isGate=g=>g>0&&(g%SPAN===0||g%DIM_LEN===0);
function ovRoad(step,far0){ // the way to the next captain: a block for each step, the knight where he stopped, the flag at the best so far
  let a=step;while(a>0&&!isGate(a))a--;
  let z=step+1;while(!isGate(z))z++;
  const n=z-a,k=step-a,king=z%DIM_LEN===0,dt=Math.min(40,600/Math.max(1,k)),at=q=>`${(Math.max(0,q-.5)/n*100).toFixed(2)}%`;
  let h='';for(let q=1;q<=n;q++)h+=q<=k?`<i class="on" style="--d:${Math.round((q-1)*dt)}ms"></i>`:'<i></i>';
  if(far0>step&&far0<z)h+=`<s style="left:${at(far0-a)}">${ico(SPR.flag)}</s>`;
  h+=`<u style="left:${at(k)};--d:${Math.round(k*dt)}ms">${svg(SPR.hero)}</u>`;
  const art=king&&document.getElementById('a-king')?`<svg viewBox="-4 -32 108 132" aria-hidden="true">${U('king',-2,-30,104,124)}</svg>`
    :document.getElementById('a-boss')?`<svg viewBox="2 -22 96 134" aria-hidden="true">${U('boss',4,-20,92,110)}</svg>`:svg(SPR.boss);
  $('o-road').innerHTML=`<div class="rd-pips">${h}</div><b class="rd-boss">${art}</b>`;
  $('o-to').textContent=`${king?'王さま':'兵隊長'}まで あと${z-step}段`;
}
function gameOver(why){
  if(!run)return;
  const step=stepOf(run.top),far0=meta.far,best=step>far0&&step>0,gold=run.gold,found=(run.found||[]).slice();
  meta.bank+=gold;meta.far=Math.max(meta.far,step);saveMeta();
  const p=(dimOf(run.top)?dimName(dimOf(run.top))+' ':'')+areaOf(rowOf(run.at)).n,home=why==='quit';
  const head={hp:`${p}で力つきた`,dead:`${p}で行き止まり`,nofit:`${p}で道がとぎれた`,quit:`${p}から帰還`};
  $('o-head').textContent=head[why]||head.quit;
  $('o-hero').innerHTML=home?svg(SPR.hero):'<i class="ov-sh" aria-hidden="true"></i>'+svg(SPR.hero.replace(/^<ellipse[^>]*\/>/,'')); // fallen: his shadow lies flat under him, it does not turn with him
  $('o-hero').classList.toggle('home',home);
  const ov=$('ov');ov.classList.toggle('home',home);ov.classList.toggle('rec',best);ov.classList.remove('fin');
  $('o-new').hidden=!best;
  $('o-best').innerHTML=`${ico(SPR.flag)}${nf(meta.far)}<small>段</small>`;
  ovRoad(step,far0);
  lastFound=found.length;$('o-foundw').hidden=!found.length;
  $('o-found').innerHTML=found.slice(0,8).map((id,k)=>{const g=GEAR_ID[id];return g?`<i class="r${g.r}" style="--k:${k}" title="${g.n}">${ico(g.art)}</i>`:''}).join('');
  $('o-shop-i').innerHTML=ico(ICON_UP_F());$('o-home-i').innerHTML=ico(SPR.door);
  $('o-gold').innerHTML=`${ico(SPR.coin)}<b>+0</b>`;$('o-step').textContent='0';
  store.del(SAVE);run=null;busy=false;aim=null;hideSay();
  ovQ.forEach(j=>clearTimeout(j.t));ovQ=[];skipCount();
  hideSheets();show('s-over');$('o-dot').hidden=!affordable();
  ovAt(450,()=>countUp($('o-step'),step,650)); // the card has landed
  ovAt(1000,()=>countUp($('o-gold').querySelector('b'),gold,700,'+'));
  if(best)ovAt(1450,confetti,1); // the stamp has come down
}
''' + s[m.end():]

rep("$('s-over').addEventListener('click',e=>{if(!e.target.closest('button'))skipCount()});",
    "$('s-over').addEventListener('click',()=>ovFlush()); // a tap shows the rest at once (a button too, so nothing runs on after it)")
open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
