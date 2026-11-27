import cv2, numpy as np, json, sys
from PIL import Image
SP=sys.argv[1]; OUT=sys.argv[2]
a=np.asarray(Image.open(SP+'/src1080.png').convert('RGB'))
H,W=a.shape[:2]
lab=cv2.cvtColor(a,cv2.COLOR_RGB2LAB).astype(float)
yy,xx=np.mgrid[0:H,0:W]
E=[("logo",440,100,650,190),("star",440,345,640,550),("con",182,528,328,602),
   ("cuarto",142,598,942,690),("desp",102,700,992,832),("elano",268,834,872,962),
   ("div1",265,1018,815,1068),("date",168,1082,922,1148),("div2",265,1150,885,1188),
   ("tag",98,1222,988,1338)]
names=[e[0] for e in E]
def dl(paper):
    labp=cv2.cvtColor(paper,cv2.COLOR_RGB2LAB).astype(float)
    return lab[...,0]-labp[...,0]
def labels(dL,thr):
    lbl=np.full((H,W),-1,np.int16)
    for i,(n,x0,y0,x1,y1) in enumerate(E):
        reg=np.zeros((H,W),bool); reg[y0:y1,x0:x1]=True
        lbl[(dL>thr)&reg&(lbl<0)]=i
    return lbl
from scipy.ndimage import percentile_filter
sm=cv2.resize(a,(W//4,H//4),interpolation=cv2.INTER_AREA)
bgs=np.dstack([percentile_filter(sm[...,c],25,size=21) for c in range(3)]).astype(np.uint8)
bg=cv2.GaussianBlur(cv2.resize(bgs,(W,H),interpolation=cv2.INTER_CUBIC),(0,0),6)
lbl=labels(dl(bg),28)
for i,n in enumerate(names):
    if n in ('desp','elano','cuarto','con','logo'):
        c=(lbl==i).astype(np.uint8)
        c=cv2.morphologyEx(c,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)))
        ff=c.copy(); msk=np.zeros((H+2,W+2),np.uint8); cv2.floodFill(ff,msk,(0,0),1); c=c|(1-ff)
        x0,y0,x1,y1=E[i][1:]; box=np.zeros((H,W),bool); box[y0:y1,x0:x1]=True
        lbl[(c>0)&box&(lbl<0)]=i
m=cv2.dilate((lbl>=0).astype(np.uint8)*255,np.ones((9,9),np.uint8))
paper1=cv2.inpaint(a,m,6,cv2.INPAINT_TELEA)
lbl2=labels(dl(paper1),24)
lbl=np.where(lbl>=0,lbl,lbl2)
core=(lbl>=0).astype(np.uint8)*255
core=cv2.morphologyEx(core,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
lbl[core==0]=-1
# drop tiny specks (paper texture) per element
for i,n in enumerate(names):
    c=(lbl==i).astype(np.uint8)
    k,cc,st,_=cv2.connectedComponentsWithStats(c,8)
    minarea=40 if n not in ('div1','div2','date','tag','con') else 12
    for j in range(1,k):
        if st[j,cv2.CC_STAT_AREA]<minarea: lbl[cc==j]=-1
regions={}
for i,n in enumerate(names):
    c=(lbl==i).astype(np.uint8)
    if n=='star':
        c=cv2.morphologyEx(c,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(17,17)))
        ff=c.copy(); h_,w_=ff.shape; msk=np.zeros((h_+2,w_+2),np.uint8); cv2.floodFill(ff,msk,(0,0),1); c=c|(1-ff)
    elif n in ('desp','elano','cuarto','logo','con'):
        c=cv2.morphologyEx(c,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)))
        ff=c.copy(); msk=np.zeros((H+2,W+2),np.uint8); cv2.floodFill(ff,msk,(0,0),1); c=c|(1-ff)
    k={'desp':19,'elano':19,'cuarto':15,'logo':13,'con':13,'star':11}.get(n,11)
    regions[n]=cv2.dilate(c,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k)))
