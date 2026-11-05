# 11/4 デバッグ その1：スキル・特別な積み木・大将まわり（tweak_1104r.py のあとに1回だけ）
#  1 ビヨヨンの着地点が障害物で行き止まりのとき、「おかたづけ」が使えるのにゲームオーバーになっていた → 道の先の障害物（F.rock）を見る
#  2 王さまを大砲・魔法の杖・おもちゃの武器でたおすと装備が出なかった（または拾えないマスに落ちた）→ その場で手に入る
#  3 王さまの前の広場（49段など）でリロールが2まで戻らなかった → 大将と同じく、つぎが大将か王さまの段なら戻す
#  4 スキルの紙を開いたまま積み木をドラッグで置くと、紙が古いクールタイムのまま残った → 置いたら閉じる
#  5 十字の積み木に「くるっと回す」「まほうの十字」を使うと、何も変わらないのにクールタイムだけ減った → 使わずにひとこと
#  6 「かたい盾」が矢や魔法をずっと防いでいた（つぎの戦いまで消えない）→ 盾は戦い1回ぶん。矢・魔法には効かない（文のとおり）
#  7 「宝さがし」が金貨・回復ののった積み木や特別な積み木にも装備をのせて、のっていた物が消えた → 何ものっていない ふつうの積み木だけ
#    回復の積み木：HP がまんたんのときは「HPは まんたん」と出す
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)

# 1
rep("  if(ready('clear')){const m=exitsOf(run.at)&~DOWN;for(const b of BITS)if(m&b){const j=nbr(run.at,b),c=j>=0&&cellAt(j);if(c&&(c.rock===1||c.rock===3||c.foe))return true}}",
    "  if(ready('clear')&&F.rock&&F.rock.size)return true; // an obstacle where the road goes on (a spring's landing too)")
# 2: one way to hand over a piece of gear, used by the walk and by every far kill of the king
rep("""    else{const g=gearOf(e);if(g){
      if(owned(g.id)){pop(i,`+${addGold(dupGold(g))}`,'p-gold');fly(i,SPR.coin,$('i-gold'))}
      else{ // a new piece goes home to the collection; an empty slot takes it for the next climb
        meta.gear.own.push(g.id);(meta.newg=meta.newg||[]).push(g.id);if(!meta.gear.eq[g.s])meta.gear.eq[g.s]=g.id;saveMeta();
        (run.found=run.found||[]).push(g.id);
        note(`${g.n}を見つけた`,'good');fly(i,g.art,$('quit'));
      }
    }}""", "    else takeGear(i,e);")
rep("function hammerHit(j){", """function takeGear(i,e){ // a piece of gear reaches the knight: a new one goes home to the collection (an empty slot takes it for the next climb), one he has turns into gold
  const g=gearOf(e);if(!g)return false;
  if(owned(g.id)){pop(i,`+${addGold(dupGold(g))}`,'p-gold');fly(i,SPR.coin,$('i-gold'))}
  else{
    meta.gear.own.push(g.id);(meta.newg=meta.newg||[]).push(g.id);if(!meta.gear.eq[g.s])meta.gear.eq[g.s]=g.id;saveMeta();
    (run.found=run.found||[]).push(g.id);
    note(`${g.n}を見つけた`,'good');fly(i,g.art,$('quit'));
  }
  return true;
}
const kingGear=i=>({k:'gear',g:pickGear(SLOTS[rnd(3)].k,Math.min(4,dimOf(rowOf(i))+2),true).id}); // the king leaves a piece of the next dimension's rarest gear
const kingDrop=i=>takeGear(i,kingGear(i)); // the king falls from afar: the piece comes to the knight at once
function hammerHit(j){""")
rep("    c.tile.e=foe.king?{k:'gear',g:pickGear(SLOTS[rnd(3)].k,Math.min(4,dimOf(rowOf(i))+2),true).id}:null; // the king leaves a piece of the next dimension's rarest gear",
    "    c.tile.e=foe.king?kingGear(i):null; // the king leaves a piece of the next dimension's rarest gear")
rep("    if(x.foe)x.foe=null;else x.tile.e=e.king?{k:'gear',g:pickGear(SLOTS[rnd(3)].k,Math.min(4,dimOf(rowOf(i))+2),true).id}:null;",
    "    if(x.foe)x.foe=null;else{x.tile.e=null;if(e.king)kingDrop(i)}")
rep("    for(const h of hits){h.e.hp-=dmg;if(h.e.hp<=0){h.dead=true;h.g=addGold(h.e.gold);if(h.stand)h.stand.foe=null;else h.on.e=null}}",
    "    for(const h of hits){h.e.hp-=dmg;if(h.e.hp<=0){h.dead=true;h.g=addGold(h.e.gold);if(h.stand)h.stand.foe=null;else{h.on.e=null;if(h.e.king&&h.i!=null)kingDrop(h.i)}}}")
rep("      if(e.hp<=0){const g=addGold(e.gold);if(x.foe)x.foe=null;else x.tile.e=null;updateCell(i);breakToy(i,e);",
    "      if(e.hp<=0){const g=addGold(e.gold);if(x.foe)x.foe=null;else{x.tile.e=null;if(e.king)kingDrop(i)}updateCell(i);breakToy(i,e);")
# 3 (the gate test is written out here: reach() can run before isGate is defined)
rep("  if(s%SPAN===SPAN-1&&run.rolls<2){", "  if(((s+1)%SPAN===0||(s+1)%DIM_LEN===0)&&run.rolls<2){") # the yard in front of a captain or the king
# 4
rep("  if(busy||!run||run.phase!=='build')return;\n  if(fpick>=0)hidePick();", "  if(busy||!run||run.phase!=='build')return;\n  if(pick>=0||fpick>=0)hidePick(); // a skill's paper or a toy's paper closes (a drag does not pass the slots)")
# 5
rep("  turn:x=>{run.hand[x].m=rot(run.hand[x].m);return dealFx(x)},\n  cross:x=>{run.hand[x].m=15;aceNew=[x];return null},",
    "  turn:x=>{const t=run.hand[x];if(rot(t.m)===t.m)return '回しても同じ形';t.m=rot(t.m);return dealFx(x)},\n  cross:x=>{if(run.hand[x].m===15)return 'もう十字の積み木';run.hand[x].m=15;aceNew=[x];return null},")
# 6
rep("      let d=FX().guard?0:e.t==='mage'?e.atk:Math.max(0,e.atk-run.def);if(d&&bubbleBlock(run.at))d=0;",
    "      let d=e.t==='mage'?e.atk:Math.max(0,e.atk-run.def);if(d&&bubbleBlock(run.at))d=0; // the hard shield waits for the next fight; shots are not fights")
# 7
rep("  return run.hand.map((t,i)=>{const foe=!!(t&&t.e&&t.e.k==='foe');return t&&(kind==='tile'||(kind==='foe')===foe)?i:-1}).filter(i=>i>=0);",
    "  return run.hand.map((t,i)=>{const foe=!!(t&&t.e&&t.e.k==='foe');return t&&(kind==='tile'||(kind==='free'?!t.e&&!t.sp:foe))?i:-1}).filter(i=>i>=0);")
rep("free:'敵のいない積み木がない'", "free:'何ものっていない積み木がない'")
rep("  if(t.sp==='heal'){const h=Math.min(Math.max(2,Math.ceil(run.maxHp*.15)),run.maxHp-run.hp);if(h<=0)return false;",
    "  if(t.sp==='heal'){const h=Math.min(Math.max(2,Math.ceil(run.maxHp*.15)),run.maxHp-run.hp);if(h<=0){note('HPは まんたん');return false}")
open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
