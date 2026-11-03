# 11/4 その4：tweak_1104c.py のあとの index.html に1回だけ当てる
#  生きもの：パネルの中にいると「何かあるマス」に見えるので、マス目に関係なく盤の上を飛ぶ・歩いて横切るようにする
#  （虫は飛ぶ：ちょうちょ・はち・てんとう虫・とんぼ・ほたる。ほかは歩いて横切る。騎士が近づくと逃げる）
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()

def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, old[:100])
    s = s.replace(old, new)

# no critter sits inside a panel any more
rep("      const k=!S.off.has('crit')&&critterKind(i,c);if(k)post+=critterHTML(i,k);\n", '')

JS = r'''
  /* critters roam the field (11/4): they fly or walk across the panels and never sit in one, so no panel looks like it holds something.
     each one is anchored to a row of the world (its top is set again on every redraw) and its path is drawn in board pixels from there */
  const FLYK={bfly:1,bfly2:1,bee:1,lady:1,dfly:1,ffly:1};
  const TOPV={lady:1,dfly:1},SYMV={bfly:1,bfly2:1,ffly:1,top:1}; // seen from above: turn with the path; seen from the front: only lean
  const SPEED={bfly:.55,bfly2:.55,bee:.85,lady:.6,dfly:1.1,ffly:.3,snail:.07,squir:.42,frog:.36,duckl:.3,bunny:.42,peng:.28,robin:.38,mouse:.55,top:.32,wduck:.3}; // panels a second
  const RM={layer:null,list:[],t:0,run:null};
  const rowTop=r=>4+(win.hi-r)*win.pitch;
  function roamLayer(){
    if(!RM.layer){RM.layer=document.createElement('div');RM.layer.className='lf-roam';RM.layer.setAttribute('aria-hidden','true')}
    if(RM.layer.parentNode!==board)board.appendChild(RM.layer); // after the cells: elOf counts the board's children
    return RM.layer;
  }
  function roamClear(){for(const o of RM.list){o.a.cancel();o.el.remove()}RM.list=[];clearTimeout(RM.t);RM.t=0}
  const roamWant=()=>run&&dimOf(rowOf(run.at))===2?3:2;
  function roamNext(ms){if(!RM.t)RM.t=setTimeout(roamSpawn,ms==null?1800+Math.random()*4500:ms)}
  function spline(P,n){ // a smooth line through the points (Catmull-Rom), n steps between two points
    const out=[];
    for(let i=0;i<P.length-1;i++){const p0=P[Math.max(0,i-1)],p1=P[i],p2=P[i+1],p3=P[Math.min(P.length-1,i+2)];
      for(let k=0;k<n;k++){const t=k/n,t2=t*t,t3=t2*t;out.push([0,1].map(j=>.5*(2*p1[j]+(-p0[j]+p2[j])*t+(2*p0[j]-5*p1[j]+4*p2[j]-p3[j])*t2+(-p0[j]+3*p1[j]-3*p2[j]+p3[j])*t3)))}}
    out.push(P[P.length-1]);return out;
  }
  function roamSpawn(){
    RM.t=0;if(!run||REDUCED||S.off.has('crit')||!win.pitch)return;
    if(RM.list.length>=roamWant())return;
    const mid=Math.max(2,Math.round((S.vlo+S.vhi)/2)),night=dimOf(mid)===2,land=S.land[areaOf(mid).k]||S.land.grass||[];
    const ks=(night?['ffly'].concat(land):land).filter(k=>KIND[k]&&!RM.list.some(o=>o.k===k));
    if(!ks.length)return roamNext();
    const k=ks[(Math.random()*ks.length)|0],mv=KIND[k][0],z=KIND[k][1],fly=!!FLYK[k];
    const cw=win.pitch-GAP,size=cw*z/100,BW=board.clientWidth,lo=Math.max(S.vlo+.6,2),hi=Math.max(lo+.6,S.vhi-1.8);
    const rnd=(a,b)=>a+Math.random()*(b-a),r0=Math.floor(lo),fromL=Math.random()<.5,x0=fromL?-size:BW+size,x1=fromL?BW+size:-size;
    const yOf=rf=>(r0-rf)*win.pitch+cw/2; // below the anchor row's top, in board pixels
    let P;
    if(fly){P=[[x0,yOf(rnd(lo,hi))]];for(let j=1;j<=3;j++)P.push([x0+(x1-x0)*j/4+rnd(-.7,.7)*cw,yOf(rnd(lo,hi))]);P.push([x1,yOf(rnd(lo,hi))]);P=spline(P,10)}
    else{const y=yOf(rnd(lo,Math.min(hi,lo+2.6))),ph=rnd(0,6);P=[];for(let j=0;j<=12;j++)P.push([x0+(x1-x0)*j/12,y+Math.sin(j*1.1+ph)*cw*.09])}
    const sp=cw*(SPEED[k]||.4)/1000,T=[0];for(let j=1;j<P.length;j++)T.push(T[j-1]+Math.hypot(P[j][0]-P[j-1][0],P[j][1]-P[j-1][1])/sp);
    const side=!TOPV[k]&&!SYMV[k];
    const pose=j=>{const q=P[Math.min(P.length-1,j+1)],o=P[Math.max(0,j-1)],dx=q[0]-o[0],dy=q[1]-o[1];
      const rot=TOPV[k]?Math.atan2(dy,dx)*180/Math.PI+90:SYMV[k]&&fly?Math.max(-16,Math.min(16,(dx>0?1:-1)*dy/cw*18)):0;
      return `translate(${P[j][0].toFixed(1)}px,${P[j][1].toFixed(1)}px) rotate(${rot.toFixed(1)}deg)`};
    const F=P.map((p,j)=>({t:T[j],tr:pose(j)}));
    if(!fly){const j=3+((Math.random()*6)|0),w=1000+Math.random()*1500;for(let n=j+1;n<F.length;n++)F[n].t+=w;F.splice(j+1,0,{t:F[j].t+w,tr:F[j].tr})} // a walker stops once for a breath
    const dur=F[F.length-1].t,kf=F.map(f=>({offset:f.t/dur,transform:f.tr}));
    const air=fly?(k==='ffly'?'':' lf-air'):' lf-gr',gold=Math.random()<1/30;
    const el=document.createElement('i');el.className='lf-r '+(fly?'fly':'walk');
    el.innerHTML=`<i class="lf-rm"><i class="lf-c mv-${mv} lf-s-${k}${air}${gold?' lf-gold':''}${CR_WB.has(k)?' lf-wb':''}" style="width:${size.toFixed(1)}px;--lfT:0s;--sd:-${(Math.random()*90).toFixed(1)}s${side&&!fromL?';transform:scaleX(-1)':''}"><b></b></i></i>`;
    roamLayer().appendChild(el);el.style.top=rowTop(r0).toFixed(1)+'px';
    const a=el.firstChild.animate(kf,{duration:dur,easing:'linear'}),o={el,a,k,r0};
    RM.list.push(o);
    a.onfinish=()=>{el.remove();RM.list=RM.list.filter(x=>x!==o);roamNext()};
    if(RM.list.length<roamWant())roamNext();
  }
  function roamScare(i,R){ // the knight (or a blast) comes near: whoever is close flies or runs off
    const e=elOf(i);if(!e||!RM.list.length)return;
    const b=e.getBoundingClientRect(),cx=b.left+b.width/2,cy=b.top+b.height/2,lim=b.width*(R+.35);
    for(const o of RM.list.slice()){
      const c=o.el.querySelector('.lf-c');if(!c)continue;const r=c.getBoundingClientRect();
      if(Math.hypot(r.left+r.width/2-cx,r.top+r.height/2-cy)>lim)continue;
      flee(c,-1);o.a.cancel();o.el.remove();RM.list=RM.list.filter(x=>x!==o);roamNext();
    }
  }
  FXH.add('render',()=>{
    if(!run||S.off.has('crit'))return;
    if(RM.run!==run){roamClear();RM.run=run}
    roamLayer();for(const o of RM.list)o.el.style.top=rowTop(o.r0).toFixed(1)+'px';
    if(RM.list.length<roamWant())roamNext(RM.list.length?null:500+Math.random()*1500);
  });
  FXH.add('step',({to})=>{if(run)roamScare(to,1)});
  FXH.add('kill',({i})=>{if(run)roamScare(i,1)});
  FXH.add('boom',({at,R})=>{if(run)roamScare(at,(R|0)+1)});
  FXH.add('cannon',({hits})=>{if(run)(hits||[]).forEach(x=>roamScare(x.i,1))});
'''
rep("  FXH.add('cannon',({hits})=>{if(run)(hits||[]).forEach(x=>scare(x.i,1))});\n",
    "  FXH.add('cannon',({hits})=>{if(run)(hits||[]).forEach(x=>scare(x.i,1))});\n" + JS)

CSS = '''/* ===== 11/4: critters roam over the field, never inside one panel ===== */
.lf-roam{position:absolute;left:0;top:0;width:100%;height:0;pointer-events:none}
.lf-r{position:absolute;left:0;width:0;height:0;pointer-events:none}
.lf-r.walk{z-index:1}.lf-r.fly{z-index:4}
.lf-rm{position:absolute;left:0;top:0;width:0;height:0}
.lf-rm>.lf-c{left:0;top:0;translate:-50% -50%;animation:none!important}
.lf-rm>.mv-cr>b{animation:lfAlt 1.9s ease-in-out var(--sd,0s) infinite alternate}
@media (prefers-reduced-motion:reduce){.lf-roam{display:none}}
'''
rep('/* ===== end of fx css D ===== */\n', '/* ===== end of fx css D ===== */\n' + CSS)

open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
