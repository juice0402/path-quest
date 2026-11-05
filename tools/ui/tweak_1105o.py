"""11/5 o: the hand-block paper: the little coin/heart inside the words had no size and grew to fill the paper
(しょーくんの iPad で、金貨の紙のコインが画面いっぱいに). The words line gets its own class and its icons are 16px, like the toy paper's.
Applied once (like the other tweak_* files). Check: tools/test/slot_paper.py out.png (every kind, two widths)
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


sub("<div class=\"sb-t\"><b>${n}</b><span>${d}</span></div>",
    "<div class=\"sb-t\"><b>${n}</b><span class=\"sp-d\">${d}</span></div>")
sub(".fd-g svg{width:16px;height:16px;display:block}",
    ".fd-g svg{width:16px;height:16px;display:block}\n"
    ".sb-t .sp-d svg{display:inline-block;width:16px;height:16px;margin:0 1px;vertical-align:-3px} /* 11/5: the coin and heart inside the words of a hand block's paper */")

P.write_text(s, encoding='utf-8')
print('ok')
