# 11/4 その2：tweak_1104.py のあとの index.html に1回だけ当てる
#  1. メッセージ窓：1行ずつ5秒ほど残す。続けて来たら下に足す（3行まで、古い行から消える）
#  2. スキル：説明文をなくし、クールタイム（何マス休むか）を出す（強化画面の紙と、遊ぶ画面の紙）
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()

def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, old[:100])
    s = s.replace(old, new)

# ---------- 1. the message window keeps each line about 5 seconds ----------
rep('''/* the message window under the status (11/4): one short line at a time for about a second, ▶ in front —
   red when it helps the knight, blue when it hurts. lines wait while a sheet covers the field */
function note(t,k){
  if(!t)return;const q=note.q||(note.q=[]);q.push({t,k:k||''});if(q.length>6)q.splice(0,q.length-6);
  if(!note.on)noteNext();
}
function noteNext(){
  const q=note.q||[],el=$('say');clearTimeout(note.t);
  if(!q.length){note.on=false;el.hidden=true;return}
  note.on=true;
  if(SHEETS.some(id=>!$(id).hidden)){el.hidden=true;note.t=setTimeout(noteNext,250);return}
  const m=q.shift();el.className='say'+(m.k?' '+m.k:'');el.innerHTML='<i class="cur" aria-hidden="true"></i><span></span>';el.lastChild.textContent=m.t;el.hidden=false;
  if(!REDUCED){el.classList.remove('in');void el.offsetWidth;el.classList.add('in')}
  note.t=setTimeout(noteNext,q.length?850:1100);
}
function say(t){note(t)}
function hideSay(){clearTimeout(note.t);note.q=[];note.on=false;$('say').hidden=true;hidePick()}''',
'''/* the message window under the status (11/4): short lines with ▶ in front, each staying about 5 seconds —
   red when it helps the knight, blue when it hurts. a new line goes under the last (3 at most, the oldest leaves first).
   lines wait while a sheet covers the field */
const NOTE_MS=5000,NOTE_MAX=3;
function note(t,k){
  if(!t)return;(note.q||(note.q=[])).push({t,k:k||''});noteFlush();
}
function noteFlush(){
  const q=note.q||[],el=$('say');clearTimeout(note.w);if(!q.length)return;
  if(SHEETS.some(id=>!$(id).hidden)){note.w=setTimeout(noteFlush,250);return}
  while(q.length){
    const m=q.shift(),ln=document.createElement('div');ln.className='ln'+(m.k?' '+m.k:'')+(REDUCED?'':' in');
    ln.innerHTML='<i class="cur" aria-hidden="true"></i><span></span>';ln.lastChild.textContent=m.t;el.appendChild(ln);
    while(el.children.length>NOTE_MAX)el.firstChild.remove();
    setTimeout(()=>ln.classList.add('out'),NOTE_MS-300);
    setTimeout(()=>{ln.remove();if(!el.children.length)el.hidden=true},NOTE_MS);
  }
  el.hidden=false;
}
function say(t){note(t)}
function hideSay(){clearTimeout(note.w);note.q=[];const el=$('say');el.innerHTML='';el.hidden=true;hidePick()}''')
rep('''.say{left:8px;right:8px;top:calc(var(--hudh) + 4px);transform:none;width:auto;max-width:none;display:flex;align-items:center;gap:7px;min-height:38px;padding:6px 14px;border-radius:2px;''',
    '''.say{left:8px;right:8px;top:calc(var(--hudh) + 4px);transform:none;width:auto;max-width:none;display:flex;flex-direction:column;align-items:stretch;gap:3px;min-height:38px;padding:8px 14px;border-radius:2px;''')
rep('''.say>span{min-width:0;overflow:hidden;text-overflow:ellipsis}
.say .cur{flex:none;width:0;height:0;border-left:9px solid currentColor;border-top:6px solid transparent;border-bottom:6px solid transparent}
.say.good{color:#cf2338}
.say.bad{color:#2456c4}
.say.in{animation:sayin .14s ease-out}
@keyframes sayin{from{opacity:0;transform:translateY(-4px)}}
@media (prefers-reduced-motion:reduce){.say.in{animation:none}}''', '''.say .ln{display:flex;align-items:center;gap:7px;min-width:0;transition:opacity .3s}
.say .ln>span{min-width:0;overflow:hidden;text-overflow:ellipsis}
.say .cur{flex:none;width:0;height:0;border-left:9px solid currentColor;border-top:6px solid transparent;border-bottom:6px solid transparent}
.say .ln.good{color:#cf2338}
.say .ln.bad{color:#2456c4}
.say .ln.in{animation:sayin .14s ease-out}
.say .ln.out{opacity:0}
@keyframes sayin{from{opacity:0;transform:translateY(-4px)}}''')

# ---------- 2. skills: no description, the cool time instead ----------
# the shop's pinned paper
rep("    const what=`${SKILL_AIM[k.aim]||'すぐ効く'}　使うと${k.ct}マス休む`;\n", '')
rep('''`<div class="dt-body"><p class="dt-d">${k.d}</p><p class="dt-d dim">${what}</p></div><div class="dt-foot">${foot}</div>`;''',
    '''`<div class="dt-body"><p class="dt-ct"><span>クールタイム</span><b>${k.ct}</b><span>マス</span></p></div><div class="dt-foot">${foot}</div>`;''')
# the paper on the play screen: the name with its cool time; a second line only for what to do now
rep('''  let line,btns='<button class="sb-x" type="button" data-sb="x">やめる</button>';
  if(s.cd>0){line=`あと${s.cd}マス歩くと使える`;btns='<button class="sb-x" type="button" data-sb="x">とじる</button>'}
  else if(note)line=note;
  else if(d.aim)line=`<span class="do">${AIM_SAY[d.id]}</span>`;
  else{line=d.d;btns+='<button class="sb-go" type="button" data-sb="go">使う</button>'}
  el.innerHTML=`<span class="sb-ic">${svg(SK_ART[d.id])}</span><div class="sb-t"><b>${d.n}</b>${line.startsWith('<span')?line:`<span>${line}</span>`}</div><div class="sb-b">${btns}</div>`;''',
'''  let line='',btns='<button class="sb-x" type="button" data-sb="x">やめる</button>';const ct=Math.max(1,d.ct-qv('cdr'));
  if(s.cd>0){line=`あと${s.cd}マス歩くと使える`;btns='<button class="sb-x" type="button" data-sb="x">とじる</button>'}
  else if(note)line=note;
  else if(d.aim)line=`<span class="do">${AIM_SAY[d.id]}</span>`;
  else btns+='<button class="sb-go" type="button" data-sb="go">使う</button>';
  el.innerHTML=`<span class="sb-ic">${svg(SK_ART[d.id])}</span><div class="sb-t"><b>${d.n}<em class="ct">クールタイム ${ct}マス</em></b>${!line?'':line.startsWith('<span')?line:`<span>${line}</span>`}</div><div class="sb-b">${btns}</div>`;''')
rep('/* ===== end of 11/4 ===== */', '''/* skills: the cool time in place of the description */
.dt-ct{margin:2px 0 0;display:flex;align-items:baseline;gap:6px;font:800 14px/1 var(--round);color:var(--ink)}
.dt-ct b{font:400 30px/1 var(--disp);color:var(--frame);font-variant-numeric:tabular-nums}
.skn .sb-t b .ct{display:inline-block;margin-left:8px;padding:2px 6px;border-radius:2px;background:#efe2cc;font:800 11px/1.3 var(--round);font-style:normal;color:var(--frame);vertical-align:2px}
/* ===== end of 11/4 ===== */''')

open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
