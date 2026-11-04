# 11/4 夕方 敵を大ボリュームに：黒っぽい衣装のいたずら顔のおもちゃ20体（絵は tools/art/build_foes_1104.py）
#  - 積み木の敵のくせ（ラッパ兵・大砲・ロボ）、景色ごとの敵2体ずつ（草原・森・湖・雪原・城）、立つ敵は景色ごとに早く出る
#  - 兵隊長・王さまの技、★2の装備は30段ごろから少しだけ
#  - 敵の動き（待ち・出てくる・攻撃・よける・起き上がる・にげる・たおれる）
#  - 騎士くんの12ポーズ（後ろ姿・横向き・剣・盾・ジャンプ・いたい・ばんざい・のびる・キャンディ・宝物・剣をかかげる）と、待っているときのしぐさ
# 1回だけ当てる（文字列の置きかえ。数が合わないと止まる）
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, old[:90])
    s = s.replace(old, new)

# ---------- the look: a soft dark-purple stand instead of the red glow ----------
rep('''const EVIL=rx=>`<ellipse cx="50" cy="86" rx="${rx+6}" ry="7" fill="rgba(214,51,79,.28)"/><ellipse cx="50" cy="86" rx="${rx}" ry="4.5" fill="rgba(90,20,40,.4)"/>`; // the toys that fight stand on a red glow''',
    '''const EVIL=rx=>`<ellipse cx="50" cy="86" rx="${rx+6}" ry="7" fill="rgba(122,79,176,.24)"/><ellipse cx="50" cy="86" rx="${rx}" ry="4.5" fill="rgba(40,22,52,.38)"/>`; // the toys that fight stand on a dark purple stand (11/4: no red glow)''')
rep('''fill="rgba(214,51,79,.28)"/><ellipse cx="${cx}" cy="171" rx="${en.king?50:44}" ry="8.5" fill="rgba(90,20,40,.4)"/>''',
    '''fill="rgba(122,79,176,.24)"/><ellipse cx="${cx}" cy="171" rx="${en.king?50:44}" ry="8.5" fill="rgba(40,22,52,.38)"/>''')

# the pictures: each toy its own height, its body on the middle of the block, feet at 88 (the captain 90, the king 94)
rep('''    // the toys stand a little taller than their block, like figures on a board
    soldier:EVIL(16)+U('soldier',18,-6,64,94),
    bugle:EVIL(16)+U('bugle',18,-6,64,94),
    cannon:EVIL(26)+U('cannon',10,12,80,76),
    robot:EVIL(18)+U('robot',16,-2,68,90),
    boss:EVIL(26)+U('boss',4,-20,92,110),
    archer:EVIL(16)+U('archer',18,-6,64,94),
    mage:EVIL(16)+U('mage',16,-8,68,96),
    clown:EVIL(16)+U('clown',16,-6,68,94),
    mason:EVIL(18)+U('mason',12,2,76,86),
''', '''    // the toys stand a little taller than their block, like figures on a board
    ...Object.fromEntries(Object.entries(FOE_H).map(([t,[h,rx,mw,f]])=>[t,EVIL(rx)+FA(t,h,mw,f)])),
''')
rep('''    king:document.getElementById('a-king')?EVIL(30)+U('king',-2,-30,104,124):SPR.boss,
''', '')
rep('''if(HAS_ART){
  Object.assign(SPR,{''', '''const FA=(n,h,mw,f)=>{ // a toy's picture by its own shape: h tall, its body (data-ax) on x=50, feet at f
  const s=document.getElementById('a-'+n);if(!s)return '';const v=s.viewBox.baseVal,ax=+(s.getAttribute('data-ax')||.5),m=mw||100;
  let w=h*v.width/v.height;if(w>m){h*=m/w;w=m}f=f||88;return U(n,+(50-w*ax).toFixed(1),+(f-h).toFixed(1),+w.toFixed(1),+h.toFixed(1));
};
const FOE_H={ // height, stand size, widest, feet
  soldier:[92,16],bugle:[92,16],cannon:[74,26],robot:[90,18],archer:[90,16],mage:[94,16],clown:[90,18],mason:[84,20],
  imp:[84,16],mouse:[60,20],bear:[78,20],shroom:[86,16],duck:[68,22],frog:[62,22],peng:[78,18],hedge:[70,22],skel:[90,16],ghost:[84,20,110],
  boss:[110,26,100,90],king:[124,30,110,94]
};
if(HAS_ART){
  Object.assign(SPR,{''')

