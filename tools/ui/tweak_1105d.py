# 11/5 騎士くんの動きをなめらかに（#3）：ポーズの切りかわりは前の絵がすっと消えて少しつぶれて戻る・
# 歩くとき1歩ずつ左右にかたむいて着地でつぶれる（マスの間で止まらない）・剣はためてからふる・盾は少し押される・いたいときは後ろにはじかれる
import sys
P='games/path-quest/index.html'
s=open(P,encoding='utf-8').read()
R=[
 # walking: the slide between squares lasts the whole step (it stopped 20ms each square), one waddle per step
 (".hero{position:absolute;left:0;top:0;z-index:3;pointer-events:none;transition:transform .15s linear}",
  ".hero{position:absolute;left:0;top:0;z-index:3;pointer-events:none;transition:transform .17s linear}"),
 (".hero.walk svg{animation:bob .17s ease-in-out infinite alternate}",
  ".hero.walk svg{animation:hWalk .34s linear infinite}"),
 (".hero.hurt svg{animation:hurt .3s ease-out}",".hero.hurt svg{animation:hurt .34s ease-out}"),
 ("@keyframes hurt{30%{transform:translateX(-7%);filter:drop-shadow(0 0 5px var(--bad))}70%{transform:translateX(7%);filter:drop-shadow(0 0 5px var(--bad))}}",
  "@keyframes hurt{0%{transform:none;animation-timing-function:cubic-bezier(.2,.8,.4,1)}22%{transform:translate(-9%,-2%) rotate(-7deg) scale(1.04,.95);filter:drop-shadow(0 0 5px var(--bad))}58%{transform:translateX(3%) rotate(2deg);filter:drop-shadow(0 0 5px var(--bad))}100%{transform:none}}"),
 # the sword: lean back a little, then strike forward and hold, then back (same 240ms)
 ("function lunge(dx,dy){if(!REDUCED)hero.firstElementChild.animate([{transform:'none'},{transform:`translate(${dx}px,${dy}px)`,offset:.35},{transform:`translate(${dx}px,${dy}px)`,offset:.6},{transform:'none'}],{duration:240,easing:'ease-out'})}",
  "function lunge(dx,dy){if(!REDUCED)hero.firstElementChild.animate([{transform:'none',easing:'ease-out'},{transform:`translate(${-dx*.22}px,${-dy*.22}px) scale(.96,1.04)`,offset:.16,easing:'cubic-bezier(.3,0,.2,1)'},{transform:`translate(${dx}px,${dy}px) scale(1.06,.95)`,offset:.4},{transform:`translate(${dx*.92}px,${dy*.92}px)`,offset:.62,easing:'ease-in-out'},{transform:'none'}],{duration:240})}"),
 # a new pose: the old picture fades away on top while the new one settles with a little squash
 ("  if(s0&&s1&&s0!==s1){s0.innerHTML=body;s1.innerHTML=sh;return}",
  "  if(s0&&s1&&s0!==s1){if(!REDUCED)poseGhost(s0);s0.innerHTML=body;s1.innerHTML=sh;if(!REDUCED)poseSettle(s0,p,flip);return}"),
 ("const a=heroArt(p),f=flip?' transform=\"translate(100 0) scale(-1 1)\"':'',body=`<g transform=\"${HG}\"><g${f}>${a}</g></g>`",
  "const a=heroArt(p),f=flip?' transform=\"translate(100 0) scale(-1 1)\"':'',body=`<g class=\"hpz\"><g transform=\"${HG}\"><g${f}>${a}</g></g></g>`"),
]
for a,b in R:
  n=s.count(a)
  if n!=1: sys.exit(f'NG {n}: {a[:70]}')
  s=s.replace(a,b)
fn='''function poseGhost(s0){ /* the picture he had a moment ago stays on top and fades out quickly (a soft change, not a cut) */
  const o=hero.querySelector(':scope>svg.hghost');if(o)o.remove();
  const g=s0.cloneNode(true);g.classList.add('hghost');g.style.transform=getComputedStyle(s0).transform;s0.after(g);
  const a=g.animate([{opacity:.9},{opacity:0}],{duration:140,easing:'ease-out'});a.onfinish=a.oncancel=()=>g.remove();
}
function poseSettle(s0,p,flip){ /* the new pose lands: a small squash and back; the shield is pushed back a little */
  const z=s0.querySelector('.hpz');if(!z)return;
  if(p==='block'){const x=flip?-7:7;z.animate([{transform:'none'},{transform:`translateX(${x}px) scale(1.05,.94)`,offset:.28},{transform:'none'}],{duration:280,easing:'ease-out'});return}
  if(p==='hurt'||p==='ko')return;
  const k=p==='swing'?[1.07,.93]:p==='jump'||p==='cheer'||p==='raise'||p==='lift'?[.95,1.06]:[1.035,.965];
  z.animate([{transform:`scale(${k[0]},${k[1]})`},{transform:`scale(${(2-k[0]).toFixed(3)},${(2-k[1]).toFixed(3)})`,offset:.55},{transform:'none'}],{duration:200,easing:'ease-out'});
}
'''
a='function drawHero(p,flip){'
if s.count(a)!=1: sys.exit('NG drawHero')
s=s.replace(a,fn+a)
css='''
/* the knight moves smoothly (11/5) */
@keyframes hWalk{0%{transform:translateY(0) rotate(-2.5deg) scale(1.03,.97);animation-timing-function:ease-out}25%{transform:translateY(-6%) rotate(0deg) scale(.98,1.02);animation-timing-function:ease-in}50%{transform:translateY(0) rotate(2.5deg) scale(1.03,.97);animation-timing-function:ease-out}75%{transform:translateY(-6%) rotate(0deg) scale(.98,1.02);animation-timing-function:ease-in}100%{transform:translateY(0) rotate(-2.5deg) scale(1.03,.97)}}
.hero>svg.hghost{position:absolute;inset:0;pointer-events:none;animation:none!important}
.hero .hpz{transform-box:view-box;transform-origin:50% 86%}
'''
a='@keyframes ovThud{35%{transform:translateY(5px)}}'
if s.count(a)!=1: sys.exit('NG css anchor')
s=s.replace(a,a+css)
open(P,'w',encoding='utf-8').write(s)
print('ok')
