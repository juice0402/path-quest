"""11/6 b: lighter redraws. The field and the hand keep the cells that did not change.

しょーくん「ブラウザで遊んでるんだけど重い気がする。特に進んだときとか、敵と戦って賞金をもらう流れとか。体感滑らかに動いていない」
Measured (tools/test/perf_run.py, rtime): every render() threw the whole field away (board.innerHTML, ~450 elements,
with the knight) and the hand, and built them again: ~28ms of main thread on a fast PC (style 8, paint 10, layout,
layers), 3 times for every block (place, walk start, walk end) and after every reward. All the idle animations
(toys, grass, the knight breathing) also started over each time, so they jumped.
Now:
- patchKids(): each child keeps the html it was made from (_h). A MutationObserver marks a child dirty when anything
  changes inside it after that (a class from refreshMarks, a flash, a finger, a toy animation's class ...), so a dirty
  child is built again just like before. Only new or changed children are made (one parse for all of them).
- the field: cells by data-i (rows come and go as the knight climbs), the knight stays where he is (not moved, so his
  breathing goes on), the row ticks only when they change. Anything else in the field is cleared, as before.
- the hand: slots by place.
- a kept child loses its script animations (el.animate) as a new one would; its CSS loops go on.
- the scenery clock (--lfT) is left out when two htmls are compared: it only lines new loops up with the clock.
- the land and the dimension (data-area, data-dim, --dtint on .app) are set only when they change: setting the
  same value made the browser restyle every cell, slot and tick (.app[data-dim="1"] .cell …) on every render.
- no :nth-child on the field (5th dimension colors by a column class cq0…cq5, title letters lgd1…lgd9): with any
  :nth-child rule naming .cell or <i>, each thing put into the field restyled every cell and <i> in it.
- updateCell() keeps its html too. slide(false) and placeHero(…,true) skip the forced reflow when nothing moves.
Applied once (like the other tweak_* files).
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


# the helper, right before renderBoard
sub("function renderBoard(F){\n",
    "/* 11/6: keep the children that did not change (each knows the html it was made from; anything that changes inside it after that marks it dirty) */\n"
    "const KIDS=new Set(),DIRTY=new WeakSet();\n"
    "const kidMark=rs=>{for(const r of rs){let n=r.target;while(n&&n.parentNode&&!KIDS.has(n.parentNode))n=n.parentNode;if(n&&n.parentNode)DIRTY.add(n)}};\n"
    "const KIDMO=new MutationObserver(kidMark);\n"
    "const kidTpl=document.createElement('template');\n"
    "function kidsOf(par){if(!KIDS.has(par)){KIDS.add(par);KIDMO.observe(par,{subtree:true,childList:true,attributes:true,characterData:true})}kidMark(KIDMO.takeRecords())}\n"
    "const kidKey=h=>h.replace(/--lfT:-?[\\d.]+s;?/g,''); /* the scenery clock (--lfT) only lines new loops up with the old ones: a kept cell's loops already run on that clock */\n"
    "const kidOk=(el,h)=>!!el&&el._h===kidKey(h)&&!DIRTY.has(el);\n"
    "const NT=document.createElement('i'),normT=t=>(NT.style.transform=t,NT.style.transform); /* a transform as the browser keeps it */\n"
    "function kidsMake(list){ /* the html of the children to make: one parse for all */\n"
    "  if(!list.length)return [];kidTpl.innerHTML=list.join('');const out=[...kidTpl.content.children];out.forEach((el,k)=>{el._h=kidKey(list[k])});return out;\n"
    "}\n"
    "function kidsCalm(par,keep){ /* a kept child loses the script animations it had, as a new one would (its CSS loops go on) */\n"
    "  const CA=window.CSSAnimation,CT=window.CSSTransition;\n"
    "  for(const a of par.getAnimations({subtree:true})){if((CA&&a instanceof CA)||(CT&&a instanceof CT))continue;let t=a.effect&&a.effect.target;while(t&&t.parentNode!==par)t=t.parentNode;if(t&&keep.has(t))a.cancel()}\n"
    "}\n"
    "function kidsPlace(par,els,ref){ /* put els in order from ref on; the ones already in place are not moved */\n"
    "  for(const el of els){if(el===ref){ref=ref.nextSibling;continue}par.insertBefore(el,ref)}\n"
    "}\n"
    "function renderBoard(F){\n")

old_body = """  let h='';for(let rr=hi;rr>=lo;rr--)for(let c=0;c<W;c++)h+=cellHTML(idOf(rr,c),F);
  board.innerHTML=h;board.appendChild(hero);justPlaced=-1;board.classList.toggle('holding',sel>=0);
  let rl='';
  for(let rr=hi;rr>=Math.max(lo,2);rr--){
    const s=stepOf(rr),y=4+(hi-rr)*pitch+cell,big=s%5===0;
    rl+=`<i class="tick${big?' big':''}" style="top:${y}px"></i>`+(big?`<b class="mark" style="top:${y-14}px">${s}</b>`:'');
  }
  const br=(run.best|0)+1;
  if(run.best>0&&br>=lo&&br<=hi)rl+=`<i class="best" style="top:${4+(hi-br)*pitch+cell+1}px">${FLAG}</i>`;
  board.insertAdjacentHTML('beforeend',rl);