# ---------- the toys: who they are and their habits ----------
rep('''function makeFoe(f,r){ // f: how far the climb is (gold, which toys turn up); r: the row, which sets how strong it is
  if(r==null)r=run?rowOf(run.at):1;
  const pool=FOES.filter(x=>x.from<=f);
  const t=pool.length>1&&Math.random()<.55?pool[pool.length-1]:pool[rnd(pool.length)];
  const L=foeLv(r),x=dimX(dimOf(r));
  const B=BAL.foe;return {k:'foe',t:t.t,name:t.name,hp:Math.round(Math.max(2,B.hp[0]+B.hp[1]*L+t.hp)*x),atk:Math.round(Math.max(1,B.atk[0]+Math.floor((L-1)*B.atk[1])+t.atk)*x),gold:Math.round(B.gold[0]+B.gold[1]*f)};
}''', '''/* each land has two toys of its own (11/4), mixed in with the soldiers above */
const LAND_FOES={
  grass:[{t:'imp',name:'いたずら小僧',hp:0,atk:0},{t:'mouse',name:'ゼンマイねずみ',hp:0,atk:0}],
  forest:[{t:'bear',name:'くまのぬいぐるみ',hp:1,atk:0},{t:'shroom',name:'きのこのこびと',hp:0,atk:0}],
  lake:[{t:'duck',name:'ゴムのアヒル',hp:1,atk:0},{t:'frog',name:'ブリキのカエル',hp:0,atk:0}],
  snow:[{t:'peng',name:'ゼンマイペンギン',hp:0,atk:0},{t:'hedge',name:'とげとげハリネズミ',hp:1,atk:0}],
  castle:[{t:'skel',name:'カタカタがいこつ',hp:0,atk:0},{t:'ghost',name:'鉄球おばけ',hp:0,atk:0}]
};
/* how each kind fights (11/4). the fight (battle), its forecast (dmgFor) and the toy's paper all read this.
   grow: each hit harder by this share of its attack · first2: the first hit doubled · armor: the knight's first hit does nothing
   flee: runs at this share of its hp (half the gold) · dodge: every 2nd hit of the knight misses · spore: poison after it breaks
   nomag: magic and poison do nothing · double: hits twice in the first round · pierce: the knight's guard does nothing
   thorn: the knight takes this share of each hit he lands · revive: gets up once with this share of its hp
   rage: at half hp its attack times this · wind: once, at 30% hp, winds itself back by this share */
const QK={
  bugle:{d:'ぷっぷー：戦うほど攻撃が上がる',grow:.25},
  cannon:{d:'ドーン：最初の一発は攻撃2倍',first2:1},
  robot:{d:'カチカチ：最初の1回は攻撃が効かない',armor:1},
  imp:{d:'にげ足：HPが半分になると にげる（金貨は半分）',flee:.5},
  mouse:{d:'ちょこまか：攻撃が2回に1回よけられる',dodge:2},
  bear:{d:'ふかふか：HPは多いけど攻撃は弱い'},
  shroom:{d:'ぽふっ：たおすと胞子で3マス毒になる',spore:3},
  duck:{d:'ぷかぷか：魔法と毒が効かない',nomag:1},
  frog:{d:'ぴょん：最初に2回つづけて攻撃',double:1},
  peng:{d:'すべりこみ：守りが効かない',pierce:1},
  hedge:{d:'とげとげ：たたくと少しダメージを受ける',thorn:.2},
  skel:{d:'カタカタ：1回だけ起き上がる',revive:.5},
  ghost:{d:'鉄球どすん：攻撃は強いけどHPは少ない'},
  boss:{d:'はりきり：HPが半分になると攻撃1.5倍',rage:1.5},
  king:{d:'ぜんまい巻き直し：HPが3割になると1回だけ回復',wind:.4}
};
const QM={bear:[2,.5],ghost:[.55,1.8],mouse:[.7,1],skel:[.8,1],imp:[1.1,1]}; // [hp, attack] for the kinds built that way
const tuneFoe=o=>{const m=QM[o.t];if(m){o.hp=Math.max(2,Math.round(o.hp*m[0]));o.atk=Math.max(1,Math.round(o.atk*m[1]))}return o};
function makeFoe(f,r){ // f: how far the climb is (gold, which toys turn up); r: the row, which sets how strong it is
  if(r==null)r=run?rowOf(run.at):1;
  const pool=FOES.filter(x=>x.from<=f),land=LAND_FOES[areaOf(r).k]||[];
  const t=land.length&&Math.random()<.45?land[rnd(land.length)]:pool.length>1&&Math.random()<.55?pool[pool.length-1]:pool[rnd(pool.length)];
  const L=foeLv(r),x=dimX(dimOf(r));
  const B=BAL.foe;return tuneFoe({k:'foe',t:t.t,name:t.name,hp:Math.round(Math.max(2,B.hp[0]+B.hp[1]*L+t.hp)*x),atk:Math.round(Math.max(1,B.atk[0]+Math.floor((L-1)*B.atk[1])+t.atk)*x),gold:Math.round(B.gold[0]+B.gold[1]*f)});
}''')
rep('''/* toys that act from where they stand, one more kind each dimension. they only stand on the field.''',
    '''/* toys that act from where they stand, one more kind with each land (11/4: from: the step they first turn up). they only stand on the field.''')
rep('''  archer:{name:'弓兵',dim:1,rng:2,hp:0,atk:0},
  mage:{name:'魔法使い',dim:2,rng:3,hp:-1,atk:0},
  clown:{name:'毒まきピエロ',dim:3,rng:3,hp:0,atk:-1},
  mason:{name:'かべ職人',dim:4,rng:3,hp:2,atk:-1}''', '''  archer:{name:'弓兵',from:5,rng:2,hp:0,atk:-1},
  mage:{name:'魔法使い',from:21,rng:3,hp:-1,atk:0},
  clown:{name:'びっくり箱ピエロ',from:41,rng:3,hp:0,atk:-1},
  mason:{name:'かべ職人',from:61,rng:3,hp:2,atk:-1}''')
rep('''  const e=Object.assign(makeFoe(f,r),{stand:1}),d=dimOf(r),ks=Object.keys(SHOOTERS).filter(k=>SHOOTERS[k].dim<=d);
  if(ks.length&&Math.random()<.6){''', '''  const e=Object.assign(makeFoe(f,r),{stand:1}),d=dimOf(r),st=stepOf(r),ks=Object.keys(SHOOTERS).filter(k=>SHOOTERS[k].from<=st);
  if(ks.length&&Math.random()<(d?.6:.4)){''')

