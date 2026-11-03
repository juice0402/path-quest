import re,base64,io,json
import numpy as np
from PIL import Image,ImageFilter
SRC='/home/claude/pq/orig.html'
s=open(SRC).read().split('\n')[824]
SH=['house','tree','snowman','wall','brick','soldier','bugle','cannon','robot','boss','king','archer','mage','clown','mason','hero']
out=[];tot=0
for m in re.finditer(r'<symbol id="a-([a-z0-9]+)" viewBox="([^"]+)" preserveAspectRatio="([^"]+)"><image href="data:image/webp;base64,([^"]+)" width="([^"]+)" height="([^"]+)"/></symbol>',s):
    n=m.group(1)
    if n not in SH:continue
    im=Image.open(io.BytesIO(base64.b64decode(m.group(4)))).convert('RGBA')
    w,h=im.size
    a=im.getchannel('A').resize((max(8,w//2),max(8,h//2)),Image.LANCZOS)
    a=a.filter(ImageFilter.GaussianBlur(1.6))
    A=(np.asarray(a).astype(np.float32)*0.4).astype(np.uint8)
    rgba=np.dstack([np.full_like(A,56),np.full_like(A,30),np.full_like(A,46),A])
    b=io.BytesIO();Image.fromarray(rgba,'RGBA').save(b,'WEBP',quality=50,alpha_quality=60,method=6)
    d=base64.b64encode(b.getvalue()).decode();tot+=len(d)
    out.append(f'<symbol id="a-{n}-sh" viewBox="{m.group(2)}" preserveAspectRatio="{m.group(3)}"><image href="data:image/webp;base64,{d}" width="{m.group(5)}" height="{m.group(6)}"/></symbol>')
open('/home/claude/pq/build/shadows.html','w').write('<svg class="art-defs" width="0" height="0" aria-hidden="true" focusable="false"><defs>'+''.join(out)+'</defs></svg>')
print('shadows',len(out),'b64 bytes',tot)
# critters
C='bee bfly bfly2 lady dfly snail squir frog duckl bunny peng robin tit mouse top wduck cat fish'.split()
R={};tot=0
def enc(im,mx=96):
    im=im.copy();im.thumbnail((mx,mx),Image.LANCZOS)
    b=io.BytesIO();im.save(b,'WEBP',quality=84,alpha_quality=90,method=6)
    return base64.b64encode(b.getvalue()).decode(),im.size
for n in C:
    im=Image.open(f'/home/claude/pq/cut/{n}.png').convert('RGBA')
    if n=='snail':im=im.transpose(Image.FLIP_LEFT_RIGHT) # face right like the others
    d,sz=enc(im);R[n]=[d,sz];tot+=len(d)
# heads that peek from behind a house or a tree
cat=Image.open('/home/claude/pq/cut/cat.png').convert('RGBA');w,h=cat.size
d,sz=enc(cat.crop((0,0,w,int(h*.56))),64);R['cath']=[d,sz];tot+=len(d)
sq=Image.open('/home/claude/pq/cut/squir.png').convert('RGBA');w,h=sq.size
d,sz=enc(sq.crop((int(w*.5),0,w,int(h*.5))),64);R['sqh2']=[d,sz];tot+=len(d)
json.dump(R,open('/home/claude/pq/build/crit.json','w'))
print('critters',len(R),'b64 bytes',tot,{k:v[1] for k,v in R.items()})
# bee and dragonfly: wings and body apart, so the wings can beat
from scipy import ndimage as ndi
for n in ('bee','dfly'):
    im=Image.open(f'/home/claude/pq/cut/{n}.png').convert('RGBA');A=np.asarray(im).astype(int)
    r,g,b,a=[A[...,k] for k in range(4)]
    mx=np.maximum(np.maximum(r,g),b);mn=np.minimum(np.minimum(r,g),b)
    w=(a>20)&(b>=r-4)&(b>150)&((mx-mn)<(90 if n=='bee' else 40))
    lab,k=ndi.label(w);sz=ndi.sum(w,lab,range(1,k+1));big=[i+1 for i,s in enumerate(sz) if s>800]
    w=np.isin(lab,big);w=ndi.binary_opening(w,iterations=3);w=ndi.binary_closing(w,iterations=2)
    wing=A.copy();wing[...,3]=np.where(w,a,0)
    body=A.copy();body[...,3]=np.where(w,0,a)
    for part,arr in (('w',wing),('b',body)):
        d,sz2=enc(Image.fromarray(arr.astype(np.uint8),'RGBA'));R[f'{n}-{part}']=[d,sz2];tot+=len(d)
json.dump(R,open('/home/claude/pq/build/crit.json','w'))
print('with wings',tot)
# skill and reward-toy icons from Canva, as symbols centred in their box
out=[];tot=0
SK='turn cross clear box cannon wind guard bugle rain magnet candy treasure'.split()
IT='plane top bomb boomer bubble spring block cookie clover honey cat dice clock'.split()
for pre,names in (('sk',SK),('it',IT)):
    for n in names:
        im=Image.open(f'/home/claude/pq/cut2/{n}.png').convert('RGBA');im.thumbnail((128,128),Image.LANCZOS)
        b=io.BytesIO();im.save(b,'WEBP',quality=84,alpha_quality=90,method=6);d=base64.b64encode(b.getvalue()).decode();tot+=len(d)
        w,h=im.size
        out.append(f'<symbol id="a-{pre}_{n}" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid meet"><image href="data:image/webp;base64,{d}" width="{w}" height="{h}"/></symbol>')
open('/home/claude/pq/build/icons.html','w').write('<svg class="art-defs" width="0" height="0" aria-hidden="true" focusable="false"><defs>'+''.join(out)+'</defs></svg>')
print('icons',len(out),'b64',tot)
