# 11/4 その6：tweak_1104e.py のあとの index.html に1回だけ当てる
#  1. 大将（王さま）の門：2×2のピンクの十字マス。大将はそのまんなかに立ち、下の2マスのどちらからでも戦える。
#     倒したら、四角の上の2マスのまわりから先へ進める（四角の中は自分で歩いて通る）
#  2. 演出の電車・楽隊：障害物や置いた積み木の上を通る（後ろにかくれない）
#  3. 置くマス：指の下のマスは盤のマス目から決める（となりの障害物の頭や数字が重なっていても断られない）
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()

def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, old[:100])
    s = s.replace(old, new)

# ---------- 1. the captain's square ----------
rep('''    row.forEach((c,k)=>{if(k!==b)c.rock=2});
    row[b].tile={m:15,e:s%DIM_LEN===0?makeKing(lvOf(r),r):makeBoss(lvOf(r),r),c:rnd(BLOCKS.length),gate:1,kg:s%DIM_LEN===0?1:0}; // kg: the king's gap opens into a portal once he falls''',
'''    const nb=b<=2?b+1:b-1,pz=[idOf(r,b),idOf(r,nb),idOf(r+1,b),idOf(r+1,nb)]; // a square of four cross panels: this row and the next (11/4)
    row.forEach((c,k)=>{if(k!==b&&k!==nb)c.rock=2});
    row[b].tile={m:15,e:s%DIM_LEN===0?makeKing(lvOf(r),r):makeBoss(lvOf(r),r),c:0,gate:1,anc:1,pz,bi:pz[0],kg:s%DIM_LEN===0?1:0}; // kg: the king's gap opens into a portal once he falls
    Object.assign(row[nb],{rock:0,gem:0,foe:null,tile:{m:15,e:null,c:0,gate:1,pz,bi:pz[0]}});''')
rep('''    row[b].rock=0;
    const fp=''', '''    row[b].rock=0;
    const fp=''')
rep('''  if(prev[b].rock===1)prev[b].rock=0;
  prev[b].foe=null;
  run.spine=b;''', '''  if(prev[b].rock===1)prev[b].rock=0;
  prev[b].foe=null;
  const sq=prev.find(c=>c.tile&&c.tile.anc); // the top half of the captain's square
  if(sq)for(const id of sq.tile.pz)if(rowOf(id)===r)Object.assign(row[colOf(id)],{rock:0,gem:0,foe:null,tile:{m:15,e:null,c:0,gate:2,pz:sq.tile.pz,bi:sq.tile.bi}});
  run.spine=b;''')
# only the bottom row of the square is walked into from below
rep("    if(c&&c.tile&&c.tile.gate)return j; // even once the cannon has cleared it", "    if(c&&c.tile&&c.tile.gate===1)return j; // even once the cannon has cleared it")
# standing in the square after he falls: the way on is anywhere around its top half
rep('''  map.rock=new Map(); // obstacles next in line: only a ghost block goes there''', '''  map.rock=new Map(); // obstacles next in line: only a ghost block goes there
  map.via=new Map(); // in the captain's square: which of its panels the knight walks to first
  const pz=here&&here.tile&&here.tile.pz;
  if(pz&&!sqBoss(pz)){
    for(const p of pz)for(const b of BITS){
      if(b===DOWN)continue;const j=nbr(p,b);if(j<0||pz.includes(j))continue;const c=cellAt(j);if(!c)continue;
      if((c.rock===1||c.rock===3)&&!c.foe&&!c.tile&&!c.start){if(!map.rock.has(j)){map.rock.set(j,OPP[b]);map.via.set(j,p)}continue}
      if(c.rock||c.foe||c.tile||c.start||map.has(j))continue;
      map.set(j,OPP[b]);map.via.set(j,p);
    }
    return map;
  }''')
rep("const openF=F=>", '''const sqBoss=pz=>{const a=cellAt(pz[0]);return !!(a&&a.tile&&a.tile.e&&a.tile.e.k==='foe')}; // the captain still stands in his square
const sqPath=(a,b)=>Math.abs(rowOf(a)-rowOf(b))+Math.abs(colOf(a)-colOf(b))===1?[b]:[idOf(rowOf(b),colOf(a)),b];
const openF=F=>''')
rep("  if(!fits(t,j,frontier())){flashCell(j);flashSlot(hi);return}\n  {const o=cellAt(j);if(o.rock)",
    "  const F=frontier();if(!fits(t,j,F)){flashCell(j);flashSlot(hi);return}\n  run.via=F.via&&F.via.has(j)?F.via.get(j):-1;\n  {const o=cellAt(j);if(o.rock)")
rep("  if(run.at!==run.target&&!await stepTo(run.target))return;",
    "  if(run.at!==run.target&&run.via>=0&&run.via!==run.at)for(const p of sqPath(run.at,run.via))if(!await stepTo(p))return; // across the captain's square first\n"
    "  run.via=-1;\n  if(run.at!==run.target&&!await stepTo(run.target))return;")
