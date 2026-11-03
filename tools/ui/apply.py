# builds new.html from orig.html: things stand up out of their panels, and the critters are Canva toys
import json, re
SRC = '/home/claude/pq/orig.html'
OUT = '/home/claude/pq/new.html'
s = open(SRC).read()

def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, old[:90])
    s = s.replace(old, new)

# ---------- css ----------
CSS_D = r'''
/* ===== fx css D: depth — toys and obstacles stand up out of their panels ===== */
/* they are drawn taller than the panel, so their heads reach over the panel behind (the rows are drawn back to front) */
.cell.rock>svg,.cell.stand>svg{overflow:visible}
.cell.rock.a-grass{--obk:1.3}.cell.rock.a-forest,.cell.rock.a-snow{--obk:1.45}.cell.rock.a-castle{--obk:1.28}
/* panels with something standing on them are drawn over the plain ground around them, in row order among themselves */
.board>.cell.rock,.board>.cell.laid{z-index:2}
.cell.lf-sway>svg,.cell.lf-wob>svg{transform-origin:50% 62%}
/* the small lives on an obstacle grow with it */
.cell .lf-smk{width:calc(14% * var(--obk,1));margin:calc(-7% * var(--obk,1)) 0 0 calc(-7% * var(--obk,1))}
.cell .lf-leaf{width:calc(11% * var(--obk,1));margin:calc(-5.5% * var(--obk,1)) 0 0 calc(-5.5% * var(--obk,1))}
.cell .lf-pk{width:calc(18% * var(--obk,1));margin:calc(-9% * var(--obk,1)) 0 0 calc(-9% * var(--obk,1))}
.cell .lf-pk2{width:calc(16% * var(--obk,1));margin:calc(-8% * var(--obk,1)) 0 0 calc(-8% * var(--obk,1))}
.cell .lf-pen{width:calc(2.4% * var(--obk,1));height:calc(14% * var(--obk,1));margin:calc(-14% * var(--obk,1)) 0 0 calc(-1.2% * var(--obk,1))}
.cell .lf-chim{width:calc(12% * var(--obk,1))}
.cell .lf-door{width:calc(30% * var(--obk,1));height:calc(32% * var(--obk,1));margin:calc(-16% * var(--obk,1)) 0 0 calc(-15% * var(--obk,1))}
/* the knight's cast shadow stays on the ground while he bobs */
.hero>svg.hsh{position:absolute;inset:0;z-index:-1;animation:none!important;transition:opacity .4s}
.hero.down>svg.hsh{opacity:0;transition-delay:.9s}
/* treasure floating over its panel: its shadow shrinks as it rises */
.lsh{transform-box:fill-box;transform-origin:center;animation:lsh 1.1s ease-in-out var(--d,0s) infinite alternate}
@keyframes lsh{from{transform:scale(1.05);opacity:1}to{transform:scale(.68);opacity:.55}}
/* critters: a soft shadow on the ground, and for the flyers a shadow that shrinks as they climb */
.lf-gr::before{left:12%;right:12%;bottom:-4%;height:20%;background:radial-gradient(closest-side,rgba(60,32,46,.34),rgba(60,32,46,.12) 62%,rgba(60,32,46,0))}
.lf-air::before{left:22%;right:22%;bottom:-46%;height:17%;background:radial-gradient(closest-side,rgba(60,32,46,.26),rgba(60,32,46,0));animation:lfAirSh 1.9s ease-in-out calc(var(--lfT,0s) + var(--sd,0s)) infinite alternate}
@keyframes lfAirSh{to{scale:.66;opacity:.55}}
.mv-fl>b{animation:lfFlap .2s ease-in-out calc(var(--lfT,0s) + var(--sd,0s)) infinite alternate,lfAlt 1.9s ease-in-out calc(var(--lfT,0s) + var(--sd,0s)) infinite alternate}
.mv-df>b{animation:lfFlick .1s steps(2) calc(var(--lfT,0s) + var(--sd,0s)) infinite,lfAlt 1.9s ease-in-out calc(var(--lfT,0s) + var(--sd,0s)) infinite alternate}
@keyframes lfAlt{to{translate:0 -16%}}
/* the bee and the dragonfly: the wings beat behind the body */
.lf-wb>b{background:none!important}
.lf-wb>b::before,.lf-wb>b::after{content:"";position:absolute;inset:0;background:center/contain no-repeat}
.lf-wb>b::before{transform-origin:50% 42%;animation:lfBeat .06s ease-in-out calc(var(--lfT,0s) + var(--sd,0s)) infinite alternate}
.lf-s-dfly.lf-wb>b::before{transform-origin:50% 30%;animation-duration:.05s}
@keyframes lfBeat{from{scale:1 1;opacity:.95}to{scale:.42 .92;opacity:.6}}
.mv-df.lf-wb>b{animation:lfAlt 1.9s ease-in-out calc(var(--lfT,0s) + var(--sd,0s)) infinite alternate}
/* the snail inches along */
.mv-sl{animation:lfWd 40s linear calc(var(--lfT,0s) + var(--sd,0s)) infinite}
.mv-sl>b{transform-origin:50% 100%;animation:lfInch 1.6s ease-in-out calc(var(--lfT,0s) + var(--sd,0s)) infinite alternate}
@keyframes lfInch{to{scale:1.07 .94}}
@media (prefers-reduced-motion:reduce){.lsh,.lf-air::before,.lf-wb>b::before,.mv-sl,.mv-sl>b{animation:none!important}}
/* the climb gauge under the status is gone: the status is one row */
.prog{display:none!important}
.say{top:calc(var(--hudh) + 6px)}
/* ===== end of fx css D ===== */
'''
rep('/* ===== end of fx css C ===== */\n</style>', '/* ===== end of fx css C ===== */\n' + CSS_D + '</style>')