allreg=np.zeros((H,W),np.uint8)
for r in regions.values(): allreg|=r
inp=cv2.dilate(allreg*255,np.ones((5,5),np.uint8))
paper=cv2.inpaint(a,inp,9,cv2.INPAINT_TELEA).astype(float)
af=a.astype(float)
hp=af-cv2.GaussianBlur(af,(0,0),2.2)
need=inp>0; fill=np.zeros_like(hp); done=np.zeros((H,W),bool)
interior=np.zeros((H,W),bool); interior[80:H-80,80:W-80]=True
srcok=(~cv2.dilate(need.astype(np.uint8),np.ones((9,9),np.uint8)).astype(bool))&interior
for (dy,dx) in [(0,170),(0,-170),(170,0),(-170,0),(120,120),(-120,-120),(120,-120),(-120,120),(0,340),(0,-340),(340,0),(-340,0),(250,250),(-250,-250)]:
    ok=np.roll(np.roll(srcok,dy,0),dx,1); take=need&~done&ok
    fill[take]=np.roll(np.roll(hp,dy,0),dx,1)[take]; done|=take
# also borrow some mid-frequency mottling so filled areas are not flat
mp=cv2.GaussianBlur(af,(0,0),2.2)-cv2.GaussianBlur(af,(0,0),9)
fill2=np.zeros_like(mp); done=np.zeros((H,W),bool)
for (dy,dx) in [(0,190),(0,-190),(190,0),(-190,0),(140,140),(-140,-140),(0,380),(0,-380)]:
    ok=np.roll(np.roll(srcok,dy,0),dx,1); take=need&~done&ok
    fill2[take]=np.roll(np.roll(mp,dy,0),dx,1)[take]; done|=take
fm=cv2.GaussianBlur(need.astype(float),(0,0),2)[...,None]
paper=np.clip(paper+(fill+0.8*fill2)*fm,0,255)
Image.fromarray(paper.astype(np.uint8)).save(OUT+'/paper.jpg',quality=93)
P=paper/255.0; O=af/255.0; meta={}
for i,n in enumerate(names):
    r=regions[n].astype(bool)
    ys,xs=np.where(r); x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
    Pc=P[y0:y1,x0:x1]; Oc=O[y0:y1,x0:x1]; rc=cv2.GaussianBlur(r[y0:y1,x0:x1].astype(float),(0,0),1.2)
    up=(Oc-Pc)/np.maximum(1-Pc,1e-3); dn=(Pc-Oc)/np.maximum(Pc,1e-3)
    al=np.clip(np.maximum(up,dn).max(2),0,1)
    al=al*np.clip((al-0.04)/0.08,0,1)
    C=np.clip((Oc-(1-al[...,None])*Pc)/np.maximum(al[...,None],1e-3),0,1)
    A=al*np.clip(rc*1.4,0,1)
    Image.fromarray((np.dstack([C,A[...,None]])*255+.5).astype(np.uint8),'RGBA').save(f'{OUT}/el/{n}.png')
    meta[n]=dict(x=int(x0),y=int(y0),w=int(x1-x0),h=int(y1-y0))
    if n in ('logo','con','cuarto','desp','elano','date','tag'):
        cb=(lbl[y0:y1,x0:x1]==i).astype(np.uint8)
        cb=cv2.morphologyEx(cb,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
        edge=cb-cv2.erode(cb,np.ones((3,3),np.uint8))
        edge=cv2.GaussianBlur(edge.astype(float),(0,0),0.6)
        col=np.array([0.98,0.80,0.45])  # warm gold pencil
        ol=np.zeros(cb.shape+(4,)); ol[...,:3]=col; ol[...,3]=np.clip(edge*1.7,0,1)*0.95
        Image.fromarray((ol*255+.5).astype(np.uint8),'RGBA').save(f'{OUT}/el/{n}_sketch.png')
json.dump(meta,open(OUT+'/el/meta.json','w'),indent=1)
comp=Image.open(OUT+'/paper.jpg').convert('RGBA')
for n,m_ in meta.items(): comp.alpha_composite(Image.open(f'{OUT}/el/{n}.png'),(m_['x'],m_['y']))
comp.convert('RGB').save(SP+'/recomposed.png')
print('diff',round(np.abs(np.asarray(comp.convert('RGB')).astype(float)-af).mean(),2)); print(json.dumps(meta))
