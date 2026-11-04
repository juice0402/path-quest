# 11/4 夕方 u の続き：テスト用に騎士くんのポーズと敵のくせを PQ から使えるようにする（1回だけ当てる）
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    c = s.count(old); assert c == n, (c, old[:90]); s = s.replace(old, new)
rep('gateFrom,dmgFor,targets,', 'gateFrom,dmgFor,targets,heroPose,heroBase,toyAct,fightRules,QK,')

# the big captain and king show their habit too (the small toy under them is hidden)
rep("""function bossAct(i){ // the big captain or king throws his weight forward
  if(REDUCED)return;const b=board.querySelector(`:scope>.bboss[data-i="${i}"] .bb-b`);if(!b)return toyAct(i,'atk');
  b.animate([{translate:'0% 0%',scale:'1'},{translate:'0% -4%',scale:'.96 1.06',offset:.3},{translate:'0% 3%',scale:'1.08 .94',offset:.55},{translate:'0% 0%',scale:'1'}],{duration:340,easing:'ease-out'});
}""", """function bossAct(i,kind){ // the big captain or king: throws his weight forward, swells up angry, or winds himself back
  if(REDUCED)return;const b=board.querySelector(`:scope>.bboss[data-i="${i}"] .bb-b`);if(!b)return toyAct(i,kind||'atk');
  const K={
    atk:[[{translate:'0% 0%',scale:'1'},{translate:'0% -4%',scale:'.96 1.06',offset:.3},{translate:'0% 3%',scale:'1.08 .94',offset:.55},{translate:'0% 0%',scale:'1'}],340],
    rage:[[{scale:'1',filter:'brightness(1)'},{scale:'1.14 1.1',filter:'brightness(1.25)',offset:.35},{scale:'1.04',offset:.7},{scale:'1',filter:'brightness(1)'}],560],
    wind:[[{rotate:'0deg'},{rotate:'-7deg',offset:.2},{rotate:'7deg',offset:.4},{rotate:'-4deg',offset:.6},{rotate:'0deg',scale:'1.08',offset:.8},{rotate:'0deg',scale:'1'}],640]
  }[kind||'atk'];if(K)b.animate(K[0],{duration:K[1],easing:'ease-out'});
}""")
rep("""    if(w==='wind'){toyAct(i,'wind',e);""", """    if(w==='wind'){e.boss?bossAct(i,'wind'):toyAct(i,'wind',e);""")
rep("""    if(w==='rage'){toyAct(i,'rage',e);""", """    if(w==='rage'){e.boss?bossAct(i,'rage'):toyAct(i,'rage',e);""")
# the ghost with its ball is wide: a little narrower, so the screen's edge does not cut it
rep("ghost:[84,20,110]", "ghost:[80,20,96]")
# a new climb: he stands breathing from the start
rep("hero.classList.remove('down','kop');app.classList.remove('ko');heroBase('front');", "hero.classList.remove('down','kop');app.classList.remove('ko');heroBase('front');hero.classList.add('idle');")
open(P, 'w', encoding='utf-8').write(s); print('ok')
# renderBoard runs on every full redraw: only undo the fallen pose there, never a walking or fighting one
s = open(P, encoding='utf-8').read()
rep("hero.classList.remove('down','kop');app.classList.remove('ko');heroBase('front');hero.classList.add('idle');",
    "hero.classList.remove('down','kop');app.classList.remove('ko');if(HS.cur.startsWith('ko/'))heroBase('front');if(run.phase==='build'&&!busy&&HS.base==='front')hero.classList.add('idle');")
open(P, 'w', encoding='utf-8').write(s); print('ok fix')
# a new climb starts with him facing us, whatever he did last time
s = open(P, encoding='utf-8').read()
rep("""function newRun(){
  const u=meta.up,q=gearSum(meta.gear.eq); // the gear is fixed when the climb starts""", """function newRun(){
  if(HS){HS.base='front';HS.bflip=false;heroPose('front',0,false)} // HS is set further down the page
  const u=meta.up,q=gearSum(meta.gear.eq); // the gear is fixed when the climb starts""")
open(P, 'w', encoding='utf-8').write(s); print('ok newRun')
