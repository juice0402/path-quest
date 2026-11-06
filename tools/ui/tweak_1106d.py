"""11/6 d: the moving parts of the treasures and the toys get their own boxes (lighter fights on phones).

しょーくん「戦闘は派手なほうがいいから、2がいいかもしれないね」（見た目そのままで、宝物と敵の動かし方を作りかえる）
「ほんの少しのちがいならOK」

Why: the loops that move a part *inside* a cell's <svg> (a treasure bobbing, its shadow, its glow, the two sparkles,
the sparkles of the cross block, a toy waiting, a toy popping up) make the browser lay out and paint that svg again on
every frame where anything else changes — and in a fight that is almost every frame.
Now those parts are drawn in boxes of their own, over the picture:
- the generators mark a moving part with <lx c="classes" s="style" sp="1" m="svg transform">content</lx>
  (LOOT, the cross block's stars in tileArt0, the toy in TOYG/standArt).
- svgx(content) (cell pictures and the hand's blocks) takes the marked parts out of the svg and puts each into
  <div class="lxw"> right after the picture: <i class="lxp <classes>"> placed on the part's own bounding box (measured
  once per drawing with getBBox, the same box the old transform-box:fill-box used), holding an <svg> whose viewBox is
  that box. So the same CSS (.loot, .tw, .lsh, .lglow, .toy.t-…, .spawn) moves the same box the same way.
  A toy's lean/scale (standArt) becomes a CSS transform on <i class="lxm"> (the same numbers; 1 unit = 1%).
- svg(content) everywhere else (papers, rewards, the ghost block, the hand's preview) puts the parts back inline as <g>,
  so those look and move exactly as before.
- a cell's whole-picture effects also move the boxes: the "placed" thump (.cell.new), the hit shake (struck), the poke.
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


# the helpers, next to svg()
sub('const svg=s=>`<svg viewBox="0 0 100 100" aria-hidden="true">${s}</svg>`;',
    'const svg=s=>`<svg viewBox="0 0 100 100" aria-hidden="true">${unlx(s)}</svg>`;\n'
    '/* 11/6: moving parts (treasure, sparkles, toys) are marked <lx>; svgx() gives them boxes of their own over the picture, svg() keeps them inline */\n'
    'function LX(c,inner,st,sp){return `<lx c="${c}"${st?` s="${st}"`:\'\'}${sp?\' sp="1"\':\'\'}>${inner}</lx>`}\n'
    'function lxA(a){const o={};a.replace(/(\\w+)="([^"]*)"/g,(_,k,v)=>{o[k]=v});return o}\n'
    'function lxInline(a,inner){const o=lxA(a);let g=`<g class="${o.c}"${o.s?` style="${o.s}"`:\'\'}>${inner}</g>`;if(o.sp)g=`<g class="spawn">${g}</g>`;if(o.m)g=`<g transform="${o.m}">${g}</g>`;return g}\n'
    'function unlx(s){return typeof s===\'string\'&&s.indexOf(\'<lx \')>=0?s.replace(/<lx ([^>]*)>([\\s\\S]*?)<\\/lx>/g,(_,a,inner)=>lxInline(a,inner)):s}\n'
    'const LXB=new Map();let lxMs=null;\n'
    'function lxBox(h){ /* the part\'s own bounding box (what transform-box:fill-box used), measured once per drawing */\n'
    '  if(LXB.has(h))return LXB.get(h);\n'
    '  if(!lxMs){lxMs=document.createElementNS(\'http://www.w3.org/2000/svg\',\'svg\');lxMs.setAttribute(\'width\',\'0\');lxMs.setAttribute(\'height\',\'0\');lxMs.setAttribute(\'aria-hidden\',\'true\');lxMs.style.cssText=\'position:absolute;left:0;top:0;visibility:hidden;pointer-events:none\';lxMs.appendChild(document.createElementNS(\'http://www.w3.org/2000/svg\',\'g\'));document.body.appendChild(lxMs)}\n'
    '  const g=lxMs.firstChild;let r=null;try{g.innerHTML=h;const q=g.getBBox();if(q.width>0&&q.height>0)r={x:+q.x.toFixed(3),y:+q.y.toFixed(3),w:+q.width.toFixed(3),h:+q.height.toFixed(3)}}catch(e){}\n'
    '  g.innerHTML=\'\';LXB.set(h,r);return r;\n'
    '}\n'
    'function cssT(m){return m.replace(/translate\\(([-\\d.e]+)[ ,]+([-\\d.e]+)\\)/g,\'translate($1%,$2%)\').replace(/(skewX|skewY|rotate)\\(([-\\d.e]+)\\)/g,\'$1($2deg)\').replace(/scale\\(([-\\d.e]+)[ ,]+([-\\d.e]+)\\)/g,\'scale($1,$2)\')}\n'
    'function svgx(s){\n'
    '  if(typeof s!==\'string\'||s.indexOf(\'<lx \')<0)return svg(s);\n'
    '  const parts=[];\n'
    '  const main=s.replace(/<lx ([^>]*)>([\\s\\S]*?)<\\/lx>/g,(_,a,inner)=>{\n'
    '    const o=lxA(a),b=lxBox(inner);if(!b)return lxInline(a,inner);\n'
    '    const geo=`left:${b.x}%;top:${b.y}%;width:${b.w}%;height:${b.h}%`,sv=`<svg viewBox="${b.x} ${b.y} ${b.w} ${b.h}" preserveAspectRatio="none" aria-hidden="true">${inner}</svg>`;\n'
    '    let h=o.sp?`<i class="lxp spawn" style="${geo}"><i class="lxp ${o.c}" style="left:0;top:0;width:100%;height:100%${o.s?\';\'+o.s:\'\'}">${sv}</i></i>`:`<i class="lxp ${o.c}" style="${geo}${o.s?\';\'+o.s:\'\'}">${sv}</i>`;\n'
    '    if(o.m)h=`<i class="lxm" style="transform:${cssT(o.m)}">${h}</i>`;\n'
    '    parts.push(h);return \'\';\n'
    '  });\n'
    '  return svg(main)+(parts.length?`<div class="lxw" aria-hidden="true">${parts.join(\'\')}</div>`:\'\');\n'
    '}')

# the generators mark their moving parts
sub("(ace?`<g class=\"tw\">${STAR(86,12,9)}</g><g class=\"tw tw2\">${STAR(13,82,7)}</g>`:'')};",
    "(ace?LX('tw',STAR(86,12,9))+LX('tw tw2',STAR(13,82,7)):'')};")
sub("const LOOT=(s,i,glow)=>{const d=`style=\"--d:-${((i|0)*7%11)/10}s\"`;return `<ellipse class=\"lsh\" cx=\"50\" cy=\"79\" rx=\"15\" ry=\"3.6\" fill=\"rgba(60,30,46,.24)\" ${d}/>`+(glow?`<circle class=\"lglow\" cx=\"50\" cy=\"54\" r=\"23\" fill=\"#fff3a8\" ${d}/>`:'')+`<g class=\"loot\" ${d}>${s}</g><g class=\"tw\">${STAR(79,26,6)}</g><g class=\"tw tw2\">${STAR(23,68,4.5)}</g>`};",
    "const LOOT=(s,i,glow)=>{const d=`--d:-${((i|0)*7%11)/10}s`;return LX('lsh','<ellipse cx=\"50\" cy=\"79\" rx=\"15\" ry=\"3.6\" fill=\"rgba(60,30,46,.24)\"/>',d)+(glow?LX('lglow','<circle cx=\"50\" cy=\"54\" r=\"23\" fill=\"#fff3a8\"/>',d):'')+LX('loot',s,d)+LX('tw',STAR(79,26,6))+LX('tw tw2',STAR(23,68,4.5))};")
sub("const tileArt=(t,inTray,at)=>{const a0=tileArt0(t,inTray,at);return !t.sp?a0:(t.sp==='ghost'?`<g opacity=\".72\">${a0}</g>`:a0)+spIco(t.sp)};",
    "const tileArt=(t,inTray,at)=>{const a0=tileArt0(t,inTray,at);return !t.sp?a0:(t.sp==='ghost'?`<g opacity=\".72\">${unlx(a0)}</g>`:a0)+spIco(t.sp)};")
sub("const TOYG=(t,e)=>{const g=`<g class=\"toy t-${t}\">${SPR[t]||SPR.soldier}</g>`;if(!e||SEEN.has(e))return g;SEEN.add(e);SND('pon');return REDUCED?g:`<g class=\"spawn\">${g}</g>`};",
    "const TOYG=(t,e)=>{const a=SPR[t]||SPR.soldier;if(!e||SEEN.has(e))return LX('toy t-'+t,a);SEEN.add(e);SND('pon');return LX('toy t-'+t,a,'',!REDUCED)};")
sub("  return `<g transform=\"${CASTM(f)}\"><g transform=\"${g}\">${SHAD(art)}</g></g>`+(rx?CONTACT(f,rx):'')+`<g transform=\"${g}\">${art}</g>`;",
    "  const body=art.indexOf('<lx ')===0&&art.indexOf('<lx ',4)<0?art.replace('<lx ',`<lx m=\"${g}\" `):`<g transform=\"${g}\">${unlx(art)}</g>`; /* 11/6: a toy keeps its lean as the box's transform */\n"
    "  return `<g transform=\"${CASTM(f)}\"><g transform=\"${g}\">${SHAD(art)}</g></g>`+(rx?CONTACT(f,rx):'')+body;")

# the places that draw on the field and in the hand take the parts out
sub("inner=svg(deco(i)+(c.psn?SPR.psn:'')+(c.gem||c.coin?LOOT((c.gem?SPR.gem:'')+(c.coin?SPR.coin:''),i,1):''));",
    "inner=svgx(deco(i)+(c.psn?SPR.psn:'')+(c.gem||c.coin?LOOT((c.gem?SPR.gem:'')+(c.coin?SPR.coin:''),i,1):''));")
sub("inner=svg(HAS_ART?toyStand(i,c.foe.t,c.foe):`<g class=\"toy\">${SPR[c.foe.t]||SPR.soldier}</g>`);",
    "inner=svgx(HAS_ART?toyStand(i,c.foe.t,c.foe):`<g class=\"toy\">${SPR[c.foe.t]||SPR.soldier}</g>`);")
sub("inner=svg(tileArt(c.tile,false,i))", "inner=svgx(tileArt(c.tile,false,i))")
sub('<span class="blk">${svg(tileArt(t,true))}', '<span class="blk">${svgx(tileArt(t,true))}')

# whole-picture effects move the boxes too
sub("function struck(el){const s=el&&(el.querySelector(':scope>svg')||el.firstElementChild);if(s&&!REDUCED)s.animate([{transform:'none'},{transform:'translateX(7%)',filter:'brightness(1.35)'},{transform:'translateX(-7%)'},{transform:'none'}],{duration:220})}",
    "function struck(el){const s=el&&(el.querySelector(':scope>svg')||el.firstElementChild);if(s&&!REDUCED){const K=[{transform:'none'},{transform:'translateX(7%)',filter:'brightness(1.35)'},{transform:'translateX(-7%)'},{transform:'none'}];s.animate(K,{duration:220});const x=el.querySelector(':scope>.lxw');if(x&&x!==s)x.animate(K,{duration:220})}}")
sub("    const e=elOf(i),s=e&&e.querySelector(':scope>svg');if(s)s.animate([{transform:'none'},{transform:'translateY(5%) scale(1.04,.93)'},{transform:'translateY(-3%)'},{transform:'none'}],{duration:320,easing:'ease-out'});",
    "    const e=elOf(i);for(const s of e?[e.querySelector(':scope>svg'),e.querySelector(':scope>.lxw')]:[])if(s)s.animate([{transform:'none'},{transform:'translateY(5%) scale(1.04,.93)'},{transform:'translateY(-3%)'},{transform:'none'}],{duration:320,easing:'ease-out'});")

# CSS: the boxes
sub(".cell.new svg{transform-origin:50% 100%;animation:thunk .34s ease-out}",
    ".cell.new svg{transform-origin:50% 100%;animation:thunk .34s ease-out}"
    ".lxw{position:absolute;inset:0;pointer-events:none}.lxw .lxp,.lxw .lxm{position:absolute;display:block;pointer-events:none}"
    ".lxw .lxm{left:0;top:0;width:100%;height:100%;transform-origin:0 0}.lxw svg{overflow:visible;pointer-events:none}.lxw svg>*{pointer-events:visiblePainted}"
    ".cell.new>.lxw{transform-origin:50% 100%;animation:thunk .34s ease-out}.cell.new .lxw svg{animation:none}")
sub("  .cell.new svg,.pop,.hero.hurt svg{animation-duration:.01s}",
    "  .cell.new svg,.pop,.hero.hurt svg{animation-duration:.01s}\n  .cell.new>.lxw{animation-duration:.01s}")

P.write_text(s, encoding='utf-8')
print('ok')