# ---------- cast-shadow symbols, right after the art block ----------
sh = open('/home/claude/pq/build/shadows.html').read()
lines = s.split('\n')
ix=[k for k,l in enumerate(lines) if l.startswith('<svg class="art-defs"') and 'id="a-hero"' in l]
assert len(ix)==1 and lines[ix[0]].endswith('</svg>')
lines.insert(ix[0]+1, sh)
s = '\n'.join(lines)

# ---------- module A: the standing pose ----------
rep("const OB_BASE={ // drawn under the obstacle: its shadow and a little ground of its land",
r'''/* standing up: things are drawn taller than their panel with their feet a little above its front edge, so their heads
   reach over the panel behind; each leans away from the middle of the screen (a camera above the board) and casts a
   long soft shadow back and to the left (the Canva art's silhouettes, a-*-sh) */
const DEP={up:1.4,upA:{grass:1.3,forest:1.45,snow:1.45,castle:1.28},foot:62,sa:.5,sb:.5,foe:1.22};
const LEAN=i=>((W-1)/2-colOf(i))*2.2; // skewX degrees: + leans left
const CASTM=fy=>`matrix(1 0 ${DEP.sa} ${DEP.sb} ${(-DEP.sa*fy).toFixed(2)} ${(fy*(1-DEP.sb)).toFixed(2)})`;
const SHM=new Map();
const SHAD=s=>(String(s).match(/<use href="#a-[a-z0-9]+"[^>]*\/>/g)||[]).map(u=>{const n=u.match(/#a-([a-z0-9]+)/)[1];
  if(!SHM.has(n))SHM.set(n,!!document.getElementById('a-'+n+'-sh'));return SHM.get(n)?u.replace('"#a-'+n+'"','"#a-'+n+'-sh"'):''}).join('');
const CONTACT=(f,rx)=>`<ellipse cx="50" cy="${f+.6}" rx="${rx}" ry="${(rx*.17).toFixed(1)}" fill="url(#pq-ct)"/>`;
document.body.insertAdjacentHTML('beforeend','<svg class="art-defs" width="0" height="0" aria-hidden="true" focusable="false"><defs><radialGradient id="pq-ct"><stop offset="0" stop-color="#2e1624" stop-opacity=".5"/><stop offset=".55" stop-color="#2e1624" stop-opacity=".26"/><stop offset="1" stop-color="#2e1624" stop-opacity="0"/></radialGradient></defs></svg>');
/* art drawn with its feet at (50,f0) stands on panel i: feet at f, k times bigger, leaning, with its shadows */
function standArt(i,art,f0,k,f,rx,flip){
  const g=`translate(50 ${f}) skewX(${LEAN(i).toFixed(2)}) scale(${(flip?-k:k).toFixed(3)} ${k.toFixed(3)}) translate(-50 -${f0})`;
  return `<g transform="${CASTM(f)}"><g transform="${g}">${SHAD(art)}</g></g>`+(rx?CONTACT(f,rx):'')+`<g transform="${g}">${art}</g>`;
}
const OB_BASE={ // drawn under the obstacle: its shadow and a little ground of its land''')

rep(r'''function obArt(i,a){ // the obstacle on panel i: its land's base, then the toy turned, sized and nudged its own way
  const ob=SPR.ob[a]||SPR.ob.grass,h=A_H(i,7),fl=h&1,x=(h>>>10)%10,ex=(OB_EXTRA[a]||OB_EXTRA.grass)(x);
  let s=.92+((h>>>1)%8)*.016,dx=((h>>>4)%7)-3;const ro=((((h>>>7)%7)-3)*.8).toFixed(1);
  if(a==='forest'&&ex[0]){s*=.9;dx-=9} // two trees: the big one steps aside
  return (OB_BASE[a]||'')+ex[0]+`<g transform="translate(${50+dx} 88) rotate(${ro}) scale(${(fl?-s:s).toFixed(3)} ${s.toFixed(3)}) translate(-50 -88)">${ob}</g>`+ex[1];
}''',
r'''function obArt(i,a){ // the obstacle on panel i: its land's base, then the toy turned, sized and nudged its own way
  const ob=SPR.ob[a]||SPR.ob.grass,h=A_H(i,7),fl=h&1,x=(h>>>10)%10,ex=(OB_EXTRA[a]||OB_EXTRA.grass)(x);
  let s=.92+((h>>>1)%8)*.016,dx=((h>>>4)%7)-3;const ro=((((h>>>7)%7)-3)*.8).toFixed(1);
  if(a==='forest'&&ex[0]){s*=.9;dx-=9} // two trees: the big one steps aside
  if(a==='lake')return (OB_BASE[a]||'')+ex[0]+`<g transform="translate(${50+dx} 88) rotate(${ro}) scale(${(fl?-s:s).toFixed(3)} ${s.toFixed(3)}) translate(-50 -88)">${ob}</g>`+ex[1]; // the pond lies flat
  const k=s*(DEP.upA[a]||DEP.up),f=DEP.foot,c0=colOf(i);dx+=c0===0?5:c0===W-1?-5:0; // the edge columns step in, so a toy is not cut by the screen
  const g=`translate(${50+dx} ${f}) rotate(${ro}) skewX(${LEAN(i).toFixed(2)}) scale(${(fl?-k:k).toFixed(3)} ${k.toFixed(3)}) translate(-50 -88)`;
  const back=ex[0]?`<g transform="translate(0 ${f-88})">${ex[0]}</g>`:'',front=ex[1]?`<g transform="translate(0 ${f-88})">${ex[1]}</g>`:'';
  return `<g transform="${CASTM(f)}"><g transform="${g}">${SHAD(ob)}</g></g>`+`<g transform="translate(0 ${f-88+1})">${OB_BASE[a]||''}</g>`+CONTACT(f,a==='snow'?22:28)+back+`<g transform="${g}">${ob}</g>`+front;
}
/* a toy standing on the field, and a toy standing on a laid block */
const FOE_F0=t=>t==='king'?94:t==='boss'?90:88;
const toyStand=(i,t)=>standArt(i,`<g class="toy">${SPR[t]||SPR.soldier}</g>`,FOE_F0(t),DEP.foe,DEP.foot,0);
const toyOnBlock=(i,t)=>standArt(i,`<g class="toy">${SPR[t]||SPR.soldier}</g>`,FOE_F0(t),.86,RC+14,0);''')

