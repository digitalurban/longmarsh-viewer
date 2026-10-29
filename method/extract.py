import pymupdf as fitz, numpy as np, json
d=fitz.open('f1.pdf'); p=d[10]
CLASSES={(0.96,0.79,0.14):'solar',(0.0,0.0,1.0):'cable_buried',(0.98,0.85,0.97):'walpole_substation',
 (0.99,0.49,0.0):'datacentre_west',(0.84,0.27,0.77):'substation_bess_east',(0.0,0.37,0.02):'biodiversity',
 (0.44,0.75,0.92):'ohl_35',(0.58,0.52,0.93):'ohl_50',(0.0,0.0,0.0):'access_track'}
def rings(items):
    out=[];cur=[]
    for it in items:
        if it[0]=='l': a,b=it[1],it[2]
        elif it[0]=='c': a,b=it[1],it[4]
        elif it[0]=='re':
            r=it[1]; out.append([(r.x0,r.y0),(r.x1,r.y0),(r.x1,r.y1),(r.x0,r.y1)]); continue
        else: continue
        if cur and (abs(cur[-1][0]-a.x)>0.01 or abs(cur[-1][1]-a.y)>0.01):
            out.append(cur); cur=[]
        if not cur: cur.append((a.x,a.y))
        if it[0]=='c':
            # sample bezier
            P=[np.array([q.x,q.y]) for q in it[1:5]]
            for t in np.linspace(0.25,1,4):
                q=(1-t)**3*P[0]+3*(1-t)**2*t*P[1]+3*(1-t)*t**2*P[2]+t**3*P[3]; cur.append(tuple(q))
        else: cur.append((b.x,b.y))
    if cur: out.append(cur)
    return [r for r in out if len(r)>=3]
feats=[]; seen_inset=False
for i,x in enumerate(p.get_drawings()):
    r=x['rect']
    if i==101: seen_inset=True
    if r.x0<19 or r.x1>958 or r.y1>642: continue
    if seen_inset and r.x0>=500 and r.x1<=726 and r.y0>=30 and r.y1<=227: continue
    f=x.get('fill')
    if f and 'f' in x['type']:
        key=tuple(round(c,2) for c in f)
        cls=CLASSES.get(key)
        if not cls: continue
        if r.width>900: continue
        rs=rings(x['items'])
        feats.append({'cls':cls,'rings':rs,'i':i})
    c=x.get('color')
    if c and abs(c[0]-0.89)<0.02 and abs(c[1]-0.1)<0.02 and x['type']=='s' and not seen_inset:
        feats.append({'cls':'boundary','rings':rings(x['items']),'i':i})
json.dump(feats,open('page11_feats.json','w'))
from collections import Counter
print(Counter(f['cls'] for f in feats)); print([(f['cls'],f['i'],len(f['rings']),[len(r) for r in f['rings']][:5]) for f in feats])
