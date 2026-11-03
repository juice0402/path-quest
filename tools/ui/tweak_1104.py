# 11/4 試遊の感想で調整：15ab5ee の games/path-quest/index.html に1回だけ当てる（当てたあとに走らせると assert で止まる）
#  1. リザルト：強化を大きい木の板に。もう一回・ホームはその下に、2つで同じ幅の木の板
#  2. 強化画面：はじめは何もえらばれていない（説明の紙は、えらんだときだけ出る）
#  3. タイトル：あそぶだけ（強化のボタンをなくす）
#  4. ステータスの下のメッセージ窓：1行を1秒ほど、▶つき。よい変化は赤、わるい変化は青
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()

def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, old[:100])
    s = s.replace(old, new)

# ---------- 1. result ----------
rep('''    <button class="btn main play" id="o-again" type="button">もう一回</button>
    <div class="ov-sub">
      <button class="ibtn" id="o-shop" type="button" aria-label="強化"><span id="o-shop-i"></span><span>強化</span><i class="mk" id="o-dot" hidden></i></button>
      <button class="ibtn" id="o-title" type="button" aria-label="タイトルへ"><span id="o-home-i"></span><span>ホーム</span></button>
    </div>''', '''    <button class="btn main ov-go" id="o-shop" type="button"><span class="bi" id="o-shop-i"></span>強化<i class="mk" id="o-dot" hidden></i></button>
    <div class="ov-sub">
      <button class="btn main play" id="o-again" type="button">もう一回</button>
      <button class="btn main" id="o-title" type="button"><span class="bi" id="o-home-i"></span>ホーム</button>
    </div>''')

# ---------- 3. title: only あそぶ ----------
rep('''      <div class="t-sub"><button class="ibtn" id="t-shop" type="button" aria-label="強化"><span id="t-shop-i"></span><span>強化</span><i class="mk" id="t-dot" hidden></i></button></div>\n''', '')
rep("  $('t-shop-i').innerHTML=ico(ICON_UP_F());$('t-dot').hidden=!affordable();\n", '')
rep("$('t-shop').addEventListener('click',()=>showShop());\n", '')

# ---------- 2. shop: nothing chosen until a tap ----------
rep("const shopSel={up:'hp',gear:null,skill:null,deck:'dx'};", "const shopSel={up:null,gear:null,skill:null,deck:null};")
rep('''function pickDefault(){ // a tab never opens with nothing on the pinned paper
  if(shopTab==='gear'){const s=GEAR_ID[shopSel.gear];if(!s||s.s!==gearSlot){const nw=(meta.newg||[]).map(x=>GEAR_ID[x]).find(g=>g&&g.s===gearSlot);
    shopSel.gear=nw?nw.id:meta.gear.eq[gearSlot]||((GEAR.find(g=>g.s===gearSlot&&owned(g.id))||GEAR.find(g=>g.s===gearSlot)||{}).id)||null}}
  if(shopTab==='skill'&&!SKILL_ID[shopSel.skill])shopSel.skill=meta.sk.eq.find(Boolean)||SKILLS[0].id;
}''', '''function pickDefault(){ // nothing is chosen until a tap: the pinned paper comes up only then (11/4)
  if(shopTab==='gear'){const s=GEAR_ID[shopSel.gear];if(!s||s.s!==gearSlot)shopSel.gear=null}
  if(shopTab==='skill'&&!SKILL_ID[shopSel.skill])shopSel.skill=null;
}''')
rep('''const g=GEAR_ID[sel];if(!g)return `<span class="dt-art"></span><div class="dt-head"><b>${(SLOTS.find(s=>s.k===gearSlot)||{}).n}</b></div><div class="dt-body"><p class="dt-d dim">まだ何も見つけていない。冒険で拾うとここに並ぶ</p></div><div class="dt-foot"></div>`;''',
    "const g=GEAR_ID[sel];if(!g)return '';")
rep("  const d=$('sh-det');d.innerHTML=detailHTML();", "  const d=$('sh-det'),dh=detailHTML();d.innerHTML=dh;d.hidden=!dh;")
rep('''  shopSel[shopTab]=key;detT=performance.now();renderShop();
  const d=$('sh-det');if(!REDUCED){d.classList.remove('flash');void d.offsetWidth;d.classList.add('flash')}''',
    '''  shopSel[shopTab]=key;detT=performance.now();renderShop();
  const d=$('sh-det');if(!REDUCED){d.classList.remove('flash');void d.offsetWidth;d.classList.add('flash')}
  const on=$('sh-body').querySelector('.sel');if(on)on.scrollIntoView({block:'nearest'}); // the paper came up under it: keep the chosen row in view''')
rep("function setShopTab(t){if(swap)swap=null;shopTab=t;renderShop(true)}", "function setShopTab(t){if(swap)swap=null;shopTab=t;shopSel[t]=null;renderShop(true)}")
rep("  if(tab)shopTab=tab;visit=[];swap=null;\n", "  if(tab)shopTab=tab;visit=[];swap=null;for(const k in shopSel)shopSel[k]=null;\n")

