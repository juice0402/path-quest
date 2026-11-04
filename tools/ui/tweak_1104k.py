# 11/4 バランス：数字を1か所（BAL）にまとめる。#fxtest のときは localStorage の pq.bal で上書きして試せる（slim_1104.py のあとに1回だけ）
#  あわせて：大将の四角の下の2マスをあける（行き止まりで大将にたどりつけない、をなくす）
#            敵をたおすと メッセージ窓に「金貨+N」、敵の紙にも「たおすと 金貨+N」
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()

def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)

rep("const DIM_X=2;", """/* the balance numbers in one place (11/4). [a,b] means a + b × level. a test page (#fxtest) can try others from localStorage 'pq.bal' */
const BAL={
  knight:{hp:10,atk:2,rolls:3,hand:4},
  ob:[.13,.002,.3],gem:.035,gemV:[5,2],stand:[.03,.025,.0002,.12], // obstacles: base, per step, most; gems; standing toys: base, per dimension, per step, most
  ev:{foe:[.16,.012,.3],coin:.13,potion:.07,wpn:.04,shd:.04,chm:.03},coinV:[2,.5],potV:[3,.34], // what rides on a block
  foe:{hp:[2,1],atk:[1,.5],gold:[3,.8]},boss:{hp:[4,1.2],atk:[1,.5],gold:[10,2]},king:{hp:[8,1.6],atk:[1,.5],gold:[30,4]},
  cost:1 // all upgrade prices are multiplied by this
};
if(/fxtest/.test(location.hash))try{const o=JSON.parse(localStorage.getItem('pq.bal')||'{}');for(const k in o)BAL[k]=typeof o[k]==='object'&&!Array.isArray(o[k])?{...BAL[k],...o[k]}:o[k]}catch(e){}
const DIM_X=2;""")
# toys, captains, kings
rep("  return {k:'foe',t:t.t,name:t.name,hp:Math.round(Math.max(2,2+L+t.hp)*x),atk:Math.round(Math.max(1,1+Math.floor((L-1)/2)+t.atk)*x),gold:3+Math.floor(f*.8)};",
    "  const B=BAL.foe;return {k:'foe',t:t.t,name:t.name,hp:Math.round(Math.max(2,B.hp[0]+B.hp[1]*L+t.hp)*x),atk:Math.round(Math.max(1,B.atk[0]+Math.floor((L-1)*B.atk[1])+t.atk)*x),gold:Math.round(B.gold[0]+B.gold[1]*f)};")
rep("function makeKing(f,r){const L=foeLv(r),x=dimX(dimOf(r));return {k:'foe',t:'king',name:'おもちゃの王さま',hp:Math.round((8+L*1.6)*x),atk:(1+Math.floor(L/2))*x,gold:30+4*f,boss:true,king:true}}",
    "function makeKing(f,r){const L=foeLv(r),x=dimX(dimOf(r)),B=BAL.king;return {k:'foe',t:'king',name:'おもちゃの王さま',hp:Math.round((B.hp[0]+L*B.hp[1])*x),atk:Math.round((B.atk[0]+Math.floor(L*B.atk[1]))*x),gold:Math.round(B.gold[0]+B.gold[1]*f),boss:true,king:true}}")
rep("    Object.assign(e,{t:k,name:s.name,hp:Math.round(Math.max(2,2+L+s.hp)*x),atk:Math.round(Math.max(1,1+Math.floor((L-1)/2)+s.atk)*x)});",
    "    const B=BAL.foe;Object.assign(e,{t:k,name:s.name,hp:Math.round(Math.max(2,B.hp[0]+B.hp[1]*L+s.hp)*x),atk:Math.round(Math.max(1,B.atk[0]+Math.floor((L-1)*B.atk[1])+s.atk)*x)});")
rep("function makeBoss(f,r){const L=foeLv(r),x=dimX(dimOf(r));return {k:'foe',t:'boss',name:'兵隊長',hp:Math.round((4+L*1.2)*x),atk:(1+Math.floor(L/2))*x,gold:10+2*f,boss:true}}",
    "function makeBoss(f,r){const L=foeLv(r),x=dimX(dimOf(r)),B=BAL.boss;return {k:'foe',t:'boss',name:'兵隊長',hp:Math.round((B.hp[0]+L*B.hp[1])*x),atk:Math.round((B.atk[0]+Math.floor(L*B.atk[1]))*x),gold:Math.round(B.gold[0]+B.gold[1]*f),boss:true}}")