"""
new_body = """  let rl='';
  for(let rr=hi;rr>=Math.max(lo,2);rr--){
    const s=stepOf(rr),y=4+(hi-rr)*pitch+cell,big=s%5===0;
    rl+=`<i class="tick${big?' big':''}" style="top:${y}px"></i>`+(big?`<b class="mark" style="top:${y-14}px">${s}</b>`:'');
  }
  const br=(run.best|0)+1;
  if(run.best>0&&br>=lo&&br<=hi)rl+=`<i class="best" style="top:${4+(hi-br)*pitch+cell+1}px">${FLAG}</i>`;
  /* 11/6: only the cells that changed are made again; the knight is not moved; the ticks only when they change */
  kidsOf(board);
  const ids=[],hs=[];for(let rr=hi;rr>=lo;rr--)for(let c=0;c<W;c++){const i=idOf(rr,c);ids.push(i);hs.push(cellHTML(i,F))}
  const have=new Map();for(const el of board.children)if(el.classList.contains('cell')&&el.dataset.i!=null&&!have.has(+el.dataset.i))have.set(+el.dataset.i,el);
  const keep=new Set(),need=[];
  const els=ids.map((i,k)=>{const el=have.get(i);if(kidOk(el,hs[k])){keep.add(el);return el}need.push(k);return null});
  const tk=rl===board._rl&&board._tk&&board._tk.every(x=>x.parentNode===board&&!DIRTY.has(x))?board._tk:null;
  if(need.length>ids.length*.6){ /* most of it is new (a new climb, a jump): build it all at once as before */
    board.innerHTML=hs.join('');[...board.children].forEach((el,k)=>{el._h=kidKey(hs[k])});board.appendChild(hero);
    board.insertAdjacentHTML('beforeend',rl);
  }else{
    const made=kidsMake(need.map(k=>hs[k]));need.forEach((k,j)=>{els[k]=made[j]});
    kidsCalm(board,keep);
    for(const el of [...board.children])if(!keep.has(el)&&el!==hero&&!(tk&&tk.includes(el)))el.remove();
    kidsPlace(board,els,board.firstChild);
    if(hero.parentNode!==board)board.appendChild(hero); /* he stays where he is: his breathing goes on */
    if(!tk)board.insertAdjacentHTML('beforeend',rl);
  }
  board._rl=rl;board._tk=[];for(let n=hero.nextElementSibling;n;n=n.nextElementSibling)board._tk.push(n);
  KIDMO.takeRecords(); /* our own changes: not dirty */
  justPlaced=-1;board.classList.toggle('holding',sel>=0);