# ---------- one set of fight rules for the fight and its forecast ----------
rep('''function dmgFor(e){ // the hp a fight costs, crits not counted: the toy hits, then the knight, until the toy falls
  const A=atkNow(),back=FX().guard&&!e.boss?0:Math.ceil(Math.max(0,e.atk-run.def)/((FX().half?2:1)*(FX().guard?2:1))),ref=qv('ref'),first=qv('first');
  const tl=itLv('top'),T2=tl?toyDmg(isEvo('top')?100:L5(TOY.top.p,tl)):0;
  let hp=e.hp,block=qv('block')+(isEvo('top')?1:0)+(run.bub|0),taken=0;
  for(let n=0;n<300&&hp>0;n++){
    if(first){hp-=A+T2;if(hp<=0)break}
    let b=back;if(b&&block>0){b=0;block--}
    taken+=b;if(b&&ref)hp-=Math.ceil(b*ref);if(hp<=0)break;
    if(!first)hp-=A+T2;
  }
  return taken;
}''', '''function fightRules(e){ // one fight with toy e: its hp as the fight goes, and what its habit does (QK)
  const q=QK[e.t]||{},guard=!!FX().guard&&!e.boss,div=(FX().half?2:1)*(FX().guard?2:1);
  return {q,hp:e.hp,max:e.hp,n:0,kn:0,mul:1,up:0,wound:0,
    back(){ // the toy's hit in this round, before the knight's blocks
      if(guard)return 0;
      let a=e.atk*this.mul+(q.grow?Math.ceil(e.atk*q.grow)*this.n:0);if(q.first2&&this.n===0)a*=2;
      return Math.ceil(Math.max(0,Math.round(a)-(q.pierce?0:run.def))/div);
    },
    hits(){return q.double&&this.n===0?2:1},
    hit(d){ // the knight's hit lands, or not
      this.kn++;
      if(q.armor&&this.kn===1)return {d:0,why:'armor'};
      if(q.dodge&&this.kn%q.dodge===0)return {d:0,why:'dodge'};
      this.hp-=d;return {d,thorn:q.thorn?Math.max(1,Math.ceil(d*q.thorn)):0};
    },
    after(){ // after its hp changed: it may get up, wind itself, get angry or run
      if(this.hp<=0){if(q.revive&&!this.up){this.up=1;this.hp=Math.ceil(this.max*q.revive);return 'revive'}return ''}
      if(q.wind&&!this.wound&&this.hp<=this.max*.3){this.wound=1;const h=Math.ceil(this.max*q.wind);this.hp+=h;return 'wind'}
      if(q.rage&&this.mul===1&&this.hp<=this.max*.5){this.mul=q.rage;return 'rage'}
      if(q.flee&&this.hp<=this.max*q.flee)return 'flee';
      return '';
    }};
}
function dmgFor(e){ // the hp a fight costs, crits not counted: the toy hits, then the knight, until the toy falls (or runs)
  const R=fightRules(e),A=atkNow(),ref=qv('ref'),first=qv('first');
  const tl=itLv('top'),T2=tl?toyDmg(isEvo('top')?100:L5(TOY.top.p,tl)):0;
  let block=qv('block')+(isEvo('top')?1:0)+(run.bub|0),taken=0,gone=false;
  const strike=()=>{const h=R.hit(A);if(!h.why&&T2&&R.hp>0)R.hp-=T2;taken+=h.thorn||0;if(R.after()==='flee')gone=true};
  for(let n=0;n<300&&R.hp>0&&!gone;n++){
    if(first){strike();if(R.hp<=0||gone)break}
    for(let k=R.hits();k>0;k--){let b=R.back();if(b&&block>0){b=0;block--}taken+=b;if(b&&ref){R.hp-=Math.ceil(b*ref);if(R.after()==='flee')gone=true}}
    R.n++;
    if(R.hp<=0||gone)break;
    if(!first)strike();
  }
  return taken;
}''')

rep('''async function battle(e,at,i){
  const hEl=elOf(at),eEl=elOf(i);
  const back=FX().guard&&!e.boss?0:Math.ceil(Math.max(0,e.atk-run.def)/((FX().half?2:1)*(FX().guard?2:1))),A=atkNow(),ref=qv('ref'),first=qv('first'),est=Math.ceil(e.hp/A);
  const gap=REDUCED?80:est<=4?340:Math.max(170,1400/est);
  let hp=e.hp,block=qv('block')+(isEvo('top')?1:0); // the tornado top takes the first hit
  const tl=itLv('top'),tp=tl?(isEvo('top')?100:L5(TOY.top.p,tl)):0;
  const dx=(eEl.offsetLeft-hEl.offsetLeft)*.3,dy=(eEl.offsetTop-hEl.offsetTop)*.3;
  await sleep(REDUCED?0:140);
  const strike=async()=>{ // the knight hits; now and then a crit
    let d=A;const cr=Math.random()<qv('crit');if(cr)d*=2+qv('critx');hp-=d;
    lunge(dx,dy);setTimeout(()=>{struck(eEl);spark(i)},80);pop(i,cr?`-${d}!`:`-${d}`,cr?'p-crit':'p-deal');if(cr)shake(5);
    FXH.emit('strike',{i,at,d,crit:cr,atk:A,hpBefore:hp+d,hpMax:e.hp,boss:!!e.boss,king:!!e.king});
    if(tp&&hp>0){const t=toyDmg(tp);hp-=t;setTimeout(()=>pop(i,`-${t}`,'p-top'),170)} // the spinning top follows up
    await sleep(gap/2+(REDUCED?0:60));
  };
  for(let n=0;n<300&&hp>0;n++){
    if(first){await strike();if(hp<=0)break}
    let b=back;if(b&&block>0){b=0;block--}else if(b&&bubbleBlock(at))b=0;
    run.hp-=b; // the toy hits
    pop(at,b?`-${b}`:'0',b?'p-hurt':'p-guard');if(b){hurt();shake(e.boss?7:4);FXH.emit('hurt',{at,b,boss:!!e.boss,i,src:'fight',max:run.maxHp})}
    renderStats();
    if(run.hp<=0)return false;
    if(b&&ref){const r=Math.ceil(b*ref);hp-=r;setTimeout(()=>{pop(i,`-${r}`,'p-ref');struck(eEl)},120)} // the mirror throws it back
    await sleep(gap/2);
    if(hp<=0)break;
    if(!first)await strike();
  }''', '''async function battle(e,at,i){
  const hEl=elOf(at),eEl=elOf(i),R=fightRules(e);
  const A=atkNow(),ref=qv('ref'),first=qv('first'),est=Math.ceil(e.hp/A);
  const gap=REDUCED?80:est<=4?340:Math.max(170,1400/est);
  let block=qv('block')+(isEvo('top')?1:0),gone=false; // the tornado top takes the first hit
  const tl=itLv('top'),tp=tl?(isEvo('top')?100:L5(TOY.top.p,tl)):0;
  const dx=(eEl.offsetLeft-hEl.offsetLeft)*.3,dy=(eEl.offsetTop-hEl.offsetTop)*.3,fl=eEl.offsetLeft>hEl.offsetLeft+4; // fl: the toy is to his right
  const tw=[Math.sign(hEl.offsetLeft-eEl.offsetLeft)*14,Math.sign(hEl.offsetTop-eEl.offsetTop)*10]; // the toy leans this way to hit
  hero.classList.remove('idle');
  await sleep(REDUCED?0:140);
  const habit=async()=>{ // after its hp changed: what its habit does now
    const w=R.after();if(!w)return;
    if(w==='flee'){gone=true;return}
    if(w==='revive'){toyAct(i,'revive',e);pop(i,'カタカタ！','p-q');note(`${e.name}が起き上がった`,'bad')}
    if(w==='wind'){toyAct(i,'wind',e);pop(i,'ぜんまい！','p-q');note(`${e.name}がぜんまいを巻き直した`,'bad')}
    if(w==='rage'){toyAct(i,'rage',e);pop(i,'はりきり！','p-q');note(`${e.name}がはりきった！`,'bad');shake(5)}
    await sleep(REDUCED?0:360);
  };
  const strike=async()=>{ // the knight hits; now and then a crit. false: the thorns took his last hp
    let d=A;const cr=Math.random()<qv('crit');if(cr)d*=2+qv('critx');
    const was=R.hp,h=R.hit(d);heroPose('swing',260,fl);lunge(dx,dy);
    if(h.why==='armor'){setTimeout(()=>toyAct(i,'armor',e),80);pop(i,'カチン','p-guard')}
    else if(h.why==='dodge'){toyAct(i,'dodge',e);pop(i,'ひょい','p-guard')}
    else{
      setTimeout(()=>{struck(eEl);spark(i)},80);pop(i,cr?`-${d}!`:`-${d}`,cr?'p-crit':'p-deal');if(cr)shake(5);
      FXH.emit('strike',{i,at,d,crit:cr,atk:A,hpBefore:was,hpMax:e.hp,boss:!!e.boss,king:!!e.king});
      if(tp&&R.hp>0){const t=toyDmg(tp);R.hp-=t;setTimeout(()=>pop(i,`-${t}`,'p-top'),170)} // the spinning top follows up
      if(h.thorn){run.hp-=h.thorn;setTimeout(()=>{pop(at,`-${h.thorn}`,'p-hurt');hurt()},160);renderStats();if(run.hp<=0)return false}
    }
    await sleep(gap/2+(REDUCED?0:60));
    await habit();
    return true;
  };
  for(let n=0;n<300&&R.hp>0&&!gone;n++){
    if(first){if(!await strike())return false;if(R.hp<=0||gone)break}
    for(let k=R.hits();k>0;k--){
      let b=R.back();if(b&&block>0){b=0;block--}else if(b&&bubbleBlock(at))b=0;
      run.hp-=b; // the toy hits
      if(e.boss)bossAct(i);else toyAct(i,e.t==='cannon'?'recoil':'atk',e,tw);
      heroPose(b?'hurt':'block',300,b?false:fl);
      pop(at,b?`-${b}`:'0',b?'p-hurt':'p-guard');if(b){hurt();shake(e.boss?7:4);FXH.emit('hurt',{at,b,boss:!!e.boss,i,src:'fight',max:run.maxHp})}
      renderStats();
      if(run.hp<=0)return false;
      if(b&&ref){const r=Math.ceil(b*ref);R.hp-=r;setTimeout(()=>{pop(i,`-${r}`,'p-ref');struck(eEl)},120);await habit()} // the mirror throws it back
      if(k>1)await sleep(gap/3);
    }
    R.n++;
    await sleep(gap/2);
    if(R.hp<=0||gone)break;
    if(!first&&!await strike())return false;
  }''')
