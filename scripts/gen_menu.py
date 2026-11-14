#!/usr/bin/env python3
"""Draw a completely new original FancyMenu atlas + interactive UI layout."""
from __future__ import annotations

import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/"config/fancymenu/assets"
LAYOUT=ROOT/"config/fancymenu/customization/chronicles_title_layout.txt"

def font(px,bold=False):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"):
        try:return ImageFont.truetype(path,px)
        except OSError:pass
    return ImageFont.load_default()

def gear(draw,cx,cy,r,n,col,width=5):
    draw.ellipse((cx-r,cy-r,cx+r,cy+r),outline=col,width=width)
    ir=int(r*.68)
    draw.ellipse((cx-ir,cy-ir,cx+ir,cy+ir),outline=(*col[:3],int(col[3]*.62)),width=max(2,width-2))
    draw.ellipse((cx-int(r*.23),cy-int(r*.23),cx+int(r*.23),cy+int(r*.23)),
                 outline=col,width=max(2,width-1))
    for i in range(n):
        a=i*2*math.pi/n
        x1=cx+(r-10)*math.cos(a);y1=cy+(r-10)*math.sin(a)
        x2=cx+(r+15)*math.cos(a);y2=cy+(r+15)*math.sin(a)
        draw.line((x1,y1,x2,y2),fill=col,width=width+4)
    for i in range(6):
        a=i*math.pi/3
        draw.line((cx+int(r*.24)*math.cos(a),cy+int(r*.24)*math.sin(a),
                   cx+int(r*.65)*math.cos(a),cy+int(r*.65)*math.sin(a)),
                  fill=(*col[:3],int(col[3]*.8)),width=max(2,width-1))

def background():
    W,H=1920,1080
    im=Image.new("RGB",(W,H))
    d=ImageDraw.Draw(im)
    # Slate-blue dusk to copper-lit horizon, with no old Starlight imagery.
    for y in range(H):
        t=y/H
        col=(int(6+11*t),int(20+23*t),int(34+21*t))
        d.line((0,y,W,y),fill=col,width=1)
    d=ImageDraw.Draw(im,"RGBA")
    rng=random.Random(67071)
    # Contour-map lines establish a recognisable atlas aesthetic.
    for k in range(22):
        yy=160+k*41
        last=None
        for x in range(-80,W+100,12):
            y=yy+23*math.sin(x*.007+k*.4)+9*math.sin(x*.017+k)
            if last is not None:
                d.line((last[0],last[1],x,y),fill=(170,208,202,18 if k%3 else 28),width=2)
            last=(x,y)
    # Terrain silhouettes / workshop skyline.
    for h,alpha,polycol in [(650,190,(9,33,43)),(755,225,(9,29,41)),(880,255,(8,23,35))]:
        pts=[(-50,H),(W+50,H)]
        pts+=[(x,h-42*math.sin(x*.008+.9*h)-21*math.cos(x*.015+h)) for x in range(W+50,-60,-25)]
        d.polygon(pts,fill=(*polycol,alpha))
    # Mechanical core on the right, with rotating rings and copper compass ticks.
    gear(d,1450,540,315,26,(185,132,74,118),7)
    gear(d,1450,540,225,18,(88,161,166,170),6)
    gear(d,1450,540,95,12,(232,194,113,179),5)
    gear(d,1707,800,152,16,(170,112,72,115),5)
    gear(d,1118,790,110,12,(115,177,179,120),4)
    d.arc((945,28,1920,1025),50,319,fill=(228,177,99,82),width=5)
    d.arc((1020,110,1855,900),82,351,fill=(154,211,202,52),width=4)
    for n in range(55):
        a=n*math.pi*2/55
        rad=365
        x1=1450+rad*math.cos(a);y1=540+rad*math.sin(a)
        x2=1450+(rad+ (21 if n%5==0 else 9))*math.cos(a)
        y2=540+(rad+ (21 if n%5==0 else 9))*math.sin(a)
        d.line((x1,y1,x2,y2),fill=(226,183,116,145),width=3)
    # Blueprint workbench panel on the left with gold separators.
    d.rounded_rectangle((82,136,705,965),radius=28,fill=(7,20,32,172),
                        outline=(174,139,89,110),width=3)
    d.rounded_rectangle((103,159,685,944),radius=19,outline=(93,151,153,70),width=2)
    d.line((138,344,649,344),fill=(194,153,94,130),width=3)
    d.text((146,203),"CHRONICLES",font=font(74,True),fill=(237,221,180,250))
    d.text((149,292),"CLOCKWORK  /  ATLAS",font=font(24,True),fill=(145,202,203,230))
    d.text((148,386),"ONE WORLD. A THOUSAND ROUTES.",font=font(18),fill=(201,212,208,186))
    d.line((137,878,650,878),fill=(203,170,109,100),width=2)
    d.text((150,896),"CREATE   /   EXPLORATION   /   QUESTS",font=font(17),fill=(179,202,205,196))
    # Tiny decorative star chart particles, low-contrast.
    for _ in range(230):
        x,y=rng.randint(740,1900),rng.randint(20,1040)
        rr=rng.choice((1,1,2,2,3))
        d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(218,194,143,rng.randint(35,120)))
    im.save(ASSETS/"chronicles_background.png",optimize=True)
    # Button sprites, deliberately different from vanilla buttons.
    for hover in (False,True):
        w,h=570,90
        btn=Image.new("RGBA",(w,h),(0,0,0,0))
        b=ImageDraw.Draw(btn,"RGBA")
        if hover:
            b.rounded_rectangle((6,6,w-7,h-7),radius=12,fill=(54,93,100,234),
                                outline=(242,197,111,250),width=4)
        else:
            b.rounded_rectangle((6,6,w-7,h-7),radius=12,fill=(23,49,66,215),
                                outline=(118,168,168,200),width=3)
        b.polygon([(18,45),(38,29),(38,61)],fill=(237,193,117,255) if hover else (124,180,184,210))
        b.line((55,70,528,70),fill=(228,188,104,180) if hover else (128,163,159,78),width=3)
        if hover:
            b.rounded_rectangle((3,3,w-4,h-4),radius=12,outline=(255,226,166,83),width=2)
        btn.save(ASSETS/("chronicles_button_hover.png" if hover else "chronicles_button.png"),optimize=True)

