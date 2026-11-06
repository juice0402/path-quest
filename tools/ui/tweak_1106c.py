"""11/6 c: lighter frames on phones (Android). Each part measured with tools/test/frame_cost.py and bench.py (CPU 4x slower, Android
screen): the main-thread time of one frame while the game is doing something (walking, fighting).

しょーくん「今はAndroidのスマホで遊んでるの。まだ最適化や軽量化できることが残ってたら徹底して行って欲しい。重いのはストレスだからね！」

1. the flying critters: their box has the class "fly", which is also the class of the flying coins (.fly), so they got the
   coin's drop-shadow. A filter around a moving layer makes the browser lay out all its layers again on every frame
   (about 4ms of 14 on a slow phone). The same shadow now sits on the critter's picture itself (.lf-c>b), which moves with
   it; nothing else changes (the coin's margin stays too, so they fly where they flew).
2. the loops out of sight wait: the scenery and toy loops in the rows above the screen (the field keeps a few rows up there
   for the climb) and under the tray are paused, and come back on exactly the same beat (their start time is kept) one
   row before they slide into sight. Every frame the browser had to update all of them (about 70).
3. the knight's "ouch": it restarted its animation by taking the class off, making the browser lay out the whole page right
   there, and putting it back. Now a second, identical keyframes (hurt2) is switched in, which restarts it without that.
   The rule has the same weight as before (:where), so the same rules win over it as before.
4. the top bar and the tray (hearts, sword, shield, coins, the die, the skill buttons) were built again on every hit even
   when nothing in them changed. Now each one is built again only when its html changes (or something changed inside it,
   seen by the same watcher as the field).
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


# 1. the flying critter's shadow: on the picture, not around the moving layer
sub(".lf-r.fly{z-index:4}",
    ".lf-r.fly{z-index:4}.lf-r.fly{filter:none}.lf-r.fly .lf-c>b{filter:drop-shadow(0 2px 2px rgba(74,53,65,.25))}"
    ".lf-r.fly .lf-gold>b{filter:sepia(.9) saturate(2.4) hue-rotate(-8deg) brightness(1.1) drop-shadow(0 2px 2px rgba(74,53,65,.25))}")

# 2. the loops out of sight wait
sub("function render(){const F=frontier();renderStats();renderBoard(F);renderHand(F);markStuck(F);hintFinger(F)}",
    "function render(){const F=frontier();renderStats();renderBoard(F);renderHand(F);markStuck(F);hintFinger(F);offPause()}\n"
    "/* 11/6: the loops out of sight wait (the rows kept above the screen, under the tray) and come back on the same beat, a row before they show */\n"
    "const OFFP=new Map();\n"
    "function offPause(){\n"
    "  const CA=window.CSSAnimation;if(REDUCED||!run||!CA||!board.firstElementChild||!win.pitch)return;\n"
    "  const y=(rowOf(run.at)-1-win.lo)*win.pitch,pad=win.pitch,top=-board.offsetTop-y-pad,bot=top+view.clientHeight+2*pad; /* in the field's own pixels, where it is going */\n"
    "  for(const [a] of OFFP){const t=a.effect&&a.effect.target;if(!t||!t.isConnected)OFFP.delete(a)}\n"
    "  const b0=board.getBoundingClientRect().top;\n"
    "  for(const a of board.getAnimations({subtree:true})){\n"
    "    if(!(a instanceof CA)||a.effect.getTiming().iterations!==Infinity)continue;\n"
    "    const r=a.effect.target.getBoundingClientRect(),out=r.bottom-b0<top||r.top-b0>bot;\n"
    "    if(out){if(a.playState==='running'&&!OFFP.has(a)){OFFP.set(a,a.startTime);a.pause()}}\n"
    "    else if(OFFP.has(a)){const s=OFFP.get(a);OFFP.delete(a);a.play();if(s!=null)a.startTime=s}\n"
    "  }\n"
    "}")
sub("  run.at=i;placeHero(i);if(up)slide(true);",
    "  run.at=i;placeHero(i);if(up){offPause();slide(true)} /* 11/6: the row coming into sight moves again first */")

# 3. the knight's "ouch" without a forced layout
sub(".hero.hurt svg{animation:hurt .34s ease-out}",
    ".hero.hurt svg{animation:hurt .34s ease-out}.hero.hurt:where(.hurt2) svg{animation-name:hurt2}")
import re as _re
_m = _re.search(r"@keyframes hurt\{(.*?\})\}", s)
if not _m: sys.exit('no @keyframes hurt')
_kf = _m.group(0)
sub(_kf, _kf + _kf.replace('@keyframes hurt{', '@keyframes hurt2{', 1))
sub("function hurt(){hero.classList.remove('hurt');void hero.offsetWidth;hero.classList.add('hurt')}",
    "function hurt(){if(hero.classList.contains('hurt'))hero.classList.toggle('hurt2');else hero.classList.add('hurt')} /* 11/6: hurt2 (same keyframes) restarts it without a forced layout */")

# 4. the top bar and the tray: built again only when they change
sub("function kidsOf(par){",
    "function setH(el,h){if(!el)return;kidsOf(el.parentNode);if(el._sh===h&&!DIRTY.has(el))return;el.innerHTML=h;el._sh=h;DIRTY.delete(el);KIDMO.takeRecords()} /* 11/6: only when it changes */\n"
    "function kidsOf(par){")
sub("$('hpblocks').innerHTML=h;", "setH($('hpblocks'),h);")
sub("$('i-atk').innerHTML=ico(SPR.sword)+`<b>${nf(atkNow())}</b>`;", "setH($('i-atk'),ico(SPR.sword)+`<b>${nf(atkNow())}</b>`);")
sub("$('i-def').innerHTML=ico(SPR.shield)+`<b>${nf(run.def)}</b>`;", "setH($('i-def'),ico(SPR.shield)+`<b>${nf(run.def)}</b>`);")
sub("$('i-gold').innerHTML=ico(SPR.coin)+`<b>${nf(run.gold)}</b>`;", "setH($('i-gold'),ico(SPR.coin)+`<b>${nf(run.gold)}</b>`);")
sub("""  $('rollicon').innerHTML=svg('<rect x="7" y="12" width="86" height="82" rx="13" fill="#e9d6c4"/>""",
    """  setH($('rollicon'),svg('<rect x="7" y="12" width="86" height="82" rx="13" fill="#e9d6c4"/>""")
sub("""<circle cx="${x-2.4}" cy="${y-5.4}" r="2.6" fill="#ff9db4"/>`).join(''));""",
    """<circle cx="${x-2.4}" cy="${y-5.4}" r="2.6" fill="#ff9db4"/>`).join('')));""")
sub("""    b.innerHTML=`<span class="sk-ic">""", """    setH(b,`<span class="sk-ic">""")
sub("""<b>${s.cd}</b></i>`:''}</span><span class="sk-n">${d.n}</span>`;""", """<b>${s.cd}</b></i>`:''}</span><span class="sk-n">${d.n}</span>`);""")

P.write_text(s, encoding='utf-8')
print('ok')