rep('''  breakToy(i,e);if(e.boss)shake(8);
  {const g=addGold(e.gold);pop(i,`+${g}`,'p-gold');fly(i,SPR.coin,$('i-gold'),120);note(`${e.name}をたおした！ 金貨+${nf(g)}`,'good')}renderStats();
  await sleep(REDUCED?0:320);
  return true;
}''', '''  if(gone){ // the imp runs off with half the gold
    toyAct(i,'flee',e);const g=addGold(Math.ceil(e.gold/2));pop(i,`+${g}`,'p-gold');fly(i,SPR.coin,$('i-gold'),120);note(`${e.name}がにげた！ 金貨+${nf(g)}`,'good');renderStats();
    heroPose('side',500,fl);await sleep(REDUCED?0:520);return true;
  }
  breakToy(i,e);if(e.boss)shake(8);
  {const g=addGold(e.gold);pop(i,`+${g}`,'p-gold');fly(i,SPR.coin,$('i-gold'),120);note(`${e.name}をたおした！ 金貨+${nf(g)}`,'good')}
  if(R.q.spore){run.pz={n:R.q.spore,d:Math.max(1,Math.ceil(e.atk/3))};hero.classList.add('psn');setTimeout(()=>puff(at),120);note('胞子をすって 毒状態になった','bad')}
  heroPose(e.boss?'cheer':'raise',e.boss?900:420);if(e.boss)heroHop();
  renderStats();
  await sleep(REDUCED?0:320);
  return true;
}''')

# the toy's paper says its habit
rep('''what=(s&&FOE_DO[e.t]?`<span class="fd-do">${FOE_DO[e.t](s.rng)}</span>`:'')+''',
    '''what=(s&&FOE_DO[e.t]?`<span class="fd-do">${FOE_DO[e.t](s.rng)}</span>`:'')+(QK[e.t]?`<span class="fd-do">${QK[e.t].d}</span>`:'')+''')

# the duck: magic and poison do nothing
rep('''  const t=run.hand[k],e=t&&t.e;if(!e||e.k!=='foe')return;
  e.hp-=dmg;const el=handEl.children[k],a=mid(el);''', '''  const t=run.hand[k],e=t&&t.e;if(!e||e.k!=='foe')return;
  const el=handEl.children[k],a=mid(el);
  if((QK[e.t]||{}).nomag&&(cls==='mag'||cls==='psn')){e.psn=0;bump(el);return} // the rubber duck shrugs it off
  e.hp-=dmg;''')
rep('''const c=run.hand.filter(t=>t&&t.e&&t.e.k==='foe'&&!t.e.psn);''', '''const c=run.hand.filter(t=>t&&t.e&&t.e.k==='foe'&&!t.e.psn&&!(QK[t.e.t]||{}).nomag);''')
rep('''      const e=x.foe||(x.tile&&x.tile.gate&&x.tile.e);if(!e||e.k!=='foe')continue; // not the piece the king left
      e.hp-=M;const d=n++*70;''', '''      const e=x.foe||(x.tile&&x.tile.gate&&x.tile.e);if(!e||e.k!=='foe')continue; // not the piece the king left
      if((QK[e.t]||{}).nomag){pop(i,'効かない','p-guard',n++*70);continue}
      e.hp-=M;const d=n++*70;''')

