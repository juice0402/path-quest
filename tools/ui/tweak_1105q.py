"""11/5 q: the lesson for the first climbs: 2 steps (not 3), the lesson block on the left, and a finger that never walks into a dead end.

しょーくん「最初の3段まで、指のガイド通りに置いて行ったら、即ゲームオーバーになった」「2段まででいいんじゃないのかな」
「最初の直線は左端のパネル固定にしたほうが、なんかチュートリアルっぽい」
- the lesson (the straight block that only goes up, the finger, the chevrons) lasts until the record reaches 2 steps (was 3)
- the lesson block is the leftmost one in hand (was the rightmost); a cross from the deck upgrade moves to the rightmost
- the cell above the lesson cell is cleared too, so the lesson block never leads into a house
- the finger chose the first block that fitted and the first place it fitted, so following it could close the way
  (2 of 10 first climbs ended 「行き止まり」). Now it scores every block × place: the ways left open after it
  (up counts most, a little for the room beyond), a block with a toy or a special block a bit lower.
  When every place that fits would end the way (or nothing fits) and a reroll is left, the finger points at the die
  (the drawer opens by itself, as at a dead end)
Applied once (like the other tweak_* files). Check: tools/test/intro_check.py [out.png]・tools/test/shot_upcue.py
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


sub("run.intro=meta.far<3?1:0; /* 11/5: the first climbs: one straight block, and it can only go up */",
    "run.intro=meta.far<2?1:0; /* 11/5: the first climbs: one straight block, and it can only go up (q: until 2 steps) */")
sub("if(run.intro){const up=cellAt(idOf(2,2));if(up){up.rock=0;up.foe=null}run.hand[run.hand.length-1]={m:5,e:null,c:rnd(BLOCKS.length),intro:1}}",
    "if(run.intro){for(const r of [2,3]){const up=cellAt(idOf(r,2));if(up){up.rock=0;up.foe=null}} /* q: the cell beyond is open too, so the lesson block never leads into a house */\n"
    "    const a=run.hand[0];run.hand[0]={m:5,e:null,c:rnd(BLOCKS.length),intro:1};if(a&&a.m===15)run.hand[run.hand.length-1]=a} /* q: the lesson block is the leftmost one */")

old_finger = s[s.index("function hintFinger(F){"):s.index("function upCue(){")]
sub(old_finger, """function hintFinger(F){ /* the first climbs (until 2 steps): a finger on the block and the place that keep the way open, up first; on the die when every place would end the way */
  document.querySelectorAll('.finger,.upcue').forEach(x=>x.remove());
  if(meta.far>=2||!run||run.phase!=='build'||busy||aim)return;
  upCue();
  const spots=[...F.keys(),...(F.rock?F.rock.keys():[])];
  const bestFor=t=>{let b=null;if(t)for(const j of spots){const v=hintScore(t,j,F);if(v>-9&&(!b||v>b.v))b={j,v}}return b};
  let best=null;run.hand.forEach((t,k)=>{const b=bestFor(t);if(b&&(!best||b.v>best.v))best={k,j:b.j,v:b.v}});
  let el=null;
  if((!best||best.v<0)&&run.rolls>0){el=rollBtn;if(!drawerOpen)setDrawer(true,true);clearTimeout(drawerTimer)}
  else if(sel<0){if(best)el=handEl.children[best.k]}
  else{const b=bestFor(run.hand[sel]);el=b&&(b.v>=0||!best||best.v<0)?elOf(b.j):best?handEl.children[best.k]:null}
  if(el)el.insertAdjacentHTML('beforeend','<span class="finger" aria-hidden="true">👆</span>');
}
function hintScore(t,j,F){ /* 11/5 q: how good a lesson move is: -9 does not fit, -1 the way ends there, else the ways left open (up counts most) */
  if(!fits(t,j,F))return -9;
  const back=F.has(j)?F.get(j):(F.rock&&F.rock.get(j))||0,m=t.m&~DOWN&~back,free=c=>!!c&&!c.rock&&!c.tile&&!c.start;
  let s=0;
  for(const b of BITS){
    if(!(m&b))continue;const n=nbr(j,b),c=n>=0&&cellAt(n);if(!free(c))continue;
    s+=(b===1?4:1)-(c.foe?.5:0);
    for(const d of BITS){if(d===DOWN||d===OPP[b])continue;const o=nbr(n,d);if(o>=0&&free(cellAt(o)))s+=.3}
  }
  if(!s)return -1;
  if(t.e&&t.e.k==='foe')s-=2;
  if(t.sp)s-=1;
  return Math.max(.1,s);
}
""")

P.write_text(s, encoding='utf-8')
print('ok')
