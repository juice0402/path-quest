# 11/4 HPが少ないとき（tweak_1104m.py のあとに1回だけ）
#  最大HPの3割以下：ステータスのハートがドクンドクンと脈打ち、HPの数字が赤。ゲージの残りが赤くゆっくり点滅
#  2割以下（または残り1〜2）：脈がはやくなる。そうなったとき1回だけ メッセージ窓に「HPがのこりわずか」（青）
#  光る輪やグラデーションは使わない。動きを減らす設定では 脈はなく、色だけ
import sys
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)

rep("  $('hp').classList.toggle('dying',preview>0&&preview>=hp);\n}",
"""  $('hp').classList.toggle('dying',preview>0&&preview>=hp);
  const low=hp>0&&hp<=Math.max(2,m*.3),crit=hp>0&&hp<=Math.max(2,Math.floor(m*.2)); // the heart beats when the knight is about to fall (11/4)
  $('hp').classList.toggle('low',low);$('hp').classList.toggle('crit',crit);
  if(crit&&!run.lowSaid){run.lowSaid=1;note('HPがのこりわずか','bad')}else if(!low)run.lowSaid=0;
}""")
CSS = '''/* HP low: the heart beats, the number and what is left of the gauge turn red */
.hp.low>span>svg{transform-origin:50% 60%;animation:hbeat 1s ease-in-out infinite}
.hp.crit>span>svg{animation-duration:.55s}
@keyframes hbeat{0%,40%,100%{scale:1}12%{scale:1.32}26%{scale:1.08}32%{scale:1.22}}
.hp.low b{color:#d42a48}
.hp.low .blocks u{animation:hlow 1s ease-in-out infinite}
.hp.crit .blocks u{animation-duration:.55s}
@keyframes hlow{50%{background:#c81e3c}}
.hp.low .blocks i{background:#f3c2cc}
@media (prefers-reduced-motion:reduce){.hp.low>span>svg,.hp.low .blocks u{animation:none}.hp.low .blocks u{background:#c81e3c}}
'''
rep('/* ===== end of 11/4 ===== */', CSS + '/* ===== end of 11/4 ===== */')
open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
