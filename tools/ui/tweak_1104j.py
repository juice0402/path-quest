# 11/4 その10：tweak_1104i.py のあとの index.html に1回だけ当てる
#  敵のくわしい情報は、敵をタップしたときの紙（スキルと同じ紙）に1つにまとめる。盤の上の札（大将の札も）はなくす
#  紙：敵の絵・名前・攻撃とHP（Canva の剣とハート）・2行目にひとこと（立っている敵は何をするか、道の敵と大将は戦うと減るHP）・［とじる］
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()

def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80]); s = s.replace(a, b)

# ---------- no tags on the board ----------
i = s.index('\n/* the attack and life tags of the toys on the field: one layer over the panels')
j = s.index("FXH.add('update',({i})=>{if(!TAGS.layer", i); j = s.index('\n', j) + 1
s = s[:i] + '\n' + s[j:]
rep('''/* the tag layer: over the panels and the knight, under the flying critters */
.tagl{position:absolute;left:0;top:0;width:100%;height:0;z-index:3;pointer-events:none}
.tagl .tg{position:absolute}
''', '')
rep("</g>`)+`${foeTags(c.foe)}`;tab=", "</g>`);tab=")
rep("  if(e.k==='foe')return foeTags(e);", "  if(e.k==='foe')return ''; // a toy's numbers are on its paper (tap it)")

# ---------- the paper of a toy ----------
rep("let pick=-1; // the skill whose note is pinned\nfunction hidePick(){pick=-1;const el=$('skbar');if(el)el.hidden=true}",
'''let pick=-1; // the skill whose note is pinned
let fpick=-1;const fsel=new Set(); // the toy whose paper is open, and its panels (the captain has four)
function hidePick(){pick=-1;if(fpick>=0||fsel.size){fpick=-1;fsel.clear();document.querySelectorAll('.cell.fsel').forEach(x=>x.classList.remove('fsel'))}const el=$('skbar');if(el)el.hidden=true}
function foeAt(i){ // the toy a tap on this panel means: one standing here, one riding a block, or the captain of this square
  const c=cellAt(i);if(!c)return null;if(c.foe)return c.foe;
  const t=c.tile;if(!t)return null;
  if(t.pz){const h=cellAt(t.bi),e=h&&h.tile&&h.tile.e;return e&&e.k==='foe'?e:null}
  return t.e&&t.e.k==='foe'?t.e:null;
}
const FOE_DO={archer:r=>`${r}マス以内に矢をうつ`,mage:r=>`${r}マス以内に魔法（守りは効かない）`,clown:()=>'近くに毒の水たまりをまく',mason:()=>'近くにかべを作る'};
function showFoe(i,e){
  hidePick();fpick=i;const c=cellAt(i),pz=c.tile&&c.tile.pz;(pz||[i]).forEach(x=>{fsel.add(x);const el=elOf(x);if(el)el.classList.add('fsel')});
  const hp=x=>`<i class="st-h"><b class="ic"></b>${x}</i>`;
  let what;
  if(c.foe){const s=SHOOTERS[e.t];what=s&&FOE_DO[e.t]?FOE_DO[e.t](s.rng):'道をふさいでいる'}
  else{const d=dmgFor(e);what=d?`<span class="fd-c">戦うと${hp('-'+nf(d))}</span>`:'戦ってもダメージなし'}
  const el=$('skbar');
  el.innerHTML=`<span class="sb-ic fd-ic${e.boss||e.king?'':' sm'}">${svg(SPR[e.t]||SPR.soldier)}</span><div class="sb-t"><b><span class="fd-n">${e.name}</span><span class="fd-st"><i class="st-a"><b class="ic"></b>${nf(e.atk)}</i>${hp(nf(e.hp))}</span></b><span>${what}</span></div><div class="sb-b"><button class="sb-x" type="button" data-sb="x">とじる</button></div>`;
  el.hidden=false;
}
FXH.cells.push(i=>fsel.has(i)?{cls:'fsel'}:null);''')
rep("  const s=run.sk[k],d=SKILL_ID[s.id],el=$('skbar');", "  if(fpick>=0){fpick=-1;fsel.clear();document.querySelectorAll('.cell.fsel').forEach(x=>x.classList.remove('fsel'))}\n  const s=run.sk[k],d=SKILL_ID[s.id],el=$('skbar');")
rep("  if(pick>=0)hidePick();\n  const t=run.hand[i];if(!t)return;", "  if(pick>=0||fpick>=0)hidePick();\n  const t=run.hand[i];if(!t)return;")
rep('''  if(pick>=0)return closePick();
  if(sel<0){if(frontier().has(i))hop();return}
  place(i,sel);''', '''  if(pick>=0)return closePick();
  const e=foeAt(i),F=frontier();
  if(e&&!(sel>=0&&fits(run.hand[sel],i,F))){if(fpick>=0&&fsel.has(i))return hidePick();return showFoe(i,e)} // a toy: its paper (again: closed)
  if(fpick>=0)hidePick();
  if(sel<0){if(F.has(i))hop();return}
  place(i,sel);''')
rep("function place(j,hi){\n  if(busy||!run||run.phase!=='build')return;", "function place(j,hi){\n  if(busy||!run||run.phase!=='build')return;\n  if(fpick>=0)hidePick();")

CSS = '''/* the paper of a toy (tap it): its picture, name, attack and life, and one line of what it does */
.skn .fd-ic svg{overflow:visible}
.skn .fd-ic.sm svg{transform:scale(1.3);transform-origin:50% 80%}
.skn .sb-t b .fd-n{display:inline;margin:0;font:inherit;color:inherit;vertical-align:middle}
.skn .sb-t .fd-st{display:inline-flex;align-items:center;gap:9px;margin:0 0 0 10px;vertical-align:middle;font:800 15px/1 var(--round);font-variant-numeric:tabular-nums}
.skn .fd-st i,.skn .fd-c i{display:inline-flex;align-items:center;gap:2px;font-style:normal}
.skn .fd-st .ic,.skn .fd-c .ic{flex:none;display:inline-block;width:16px;height:16px;background:var(--ui-ic-atk) center/contain no-repeat}
.skn .fd-st .st-h .ic,.skn .fd-c .ic{background-image:var(--ui-ic-hp)}
.skn .fd-st .st-a{color:#5a3826}.skn .fd-st .st-h,.skn .fd-c{color:#d42a48}
.skn .sb-t .fd-c{display:inline-flex;align-items:center;gap:4px;margin:0;font:800 13px/1.3 var(--round)}
.cell.fsel{outline:3px solid #fff8e8;outline-offset:-3px}
.bboss .bb-tag{display:none}
'''
rep('/* ===== end of 11/4 ===== */', CSS + '/* ===== end of 11/4 ===== */')
# the old tag maker is not used any more
i = s.index("function foeTags(e){"); j = s.index("function badge(e){", i); s = s[:i] + s[j:]
rep(".board>.cell .b-st{display:none}\n", "")
open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
