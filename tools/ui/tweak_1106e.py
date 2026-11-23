"""11/6 e: くるっと回すで、道が積み木からはみ出さない。

しょーくん「くるっと回すのスキルの回転って、積み木自体を回すことはやっぱり難しいのかな。
道の絵だけ回すとしても、回した後はみ出さないように回して欲しい」

The block's top face is wider than it is tall (92 x 76: the block is seen a little from the front), and the road in the
tray ran from the middle of the top face to its edges (up 39, sideways 46) and on down the front side to the bottom (53).
The whole road turned as one picture around the middle of the top face, so a quarter turn put the long arm off the left
edge, the short ones fell short of the edges, and half way round the ends stuck out past the corners.

Now in the tray:
- the road on the top face is cut to the top face (clipPath #rdtop), so no part of it ever leaves the block
- the arms that run up/down (.rv) and the ones that run sideways (.rh) turn as two groups, and each stretches or shrinks
  along its own length while it turns (up/down 39 -> sideways 46, sideways 46 -> up/down 39), so after a quarter turn the
  ends sit on the edges of the top face exactly, as the road of the new shape does. The width stays the same.
- the bit of road down the front side (.rs, cut to below the top face by #rdside) is drawn apart and does not turn: the
  front of the block stays where it is. In the preview it fades out as its arm leaves and the new shape's one fades in
  as an arm arrives (.rsx, only drawn while choosing a block to turn); on the tap it shows when the arm has come round.
At rest the tray looks as before (the cuts are just outside the road's ends; tools/test/same_look.py).
The block itself stays still: its picture has the thick side painted at the bottom, so turning the whole picture would
swing the side round to the left, as if the block fell over.
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


# the cuts: the top face, and the front side under it (in the block's own 0..100 box)
sub("const RC=HAS_ART?43:47;",
    "const RC=HAS_ART?43:47;"
    "/* 11/6 e: the tray road is cut to the block's top face, so a turn never pokes out; #rdside is the front side under it */"
    "{const fb=HAS_ART?82:88.5;(document.body||document.documentElement).insertAdjacentHTML('beforeend',"
    "`<svg class=\"art-defs\" width=\"0\" height=\"0\" aria-hidden=\"true\" focusable=\"false\"><defs>"
    "<clipPath id=\"rdtop\" clipPathUnits=\"userSpaceOnUse\"><rect x=\"3.5\" y=\"3.5\" width=\"93\" height=\"${fb-3.5}\" rx=\"8\"/></clipPath>"
    "<clipPath id=\"rdside\" clipPathUnits=\"userSpaceOnUse\"><rect x=\"0\" y=\"${fb-1}\" width=\"100\" height=\"${104-fb}\"/></clipPath>"
    "</defs></svg>`)}")

# the tray's road: two groups of arms that turn and stretch, inside the top face; the front side apart
sub("const tileArt0=(t,inTray,at)=>",
    "function roadTray(m,sh,ace){ /* 11/6 e: the road in the tray. Up/down arms (.rv) and sideways arms (.rh) turn as two groups\n"
    "  and stretch to the top face's edges (it is wider than tall); all of it is cut to the top face. The bit down the front side\n"
    "  (.rs) does not turn: .rsn is this shape's, .rsx the shape after a quarter turn (shown only in the preview) */\n"
    "  const w=ace?'#fff0a0':'#fffdf8',dc=ace?'#e8a520':sh,o=`style=\"transform-origin:50% ${RC}%\"`;\n"
    "  const seg={1:`M50 ${RC}V4`,2:`M50 ${RC}H96`,4:`M50 ${RC}V96`,8:`M50 ${RC}H4`};\n"
    "  const L=[d=>`<path d=\"${d}\" stroke=\"${sh}\" stroke-width=\"36\" fill=\"none\"/>`,d=>`<path d=\"${d}\" stroke=\"${w}\" stroke-width=\"28\" fill=\"none\"/>`,\n"
    "    d=>`<path d=\"${d}\" stroke=\"${dc}\" stroke-width=\"3.5\" stroke-dasharray=\"7 7\" fill=\"none\"/>`];\n"
    "  const v=(m&1?seg[1]:'')+(m&4?seg[4]:''),h=(m&2?seg[2]:'')+(m&8?seg[8]:'');\n"
    "  const arms=f=>(v?`<g class=\"ra rv\" ${o}>${f(v)}</g>`:'')+(h?`<g class=\"ra rh\" ${o}>${f(h)}</g>`:'');\n"
    "  const side=c=>`<g class=\"rs ${c}\" clip-path=\"url(#rdside)\">${L[0](seg[4])}${L[1](seg[4])}${L[2](seg[4])}</g>`;\n"
    "  return `<g clip-path=\"url(#rdtop)\">${arms(L[0])}<circle cx=\"50\" cy=\"${RC}\" r=\"18\" fill=\"${sh}\"/>${arms(L[1])}<circle cx=\"50\" cy=\"${RC}\" r=\"14\" fill=\"${w}\"/>${arms(L[2])}</g>`\n"
    "    +(m&4?side('rsn'):'')+(m&2?side('rsx'):'');\n"
    "}\n"
    "const tileArt0=(t,inTray,at)=>")
sub("(inTray?`<g class=\"rd\" style=\"transform-origin:50% ${RC}%\">${roadSVG(t.m,BLOCKS[c][1],4,96,ace)}</g>`:",
    "(inTray?`<g class=\"rd\">${roadTray(t.m,BLOCKS[c][1],ace)}</g>`:")

# the motion: the preview loop and the tap
sub("/* 11/5: くるっと回す: only the road turns, around the top face's centre */\n"
    ".slot .rd{transform-box:view-box}\n"
    ".slot.turnable .rd{animation:rdprev 1.8s ease-in-out infinite}\n"
    "@keyframes rdprev{0%,18%{transform:rotate(0);opacity:1}52%,78%{transform:rotate(90deg);opacity:1}88%{transform:rotate(90deg);opacity:0}89%{transform:rotate(0);opacity:0}100%{transform:rotate(0);opacity:1}}\n"
    ".slot .rd.turning{animation:rdturn .5s cubic-bezier(.3,1.45,.55,1) both}\n"
    "@keyframes rdturn{from{transform:rotate(-90deg)}to{transform:rotate(0)}}\n",
    "/* 11/5: くるっと回す: only the road turns, around the top face's centre. 11/6 e: cut to the top face, the arms stretch to its\n"
    "   edges as they turn (up/down 39 <-> sideways 46), the bit down the front side stays and fades (roadTray) */\n"
    ".slot .ra{transform-box:view-box}\n"
    ".rs.rsx{display:none}\n"
    ".slot.turnable .rd{animation:rdfade 1.8s ease-in-out infinite}\n"
    ".slot.turnable .rv{animation:rvprev 1.8s ease-in-out infinite}\n"
    ".slot.turnable .rh{animation:rhprev 1.8s ease-in-out infinite}\n"
    ".slot.turnable .rsn{animation:rsnprev 1.8s linear infinite}\n"
    ".slot.turnable .rs.rsx{display:inline;animation:rsxprev 1.8s linear infinite}\n"
    "@keyframes rdfade{0%,78%{opacity:1}88%,89%{opacity:0}100%{opacity:1}}\n"
    "@keyframes rvprev{0%,18%{transform:rotate(0) scaleY(1)}52%,88%{transform:rotate(90deg) scaleY(1.18)}89%,100%{transform:rotate(0) scaleY(1)}}\n"
    "@keyframes rhprev{0%,18%{transform:rotate(0) scaleX(1)}52%,88%{transform:rotate(90deg) scaleX(.85)}89%,100%{transform:rotate(0) scaleX(1)}}\n"
    "@keyframes rsnprev{0%,18%{opacity:1}26%,88%{opacity:0}89%,100%{opacity:1}}\n"
    "@keyframes rsxprev{0%,44%{opacity:0}52%,88%{opacity:1}89%,100%{opacity:0}}\n"
    ".slot .rd.turning .rv{animation:rvturn .5s cubic-bezier(.3,1.45,.55,1) both}\n"
    ".slot .rd.turning .rh{animation:rhturn .5s cubic-bezier(.3,1.45,.55,1) both}\n"
    ".slot .rd.turning .rsn{animation:rsnturn .5s linear both}\n"
    "@keyframes rvturn{from{transform:rotate(-90deg) scaleY(1.18)}to{transform:rotate(0) scaleY(1)}}\n"
    "@keyframes rhturn{from{transform:rotate(-90deg) scaleX(.85)}to{transform:rotate(0) scaleX(1)}}\n"
    "@keyframes rsnturn{0%,40%{opacity:0}62%,100%{opacity:1}}\n")
sub("@media (prefers-reduced-motion:reduce){.slot.turnable .rd,.slot .turnmk{animation:none}}",
    "@media (prefers-reduced-motion:reduce){.slot.turnable .rd,.slot.turnable .ra,.slot.turnable .rs,.slot .turnmk{animation:none}.slot.turnable .rs.rsx{display:none}}")

P.write_text(s, encoding='utf-8')
print('ok')
