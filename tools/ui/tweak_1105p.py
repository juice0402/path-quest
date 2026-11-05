"""11/5 p: a tap on a thing on the field tells what it is (the same paper as a toy's and a hand block's).

しょーくん「盤面の要素も情報が見られるようにしてほしい」
- an obstacle (家・木・池・雪だるま・城のかべ), the mason's wall, the captain's fence: its name, that no block goes there,
  and only what this knight has to deal with it (幽霊の積み木・ハンマーの積み木 bought, おかたづけ set)
- poison, a marble, coins lying on the field: what passing over them does (and おかたづけ / じしゃく when set)
- a laid block still carrying gear, gold, candy, or a special block: the same paper as in the hand (+ what lies under it)
- the tapped panel gets the same white frame as a toy's; a second tap or a block put down closes it
- a block in hand still goes down as before: an obstacle the chosen block fits (ghost) takes it, and an open panel in
  front takes the block (or shakes) even with a marble or poison on it
Applied once (like the other tweak_* files). Check: tools/test/board_paper.py [out.png]
"""
import pathlib, sys

P = pathlib.Path(__file__).resolve().parents[2] / 'games/path-quest/index.html'
s = P.read_text(encoding='utf-8')


def sub(old, new, n=1):
    global s
    c = s.count(old)
    if c != n:
        sys.exit(f'expected {n} of: {old[:80]!r} (found {c})')
    s = s.replace(old, new)


# the hand block's paper: its "what" becomes a function the field shares
sub("""  if(e&&e.k==='foe')h=foePaper(e,foeWhat(e,null));
  else{
    const g=e&&gearOf(e);let ic='',n='',d='';
    if(g){const sl=SLOTS.find(x=>x.k===g.s);ic=ico(g.art);n=`${g.n}<em class="ct">${sl?sl.n:''} ${'★'.repeat(g.r)}</em>`;
      d=owned(g.id)?`もう持っている：のると${ico(SPR.coin)}+${nf(gainOf(dupGold(g)))}`:`のると手に入る${gearDesc(g)?'・'+gearDesc(g):''}`}
    else if(e&&e.k==='coin'){ic=ico(SPR.coin);n='金貨';d=`のると${ico(SPR.coin)}+${nf(e.v)}`}
    else if(e&&e.k==='potion'){ic=ico(SPR.potion);n='キャンディ';d=`のると${ico(SPR.heart)}+${nf(e.v)}`}
    else if(t.sp&&SP_ID[t.sp]){ic=svg(spBlock(t.sp));n=SP_ID[t.sp][2];d=SP_ID[t.sp][4]}
    else{if(hpick>=0)hidePick();return}
    h=`<span class="sb-ic">${ic}</span><div class="sb-t"><b>${n}</b><span class="sp-d">${d}</span></div><div class="sb-b"><button class="sb-x" type="button" data-sb="x">とじる</button></div>`;
  }
""", """  if(e&&e.k==='foe')h=foePaper(e,foeWhat(e,null));
  else{const w=blockWhat(t);if(!w){if(hpick>=0)hidePick();return}h=thingPaper(w.ic,w.n,[w.d])}
""")

