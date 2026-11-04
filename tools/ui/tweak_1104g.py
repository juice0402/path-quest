# 11/4 その7：tweak_1104f.py のあとの index.html に1回だけ当てる
#  道に立っている敵と大将の下に、攻撃（剣）とHP（ハート）を並べて出す。手持ちの積み木の下は今のまま（減るHP）
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()

def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80]); s = s.replace(a, b)

rep("<span class=\"badge b-life\">♥${nf(c.foe.hp)}</span>", "${foeTags(c.foe)}")
rep("  if(e.k==='foe'){const d=dmgFor(e);return `<span class=\"badge ${d?'b-foe':'b-zero'}\">-${nf(d)}</span>`}",
    "  if(e.k==='foe')return foeTags(e);")
rep("function badge(e){", """function foeTags(e){ // a toy on the field: its attack and its life, side by side under it (11/4)
  const a=nf(e.atk),h=nf(e.hp);
  return `<span class="badge b-st${(a+h).length>5?' sm':''}"><i class="st-a">${ico(SPR.sword)}${a}</i><i class="st-h">${ico(SPR.heart)}${h}</i></span>`;
}
function badge(e){""")
rep('bb-tag" style="left:${(w-g.offsetWidth)/2}px;bottom:0;width:${g.offsetWidth}px;height:${g.offsetHeight}px"',
    'bb-tag" style="left:0;bottom:0;width:${w}px;height:${g.offsetHeight}px"')
CSS = '''/* enemies on the field: attack and life under each one */
.badge.b-st{left:50%;right:auto;bottom:2px;translate:-50% 0;display:flex;align-items:center;gap:5px;padding:1px 5px;white-space:nowrap;color:var(--ink)}
.b-st i{display:inline-flex;align-items:center;gap:1px;font-style:normal}
.b-st svg{position:static!important;inset:auto;flex:none;width:11px;height:11px;display:block;margin:0;transform:none}
.b-st .st-a{color:#6b4a3a}.b-st .st-h{color:var(--foe)}
.badge.b-st.sm{gap:3px;padding:1px 3px;font-size:9.5px;letter-spacing:-.02em}
.b-st.sm svg{width:9px;height:9px}
.bboss .badge.b-st{bottom:4px;gap:8px;padding:2px 8px;font-size:14px}
.bboss .b-st svg{width:14px;height:14px}
'''
rep('/* ===== end of 11/4 ===== */', CSS + '/* ===== end of 11/4 ===== */')
open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
