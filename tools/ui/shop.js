/* ---------- the shop: a tap only chooses; the one button on the pinned paper buys, puts on, learns or sets.
   everything bought on this visit can be taken back for the full price until the shop is left ---------- */
const UPV={ // what an upgrade gives at level l: [short name, value]
  hp:['最大HP',l=>10+2*l],atk:['攻撃',l=>2+l],def:['守り',l=>l],bag:['場所ごとの回復',l=>l?'HP+'+2*l:'なし'],
  roll:['リロール',l=>(3+l)+'回'],hand:['手持ち',l=>(4+l)+'こ'],
  dg:['装備と金貨',l=>l?'+'+30*l+'%':'ふつう'],dp:['キャンディ',l=>l?'+'+40*l+'%':'ふつう'],ds:['はじめの十字',l=>l+'こ']
};
const MIXG=[[m=>m===5,4,5,'縦'],[m=>m===10,1,10,'横'],[isCurve,0,3,'カーブ'],[isT,3,7,'T字'],[m=>m===15,2,15,'十字']]; // [which shapes, block colour, road, name]
const MIX_OF={dh:1,dc:2,dt:3,dx:4};
function mixAt(over){ // the share of each kind of block (0..1), with some upgrade levels changed
  const keep=meta.up;if(over)meta.up={...keep,...over};
  const W=shapeW(),tot=W.reduce((a,x)=>a+x[1],0)||1;meta.up=keep;
  return MIXG.map(([f])=>W.filter(x=>f(x[0])).reduce((a,x)=>a+x[1],0)/tot);
}
const pc=x=>Math.round(x*100)+'%';
const SKILL_AIM={tile:'ねらう：手持ちの積み木',rock:'ねらう：じゃまな物',foe:'ねらう：敵がのった積み木',free:'ねらう：何ものっていない積み木'};
const GCMP=[['atk','攻撃',x=>x],['def','守り',x=>x],['hp','最大HP',x=>x],['crit','会心',pct],['mag','魔法',x=>x],['gold','金貨',x=>'+'+pct(x)],['roll','リロール',x=>x],['bag','回復',x=>x],['cdr','スキルの休み',x=>'-'+x]];
let shopTab='up',gearSlot='wpn',lastFound=0,swap=null,visit=[],detT=0;
const shopSel={up:'hp',gear:null,skill:null,deck:'dx'};
const lvPips=(l,max,big,next)=>`<span class="lv${big?' big':''}" aria-label="Lv${l}/${max}">${Array.from({length:max},(_,j)=>`<i class="${j<l?'on':next&&j===l?'new':''}"></i>`).join('')}</span>`;
const priceTag=(c,can)=>`<span class="tag${can?'':' no'}">${ico(SPR.coin)}${nf(c)}</span>`;
const upArt=u=>{const mi=MIX_OF[u.k];if(mi!=null){const [,c,m]=MIXG[mi];return svg(blockSVG(c)+roadSVG(m,BLOCKS[c][1],4,96)+(u.k==='dh'?'<path d="M66 10l22 22M88 10 66 32" stroke="#fff" stroke-width="12" stroke-linecap="round"/><path d="M66 10l22 22M88 10 66 32" stroke="#d6334f" stroke-width="6" stroke-linecap="round"/>':''))}return u.art?svg(u.art):ico(SPR[u.icon])};
const UPNAME={dx:'十字',dt:'T字',dc:'カーブ',dh:'横まっすぐを減らす',dg:'宝の積み木',dp:'キャンディの積み木',ds:'はじめの十字'};
function upRow(u){
  const l=meta.up[u.k],max=l>=u.max,c=u.cost(l),can=!max&&meta.bank>=c,v=UPV[u.k],mi=MIX_OF[u.k];
  const sub=mi!=null?`${MIXG[mi][3]} ${pc(mixAt()[mi])}`:v?`${v[0]} ${v[1](l)}`:'';
  return `<button class="row-i${shopSel[shopTab]===u.k?' sel':''}" type="button" data-k="${u.k}"><span class="ri-art">${upArt(u)}</span>`+
    `<span class="ri-name"><b>${UPNAME[u.k]||u.name}</b><span class="ri-sub">${lvPips(l,u.max)} ${sub}</span></span>`+
    (max?'<span class="tag max">MAX</span>':priceTag(c,can))+'</button>';
}
function mixHTML(){ // the bar of how the blocks come now, and with a shape chosen, after one more level
  const now=mixAt(),k=shopSel.deck,u=UPS.find(x=>x.k===k),mi=MIX_OF[k],after=u&&mi!=null&&meta.up[k]<u.max?mixAt({[k]:meta.up[k]+1}):null;
  const bar=(m,lab)=>`<div class="mx-row"><span class="mx-l">${lab}</span><div class="bar">${m.map((w,j)=>`<i class="${after&&j===mi?'hi':''}" style="flex-grow:${w.toFixed(4)};background:${BLOCKS[MIXG[j][1]][0]}">${w>=.08?pc(w):''}</i>`).join('')}</div></div>`;
  return `<div class="sh-sheet mix">${bar(now,'いま')}${after?bar(after,'強化後'):''}<div class="lg">${MIXG.map(([,c,m,n],j)=>`<span class="${after&&j===mi?'hi':''}">${svg(blockSVG(c)+roadSVG(m,BLOCKS[c][1],4,96))}${n}</span>`).join('')}</div></div>`;
}
function gearHTML(){
  const eq=meta.gear.eq,nw=meta.newg||[];
  let h='<div class="slots3">'+SLOTS.map(s=>{const g=GEAR_ID[eq[s.k]],all=GEAR.filter(x=>x.s===s.k);
    return `<button class="slot3${s.k===gearSlot?' on':''}" type="button" data-slot="${s.k}" aria-pressed="${s.k===gearSlot}"><span class="s3-art" style="--rc:${g?['','#b9a998','#5f97de','#e0a12a','#c4467a'][g.r]:'#d8c1a6'}">${g?ico(g.art):''}</span><b>${s.n}</b><small>集めた ${all.filter(x=>owned(x.id)).length}/${all.length}</small></button>`}).join('')+'</div>';
  const list=GEAR.filter(x=>x.s===gearSlot).sort((a,b)=>(owned(b.id)-owned(a.id))||(a.r-b.r));
  h+='<div class="case">'+list.map(g=>{const own=owned(g.id),on=eq[g.s]===g.id;
    return `<button class="gi2 r${g.r}${own?'':' lock'}${shopSel.gear===g.id?' sel':''}" type="button" data-g="${g.id}" aria-label="${own?g.n:'まだ見つけていない'} ★${g.r}">${ico(g.art)}<em class="st">${'★'.repeat(g.r)}</em>${on?'<i class="eqk">装備中</i>':''}${own&&nw.includes(g.id)?'<i class="nw">NEW</i>':''}</button>`}).join('')+'</div>';
  return h;
}
function skillHTML(){
  const own=meta.sk.own,eq=meta.sk.eq;
  let h=`<div class="pegs${swap?' swap':''}"><span>${swap?'どの枠と入れかえる？':'セット'}</span>${eq.map((id,j)=>`<button class="peg${id&&shopSel.skill===id&&!swap?' sel':''}" type="button" data-peg="${j}" aria-label="枠${j+1}${id?'：'+SKILL_ID[id].n:'（空き）'}"><em>${j+1}</em>${id?svg(SK_ART[id]):''}</button>`).join('')}</div>`;
  h+='<div class="book">'+SKILLS.map(k=>{const has=own.includes(k.id),on=eq.includes(k.id);
    const tag=on?'<span class="tag on">セット中</span>':has?'<span class="tag own">覚えた</span>':priceTag(k.cost,meta.bank>=k.cost);
    return `<button class="sk2${has?'':' not'}${shopSel.skill===k.id?' sel':''}" type="button" data-s="${k.id}">${svg(SK_ART[k.id])}<b>${k.n}</b>${tag}</button>`}).join('')+'</div>';
  return h;
}
const bought=(t,key)=>{for(let j=visit.length-1;j>=0;j--)if(visit[j].t===t&&visit[j].key===key)return j;return -1};
function chg(label,a,b){ // "攻撃 2 → 3", the new number green when it goes up and red when it goes down
  const na=parseFloat(a),nb=parseFloat(b),d=isNaN(na)||isNaN(nb)?0:nb-na;
  return `<span><span class="k">${label}</span><span class="a">${a}</span><span class="to">→</span><span class="b${d<0?' dn':d===0&&a===b?' same':''}">${b}</span></span>`;
}
function detailHTML(){
  const sel=shopSel[shopTab],coinBtn=(lab,c)=>`<button class="dt-btn" type="button" data-act="buy">${lab}${ico(SPR.coin)}<b>${nf(c)}</b></button>`;
  const short=c=>`<button class="dt-btn" type="button" disabled>あと ${nf(c-meta.bank)} 枚</button>`;
  const undo=(t,key)=>`<button class="dt-sub" type="button" data-act="undo"${bought(t,key)>=0?'':' disabled'}>もどす</button>`;
  if(shopTab==='up'||shopTab==='deck'){
    const u=UPS.find(x=>x.k===sel);if(!u)return '';
    const l=meta.up[u.k],max=l>=u.max,c=u.cost(l),v=UPV[u.k],mi=MIX_OF[u.k];
    let ch='';
    if(mi!=null)ch=chg(MIXG[mi][3]+'の出やすさ',pc(mixAt()[mi]),max?pc(mixAt()[mi]):pc(mixAt({[u.k]:l+1})[mi]));
    else if(v)ch=max?`<span><span class="k">${v[0]}</span><span class="b same">${v[1](l)}</span></span>`:chg(v[0],v[1](l),v[1](l+1));
    const btn=max?'<button class="dt-btn" type="button" disabled>MAX</button>':meta.bank>=c?coinBtn('強化する',c):short(c);
    return `<span class="dt-art">${upArt(u)}</span><div class="dt-head"><b>${UPNAME[u.k]||u.name}</b>${lvPips(l,u.max,true,!max)}</div>`+
      `<div class="dt-body"><p class="dt-d">${u.desc}</p><div class="dt-ch">${ch}</div></div><div class="dt-foot">${undo('up',u.k)}<span class="note"></span>${btn}</div>`;
  }
  if(shopTab==='gear'){
    const g=GEAR_ID[sel];if(!g)return `<span class="dt-art"></span><div class="dt-head"><b>${(SLOTS.find(s=>s.k===gearSlot)||{}).n}</b></div><div class="dt-body"><p class="dt-d dim">まだ何も見つけていない。冒険で拾うとここに並ぶ</p></div><div class="dt-foot"></div>`;
    const own=owned(g.id),on=meta.gear.eq[g.s]===g.id,cur=GEAR_ID[meta.gear.eq[g.s]];
    const head=`<span class="dt-art">${own?ico(g.art):`<svg viewBox="22 22 56 56" aria-hidden="true" style="filter:brightness(0) opacity(.15)">${g.art}</svg>`}</span><div class="dt-head"><b>${own?g.n:'？？？'}</b><span class="st">${'★'.repeat(g.r)}</span></div>`;
    if(!own)return head+`<div class="dt-body"><p class="dt-d dim">まだ見つけていない。${g.r>1?`${g.r}つめの次元（${dimName(g.r-1)}）から見つかる`:'冒険のどこかで見つかる'}</p></div><div class="dt-foot"></div>`;
    let ch='';
    if(!on){const n=GCMP.filter(([k])=>(g[k]||0)||(cur&&cur[k]||0)).slice(0,3);ch=n.map(([k,lab,f])=>{const a=cur&&cur[k]||0,b=g[k]||0;const s=chg(lab,f(a),f(b));return a<b?s:a>b?s.replace('class="b"','class="b dn"'):s}).join('')}
    const note=run?'つぎの冒険から':'';
    return head+`<div class="dt-body"><p class="dt-d">${gearDesc(g)||'—'}</p>${ch?`<div class="dt-ch">${ch}</div>`:''}</div>`+
      `<div class="dt-foot"><span class="note">${note}</span>${on?'<button class="dt-btn alt" type="button" data-act="off">はずす</button>':'<button class="dt-btn" type="button" data-act="on">つける</button>'}</div>`;
  }
  if(shopTab==='skill'){
    const k=SKILL_ID[sel];if(!k)return '';
    const has=meta.sk.own.includes(k.id),on=meta.sk.eq.includes(k.id);
    const what=`${SKILL_AIM[k.aim]||'すぐ効く'}　使うと${k.ct}マス休む`;
    let foot;
    if(swap)foot=`<span class="note">入れかえる枠を上でえらぶ</span><button class="dt-sub" type="button" data-act="cancel">やめる</button>`;
    else if(!has)foot=`${undo('sk',k.id)}<span class="note"></span>${meta.bank>=k.cost?coinBtn('覚える',k.cost):short(k.cost)}`;
    else foot=`${undo('sk',k.id)}<span class="note">${run?'つぎの冒険から':''}</span>${on?'<button class="dt-btn alt" type="button" data-act="unset">はずす</button>':'<button class="dt-btn" type="button" data-act="set">セットする</button>'}`;
    return `<span class="dt-art">${svg(SK_ART[k.id])}</span><div class="dt-head"><b>${k.n}</b>${on?'<span class="tag on">セット中</span>':''}</div>`+
      `<div class="dt-body"><p class="dt-d">${k.d}</p><p class="dt-d dim">${what}</p></div><div class="dt-foot">${foot}</div>`;
  }
  return '';
}
function shopMarks(){
  const b=meta.bank,canU=f=>UPS.some(u=>!!u.deck===f&&meta.up[u.k]<u.max&&u.cost(meta.up[u.k])<=b);
  const mk=(id,cls,txt)=>{const m=$(id).querySelector('.mk');m.className='mk'+(cls?' '+cls:'');m.textContent=txt||''};
  mk('tab-up',canU(false)?'coin':'');mk('tab-deck',canU(true)?'coin':'');
  const nn=(meta.newg||[]).length;mk('tab-gear',nn?'new':'',nn?String(nn):'');
  mk('tab-skill',SKILLS.some(k=>!meta.sk.own.includes(k.id)&&k.cost<=b)?'coin':'');
}
function pickDefault(){ // a tab never opens with nothing on the pinned paper
  if(shopTab==='gear'){const s=GEAR_ID[shopSel.gear];if(!s||s.s!==gearSlot){const nw=(meta.newg||[]).map(x=>GEAR_ID[x]).find(g=>g&&g.s===gearSlot);
    shopSel.gear=nw?nw.id:meta.gear.eq[gearSlot]||((GEAR.find(g=>g.s===gearSlot&&owned(g.id))||GEAR.find(g=>g.s===gearSlot)||{}).id)||null}}
  if(shopTab==='skill'&&!SKILL_ID[shopSel.skill])shopSel.skill=meta.sk.eq.find(Boolean)||SKILLS[0].id;
}
function renderShop(fresh){
  pickDefault();
  $('sh-bank').textContent=nf(meta.bank);
  for(const [k,tab,panel,name] of [['up','tab-up','sh-up','能力'],['gear','tab-gear','sh-gear','装備'],['skill','tab-skill','sh-skill','スキル'],['deck','tab-deck','sh-deck','積み木の箱']]){
    const on=k===shopTab;$(tab).setAttribute('aria-selected',on);$(panel).hidden=!on;if(on)$('sh-title').textContent=name;
  }
  if(shopTab==='up')$('sh-up').innerHTML='<div class="sh-sheet">'+UPS.filter(u=>!u.deck).map(upRow).join('')+'</div>';
  if(shopTab==='deck')$('sh-deck').innerHTML=mixHTML()+'<div class="sh-sheet">'+UPS.filter(u=>u.deck&&MIX_OF[u.k]!=null).map(upRow).join('')+'</div><p class="sh-cap">のっている物</p><div class="sh-sheet">'+UPS.filter(u=>u.deck&&MIX_OF[u.k]==null).map(upRow).join('')+'</div>';
  if(shopTab==='gear')$('sh-gear').innerHTML=gearHTML();
  if(shopTab==='skill')$('sh-skill').innerHTML=skillHTML();
  const d=$('sh-det');d.innerHTML=detailHTML();
  if(fresh)$('sh-body').scrollTop=0;
  shopMarks();
  if(shopTab==='gear'&&meta.newg&&meta.newg.includes(shopSel.gear)){meta.newg=meta.newg.filter(x=>x!==shopSel.gear);saveMeta()} // seen: the NEW goes after this look
}
function choose(key){ // a tap on the list: only the pinned paper changes
  if(shopSel[shopTab]===key)return;
  shopSel[shopTab]=key;detT=performance.now();renderShop();
  const d=$('sh-det');if(!REDUCED){d.classList.remove('flash');void d.offsetWidth;d.classList.add('flash')}
}
function shopAct(act){
  if(performance.now()-detT<250)return; // a tap that just chose cannot also buy
  const sel=shopSel[shopTab];let el=$('sh-body').querySelector(`.sel`),msg=false;
  if(act==='buy'&&(shopTab==='up'||shopTab==='deck')){
    const u=UPS.find(x=>x.k===sel),l=meta.up[sel],c=u&&u.cost(l);if(!u||l>=u.max||meta.bank<c)return;
    meta.bank-=c;meta.up[sel]++;visit.push({t:'up',key:sel,c});msg=true;
  }
  if(act==='buy'&&shopTab==='skill'){const k=SKILL_ID[sel];if(!k||meta.sk.own.includes(k.id)||meta.bank<k.cost)return;meta.bank-=k.cost;meta.sk.own.push(k.id);visit.push({t:'sk',key:k.id,c:k.cost});msg=true}
  if(act==='undo'){
    const t=shopTab==='skill'?'sk':'up',j=bought(t,sel);if(j<0)return;const v=visit.splice(j,1)[0];meta.bank+=v.c;
    if(t==='up')meta.up[sel]=Math.max(0,meta.up[sel]-1);else{meta.sk.own=meta.sk.own.filter(x=>x!==sel);meta.sk.eq=meta.sk.eq.map(x=>x===sel?null:x)}
  }
  if(act==='on'){const g=GEAR_ID[sel];if(g&&owned(g.id))meta.gear.eq[g.s]=g.id}
  if(act==='off'){const g=GEAR_ID[sel];if(g)meta.gear.eq[g.s]=null}
  if(act==='set'){const eq=meta.sk.eq,f=eq.indexOf(null);if(f>=0)eq[f]=sel;else{swap=sel;renderShop();return}}
  if(act==='unset')meta.sk.eq=meta.sk.eq.map(x=>x===sel?null:x);
  if(act==='cancel'){swap=null;renderShop();return}
  saveMeta();renderShop();
  el=$('sh-body').querySelector('.sel');
  if(el&&(act==='on'||act==='set'||msg))el.classList.add('got');
  if(msg&&el){fly($('sh-bankp'),SPR.coin,el.querySelector('.ri-art,svg')||el);bump($('sh-bankp'));const a=mid(el);if(a)bits(a.x,a.y,12,['#ffe58a','#fff','#8fe0a8'],a.w*.5,5)}
  if(act==='undo')bump($('sh-bankp'));
}
function setShopTab(t){if(swap)swap=null;shopTab=t;renderShop(true)}
function leaveShop(){visit=[];swap=null} // what was bought is kept for good from here
function showShop(tab){
  if(tab)shopTab=tab;visit=[];swap=null;
  const ti=(id,a)=>{$(id).querySelector('.ti').innerHTML=ico(a)};
  ti('tab-up',SPR.heart);ti('tab-gear',SPR.shield);ti('tab-skill',SK_ART.turn?`<g transform="translate(50 50) scale(.6) translate(-50 -50)">${SK_ART.turn}</g>`:STAR(50,50,20));ti('tab-deck',SPR.box);
  $('sh-home-i').innerHTML=ico(SPR.door);$('sh-coin-i').innerHTML=ico(SPR.coin);
  $('sh-go').querySelector('.go-t').textContent=run?'つづき':'あそぶ';$('sh-go').querySelector('.go-s').textContent=run?placeName(rowOf(run.at)):'';
  renderShop(true);show('s-shop');
}