sub("function slotPaper(i){",
    """function blockWhat(t){ /* what rides on a block (gear, gold, candy) or what a special block does; a plain one: null */
  const e=t&&t.e,g=e&&gearOf(e);
  if(g){const sl=SLOTS.find(x=>x.k===g.s);return {ic:ico(g.art),n:`${g.n}<em class="ct">${sl?sl.n:''} ${'★'.repeat(g.r)}</em>`,
    d:owned(g.id)?`もう持っている：のると${ico(SPR.coin)}+${nf(gainOf(dupGold(g)))}`:`のると手に入る${gearDesc(g)?'・'+gearDesc(g):''}`}}
  if(e&&e.k==='coin')return {ic:ico(SPR.coin),n:'金貨',d:`のると${ico(SPR.coin)}+${nf(e.v)}`};
  if(e&&e.k==='potion')return {ic:ico(SPR.potion),n:'キャンディ',d:`のると${ico(SPR.heart)}+${nf(e.v)}`};
  if(t&&t.sp&&SP_ID[t.sp])return {ic:svg(spBlock(t.sp)),n:SP_ID[t.sp][2],d:SP_ID[t.sp][4]};
  return null;
}
function thingPaper(ic,n,ds){
  return `<span class="sb-ic">${ic}</span><div class="sb-t"><b>${n}</b>${ds.filter(Boolean).map(d=>`<span class="sp-d">${d}</span>`).join('')}</div><div class="sb-b"><button class="sb-x" type="button" data-sb="x">とじる</button></div>`;
}
/* 11/5: the things on the field. only what this knight has to deal with them is told */
const OB_N={grass:'家',forest:'木',lake:'池',snow:'雪だるま',castle:'城のかべ'};
const setSk=id=>!!(run&&run.sk&&run.sk.some(x=>x&&x.id===id));
function floorWhat(c){ /* poison, a marble, coins lying on a panel */
  const a=[];
  if(c.psn)a.push({ic:svg(SPR.psn),n:'毒の水たまり',d:`通ると毒：3歩のあいだ ${ico(SPR.heart)}-${nf(c.psn)}ずつ`,x:setSk('clear')?'おかたづけで消せる':''});
  if(c.gem)a.push({ic:ico(SPR.gem),n:'ビー玉',d:`通ると${ico(SPR.coin)}+${nf(gainOf(c.gem))}`,x:setSk('magnet')?'じしゃくで集められる':''});
  if(c.coin)a.push({ic:ico(SPR.coin),n:'金貨',d:`通ると${ico(SPR.coin)}+${nf(gainOf(c.coin))}`,x:setSk('magnet')?'じしゃくで集められる':''});
  return a;
}
function boardPaper(i){ /* the paper for a tap on panel i (a toy has its own), or '' */
  const c=cellAt(i);if(!c||c.start)return '';
  const fl=floorWhat(c),more=fl.map(x=>x.n+'：'+x.d);
  if(c.rock===2){const row=run.rows[rowOf(i)],g=row&&row.find(x=>x.tile&&x.tile.anc),who=g&&g.tile.kg?'王さま':'大将';
    return thingPaper(svg(SPR.fence),`${who}の柵`,['こわせない',`通れるのは ${who}のマスだけ`])}
  if(c.rock){const a=areaOf(rowOf(i)).k,fix=[];
    if((meta.up.sg|0)>0)fix.push('幽霊なら置ける');
    if((meta.up.sh|0)>0)fix.push('ハンマーでこわせる');
    if(setSk('clear'))fix.push('おかたづけでどかせる');
    return c.rock===3?thingPaper(svg(SPR.brick),'かべ職人のかべ',['ここには積み木を置けない',fix.join('・')])
      :thingPaper(svg(SPR.ob[a]||SPR.ob.grass),OB_N[a]||'障害物',['ここには積み木を置けない',fix.join('・')])}
  if(c.tile){const w=blockWhat(c.tile);
    if(w)return thingPaper(w.ic,w.n,[w.d,...more]);
    if(!fl.length)return '';}
  if(!fl.length)return '';
  const f=fl[0];return thingPaper(f.ic,f.n,[f.d,...more.slice(1),f.x]);
}
function showThing(i,h){
  hidePick();fpick=i;fsel.add(i);const c0=elOf(i);if(c0)c0.classList.add('fsel');
  const el=$('skbar');el.innerHTML=h;el.hidden=false;
}
function slotPaper(i){""")

# the field tap: a thing's paper, unless the chosen block goes down there
sub("""  if(fpick>=0)hidePick();
  if(sel<0){if(F.has(i))hop();return}
  place(i,sel);""",
    """  if(!e){const c=cellAt(i),h=boardPaper(i); /* 11/5: a thing on the field: its paper (again: closed) */
    if(h&&!(sel>=0&&(fits(run.hand[sel],i,F)||(c&&!c.rock&&!c.tile&&F.has(i))))){if(fpick>=0&&fsel.has(i))return hidePick();return showThing(i,h)}}
  if(fpick>=0)hidePick();
  if(sel<0){if(F.has(i))hop();return}
  place(i,sel);""")

P.write_text(s, encoding='utf-8')
print('ok')