# walking into either bottom panel of the square fights him
rep("  const c=cellAt(i),foe=c.tile&&c.tile.e&&c.tile.e.k==='foe'?c.tile.e:null;",
    "  const c=cellAt(i),hi=c.tile&&c.tile.bi!=null?c.tile.bi:i,h=cellAt(hi)||c,foe=h.tile&&h.tile.e&&h.tile.e.k==='foe'?h.tile.e:null; // the captain stands in the middle of his square")
rep("    if(!await battle(foe,run.at,i)){await knockOut();busy=false;gameOver('hp');return false}",
    "    if(!await battle(foe,run.at,hi)){await knockOut();busy=false;gameOver('hp');return false}\n    if(hi!==i){h.tile.e=null;updateCell(hi)}")
rep("  if(j>=0&&fits(t,j,frontier())){const g=gateFrom(j,t.m),ge=g>=0&&cellAt(g).tile.e;if(ge)d+=dmgFor(ge)}",
    "  if(j>=0&&fits(t,j,frontier())){const g=gateFrom(j,t.m),gc=g>=0&&cellAt(g),gh=gc&&gc.tile.bi!=null?cellAt(gc.tile.bi):gc,ge=gh&&gh.tile&&gh.tile.e;if(ge&&ge.k==='foe')d+=dmgFor(ge)}")
# the big captain: found by his own panel, standing in the middle of the four
ANC = "x.tile&&x.tile.gate===1&&(x.tile.anc||!x.tile.pz)"
rep("    const b=prev.findIndex(c=>c.tile&&c.tile.gate);if(b<0)return;", "    const b=prev.findIndex(x=>" + ANC + ");if(b<0)return;")
rep("b=row?row.findIndex(x=>x.tile&&x.tile.gate):-1;", "b=row?row.findIndex(x=>" + ANC + "):-1;")
rep("const b=row.findIndex(x=>x.tile&&x.tile.gate);if(b<0)continue;", "const b=row.findIndex(x=>" + ANC + ");if(b<0)continue;")
rep("const cx=en.b<en.nb?86:114,k=en.king?1.75:1.8", "const cx=100,k=en.king?1.4:1.55")
rep('''`<div class="bb-tag" style="left:${g.offsetLeft-L}px;bottom:0;''', '''`<div class="bb-tag" style="left:${(w-g.offsetWidth)/2}px;bottom:0;''')

# ---------- 2. the train and the band pass in front ----------
rep(".lf-train,.lf-band{position:absolute;left:0;top:0}", ".lf-train,.lf-band{position:absolute;left:0;top:0;z-index:2} /* over the obstacles and the laid blocks (they come later than the cells), under the knight (11/4) */")

# ---------- 3. the panel under a finger comes from the grid ----------
rep("function cellUnder(x,y){const el=document.elementFromPoint(x,y),c=el&&el.closest('.cell');return c&&board.contains(c)?+c.dataset.i:-1}",
'''function cellAtPoint(x,y){ // the panel under a point by the grid itself: a tall obstacle's head, a number or a critter over it never gets in the way (11/4)
  const v=view.getBoundingClientRect();if(!win.pitch||x<v.left||x>v.right||y<v.top||y>v.bottom)return -1;
  const r=board.getBoundingClientRect(),lx=x-r.left-4,ly=y-r.top-4;if(lx<0||ly<0)return -1;
  const c=Math.floor(lx/win.pitch),rr=win.hi-Math.floor(ly/win.pitch);
  return c<0||c>=W||rr<win.lo||rr>win.hi?-1:idOf(rr,c);
}
function cellUnder(x,y){return cellAtPoint(x,y)}
function pickCellAt(e,c){ // a tap: the grid's panel when the held block can go there, else the panel that was touched
  const g=view.contains(e.target)?cellAtPoint(e.clientX,e.clientY):-1,el=c&&board.contains(c)?+c.dataset.i:-1;
  if(sel>=0&&run.hand[sel]&&!aim){const F=frontier(),t=run.hand[sel];if(g>=0&&fits(t,g,F))return g;if(el>=0&&fits(t,el,F))return el}
  return el>=0?el:g;
}''')
rep('''  const s=e.target.closest('.slot'),c=e.target.closest('.cell');
  if(!(s&&handEl.contains(s))&&!(c&&board.contains(c)))return;
  if(s)e.preventDefault();
  drag={id:e.pointerId,x:e.clientX,y:e.clientY,slot:s?+s.dataset.i:-1,cell:!s?+c.dataset.i:-1,moving:false};''',
'''  const s=e.target.closest('.slot'),c=e.target.closest('.cell'),ci=s&&handEl.contains(s)?-1:pickCellAt(e,c);
  if(!(s&&handEl.contains(s))&&ci<0)return;
  if(s)e.preventDefault();
  drag={id:e.pointerId,x:e.clientX,y:e.clientY,slot:s&&handEl.contains(s)?+s.dataset.i:-1,cell:ci,moving:false};''')

open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
