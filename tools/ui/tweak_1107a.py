"""11/7 a: スキルは覚えたら覚えたまま（お店の「もどす」はスキルには出さない）。

しょーくん「一度購入したスキルに対して戻すをおすと、未購入にもどって返金されるんだけど、
購入状態の解除と返金はいらないんじゃないかな」

The shop paper of a skill had もどす next to 覚える / セットする: it undid a skill bought in this visit (back to not owned, the
coins back, taken off its slot). Now a skill paper has no もどす, and the undo itself does nothing for a skill (the button is
gone, and shopAct also stops it, like the other shop guards). 強化 and 積み木の箱 keep their もどす as before.
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


sub("else if(!has)foot=`${undo('sk',k.id)}<span class=\"note\"></span>",
    "else if(!has)foot=`<span class=\"note\"></span>")
sub("else foot=`${undo('sk',k.id)}<span class=\"note\">${run?'つぎの冒険から':''}</span>",
    "else foot=`<span class=\"note\">${run?'つぎの冒険から':''}</span>")
sub("  if(act==='undo'){\n    const t=shopTab==='skill'?'sk':'up',j=bought(t,sel);if(j<0)return;",
    "  if(act==='undo'){ /* 11/7: a skill stays learned once bought (no もどす for skills) */\n"
    "    if(shopTab==='skill')return;const t='up',j=bought(t,sel);if(j<0)return;")

P.write_text(s, encoding='utf-8')
print('ok')