# bits that fly when a toy breaks, in the new colours
rep('''const TOYBITS={archer:['#8fd08a','#b08968','#f2c14e'],mage:['#9f8fd6','#f2c14e','#fff'],clown:['#b48be0','#8fd08a','#e8607e'],mason:['#f2a65e','#93c3e4','#e6b98e'],king:['#e8607e','#f2c14e','#fff','#3d4170'],soldier:['#f08a8a','#3d4170','#f2c14e'],bugle:['#8fcdb6','#f2c14e','#3d4170'],cannon:['#9f8fd6','#e6b98e','#b4a3e8'],robot:['#cfd8e8','#8e9cc0','#e8607e','#ffd36e'],boss:['#e8607e','#f2c14e','#3d4170','#ee88ac']};''',
    '''const TOYBITS={soldier:['#2e2a36','#7a4fb0','#f2c14e'],bugle:['#2e2a36','#d9a63a','#7a4fb0'],cannon:['#2a2730','#6b4a9e','#8a8494'],robot:['#2e2a36','#8a8494','#e8607e','#d9a63a'],
  archer:['#2e2a36','#8b6a4f','#e8504a'],mage:['#3a2d52','#7a4fb0','#f2c14e'],clown:['#2e2a36','#7a4fb0','#fff','#c4364a'],mason:['#2e2a36','#6b4a9e','#8b6a4f'],
  boss:['#2e2a36','#7a4fb0','#f2c14e','#fff'],king:['#2e2a36','#7a4fb0','#d9a63a','#fff'],imp:['#2e2a36','#7a4fb0','#f2d0b0'],mouse:['#3a3640','#7a4fb0','#d9a63a'],
  bear:['#2e2a36','#7a4fb0','#e9dcc8'],shroom:['#2e2a36','#7a4fb0','#f2d0b0'],duck:['#24222a','#7a4fb0'],frog:['#24222a','#6b4a9e','#d9a63a'],
  peng:['#24222a','#e9dcc8','#7a4fb0','#d9a63a'],hedge:['#2e2a36','#7a4fb0','#e9dcc8'],skel:['#efe6d6','#2e2a36','#b35fd0'],ghost:['#f5f2ec','#7a4fb0','#24222a']};''')
# the beaten toy spins once as it pops
rep('''if(t&&!REDUCED)t.animate([{transform:'none',opacity:1},{transform:'scale(1.25)',opacity:1,offset:.4},{transform:'scale(.2) translateY(-20%)',opacity:0}],{duration:260,easing:'ease-in',fill:'forwards'});''',
    '''if(t&&!REDUCED)t.animate([{transform:'none',opacity:1},{transform:'translateY(-8%) rotate(-14deg) scale(1.25,1.15)',opacity:1,offset:.35},{transform:'translateY(-30%) rotate(200deg) scale(.2)',opacity:0}],{duration:340,easing:'ease-in',fill:'forwards'});''')

# ---------- ★2 gear from about the 30th step ----------
rep('''const RW=[0,6,3,1.6,.8]; // how often each rarity turns up once its dimension is reached: ★1 from the start, ★2 from the 2nd dimension…
const topR=()=>Math.min(4,(run?dimOf(rowOf(run.at)):0)+1);
function pickGear(s,top,exact){const pool=GEAR.filter(g=>g.s===s&&(exact?g.r===top:g.r<=top));return pickW(pool.map(g=>[g,RW[g.r]]))}
function makeGear(s){return {k:'gear',g:pickGear(s,topR()).id}}''', '''const RW=[0,6,3,1.6,.8]; // how often each rarity turns up once it is reached: ★1 from the start, ★2 from the 30th step (a little), ★3 from the 2nd dimension…
const R2_AT=30; // 11/4: a few ★2 pieces already in the first dimension
const topR=()=>{if(!run)return 1;const r=rowOf(run.at),d=dimOf(r);return Math.min(4,d===0?(stepOf(r)>=R2_AT?2:1):d+1)};
function pickGear(s,top,exact,soft){const pool=GEAR.filter(g=>g.s===s&&(exact?g.r===top:g.r<=top));return pickW(pool.map(g=>[g,RW[g.r]*(soft&&g.r===top?.5:1)]))}
function makeGear(s){const top=topR();return {k:'gear',g:pickGear(s,top,false,!!run&&dimOf(rowOf(run.at))===0&&top===2).id}}''')


# ---------- the shop says ★2 comes early now ----------
rep('''${g.r>1?`${g.r}つめの次元（${dimName(g.r-1)}）から見つかる`:'冒険のどこかで見つかる'}''',
    '''${g.r>2?`${g.r}つめの次元（${dimName(g.r-1)}）から見つかる`:g.r===2?`はじまりの次元の${R2_AT}段ごろから見つかる`:'冒険のどこかで見つかる'}''')

# ---------- toys on the field: their own kind of idle motion, and a pop when they first show ----------
rep('''const toyStand=(i,t)=>standArt(i,`<g class="toy">${SPR[t]||SPR.soldier}</g>`,FOE_F0(t),DEP.foe,DEP.foot,0);
const toyOnBlock=(i,t)=>standArt(i,`<g class="toy">${SPR[t]||SPR.soldier}</g>`,FOE_F0(t),.86,RC+14,0);''',
    '''const SEEN=new WeakSet(); // toys already drawn once: only a new one pops up
const TOYG=(t,e)=>{const g=`<g class="toy t-${t}">${SPR[t]||SPR.soldier}</g>`;if(!e||SEEN.has(e))return g;SEEN.add(e);return REDUCED?g:`<g class="spawn">${g}</g>`};
const toyStand=(i,t,e)=>standArt(i,TOYG(t,e),FOE_F0(t),DEP.foe,DEP.foot,0);
const toyOnBlock=(i,t,e)=>standArt(i,TOYG(t,e),FOE_F0(t),.86,RC+14,0);''')
rep('''inner=svg(HAS_ART?toyStand(i,c.foe.t):''', '''inner=svg(HAS_ART?toyStand(i,c.foe.t,c.foe):''')
rep('''if(e.k==='foe'&&at!=null&&HAS_ART)return toyOnBlock(at,e.t);''', '''if(e.k==='foe'&&at!=null&&HAS_ART)return toyOnBlock(at,e.t,e);''')

