# 11/4 その5：defringe_1104.py と tweak_1104d.py のあとの index.html に1回だけ当てる
#  1. 特別な積み木（積み木の箱で買うと手持ちに出る。Lv1〜3 で出る確率 4・7・10%。のっている物はない）
#     幽霊：障害物の上にも置ける（すりぬける） / ビヨヨン：まっすぐだけ。のると1マスとびこえる
#     金ぴか：のると金貨 / ハンマー：置くと となりの障害物を1つこわす / 回復：のるとHP回復 / 盾：次の戦いのダメージ半分
#     絵：Canva「PATH QUEST 素材（作業用）」20ページ（幽霊・ハンマー）＋ いまあるバネ・金貨・ハート・盾
#  2. ごほうびの説明を短く、ゲームらしい言い方に
# usage: python3 tools/ui/tweak_1104e.py <幽霊とハンマーを切り出したフォルダ(ghost.png, hammer.png)> [index.html]
import sys, io, base64
from PIL import Image
CUT = sys.argv[1]
P = sys.argv[2] if len(sys.argv) > 2 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()

def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, old[:100])
    s = s.replace(old, new)

# ---------- art: the ghost and the mallet as symbols ----------
sym = ''
for n in ('ghost', 'hammer'):
    im = Image.open(f'{CUT}/{n}.png').convert('RGBA'); im.thumbnail((128, 128), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'WEBP', quality=84, alpha_quality=90, method=6)
    w, h = im.size
    sym += f'<symbol id="a-sp_{n}" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid meet"><image href="data:image/webp;base64,{base64.b64encode(b.getvalue()).decode()}" width="{w}" height="{h}"/></symbol>'
rep('<symbol id="a-sk_turn"', sym + '<symbol id="a-sk_turn"')

# ---------- 1. special blocks ----------
rep('const UPS=[', '''/* special blocks (11/4): bought in the toy box, each level makes that kind come more often; none carries a rider */
const SPK=[ // [kind, upgrade key, name, short name under the block, what it does]
  ['ghost','sg','幽霊の積み木','幽霊','障害物の上にも置ける'],
  ['spring','sj','ビヨヨンの積み木','ビヨヨン','のると1マスとびこえる（まっすぐだけ）'],
  ['gold','sm','金ぴかの積み木','金ぴか','のると金貨がもらえる'],
  ['hammer','sh','ハンマーの積み木','ハンマー','置くと となりの障害物を1つこわす'],
  ['heal','sr','回復の積み木','回復','のるとHPが回復'],
  ['guard','sd','盾の積み木','盾','のると次の戦いのダメージ半分']
];
const SP_ID={};SPK.forEach(x=>SP_ID[x[0]]=x);
const SP_P=[0,4,7,10]; // % that a new block is this kind, by level
const SP_ICON={ghost:'sp_ghost',spring:'it_spring',gold:'coin',hammer:'sp_hammer',heal:'heart',guard:'sk_guard'};
const spIco=sp=>`<g class="spi">${U(SP_ICON[sp],27,18,46,46)}</g>`;
const spBlock=sp=>{const c={ghost:4,spring:1,gold:2,hammer:0,heal:3,guard:4}[sp],m=sp==='spring'?5:15,b=blockSVG(c)+roadSVG(m,BLOCKS[c][1],4,96);return (sp==='ghost'?`<g opacity=".72">${b}</g>`:b)+spIco(sp)};
const UPS=[''')
rep("  {k:'ds',deck:1,name:'はじめの十字',desc:'冒険のはじめ、手持ちに十字が1こ（2つで2こ）',art:SK_ART.cross+STAR(18,84,10),max:2,cost:l=>60+60*l}\n];",
    "  {k:'ds',deck:1,name:'はじめの十字',desc:'冒険のはじめ、手持ちに十字が1こ（2つで2こ）',art:SK_ART.cross+STAR(18,84,10),max:2,cost:l=>60+60*l},\n"
    "  ...SPK.map(([sp,k,n,,d])=>({k,deck:1,sp,name:n,desc:d,art:spBlock(sp),max:3,cost:l=>(sp==='ghost'||sp==='spring'?45:35)+30*l}))\n];")
