# 11/4 リザルト：倒れた騎士の影（tweak_1104n.py のあとに1回だけ）
#  倒れたときは、騎士の絵から足もとの影を外して、横になった体の下に平たい影を置く（影が絵といっしょに立ってしまっていた）
#  帰還のときは、立ったままの騎士と影のまま
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)
rep("  $('o-hero').innerHTML=svg(SPR.hero);$('o-hero').classList.toggle('home',why==='quit');",
    "  $('o-hero').innerHTML=why==='quit'?svg(SPR.hero):'<i class=\"ov-sh\" aria-hidden=\"true\"></i>'+svg(SPR.hero.replace(/^<ellipse[^>]*\\/>/,'')); // fallen: his shadow lies flat under him, it does not turn with him\n  $('o-hero').classList.toggle('home',why==='quit');")
rep('/* ===== end of 11/4 ===== */', '''/* the fallen knight on the result: a flat shadow under him */
.ov-hero{position:relative}
.ov-hero .ov-sh{position:absolute;left:15%;right:15%;bottom:6%;height:15%;border-radius:50%;background:rgba(30,14,24,.42);filter:blur(1.5px)}
/* ===== end of 11/4 ===== */''')
open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