# the toys move when they act
rep('''function breakToy(i,e){ // the beaten toy pops and flies apart''', '''function toyAct(i,kind,e,tw){ // a toy on the field moves its own way: hits (toward the knight), dodges, gets up, runs…
  if(REDUCED)return;const el=elOf(i),g=el&&el.querySelector('.toy');if(!g)return;
  const [x,y]=tw||[0,-6];
  const K={
    atk:[[{transform:'none'},{transform:`translate(${x*.4}%,-12%) rotate(${x>=0?-8:8}deg) scale(.94,1.08)`,offset:.3},{transform:`translate(${x}%,${y}%) rotate(${x>=0?6:-6}deg) scale(1.08,.92)`,offset:.55},{transform:'none'}],320],
    recoil:[[{transform:'none'},{transform:'scale(1.12,.86)',offset:.15},{transform:`translate(${-x*.8}%,${-y*.4}%) rotate(${x>=0?-10:10}deg)`,offset:.4},{transform:'none'}],380],
    dodge:[[{transform:'none'},{transform:'translate(30%,-6%) rotate(14deg)',offset:.35},{transform:'translate(26%,0) rotate(10deg)',offset:.6},{transform:'none'}],380],
    armor:[[{transform:'none',filter:'none'},{transform:'scale(1.06)',filter:'brightness(1.7)',offset:.25},{transform:'none',filter:'none'}],260],
    revive:[[{transform:'translateY(14%) rotate(-80deg) scale(.8)',opacity:.4},{transform:'translateY(-10%) rotate(12deg) scale(1.1)',opacity:1,offset:.6},{transform:'none',opacity:1}],620],
    wind:[[{transform:'none'},{transform:'rotate(-10deg)',offset:.2},{transform:'rotate(10deg)',offset:.4},{transform:'rotate(-6deg)',offset:.6},{transform:'scale(1.1)',offset:.8},{transform:'none'}],620],
    rage:[[{transform:'none'},{transform:'scale(1.18,1.12)',offset:.4},{transform:'scale(1.06)',offset:.7},{transform:'none'}],480],
    flee:[[{transform:'none',opacity:1},{transform:'translateY(-18%) rotate(-12deg)',opacity:1,offset:.3},{transform:'translate(170%,-12%) rotate(24deg)',opacity:0}],520],
    shoot:[[{transform:'none'},{transform:'scale(1.1,.9)',offset:.3},{transform:'scale(.94,1.08) translateY(-6%)',offset:.6},{transform:'none'}],340]
  }[kind];if(!K)return;
  g.animate(K[0],{duration:K[1],easing:'ease-out',fill:kind==='flee'?'forwards':'none'});
}
function bossAct(i){ // the big captain or king throws his weight forward
  if(REDUCED)return;const b=board.querySelector(`:scope>.bboss[data-i="${i}"] .bb-b`);if(!b)return toyAct(i,'atk');
  b.animate([{translate:'0% 0%',scale:'1'},{translate:'0% -4%',scale:'.96 1.06',offset:.3},{translate:'0% 3%',scale:'1.08 .94',offset:.55},{translate:'0% 0%',scale:'1'}],{duration:340,easing:'ease-out'});
}
function breakToy(i,e){ // the beaten toy pops and flies apart''')
rep('''    struck(elOf(i));
''', '''    struck(elOf(i));toyAct(i,'shoot',e);
''')
rep('''      run.hp-=d;pop(run.at,d?`-${d}`:'0',d?'p-hurt':'p-guard');''', '''      run.hp-=d;heroPose(d?'hurt':'block',300);pop(run.at,d?`-${d}`:'0',d?'p-hurt':'p-guard');''')

