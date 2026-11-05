# 11/4 リザルト画面の直し（tweak_1104p.py のあとに1回だけ）
#  - ネタバレにしない：「つぎの大将までの道」と「兵隊長まで あと○段」は、その大将を盤面で一度見てから出す
#    （盤面を描くたびに、つぎの大将のマスが画面に入ったかを見て meta.seen に覚える。前に通りこした大将も見たことにする）
#  - 倒れた騎士が木の札・額にめりこまないように：札の上にのせて、札より手前に描く（背の低いスマホの配置も）
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)

# the road shows only a captain the knight has already seen
rep("""  $('o-road').innerHTML=`<div class="rd-pips">${h}</div><b class="rd-boss">${art}</b>`;
  $('o-to').textContent=`${king?'王さま':'兵隊長'}まで あと${z-step}段`;""",
"""  $('o-road').innerHTML=`<div class="rd-pips">${h}</div><b class="rd-boss">${art}</b>`;
  $('o-to').textContent=`${king?'王さま':'兵隊長'}まで あと${z-step}段`;
  const met=(meta.seen|0)>=z||far0>=z;$('o-road').hidden=$('o-to').hidden=!met; // no spoilers: not before he has been seen on the field""")
rep("""  if(best)ovAt(1450,confetti,1); // the stamp has come down
}
""", """  if(best)ovAt(1450,confetti,1); // the stamp has come down
}
FXH.add('render',()=>{ // remember the next captain once his square is on the screen (the result screen may then name him)
  if(!run)return;let g=stepOf(run.top)+1;while(!isGate(g))g++;
  if((meta.seen|0)>=g)return;
  const row=run.rows[g+1],k=row?row.findIndex(c=>c.tile&&c.tile.anc):-1;if(k<0)return;
  const el=elOf(idOf(g+1,k));if(!el)return;
  const a=el.getBoundingClientRect(),v=view.getBoundingClientRect(),top=Math.max(v.top,document.querySelector('.hud').getBoundingClientRect().bottom);
  if(a.bottom>top+a.height*.4&&a.top<v.bottom){meta.seen=g;saveMeta()}
});
""")
# the knight lies on the plank, in front of it
rep(".ov-hero.home{top:-101px}", ".ov-hero.home{top:-101px}\n.ov-hero{z-index:1}\n.ov-road[hidden],.ov-to[hidden]{display:none}\n.ov-to[hidden]+.ov-led{margin-top:22px}")
rep("  .ov-hero{top:-84px;width:90px;height:68px;margin-left:-45px}.ov-hero.home{top:-81px}",
    "  .ov-hero{top:-92px;width:90px;height:68px;margin-left:-45px}.ov-hero.home{top:-88px}")
open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