rep("SPR.brick=AO(50,85,40,7.5)+'<rect x=\"10\" y=\"84\" width=\"4\" height=\"3\" rx=\"1\" fill=\"#d8cdf6\"/><rect x=\"85\" y=\"82\" width=\"3.5\" height=\"3\" rx=\"1\" fill=\"#f7c3d4\"/>'+(HAS_ART?U('brick',8,18,84,68):SPR.brick);",
"SPR.brick=AO(50,85,40,7.5)+'<rect x=\"10\" y=\"84\" width=\"4\" height=\"3\" rx=\"1\" fill=\"#d8cdf6\"/><rect x=\"85\" y=\"82\" width=\"3.5\" height=\"3\" rx=\"1\" fill=\"#f7c3d4\"/>'+(HAS_ART?U('brick',8,18,84,68):SPR.brick);\n"
"const brickArt=i=>HAS_ART?standArt(i,U('brick',8,18,84,68),86,1.12,DEP.foot,34):SPR.brick;\n"
"if(HAS_ART){ // the knight: a little taller, with his long shadow on the ground beside him\n"
"  const ha=U('hero',16,-6,68,94),hf=70,hg=`translate(50 ${hf}) scale(1.1) translate(-50 -88)`;\n"
"  hero.innerHTML=svg(`<g transform=\"${hg}\">${ha}</g>`)+`<svg class=\"hsh\" viewBox=\"0 0 100 100\" aria-hidden=\"true\" style=\"overflow:visible\"><g transform=\"${CASTM(hf)}\"><g transform=\"${hg}\">${SHAD(ha)}</g></g>${CONTACT(hf,20)}</svg>`; // the shadow goes last: lunge() moves the first child\n"
"}")

# ---------- cells ----------
rep("""else if(c.foe){cls+=' rock stand'+(aim&&aim.kind==='rock'&&rowOf(i)>=rowOf(run.at)?' aim':'')+(reachOf(i,c.foe)?' threat':'');inner=svg(`<g class="toy">${SPR[c.foe.t]||SPR.soldier}</g>`)""",
    """else if(c.foe){cls+=' rock stand'+(aim&&aim.kind==='rock'&&rowOf(i)>=rowOf(run.at)?' aim':'')+(reachOf(i,c.foe)?' threat':'');inner=svg(HAS_ART?toyStand(i,c.foe.t):`<g class="toy">${SPR[c.foe.t]||SPR.soldier}</g>`)""")
rep("inner=svg(c.rock===3?SPR.brick:obArt(i,a))", "inner=svg(c.rock===3?brickArt(i):obArt(i,a))")
rep("inner=svg(tileArt(c.tile))+badge(c.tile.e)", "inner=svg(tileArt(c.tile,false,i))+badge(c.tile.e)")
rep("const tileArt=(t,inTray)=>{", "const tileArt=(t,inTray,at)=>{")
rep("+evSVG(t.e)+(ace?", "+evSVG(t.e,at)+(ace?")
rep("""function evSVG(e){
  if(!e)return '';
  if(e.k==='foe')return `<g""", """function evSVG(e,at){
  if(!e)return '';
  if(e.k==='foe'&&at!=null&&HAS_ART)return toyOnBlock(at,e.t); // on the field the toy stands on the block
  if(e.k==='foe')return `<g""")
# treasure: a shadow on the ground under it
rep("""return (glow?`<circle class="lglow" cx="50" cy="54" r="23" fill="#fff3a8" ${d}/>`:'')+`<g class="loot" ${d}>""",
    """return `<ellipse class="lsh" cx="50" cy="79" rx="15" ry="3.6" fill="rgba(60,30,46,.24)" ${d}/>`+(glow?`<circle class="lglow" cx="50" cy="54" r="23" fill="#fff3a8" ${d}/>`:'')+`<g class="loot" ${d}>""")

# ---------- module B: the big captain and king cast a shadow too ----------
rep("""<ellipse cx="${cx}" cy="189" rx="${en.king?50:44}" ry="8.5" fill="rgba(90,20,40,.4)"/></svg>`+""",
    """<ellipse cx="${cx}" cy="189" rx="${en.king?50:44}" ry="8.5" fill="rgba(90,20,40,.4)"/>${typeof SHAD==='function'?`<g transform="matrix(1 0 .5 .5 -86.5 86.5)"><g transform="translate(${(cx-50*k).toFixed(1)} ${(192-foot*k).toFixed(1)}) scale(${k})">${SHAD(art)}</g></g>`:''}</svg>`+""")