# ---------- the knight: twelve poses, faced the way he walks ----------
rep('''if(HAS_ART){ // the knight: a little taller, with his long shadow on the ground beside him
  const ha=U('hero',16,-6,68,94),hf=70,hg=`translate(50 ${hf}) scale(1.1) translate(-50 -88)`;
  hero.innerHTML=svg(`<g transform="${hg}">${ha}</g>`)+`<svg class="hsh" viewBox="0 0 100 100" aria-hidden="true" style="overflow:visible"><g transform="${CASTM(hf)}"><g transform="${hg}">${SHAD(ha)}</g></g>${CONTACT(hf,20)}</svg>`; // the shadow goes last: lunge() moves the first child
}''', '''/* the knight's poses (11/4, Canva page 28): all at the front one's scale, his body on the middle of the panel, feet at 88.
   the side one faces left: walking right flips it */
var HF=70,HG=`translate(50 ${HF}) scale(1.1) translate(-50 -88)`,HBOX={},
  HPOSE={front:'hero',back:'hback',side:'hside',swing:'hswing',block:'hblock',jump:'hjump',hurt:'hhurt',cheer:'hcheer',ko:'hko',eat:'heat',lift:'hlift',raise:'hraise'};
function hbox(n){
  if(n in HBOX)return HBOX[n];const s=document.getElementById('a-'+n);if(!s)return HBOX[n]=null;
  const v=s.viewBox.baseVal,k=94/220,w=v.width*k,h=v.height*k,ax=+(s.getAttribute('data-ax')||.5);
  return HBOX[n]={x:+(50-w*ax).toFixed(1),y:+(88-h).toFixed(1),w:+w.toFixed(1),h:+h.toFixed(1)};
}
function heroArt(p){const n=HPOSE[p]&&hbox(HPOSE[p])?HPOSE[p]:'hero',b=hbox(n)||{x:16,y:-6,w:68,h:94};return U(n,b.x,b.y,b.w,b.h)}
function drawHero(p,flip){ // the shadow goes last: lunge() moves the first child, which is kept (only its inside changes)
  const a=heroArt(p),f=flip?' transform="translate(100 0) scale(-1 1)"':'',body=`<g transform="${HG}"><g${f}>${a}</g></g>`,sh=`<g transform="${CASTM(HF)}"><g transform="${HG}"><g${f}>${SHAD(a)}</g></g></g>${CONTACT(HF,20)}`;
  const s0=hero.firstElementChild,s1=hero.querySelector(':scope>svg.hsh');
  if(s0&&s1&&s0!==s1){s0.innerHTML=body;s1.innerHTML=sh;return}
  hero.innerHTML=svg(body)+`<svg class="hsh" viewBox="0 0 100 100" aria-hidden="true" style="overflow:visible">${sh}</svg>`;
}
if(HAS_ART)drawHero('front',false); // the knight: a little taller, with his long shadow on the ground beside him
setInterval(()=>{ // while he waits: now and then he looks around, up the road, lifts his sword or hops
  if(!HAS_ART||REDUCED||!run||run.phase!=='build'||busy||document.hidden||HS.base!=='front'||HS.tok!==HS.rest)return;
  if(++HS.idle<7)return;HS.idle=0;const r=Math.random();
  if(r<.3){heroPose('side',700,false);const t=HS.tok;setTimeout(()=>{if(HS.tok===t)heroPose('side',700,true)},700)}
  else if(r<.55)heroPose('back',1200);
  else if(r<.75)heroPose('raise',800);
  else if(r<.9){heroPose('jump',450);heroHop()}
  else heroPose('cheer',650);
  HS.rest=HS.tok;
},1000);
['pointerdown','keydown'].forEach(t=>addEventListener(t,()=>{HS.idle=0},{passive:true}));''')
# the pose helpers are declarations, so the fight and the walk (earlier in the page) can call them
rep('''function breakToy(i,e){ // the beaten toy pops and flies apart''', '''var HS={base:'front',bflip:false,cur:'front/0',tok:0,rest:0,idle:0}; // the knight's pose now, and the one he goes back to
function heroPose(p,ms,flip){ // a pose for a moment (ms), then back to his base pose
  if(!HAS_ART||typeof drawHero!=='function'||!HPOSE)return;
  const tk=++HS.tok,f=flip==null?(p===HS.base&&HS.bflip):!!flip,key=p+'/'+(f?1:0);
  if(HS.cur!==key){drawHero(p,f);HS.cur=key}
  if(ms)setTimeout(()=>{if(HS.tok===tk){heroPose(HS.base,0,HS.bflip);HS.rest=HS.tok}},ms);else HS.rest=HS.tok;
}
function heroBase(p,flip){HS.base=p;HS.bflip=!!flip;heroPose(p,0,!!flip)}
function heroHop(){if(REDUCED)return;hero.classList.remove('hop');void hero.offsetWidth;hero.classList.add('hop');setTimeout(()=>hero.classList.remove('hop'),540)}
function heroRest(){setTimeout(()=>{if(run&&run.phase==='build'&&!busy){heroBase('front');hero.classList.add('idle')}},260)}
function breakToy(i,e){ // the beaten toy pops and flies apart''')
# walking: back view going up, side view across, front coming down; a jump pose over a gap
rep('''  if(jump)hero.classList.add('jump');
''', '''  if(jump)hero.classList.add('jump');
  hero.classList.remove('idle');{const dr=rowOf(i)-rowOf(from),dc=colOf(i)-colOf(from);if(jump){heroBase(dr>0?'back':'front');heroPose('jump',Math.max(STEP,380))}else heroBase(dr>0?'back':dr<0?'front':'side',dc>0)}
''')
rep(''','p-psn'),c.psn===0?260:0);hurt();''', ''','p-psn'),c.psn===0?260:0);hurt();heroPose('hurt',260);''')
rep('''    else if(e.k==='potion'){const h=Math.min(e.v,run.maxHp-run.hp);run.hp+=h;pop(i,`+${h}`,'p-heal');fly(i,SPR.heart,$('hp'))}
    else takeGear(i,e);''', '''    else if(e.k==='potion'){const h=Math.min(e.v,run.maxHp-run.hp);run.hp+=h;pop(i,`+${h}`,'p-heal');fly(i,SPR.heart,$('hp'));heroPose('eat',700)}
    else{takeGear(i,e);heroPose('lift',900)}''')
rep('''    if(e.k==='coin'){pop(i,`+${addGold(e.v)}`,'p-gold');fly(i,SPR.coin,$('i-gold'))}''', '''    if(e.k==='coin'){pop(i,`+${addGold(e.v)}`,'p-gold');fly(i,SPR.coin,$('i-gold'));heroHop()}''')
rep('''run.hp+=h;pop(i,`+${h}`,'p-heal');fly(i,SPR.heart,$('hp'));return true}''', '''run.hp+=h;pop(i,`+${h}`,'p-heal');fly(i,SPR.heart,$('hp'));heroPose('eat',600);return true}''')
rep('''  run.chest=false;run.phase='build';render();afterAction();''', '''  run.chest=false;run.phase='build';render();heroRest();afterAction();''')
rep('''function openReward(){ // the dimension power first, then the reward for every 10 rows, then the captain's chest if a toy can evolve
''', '''function openReward(){ // the dimension power first, then the reward for every 10 rows, then the captain's chest if a toy can evolve
  heroPose('cheer',900);heroHop();
''')
rep('''  if(shown)shown();
  FXH.emit('skill',{id:d.id});''', '''  if(shown)shown();
  heroPose('raise',650);
  FXH.emit('skill',{id:d.id});''')
rep('''  hero.classList.remove('walk','hurt');hero.classList.add('down');app.classList.add('ko');FXH.emit('over',{at:run.at});
  if(REDUCED)return sleep(400);''', '''  hero.classList.remove('walk','hurt','idle');hero.classList.add('down');app.classList.add('ko');FXH.emit('over',{at:run.at});
  heroPose('hurt');
  if(REDUCED){hero.classList.add('kop');heroPose('ko');return sleep(400)}
  setTimeout(()=>{if(hero.classList.contains('down')){hero.classList.add('kop');heroPose('ko')}},900); // he lies down in his own picture
''')
rep('''hero.classList.remove('down');app.classList.remove('ko');''', '''hero.classList.remove('down','kop');app.classList.remove('ko');heroBase('front');''')
rep('''  if(s>meta.far){meta.far=s;saveMeta()}
''', '''  if(s>meta.far){meta.far=s;saveMeta()}
  if(s===(run.best|0)+1&&(run.best|0)>=3){note('じぶんの記録をこえた！','good');heroPose('cheer',800);heroHop()}
  if(s===R2_AT&&!dimOf(r))note('★2の装備も見つかるようになった','good');
''')

