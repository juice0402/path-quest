# 音のしくみ（tools/audio/sound.js）を、ゲームの SND の印のあいだに入れる。何度でも走らせてよい
import re,sys,os
H=os.path.dirname(os.path.abspath(__file__))
P=os.path.join(H,'../../games/path-quest/src/page.html')  # 11/16: 直すのは src/page.html（index.html はビルドで作る）
s=open(P,encoding='utf-8').read()
js=open(os.path.join(H,'sound.js'),encoding='utf-8').read().strip()
B,E='/*SND:begin*/','/*SND:end*/'
blk=B+'\n'+js+'\n'+E
if B in s:
  s=re.sub(re.escape(B)+r'.*?'+re.escape(E),lambda m:blk,s,flags=re.S)
else:
  a='/* test only: open with #fxtest'
  if s.count(a)!=1: sys.exit('NG anchor')
  s=s.replace(a,blk+'\n\n'+a)
open(P,'w',encoding='utf-8').write(s)
print('ok',len(js))
print('つぎに node tools/build/build.mjs で index.html を作る')
