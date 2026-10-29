import pickle,numpy as np,math,zipfile
from shapely.geometry import box,LineString,Polygon,Point
from shapely.ops import unary_union
from shapely import affinity
from pyproj import Transformer
G,_=pickle.load(open('G.pkl','rb')); rows,CONV,ORG=pickle.load(open('rows.pkl','rb'))
T=Transformer.from_crs(27700,4326,always_xy=True).transform
TILT=25; CLEAR=0.8; HMAX=4.5; DEPTH=(HMAX-CLEAR)/math.tan(math.radians(TILT)); TABLE=40.0; TGAP=1.0
def c(x,y,z): lo,la=T(x,y); return f"{lo:.6f},{la:.6f},{z:g}"
def esc(s): return s.replace('&','&amp;').replace('<','&lt;')
SRC="Source: Longmarsh Green Energy EIA Scoping Report (Oct 2026), Fig. 1-3 and §4.4."
AW="PRESUMPTION – AWAITING INFORMATION. "
STY='''<Style id="panel"><LineStyle><color>ff3a2a1a</color><width>0.5</width></LineStyle><PolyStyle><color>ff5a3a22</color></PolyStyle></Style>
<Style id="deer"><LineStyle><color>ff2f6f8f</color><width>1</width></LineStyle><PolyStyle><color>662f6f8f</color></PolyStyle></Style>
<Style id="palisade"><LineStyle><color>ff606060</color><width>1.5</width></LineStyle><PolyStyle><color>aa707070</color></PolyStyle></Style>
<Style id="dc"><LineStyle><color>ff0e7cc2</color><width>1</width></LineStyle><PolyStyle><color>dd0e8ad6</color></PolyStyle></Style>
<Style id="tower"><LineStyle><color>ffc0c0c0</color><width>1</width></LineStyle><PolyStyle><color>ff9a9a9a</color></PolyStyle></Style>
<Style id="wire"><LineStyle><color>ff202020</color><width>1.5</width></LineStyle></Style>
<Style id="cctv"><IconStyle><scale>0.5</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon></IconStyle><LineStyle><color>ff303030</color><width>2</width></LineStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="light"><IconStyle><scale>1.1</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/caution.png</href></Icon></IconStyle></Style>
<Style id="zone"><LineStyle><color>ff1c19e3</color><width>2.5</width></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>'''
def doc(name,desc,body):
    return f'<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>{esc(name)}</name><description>{esc(desc)}</description>{STY}{body}</Document></kml>'
def wall(line_coords,h,style,name,desc):
    co=" ".join(c(x,y,h) for x,y in line_coords)
    return f'<Placemark><name>{esc(name)}</name><description>{esc(desc)}</description><styleUrl>#{style}</styleUrl><LineString><extrude>1</extrude><altitudeMode>relativeToGround</altitudeMode><coordinates>{co}</coordinates></LineString></Placemark>'
def block(poly,h,style,name,desc):
    ring=" ".join(c(x,y,h) for x,y in poly.exterior.coords)
    return f'<Placemark><name>{esc(name)}</name><description>{esc(desc)}</description><styleUrl>#{style}</styleUrl><Polygon><extrude>1</extrude><altitudeMode>relativeToGround</altitudeMode><outerBoundaryIs><LinearRing><coordinates>{ring}</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>'
def rings(g):
    out=[]
    for p in getattr(g,'geoms',[g]):
        if p.geom_type!='Polygon': continue
        out.append(list(p.exterior.coords)); out+= [list(i.coords) for i in p.interiors]
    return out
