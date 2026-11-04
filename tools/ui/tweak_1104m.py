# 11/4 バランス その3（tweak_1104l.py のあとに1回だけ）：自動プレイ tools/test/sim.py で決めた数字を BAL に入れる
#  ねらい：1回目は10〜19段（大将の手前まで）。強化しながら だいたい10回で1つめの大将（20段）、20回で2つめ（40段）をこえる
#  - 大将：強さの関門にする（20段 HP21・攻撃5、40段 HP34・攻撃8）。王さまも少し強く
#  - 金貨：敵からを多く（へいたい 4+1.2×レベル、大将 12+3×レベル）、積み木の金貨とビー玉は少なめ（敵の約3分の1）
#  - 障害物：はじめを少し少なく（13%→11%、いちばん多くて28%）
#  - 強化の値段：すべて1.5倍
#  - かたい盾：大将と王さまには ダメージ0 ではなく半分
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)

rep("""  ob:[.13,.002,.3],gem:.035,gemV:[5,2],stand:[.03,.025,.0002,.12], // obstacles: base, per step, most; gems; standing toys: base, per dimension, per step, most
  ev:{foe:[.16,.012,.3],coin:.13,potion:.07,wpn:.04,shd:.04,chm:.03},coinV:[2,.5],potV:[3,.34], // what rides on a block
  foe:{hp:[2,1],atk:[1,.5],gold:[3,.8]},boss:{hp:[4,1.2],atk:[1,.5],gold:[10,2]},king:{hp:[8,1.6],atk:[1,.5],gold:[30,4]},
  cost:1 // all upgrade prices are multiplied by this""",
"""  ob:[.11,.002,.28],gem:.025,gemV:[5,2],stand:[.03,.025,.0002,.12], // obstacles: base, per step, most; gems; standing toys: base, per dimension, per step, most
  ev:{foe:[.16,.012,.3],coin:.09,potion:.07,wpn:.04,shd:.04,chm:.03},coinV:[2,.4],potV:[3,.34], // what rides on a block
  foe:{hp:[2,1],atk:[1,.5],gold:[4,1.2]}, // the toys give most of the gold: about three times the coins on the blocks
  boss:{hp:[8,4.4],atk:[2,1.1],gold:[12,3]}, // each captain is a wall of strength: about ten climbs of upgrades for each one (tools/test/sim.py)
  king:{hp:[5,2.5],atk:[1,.7],gold:[30,4]},
  cost:1.5 // all upgrade prices are multiplied by this""")
# the hard shield: a captain or the king still lands half
for a in ("  const A=atkNow(),back=FX().guard?0:Math.ceil(Math.max(0,e.atk-run.def)/(FX().half?2:1))",
          "  const back=FX().guard?0:Math.ceil(Math.max(0,e.atk-run.def)/(FX().half?2:1))"):
    rep(a, a.replace("FX().guard?0:Math.ceil(Math.max(0,e.atk-run.def)/(FX().half?2:1))",
                     "FX().guard&&!e.boss?0:Math.ceil(Math.max(0,e.atk-run.def)/((FX().half?2:1)*(FX().guard?2:1)))"))
rep("guard:()=>{run.fx.guard=1;return ()=>note('つぎの戦いはダメージ0','good')},", "guard:()=>{run.fx.guard=1;return ()=>note('つぎの戦いはダメージ0（大将は半分）','good')},")
rep("{id:'guard',n:'かたい盾',d:'つぎの戦い1回は ダメージ0',ct:10,cost:40},", "{id:'guard',n:'かたい盾',d:'つぎの戦い1回は ダメージ0（大将・王さまは半分）',ct:10,cost:40},")
open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
