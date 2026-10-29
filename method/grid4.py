import cv2,numpy as np,sys
fn=sys.argv[1]; sp0=float(sys.argv[2])
im=cv2.imread(fn,0).astype(float); H,W=im.shape
D=(im<228).astype(float)
def sc(ang,ph,sp,hor):
    t=np.tan(np.radians(ang)); tot=0;n=0
    if hor:
        xs=np.arange(0,W,2)
        for k in range(-3,int(H/sp)+4):
            y=ph+k*sp+xs*t; m=(y>=0)&(y<H-1)
            if m.sum()<W/4: continue
            tot+=D[y[m].round().astype(int),xs[m]].mean(); n+=1
    else:
        ys=np.arange(0,H,2)
        for k in range(-3,int(W/sp)+4):
            x=ph+k*sp+ys*t; m=(x>=0)&(x<W-1)
            if m.sum()<H/4: continue
            tot+=D[ys[m],x[m].round().astype(int)].mean(); n+=1
    return tot/max(n,1)
res={}
for hor in [1,0]:
    best=(0,)
    for sp in np.arange(sp0*0.97,sp0*1.03,sp0*0.0025):
      for ang in np.arange(-2.5,2.51,0.1):
        for ph in np.arange(0,sp,0.5):
            s=sc(ang,ph,sp,hor)
            if s>best[0]: best=(s,ang,ph,sp)
    s,a0,p0,s0=best
    for sp in np.arange(s0-sp0*0.003,s0+sp0*0.003,sp0*0.0003):
      for ang in np.arange(a0-0.1,a0+0.1,0.01):
        for ph in np.arange(p0-1,p0+1,0.1):
            s=sc(ang,ph,sp,hor)
            if s>best[0]: best=(s,ang,ph,sp)
    print('h' if hor else 'v',[round(float(v),4) for v in best])
