import json,numpy as np
from geo import to_bng
from pyproj import Transformer
from shapely.geometry import Polygon,MultiPolygon,LineString,mapping,shape
from shapely.ops import unary_union
from shapely.validation import make_valid
T=Transformer.from_crs(27700,4326,always_xy=True)
feats=json.load(open('page11_feats.json'))
E0,N0=547000,318000
def bng(r): return to_bng(11,r,E0,N0)
groups={}
for f in feats:
    if f['cls']=='boundary': continue
    polys=[]
    rings=[bng(r) for r in f['rings']]
    # treat first ring as outer, others: holes if inside outer else separate
    P=[make_valid(Polygon(r)) for r in rings]
    g=P[0]
    for q in P[1:]:
        if g.contains(q.representative_point()): g=g.difference(q)
        else: g=g.union(q)
    groups.setdefault(f['cls'],[]).append(g)
G={k:make_valid(unary_union(v)) for k,v in groups.items()}
# remove datacentre & east substation & access from solar
G['solar']=G['solar'].difference(G['datacentre_west'].buffer(0.5)).difference(G['substation_bess_east'].buffer(0.5))
if 'biodiversity' in G: G['solar']=G['solar'].difference(G['biodiversity'])
for k,g in G.items(): print(k, round(g.area/1e4,1),'ha')
# boundary: page 11 boundary path
bpts=[bng(f['rings'][0]) for f in feats if f['cls']=='boundary' and f['rings']]
json.dump({k:mapping(v) for k,v in G.items()},open('bng_groups.json','w'))
np.save('boundary_main.npy',bpts[0])
import pickle; pickle.dump((G,bpts),open('G.pkl','wb'))
