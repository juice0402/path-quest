# 11/4 バランス その2（tweak_1104k.py のあとに1回だけ）：大将の前の段（四角の1つ下の段）は、障害物と立っている敵をなくして広場にする
#   広場に入ったとき、リロールが2回より少なければ2回にする
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)
rep("  {const g=row.findIndex(c=>c.tile&&c.tile.anc);if(g>=0){const n2=g<=2?g+1:g-1;for(const k of [g,n2]){if(prev[k].rock===1||prev[k].rock===3)prev[k].rock=0;prev[k].foe=null}}} // the way into the captain's square",
    "  if(row.some(c=>c.tile&&c.tile.anc))for(const c of prev){if(c.rock===1||c.rock===3)c.rock=0;c.foe=null} // the row in front of the captain's square is an open yard: the way to him is never walled off")
# the yard: stepping into it, the knight has at least 2 rerolls (the way to the captain needs the right turn)
rep("  if(s>0&&s%10===0)run.reward=true;\n  FXH.emit('reach',{r,s});",
    "  if(s>0&&s%10===0)run.reward=true;\n  if(s%SPAN===SPAN-1&&run.rolls<2){note(`広場でリロール+${2-run.rolls}`,'good');run.rolls=2;renderStats()}\n  FXH.emit('reach',{r,s});")
open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
