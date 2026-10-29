import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import LineString
def order(P):
    tree=cKDTree(P)
    # endpoint: point farthest from centroid-farthest
    c=P.mean(0); s=np.argmax(((P-c)**2).sum(1))
    used=np.zeros(len(P),bool); path=[s]; used[s]=True
    cur=s
    while True:
        d,i=tree.query(P[cur],k=min(30,len(P)))
        nxt=[j for dd,j in zip(d,i) if not used[j] and dd<40]
        if not nxt: break
        cur=nxt[0]; used[cur]=True; path.append(cur)
    return P[path], used.mean()
for k in ['ohl_50','ohl_35']:
    P=np.load(f'cl_{k}.npy'); L,cov=order(P)
    ls=LineString(L).simplify(15)
    print(k,'coverage',round(cov,3),'length km',round(ls.length/1000,2))
    np.save(f'line_{k}.npy',np.array(ls.coords))
