# cut a grid sheet of toys on white into transparent pieces
# usage: slice.py sheet.png cols rows name1,name2,... outdir
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
f,cols,rows,names,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4].split(','),sys.argv[5]
NEAR=int(sys.argv[6]) if len(sys.argv)>6 else 26
SOFT=float(sys.argv[7]) if len(sys.argv)>7 else 20
KEEP=float(sys.argv[8]) if len(sys.argv)>8 else 0
im=np.asarray(Image.open(f).convert('RGB')).astype(np.float32)
H,W,_=im.shape
d=(255-im).max(axis=2)            # how far from white
near=d<NEAR                          # candidate background
lab,n=ndi.label(near)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
bg=np.isin(lab,list(border))
# soft edge: in the background region alpha grows with distance from white
a=np.where(bg,np.clip((d-3)/SOFT,0,1),1.0)
a=ndi.gaussian_filter(a,0.6)*np.where(bg,1,1)
a=np.where(~bg,1.0,a)
rgb=im.copy()
aa=np.maximum(a,1e-3)[...,None]
rgb=np.where(a[...,None]<1,(rgb-(1-aa)*255)/aa,rgb)  # remove the white fringe
rgb=np.clip(rgb,0,255)
rgba=np.dstack([rgb,a*255]).astype(np.uint8)
fg=a>0.06
cw,ch=W/cols,H/rows
k=0
for r in range(rows):
  for c in range(cols):
    if k>=len(names):break
    nm=names[k];k+=1
    if nm=='-':continue
    x0,x1,y0,y1=int(c*cw),int((c+1)*cw),int(r*ch),int((r+1)*ch)
    m=fg[y0:y1,x0:x1]
    # drop tiny specks
    l2,n2=ndi.label(m);
    if n2:
      sz=ndi.sum(m,l2,range(1,n2+1));keep=[i+1 for i,s in enumerate(sz) if s>max(40,KEEP*max(sz))]
      m=np.isin(l2,keep)
    ys,xs=np.nonzero(m)
    bx0,bx1,by0,by1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
    pad=4
    crop=rgba[y0+by0-pad:y0+by1+pad,x0+bx0-pad:x0+bx1+pad].copy()
    mm=np.pad(m[by0:by1,bx0:bx1],pad)
    crop[...,3]=np.where(mm|(crop[...,3]>0),crop[...,3],0)
    crop[...,3]=(crop[...,3]*ndi.binary_dilation(mm,iterations=2)).astype(np.uint8)
    Image.fromarray(crop).save(f'{out}/{nm}.png')
    print(nm,crop.shape[1],crop.shape[0])