"""
sub(old_body, new_body)

# slide(false): no forced reflow when the field does not move
sub("""  if(smooth&&!REDUCED){board.style.transform=`translateY(${y}px)`;return}
  board.style.transition='none';board.style.transform=`translateY(${y}px)`;void board.offsetWidth;board.style.transition='';""",
    """  if(smooth&&!REDUCED){board.style.transform=`translateY(${y}px)`;return}
  if(board.style.transform===normT(`translateY(${y}px)`))return; /* 11/6: already there (a slide that is still going finishes softly) */
  board.style.transition='none';board.style.transform=`translateY(${y}px)`;void board.offsetWidth;board.style.transition='';""")

# placeHero(…,true): no forced reflow when he is already there
sub("""  if(instant)hero.style.transition='none';
  hero.style.width=el.offsetWidth+'px';hero.style.height=el.offsetHeight+'px';
  hero.style.transform=`translate(${el.offsetLeft}px,${el.offsetTop}px)`;""",
    """  const w=el.offsetWidth+'px',h=el.offsetHeight+'px',t=`translate(${el.offsetLeft}px,${el.offsetTop}px)`;
  if(instant&&hero.style.width===w&&hero.style.height===h&&hero.style.transform===normT(t))return; /* 11/6: already there */
  if(instant)hero.style.transition='none';
  hero.style.width=w;hero.style.height=h;
  hero.style.transform=t;""")

# updateCell keeps its html
sub("function updateCell(i){const el=elOf(i);if(el){el.outerHTML=cellHTML(i,null);FXH.emit('update',{i})}}",
    "function updateCell(i){const el=elOf(i);if(el){const h=cellHTML(i,null);el.outerHTML=h;const n=elOf(i);if(n)n._h=kidKey(h);FXH.emit('update',{i})}}")

# the hand: slots by place
old_hand_head = "handEl.innerHTML=run.hand.map((t,i)=>t?"
sub(old_hand_head, "const hh=run.hand.map((t,i)=>t?")
sub("""`<div class="slot none" data-i="${i}"></div>`).join('')+'<div class="slot lock" aria-hidden="true"></div>'.repeat(Math.max(0,6-run.hand.length));""",
    """`<div class="slot none" data-i="${i}"></div>`);for(let k=run.hand.length;k<6;k++)hh.push('<div class="slot lock" aria-hidden="true"></div>');
  /* 11/6: only the slots that changed are made again */
  kidsOf(handEl);const old=[...handEl.children],need=[],els=hh.map((h,k)=>kidOk(old[k],h)?old[k]:(need.push(k),null));
  if(need.length===hh.length){handEl.innerHTML=hh.join('');[...handEl.children].forEach((el,k)=>{el._h=kidKey(hh[k])})}
  else{const made=kidsMake(need.map(k=>hh[k]));need.forEach((k,j)=>{els[k]=made[j]});const ks=new Set(els);kidsCalm(handEl,ks);for(const el of old)if(!ks.has(el))el.remove();kidsPlace(handEl,els,handEl.firstChild)}
  KIDMO.takeRecords();""")

# the land and the dimension on the app: set only when they change (setting the same value still makes the browser
# look again at every cell, slot and tick: .app[data-dim="1"] .cell …)
sub("  app.dataset.area=areaOf(rowOf(run.at)).k;weather();",
    "  {const a=areaOf(rowOf(run.at)).k;if(app.dataset.area!==a)app.dataset.area=a}weather(); /* 11/6: only when it changes */")
sub("const r=rowOf(run.at),t=tintOf(r);app.style.setProperty('--dtint',t?t.slice(t.indexOf(':')+1):'#0000');app.dataset.dim=Math.min(5,dimOf(r));",
    "const r=rowOf(run.at),t=tintOf(r),dt=t?t.slice(t.indexOf(':')+1):'#0000',dm=String(Math.min(5,dimOf(r)));if(app._dt!==dt){app._dt=dt;app.style.setProperty('--dtint',dt)}if(app.dataset.dim!==dm)app.dataset.dim=dm; /* 11/6: only when they change */")

# no :nth-child on the field: putting anything into the field made the browser restyle every cell and every <i> in it
# (its "nth" check covers every class and tag that any :nth-child rule names). The 5th dimension's rainbow cells now use a
# column class (cq0…cq5), and the title letters a class each (lgd1…lgd9) — same colors, same delays, same weight of rule.
for k, n in enumerate(['6n+1', '6n+2', '6n+3', '6n+4', '6n+5', '6n']):
    sub(f'.app[data-dim="5"] .cell:nth-child({n}){{', f'.app[data-dim="5"] .cell.cq{k}{{')
sub("  const tn=tintOf(rowOf(i));if(tn)tab=", "  cls+=' cq'+colOf(i); /* 11/6: the column, for the 5th dimension's colors (no :nth-child) */\n  const tn=tintOf(rowOf(i));if(tn)tab=")
for k in range(1, 5):
    sub(f'#s-title .logo span:first-child i:nth-child({k}){{', f'#s-title .logo span i.lgd{k}.lgd{k}{{')
for k in range(1, 6):
    sub(f'#s-title .logo span+span i:nth-child({k}){{', f'#s-title .logo span i.lgd{k+4}.lgd{k+4}{{')
sub('<span><i class="c0">P</i><i class="c1">A</i><i class="c2">T</i><i class="c3">H</i></span><span><i class="c4">Q</i><i class="c0">U</i><i class="c1">E</i><i class="c2">S</i><i class="c3">T</i></span>',
    '<span><i class="c0 lgd1">P</i><i class="c1 lgd2">A</i><i class="c2 lgd3">T</i><i class="c3 lgd4">H</i></span><span><i class="c4 lgd5">Q</i><i class="c0 lgd6">U</i><i class="c1 lgd7">E</i><i class="c2 lgd8">S</i><i class="c3 lgd9">T</i></span>')

P.write_text(s, encoding='utf-8')
print('ok')
