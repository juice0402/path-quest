"""11/5 k: a first-time player did not see that the knight goes UP.

しょーくん「初見で試プレイしてもらったんだけど、上に進むってことがわからなかったみたい！最初上の矢印を表示するとかした方がいいかなぁ」
- no words (the rule: no how-to-play text): three cream chevrons with a wood outline rise over the knight's head, one after another
- only while the best climb ever is under 3 steps (the same time as the finger hint), only while building; gone during a walk
Applied once (like the other tweak_* files). Check: tools/test/shot_upcue.py
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


sub("function hintFinger(F){ // the very first climb: a finger on a block that fits, then on where it goes\n"
    "  document.querySelectorAll('.finger').forEach(x=>x.remove());\n"
    "  if(meta.far>=3||!run||run.phase!=='build'||busy||aim)return;\n",
    "function hintFinger(F){ // the very first climb: a finger on a block that fits, then on where it goes\n"
    "  document.querySelectorAll('.finger,.upcue').forEach(x=>x.remove());\n"
    "  if(meta.far>=3||!run||run.phase!=='build'||busy||aim)return;\n"
    "  upCue();\n")

sub("function placeHero(i,instant){\n",
    "function upCue(){ /* 11/5: the first climbs: chevrons rise over the knight's head, so the way is UP (no words) */\n"
    "  const h=elOf(run.at);if(!h)return;\n"
    "  const c=document.createElement('div');c.className='upcue';c.setAttribute('aria-hidden','true');\n"
    "  const w=h.offsetWidth,ht=h.offsetHeight;\n"
    "  c.style.cssText=`left:${h.offsetLeft}px;top:${h.offsetTop-ht*1.55}px;width:${w}px;height:${ht*1.5}px`;\n"
    "  const v=y=>{const d=`M14 ${y+15}L30 ${y}L46 ${y+15}`;return `<g class=\"cv\"><path class=\"o\" d=\"${d}\"/><path class=\"i\" d=\"${d}\"/></g>`};\n"
    "  c.innerHTML=`<svg viewBox=\"0 0 60 100\">${v(70)}${v(44)}${v(18)}</svg>`;\n"
    "  board.appendChild(c);\n"
    "}\n"
    "function placeHero(i,instant){\n")

sub("\nconst ICON_UP_F=()=>",
    "\nFXH.add('step',()=>document.querySelectorAll('.upcue').forEach(x=>x.remove())); /* 11/5: the chevrons go once the knight walks */\n"
    "const ICON_UP_F=()=>")

sub(".finger{position:absolute;",
    "/* 11/5: the way is up: three chevrons rise over the knight in turn (the first climbs only) */\n"
    ".upcue{position:absolute;z-index:4;pointer-events:none;display:flex;justify-content:center}\n"
    ".upcue svg{width:64%;height:100%;overflow:visible;filter:drop-shadow(0 2px 0 rgba(58,28,8,.35))}\n"
    ".upcue .cv{opacity:0;animation:cvup 1.5s ease-in-out infinite}\n"
    ".upcue .cv path{fill:none;stroke-linecap:round;stroke-linejoin:round}\n"
    ".upcue .cv .o{stroke:var(--wood-deep);stroke-width:14}\n"
    ".upcue .cv .i{stroke:#fff6e6;stroke-width:8}\n"
    ".upcue .cv:nth-child(2){animation-delay:.25s}\n"
    ".upcue .cv:nth-child(3){animation-delay:.5s}\n"
    "@keyframes cvup{0%{opacity:0;transform:translateY(6px)}35%{opacity:1}70%{opacity:1}100%{opacity:0;transform:translateY(-6px)}}\n"
    "@media (prefers-reduced-motion:reduce){.upcue .cv{animation:none;opacity:1}}\n"
    ".finger{position:absolute;")

P.write_text(s, encoding='utf-8')
print('ok')
