"""Render the CP-CODER9 mural family. Local fonts only; deterministic Pillow/numpy art."""
from pathlib import Path
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'street'
OUT.mkdir(parents=True, exist_ok=True)
S = 2
INK = '#101322'
PALETTE = ['#ff36aa', '#c7ff32', '#20eadc', '#ff8b35', '#a777ff']
FONT = 'C:/Windows/Fonts/impact.ttf'
HAND = 'C:/Windows/Fonts/comicbd.ttf'

def font(size, hand=False):
    return ImageFont.truetype(HAND if hand else FONT, int(size*S))

def wall(w,h,seed):
    rng = np.random.default_rng(seed)
    yy,xx = np.mgrid[:h*S,:w*S]
    grain = rng.normal(0,3,(h*S,w*S))
    glow = 10*np.sin(xx/(w*S)*math.pi) + 4*np.cos(yy/85)
    a = np.zeros((h*S,w*S,3),dtype=np.uint8)
    for c,b in enumerate([20,24,35]): a[:,:,c] = np.clip(b+glow+grain,0,255)
    im = Image.fromarray(a)
    d=ImageDraw.Draw(im,'RGBA')
    for y in range(-20,h+70,58):
        d.line([(0,y*S),(w*S,y*S)],fill=(5,9,18,125),width=3*S)
        for x in range(-180,w+180,185):
            bx=x+(92 if (y//58)%2 else 0)
            d.line([(bx*S,y*S),(bx*S,(y+58)*S)],fill=(5,9,18,105),width=2*S)
    return im

def spray(im,r,cx,cy,color,radius=70,n=900):
    d=ImageDraw.Draw(im,'RGBA'); rgb=tuple(bytes.fromhex(color[1:]))
    for _ in range(n):
        x=r.gauss(cx,radius*.5); y=r.gauss(cy,radius*.36)
        q=r.uniform(.25,2.4)*S
        d.ellipse((x*S-q,y*S-q,x*S+q,y*S+q),fill=rgb+(r.randint(15,100),))

def stroke(im,points,color,width):
    d=ImageDraw.Draw(im); p=[(int(x*S),int(y*S)) for x,y in points]
    d.line(p,fill=color,width=int(width*S),joint='curve')
    for x,y in [p[0],p[-1]]:
        rr=width*S/2; d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=color)

def gestures(im,r,w,h,accent):
    # Hand-painted, uneven swoops, broad overpaint and aerosol clouds.
    for i,col in enumerate([accent,PALETTE[(r.randrange(4)+1)%5], '#20eadc']):
        cx=r.uniform(w*.1,w*.9); cy=r.uniform(h*.25,h*.8)
        spray(im,r,cx,cy,col,110,1400)
    # Broad ragged paint swipes; bristle gaps and gravity runs stay visible.
    d=ImageDraw.Draw(im,'RGBA')
    for j in range(9):
        col=PALETTE[j%5]; rgb=tuple(bytes.fromhex(col[1:]))
        x=r.uniform(-80,w*.94); y=r.uniform(5,h-5); length=r.uniform(85,240)
        points=[((x+t*length/18)*S,(y+math.sin(t*.32+j)*18+r.uniform(-7,7))*S) for t in range(19)]
        points += [((x+t*length/18)*S,(y+35+math.sin(t*.32+j)*18+r.uniform(-9,9))*S) for t in range(18,-1,-1)]
        d.polygon(points,fill=rgb+(150,))
        for k in range(7):
            dx=x+r.uniform(0,length);dy=y+30
            d.line([(dx*S,dy*S),((dx+r.uniform(-1,1))*S,(dy+r.uniform(12,60))*S)],fill=rgb+(170,),width=r.randint(1,3)*S)
        for k in range(20):
            yy=y+r.uniform(-5,40)
            d.line([(x*S,yy*S),((x+length)*S,(yy-10)*S)],fill=(15,20,30,55),width=S)
    # Loose marker calligraphy, cut and overpainted like a layered real wall.
    tags=Image.new('RGBA',im.size);td=ImageDraw.Draw(tags)
    for j in range(7):
        tx=r.uniform(-30,w-100);ty=r.uniform(-25,h-30)
        td.text((tx*S,ty*S),r.choice(['create','code','CP','//']),font=font(r.randint(25,47),True),fill=tuple(bytes.fromhex(PALETTE[(j+2)%5][1:]))+(130,),stroke_width=S)
    im.paste(tags,(0,0),tags)
    for j in range(6):
        col=PALETTE[j%5]; x=r.uniform(-100,w*.8); y=r.uniform(35,h-15)
        pts=[(x+t*17,y+math.sin(t*.24+j)*23-t*1.8+r.uniform(-1.5,1.5)) for t in range(25)]
        stroke(im,pts,INK,23); stroke(im,pts,col,r.uniform(5,12))
    d=ImageDraw.Draw(im,'RGBA')
    for _ in range(45):
        x=r.uniform(0,w);y=r.uniform(0,h); rr=r.uniform(.7,4)
        d.ellipse(((x-rr)*S,(y-rr)*S,(x+rr)*S,(y+rr)*S),fill=tuple(bytes.fromhex(r.choice(PALETTE)[1:]))+(180,))
    # Small brush crosses and loose line-art stars, deliberately imperfect.
    for x,y in [(w*.94,h*.25),(w*.065,h*.76),(w*.85,h*.82)]:
        stroke(im,[(x-8,y-10),(x+6,y+10)],'#f4f0d9',2)
        stroke(im,[(x-11,y+5),(x+12,y-5)],'#f4f0d9',2)


def letters(im,text,box,seed,fill='#c7ff32'):
    """Individually bounced, rotated outlined letters, paint wear and drips."""
    r=random.Random(seed); x,y,bw,bh=box
    fs=int(bh*.82); f=font(fs)
    advances=[f.getlength(c)/S for c in text]
    total=sum(advances)*.92
    factor=min(1,bw/total)
    fs=int(fs*factor); f=font(fs)
    advances=[f.getlength(c)/S for c in text]
    x+=(bw-sum(advances)*.92)/2
    for j,(ch,adv) in enumerate(zip(text,advances)):
        if ch==' ': x+=adv*.7; continue
        pad=25*S; bb=f.getbbox(ch); cw=int(adv*S+pad*2); chh=int(fs*S+pad*2)
        tile=Image.new('RGBA',(cw,chh)); d=ImageDraw.Draw(tile)
        tx=pad; ty=pad-bb[1]
        # Deep extrusion then ivory keyline and ink outline.
        for dep in range(13,0,-2):
            d.text((tx+dep*S,ty+dep*S),ch,font=f,fill=INK,stroke_width=7*S,stroke_fill=INK)
        d.text((tx,ty),ch,font=f,fill=fill,stroke_width=8*S,stroke_fill='#f6efda')
        d.text((tx,ty),ch,font=f,fill=fill,stroke_width=4*S,stroke_fill=INK)
        mask=Image.new('L',tile.size); md=ImageDraw.Draw(mask)
        md.text((tx,ty),ch,font=f,fill=255)
        paint=Image.new('RGBA',tile.size); pd=ImageDraw.Draw(paint)
        for k in range(20):
            yy=r.randrange(max(1,int(fs*S)))+pad
            pd.line([(0,yy),(cw,yy-r.randint(0,8)*S)],fill=(255,255,245,r.randint(12,65)),width=r.randint(1,3)*S)
        for k in range(70):
            xx=r.randrange(cw); yy=r.randrange(chh)
            pd.ellipse((xx,yy,xx+S,yy+S),fill=(10,20,30,100))
        alpha=Image.fromarray((np.asarray(paint.getchannel('A'),dtype=np.uint16)*np.asarray(mask,dtype=np.uint16)//255).astype('uint8'))
        paint.putalpha(alpha);tile.alpha_composite(paint)
        tile=tile.rotate(r.uniform(-8,8),Image.Resampling.BICUBIC,expand=True)
        im.paste(tile,(int((x-27)*S),int((y+r.uniform(-5,5)-22)*S)),tile)
        if j%3==0:
            dx=x+adv*.5; dy=y+fs*.8
            stroke(im,[(dx,dy),(dx+r.uniform(-2,2),dy+r.uniform(12,25))],fill,3)
        x+=adv*.92

def sticker(im,text,x,y,angle=-4,color='#f7eed7',size=16):
    f=font(size,True); bb=f.getbbox(text); w=bb[2]+24*S; h=bb[3]-bb[1]+17*S
    tile=Image.new('RGBA',(w+8*S,h+8*S));d=ImageDraw.Draw(tile)
    d.polygon([(4*S,8*S),(w,2*S),(w-3*S,h),(0,h+3*S)],fill=INK)
    d.polygon([(0,3*S),(w-4*S,0),(w-6*S,h-4*S),(2*S,h)],fill=color)
    d.text((10*S,6*S-bb[1]),text,font=f,fill=INK)
    tile=tile.rotate(angle,Image.Resampling.BICUBIC,expand=True)
    im.paste(tile,(int(x*S),int(y*S)),tile)

def save(im,path):
    im.resize((im.width//S,im.height//S),Image.Resampling.LANCZOS).convert('RGB').save(path,optimize=True)

def header():
    w,h=1200,420;r=random.Random(901); im=wall(w,h,901)
    gestures(im,r,w,h,PALETTE[0])
    # Layered wide turquoise/pink brush grounds, not a rectangular title plaque.
    for off,col,width in [(14,INK,123),(6,'#ff36aa',105),(0,'#20eadc',70)]:
        stroke(im,[(100,235+off),(290,170+off),(560,210+off),(890,145+off),(1090,210+off)],col,width)
    letters(im,'CP-CODER9',(60,122,1080,172),902,'#c7ff32')
    sticker(im,'CODE / CREATE / REPEAT',374,332,-3,'#f7eed7',23)
    sticker(im,'BUILT DIFFERENT',62,42,7,'#ff8b35',18)
    sticker(im,'NO BLANK WALLS',901,48,-7,'#ff36aa',17)
    save(im,ROOT/'assets'/'graffiti-header.png')

def section(key,title,seed):
    w,h=1200,300;r=random.Random(seed);im=wall(w,h,seed)
    gestures(im,r,w,h,PALETTE[seed%5])
    stroke(im,[(170,205),(440,172),(700,198),(1030,123)],INK,100)
    letters(im,title,(120,72,960,153),seed,'#20eadc' if seed%2 else '#ff36aa')
    save(im,OUT/(key+'.png'))

PROJECTS=[('arc','01','ARC-1','architecture + AI'),('radar','02','ARCHITEX RADAR','tech radar'),('reminisce','03','REMINISCE','memory + AI'),('termux','04','TERMUX CONNECTOR','Android + Termux'),('ble','05','GH0ST-BLE','BLE + ESP32'),('a777','06','A777','architecture + PHP')]

def card(key,num,title,desc,idx):
    w,h=700,310;seed=110+idx;r=random.Random(seed);im=wall(w,h,seed);col=PALETTE[idx%5]
    gestures(im,r,w,h,col)
    stroke(im,[(36,150),(180,112),(340,156),(628,105)],INK,115)
    # Layered title lines keep long actual names large and readable.
    if title in ['ARCHITEX RADAR','TERMUX CONNECTOR']:
        a,b=title.split(' ')
        letters(im,a,(100,68,550,92),seed,col)
        letters(im,b,(98,147,550,85),seed+20,col)
    else:
        letters(im,title,(69,106,576,127),seed,col)
    sticker(im,num,24,23,8,'#f7eed7',25)
    sticker(im,desc,170,250,-3,'#f7eed7',18)
    # Paint-marker arrow, an affordance for the parent README image link.
    stroke(im,[(613,259),(663,252),(649,239)],'#f7eed7',4)
    stroke(im,[(663,252),(651,269)],'#f7eed7',4)
    save(im,OUT/f'project-{key}.png')

if __name__=='__main__':
    header()
    for args in [('work','SELECTED WORK',41),('signal','SIGNAL',42),('extras','SIDE QUESTS',43),('footer','KEEP CREATING',44)]: section(*args)
    for idx,p in enumerate(PROJECTS):card(*p,idx)
    print('Rendered mural header, 4 section images and 6 project cards.')
