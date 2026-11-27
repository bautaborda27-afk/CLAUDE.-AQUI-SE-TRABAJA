import cv2, numpy as np, json, sys
from PIL import Image
SP=sys.argv[1]; OUT=sys.argv[2]
a=np.asarray(Image.open(SP+'/src1080.png').convert('RGB'))
H,W=a.shape[:2]
lab=cv2.cvtColor(a,cv2.COLOR_RGB2LAB).astype(float)
yy,xx=np.mgrid[0:H,0:W]

E=[
 ("logo",      430, 88, 625,166, "any"),
 ("star1",     175,220, 235,290, "any"),
 ("star2",     115,785, 175,855, "any"),
 ("starL",      95,995, 155,1065,"any"),
 ("starR",     925,995, 995,1065,"any"),
 ("con",       270,315, 500,425, "any"),
 ("cuarto",    112,418, 890,550, "any"),
 ("despedimos",112,545, 945,692, "any"),
 ("elano",     290,692, 810,835, "any"),
 ("swash",     410,836, 780,895, "any"),
 ("date",      235,975, 865,1075,"any"),
 ("oval",      160,920, 930,1140,"any"),
 ("tagline",   140,1160,950,1255,"any"),
 ("divider",   200,1272,870,1345,"any"),
 ("disco",     650,  0,1080,560, "plum"),
 ("ribbon_tl",   0,  0, 430,460, "plum"),
 ("ribbon_r",  850,740,1080,910, "plum"),
 ("ribbon_b",    0,1370,1080,1920,"plum"),
]
names=[e[0] for e in E]

def ink_d(paper):
    labp=cv2.cvtColor(paper,cv2.COLOR_RGB2LAB).astype(float)
    dL=lab[...,0]-labp[...,0]; da=lab[...,1]-labp[...,1]; db=lab[...,2]-labp[...,2]
    return np.sqrt((np.minimum(dL,0)*0.6)**2+da**2+db**2), db

def labels(d,db,thr,thr_plum):
    lbl=np.full((H,W),-1,np.int16)
    for i,(n,x0,y0,x1,y1,kind) in enumerate(E):
        reg=np.zeros((H,W),bool); reg[y0:y1,x0:x1]=True
        if kind=="plum": m=(d>thr_plum)&reg&(lbl<0)&(db<6)
        else: m=(d>thr)&reg&(lbl<0)
        lbl[m]=i
    return lbl

bg=cv2.medianBlur(cv2.medianBlur(a,101),41)
d,db=ink_d(bg)
lbl=labels(d,db,18,12)
m=cv2.dilate((lbl>=0).astype(np.uint8)*255,np.ones((9,9),np.uint8))
paper1=cv2.inpaint(a,m,6,cv2.INPAINT_TELEA)
d,db=ink_d(paper1)
lbl=labels(d,db,10,7)
core=(lbl>=0).astype(np.uint8)*255
core=cv2.morphologyEx(core,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
lbl[core==0]=-1

# region per element (what gets inpainted / where ink is computed)
disk=((xx-912)/136.0)**2+((yy-294)/139.0)**2<=1
regions={}
for i,n in enumerate(names):
    c=(lbl==i).astype(np.uint8)
    if n.startswith('ribbon'):
        c=cv2.morphologyEx(c,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))
    if n=='disco':
        c=c|disk.astype(np.uint8)
    regions[n]=cv2.dilate(c,np.ones((7,7),np.uint8))
allreg=np.zeros((H,W),np.uint8)
for r in regions.values(): allreg|=r
inp=cv2.dilate(allreg*255,np.ones((5,5),np.uint8))
paper=cv2.inpaint(a,inp,7,cv2.INPAINT_TELEA).astype(float)

# borrow real paper grain (high-pass) from shifted clean locations
af=a.astype(float)
hp=af-cv2.GaussianBlur(af,(0,0),2.2)
need=inp>0; fill=np.zeros_like(hp); done=np.zeros((H,W),bool)
for (dy,dx) in [(0,170),(0,-170),(170,0),(-170,0),(120,120),(-120,-120),(120,-120),(-120,120),(0,340),(0,-340),(340,0),(-340,0),(250,250),(-250,-250)]:
    src_ok=np.roll(np.roll(~need,dy,0),dx,1)
    take=need&~done&src_ok
    fill[take]=np.roll(np.roll(hp,dy,0),dx,1)[take]
    done|=take