# ---------- panels, split by site (west x<560000) ----------
pdesc=AW+f"Solar table drawn to the published parameters: fixed tilt {TILT}° (§4.4.6 allows 20–25°), lowest edge 0.8 m, top edge 4.5 m, south-facing (§4.4.7), rows 3.5 m apart (§4.4.10 allows 2–5 m), set 3.2 m inside the fence (§4.4.11). Row positions, tables, trackers, east–west fields, tracks, inverters and the 30 m stand-off from homes are NOT yet published. "+SRC
def panels(sel):
    out=[]
    for x0,x1,y in rows:
        if not sel(affinity.rotate(Point(x0,y),-CONV,origin=ORG).x): continue
        n=max(1,int((x1-x0+TGAP)//(TABLE+TGAP)))
        w=(x1-x0-(n-1)*TGAP)/n
        for i in range(n):
            a=x0+i*(w+TGAP); b=a+w
            q=affinity.rotate(Polygon([(a,y),(b,y),(b,y+DEPTH),(a,y+DEPTH)]),-CONV,origin=ORG).exterior.coords
            ring=f"{c(*q[0],CLEAR)} {c(*q[1],CLEAR)} {c(*q[2],HMAX)} {c(*q[3],HMAX)} {c(*q[0],CLEAR)}"
            out.append(f'<Placemark><styleUrl>#panel</styleUrl><Polygon><altitudeMode>relativeToGround</altitudeMode><outerBoundaryIs><LinearRing><coordinates>{ring}</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>')
    return out
pw=panels(lambda x:x<560000); pe=panels(lambda x:x>=560000)
print('tables west',len(pw),'east',len(pe))
info=f'<Placemark><name>About these panels</name><description>{esc(pdesc)}</description></Placemark>'
open('ge_panels_west.kml','w').write(doc('Longmarsh – solar panels, Western Site (presumed layout)',pdesc,info+''.join(pw)))
open('ge_panels_east.kml','w').write(doc('Longmarsh – solar panels, Eastern Site (presumed layout)',pdesc,info+''.join(pe)))
# ---------- infrastructure ----------
body=[]
# published zones outline (clamped)
zdesc="PUBLISHED zone outline from Fig. 1-3. "+SRC
for k,nm in [('solar','Solar panel & battery area'),('datacentre_west','Data centre, 400 kV substation & batteries zone (max 25 m)'),('substation_bess_east','Eastern substation & batteries zone (max 8 m)'),('walpole_substation','Walpole substation works area (max 8 m)'),('ohl_50','Overhead line corridor West (towers max 50 m)'),('ohl_35','Overhead line corridor East (towers max 35 m)'),('cable_buried','Underground cable corridor'),('biodiversity','Biodiversity area'),('access_track','Access track')]:
    for r in rings(G[k].simplify(1)):
        co=" ".join(c(x,y,0) for x,y in r)
        body.append(f'<Placemark><name>{esc(nm)}</name><description>{esc(zdesc)}</description><styleUrl>#zone</styleUrl><LineString><tessellate>1</tessellate><coordinates>{co}</coordinates></LineString></Placemark>')
body='<Folder><name>Published zones (Fig. 1-3)</name>'+''.join(body)+'</Folder>'
# fences
fd=AW+"Operational areas fenced with wooden posts and wire mesh, max 2.5 m, with mammal gaps (§4.4.51). Drawn along the edge of the published solar area; the actual fence line is not yet published. "+SRC
pd=AW+"Metal palisade fence up to 3 m around the data centre and all high-voltage infrastructure (§4.4.52). Drawn on the zone edge; the actual line is not published. "+SRC
f=[]
for r in rings(G['solar'].simplify(2)):
    if Polygon(r).area<2000: continue
    f.append(wall(r,2.5,'deer','Security fence 2.5 m (presumed line)',fd))
for k in ['datacentre_west','substation_bess_east','walpole_substation']:
    for r in rings(G[k].simplify(1)): f.append(wall(r,3.0,'palisade','Palisade fence 3 m (presumed line)',pd))
body+='<Folder><name>Fencing – presumed lines, published heights</name>'+''.join(f)+'</Folder>'
# CCTV
cd=AW+"Pole-mounted CCTV up to 5 m around the perimeter of the Main Sites (§4.4.51). Pole spacing is NOT published – shown every 150 m for illustration. "+SRC
main=unary_union([G['solar'],G['datacentre_west'],G['substation_bess_east']])
cc=[]
for p in getattr(main,'geoms',[main]):
    ext=p.exterior
    if p.area<5000: continue
    n=int(ext.length//150)
    for i in range(n):
        q=ext.interpolate(i*150)
        cc.append(f'<Placemark><name>CCTV pole</name><description>{esc(cd)}</description><styleUrl>#cctv</styleUrl><Point><extrude>1</extrude><altitudeMode>relativeToGround</altitudeMode><coordinates>{c(q.x,q.y,5)}</coordinates></Point></Placemark>')
print('cctv',len(cc))
body+='<Folder><name>CCTV poles 5 m – presumed spacing</name><visibility>0</visibility>'+''.join(cc).replace('<Placemark>','<Placemark><visibility>0</visibility>')+'</Folder>'
# lighting
ld={'datacentre_west':AW+"Data centre: additional CCTV, security and external lighting designed to standards (§4.4.54); substation and BESS areas have lighting but are not permanently lit (§4.4.53). Positions, heights and hours are NOT published.",
    'substation_bess_east':AW+"Substation & BESS: lighting installed to relevant standards but not permanently lit (§4.4.53). Positions are NOT published.",
    'walpole_substation':AW+"High-voltage area: lighting to standards, not permanently lit (§4.4.53). Positions are NOT published."}
lp=[]
for k,d in ld.items():
    q=max(getattr(G[k],'geoms',[G[k]]),key=lambda p:p.area).representative_point()
    lp.append(f'<Placemark><name>Lighting – details awaited</name><description>{esc(d+" Solar areas are not permanently lit (Leaflet p14). "+SRC)}</description><styleUrl>#light</styleUrl><Point><coordinates>{c(q.x,q.y,0)}</coordinates></Point></Placemark>')
body+='<Folder><name>Lighting – awaiting information</name>'+''.join(lp)+'</Folder>'
# towers + conductors
tw=[]
for k,H,span,nm in [('ohl_50',50,350,'West 400 kV line'),('ohl_35',35,300,'East 132 kV line')]:
    ls=LineString(np.load(f'line_{k}.npy')); n=max(2,int(round(ls.length/span)))
    pts=[ls.interpolate(i/n,normalized=True) for i in range(n+1)]
    td=AW+f"{nm}: metal towers up to {H} m (§4.4.47–4.4.48), not within 100 m of a home (§4.4.50). Tower positions are NOT published – evenly spaced every ~{span} m along the corridor centre for illustration. "+SRC
    for p in pts:
        tw.append(block(p.buffer(4,cap_style=3),H,'tower',f'Tower (illustrative) – {H} m',td))
    for arm in (-6,6):
        off=ls.parallel_offset(abs(arm),'left' if arm<0 else 'right')
        co=" ".join(c(*off.interpolate(off.project(p)).coords[0],H*0.85) for p in pts)
        tw.append(f'<Placemark><name>Conductor (illustrative)</name><description>{esc(td)}</description><styleUrl>#wire</styleUrl><LineString><altitudeMode>relativeToGround</altitudeMode><coordinates>{co}</coordinates></LineString></Placemark>')
body+='<Folder><name>Overhead line towers – presumed positions, published heights</name>'+''.join(tw)+'</Folder>'
# data centre illustrative massing
dz=max(getattr(G['datacentre_west'],'geoms',[G['datacentre_west']]),key=lambda p:p.area).buffer(-25)
mrr=dz.minimum_rotated_rectangle; xs=list(mrr.exterior.coords)
e1=np.subtract(xs[1],xs[0]); e2=np.subtract(xs[2],xs[1])
long_=e1 if np.hypot(*e1)>np.hypot(*e2) else e2
ang=math.degrees(math.atan2(long_[1],long_[0]))
cx,cy=dz.centroid.x,dz.centroid.y
# work in rotated frame: buildings long axis across the zone's short side
R=affinity.rotate(dz,-ang,origin=(cx,cy))
bx0,by0,bx1,by1=R.bounds
BW,BL,G2=95,210,30   # building 95 m x 210 m, 30 m spacing (presumption)
cands=[]
x=bx0
while x+BW<=bx1:
    y=by0
    while y+BL<=by1:
        b=box(x,y,x+BW,y+BL)
        if R.contains(b): cands.append(b)
        y+=BL+G2
    x+=BW+G2
cands=cands[:10]
dd=AW+"ILLUSTRATIVE MASSING ONLY. The report allows up to 10 data centre buildings, max 25 m including plant, within a max 70 ha campus footprint (§4.4.37–4.4.38). Building sizes (95 × 210 m) and positions are invented to show scale; the substation and batteries also sit in this zone. "+SRC
db=[block(affinity.rotate(b,ang,origin=(cx,cy)),25,'dc',f'Data centre building {i+1} (illustrative)',dd) for i,b in enumerate(cands)]
print('dc buildings',len(db))
body+='<Folder><name>Data centre – illustrative massing (awaiting design)</name>'+''.join(db)+'</Folder>'
# height envelopes (off)
env=[]
for k,h in [('datacentre_west',25),('substation_bess_east',8),('walpole_substation',8)]:
    for p in getattr(G[k].simplify(1),'geoms',[G[k].simplify(1)]):
        env.append(block(p,h,'dc',f'Maximum height envelope {h} m',AW+f'Whole zone raised to its published maximum height ({h} m). Worst case used in the applicant\'s ZTV. '+SRC).replace('<Placemark>','<Placemark><visibility>0</visibility>'))
body+='<Folder><name>Height envelopes (worst case) – off by default</name><visibility>0</visibility>'+''.join(env)+'</Folder>'
open('ge_infrastructure.kml','w').write(doc('Longmarsh – infrastructure (published zones + presumptions)','Independent visualisation. Published = from the applicant\'s plans. PRESUMPTION = awaiting information. '+SRC,body))
# KMZ bundle: doc.kml with network links? simpler: one KMZ per file + combined
for n in ['ge_panels_west','ge_panels_east','ge_infrastructure']:
    with zipfile.ZipFile(n+'.kmz','w',zipfile.ZIP_DEFLATED) as z: z.write(n+'.kml','doc.kml')
import os
for n in ['ge_panels_west','ge_panels_east','ge_infrastructure']: print(n, os.path.getsize(n+'.kml')//1024,'KB kml', os.path.getsize(n+'.kmz')//1024,'KB kmz')