# the shop: its own shelf, and the chance as the number that changes
rep("+'</div><p class=\"sh-cap\">のっている物</p><div class=\"sh-sheet\">'+UPS.filter(u=>u.deck&&MIX_OF[u.k]==null).map(upRow).join('')+'</div>';",
    "+'</div><p class=\"sh-cap\">のっている物</p><div class=\"sh-sheet\">'+UPS.filter(u=>u.deck&&!u.sp&&MIX_OF[u.k]==null).map(upRow).join('')+'</div><p class=\"sh-cap\">特別な積み木</p><div class=\"sh-sheet\">'+UPS.filter(u=>u.sp).map(upRow).join('')+'</div>';")
rep("const MIXG=[", "SPK.forEach(([,k])=>UPV[k]=['出る確率',l=>SP_P[Math.min(3,l|0)]+'%']);\nconst MIXG=[")
# a new block may be special
rep("const makeTile=(f,m)=>({m:m||pickW(shapeW()),e:makeEvent(f),c:rnd(BLOCKS.length)});",
    '''function pickSp(){const u=meta.up;for(const [sp,k] of shuffle(SPK.slice())){const l=u[k]|0;if(l&&Math.random()*100<SP_P[Math.min(3,l)])return sp}return null}
const makeTile=(f,m)=>{
  if(!m){const sp=pickSp();if(sp)return {m:sp==='spring'?(Math.random()<.65?5:10):pickW(shapeW()),e:null,c:rnd(BLOCKS.length),sp}}
  return {m:m||pickW(shapeW()),e:makeEvent(f),c:rnd(BLOCKS.length)};
};''')
# how a special block looks: the mark on top, the ghost see-through
rep("const tileArt=(t,inTray,at)=>{const c=t.c|0,", "const tileArt=(t,inTray,at)=>{const a0=tileArt0(t,inTray,at);return !t.sp?a0:(t.sp==='ghost'?`<g opacity=\".72\">${a0}</g>`:a0)+spIco(t.sp)};\nconst tileArt0=(t,inTray,at)=>{const c=t.c|0,")
rep("  if(!e)return `${s}の積み木`;", "  if(t.sp)return `${SP_ID[t.sp][2]}（${s}）`;\n  if(!e)return `${s}の積み木`;")
rep("  else if(e){const g=gearOf(e);if(g){if(owned(g.id)){c=' coin';h=`${ico(SPR.coin)}+${gainOf(dupGold(g))}`}else{c=' new';h='<b>NEW</b>'}}}\n  return `<span class=\"lbl${c}\">${h}</span>`;",
    "  else if(e){const g=gearOf(e);if(g){if(owned(g.id)){c=' coin';h=`${ico(SPR.coin)}+${gainOf(dupGold(g))}`}else{c=' new';h='<b>NEW</b>'}}}\n  else if(t.sp){c=' sp';h=`<b>${SP_ID[t.sp][3]}</b>`}\n  return `<span class=\"lbl${c}\">${h}</span>`;")
# where blocks can go: the ghost also onto an obstacle, the spring throws the knight over one cell (never over a fence or a captain's gap)
rep('''function frontier(){
  const map=new Map(),m=exitsOf(run.at)&~DOWN;
  for(const b of BITS){
    if(!(m&b))continue;
    const j=nbr(run.at,b),c=j>=0&&cellAt(j);
    if(!c||c.rock||c.foe||c.tile||c.start)continue;
    map.set(j,OPP[b]);
  }
  return map;
}''', '''function frontier(){
  const map=new Map(),m=exitsOf(run.at)&~DOWN,here=cellAt(run.at),jump=!!(here&&here.tile&&here.tile.sp==='spring');
  map.rock=new Map(); // obstacles next in line: only a ghost block goes there
  for(const b of BITS){
    if(!(m&b))continue;
    let j=nbr(run.at,b);
    if(jump&&j>=0){const o=cellAt(j);if(!o||o.rock===2||(o.tile&&o.tile.gate))continue;j=nbr(j,b)} // the spring: over one cell
    const c=j>=0&&cellAt(j);
    if(!c)continue;
    if((c.rock===1||c.rock===3)&&!c.foe&&!c.tile&&!c.start){map.rock.set(j,OPP[b]);continue}
    if(c.rock||c.foe||c.tile||c.start)continue;
    map.set(j,OPP[b]);
  }
  return map;
}
const openF=F=>F.size>0||(!!F.rock&&F.rock.size>0&&(meta.up.sg|0)>0); // somewhere a block could still go''')
rep("const fits=(t,j,F)=>!!t&&F.has(j)&&!!(t.m&F.get(j));\nconst anyFit=(t,F)=>{if(!t)return false;for(const j of F.keys())if(t.m&F.get(j))return true;return false};",
    "const fits=(t,j,F)=>!!t&&(F.has(j)?!!(t.m&F.get(j)):t.sp==='ghost'&&!!F.rock&&F.rock.has(j)&&!!(t.m&F.rock.get(j)));\n"
    "const anyFit=(t,F)=>{if(!t)return false;for(const j of F.keys())if(t.m&F.get(j))return true;if(t.sp==='ghost'&&F.rock)for(const [j,b] of F.rock)if(t.m&b)return true;return false};")
