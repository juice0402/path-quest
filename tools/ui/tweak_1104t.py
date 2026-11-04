# 11/4 デバッグ その2：装備・おもちゃ・お店・セーブ・リザルト（tweak_1104s.py のあとに1回だけ）
#  1 リザルトの「新記録」のはんこが ふつうに遊ぶと出なかった（のぼるたびに meta.far が先にふえていた）→ のぼる前の記録 run.best とくらべる
#  2 大将を見たこと（meta.seen）が ページを開きなおすと消えていた → 読みこみのときに残す
#  3 歩いているとちゅうに新しい装備を拾って すぐページを開きなおすと、持っている物あつかいで金貨になっていた → 拾ったらすぐ冒険も保存
#  4 杖（手持ちの敵に魔法）が 地面に立っている敵と戦ったあとに出なかった
#  5 歩いているとちゅうに開きなおすと 紙ひこうき・ブーメランがもう一度とんだ → この積み木で もうとんだら とばない
#  6 範囲の魔法が 王さまの落とした装備にも「-2」を出していた → 敵だけ
#  7 お店の装備タブの赤い数字が 1つおくれていた → NEW を消してから数える
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)

# 1
rep("  const step=stepOf(run.top),far0=meta.far,best=step>far0&&step>0,", "  const step=stepOf(run.top),far0=run.best|0,best=step>far0&&step>0,") # the record before this climb (reach() moves meta.far as he climbs)
# 2
rep("  meta={bank:meta.bank|0,best:meta.best|0,far:meta.far|0,", "  meta={bank:meta.bank|0,best:meta.best|0,far:meta.far|0,seen:meta.seen|0,")
# 3
rep("    (run.found=run.found||[]).push(g.id);\n    note(`${g.n}を見つけた`,'good');fly(i,g.art,$('quit'));\n  }\n  return true;",
    "    (run.found=run.found||[]).push(g.id);save(); // the climb is saved with it, so a reload does not take it again as one he has\n    note(`${g.n}を見つけた`,'good');fly(i,g.art,$('quit'));\n  }\n  return true;")
# 4
rep("    c.foe=null;updateCell(i);await sleep(STEP);\n  }", "    c.foe=null;updateCell(i);castHand();await sleep(STEP);\n  }")
# 5
rep("  await toysAct();", "  if(run.ta!==run.at){run.ta=run.at;await toysAct()} // once for each block, also when a reload replays the walk")
# 6
rep("      const e=x.foe||(x.tile&&x.tile.gate&&x.tile.e);if(!e)continue;\n      e.hp-=M;",
    "      const e=x.foe||(x.tile&&x.tile.gate&&x.tile.e);if(!e||e.k!=='foe')continue; // not the piece the king left\n      e.hp-=M;")
# 7
rep("""  shopMarks();
  if(shopTab==='gear'&&meta.newg&&meta.newg.includes(shopSel.gear)){meta.newg=meta.newg.filter(x=>x!==shopSel.gear);saveMeta()} // seen: the NEW goes after this look""",
"""  if(shopTab==='gear'&&meta.newg&&meta.newg.includes(shopSel.gear)){meta.newg=meta.newg.filter(x=>x!==shopSel.gear);saveMeta()} // seen: the NEW goes after this look
  shopMarks();""")
open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
