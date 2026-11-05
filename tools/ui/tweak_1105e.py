"""11/5 e: the strong special blocks and skills open only as the climb goes further.

しょーくん「特殊な道とスキルとかで、強いやつは、コースを進めないとアンロックできないようにして」
- LOCK: the step (meta.far, the best ever) each one needs; what is already bought stays open
- the shop shows a locked one as a silhouette, ？？？ and a flag tag with the step
- passing the step in a climb: a note, and a NEW on it in the shop until it is tapped
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


# --- the table, the checks, and what opens when the record moves ---
sub("const saveMeta=()=>store.set(META,meta);",
    "const saveMeta=()=>store.set(META,meta);\n"
    "/* 11/5: the strong ones open as the climb goes further (meta.far = the best step ever). what is already bought stays open */\n"
    "const LOCK={\n"
    "  sk:{clear:10,rain:10,cross:20,wind:20,box:40,cannon:40,treasure:50},\n"
    "  up:{sd:10,dx:20,sh:20,sj:20,ds:40,sg:40}\n"
    "};\n"
    "const lockAt=(t,k)=>LOCK[t][k]||0;\n"
    "const isLocked=(t,k)=>meta.far<lockAt(t,k)&&!(t==='sk'?meta.sk.own.includes(k):meta.up[k]>0);\n"
    "const lockTag=(t,k)=>`<span class=\"tag lk\">${ico(SPR.flag)}${lockAt(t,k)}段</span>`;\n"
    "const lockPaper=(art,txt)=>`<span class=\"dt-art lk\">${art}</span><div class=\"dt-head\"><b>？？？</b></div><div class=\"dt-body\"><p class=\"dt-d dim\">${txt}</p><p class=\"dt-d dim lk-now\">いまの記録 ${nf(meta.far)}段</p></div><div class=\"dt-foot\"></div>`;\n"
    "function opened(a,b){ /* the record went from a to b: what opened goes into the shop with a NEW */\n"
    "  const sk=SKILLS.filter(k=>LOCK.sk[k.id]>a&&LOCK.sk[k.id]<=b&&!meta.sk.own.includes(k.id)).map(k=>'sk:'+k.id),\n"
    "        up=UPS.filter(u=>LOCK.up[u.k]>a&&LOCK.up[u.k]<=b&&!meta.up[u.k]).map(u=>'up:'+u.k);\n"
    "  if(!sk.length&&!up.length)return;\n"
    "  meta.newu=[...new Set([...(meta.newu||[]),...sk,...up])];\n"
    "  note(`お店に 新しい${sk.length&&up.length?'スキルと積み木':sk.length?'スキル':'積み木'}が出た`,'good');\n"
    "}")

sub("newg:(Array.isArray(meta.newg)?meta.newg:[]).filter(id=>GEAR_ID[id])};",
    "newg:(Array.isArray(meta.newg)?meta.newg:[]).filter(id=>GEAR_ID[id]),newu:(Array.isArray(meta.newu)?meta.newu:[]).filter(x=>/^(sk|up):/.test(x))};")

sub("if(s>meta.far){meta.far=s;saveMeta()}",
    "if(s>meta.far){const was=meta.far;meta.far=s;opened(was,s);saveMeta()}")

# --- the shop: rows, the skill book, the pinned paper ---
sub("function upRow(u){\n",
    "function upRow(u){\n"
    "  const nw=(meta.newu||[]).includes('up:'+u.k)?' <i class=\"nw\">NEW</i>':'';\n"
    "  if(isLocked('up',u.k))return `<button class=\"row-i lk${shopSel[shopTab]===u.k?' sel':''}\" type=\"button\" data-k=\"${u.k}\" aria-label=\"まだ出てきていない\"><span class=\"ri-art\">${upArt(u)}</span>`+\n"
    "    `<span class=\"ri-name\"><b>？？？</b><span class=\"ri-sub\">先へ進むと出てくる</span></span>${lockTag('up',u.k)}</button>`;\n")
sub("`<span class=\"ri-name\"><b>${UPNAME[u.k]||u.name}</b>",
    "`<span class=\"ri-name\"><b>${UPNAME[u.k]||u.name}${nw}</b>")

sub("after=u&&mi!=null&&meta.up[k]<u.max?",
    "after=u&&mi!=null&&meta.up[k]<u.max&&!isLocked('up',k)?")

sub("""  h+='<div class="book">'+SKILLS.map(k=>{const has=own.includes(k.id),on=eq.includes(k.id);
    const tag=on?""",
    """  h+='<div class="book">'+SKILLS.map(k=>{const has=own.includes(k.id),on=eq.includes(k.id),lk=isLocked('sk',k.id),nw=(meta.newu||[]).includes('sk:'+k.id);
    const tag=lk?lockTag('sk',k.id):on?""")
sub("""return `<button class="sk2${has?'':' not'}${shopSel.skill===k.id?' sel':''}" type="button" data-s="${k.id}">${svg(SK_ART[k.id])}<b>${k.n}</b>${tag}</button>`}""",
    """return `<button class="sk2${has?'':' not'}${lk?' lk':''}${shopSel.skill===k.id?' sel':''}" type="button" data-s="${k.id}"${lk?' aria-label="まだ出てきていない"':''}>${svg(SK_ART[k.id])}<b>${lk?'？？？':k.n}</b>${tag}${nw?'<i class="nw">NEW</i>':''}</button>`}""")

sub("    const u=UPS.find(x=>x.k===sel);if(!u)return '';\n    const l=meta.up[u.k],max=l>=u.max,c=u.cost(l),v=UPV[u.k],mi=MIX_OF[u.k];",
    "    const u=UPS.find(x=>x.k===sel);if(!u)return '';\n"
    "    if(isLocked('up',u.k))return lockPaper(upArt(u),`${lockAt('up',u.k)}段まで進むと お店に出てくる`);\n"
    "    const l=meta.up[u.k],max=l>=u.max,c=u.cost(l),v=UPV[u.k],mi=MIX_OF[u.k];")
sub("    const k=SKILL_ID[sel];if(!k)return '';\n    const has=meta.sk.own.includes(k.id)",
    "    const k=SKILL_ID[sel];if(!k)return '';\n"
    "    if(isLocked('sk',k.id))return lockPaper(svg(SK_ART[k.id]),`${lockAt('sk',k.id)}段まで進むと 覚えられるようになる`);\n"
    "    const has=meta.sk.own.includes(k.id)")

# marks on the tabs and on the result screen's shop button: locked ones do not count, NEW ones do
sub("canU=f=>UPS.some(u=>!!u.deck===f&&meta.up[u.k]<u.max&&u.cost(meta.up[u.k])<=b);",
    "canU=f=>UPS.some(u=>!!u.deck===f&&meta.up[u.k]<u.max&&u.cost(meta.up[u.k])<=b&&!isLocked('up',u.k)),nn2=p=>(meta.newu||[]).filter(x=>x.startsWith(p)).length;")
sub("mk('tab-deck',canU(true)?'coin':'');",
    "{const n=nn2('up:');mk('tab-deck',n?'new':canU(true)?'coin':'',n?String(n):'')}")
sub("mk('tab-skill',SKILLS.some(k=>!meta.sk.own.includes(k.id)&&k.cost<=b)?'coin':'');",
    "{const n=nn2('sk:');mk('tab-skill',n?'new':SKILLS.some(k=>!meta.sk.own.includes(k.id)&&k.cost<=b&&!isLocked('sk',k.id))?'coin':'',n?String(n):'')}")
sub("const affordable=()=>{const b=meta.bank;return UPS.some(u=>meta.up[u.k]<u.max&&u.cost(meta.up[u.k])<=b)||SKILLS.some(k=>!meta.sk.own.includes(k.id)&&k.cost<=b)};",
    "const affordable=()=>{const b=meta.bank;return (meta.newu||[]).length>0||UPS.some(u=>meta.up[u.k]<u.max&&u.cost(meta.up[u.k])<=b&&!isLocked('up',u.k))||SKILLS.some(k=>!meta.sk.own.includes(k.id)&&k.cost<=b&&!isLocked('sk',k.id))};")

# the NEW goes once it has been looked at (like the gear's)
sub("if(shopTab==='gear'&&meta.newg&&meta.newg.includes(shopSel.gear)){meta.newg=meta.newg.filter(x=>x!==shopSel.gear);saveMeta()}",
    "if(shopTab==='gear'&&meta.newg&&meta.newg.includes(shopSel.gear)){meta.newg=meta.newg.filter(x=>x!==shopSel.gear);saveMeta()}\n"
    "  if(shopTab==='skill'||shopTab==='deck'){const nk=(shopTab==='skill'?'sk:':'up:')+shopSel[shopTab];if(meta.newu&&meta.newu.includes(nk)){meta.newu=meta.newu.filter(x=>x!==nk);saveMeta()}}")

# buying cannot go round the lock
sub("if(!u||l>=u.max||meta.bank<c)return;", "if(!u||l>=u.max||meta.bank<c||isLocked('up',u.k))return;")
sub("if(!k||meta.sk.own.includes(k.id)||meta.bank<k.cost)return;", "if(!k||meta.sk.own.includes(k.id)||meta.bank<k.cost||isLocked('sk',k.id))return;")

# test hook
sub("AUD,QK,UPS,SKILL_ID,", "AUD,QK,UPS,SKILL_ID,LOCK,isLocked,opened,")

# --- styles: the same quiet silhouette as gear not found yet ---
sub(".gi2.lock .st{color:#b3a493}",
    ".gi2.lock .st{color:#b3a493}\n"
    ".sk2.lk{background:#efe6dc}\n"
    ".book .sk2.lk>svg,.row-i.lk .ri-art svg,.dt-art.lk svg{filter:brightness(0) opacity(.13)}\n"
    ".sk2.lk b,.row-i.lk .ri-name b{color:#b3a493}\n"
    ".tag.lk{padding:2px 7px 2px 2px;background:transparent;outline-color:#cdbca9;color:#9c8774;font-size:14px}\n"
    ".tag.lk svg{width:18px;height:18px;filter:saturate(.4) opacity(.8)}\n"
    ".sk2 .tag.lk{font-size:12px}\n"
    ".sk2 .tag.lk svg{width:15px;height:15px}\n"
    ".sk2 .nw{position:absolute;top:-6px;right:-6px;padding:1px 4px;background:#e23c56;font:800 10px/1.4 var(--round);color:#fff;font-style:normal}\n"
    ".row-i .ri-name b .nw{display:inline-block;margin-left:6px;padding:2px 4px;font-size:10px;font-style:normal;vertical-align:2px}\n"
    ".dt-d.lk-now{margin-top:4px;font-size:12px}")

P.write_text(s, encoding='utf-8')
print('ok')
