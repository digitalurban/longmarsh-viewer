import numpy as np
t=np.tan(np.radians(1.0))
GRID={ # page: (h_phase,h_sp,v_phase,v_sp)
 11:(62.4,64.8135,61.8,64.7747), 10:(19.0,178.7529,8.4,178.7529), 8:(55.5,231.2823,197.5,231.2823),
 7:(129.0,203.0166,25.3,202.9558), 9:(62.8,151.2732,81.3,151.3186)}
def frac(pg,pts):
    hp,hs,vp,vs=GRID[pg]; pts=np.asarray(pts,float)
    u=(pts[:,0]-19.9)*1.99893; v=(pts[:,1]-19.5)*1.99968
    j=(u-vp+v*t)/vs; k=(v-hp-u*t)/hs
    return j,k
def to_bng(pg,pts,E0,N0):
    j,k=frac(pg,pts); return np.c_[E0+1000*j, N0-1000*k]