rep('transform-origin:${cx/2}% 95%','transform-origin:${cx/2}% 86%')
rep('192-foot*k','173-foot*k',2)
rep('<ellipse cx="${cx}" cy="189" rx="${en.king?64:58}" ry="14" fill="rgba(214,51,79,.28)"/><ellipse cx="${cx}" cy="189"','<ellipse cx="${cx}" cy="171" rx="${en.king?64:58}" ry="14" fill="rgba(214,51,79,.28)"/><ellipse cx="${cx}" cy="171"')
# ---------- module C: small lives follow the standing pose; Canva critters ----------
rep("""    if(typeof A_H!=='function')return {fl:0,s:1,dx:0,ro:0};""", """    if(typeof A_H!=='function')return {fl:0,s:1,k:1,dx:0,ro:0,f:88,ln:0};""")
rep("""    return {fl:h&1,s,dx,ro:(((h>>>7)%7)-3)*.8};""",
    """    const st=a!=='lake'&&typeof DEP!=='undefined'; // standing obstacles are taller and lean (module A's obArt)
    const c0=colOf(i),dx2=st?dx+(c0===0?5:c0===W-1?-5:0):dx;
    return {fl:h&1,s,k:st?s*(DEP.upA[a]||DEP.up):s,dx:dx2,ro:(((h>>>7)%7)-3)*.8,f:st?DEP.foot:88,ln:st?LEAN(i):0};""")
rep("""    const at=(x,y)=>{const X=(x-50)*(p.fl?-p.s:p.s),Y=(y-88)*p.s;return `left:${(X*cs-Y*sn+50+p.dx).toFixed(1)}%;top:${(X*sn+Y*cs+88).toFixed(1)}%`};""",
    """    const tk=Math.tan(p.ln*Math.PI/180),at=(x,y)=>{const Y=(y-88)*p.k,X=(x-50)*(p.fl?-p.k:p.k)+tk*Y;return `left:${(X*cs-Y*sn+50+p.dx).toFixed(1)}%;top:${(X*sn+Y*cs+p.f).toFixed(1)}%`};""")
rep("""lf-s-tit" style="${at(75,51)};--z:15%;""", """lf-s-tit" style="${at(75,51)};--z:${(15*p.k/p.s).toFixed(1)}%;""")
rep(""";rotate:${p.ro}deg;--k:${p.s.toFixed(3)}""", """;rotate:${p.ro}deg;--k:${p.k.toFixed(3)}""")
rep("""const KIND={bfly:['fl',33,1],bfly2:['fl',33,1],bee:['bz',28,1],lady:['cr',24],squir:['hp',36],ffly:['ff',19,2],snail:['cr mv-sn',27],
    frog:['hp',32],dfly:['df',35,1],duckl:['wd',31],bunny:['hp',35],peng:['wd',33],robin:['hp',29],mouse:['ms',33],top:['tp',29,2],wduck:['wd',32]};""",
    """const KIND={bfly:['fl',44,1],bfly2:['fl',44,1],bee:['bz',40,1],lady:['cr',34],squir:['hp',50],ffly:['ff',19,2],snail:['sl',38],
    frog:['hp',44],dfly:['df',46,1],duckl:['wd',42],bunny:['hp',48],peng:['wd',44],robin:['hp',42],mouse:['ms',42],top:['tp',38],wduck:['wd',44]};""")
rep("""const MV={fl:[.46,.62,.68,0],""", """const MV={sl:[.25,.6,0,0],fl:[.46,.62,.68,0],""")
# the critter element: bee and dragonfly carry their wings apart
rep("""return `<i class="lf-c mv-${mv} lf-s-${k}${air===1?' lf-air':air?'':' lf-gr'}${gold?' lf-gold':''}" """,
    """return `<i class="lf-c mv-${mv} lf-s-${k}${air===1?' lf-air':air?'':' lf-gr'}${gold?' lf-gold':''}${CR_WB.has(k)?' lf-wb':''}" """)
crit = json.load(open('/home/claude/pq/build/crit.json'))
cr = {k: 'data:image/webp;base64,' + v[0] for k, v in crit.items()}
# peeking heads and the jumping fish use the same Canva toys
cr['cat'] = cr.pop('cath'); cr['sqh'] = cr.pop('sqh2')
wb = {k: cr.pop(k) for k in ('bee-w', 'bee-b', 'dfly-w', 'dfly-b')}
rep("""   const st=document.createElement('style');st.textContent=css;document.head.appendChild(st)}""",
    """   /* the critters and the peeking heads are Canva toys (the drawings above stay as the fallback); the bee and the dragonfly beat their wings */
   for(const k in CR)css+=`.lf-c.lf-s-${k}>b,.lf-1.lf-s-${k}{background-image:url("${CR[k]}")}`;
   for(const k of CR_WB)css+=`.lf-wb.lf-s-${k}>b::before{background-image:url("${CR_W[k+'-w']}")}.lf-wb.lf-s-${k}>b::after{background-image:url("${CR_W[k+'-b']}")}`;
   const st=document.createElement('style');st.textContent=css;document.head.appendChild(st)}""")
rep("""  const ART={ // [viewBox, drawing]; critters facing right when seen from the side, head up when seen from above""",
    "  const CR=" + json.dumps(cr, separators=(',', ':')) + ";\n  const CR_W=" + json.dumps(wb, separators=(',', ':')) + ";\n  const CR_WB=new Set(['bee','dfly']);\n"
    """  const ART={ // [viewBox, drawing]; critters facing right when seen from the side, head up when seen from above""")

open(OUT, 'w').write(s)
print('ok', len(s))

# ================= shop v2 =================
s = open(OUT).read()
def rep2(old, new, n=1):
    global s
    c = s.count(old); assert c == n, (c, old[:100]); s = s.replace(old, new)
