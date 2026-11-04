# 11/4 その8：tweak_1104g.py のあとの index.html に1回だけ当てる
#  敵の攻撃とHPの札：アイコンは Canva の剣とハート（build_ui_1104.py が CSS の絵として入れる）。ここでは札の中身の形だけ変える
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()

def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80]); s = s.replace(a, b)

rep("  const a=nf(e.atk),h=nf(e.hp);\n", "  const a=nf(e.atk),h=nf(e.hp),n=a.length+h.length,cw=win.pitch?win.pitch-GAP:60;\n  const big=e.boss||e.king,one=(cw-3)/(37+7.4*n),two=(cw-3)/(23+7.4*Math.max(a.length,h.length)),stack=!big&&one<.78; // one panel wide at most: long numbers go on two lines
  const k=big?1:Math.min(1,stack?two:one);\n")
rep("  return `<span class=\"badge b-st${(a+h).length>5?' sm':''}\"><i class=\"st-a\">${ico(SPR.sword)}${a}</i><i class=\"st-h\">${ico(SPR.heart)}${h}</i></span>`;",
    "  return `<span class=\"badge b-st${stack?' two':''}\" style=\"--k:${k.toFixed(3)}\" aria-label=\"攻撃${a} HP${h}\"><i class=\"st-a\"><b class=\"ic\"></b>${a}</i><i class=\"st-h\"><b class=\"ic\"></b>${h}</i></span>`;")
# the old look of the tag goes; build_ui_1104.py draws the new one
i = s.index('/* enemies on the field: attack and life under each one */')
j = s.index('.bboss .b-st svg{width:14px;height:14px}\n', i) + len('.bboss .b-st svg{width:14px;height:14px}\n')
s = s[:i] + s[j:]
open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
