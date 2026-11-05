"""11/5 m: the very first steps for a new player.

しょーくん「そもそも最初はくるっと回すのスキルもいらないかもね」
「初期配置は、上に直線を置くしかないようにしておこうかな。上にしか置けるアイコンが出なくて、指が指しているパネルは上直線で、それしか置けないように」
- a new player starts with no skill (くるっと回す stays in the shop from the start, 20 coins). Players who already have it keep it
- while the best climb is under 3 steps (the same time as the finger and the up arrow), a climb starts with a lesson:
  the start panel opens only upward, the cell above is cleared, the last block in hand is a plain straight (no toy, no coin),
  and only that block can be put down (the others are dull). The finger points at it, then at the cell above
- the lesson ends with the first step walked, a reroll or a skill
Applied once (like the other tweak_* files). Check: tools/test/intro_check.py
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


# no skill for a new player
sub("k.own.filter(id=>SKILL_ID[id]):['turn'],seq=[null,null,null];",
    "k.own.filter(id=>SKILL_ID[id]):[],seq=[null,null,null];")
sub("  if(!k)seq[0]='turn';else [0,1,2].forEach(",
    "  if(k)[0,1,2].forEach(")

# the lesson at the start of a climb
sub("  aceNew=run.hand.map((t,k)=>t.m===15?k:-1).filter(k=>k>=0);\n  sel=-1;aim=null;hideSay();save();",
    "  run.intro=meta.far<3?1:0; /* 11/5: the first climbs: one straight block, and it can only go up */\n"
    "  if(run.intro){const up=cellAt(idOf(2,2));if(up){up.rock=0;up.foe=null}run.hand[run.hand.length-1]={m:5,e:null,c:rnd(BLOCKS.length),intro:1}}\n"
    "  aceNew=run.hand.map((t,k)=>t.m===15?k:-1).filter(k=>k>=0);\n  sel=-1;aim=null;hideSay();save();")
sub("c.start?11:c.tile?c.tile.m:0",
    "c.start?(run.intro?1:11):c.tile?c.tile.m:0")
sub("const fits=(t,j,F)=>!!t&&(",
    "const fits=(t,j,F)=>!!t&&!(run&&run.intro&&!t.intro)&&(")
sub("const anyFit=(t,F)=>{if(!t)return false;",
    "const anyFit=(t,F)=>{if(!t||(run&&run.intro&&!t.intro))return false;")

# the lesson ends
sub("FXH.add('step',()=>document.querySelectorAll('.upcue').forEach(x=>x.remove()));",
    "FXH.add('step',()=>{document.querySelectorAll('.upcue').forEach(x=>x.remove());if(run)run.intro=0});")
sub("  run.hand=run.hand.map(()=>makeTile(lv));",
    "  run.intro=0;run.hand=run.hand.map(()=>makeTile(lv));")
sub("  if(!d||(d.aim&&!targets(d.aim).includes(x)))return; /* pointed at something it cannot take */",
    "  if(!d||(d.aim&&!targets(d.aim).includes(x)))return; /* pointed at something it cannot take */\n"
    "  run.intro=0; /* 11/5: a skill ends the first-step lesson */")

P.write_text(s, encoding='utf-8')
print('ok')
