"""11/6 a: the locked ones in the shop go from the smallest step to the biggest (10 → 20 → 40 → 50).

しょーくん「スキルとか積み木の箱の未アンロックの順番なんだけど、上から段が少ない順の方が普通じゃない？
今は一番下に10段とかが来てるけど、逆だと思う」
- order in each list: open (from the start first, then the biggest step first) → NEW (biggest step first)
  → locked (smallest step first: the next one to open sits at the top)
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


sub("const byLock=(t,key)=>(a,b)=>{const x=key(a),y=key(b);return lockGrp(t,x)-lockGrp(t,y)||(lockAt(t,x)>0)-(lockAt(t,y)>0)||lockAt(t,y)-lockAt(t,x)}; /* open → NEW → locked; in each, from the start first, then the biggest step first */",
    "const byLock=(t,key)=>(a,b)=>{const x=key(a),y=key(b),g=lockGrp(t,x);return g-lockGrp(t,y)||(lockAt(t,x)>0)-(lockAt(t,y)>0)||(g===2?lockAt(t,x)-lockAt(t,y):lockAt(t,y)-lockAt(t,x))}; /* open → NEW → locked; open and NEW: from the start first, then the biggest step first; locked: the smallest step first (the next to open on top) */")

P.write_text(s, encoding='utf-8')
print('ok')
