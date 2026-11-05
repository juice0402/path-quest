"""11/5 l: くるっと回す, seen at a glance.

しょーくん「くるっと回すもよくわからなかったらしいから、押したら、どっちにどう回るか、くるーっと回ってどうなるかビジュアル的にわかるように」
- while choosing (after the skill is pressed): every block that would change gets a cream ↻ (right-hand turn) on its corner,
  and its road turns a quarter to the right again and again, so you see what will happen before you tap
- on the tap: the road turns a quarter to the right with a little overshoot, a big ↻ spins over it, sparkles at the end
- only the road turns (the block, a toy riding on it and a special mark stay still); the paper says 右に回す
Applied once (like the other tweak_* files). Check: tools/test/shot_turn.py
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


# the road in the tray is one group, so it can turn on its own (around the top face's centre)
sub("(inTray?roadSVG(t.m,BLOCKS[c][1],4,96,ace):roadSVG(t.m,BLOCKS[c][1],undefined,undefined,ace))",
    "(inTray?`<g class=\"rd\" style=\"transform-origin:50% ${RC}%\">${roadSVG(t.m,BLOCKS[c][1],4,96,ace)}</g>`:roadSVG(t.m,BLOCKS[c][1],undefined,undefined,ace))")

# choosing: the blocks that would change show it
sub("const can=aim&&aim.kind!=='rock'?targets(aim.kind):null;",
    "const can=aim&&aim.kind!=='rock'?targets(aim.kind):null;\n"
    "  const tA=!!(can&&run.sk&&run.sk[aim.k]&&run.sk[aim.k].id==='turn'),tOk=(t,i)=>tA&&can.includes(i)&&rot(t.m)!==t.m; /* 11/5: くるっと回す: which ones turn, and how */")
sub("${t.m===15?' ace':''}${aceNew.includes(i)?' acein':''}\" data-i=\"${i}\" tabindex=\"0\" role=\"button\" aria-label=\"${tileName(t)}\"><span class=\"blk\">${svg(tileArt(t,true))}</span>",
    "${t.m===15?' ace':''}${aceNew.includes(i)?' acein':''}${tOk(t,i)?' turnable':''}\" data-i=\"${i}\" tabindex=\"0\" role=\"button\" aria-label=\"${tileName(t)}\"><span class=\"blk\">${svg(tileArt(t,true))}${tOk(t,i)?`<i class=\"turnmk\" aria-hidden=\"true\">${turnArrow()}</i>`:''}</span>")

# the tap: turn it for real
sub("const dealFx=x=>()=>{",
    "function turnArrow(){ /* a right-hand turn: an arc over the top with its head at the bottom right, cream on a wood outline */\n"
    "  const a='M20 50A30 30 0 1 1 71.2 71.2',h='62 80 79 79 64 63';\n"
    "  return `<svg viewBox=\"0 0 100 100\"><path d=\"${a}\" fill=\"none\" stroke=\"#74401f\" stroke-width=\"17\" stroke-linecap=\"round\"/><polygon points=\"${h}\" fill=\"#74401f\" stroke=\"#74401f\" stroke-width=\"8\" stroke-linejoin=\"round\"/>`+\n"
    "    `<path d=\"${a}\" fill=\"none\" stroke=\"#fff6e6\" stroke-width=\"9\" stroke-linecap=\"round\"/><polygon points=\"${h}\" fill=\"#fff6e6\" stroke=\"#fff6e6\" stroke-width=\"2\" stroke-linejoin=\"round\"/></svg>`;\n"
    "}\n"
    "const turnFx=x=>()=>{ /* 11/5: the road comes round from where it was, a quarter to the right; a big arrow spins over it */\n"
    "  const el=handEl.children[x];if(!el)return;\n"
    "  const g=el.querySelector('.rd'),b=el.querySelector('.blk');\n"
    "  if(g){g.classList.remove('turning');void g.getBoundingClientRect();g.classList.add('turning')}\n"
    "  if(b){b.insertAdjacentHTML('beforeend',`<i class=\"turnfx\" aria-hidden=\"true\">${turnArrow()}</i>`);const f=b.lastChild;setTimeout(()=>f.remove(),700)}\n"
    "  setTimeout(()=>{const a=mid(el);if(a)bits(a.x,a.y-a.w*.1,6,['#fff','#ffe58a'],a.w*.4,4)},380);\n"
    "};\n"
    "const dealFx=x=>()=>{")
sub("turn:x=>{const t=run.hand[x];if(rot(t.m)===t.m)return '回しても同じ形';t.m=rot(t.m);return dealFx(x)},",
    "turn:x=>{const t=run.hand[x];if(rot(t.m)===t.m)return '回しても同じ形';t.m=rot(t.m);return turnFx(x)},")
sub("const AIM_SAY={turn:'回す積み木をえらぶ',",
    "const AIM_SAY={turn:'右に回す積み木をえらぶ',")

# styles
sub(".slot.deal{animation:deal .3s ease-out backwards}",
    ".slot.deal{animation:deal .3s ease-out backwards}\n"
    "/* 11/5: くるっと回す: only the road turns, around the top face's centre */\n"
    ".slot .rd{transform-box:view-box}\n"
    ".slot.turnable .rd{animation:rdprev 1.8s ease-in-out infinite}\n"
    "@keyframes rdprev{0%,18%{transform:rotate(0);opacity:1}52%,78%{transform:rotate(90deg);opacity:1}88%{transform:rotate(90deg);opacity:0}89%{transform:rotate(0);opacity:0}100%{transform:rotate(0);opacity:1}}\n"
    ".slot .rd.turning{animation:rdturn .5s cubic-bezier(.3,1.45,.55,1) both}\n"
    "@keyframes rdturn{from{transform:rotate(-90deg)}to{transform:rotate(0)}}\n"
    ".slot .turnmk{position:absolute;right:-12%;top:-14%;width:50%;height:50%;z-index:3;pointer-events:none;filter:drop-shadow(0 2px 0 rgba(58,28,8,.35));animation:tmbob 1.8s ease-in-out infinite}\n"
    ".slot .turnmk svg,.slot .turnfx svg{width:100%;height:100%;display:block;overflow:visible}\n"
    "@keyframes tmbob{0%,18%,100%{transform:rotate(0) scale(1)}52%,78%{transform:rotate(20deg) scale(1.1)}}\n"
    ".slot .turnfx{position:absolute;inset:-4%;z-index:3;pointer-events:none;opacity:0;animation:tfx .6s ease-out forwards}\n"
    "@keyframes tfx{0%{opacity:0;transform:rotate(-70deg) scale(.75)}25%{opacity:.95}100%{opacity:0;transform:rotate(25deg) scale(1.05)}}\n"
    "@media (prefers-reduced-motion:reduce){.slot.turnable .rd,.slot .turnmk{animation:none}}")

P.write_text(s, encoding='utf-8')
print('ok')