a = s.index('<div class="sheet shop" id="s-shop" hidden>'); b = s.index('<script>', a)
s = s[:a] + open('/home/claude/pq/src/shop.html').read() + '\n' + s[b:]
rep2('/* ===== end of fx css D ===== */', open('/home/claude/pq/src/shop.css').read() + '\n/* ===== end of fx css D ===== */')
a = s.index('const UPN={'); b = s.index('function resume(){')
s = s[:a] + open('/home/claude/pq/src/shop.js').read() + s[b:]
for old in ["$('sh-list').addEventListener('click',e=>{const b=e.target.closest('.ucard');if(b)buy(b.dataset.k)});\n",
            "$('sh-deck').addEventListener('click',e=>{const b=e.target.closest('.ucard');if(b)buy(b.dataset.k)});\n",
            "$('tab-up').addEventListener('click',()=>{shopTab='up';renderTab(true)});\n",
            "$('tab-deck').addEventListener('click',()=>{shopTab='deck';renderTab(true)});\n",
            "$('tab-gear').addEventListener('click',()=>{shopTab='gear';renderTab(true)});\n",
            "$('tab-skill').addEventListener('click',()=>{shopTab='skill';renderTab(true)});\n",
            "$('sh-skill').addEventListener('click',e=>{const b=e.target.closest('.kcard');if(b)tapSkillShop(b.dataset.s)});\n"]:
    rep2(old, '')
a = s.index("$('sh-gear').addEventListener('click',"); b = s.index('\n', a)
s = s[:a] + s[b+1:]
rep2("$('sh-go').addEventListener('click',()=>{if(run)resume();else newRun()});\n$('sh-back').addEventListener('click',showTitle);",
r"""$('sh-go').addEventListener('click',()=>{leaveShop();if(run)resume();else newRun()});
$('sh-back').addEventListener('click',()=>{leaveShop();showTitle()});
$('sh-body').addEventListener('click',e=>{ // the list only chooses; the pinned paper's button acts
  const sl=e.target.closest('[data-slot]');if(sl){swap=null;gearSlot=sl.dataset.slot;shopSel.gear=null;renderShop();return}
  const pg=e.target.closest('[data-peg]');
  if(pg){const j=+pg.dataset.peg,eq=meta.sk.eq;
    if(swap){const o=eq.indexOf(swap);if(o>=0)eq[o]=null;eq[j]=swap;shopSel.skill=swap;swap=null;saveMeta();renderShop();const p=$('sh-body').querySelector(`[data-peg="${j}"]`);if(p)p.classList.add('got');return}
    if(eq[j])choose(eq[j]);return}
  const b=e.target.closest('[data-k],[data-g],[data-s]');if(!b)return;
  if(swap){swap=null;renderShop()}
  choose(b.dataset.k||b.dataset.g||b.dataset.s);
});
$('sh-det').addEventListener('click',e=>{const b=e.target.closest('[data-act]');if(b&&!b.disabled)shopAct(b.dataset.act)});
['up','gear','skill','deck'].forEach(t=>$('tab-'+t).addEventListener('click',()=>setShopTab(t)));
$('t-shop').addEventListener('click',()=>showShop());""")
rep2('<i class="dot" id="o-dot" hidden></i>', '<i class="mk" id="o-dot" hidden></i>')
rep2('<button class="btn main play" id="t-new" type="button">あそぶ</button>',
     '<button class="btn main play" id="t-new" type="button">あそぶ</button>\n      <div class="t-sub"><button class="ibtn" id="t-shop" type="button" aria-label="強化"><span id="t-shop-i"></span><span>強化</span><i class="mk" id="t-dot" hidden></i></button></div>')
rep2("  $('t-best').innerHTML=meta.far?`${ico(SPR.flag)}<b>${meta.far}</b>`:'';",
     "  $('t-best').innerHTML=meta.far?`${ico(SPR.flag)}<b>${meta.far}</b>`:'';\n  $('t-shop-i').innerHTML=ico(ICON_UP_F());$('t-dot').hidden=!affordable();")
open(OUT, 'w').write(s)
print('shop ok', len(s))

# ================= play screen: shelf with skills and the die, six sockets, placement ghosts, the reward shelf =================
s = open(OUT).read()
def rep3(old, new, n=1):
    global s
    c = s.count(old); assert c == n, (c, old[:120]); s = s.replace(old, new)
# markup: the drawer leaves the field; the skill note takes its place; the tray holds skills, the die and the hand
a = s.index('    <div class="drawer" id="drawer">'); b = s.index('  </div>\n  <div class="tray">', a)
s = s[:a] + '    <div class="skn" id="skbar" hidden></div>\n' + s[b:]
rep3('<div class="tray">\n    <div class="hand" id="hand"></div>\n  </div>',
'''<div class="tray">
    <div class="kit" id="drawer-in">
      <button class="skill none" type="button" data-k="0">空き</button>
      <button class="skill none" type="button" data-k="1">空き</button>
      <button class="skill none" type="button" data-k="2">空き</button>
      <button class="dice" id="roll" type="button" aria-label="リロール：手持ちを全部引き直す"><span id="rollicon"></span><b id="rolln">3</b></button>
    </div>
    <div class="hand" id="hand"></div>
  </div>''')
