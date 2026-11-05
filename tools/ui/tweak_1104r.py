# 11/4 地面に立っている敵（弓兵・魔法使い・ピエロ・かべ職人・ふつうの兵隊）と戦えるように（tweak_1104q.py のあとに1回だけ）
#  これまで：立っている敵は かべと同じで、道の先にいると「行き止まり」でゲームオーバー（魔法か大砲でしかどかせない）
#  これから：立っている敵のマスも「道の先」。そこに積み木を置くと、騎士がその場から戦い、たおすと金貨が出て その積み木へ進む
#   - 置ける所の光（点線のわく）が敵のマスにも出る。持っている積み木の敵と同じく、HP の減りの見こみ（ハートのゲージ）にも入る
#   - 敵の紙：「戦うと♥-N」「たおすと金貨+N」を出す（矢・魔法などの とくちょうは そのまま）
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)

# the way on: a standing toy's cell is a cell a block can go on
rep("      if(c.rock||c.foe||c.tile||c.start||map.has(j))continue;", "      if(c.rock||c.tile||c.start||map.has(j))continue; // a standing toy: put a block there and fight it")
rep("    if(c.rock||c.foe||c.tile||c.start)continue;\n    map.set(j,OPP[b]);", "    if(c.rock||c.tile||c.start)continue; // a standing toy: put a block there and fight it\n    map.set(j,OPP[b]);")
rep("    for(const b of BITS){const j=nbr(i,b);if(j<0||seen.has(j))continue;const x=cellAt(j);if(!x||x.rock||x.foe||x.start||(x.tile&&!x.tile.gate))continue;seen.add(j);q.push(j)}",
    "    for(const b of BITS){const j=nbr(i,b);if(j<0||seen.has(j))continue;const x=cellAt(j);if(!x||x.rock||x.start||(x.tile&&!x.tile.gate))continue;seen.add(j);q.push(j)}")
# the toy's cell lights up like any cell on the way (the toy still shows until the fight)
rep("""inner=svg(HAS_ART?toyStand(i,c.foe.t):`<g class="toy">${SPR[c.foe.t]||SPR.soldier}</g>`);tab=` style="--d:-${(i*7%23)/5}s"`}""",
    """inner=svg(HAS_ART?toyStand(i,c.foe.t):`<g class="toy">${SPR[c.foe.t]||SPR.soldier}</g>`);tab=` style="--d:-${(i*7%23)/5}s"`;
    if(F&&F.has(i)&&!c.tile){const ok=sel>=0&&fits(run.hand[sel],i,F);cls+=' front'+(ok?' fit':'');if(ok)inner+=`<div class="gh">${svg(tileArt(run.hand[sel],false))}</div>`;tab+=' tabindex="0" role="button" aria-label="道の先（敵）"'}}""")
# the walk: the knight fights the standing toy from where he stands, then goes onto the block
rep("""  if(foe){ // fight from the cell in front of the toy
    hero.classList.remove('walk');""",
"""  if(c.foe&&c.tile){ // a block put on a standing toy: fight it from here, then walk on (11/4)
    const e=c.foe;hero.classList.remove('walk');
    if(!await battle(e,run.at,i)){await knockOut();busy=false;gameOver('hp');return false}
    c.foe=null;updateCell(i);await sleep(STEP);
  }
  if(foe){ // fight from the cell in front of the toy
    hero.classList.remove('walk');""")
# the heart gauge shows what the fight would cost
rep("  if(j>=0&&fits(t,j,frontier())){const g=gateFrom(j,t.m),",
    "  if(j>=0&&fits(t,j,frontier())){const sc=cellAt(j);if(sc&&sc.foe)d+=dmgFor(sc.foe);const g=gateFrom(j,t.m),")
# its paper: what it does (archers, mages...), what a fight costs, what it leaves
rep("""  if(c.foe){const s=SHOOTERS[e.t];what=s&&FOE_DO[e.t]?FOE_DO[e.t](s.rng):'道をふさいでいる'}
  else{const d=dmgFor(e);what=""", """  {const s=c.foe&&SHOOTERS[e.t],d=dmgFor(e);what=(s&&FOE_DO[e.t]?`<span class="fd-do">${FOE_DO[e.t](s.rng)}</span>`:'')+""")
rep("function standFoe(f,r){ // a toy standing on the ground: in the way until magic or the cannon breaks it",
    "function standFoe(f,r){ // a toy standing on the ground: put a block on it to fight it (magic and the cannon break it too)")
open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
