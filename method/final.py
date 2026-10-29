import json,pickle,numpy as np
from pyproj import Transformer
from shapely.geometry import Polygon,LineString,Point,mapping,MultiPolygon
from shapely.ops import unary_union,transform
G,b=pickle.load(open('G.pkl','rb'))
toW=Transformer.from_crs(27700,4326,always_xy=True).transform
toB=Transformer.from_crs(4326,27700,always_xy=True).transform
def W(g): 
    g=transform(lambda x,y,z=None: toW(x,y), g)
    return json.loads(json.dumps(mapping(g)), parse_float=lambda s: round(float(s),6))
META={
 'solar':dict(name='Solar PV panels (and BESS within solar areas)',h=4.5,col='#f5c518'),
 'datacentre_west':dict(name='Data Centre Campus, 400kV substation & BESS (Western Site)',h=25,col='#ff7b00'),
 'substation_bess_east':dict(name='Eastern substation & battery storage (BESS)',h=8,col='#d646c4'),
 'walpole_substation':dict(name='New substation area at Walpole',h=8,col='#f9d8f7'),
 'biodiversity':dict(name='Biodiversity enhancement area',h=0,col='#0b6e1a'),
 'access_track':dict(name='Access track',h=0,col='#222222'),
 'cable_buried':dict(name='Underground cable corridor',h=0,col='#2b4cff'),
 'ohl_50':dict(name='Overhead line corridor – Western Cable Route (towers up to 50 m)',h=0,col='#9485ed'),
 'ohl_35':dict(name='Overhead line corridor – Eastern Cable Route (towers up to 35 m)',h=0,col='#70bfeb'),
}
F=[]
for k,g in G.items():
    g=g.simplify(1.0)
    F.append({'type':'Feature','properties':{'kind':k,'name':META[k]['name'],'height':META[k]['h'],'color':META[k]['col'],'area_ha':round(g.area/1e4,1)},'geometry':W(g)})
site=unary_union(list(G.values())).buffer(0.5).buffer(-0.5)
F.append({'type':'Feature','properties':{'kind':'boundary','name':'Indicative site boundary','area_ha':round(site.area/1e4)},'geometry':W(site.boundary)})
# OHL centrelines + indicative towers
towers=[]
for k,h,span in [('ohl_50',50,350),('ohl_35',35,300)]:
    ls=LineString(np.load(f'line_{k}.npy'))
    F.append({'type':'Feature','properties':{'kind':k+'_line','name':META[k]['name'],'height':h},'geometry':W(ls)})
    n=max(2,int(round(ls.length/span)))
    for i in range(n+1):
        p=ls.interpolate(i/n,normalized=True)
        sq=p.buffer(5,cap_style=3)  # 10 m tower base
        towers.append({'type':'Feature','properties':{'kind':'tower','height':h,'route':k},'geometry':W(sq)})
F+=towers
# separation buffers (300 m around major infrastructure)
major=unary_union([G['datacentre_west'],G['substation_bess_east']])
F.append({'type':'Feature','properties':{'kind':'buffer300','name':'300 m from major built infrastructure'},'geometry':W(major.buffer(300).boundary)})
json.dump({'type':'FeatureCollection','features':F},open('longmarsh.geojson','w'),separators=(',',':'))
# villages
V=[]
layers={'panels':G['solar'],'dc':G['datacentre_west'],'eastsub':G['substation_bess_east'],'walpole':G['walpole_substation'],
        'ohl':unary_union([LineString(np.load('line_ohl_50.npy')),LineString(np.load('line_ohl_35.npy'))]),'site':site}
for l in open('villages.txt'):
    la,lo,n=l.strip().split('|'); E,N=toB(float(lo),float(la)); p=Point(E,N)
    d={k:round(g.distance(p)) for k,g in layers.items()}
    # bearing to nearest infrastructure point
    from shapely.ops import nearest_points
    q=nearest_points(p,site)[1]; brg=(np.degrees(np.arctan2(q.x-E,q.y-N))+360)%360
    V.append({'name':n,'lat':float(la),'lon':float(lo),'d':d,'bearing':round(brg)})
V.sort(key=lambda v:v['d']['site'])
json.dump(V,open('villages.json','w'))
for v in V[:40]: print(v['name'],v['d'])
import os; print(os.path.getsize('longmarsh.geojson'))