# ---------- motion styles ----------
rep('''.toy{transform-box:fill-box;transform-origin:50% 100%;animation:sway 2.3s ease-in-out var(--d,0s) infinite alternate}''',
    '''.toy{transform-box:fill-box;transform-origin:50% 100%;animation:sway 2.3s ease-in-out var(--d,0s) infinite alternate}
/* 11/4 each kind moves its own way while it waits */
.toy.t-soldier,.toy.t-boss{animation:tMarch 1.2s ease-in-out var(--d,0s) infinite}
@keyframes tMarch{0%,50%,100%{transform:none}25%{transform:translateY(-3%) rotate(-2.5deg)}75%{transform:translateY(-3%) rotate(2.5deg)}}
.toy.t-bugle{animation:tToot 2.4s ease-in-out var(--d,0s) infinite}
@keyframes tToot{0%,55%,100%{transform:none}65%{transform:rotate(-7deg) scale(1.04,.97)}75%{transform:rotate(-3deg) scale(1.06,.95)}85%{transform:rotate(-6deg)}}
.toy.t-cannon{animation:tRattle 2.8s linear var(--d,0s) infinite}
@keyframes tRattle{0%,78%,100%{transform:none}82%{transform:translateX(-2.5%) rotate(-1deg)}86%{transform:translateX(2.5%) rotate(1deg)}90%{transform:translateX(-1.5%)}94%{transform:scale(1.04,.96)}}
.toy.t-robot{animation:tRobo 1s steps(2,jump-none) var(--d,0s) infinite}
@keyframes tRobo{0%{transform:rotate(-3.5deg)}100%{transform:rotate(3.5deg)}}
.toy.t-archer{animation:tDraw 3s ease-in-out var(--d,0s) infinite}
@keyframes tDraw{0%,60%,100%{transform:none}75%{transform:scale(.95,1.03) translateX(-2%)}82%{transform:scale(1.04,.98) translateX(1%)}}
.toy.t-mage,.toy.t-ghost{animation:tFloat 1.9s ease-in-out var(--d,0s) infinite alternate}
@keyframes tFloat{from{transform:none}to{transform:translateY(-7%) rotate(2deg)}}
.toy.t-clown{animation:tBoing 1.5s cubic-bezier(.3,1.5,.6,1) var(--d,0s) infinite}
@keyframes tBoing{0%,100%{transform:none}30%{transform:scale(1.04,.86)}55%{transform:scale(.95,1.1) translateY(-4%)}75%{transform:scale(1.02,.97)}}
.toy.t-mason{animation:tTap 1.3s ease-in-out var(--d,0s) infinite}
@keyframes tTap{0%,50%,70%,100%{transform:none}62%,82%{transform:rotate(5deg) translateY(1%)}}
.toy.t-imp{animation:tSneak 1.7s ease-in-out var(--d,0s) infinite}
@keyframes tSneak{0%,50%,100%{transform:none}25%{transform:translate(-4%,-5%) rotate(-4deg)}75%{transform:translate(4%,-5%) rotate(4deg)}}
.toy.t-mouse{animation:tScurry .36s linear var(--d,0s) infinite alternate}
@keyframes tScurry{from{transform:translateX(-3%) rotate(-2deg)}to{transform:translateX(3%) rotate(2deg)}}
.toy.t-bear{animation:tWobble 2.6s ease-in-out var(--d,0s) infinite alternate}
@keyframes tWobble{from{transform:rotate(-4deg) scale(1.02,.98)}to{transform:rotate(4deg) scale(.99,1.01)}}
.toy.t-shroom{animation:tSquish 1.2s ease-in-out var(--d,0s) infinite alternate}
@keyframes tSquish{from{transform:none}to{transform:scale(1.06,.93)}}
.toy.t-duck{animation:tRock 1.7s ease-in-out var(--d,0s) infinite alternate}
@keyframes tRock{from{transform:rotate(-7deg)}to{transform:rotate(6deg) translateY(-2%)}}
.toy.t-frog{animation:tHop 2.2s ease-in-out var(--d,0s) infinite}
@keyframes tHop{0%,62%,94%,100%{transform:none}68%{transform:scale(1.08,.88)}78%{transform:translateY(-16%) scale(.94,1.08)}88%{transform:scale(1.06,.92)}}
.toy.t-peng{animation:tWaddle .75s ease-in-out var(--d,0s) infinite alternate}
@keyframes tWaddle{from{transform:rotate(-8deg)}to{transform:rotate(8deg)}}
.toy.t-hedge{animation:tShiver 2.4s linear var(--d,0s) infinite}
@keyframes tShiver{0%,70%,86%,100%{transform:none}74%,82%{transform:scale(1.05)}78%{transform:scale(.98)}}
.toy.t-skel{animation:tDance .5s ease-in-out var(--d,0s) infinite alternate}
@keyframes tDance{from{transform:rotate(-6deg)}to{transform:rotate(6deg) translateY(-3%)}}
.toy.t-king{animation:tRegal 3.2s ease-in-out var(--d,0s) infinite alternate}
@keyframes tRegal{from{transform:none}to{transform:translateY(-2%) scale(1.02)}}
.spawn{transform-box:fill-box;transform-origin:50% 100%;animation:tSpawn .5s cubic-bezier(.34,1.56,.64,1) both}
@keyframes tSpawn{from{transform:scale(.2,0);opacity:0}60%{transform:scale(1.1,1.15);opacity:1}to{transform:none;opacity:1}}
.pop.p-q{color:#7a4fb0;font-size:21px}
/* the knight breathes while he waits, hops for coins and joy, and lies in his own picture when he falls */
.hero.idle:not(.walk):not(.down):not(.hurt):not(.jump):not(.hop)>svg:first-child{animation:hBreathe 2.6s ease-in-out infinite alternate}
@keyframes hBreathe{to{transform:scale(1.025,.975)}}
.hero.hop>svg:first-child{animation:hHop .52s cubic-bezier(.3,1.4,.6,1)}
@keyframes hHop{0%,100%{transform:none}35%{transform:translateY(-16%) scale(.96,1.05)}70%{transform:scale(1.05,.95)}}
.hero.down.kop svg{animation:none}
.hero.down.kop>svg:first-child{animation:hKo .45s ease-out both}
@keyframes hKo{0%{transform:translateY(-10%)}60%{transform:translateY(2%) scale(1.04,.96)}100%{transform:none}}
@media (prefers-reduced-motion:reduce){.toy[class*="t-"],.spawn,.hero.idle>svg,.hero.hop>svg,.hero.down.kop>svg{animation:none!important}}''')

open(P, 'w', encoding='utf-8').write(s)
print('ok')
