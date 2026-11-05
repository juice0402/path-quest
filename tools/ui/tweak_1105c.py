# 11/5 音（#2）：ホームの音の切りかえボタン、効果音をゲームの動きにつなぐ、結果の画面の曲。音のしくみ本体は tools/audio/build_sound.py
import sys
P='games/path-quest/index.html'
s=open(P,encoding='utf-8').read()
R=[
 # the sound button on the home screen
 ('<div class="sheet solid" id="s-title">\n  <div class="stars" id="t-stars" aria-hidden="true"></div>',
  '<div class="sheet solid" id="s-title">\n  <div class="stars" id="t-stars" aria-hidden="true"></div>\n  <button class="sq-btn snd" id="t-snd" type="button" aria-label="音" aria-pressed="true"></button>'),
 # the knight swings, the toy hits back
 ("heroPose('swing',260,fl);lunge(dx,dy);","SND('swing');heroPose('swing',260,fl);lunge(dx,dy);"),
 ("heroPose(b?'hurt':'block',300,b?false:fl);","heroPose(b?'hurt':'block',300,b?false:fl);if(!b)SND('block');"),
 # the toys' own moves (also when moving less)
 ("  if(REDUCED)return;const el=elOf(i),g=el&&el.querySelector('.toy');if(!g)return;",
  "  SND('t_'+kind);if(REDUCED)return;const el=elOf(i),g=el&&el.querySelector('.toy');if(!g)return;"),
 ("  if(REDUCED)return;const b=board.querySelector(`:scope>.bboss[data-i=\"${i}\"] .bb-b`);if(!b)return toyAct(i,kind||'atk');",
  "  if(REDUCED)return SND('t_'+(kind||'atk'));const b=board.querySelector(`:scope>.bboss[data-i=\"${i}\"] .bb-b`);if(!b)return toyAct(i,kind||'atk');SND('t_'+(kind||'atk'));"),
 # gold, candy, treasure
 ("const addGold=v=>{const n=gainOf(v);run.gold+=n;return n};","const addGold=v=>{const n=gainOf(v);run.gold+=n;if(n>0)SND('coin');return n};"),
 ("fly(i,SPR.heart,$('hp'));heroPose('eat',600)","fly(i,SPR.heart,$('hp'));SND('eat');heroPose('eat',600)"),
 ("fly(i,SPR.heart,$('hp'));heroPose('eat',700)","fly(i,SPR.heart,$('hp'));SND('eat');heroPose('eat',700)"),
 ("takeGear(i,e);heroPose('lift',900)","takeGear(i,e);SND('chest');heroPose('lift',900)"),
 # cannot place
 ("if(!fits(t,j,F)){flashCell(j);flashSlot(hi);return}","if(!fits(t,j,F)){SND('nope');flashCell(j);flashSlot(hi);return}"),
 # rewards
 ("  heroPose('cheer',900);heroHop();\n  if(run.power)","  heroPose('cheer',900);heroHop();SND('reward');\n  if(run.power)"),
 ("  if(x.k==='it')levelUp(x.id);\n  if(x.k==='evo'){","  SND(x.k==='evo'?'evolve':'level');\n  if(x.k==='it')levelUp(x.id);\n  if(x.k==='evo'){"),
 # reroll
 ("function reroll(){\n  if(busy||!run||run.phase!=='build'||run.rolls<=0)return;","function reroll(){\n  if(busy||!run||run.phase!=='build'||run.rolls<=0)return;SND('dice');"),
 # beating his own record
 ("note('じぶんの記録をこえた！','good');","note('じぶんの記録をこえた！','good');SND('record');"),
 # the result paper: a short tune
 ("  $('o-head').textContent=head[why]||head.quit;","  if(AUD)AUD.over(best?'win':home?'quit':'lose');\n  $('o-head').textContent=head[why]||head.quit;"),
 # bubbles
 ("  run.bub--;bubbleFx(false);","  run.bub--;SND('pop');bubbleFx(false);"),
 # the shop
 ("meta.bank-=c;meta.up[sel]++;","SND('buy');meta.bank-=c;meta.up[sel]++;"),
 ("cost)return;meta.bank-=k.cost;","cost)return;SND('buy');meta.bank-=k.cost;"),
 # the paper planes and the boomerang
 ("if(i>=0){shoot(run.at,i,SPR.i_plane,240);","if(i>=0){SND('plane');shoot(run.at,i,SPR.i_plane,240);"),
 ("const k=hs[rnd(hs.length)];toss(","const k=hs[rnd(hs.length)];SND('plane');toss("),
 ("    if(ks.length){run.bmc=0;\n","    if(ks.length){run.bmc=0;SND('boomer');\n"),
 # a toy pops up for the first time
 ("if(!e||SEEN.has(e))return g;SEEN.add(e);return REDUCED?g:","if(!e||SEEN.has(e))return g;SEEN.add(e);SND('pon');return REDUCED?g:"),
 # test hook
 ("heroPose,heroBase,toyAct,toysAct,fightRules,","heroPose,heroBase,toyAct,toysAct,fightRules,AUD,"),
]
for a,b in R:
  n=s.count(a)
  if n!=1: sys.exit(f'NG {n}: {a[:70]}')
  s=s.replace(a,b)
# bubble gained (several places): one sound inside bubbleFx when on
a="function bubbleFx(on){\n"
if s.count(a)!=1: sys.exit('NG bubbleFx')
s=s.replace(a,a+"  if(on)SND('bubble');\n")
css='''
/* the sound button on the home screen (11/5) */
#t-snd{position:absolute;z-index:3;top:max(14px,env(safe-area-inset-top,0px));right:max(14px,env(safe-area-inset-right,0px));color:var(--ink)}
#t-snd svg{inset:6px;width:32px;height:32px}
#t-snd.off{color:rgba(74,53,65,.55)}
'''
a='@keyframes ovThud{35%{transform:translateY(5px)}}'
if s.count(a)!=1: sys.exit('NG css anchor')
s=s.replace(a,a+css)
open(P,'w',encoding='utf-8').write(s)
print('ok')