# what rides on a block
rep("  const a=[['foe',Math.min(.3,.16+.012*f)],['coin',.13*g],['potion',.07*p],['wpn',.04*g],['shd',.04*g],['chm',.03*g]];",
    "  const E=BAL.ev,a=[['foe',Math.min(E.foe[2],E.foe[0]+E.foe[1]*f)],['coin',E.coin*g],['potion',E.potion*p],['wpn',E.wpn*g],['shd',E.shd*g],['chm',E.chm*g]];")
rep("    if(k==='coin')return {k:'coin',v:2+Math.floor(f/2)};", "    if(k==='coin')return {k:'coin',v:BAL.coinV[0]+Math.floor(f*BAL.coinV[1])};")
rep("    if(k==='potion')return {k:'potion',v:(3+Math.floor(f/3))*PM()};", "    if(k==='potion')return {k:'potion',v:(BAL.potV[0]+Math.floor(f*BAL.potV[1]))*PM()};")
# the field
rep("    const p=Math.min(.3,.13+s*.002);\n    row.forEach(c=>{if(Math.random()<p)c.rock=1;else if(Math.random()<.035)c.gem=5+2*lvOf(r)});",
    "    const p=Math.min(BAL.ob[2],BAL.ob[0]+s*BAL.ob[1]);\n    row.forEach(c=>{if(Math.random()<p)c.rock=1;else if(Math.random()<BAL.gem)c.gem=BAL.gemV[0]+BAL.gemV[1]*lvOf(r)});")
rep("    const fp=s>4?Math.min(.12,.03+.025*dimOf(r)+s*.0002):0;", "    const fp=s>4?Math.min(BAL.stand[3],BAL.stand[0]+BAL.stand[1]*dimOf(r)+s*BAL.stand[2]):0;")
# the knight at the start
rep("  run={maxHp:10+2*u.hp+q.hp,hp:10+2*u.hp+q.hp,atk:2+u.atk+q.atk,def:u.def+q.def,gold:0,handSize:4+u.hand,rolls:3+u.roll+q.roll,",
    "  const K=BAL.knight;run={maxHp:K.hp+2*u.hp+q.hp,hp:K.hp+2*u.hp+q.hp,atk:K.atk+u.atk+q.atk,def:u.def+q.def,gold:0,handSize:K.hand+u.hand,rolls:K.rolls+u.roll+q.roll,")
rep("    run.rolls=3+meta.up.roll+Q().roll;run.chest=true;", "    run.rolls=BAL.knight.rolls+meta.up.roll+Q().roll;run.chest=true;")
# upgrade prices
rep("let meta=store.get(META)||{};", "if(BAL.cost!==1)UPS.forEach(u=>{const c=u.cost;u.cost=l=>Math.round(c(l)*BAL.cost)});\nlet meta=store.get(META)||{};")
# the two cells under the captain's square are always open
rep("  if(prev[b].rock===1)prev[b].rock=0;\n  prev[b].foe=null;",
    "  if(prev[b].rock===1)prev[b].rock=0;\n  prev[b].foe=null;\n  {const g=row.findIndex(c=>c.tile&&c.tile.anc);if(g>=0){const n2=g<=2?g+1:g-1;for(const k of [g,n2]){if(prev[k].rock===1||prev[k].rock===3)prev[k].rock=0;prev[k].foe=null}}} // the way into the captain's square")
# gold from a beaten toy shows in the message window too
rep("  pop(i,`+${addGold(e.gold)}`,'p-gold');fly(i,SPR.coin,$('i-gold'),120);renderStats();",
    "  {const g=addGold(e.gold);pop(i,`+${g}`,'p-gold');fly(i,SPR.coin,$('i-gold'),120);note(`${e.name}をたおした！ 金貨+${nf(g)}`,'good')}renderStats();")
# the toy's paper: what it leaves
rep("  else{const d=dmgFor(e);what=d?`<span class=\"fd-c\">戦うと${hp('-'+nf(d))}</span>`:'戦ってもダメージなし'}",
    "  else{const d=dmgFor(e);what=(d?`<span class=\"fd-c\">戦うと${hp('-'+nf(d))}</span>`:'戦ってもダメージなし')+`<span class=\"fd-g\">たおすと${ico(SPR.coin)}+${nf(gainOf(e.gold))}</span>`}")
rep("/* ===== end of 11/4 ===== */", ".skn .sb-t .fd-g{display:inline-flex;align-items:center;gap:3px;margin:0 0 0 10px;font:800 13px/1.3 var(--round);color:#b07a10}\n.skn .fd-g svg{width:16px;height:16px;display:block}\n/* ===== end of 11/4 ===== */")
open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
