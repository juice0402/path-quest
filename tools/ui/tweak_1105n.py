"""11/5 n: a tap on a hand block tells what rides on it.

しょーくん「パネルをタップしたら、何のパネルなのかわかるようにして欲しいってさ。コートとか、本とか敵がいるけど、そのパネル情報があると良いらしい」
- a tap on a hand block that carries something opens the same paper as a toy's (the bar over the hand):
  a toy: the toy's paper (attack, hp, habit, what a fight costs, gold) — the same as tapping it on the field
  gear: its name, slot and stars, and what it gives (or, already owned, the gold it turns into)
  gold / candy: how much, a special block: its name and what it does
- also when the block cannot go anywhere now (it still shakes); a second tap on it, or putting it down, closes the paper
- plain blocks open nothing (their shape is the whole story)
Applied once (like the other tweak_* files). Check: tools/test/slot_paper.py
"""
import pathlib, re, sys

P = pathlib.Path(__file__).resolve().parents[2] / 'games/path-quest/index.html'
s = P.read_text(encoding='utf-8')


def sub(old, new, n=1):
    global s
    c = s.count(old)
    if c != n:
        sys.exit(f'expected {n} of: {old[:80]!r} (found {c})')
    s = s.replace(old, new)


HP = "const hp=x=>`<i class=\"st-h\"><b class=\"ic\"></b>${x}</i>`"

# the toy's paper, shared by the field and the hand
m = re.search(r"\n  \{const s=c\.foe&&SHOOTERS\[e\.t\],d=dmgFor\(e\);what=(.*)\}\n", s)
if not m:
    sys.exit('the toy paper line moved')
what = m.group(1)
s = s.replace(m.group(0), "\n  what=foeWhat(e,c.foe&&SHOOTERS[e.t]);\n", 1)
m2 = re.search(r"\n  el\.innerHTML=(`<span class=\"sb-ic fd-ic.*`);\n", s)
if not m2:
    sys.exit('the toy paper markup moved')
paper = m2.group(1)
s = s.replace(m2.group(0), "\n  el.innerHTML=foePaper(e,what);\n", 1)
sub("function showFoe(i,e){\n",
    "function foeWhat(e,s){ /* what a toy does, costs and gives: the field (s: it shoots from where it stands) and the hand share it */\n"
    f"  {HP},d=dmgFor(e);\n"
    f"  return {what};\n"
    "}\n"
    "function foePaper(e,what){\n"
    f"  {HP};\n"
    f"  return {paper};\n"
    "}\n"
    "let hpick=-1; /* 11/5: the hand block whose paper is open */\n"
    "function slotPaper(i){ /* 11/5: a tap on a hand block that carries something: what it is */\n"
    "  const t=run.hand[i],e=t&&t.e,el=$('skbar');if(!t||!el)return;\n"
    "  let h='';\n"
    "  if(e&&e.k==='foe')h=foePaper(e,foeWhat(e,null));\n"
    "  else{\n"
    "    const g=e&&gearOf(e);let ic='',n='',d='';\n"
    "    if(g){const sl=SLOTS.find(x=>x.k===g.s);ic=ico(g.art);n=`${g.n}<em class=\"ct\">${sl?sl.n:''} ${'★'.repeat(g.r)}</em>`;\n"
    "      d=owned(g.id)?`もう持っている：のると${ico(SPR.coin)}+${nf(gainOf(dupGold(g)))}`:`のると手に入る${gearDesc(g)?'・'+gearDesc(g):''}`}\n"
    "    else if(e&&e.k==='coin'){ic=ico(SPR.coin);n='金貨';d=`のると${ico(SPR.coin)}+${nf(e.v)}`}\n"
    "    else if(e&&e.k==='potion'){ic=ico(SPR.potion);n='キャンディ';d=`のると${ico(SPR.heart)}+${nf(e.v)}`}\n"
    "    else if(t.sp&&SP_ID[t.sp]){ic=svg(spBlock(t.sp));n=SP_ID[t.sp][2];d=SP_ID[t.sp][4]}\n"
    "    else{if(hpick>=0)hidePick();return}\n"
    "    h=`<span class=\"sb-ic\">${ic}</span><div class=\"sb-t\"><b>${n}</b><span>${d}</span></div><div class=\"sb-b\"><button class=\"sb-x\" type=\"button\" data-sb=\"x\">とじる</button></div>`;\n"
    "  }\n"
    "  hidePick();hpick=i;el.innerHTML=h;el.hidden=false;\n"
    "}\n"
    "function showFoe(i,e){\n")

sub("function hidePick(){pick=-1;",
    "function hidePick(){pick=-1;hpick=-1;")

# the hand tap
sub("  const t=run.hand[i];if(!t)return;\n  if(sel!==i&&!anyFit(t,frontier()))return flashSlot(i);\n  sel=sel===i?-1:i;\n  renderHand();refreshMarks();setPreview(-1);hintFinger(frontier());\n}",
    "  const t=run.hand[i];if(!t)return;\n"
    "  if(sel!==i&&!anyFit(t,frontier())){if(hpick===i)hidePick();else slotPaper(i);return flashSlot(i)} /* 11/5: it cannot go anywhere now, but what is on it still shows */\n"
    "  sel=sel===i?-1:i;\n"
    "  renderHand();refreshMarks();setPreview(-1);hintFinger(frontier());\n"
    "  if(sel===i)slotPaper(i);else if(hpick>=0)hidePick();\n"
    "}")
sub("  if(pick>=0||fpick>=0)hidePick(); // a skill's paper or a toy's paper closes",
    "  if(pick>=0||fpick>=0||hpick>=0)hidePick(); // a skill's paper or a toy's paper closes")
sub("  run.intro=0;run.hand=run.hand.map(()=>makeTile(lv));",
    "  if(hpick>=0)hidePick();run.intro=0;run.hand=run.hand.map(()=>makeTile(lv));")

P.write_text(s, encoding='utf-8')
print('ok')