rep3("const drawer=$('drawer'),drawerIn=$('drawer-in'),pullBtn=$('pull');", "const drawerIn=$('drawer-in'),drawer=drawerIn,pullBtn=document.createElement('button');")
rep3('''function setDrawer(open,auto){
  clearTimeout(drawerTimer);
  if(!open&&aim){aim=null;hideSay();if(run)renderHand()}
  drawerOpen=open;drawerAuto=open&&!!auto;
  drawer.classList.toggle('open',open);pullBtn.setAttribute('aria-expanded',open);drawerIn.inert=!open;
}''', '''function setDrawer(open,auto){ // the skills are always on the shelf now: at a dead end the ones that can help bounce
  clearTimeout(drawerTimer);drawerOpen=open;drawerAuto=open&&!!auto;drawerIn.classList.toggle('stuck',drawerOpen);
}
const PIPS={1:[[50,50]],2:[[30,30],[70,70]],3:[[28,28],[50,50],[72,72]],4:[[30,30],[70,30],[30,70],[70,70]],5:[[28,28],[72,28],[50,50],[28,72],[72,72]],6:[[30,27],[70,27],[30,50],[70,50],[30,73],[70,73]]};
function diceFace(n){ // the die shows as many pips as rerolls are left
  const p=PIPS[Math.min(6,n)]||[];
  $('rollicon').innerHTML=svg('<rect x="7" y="12" width="86" height="82" rx="13" fill="#e9d6c4"/><rect x="7" y="6" width="86" height="82" rx="13" fill="#fff" stroke="#d8c1a6" stroke-width="2.5"/>'+p.map(([x,y])=>`<circle cx="${x}" cy="${y-3}" r="8.5" fill="#e23c56"/><circle cx="${x-2.4}" cy="${y-5.4}" r="2.6" fill="#ff9db4"/>`).join(''));
  const b=$('rolln');b.textContent=n;b.className=n>6?'more':'';
}''')
rep3("$('rolln').textContent=run.rolls;$('pulln').textContent=run.rolls;pullBtn.classList.toggle('out',run.rolls<=0);", "diceFace(run.rolls);")
# skills: a tap chooses and pins a note; instant ones fire from the note's button, aimed ones from their target
a = s.index('function renderSkills(){'); b = s.index('function tickSkills(){')
s = s[:a] + r'''function renderSkills(){
  skillEls.forEach((b,k)=>{
    const s=run.sk&&run.sk[k],d=s&&SKILL_ID[s.id];
    if(!d){b.className='skill none';b.textContent='空き';b.setAttribute('aria-label','スキルの空き枠（強化のスキルでセット）');b.dataset.rest='';return}
    const rest=s.cd>0,full=Math.max(1,d.ct-qv('cdr')),was=b.dataset.rest==='1';b.dataset.rest=rest?'1':'0';
    b.className='skill'+(rest?' rest':' can')+(pick===k?' on':'')+(!rest&&was&&!REDUCED?' ready':'');
    b.innerHTML=`<span class="sk-ic">${svg(SK_ART[d.id])}${rest?`<i class="sk-rest" style="--p:${Math.min(1,s.cd/full).toFixed(3)}"><b>${s.cd}</b></i>`:''}</span><span class="sk-n">${d.n}</span>`;
    b.setAttribute('aria-label',`${d.n}：${d.d}`+(rest?`（あと${s.cd}マスで使える）`:''));
  });
  hero.classList.toggle('pow',FX().wind>0);hero.classList.toggle('guard',!!FX().guard);hero.classList.toggle('psn',!!(run.pz&&run.pz.n>0));
}
let pick=-1; // the skill whose note is pinned
function hidePick(){pick=-1;const el=$('skbar');if(el)el.hidden=true}
function closePick(){aim=null;hidePick();if(run)render()}
function showPick(k,note){
  const s=run.sk[k],d=SKILL_ID[s.id],el=$('skbar');
  let line,btns='<button class="sb-x" type="button" data-sb="x">やめる</button>';
  if(s.cd>0){line=`あと${s.cd}マス歩くと使える`;btns='<button class="sb-x" type="button" data-sb="x">とじる</button>'}
  else if(note)line=note;
  else if(d.aim)line=`<span class="do">${AIM_SAY[d.id]}</span>`;
  else{line=d.d;btns+='<button class="sb-go" type="button" data-sb="go">使う</button>'}
  el.innerHTML=`<span class="sb-ic">${svg(SK_ART[d.id])}</span><div class="sb-t"><b>${d.n}</b>${line.startsWith('<span')?line:`<span>${line}</span>`}</div><div class="sb-b">${btns}</div>`;
  el.hidden=false;
}
''' + s[b:]
rep3("function hideSay(){clearTimeout(sayT);$('say').hidden=true}", "function hideSay(){clearTimeout(sayT);$('say').hidden=true;hidePick()}")
a = s.index('const AIM_SAY='); b = s.index('\n', a)
s = s[:a] + "const AIM_SAY={turn:'回す積み木をえらぶ',cross:'十字にする積み木をえらぶ',clear:'どかす物を盤でえらぶ',bugle:'追い出す敵の積み木をえらぶ',treasure:'装備をのせる積み木をえらぶ'};" + s[b:]
a = s.index('function tapSkill(k){'); b = s.index('const dealFx=')
s = s[:a] + r'''function tapSkill(k){
  if(busy||!run||run.phase!=='build')return;
  const s=run.sk&&run.sk[k],d=s&&SKILL_ID[s.id];if(!d)return;
  if(pick===k)return closePick(); // the same skill again: never mind
  aim=null;pick=k;sel=-1;let note='';
  if(s.cd<=0&&d.aim){if(targets(d.aim).length)aim={k,kind:d.aim};else note=NO_AIM[d.aim]}
  render();showPick(k,note);
}
''' + s[b:]
rep3("  const s=run.sk[k],d=SKILL_ID[s.id],lv=lvOf(rowOf(run.at));\n  aim=null;", "  const s=run.sk[k],d=SKILL_ID[s.id],lv=lvOf(rowOf(run.at));\n  aim=null;hidePick();")
rep3("  if(aim){if(aim.kind!=='rock'&&targets(aim.kind).includes(i))useSkill(aim.k,i);else flashSlot(i);return}",
     "  if(aim){if(aim.kind!=='rock'&&targets(aim.kind).includes(i))useSkill(aim.k,i);else flashSlot(i);return}\n  if(pick>=0)hidePick();")
rep3("  if(aim){if(aim.kind==='rock'&&targets('rock').includes(i))useSkill(aim.k,i);else{aim=null;hideSay();render()}return}",
     "  if(aim){if(aim.kind==='rock'&&targets('rock').includes(i))useSkill(aim.k,i);else closePick();return}\n  if(pick>=0)return closePick();")
