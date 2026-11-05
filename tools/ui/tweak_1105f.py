"""11/5 f: in the shop, the ones that open by step go after the ones open from the start, the biggest step first.

しょーくん「段でアンロックされるものはしっかりソートして降順に並べ替えて欲しい」
- skill book and each section of the toy box: open-from-the-start keep their order, then 50 → 40 → 20 → 10
- the order is by the step itself, so a row does not move when it opens
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


sub("const lockAt=(t,k)=>LOCK[t][k]||0;\n",
    "const lockAt=(t,k)=>LOCK[t][k]||0;\n"
    "const byLock=(t,key)=>(a,b)=>(lockAt(t,key(a))>0)-(lockAt(t,key(b))>0)||lockAt(t,key(b))-lockAt(t,key(a)); /* open from the start first, then the biggest step first */\n")

sub("h+='<div class=\"book\">'+SKILLS.map(k=>{",
    "h+='<div class=\"book\">'+[...SKILLS].sort(byLock('sk',k=>k.id)).map(k=>{")

sub("UPS.filter(u=>u.deck&&MIX_OF[u.k]!=null).map(upRow)",
    "UPS.filter(u=>u.deck&&MIX_OF[u.k]!=null).sort(byLock('up',u=>u.k)).map(upRow)")
sub("UPS.filter(u=>u.deck&&!u.sp&&MIX_OF[u.k]==null).map(upRow)",
    "UPS.filter(u=>u.deck&&!u.sp&&MIX_OF[u.k]==null).sort(byLock('up',u=>u.k)).map(upRow)")
sub("UPS.filter(u=>u.sp).map(upRow)",
    "UPS.filter(u=>u.sp).sort(byLock('up',u=>u.k)).map(upRow)")

P.write_text(s, encoding='utf-8')
print('ok')
