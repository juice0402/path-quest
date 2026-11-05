# 11/4 その3：build_ui_1104.py のあとの index.html に1回だけ当てる
#  1. ドラッグ中の積み木が画面に残ることがあった：指の動きを body で受けとり、指を見失ったら消す
#  2. タイトル：ロゴの下の記録（旗といちばん遠く）をなくす
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()

def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, old[:100])
    s = s.replace(old, new)

# ---------- 1. the floating block never stays behind ----------
rep('''document.addEventListener('pointerdown',e=>{
  if(!run||run.phase!=='build'||busy||(e.pointerType==='mouse'&&e.button!==0))return;''',
'''function dropGhost(){ // a drag that lost its finger: nothing may stay floating (11/4)
  if(ghost){ghost.remove();ghost=null}
  if(drag&&drag.moving)setOver(-1);
  drag=null;
}
document.addEventListener('pointerdown',e=>{
  if(ghost||drag)dropGhost(); // an old drag whose finger went missing ends here
  if(!run||run.phase!=='build'||busy||(e.pointerType==='mouse'&&e.button!==0))return;''')
rep('''    ghost=document.createElement('div');ghost.className='ghost-tile';ghost.innerHTML=svg(tileArt(run.hand[sel],true));
    document.body.appendChild(ghost);
  }''', '''    ghost=document.createElement('div');ghost.className='ghost-tile';ghost.innerHTML=svg(tileArt(run.hand[sel],true));
    document.body.appendChild(ghost);
    try{document.body.setPointerCapture(e.pointerId)}catch(err){} // the hand is drawn again under the finger: the body keeps the finger, so the lift-off is never lost
  }
  if(e.pointerType==='mouse'&&!e.buttons)return endPointer(e,false); // the button came up outside the page''')
rep('''function endPointer(e,cancel){
  if(!drag||e.pointerId!==drag.id)return;''', '''function endPointer(e,cancel){
  if(!drag){if(ghost)dropGhost();return}
  if(e.pointerId!==drag.id)return;''')
rep("document.addEventListener('pointercancel',e=>endPointer(e,true));\n",
    '''document.addEventListener('pointercancel',e=>endPointer(e,true));
document.addEventListener('lostpointercapture',e=>{if(e.target===document.body&&drag&&e.pointerId===drag.id)endPointer(e,true)});
addEventListener('blur',()=>{if(drag||ghost)dropGhost()});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&(drag||ghost))dropGhost()});
''')

# ---------- 2. title: no record under the logo ----------
rep('''    <div class="t-best pill" id="t-best" aria-label="いちばん遠く"></div>\n''', '')
rep("  $('t-best').innerHTML=meta.far?`${ico(SPR.flag)}<b>${meta.far}</b>`:'';\n", '')

open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