rep("  if(!F.size){if(!rescue(F)){why='dead';flashCell(run.at)}}", "  if(!openF(F)){if(!rescue(F)){why='dead';flashCell(run.at)}}")
rep("  const noFit=F.size>0&&!run.hand.some(t=>anyFit(t,F));", "  const noFit=openF(F)&&!run.hand.some(t=>anyFit(t,F));")
rep("const stuck=run.phase==='build'&&!busy&&((noFit&&run.rolls>0)||((noFit||!F.size)&&rescue(F)));", "const stuck=run.phase==='build'&&!busy&&((noFit&&run.rolls>0)||((noFit||!openF(F))&&rescue(F)));")
# the obstacle a ghost can go onto shows the faint block too; a ghost block over an obstacle shows the obstacle faintly
rep("  else if(c.rock){cls+=' rock'+(aim&&aim.kind==='rock'&&c.rock!==2&&rowOf(i)>=rowOf(run.at)?' aim':'');inner=svg(c.rock===3?brickArt(i):obArt(i,a))}",
    "  else if(c.rock){cls+=' rock'+(aim&&aim.kind==='rock'&&c.rock!==2&&rowOf(i)>=rowOf(run.at)?' aim':'');inner=svg(c.rock===3?brickArt(i):obArt(i,a));\n"
    "    if(F&&F.rock&&F.rock.has(i)&&sel>=0&&fits(run.hand[sel],i,F)){cls+=' front fit';inner+=`<div class=\"gh\">${svg(tileArt(run.hand[sel],false))}</div>`}}")
rep("  else if(c.tile){cls+=' laid'+(i===justPlaced?' new':'')+(c.tile.m===15&&!c.tile.gate?' ace':'');inner=svg(tileArt(c.tile,false,i))+badge(c.tile.e);",
    "  else if(c.tile){cls+=' laid'+(i===justPlaced?' new':'')+(c.tile.m===15&&!c.tile.gate?' ace':'')+(c.tile.sp?' sp-'+c.tile.sp:'');inner=svg(tileArt(c.tile,false,i))+badge(c.tile.e)+(c.tile.over?`<div class=\"gho\">${svg(c.tile.over===3?brickArt(i):obArt(i,a))}</div>`:'');")
rep('''  for(const [j] of F){const el=elOf(j);if(!el)continue;const ok=!!t&&fits(t,j,F);el.classList.toggle('fit',ok);
    const g=el.querySelector(':scope>.gh');if(g)g.remove();if(ok)el.insertAdjacentHTML('beforeend',`<div class="gh">${svg(tileArt(t,false))}</div>`)}''',
'''  for(const [j] of F){const el=elOf(j);if(!el)continue;const ok=!!t&&fits(t,j,F);el.classList.toggle('fit',ok);
    const g=el.querySelector(':scope>.gh');if(g)g.remove();if(ok)el.insertAdjacentHTML('beforeend',`<div class="gh">${svg(tileArt(t,false))}</div>`)}
  for(const [j] of F.rock||[]){const el=elOf(j);if(!el)continue;const ok=!!t&&fits(t,j,F);el.classList.toggle('front',ok);el.classList.toggle('fit',ok);
    const g=el.querySelector(':scope>.gh');if(g)g.remove();if(ok)el.insertAdjacentHTML('beforeend',`<div class="gh">${svg(tileArt(t,false))}</div>`)}''')
