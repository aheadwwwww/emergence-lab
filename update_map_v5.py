from PIL import Image, ImageDraw, ImageFont
import os, math

img = Image.new("RGB", (1150, 680), "#0f111a")
d = ImageDraw.Draw(img)
fp = next((f for f in ["C:\\Windows\\Fonts\\segoeui.ttf","C:\\Windows\\Fonts\\arial.ttf"] if os.path.exists(f)), None)
def f(s):
    try: return ImageFont.truetype(fp, s)
    except: return ImageFont.load_default()
F20=f(20);F16=f(16);F13=f(13);F11=f(11)

for x in range(0,1150,40):
    for y in range(0,680,40):
        d.ellipse([x-1,y-1,x+1,y+1],fill="#1c1e2b")

def dl(x1,y1,x2,y2,c,w=1,d5=5,g6=6):
    dx,dy=x2-x1,y2-y1;L=math.hypot(dx,dy)
    if L==0:return
    ux,uy=dx/L,dy/L;t=0;dr=True
    while t<L:
        s=d5 if dr else g6;e=min(t+s,L)
        if dr:d.line([int(x1+ux*t),int(y1+uy*t),int(x1+ux*e),int(y1+uy*e)],fill=c,width=int(w))
        t=e;dr=not dr

def ar(x1,y1,x2,y2,c):
    a=math.atan2(y2-y1,x2-x1)
    ax,ay=x2-math.cos(a)*10,y2-math.sin(a)*10
    d.polygon([(x2,y2),(ax-math.sin(a)*5,ay+math.cos(a)*5),(ax+math.sin(a)*5,ay-math.cos(a)*5)],fill=c)

def gh(x,y,r=26):
    d.ellipse([x-r,y-r,x+r,y+r],fill="#1c1e2b",outline="#2a2d3a",width=1)
    d.text((x-7,y-10),"?",fill="#4a4d63",font=F20)

def gl(x,y,r,fc,sc):
    for rr in range(r,r+5,2):
        ci=max(0,108-(rr-r)*20)
        d.ellipse([x-rr,y-rr,x+rr,y+rr],outline=f"#{ci:02x}{sc[1:]}",width=1)
    d.ellipse([x-r,y-r,x+r,y+r],fill=fc,outline=sc,width=2)

# Node positions
N = {
    "E":(380,180,55,"#2a2048","#6c63ff"),
    "A":(590,310,42,"#2a2a20","#ffc864"),
    "EC":(200,140,42,"#20202a","#00d4aa"),
    "SC":(260,380,42,"#1a202a","#f472b6"),
    "CA":(570,500,38,"#20251a","#a78bfa"),
    "T":(770,160,35,"#1a2520","#34d399"),
    "B":(920,380,35,"#1a1a28","#6c63ff"),
}

# Connections
cs = [("E","A","#6c63ff"),("E","EC","#6c63ff"),("A","EC","#6c63ff"),
      ("EC","SC","#6c63ff"),("EC","CA","#6c63ff"),("A","T","#ffc864"),
      ("SC","CA","#6c63ff"),("T","CA","#6c63ff"),("A","B","#6c63ff"),
      ("E","B","#6c63ff")]
for fr,to,c in cs:
    x1,y1=N[fr][0],N[fr][1];x2,y2=N[to][0],N[to][1]
    dl(x1,y1,x2,y2,c,1.5,7,8);ar(x1,y1,x2,y2,c)

# Ghosts
for gx,gy,gr in [(100,450,26),(420,530,26),(900,530,26),(1050,200,26),(400,100,26),(700,80,26)]:
    dl(380,180,gx,gy,"#3a3d4f",1,5,6);ar(380,180,gx,gy,"#4a4d63");gh(gx,gy,gr)

for nm,(x,y,r,fc,sc) in N.items():gl(x,y,r,fc,sc)

# Labels
d.text((335,155),"Emergence","#c4b5fd",F20);d.text((368,190),"涌现","#8892a8",F13);d.text((328,243),"#001","#6c63ff",F11)
d.text((556,295),"Langton's","#ffd700",F16);d.text((566,315),"Ant","#ffd700",F16);d.text((560,345),"朗顿蚂蚁","#a09880",F13);d.text((555,365),"#002","#ffc864",F11)
d.text((158,118),"Edge of","#5eead4",F16);d.text((158,138),"Chaos","#5eead4",F16);d.text((162,172),"混沌边缘","#a09880",F13);d.text((165,195),"#003","#00d4aa",F11)
d.text((222,358),"Self-Org.","#f9a8d4",F13);d.text((222,378),"Criticality","#f9a8d4",F13);d.text((218,415),"自组织临界性","#a09880",F13);d.text((225,438),"#004","#f472b6",F11)
d.text((530,480),"CA Classes","#ddd6fe",F13);d.text((530,510),"元胞自动机分类","#a09880",F11);d.text((540,533),"#005","#a78bfa",F11)
d.text((740,138),"Turmites","#6ee7b7",F13);d.text((740,163),"图米特","#a09880",F11);d.text((745,183),"#006","#34d399",F11)
d.text((890,358),"Boids","#a5b4fc",F13);d.text((885,383),"群聚模拟","#a09880",F11);d.text((895,405),"#007","#6c63ff",F11)

d.text((370,650),"——— 已连接的节点     - - - - 等待探索的连接","#4a4d63",F13)

p=r"C:\Users\许耀仁\.openclaw\workspace\curiosity-map.png"
img.save(p);print(f"Map v5: {os.path.getsize(p)} bytes — 7 nodes")
