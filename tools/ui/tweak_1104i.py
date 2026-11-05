# 11/4 その9：tweak_1104h.py のあとの index.html に1回だけ当てる
#  敵の攻撃とHPの札は、マスの中ではなく盤の上の1枚の層にまとめて描く。下の段の家や敵の頭にかくれない
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()

def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80]); s = s.replace(a, b)

JS = r'''
/* the attack and life tags of the toys on the field: one layer over the panels, so a tall house or a toy's head below never hides them (11/4) */
const TAGS={layer:null};
function tagFoe(c){if(!c)return null;if(c.foe)return c.foe;const t=c.tile;return t&&!t.gate&&t.e&&t.e.k==='foe'?t.e:null}
function tagHTML(i){const e=tagFoe(cellAt(i)),el=e&&elOf(i);return el?`<div class="tg" data-i="${i}" style="left:${el.offsetLeft}px;top:${el.offsetTop}px;width:${el.offsetWidth}px;height:${el.offsetHeight}px">${foeTags(e)}</div>`:''}
function tagsAll(){
  if(!run)return;
  if(!TAGS.layer){TAGS.layer=document.createElement('div');TAGS.layer.className='tagl';TAGS.layer.setAttribute('aria-hidden','true')}
  let h='';for(let r=win.lo;r<=win.hi;r++)for(let c=0;c<W;c++)h+=tagHTML(idOf(r,c));
  TAGS.layer.innerHTML=h;board.appendChild(TAGS.layer); // after the cells, never before them (elOf counts the board's children)
}
FXH.add('render',tagsAll);
FXH.add('update',({i})=>{if(!TAGS.layer||TAGS.layer.parentNode!==board)return tagsAll();const o=TAGS.layer.querySelector(`.tg[data-i="${i}"]`),h=tagHTML(i);if(o)o.outerHTML=h;else if(h)TAGS.layer.insertAdjacentHTML('beforeend',h)});
'''
rep("/* test only: open with #fxtest", JS + "\n/* test only: open with #fxtest")
CSS = '''/* the tag layer: over the panels and the knight, under the flying critters */
.tagl{position:absolute;left:0;top:0;width:100%;height:0;z-index:3;pointer-events:none}
.tagl .tg{position:absolute}
.board>.cell .b-st{display:none}
'''
rep('/* ===== end of 11/4 ===== */', CSS + '/* ===== end of 11/4 ===== */')
open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