# placing: the ghost slips over the obstacle, the mallet knocks one down
rep("  if(!fits(t,j,frontier())){flashCell(j);flashSlot(hi);return}\n  cellAt(j).tile=t;",
    "  if(!fits(t,j,frontier())){flashCell(j);flashSlot(hi);return}\n"
    "  {const o=cellAt(j);if(o.rock){t.over=o.rock;o.rock=0;note('障害物をすりぬけた','good')}}\n"
    "  if(t.sp==='hammer')hammerHit(j);\n"
    "  cellAt(j).tile=t;")
rep("async function proceed(){", '''function hammerHit(j){ // the cell in front first, then the sides, then behind
  const ord=[1,...shuffle([2,8]),4];
  for(const b of ord){const n=nbr(j,b),c=n>=0&&cellAt(n);if(!c||c.foe||c.tile||!(c.rock===1||c.rock===3))continue;
    c.rock=0;setTimeout(()=>{puff(n);spark(n);shake(4)},220);note('障害物をこわした','good');return true}
  return false;
}
function spStep(i,t){ // a special block does its thing the first time the knight stands on it
  if(t.sp==='gold'){const g=addGold(3+lvOf(rowOf(i)));pop(i,`+${g}`,'p-gold');fly(i,SPR.coin,$('i-gold'));return true}
  if(t.sp==='heal'){const h=Math.min(Math.max(2,Math.ceil(run.maxHp*.15)),run.maxHp-run.hp);if(h<=0)return false;run.hp+=h;pop(i,`+${h}`,'p-heal');fly(i,SPR.heart,$('hp'));return true}
  if(t.sp==='guard'){FX().half=1;note('つぎの戦いはダメージ半分','good');return true}
  return false;
}
async function proceed(){''')
# stepping: the spring jump arcs, the rows jumped over still count
rep("  const up=rowOf(i)>rowOf(run.at),from=run.at;", "  const up=rowOf(i)>rowOf(run.at),from=run.at,jump=Math.abs(rowOf(i)-rowOf(from))+Math.abs(colOf(i)-colOf(from))>1;\n  if(jump)hero.classList.add('jump');")
rep("  FXH.emit('step',{from,to:i,up});\n  await sleep(STEP);", "  FXH.emit('step',{from,to:i,up});\n  await sleep(jump?Math.max(STEP,380):STEP);hero.classList.remove('jump');")
rep("  if(rowOf(i)>run.top)reach(rowOf(i));", "  for(let r=run.top+1;r<=rowOf(i);r++)reach(r); // a spring may jump a row: every row on the way counts")
rep("  let hit=false;const e=c.tile.e;", "  let hit=false;const e=c.tile.e;\n  if(c.tile.sp&&!c.tile.done){c.tile.done=1;if(spStep(i,c.tile))hit=true}")
# the shield block halves the next fight
rep("FX().guard?0:Math.max(0,e.atk-run.def)", "FX().guard?0:Math.ceil(Math.max(0,e.atk-run.def)/(FX().half?2:1))", 2)
rep("  if(FX().guard)run.fx.guard=0; // the shield took this one fight", "  if(FX().guard)run.fx.guard=0; // the shield took this one fight\n  if(FX().half)run.fx.half=0;")