def create_layout():
    L=[]
    L.extend([
        "type = fancymenu_layout",
        "",
        "layout-meta {",
        "  identifier = net.minecraft.client.gui.screens.TitleScreen",
        "  is_enabled = true",
        "  randommode = false",
        "  randomgroup = 1",
        "  randomonlyfirsttime = false",
        "  layout_index = 0",
        "  render_custom_elements_behind_vanilla = false",
        "  last_edited_time = 1794590000000",
        "}",
        "",
        "menu_background {",
        "  background_type = image",
        "  image_path = [source:local]/config/fancymenu/assets/chronicles_background.png",
        "  slide = false",
        "  repeat_texture = false",
        "  parallax = false",
        "  keepaspectratio = true",
        "  instance_identifier = chronicles-background-v4",
        "}",
        "",
        "customization {",
        "  action = backgroundoptions",
        "  keepaspectratio = true",
        "}",
    ])
    # Hide the default GUI buttons; the replacement buttons use mimicbutton actions.
    buttons=[
        ("singleplayer","ОДИНОЧНАЯ ИГРА","mc_titlescreen_singleplayer_button",-60),
        ("multiplayer","СЕТЕВАЯ ИГРА","mc_titlescreen_multiplayer_button",-11),
        ("options","НАСТРОЙКИ","mc_titlescreen_options_button",38),
        ("mods","МОДЫ","forge_titlescreen_mods_button",87),
        ("quit","ВЫХОД","mc_titlescreen_quit_button",136),
    ]
    for kind,label,target,y in buttons:
        L.extend([
            "",
            "vanilla_button {",
            "  instance_identifier = "+target,
            "  is_hidden = true",
            "}",
        ])
    for kind,label,target,y in buttons:
        act="chronicles-action-"+kind
        blk="chronicles-exec-"+kind
        L.extend([
            "",
            "element {",
            "  button_element_executable_block_identifier = "+blk,
            "  [executable_action_instance:"+act+"][action_type:mimicbutton] = title_screen:"+target,
            "  [executable_block:"+blk+"][type:generic] = [executables:"+act+";]",
            "  actionid = "+blk,
            "  backgroundnormal = [source:local]/config/fancymenu/assets/chronicles_button.png",
            "  backgroundhovered = [source:local]/config/fancymenu/assets/chronicles_button_hover.png",
            "  restartbackgroundanimations = false",
            "  nine_slice_custom_background = false",
            "  label = "+label,
            "  description = "+label,
            "  navigatable = true",
            "  element_type = custom_button",
            "  instance_identifier = chronicles-btn-"+kind,
            "  anchor_point = mid-centered",
            "  x = -205",
            "  y = "+str(y),
            "  width = 248",
            "  height = 39",
            "}",
        ])
    L.extend([
        "",
        "element {",
        "  element_type = text_v2",
        "  source = NEOFORGE 1.21.1  /  CREATE  /  CHRONICLES 0.4",
        "  source_mode = direct",
        "  scale = 0.9",
        "  shadow = true",
        "  case_mode = normal",
        "  line_spacing = 1",
        "  anchor_point = bottom-centered",
        "  x = 0",
        "  y = -23",
        "  width = 510",
        "  height = 18",
        "  instance_identifier = chronicles-build-label",
        "}",
        "",
        "element {",
        "  button_element_executable_block_identifier = chronicles-exec-repo",
        "  [executable_action_instance:chronicles-action-repo][action_type:openlink] = https://github.com/yungspiderq/my-neoforge-pack",
        "  [executable_block:chronicles-exec-repo][type:generic] = [executables:chronicles-action-repo;]",
        "  actionid = chronicles-exec-repo",
        "  backgroundnormal = [source:local]/config/fancymenu/assets/chronicles_button.png",
        "  backgroundhovered = [source:local]/config/fancymenu/assets/chronicles_button_hover.png",
        "  label = САЙТ СБОРКИ",
        "  description = Репозиторий и обновления",
        "  element_type = custom_button",
        "  instance_identifier = chronicles-btn-repo",
        "  navigatable = true",
        "  anchor_point = bottom-right",
        "  x = -164",
        "  y = -54",
        "  width = 140",
        "  height = 32",
        "}",
    ])
    LAYOUT.parent.mkdir(parents=True,exist_ok=True)
    LAYOUT.write_text("\n".join(L)+"\n",encoding="utf-8")
    (ROOT/"config/fancymenu/customizablemenus.txt").write_text(
        "type = customizablemenus\n\nnet.minecraft.client.gui.screens.TitleScreen {\n}\n",encoding="utf-8")

def main():
    ASSETS.mkdir(parents=True,exist_ok=True)
    background()
    create_layout()
    assert LAYOUT.read_text(encoding="utf-8").count("action_type:mimicbutton")==5
    assert all((ASSETS/f).is_file() for f in (
        "chronicles_background.png","chronicles_button.png","chronicles_button_hover.png"))
    print("Rendered redesigned FancyMenu: custom title background, hover sprites and 6 buttons")

if __name__=="__main__":
    main()
