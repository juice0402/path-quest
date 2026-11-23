"""11/7 b: 能力（強化）も、買ったら買ったまま（もどすを出さない）。

しょーくん「能力も戻せないようにしとこ」（11/7 a のスキルにつづけて）

The 能力 tab's paper had もどす next to 強化する: it took back one level bought in this visit and gave the coins back.
Now the 能力 paper has no もどす, and shopAct stops the undo for it too. Only 積み木の箱 keeps its もどす (not asked).
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


sub("<div class=\"dt-foot\">${undo('up',u.k)}<span class=\"note\"></span>${btn}</div>",
    "<div class=\"dt-foot\">${shopTab==='deck'?undo('up',u.k):''}<span class=\"note\"></span>${btn}</div>")
sub("  if(act==='undo'){ /* 11/7: a skill stays learned once bought (no もどす for skills) */\n"
    "    if(shopTab==='skill')return;",
    "  if(act==='undo'){ /* 11/7: a skill stays learned, and a 能力 level stays, once bought (もどす only for 積み木の箱) */\n"
    "    if(shopTab!=='deck')return;")

P.write_text(s, encoding='utf-8')
print('ok')
