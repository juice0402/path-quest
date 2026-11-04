# 11/5 帰還の確認の画面を、結果の画面と同じ木と紙に（緑の札・帳面の行・木のボタン・後ろ姿の騎士くん）
import sys
P='games/path-quest/index.html'
s=open(P,encoding='utf-8').read()
R=[
 ('''<div class="sheet" id="s-quit" hidden>
  <div class="card">
    <h2>帰還する？</h2>
    <p id="q-text"></p>
    <div class="inv" id="q-inv" aria-label="もちもの"></div>
    <div class="row"><button class="btn main" id="q-no" type="button">つづける</button><button class="btn" id="q-yes" type="button">帰還する</button></div>
  </div>
</div>''',
 '''<div class="sheet over" id="s-quit" hidden>
  <div class="ov home qv">
    <div class="ov-card">
      <div class="ov-hero home" id="q-hero"></div>
      <div class="ov-head">帰還する？</div>
      <div class="ov-led">
        <p><span>いまの段</span><i></i><b id="q-step"></b></p>
        <p><span>持ち帰る金貨</span><i></i><b id="q-gold"></b></p>
      </div>
      <div class="ov-found" id="q-foundw" hidden><div class="ov-cap">見つけた装備</div><div class="ov-gear" id="q-found"></div></div>
      <div class="ov-found"><div class="ov-cap">この冒険のおもちゃ</div><div class="inv" id="q-inv" aria-label="もちもの"></div></div>
    </div>
    <div class="ov-sub">
      <button class="btn main play" id="q-no" type="button">つづける</button>
      <button class="btn main" id="q-yes" type="button"><span class="bi" id="q-door"></span>帰還する</button>
    </div>
  </div>
</div>'''),
 ("$('q-text').textContent=`ここまでの金貨 ${run.gold} を持ち帰って、強化に使える。`;renderInv($('q-inv'));show('s-quit');",
  "quitSheet();show('s-quit');"),
 ("$('q-no').addEventListener('click',hideSheets);",
  """function quitSheet(){ /* the return paper: wood and paper like the result, the knight turned toward home */
  const found=run.found||[];
  $('q-hero').innerHTML=svg(SHADOW(20)+U('hback',16,-6,68,94));
  $('q-step').innerHTML=`${nf(stepOf(run.top))}<small>段</small>`;
  $('q-gold').innerHTML=`${ico(SPR.coin)}+${nf(run.gold)}`;
  $('q-foundw').hidden=!found.length;
  $('q-found').innerHTML=found.slice(0,8).map((id,k)=>{const g=GEAR_ID[id];return g?`<i class="r${g.r}" style="--k:${k}" title="${g.n}">${ico(g.art)}</i>`:''}).join('');
  $('q-door').innerHTML=ico(SPR.door);renderInv($('q-inv'));
}
$('q-no').addEventListener('click',hideSheets);"""),
]
for a,b in R:
  n=s.count(a)
  if n!=1: sys.exit(f'NG {n}: {a[:60]}')
  s=s.replace(a,b)
css='''
/* the return paper (11/5) */
.qv .ov-card{margin-top:96px;padding-top:30px}
.qv .ov-led{margin-top:10px}
.qv .ov-led p{animation-delay:.25s}.qv .ov-led p+p{animation-delay:.32s}
.qv .ov-gear i{animation-delay:calc(.35s + var(--k) * .06s)}
.qv .ov-found{margin-top:14px}
.qv .inv .ig>small{color:rgba(74,53,65,.66)}
.qv .inv i.empty{background:#f3e8da;box-shadow:inset 0 0 0 2px #d8c1a6}
.qv .ov-sub .btn{white-space:nowrap;gap:6px;padding-left:4px;padding-right:4px}
.qv .ov-sub .bi svg{width:24px;height:24px}
.qv .ov-hero.home svg{animation:floaty 1.6s ease-in-out infinite}
'''
a='@keyframes ovThud{35%{transform:translateY(5px)}}'
if s.count(a)!=1: sys.exit('NG css anchor')
s=s.replace(a,a+css)
open(P,'w',encoding='utf-8').write(s)
print('ok')