s = s.replace("drawerIn.addEventListener('click',e=>{const b=e.target.closest('.skill');if(b)tapSkill(+b.dataset.k)});",
 "drawerIn.addEventListener('click',e=>{const b=e.target.closest('.skill');if(b)tapSkill(+b.dataset.k)});\n$('skbar').addEventListener('click',e=>{const b=e.target.closest('[data-sb]');if(!b)return;if(b.dataset.sb==='go'&&pick>=0)useSkill(pick,-1);else closePick()});")
assert "$('skbar').addEventListener" in s
# the hand: six sockets, each block with a plain label under it
a = s.index("  handEl.innerHTML=run.hand.map((t,i)=>t?"); b = s.index('\n', a)
old = s[a:b]
new = old.replace('${svg(tileArt(t,true))}${badge(t.e)}${t.e&&t.e.psn?\'<span class="pz">毒</span>\':\'\'}</div>`',
                  '<span class="blk">${svg(tileArt(t,true))}</span>${slotLabel(t)}</div>`')
new = new.replace(".join('');", ".join('')+'<div class=\"slot lock\" aria-hidden=\"true\"></div>'.repeat(Math.max(0,6-run.hand.length));")
assert new != old and 'slotLabel' in new and 'slot lock' in new
s = s[:a] + new + s[b:]
rep3("function renderHand(F){", r'''function slotLabel(t){ // under each block, what it carries: the hp its toy will cost, the coins, the candy, the gear
  const e=t.e;let c='',h='';
  if(e&&e.k==='foe'){c=' foe';h=`${ico(SPR.heart)}-${nf(dmgFor(e))}`+(e.psn?' 毒':'')}
  else if(e&&e.k==='coin'){c=' coin';h=`${ico(SPR.coin)}+${e.v}`}
  else if(e&&e.k==='potion'){c=' heal';h=`${ico(SPR.heart)}+${e.v}`}
  else if(e){const g=gearOf(e);if(g){if(owned(g.id)){c=' coin';h=`${ico(SPR.coin)}+${gainOf(dupGold(g))}`}else{c=' new';h='<b>NEW</b>'}}}
  return `<span class="lbl${c}">${h}</span>`;
}
function renderHand(F){''')
# the panels the held block fits show a faint copy of it
rep3("    if(F&&F.has(i)){cls+=' front'+(sel>=0&&fits(run.hand[sel],i,F)?' fit':'');",
     "    if(F&&F.has(i)){const ok=sel>=0&&fits(run.hand[sel],i,F);cls+=' front'+(ok?' fit':'');if(ok)inner+=`<div class=\"gh\">${svg(tileArt(run.hand[sel],false))}</div>`;")
a = s.index('function refreshMarks(){'); b = s.index('function updateCell(')
s = s[:a] + r'''function refreshMarks(){
  const F=frontier(),t=sel>=0&&run.hand[sel];
  board.classList.toggle('holding',!!t);
  for(const [j] of F){const el=elOf(j);if(!el)continue;const ok=!!t&&fits(t,j,F);el.classList.toggle('fit',ok);
    const g=el.querySelector(':scope>.gh');if(g)g.remove();if(ok)el.insertAdjacentHTML('beforeend',`<div class="gh">${svg(tileArt(t,false))}</div>`)}
}
''' + s[b:]
rep3("  board.innerHTML=h;board.appendChild(hero);justPlaced=-1;", "  board.innerHTML=h;board.appendChild(hero);justPlaced=-1;board.classList.toggle('holding',sel>=0);")
# the reward shelf
rep3('<p class="rw-info" id="r-info" aria-live="polite"></p>', '<p class="rw-info" id="r-info" aria-live="polite"></p>\n    <button class="rw-go" id="r-go" type="button" disabled>えらんでね</button>')
a = s.index("  $('r-list').innerHTML=run.rewards.map((x,i)=>"); b = s.index('\n', a)
s = s[:a] + r'''  const TAG={heal:'回復',gold:'金貨',roll:'リロール',maxhp:'体力',atk:'攻撃',def:'守り',evo:'大進化',allup:'おもちゃ箱'};
  $('r-list').innerHTML=run.rewards.map((x,i)=>{
    const it=x.k==='it',tag=it?(x.w?'武器':'お守り'):TAG[x.k]||(pw?'次元のちから':'');
    const v=it?(x.lv===1?'<em class="rr-v nw">NEW</em>':`<em class="rr-v">Lv${x.lv-1}→${x.lv}</em>`):typeof x.v==='string'?`<em class="rr-v">${x.v}</em>`:'';
    const d=it?itDesc(x.id,x.lv):(x.s||'');const h=it?evoHint(IT_ID[x.id]).replace(/^（|）$/g,''):'';
    return `<button class="rrow k-${x.kd||'gold'}${x.evo?' evo':''}" type="button" data-i="${i}" style="--n:${i};--r:${i%2?-7:6}deg" aria-label="${x.n||x.t}：${d}"><span class="rr-art">${x.art?svg(x.art):ico(x.gi||SPR[x.icon])}</span><span class="rr-main"><span class="rr-top">${tag?`<i class="rr-tag">${tag}</i>`:''}<b class="rr-name">${x.n||x.t}</b>${v}</span><span class="rr-d">${d}</span>${h?`<span class="rr-h">${h}</span>`:''}</span></button>`}).join('');
  rPick=-1;rReady=performance.now()+(REDUCED?0:550);$('r-go').disabled=true;$('r-go').textContent='えらんでね';$('r-list').classList.remove('has','picked');''' + s[b:]
