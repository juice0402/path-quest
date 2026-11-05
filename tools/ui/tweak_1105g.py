"""11/5 g: the NEW ones sit between what is already open and what is still locked.

しょーくん「Newは未アンロックと既に出てるものの間でいいよ」
- order in each list: open (from the start first, then by step, biggest first) → NEW (biggest step first) → locked (biggest step first)
- which ones count as NEW is taken when the shop opens, so a row does not jump while you look (it joins the open ones next time)
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


sub("const byLock=(t,key)=>(a,b)=>(lockAt(t,key(a))>0)-(lockAt(t,key(b))>0)||lockAt(t,key(b))-lockAt(t,key(a)); /* open from the start first, then the biggest step first */\n",
    "let shopNew=new Set(); /* the NEW ones as the shop opened: the order keeps to it until the shop closes */\n"
    "const lockGrp=(t,k)=>isLocked(t,k)?2:shopNew.has(t+':'+k)?1:0;\n"
    "const byLock=(t,key)=>(a,b)=>{const x=key(a),y=key(b);return lockGrp(t,x)-lockGrp(t,y)||(lockAt(t,x)>0)-(lockAt(t,y)>0)||lockAt(t,y)-lockAt(t,x)}; /* open → NEW → locked; in each, from the start first, then the biggest step first */\n")

sub("function showShop(tab){\n  if(tab)shopTab=tab;visit=[];swap=null;",
    "function showShop(tab){\n  if(tab)shopTab=tab;visit=[];swap=null;shopNew=new Set(meta.newu||[]);")

P.write_text(s, encoding='utf-8')
print('ok')
