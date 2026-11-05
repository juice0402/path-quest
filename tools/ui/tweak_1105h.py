"""11/5 h: fixes from the screens-and-shop check before release.

- narrow phones (under 390px): つづける / もう一回 lost their last letter, and the shop's 強化する ran past the paper at 320px
- guards that the screens already keep, made sure in the code too: a skill on cooldown or pointed at nothing,
  a second takeReward, setting a skill not learned or still locked
- a save that was edited by hand: gold below 0, levels above MAX, a NEW for something that does not exist, a broken skill list
Applied once (like the other tweak_* files). Check: tools/test/narrow_check.py
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


# --- narrow phones ---
sub(".ov .ov-go .mk{position:static;align-self:flex-start;margin:6px 0 0 -2px;flex:none}",
    ".ov .ov-go .mk{position:static;align-self:flex-start;margin:6px 0 0 -2px;flex:none}\n"
    "/* 11/5: narrow phones: the plank ends get thinner and the words smaller, so つづける・もう一回・強化する stay whole */\n"
    "@media (max-width:389px){\n"
    "  #s-quit .ov-sub .btn,#ov .ov-sub .btn{--capw:18px;padding:8px 0;gap:4px}\n"
    "  #s-quit .ov-sub .btn.play,#ov .ov-sub .btn.play{font-size:16px;letter-spacing:0}\n"
    "  #s-quit .ov-sub .btn.play::before,#ov .ov-sub .btn.play::before{border-left-width:9px;border-top-width:6px;border-bottom-width:6px}\n"
    "  #s-quit .ov-sub .bi svg,#ov .ov-sub .bi svg{width:22px;height:22px}\n"
    "  .dt-foot{gap:6px}\n"
    "  .dt-btn{--capw:20px;min-width:0;padding:0 2px;gap:4px;font-size:16px;letter-spacing:.02em}\n"
    "  .dt-btn b{font-size:17px}\n"
    "  .dt-btn svg{width:20px;height:20px}\n"
    "  .dt-sub{min-width:60px;padding:0 8px}\n"
    "}\n"
    "@media (max-width:340px){\n"
    "  #s-quit .ov-sub .btn.play::before,#ov .ov-sub .btn.play::before{display:none}\n"
    "}")

# --- guards ---
sub("function useSkill(k,x){\n  const s=run.sk[k],d=SKILL_ID[s.id],lv=lvOf(rowOf(run.at));",
    "function useSkill(k,x){\n  if(!run||!run.sk||!run.sk[k]||run.sk[k].cd>0)return; /* 11/5: resting, or nothing in that slot */\n"
    "  const s=run.sk[k],d=SKILL_ID[s.id],lv=lvOf(rowOf(run.at));\n"
    "  if(!d||(d.aim&&!targets(d.aim).includes(x)))return; /* pointed at something it cannot take */")
sub("function takeReward(i){\n  const x=run.rewards[i];if(!x)return;",
    "function takeReward(i){\n  if(!run||!run.rewards)return; /* 11/5: already taken */\n  const x=run.rewards[i];if(!x)return;")
sub("function tickSkills(){ // one step walked\n",
    "function tickSkills(){ // one step walked\n  if(!run)return;\n")
sub("if(act==='set'){const eq=meta.sk.eq,",
    "if(act==='set'){if(!meta.sk.own.includes(sel)||isLocked('sk',sel))return;const eq=meta.sk.eq,")

# --- saves edited by hand ---
sub("const k=meta.sk,sown=k&&Array.isArray(k.own)",
    "const k=meta.sk&&typeof meta.sk==='object'?meta.sk:null,sown=k&&Array.isArray(k.own)")
sub("meta={bank:meta.bank|0,",
    "meta={bank:Math.max(0,meta.bank|0),")
sub("up:Object.fromEntries(UPS.map(x=>[x.k,u[x.k]|0]))",
    "up:Object.fromEntries(UPS.map(x=>[x.k,Math.min(x.max,Math.max(0,u[x.k]|0))]))")
sub(".filter(x=>/^(sk|up):/.test(x))};",
    ".filter(x=>{const [t,k]=String(x).split(':');return t==='sk'?!!SKILL_ID[k]:t==='up'&&UPS.some(v=>v.k===k)})};")

P.write_text(s, encoding='utf-8')
print('ok')