# ---------- 4. the message window ----------
rep('''function say(t,stay){const el=$('say');clearTimeout(sayT);el.textContent=t;el.hidden=false;if(!stay)sayT=setTimeout(()=>{el.hidden=true},1700)}
function hideSay(){clearTimeout(sayT);$('say').hidden=true;hidePick()}''', '''/* the message window under the status (11/4): one short line at a time for about a second, ▶ in front —
   red when it helps the knight, blue when it hurts. lines wait while a sheet covers the field */
function note(t,k){
  if(!t)return;const q=note.q||(note.q=[]);q.push({t,k:k||''});if(q.length>6)q.splice(0,q.length-6);
  if(!note.on)noteNext();
}
function noteNext(){
  const q=note.q||[],el=$('say');clearTimeout(note.t);
  if(!q.length){note.on=false;el.hidden=true;return}
  note.on=true;
  if(SHEETS.some(id=>!$(id).hidden)){el.hidden=true;note.t=setTimeout(noteNext,250);return}
  const m=q.shift();el.className='say'+(m.k?' '+m.k:'');el.innerHTML='<i class="cur" aria-hidden="true"></i><span></span>';el.lastChild.textContent=m.t;el.hidden=false;
  if(!REDUCED){el.classList.remove('in');void el.offsetWidth;el.classList.add('in')}
  note.t=setTimeout(noteNext,q.length?850:1100);
}
function say(t){note(t)}
function hideSay(){clearTimeout(note.t);note.q=[];note.on=false;$('say').hidden=true;hidePick()}''')
# a reroll no longer wipes the lines
rep("  run.rolls--;sel=-1;aim=null;hideSay();render();", "  run.rolls--;sel=-1;aim=null;hidePick();render();")
# poison
rep("if(c.psn){run.pz={n:3,d:c.psn};c.psn=0;pop(i,'毒！','p-psn')}", "if(c.psn){run.pz={n:3,d:c.psn};c.psn=0;note('毒状態になった','bad')}")
rep('''    if(run.hp<=0){hero.classList.remove('walk','psn');await knockOut();busy=false;gameOver('hp');return false}
  }''', '''    if(run.hp<=0){hero.classList.remove('walk','psn');await knockOut();busy=false;gameOver('hp');return false}
    if(run.pz.n<=0)note('毒がぬけた','good');
  }''')
# a new land
rep("renderStats();say(`${dimName(dimOf(r))}へ！ 敵もこっちも${DIM_X}倍。★${topR()}の装備も見つかる`);",
    "renderStats();note(`${dimName(dimOf(r))}へ！`);note(`攻撃・守り・HPが${DIM_X}倍`,'good');note(`敵も${DIM_X}倍になった`,'bad');note(`★${topR()}の装備も見つかる`,'good');")
# a new piece of gear on the road
rep("pop(i,`NEW! ${g.n}`,'p-gear');fly(i,g.art,$('quit'));", "note(`${g.n}を見つけた`,'good');fly(i,g.art,$('quit'));")
# skills
rep("candy:()=>{const h=Math.min(3*PM(),run.maxHp-run.hp);if(h<=0)return 'HPは まんたん';run.hp+=h;return ()=>{pop(run.at,`+${h}`,'p-heal');fly(run.at,SPR.heart,$('hp'))}},",
    "candy:()=>{const h=Math.min(3*PM(),run.maxHp-run.hp);if(h<=0)return 'HPは まんたん';run.hp+=h;return ()=>{pop(run.at,`+${h}`,'p-heal');fly(run.at,SPR.heart,$('hp'));note(`HP${nf(h)}回復`,'good')}},")
rep("wind:()=>{run.fx.wind=3;return ()=>{pop(run.at,'攻撃2倍','p-deal');spark(run.at)}},", "wind:()=>{run.fx.wind=3;return ()=>{note('3マスのあいだ攻撃力2倍','good');spark(run.at)}},")
rep("guard:()=>{run.fx.guard=1;return ()=>pop(run.at,'ガード','p-gear')},", "guard:()=>{run.fx.guard=1;return ()=>note('つぎの戦いはダメージ0','good')},")
rep("s.cd=Math.max(1,d.ct-qv('cdr'));sel=-1;save();render();say(d.n+'！');", "s.cd=Math.max(1,d.ct-qv('cdr'));sel=-1;save();render();note(`${d.n}を使った`);")
rep("  if(FX().wind>0)run.fx.wind--;\n", "  if(FX().wind>0){run.fx.wind--;if(!run.fx.wind)note('攻撃力が元にもどった','bad')}\n")
# rewards: what the chosen card did
rep('''  const N=typeof x.val==='number'?x.val:typeof x.v==='number'?x.v:0; // older saves kept the number in v
''', '''  const N=typeof x.val==='number'?x.val:typeof x.v==='number'?x.v:0; // older saves kept the number in v
  const b0={atk:run.atk,def:run.def,mx:run.maxHp,hp:run.hp,rl:run.rolls};let gotG=0;
''')
rep('''  if(x.k==='gold')addGold(N);
  run.rewards=null;if(pending())return openReward();''', '''  if(x.k==='gold')gotG=addGold(N);
  rewardNotes(x,b0,gotG);
  run.rewards=null;if(pending())return openReward();''')