# ---------- 2. shorter reward lines ----------
for a, b in [
    ("return `積み木を置くたび、近くの敵へ${g(t.n)}機とんでいく。攻撃の${g(t.p)}%`", "return `置くたび、近くの敵へ${g(t.n)}機（攻撃${g(t.p)}%）`"),
    ("return `戦いでたたくたび、コマの追い打ち。攻撃の${g(t.p)}%`", "return `たたくたび追い打ち（攻撃${g(t.p)}%）`"),
    ("return `${g(t.e)}マス進むごとにドカン。まわり${g(t.r)}マスと手持ちの敵に攻撃の${g(t.p)}%`", "return `${g(t.e)}マスごとに爆発。まわり${g(t.r)}マスに攻撃${g(t.p)}%`"),
    ("return `積み木を置くたび、手持ちの敵${g(t.n)}体に攻撃の${g(t.p)}%`", "return `置くたび、手持ちの敵${g(t.n)}体へ（攻撃${g(t.p)}%）`"),
    ("return `${g(t.e)}マスごとにシャボン（${g(t.m)}こまで）。敵の攻撃・矢・魔法を1回ふせぐ`", "return `${g(t.e)}マスごとにシャボン。攻撃を1回ふせぐ`"),
    ("return `守り+25%（少なくとも+${PM()}）`", "return '守り+25%'"),
    ("return '最大HP+25%、HPも同じだけ回復'", "return '最大HP+25%'"),
    ("return `会心（ダメージ2倍）+8%（Lv${lv}で${8*lv}%）`", "return '会心率+8%'"),
    ("return `勝つたび、最大HPの${3*lv}%回復`", "return `勝つたびHP${3*lv}%回復`"),
    ("return 'リロール+1、大将をこえたときの回数も+1'", "return 'リロール+1'"),
    ("return 'スキルの待ち時間 -1マス'", "return 'クールタイム-1マス'"),
    ("plane:'紙ひこうきの数が2倍、ぜんぶ会心（ダメージ2倍）'", "plane:'2倍の数がとび、ぜんぶ会心'"),
    ("top:'追い打ちが攻撃の100%。戦いのはじめの1回は敵の攻撃を受けない'", "top:'追い打ち100%。最初の1回はダメージなし'"),
    ("bomb:'2マスごとにドカン。まわり3マスと手持ちの敵に攻撃の220%、倒すと金貨2倍'", "bomb:'2マスごとに大爆発（攻撃220%）。金貨2倍'"),
    ("boomer:'手持ちの敵ぜんぶに、攻撃の150%'", "boomer:'手持ちの敵ぜんぶへ（攻撃150%）'"),
    ("bubble:'2マスごとにシャボン（3こまで）。割れるたびHPが最大HPの10%回復'", "bubble:'2マスごとにシャボン。割れるとHP回復'"),
    ("return w?`（${w.n}のLv${MAXLV}と合わせて大進化）`:'';", "return w?`（${w.n}Lv${MAXLV}と大進化）`:'';"),
    ("s:`攻撃が1.5倍（いま ${run.atk}）`", "s:`攻撃×1.5（いま${run.atk}）`"),
    ("s:`最大HPが1.5倍、HPもまんたん（いま ${run.maxHp}）`", "s:'最大HP×1.5・HP全回復'"),
    ("s:run.def?`守りが1.5倍（いま ${run.def}）`:`守り+${P}`", "s:run.def?`守り×1.5（いま${run.def}）`:`守り+${P}`"),
    ("s:`会心（ダメージ2倍）が出やすくなる（いま ${Math.round((q.crit||0)*100)}%）`", "s:'会心率+15%'"),
    ("s:'この冒険のあいだ、十字の積み木が出やすくなる'", "s:'十字の積み木が出やすくなる'"),
    ("s:`勝つたびにHPが${2*P}回復する`", "s:`勝つたびHP+${2*P}`"),
    ("s:'リロール+3、場所が変わるたびのリロールも+1'", "s:'リロール+3'"),
    ("s:'受けたダメージの半分を相手に返す（矢や魔法も）'", "s:'受けたダメージの50%を返す'"),
    ("s:'杖・ステッキの魔法と毒のダメージが2倍'", "s:'魔法と毒のダメージ×2'"),
    ("s:'戦いで いつも先に攻撃する'", "s:'いつも先に攻撃'"),
    ("s:'持っている武器とお守りが ぜんぶLv+1'", "s:'武器とお守りがぜんぶLv+1'"),
    ("s:`HPを${heal}回復（いま ${Math.max(0,run.hp)}/${run.maxHp}）`", "s:`HP+${heal}`"),
    ("s:'持ち帰って強化に使える'", "s:'強化に使える'"),
    ("s:`手持ちの入れかえが2回ふえる（いま ${run.rolls}）`", "s:'リロール+2'"),
]:
    rep(a, b, s.count(a) if s.count(a) > 1 else 1)

# ---------- css ----------
CSS = '''/* ===== 11/4: special blocks ===== */
.cell .gho{position:absolute;inset:0;opacity:.36;pointer-events:none}
.cell .gho svg{width:100%;height:100%;overflow:visible}
.slot .lbl.sp b{color:#6b4a3a;font-weight:800}
.hero.jump{transition-duration:.36s}
.hero.jump>svg:not(.hsh){animation:hjump .38s ease-out}
@keyframes hjump{0%{translate:0 0}45%{translate:0 -70%}100%{translate:0 0}}
@media (prefers-reduced-motion:reduce){.hero.jump>svg{animation:none}}
'''
rep('/* ===== end of 11/4 ===== */', CSS + '/* ===== end of 11/4 ===== */')

open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
