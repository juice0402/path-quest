# 11/4 夜 点検係の指摘の直し（1回だけ当てる）
#  1 とげで力つきたとき「いたい」がたおれたあとに出る → すぐ出す
#  2 待っているときの きょろきょろ が反対を向かない → 時間の組み方を直す
#  3 ごほうびのあと・開きなおしたあとも、正面で息をして待つ
#  4 にげる・はりきり・巻き直し・起き上がりのめやすは「もとのHP」（手持ちで魔法をうけて減っていても）→ e.mhp
#  5 いたずら小僧の紙に「にげると金貨 +○」
#  6 きのこの毒は、もっと強い毒が残っていたら弱めない
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    c = s.count(old); assert c == n, (c, old[:90]); s = s.replace(old, new)

rep("""      if(h.thorn){run.hp-=h.thorn;setTimeout(()=>{pop(at,`-${h.thorn}`,'p-hurt');hurt()},160);renderStats();if(run.hp<=0)return false}""",
    """      if(h.thorn){run.hp-=h.thorn;renderStats();if(run.hp<=0){pop(at,`-${h.thorn}`,'p-hurt');hurt();return false}setTimeout(()=>{pop(at,`-${h.thorn}`,'p-hurt');hurt()},160)}""")
rep("""  if(r<.3){heroPose('side',700,false);const t=HS.tok;setTimeout(()=>{if(HS.tok===t)heroPose('side',700,true)},700)}""",
    """  if(r<.3){heroPose('side',1400,false);const t=HS.tok;setTimeout(()=>{if(HS.tok===t)heroPose('side',700,true)},700)}""")
rep("""  run.chest=false;run.phase='build';hideSheets();render();afterAction();""", """  run.chest=false;run.phase='build';hideSheets();render();heroRest();afterAction();""")
rep("""  run.phase='build';busy=false;render();afterAction();""", """  run.phase='build';busy=false;render();heroRest();afterAction();""")
# the full hp a toy was made with
rep("""const tuneFoe=o=>{const m=QM[o.t];if(m){o.hp=Math.max(2,Math.round(o.hp*m[0]));o.atk=Math.max(1,Math.round(o.atk*m[1]))}return o};""",
    """const tuneFoe=o=>{const m=QM[o.t];if(m){o.hp=Math.max(2,Math.round(o.hp*m[0]));o.atk=Math.max(1,Math.round(o.atk*m[1]))}o.mhp=o.hp;return o};""")
rep("""    const B=BAL.foe;Object.assign(e,{t:k,name:s.name,hp:Math.round(Math.max(2,B.hp[0]+B.hp[1]*L+s.hp)*x),atk:Math.round(Math.max(1,B.atk[0]+Math.floor((L-1)*B.atk[1])+s.atk)*x)});""",
    """    const B=BAL.foe;Object.assign(e,{t:k,name:s.name,hp:Math.round(Math.max(2,B.hp[0]+B.hp[1]*L+s.hp)*x),atk:Math.round(Math.max(1,B.atk[0]+Math.floor((L-1)*B.atk[1])+s.atk)*x)});e.mhp=e.hp;""")
rep("""gold:Math.round(B.gold[0]+B.gold[1]*f),boss:true,king:true}}""", """gold:Math.round(B.gold[0]+B.gold[1]*f),boss:true,king:true,mhp:Math.round((B.hp[0]+L*B.hp[1])*x)}}""")
rep("""gold:Math.round(B.gold[0]+B.gold[1]*f),boss:true}}""", """gold:Math.round(B.gold[0]+B.gold[1]*f),boss:true,mhp:Math.round((B.hp[0]+L*B.hp[1])*x)}}""")
rep("""  return {q,hp:e.hp,max:e.hp,n:0,kn:0,mul:1,up:0,wound:0,""", """  return {q,hp:e.hp,max:Math.max(e.hp,e.mhp||0),n:0,kn:0,mul:1,up:0,wound:0,""")
# the imp's paper
rep("""+`<span class="fd-g">たおすと${ico(SPR.coin)}+${nf(gainOf(e.gold))}</span>`}""",
    """+`<span class="fd-g">たおすと${ico(SPR.coin)}+${nf(gainOf(e.gold))}${(QK[e.t]||{}).flee?`（にげると+${nf(gainOf(Math.ceil(e.gold/2)))}）`:''}</span>`}""")
# spores do not weaken a stronger poison
rep("""  if(R.q.spore){run.pz={n:R.q.spore,d:Math.max(1,Math.ceil(e.atk/3))};""",
    """  if(R.q.spore){const o=run.pz&&run.pz.n>0?run.pz:{n:0,d:0};run.pz={n:Math.max(o.n,R.q.spore),d:Math.max(o.d,Math.max(1,Math.ceil(e.atk/3)))};""")
open(P, 'w', encoding='utf-8').write(s); print('ok')