a = s.index("$('r-list').addEventListener('click',e=>{"); b = s.index("});\n", a) + 4
s = s[:a] + r'''let rPick=-1,rReady=0;
function rewardTarget(x){ // the slot of the toy box the chosen toy goes into
  const inv=$('r-inv');if(!x||x.k!=='it'||!inv)return null;
  const g=[...inv.querySelectorAll('.ig')][x.w?0:1];if(!g)return null;
  const own=itOwned(x.w),j=own.findIndex(y=>y.id===x.id);return g.querySelectorAll('i')[j>=0?j:own.length]||null;
}
$('r-list').addEventListener('click',e=>{ // a tap chooses; the sign below takes it
  const b=e.target.closest('.rrow'),L=$('r-list');if(!b||L.classList.contains('picked'))return;
  rPick=+b.dataset.i;L.classList.add('has');L.querySelectorAll('.rrow').forEach(r=>r.classList.toggle('on',r===b));
  document.querySelectorAll('#r-inv i.tgt').forEach(i=>i.classList.remove('tgt'));const t=rewardTarget(run.rewards[rPick]);if(t)t.classList.add('tgt');
  const go=$('r-go');go.disabled=false;go.textContent='これにする';
});
$('r-go').addEventListener('click',()=>{
  const L=$('r-list');if(rPick<0||performance.now()<rReady||L.classList.contains('picked'))return;
  const i=rPick,x=run.rewards[i],b=L.querySelector(`.rrow[data-i="${i}"]`);L.classList.add('picked');$('r-go').disabled=true;
  L.querySelectorAll('.rrow').forEach(r=>r.classList.add(r===b?'take':'fall'));
  const t=rewardTarget(x),art=b&&b.querySelector('.rr-art');
  if(t&&art&&!REDUCED){fly(art,SPR['i_'+x.id]||SPR.coin,t);setTimeout(()=>{t.classList.remove('tgt');t.insertAdjacentHTML('beforeend',`<em class="stamp">${x.lv===1?'NEW':'Lv'+x.lv}</em>`)},380)}
  else if(b){const a=mid(b);if(a)bits(a.x,a.y,16,['#ffe58a','#fff','#ff9ec7','#a8e6ff'],a.w*.6,5)}
  setTimeout(()=>takeReward(i),REDUCED?0:720);
});
''' + s[b:]
# the toy box shows two labelled groups: weapons | charms
a = s.index("  const row=(w,n)=>{const a=itOwned(w);return a.map(chip).join('')+'<i class=\"empty\"></i>'.repeat(Math.max(0,n-a.length))};"); b = s.index('\n', a)
b2 = s.index('\n', b+1)
s = s[:a] + "  const row=(w,n)=>{const a=itOwned(w);return a.map(chip).join('')+'<i class=\"empty\"></i>'.repeat(Math.max(0,n-a.length))};\n  el.innerHTML=`<span class=\"ig\"><small>武器</small><span class=\"ig-row\">${row(1,SLOT_W)}</span></span><span class=\"sep\"></span><span class=\"ig\"><small>お守り</small><span class=\"ig-row\">${row(0,SLOT_C)}</span></span>`;" + s[b2:]
s = s.replace('/* ===== end of fx css D ===== */', open('/home/claude/pq/src/play.css').read() + '\n.slot .lbl svg{position:static;inset:auto}\n.slot.ace:not(.dull){filter:none}\n/* ===== end of fx css D ===== */', 1)
open(OUT, 'w').write(s)
print('play ok', len(s))

# ================= Canva icons for the skills and the reward toys =================
s = open(OUT).read()
ic = open('/home/claude/pq/build/icons.html').read()
k = s.index('<!--/ART-->'); s = s[:k] + ic + '\n' + s[k:]
a = s.index('const SK_ART={'); b = s.index('\n};', a) + 3
s = s[:b] + "\nif(HAS_ART&&document.getElementById('a-sk_turn')){ // the Canva pictures: each shows what the skill does\n  for(const id in SK_ART)if(document.getElementById('a-sk_'+id))SK_ART[id]=U('sk_'+id,4,4,92,92);\n  for(const x of ['plane','top','bomb','boomer','bubble','spring','block','cookie','clover','honey','cat','dice','clock'])if(document.getElementById('a-it_'+x))SPR['i_'+x]=U('it_'+x,24,24,52,52);\n}" + s[b:]
open(OUT, 'w').write(s)
print('icons ok', len(s))
s = open(OUT).read()
s = s.replace("if(/fxtest/.test(location.hash))window.PQ={get run(){return run},FXH,", "if(/fxtest/.test(location.hash))window.PQ={get run(){return run},FXH,openReward,showShop,", 1)
assert 'openReward,showShop,' in s
open(OUT, 'w').write(s)
# toys on a block in the hand sit small in its corner so the road shows; reward tags tell weapons from charms
s = open(OUT).read()
def rep4(old, new, n=1):
    global s
    c = s.count(old); assert c == n, (c, old[:120]); s = s.replace(old, new)
rep4("+evSVG(t.e,at)+(ace?", "+(inTray&&t.e&&t.e.k==='foe'?`<g transform=\"translate(70 30) scale(.5) translate(-50 -50)\"><circle cx=\"50\" cy=\"58\" r=\"34\" fill=\"#fffaf0\" stroke=\"#6b4a3a\" stroke-width=\"5\"/><g transform=\"translate(50 54) scale(.72) translate(-50 -50)\">${SPR[t.e.t]||SPR.soldier}</g></g>`:evSVG(t.e,at))+(ace?")
rep4("${tag?`<i class=\"rr-tag\">${tag}</i>`:''}", "${tag?`<i class=\"rr-tag${it&&!x.w?' ch':''}\">${tag}</i>`:''}")
open(OUT, 'w').write(s)
