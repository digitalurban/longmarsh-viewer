import pickle,numpy as np,math,zipfile,json
from shapely.geometry import box,LineString,Polygon,MultiPolygon,Point
from shapely.ops import unary_union
from shapely import affinity
from pyproj import Transformer
G,_=pickle.load(open('G.pkl','rb'))
T=Transformer.from_crs(27700,4326,always_xy=True).transform
def ll(x,y): lo,la=T(x,y); return lo,la
# --- parameters (Scoping Report §4.4.6, 4.4.10, 4.4.11) ---
TILT=25; CLEAR=0.8; HMAX=4.5
DEPTH=(HMAX-CLEAR)/math.tan(math.radians(TILT))     # horizontal table depth
GAP=3.5                                            # presumption: mid of 2–5 m
PITCH=DEPTH+GAP; FENCE_OFF=3.2
def polys(g): return [p for p in getattr(g,'geoms',[g]) if p.geom_type=='Polygon']
from shapely.ops import unary_union as UU
excl=UU([G['ohl_50'],G['ohl_35'],G['cable_buried'],G['access_track'],G['biodiversity']]).buffer(5)
solar0=G['solar'].difference(excl).buffer(-FENCE_OFF)
# rotate so rows run true east-west (BNG grid convergence ~ +1.8 deg here)
from pyproj import Proj
CONV=math.degrees(math.atan2(*np.subtract(Transformer.from_crs(4326,27700,always_xy=True).transform(0.4,52.7),Transformer.from_crs(4326,27700,always_xy=True).transform(0.4,52.69))[:2]))
O=solar0.centroid
solar=affinity.rotate(solar0,CONV,origin=O)
print('convergence',round(CONV,3))
rows=[]
minx,miny,maxx,maxy=solar.bounds
y=miny
while y<maxy:
    strip=box(minx,y,maxx,y+DEPTH)
    inter=solar.intersection(strip)
    for p in polys(inter):
        # take full-depth row parts only: use the strip line at row centre to get x-extents
        seg=solar.intersection(LineString([(minx,y+DEPTH/2),(maxx,y+DEPTH/2)]))
        break
    seg=solar.intersection(LineString([(minx,y),(maxx,y)])).intersection(solar.intersection(LineString([(minx,y+DEPTH),(maxx,y+DEPTH)])).buffer(0.01).union(LineString([(minx,y),(maxx,y)]).buffer(0.01)) ) if False else None
    # x-extents valid on both edges: intersect south and north edge segments projected
    s=solar.intersection(LineString([(minx,y),(maxx,y)]))
    n=solar.intersection(LineString([(minx,y+DEPTH),(maxx,y+DEPTH)]))
    def iv(g):
        out=[]
        for l in getattr(g,'geoms',[g]):
            if l.geom_type=='LineString' and l.length>0:
                xs=[c[0] for c in l.coords]; out.append((min(xs),max(xs)))
        return out
    S=iv(s); N=iv(n)
    for a0,a1 in S:
        for b0,b1 in N:
            x0,x1=max(a0,b0),min(a1,b1)
            if x1-x0>=12: rows.append((x0,x1,y))
    y+=PITCH
L=sum(r[1]-r[0] for r in rows)
print('rows',len(rows),'row length km',round(L/1000),'panel plan area ha',round(L*DEPTH/1e4),'depth',round(DEPTH,2),'pitch',round(PITCH,2))
pickle.dump((rows,CONV,(O.x,O.y)),open('rows.pkl','wb'))