rep('''function takeReward(i){''', '''const PNOTE={pcrit:'会心が出やすくなった',pcross:'十字の積み木が出やすくなった',pleech:'勝つとHPが回復するようになった',pref:'ダメージをはね返すようになった',pmag:'魔法と毒のダメージが2倍',pfirst:'いつも先に攻撃するようになった',allup:'おもちゃがぜんぶLv+1'};
function rewardNotes(x,b,g){ // the lines for the message window: the toy first, then every number that went up
  const L=[],up=(a,c)=>Math.round(c-a);
  if(x.k==='it')L.push(x.lv===1?`${x.n}を手に入れた`:`${x.n}がLv${x.lv}になった`);
  if(x.k==='evo')L.push(`${x.n}に大進化`);
  if(PNOTE[x.k])L.push(PNOTE[x.k]);
  if(up(b.atk,run.atk)>0)L.push(`攻撃力${nf(up(b.atk,run.atk))}アップ`);
  if(up(b.def,run.def)>0)L.push(`守り${nf(up(b.def,run.def))}アップ`);
  if(up(b.mx,run.maxHp)>0)L.push(`最大HP${nf(up(b.mx,run.maxHp))}アップ`);
  const h=up(b.hp,run.hp)-Math.max(0,up(b.mx,run.maxHp));if(h>0)L.push(`HP${nf(h)}回復`);
  if(up(b.rl,run.rolls)>0)L.push(`リロール+${up(b.rl,run.rolls)}`);
  if(g>0)L.push(`金貨+${nf(g)}`);
  L.forEach(t=>note(t,'good'));
}
function takeReward(i){''')

# the test hook (#fxtest) can write a line too
rep("window.PQ={get run(){return run},FXH,openReward,showShop,", "window.PQ={get run(){return run},FXH,openReward,showShop,note,")

# ---------- css ----------
CSS = r'''
/* ===== 11/4: result boards, the shop paper only when chosen, the message window ===== */
/* result: 強化 is the big board; もう一回 and ホーム are two boards under it, together just as wide */
.ov .ov-go,.ov-sub .btn{position:relative;display:flex;align-items:center;justify-content:center;gap:8px;width:100%;box-sizing:border-box;animation:none}
.ov .ov-go{margin-top:6px;min-height:62px;font-size:22px}
.ov-sub{display:grid;grid-template-columns:1fr 1fr;gap:10px;width:100%}
.ov-sub .btn,.ov .ov-sub .btn.play{margin-top:0;min-height:52px;padding:8px 10px;font-size:18px}
.ov-sub .btn.play::before{border-left-width:12px;border-top-width:8px;border-bottom-width:8px}
.ov-sub .btn::after{display:none}
.ov .bi svg{display:block;width:34px;height:34px;filter:drop-shadow(0 2px 0 var(--wood-deep))}
.ov-sub .bi svg{width:28px;height:28px}
.ov .ov-go .mk{position:absolute;top:9px;right:34px;width:14px;height:14px;border-radius:50%;background:#f2b632;box-shadow:0 0 0 2px var(--wood-deep),inset 0 -2px 0 #c98a12}
.ov .ov-go .mk[hidden]{display:none}
/* shop: the pinned paper is away until something is chosen */
.sh-det[hidden]{display:none}
/* the message window under the status: a framed paper strip with an inner line, ▶ in front */
.say{left:8px;right:8px;top:calc(var(--hudh) + 4px);transform:none;width:auto;max-width:none;display:flex;align-items:center;gap:7px;min-height:38px;padding:6px 14px;border-radius:2px;
  background:var(--paper);outline:2px solid var(--frame);outline-offset:-2px;box-shadow:inset 0 0 0 4px var(--paper),inset 0 0 0 5.5px var(--edge),0 4px 0 var(--frame);
  font:800 15px/1.3 var(--round);color:var(--ink);text-align:left;white-space:nowrap}
.say[hidden]{display:none}
.say>span{min-width:0;overflow:hidden;text-overflow:ellipsis}
.say .cur{flex:none;width:0;height:0;border-left:9px solid currentColor;border-top:6px solid transparent;border-bottom:6px solid transparent}
.say.good{color:#cf2338}
.say.bad{color:#2456c4}
.say.in{animation:sayin .14s ease-out}
@keyframes sayin{from{opacity:0;transform:translateY(-4px)}}
@media (prefers-reduced-motion:reduce){.say.in{animation:none}}
/* ===== end of 11/4 ===== */
'''
i = s.find('</style>')  # the end of the main style block
s = s[:i] + CSS + s[i:]

open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
