# 11/5 しょーくん「ブーメランなど手持ちの敵を倒す系は、手持ちの中で倒し切って ふつうの道に戻して」
# 手持ちの敵は、何かが当たったら その場でたおれる（金貨はもらえる）。アヒルは今までどおり魔法と毒が効かない
import sys  # あとで：3回置くごとに のときは「、」なし（カードで1行に入るように）。PQ に toysAct を足した
P='games/path-quest/index.html'
s=open(P,encoding='utf-8').read()
R=[
 ("function handHit(k,dmg,cls){ // a toy in the hand takes damage; it may break",
  "function handHit(k,dmg,cls){ // a toy in the hand that is hit is beaten for good: the block goes back to a plain path"),
 ("bump(el);return} // the rubber duck shrugs it off\n  e.hp-=dmg;",
  "bump(el);return} // the rubber duck shrugs it off\n  e.hp=0;"),
 ("handHit(k,d,'mag');renderHand();hit=true;\n    }",
  "handHit(k,d,'toy');renderHand();hit=true;\n    }"),
 ("    const ev=isEvo('boomer'),d=toyDmg(ev?150:L5(TOY.boomer.p,bm));\n    let ks=shuffle(handFoes());if(!ev)ks=ks.slice(0,L5(TOY.boomer.n,bm));\n    if(ks.length){\n",
  "    const ev=isEvo('boomer'),d=toyDmg(100);run.bmc=(run.bmc|0)+1;\n    let ks=ev||run.bmc>=L5(TOY.boomer.e,bm)?shuffle(handFoes()):[];if(!ev)ks=ks.slice(0,L5(TOY.boomer.n,bm));\n    if(ks.length){run.bmc=0;\n"),
 ("ks.forEach(k=>handHit(k,d,'mag'));renderHand();hit=true;",
  "ks.forEach(k=>handHit(k,d,'toy'));renderHand();hit=true;"),
 ("if(gm>1&&e.hp<=d)e.gold*=gm;handHit(k,d,'mag');",
  "if(gm>1)e.gold*=gm;handHit(k,d,'toy');"),
 ("  boomer:{n:[1,1,2,2,3],p:[40,50,60,70,90]},",
  "  boomer:{e:[3,2,2,1,1],n:[1,1,2,2,3]},"),
 ("    case 'boomer':return `置くたび、手持ちの敵${g(t.n)}体へ（攻撃${g(t.p)}%）`;",
  "    case 'boomer':return `${g(t.e)>1?g(t.e)+'回置くごとに':'置くたび、'}手持ちの敵${g(t.n)}体をたおす`;"),
 ("  boomer:'手持ちの敵ぜんぶへ（攻撃150%）',",
  "  boomer:'置くたび、手持ちの敵ぜんぶをたおす',"),
 ("a.push(`戦うたび 手持ちの敵${g.hand+(g.rng||0)}体に魔法${g.mag}`)",
  "a.push(`戦うたび 手持ちの敵${g.hand+(g.rng||0)}体を魔法でたおす`)"),
 ("a.push(`${g.pint}マスごとに 手持ちの敵1体を毒に（毎マス${g.psn||1}）`)",
  "a.push(`${g.pint}マスごとに 手持ちの敵1体を毒でたおす`)"),
 ("const c=run.hand.filter(t=>t&&t.e&&t.e.k==='foe'&&!t.e.psn&&!(QK[t.e.t]||{}).nomag);if(c.length){c[rnd(c.length)].e.psn=Math.max(1,qv('psn'))*PM()*(run.pmag||1);hand=true}",
  "const c=run.hand.map((t,k)=>t&&t.e&&t.e.k==='foe'&&!(QK[t.e.t]||{}).nomag?k:-1).filter(k=>k>=0);if(c.length){handHit(c[rnd(c.length)],1,'psn');hand=true}"),
 ("n:'毒の小びん',r:3,psn:1,pint:-1}", "n:'毒の小びん',r:3,pint:-1}"),
]
for a,b in R:
  n=s.count(a)
  if n!=1: sys.exit(f'NG {n}: {a[:60]}')
  s=s.replace(a,b)
open(P,'w',encoding='utf-8').write(s)
print('ok',len(R))