fm=cv2.GaussianBlur(need.astype(float),(0,0),2)[...,None]
paper=np.clip(paper+fill*fm,0,255)
Image.fromarray(paper.astype(np.uint8)).save(OUT+'/paper.jpg',quality=93)

# per-element ink layers (exact over paper), cropped
P=paper/255.0; O=af/255.0
meta={}
for i,n in enumerate(names):
    r=regions[n].astype(bool)
    if not r.any(): print('EMPTY',n); continue
    ys,xs=np.where(r); x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
    Pc=P[y0:y1,x0:x1]; Oc=O[y0:y1,x0:x1]; rc=cv2.GaussianBlur(r[y0:y1,x0:x1].astype(float),(0,0),1.2)
    al=np.clip(((Pc-Oc)/np.maximum(Pc,1e-3)).max(2),0,1)
    al=al*np.clip((al-0.03)/0.07,0,1)  # drop faint grain differences
    C=(Oc-(1-al[...,None])*Pc)/np.maximum(al[...,None],1e-3)
    C=np.clip(C,0,1)
    A=al*np.clip(rc*1.4,0,1)
    rgba=np.dstack([C,A[...,None]])
    Image.fromarray((rgba*255+.5).astype(np.uint8),'RGBA').save(f'{OUT}/el/{n}.png')
    meta[n]=dict(x=int(x0),y=int(y0),w=int(x1-x0),h=int(y1-y0))
    # sketch outline for lettering
    if n in ('logo','con','cuarto','despedimos','elano','date','tagline'):
        cb=(lbl[y0:y1,x0:x1]==i).astype(np.uint8)
        cb=cv2.morphologyEx(cb,cv2.MORPH_CLOSE,np.ones((2,2),np.uint8))
        edge=cb-cv2.erode(cb,np.ones((3,3),np.uint8),iterations=1)
        edge=cv2.GaussianBlur(edge.astype(float),(0,0),0.6)
        inkcol=np.median(Oc[cb>0],axis=0)*0.85
        ol=np.zeros(cb.shape+(4,)); ol[...,:3]=inkcol; ol[...,3]=np.clip(edge*1.6,0,1)*0.9
        Image.fromarray((ol*255+.5).astype(np.uint8),'RGBA').save(f'{OUT}/el/{n}_sketch.png')
# split disco: chain / ball / rays
dm=regions['disco'].astype(bool)
parts={'disco_chain': dm&(yy<168)&(xx>915)&(xx<975), 'disco_ball': dm&cv2.dilate(disk.astype(np.uint8),np.ones((9,9),np.uint8)).astype(bool)}
parts['disco_ball']&=~parts['disco_chain']
parts['disco_rays']=dm&~parts['disco_chain']&~parts['disco_ball']
d0=meta['disco']; full=np.asarray(Image.open(f'{OUT}/el/disco.png')).astype(float)
for k,pm in parts.items():
    sub=pm[d0['y']:d0['y']+d0['h'], d0['x']:d0['x']+d0['w']]
    ys,xs=np.where(sub); x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
    smask=cv2.GaussianBlur(sub.astype(float),(0,0),1.0)[y0:y1,x0:x1]
    crop=full[y0:y1,x0:x1].copy(); crop[...,3]*=np.clip(smask*1.3,0,1)
    Image.fromarray(crop.astype(np.uint8),'RGBA').save(f'{OUT}/el/{k}.png')
    meta[k]=dict(x=int(d0['x']+x0),y=int(d0['y']+y0),w=int(x1-x0),h=int(y1-y0))
json.dump(meta,open(OUT+'/el/meta.json','w'),indent=1)
# verification composite
comp=Image.open(OUT+'/paper.jpg').convert('RGBA')
for n,m_ in meta.items():
    if n=='disco': continue
    comp.alpha_composite(Image.open(f'{OUT}/el/{n}.png'),(m_['x'],m_['y']))
comp.convert('RGB').save(SP+'/recomposed.png')
diff=np.abs(np.asarray(comp.convert('RGB')).astype(float)-af).mean()
print('mean abs diff vs original', round(diff,2)); print(json.dumps(meta))
