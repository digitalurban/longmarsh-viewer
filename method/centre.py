import numpy as np,cv2,pickle
from shapely.geometry import LineString,MultiLineString
G,b=pickle.load(open('G.pkl','rb'))
def centreline(g,res=5):
    minx,miny,maxx,maxy=g.bounds
    W=int((maxx-minx)/res)+10;H=int((maxy-miny)/res)+10
    img=np.zeros((H,W),np.uint8)
    for p in getattr(g,'geoms',[g]):
        pts=np.array(p.exterior.coords); px=np.c_[(pts[:,0]-minx)/res+5,(maxy-pts[:,1])/res+5].astype(np.int32)
        cv2.fillPoly(img,[px],255)
    sk=cv2.ximgproc.thinning(img)
    ys,xs=np.nonzero(sk)
    P=np.c_[xs*res+minx-5*res, maxy-(ys-5)*res]
    return P
for k in ['ohl_50','ohl_35']:
    P=centreline(G[k]); print(k,len(P)); np.save(f'cl_{k}.npy',P)
