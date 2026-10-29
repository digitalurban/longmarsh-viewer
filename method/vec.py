import pymupdf as fitz, numpy as np
d=fitz.open('f1.pdf')
def red_paths(pn):
    out=[]
    for x in d[pn].get_drawings():
        c=x.get('color')
        if c and abs(c[0]-0.89)<0.02 and abs(c[1]-0.1)<0.02 and x['rect'].width<940 and x['rect'].x0>15 and x['rect'].x1<960:
            pts=[]
            for it in x['items']:
                if it[0]=='l': pts += [it[1],it[2]]
                elif it[0]=='c': pts += [it[1],it[4]]
                elif it[0]=='re': r=it[1]; pts+=[r.tl,r.br]
            if pts: out.append(np.array([[p.x,p.y] for p in pts]))
    return out
