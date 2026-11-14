#!/usr/bin/env python3
"""Chronicles 0.4: 24 non-linear FTB Quests chapters, localized & illustrated.

Preserves all existing 14 chapter IDs and the first 18 quest IDs in each.
Adds unique branch maps, custom tasks, milestone rewards and 10 new chapters.
"""
from __future__ import annotations

import json
import math
import random
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
QROOT = ROOT / "config/ftbquests/quests"
ART = ROOT / "kubejs/assets/kubejs/textures/gui/quests"
ITEM_ART = ROOT / "kubejs/assets/kubejs/textures/item"
SERVER_SCRIPTS = ROOT / "kubejs/server_scripts"
BASE = json.loads((ROOT/"scripts/quest_chapters.json").read_text(encoding="utf-8"))
EXP = json.loads((ROOT/"scripts/quest_expansion.json").read_text(encoding="utf-8"))

class Byte(int): pass
class Long(int): pass
class Double(float): pass

def val(x):
    return json.dumps(x, ensure_ascii=False)

def snbt(x, depth=0):
    t = "\t" * depth
    if isinstance(x, dict):
        if not x: return "{ }"
        bits = []
        for k,v in x.items():
            tag = k if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*",k) else val(k)
            bits.append(t+"\t"+tag+": "+snbt(v,depth+1))
        return "{\n"+",\n".join(bits)+"\n"+t+"}"
    if isinstance(x,list):
        if not x:return "[ ]"
        return "[\n"+",\n".join(t+"\t"+snbt(v,depth+1) for v in x)+"\n"+t+"]"
    if isinstance(x,Byte):return f"{int(x)}b"
    if isinstance(x,Long):return f"{int(x)}L"
    if isinstance(x,Double):return f"{float(x):.3f}d"
    if isinstance(x,bool):return "1b" if x else "0b"
    if isinstance(x,int):return str(x)
    if isinstance(x,float):return f"{x:.3f}d"
    return val(str(x))

def uid(kind, chapter, seq=0):
    assert 0<=chapter<255 and 0<=seq<4096
    return f"{((0x71+kind)<<56)|((chapter+1)<<32)|seq:016X}"

def itemstack(item):return {"count":1,"id":item}

def title_en(obj):
    if obj.startswith("biome:"):
        return "Explore "+obj.split(":")[-1].replace("_"," ").title()
    if obj.startswith("structure:"):
        return "Discover "+obj.split(":")[-1].replace("_"," ").title()
    if obj.startswith("adv:"):
        return "Advancement: "+obj.split("/")[-1].replace("_"," ").title()
    if obj.startswith("dim:"):
        return "Enter "+obj.split(":")[-1].replace("_"," ").title()
    if obj.startswith("xp:"):
        return "Reach level "+obj.split(":")[-1]
    if obj=="check":return "Milestone"
    return obj.split(":")[-1].replace("_"," ").title()

def parse_entry(text):
    parts=text.split("|",2)
    if len(parts)<2:raise ValueError("Expected id|Russian title: "+text)
    raw,ru=parts[:2]
    en=parts[2] if len(parts)>2 else title_en(raw)
    return {"raw":raw,"ru":ru,"en":en}

def rgb(hexstr):
    h=hexstr.lstrip("#")
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

def font(size,bold=False):
    paths=[
        "/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans"+("-Bold" if bold else "-Regular")+".ttf"
    ]
    for path in paths:
        try:return ImageFont.truetype(path,size)
        except OSError:pass
    return ImageFont.load_default()

LAYOUTS=["constellation","city","mountain","islands","spiral","gear","metro","wave","orbit","factory","rail","staircase"]

def make_badge(color,key,index):
    # Distinct graphic per chapter, not reused generic stripes.
    rng=random.Random(index*131+42)
    col=rgb(color)
    img=Image.new("RGBA",(660,144),(0,0,0,0))
    d=ImageDraw.Draw(img,"RGBA")
    for y in range(img.height):
        k=0.30+0.32*(1-y/img.height)
        d.line((0,y,img.width,y),fill=tuple(int(c*k) for c in col)+(241,),width=1)
    d.rectangle((6,6,653,137),outline=(*col,225),width=3)
    for x in range(24,636,45):
        d.line((x,0,x+55,144),fill=(255,239,213,15),width=2)
    # Vary the central motif by chapter: star chart, train path, gear or landscape.
    motif=index%6
    ox,oy=545,71
    if motif in (0,4):
        for r in (19,37,57):
            d.ellipse((ox-r,oy-r,ox+r,oy+r),outline=(*col,150),width=3)
        for k in range(12):
            a=2*math.pi*k/12
            d.line((ox+38*math.cos(a),oy+38*math.sin(a),
                    ox+61*math.cos(a),oy+61*math.sin(a)),fill=(245,217,155,170),width=4)
    elif motif in (1,5):
        for i in range(7):
            a=ox-95+i*30
            d.line((a,46,a+50,108),fill=(*col,135),width=5)
            d.ellipse((a+43,101,a+56,114),fill=(249,215,155,180))
    elif motif==2:
        for k in range(5):
            y=88-k*17
            d.line((430+k*22,y,645,y),fill=(*col,155),width=3)
        d.polygon([(495,103),(546,29),(598,103)],outline=(241,212,158,190))
    else:
        for j in range(5):
            r=12+12*j
            d.arc((ox-r,oy-r,ox+r,oy+r),30,330,fill=(*col,145),width=3)
    d.text((29,17),"C H R O N I C L E S",font=font(18,True),fill=(226,221,199,190))
    # The localized chapter name is rendered by FTB Quests from image.<id>.title.
    d.line((28,111,340,111),fill=(*col,185),width=3)
    img.save(ART/(key+"_banner.png"))
    # Chapter-specific badge for the quest map.
    medal=Image.new("RGBA",(160,160),(0,0,0,0))
    m=ImageDraw.Draw(medal,"RGBA")
    m.ellipse((7,7,153,153),fill=(*col,34),outline=(*col,188),width=5)
    m.ellipse((30,30,130,130),outline=(255,226,167,191),width=3)
    for k in range(8):
        a=math.pi*k/4+(index/18)
        xx=80+63*math.cos(a);yy=80+63*math.sin(a)
        m.ellipse((xx-3,yy-3,xx+3,yy+3),fill=(248,220,162,230))
    m.polygon([(80,30),(94,71),(128,80),(94,90),(80,128),(65,90),(32,80),(65,70)],
              fill=(*col,180),outline=(255,223,168,240))
    medal.save(ART/(key+"_seal.png"))
    # Stylized divider motif.
    line=Image.new("RGBA",(640,40),(0,0,0,0))
    ld=ImageDraw.Draw(line,"RGBA")
    ld.line((12,20,628,20),fill=(*col,160),width=3)
    for k in range(11):
        x=35+k*57
        ld.polygon([(x,13),(x+8,20),(x,27),(x-8,20)],fill=(247,216,153,160))
    line.save(ART/(key+"_divider.png"))

def positions(pattern):
    """Distinct geometric placement models, 24 nodes each."""
    cfg={
       "constellation":(6,4),"city":(4,6),"mountain":(3,8),
       "islands":(4,6),"spiral":(2,12),"gear":(6,4),
       "metro":(3,8),"wave":(2,12),"orbit":(4,6),
       "factory":(4,6),"rail":(3,8),"staircase":(4,6)}
    lanes, steps=cfg[pattern]
    coords=[]
    for lane in range(lanes):
        for step in range(steps):
            if pattern in ("constellation","gear"):
                angle=2*math.pi*(lane/lanes)+(0.12 if pattern=="gear" else -0.2)
                r=4.4+step*3.5
                x,y=r*math.cos(angle),r*math.sin(angle)
            elif pattern=="orbit":
                a=2*math.pi*step/steps+lane*0.16
                r=4.2+lane*3.4
                x,y=r*math.cos(a),r*math.sin(a)
            elif pattern=="spiral":
                a=step*0.43+lane*math.pi
                r=3.1+step*0.9
                x,y=r*math.cos(a),r*math.sin(a)
            elif pattern=="mountain":
                x=step*3.1
                y=(lane-1)*5.8-1.15*step+1.15*math.sin(step*1.15)
            elif pattern=="wave":
                x=step*2.9
                y=(lane-.5)*9+2.15*math.sin(step*0.8+lane)
            elif pattern=="islands":
                ox=(lane%2)*19;oy=(lane//2)*14
                x=ox+(step%3)*3.1
                y=oy+(step//3)*3.4
            elif pattern=="city":
                x=step*3.7+(lane%2)*1.1
                y=(lane-1.5)*5.2
            elif pattern=="staircase":
                x=(step if lane%2==0 else steps-1-step)*3.5
                y=lane*4.5-7
            elif pattern=="factory":
                x=step*3.7+(0.6 if step%2 else 0)
                y=(lane-1.5)*4.7
            elif pattern=="metro":
                x=step*3.15
                y=(lane-1)*7.2
            elif pattern=="rail":
                x=step*3.2
                y=(lane-1)*7.0 + math.sin(step*0.8+lane)*0.8
            else:raise ValueError(pattern)
            coords.append((round(x,3),round(y,3),lane,step))
    # root and final positions may be outside the rails or above/below an orbit.
    radial=pattern in ("constellation","gear","orbit","spiral")
    if radial:return coords,(-19.5,0),(0,18.5),lanes,steps
    if pattern=="islands":return coords,(-5,7),(29,7),lanes,steps
    if pattern=="staircase":return coords,(-5,0),(25,1),lanes,steps
    return coords,(-5,0),(steps*3.8+3,0),lanes,steps

def graph_for(pattern, root, goal_ids):
    coords,root_xy,final_xy,lanes,steps=positions(pattern)
    assert len(coords)==len(goal_ids)==24
    deps={}
    # Independent workstreams anchored at the chapter's briefing.
    for lane in range(lanes):
        for step in range(steps):
            i=lane*steps+step
            deps[goal_ids[i]]=[root] if step==0 else [goal_ids[i-1]]
            # Sparse cross-links add a discoverable workshop network without cycles.
            if step==steps-1 and lane>0 and pattern in ("factory","city","rail"):
                deps[goal_ids[i]].append(goal_ids[(lane-1)*steps+steps-2])
    finish=[goal_ids[(lane+1)*steps-1] for lane in range(lanes)]
    return coords,root_xy,final_xy,deps,finish

def task(raw,taskid):
    result={"id":taskid}
    if raw=="check":
        result["type"]="checkmark"
    elif raw.startswith("custom:"):
        result["type"]="custom"
    elif raw.startswith("dim:"):
        result.update(type="dimension",dimension=raw.removeprefix("dim:"))
    elif raw.startswith("xp:"):
        result.update(type="xp",value=Long(int(raw.split(":",1)[1])))
    elif raw.startswith("adv:"):
        result.update(type="advancement",advancement=raw.removeprefix("adv:"))
    elif raw.startswith("biome:"):
        result.update(type="biome",biome=raw.removeprefix("biome:"))
    elif raw.startswith("structure:"):
        result.update(type="structure",structure=raw.removeprefix("structure:"))
    else:
        if not re.fullmatch(r"[a-z0-9_]+:[a-z0-9_]+",raw):
            raise ValueError("Invalid exact item identifier: "+raw)
        result.update(type="item",item=itemstack(raw))
    return result

def objective_text(entry,story_en,story_ru,chapter,idx):
    raw=entry["raw"]
    k=(chapter*11+idx*7)%9
    flavour_en=[
      "Trace the next discovery on your workshop map.",
      "A small mechanism can change the whole expedition.",
      "Check the resources before moving to the next workshop.",
      "Take a different route through the chapter.",
      "Put this discovery to use in a real build.",
      "Keep an example in your expedition archive.",
      "This step opens a new part of the network.",
      "Turn what you have learned into a practical experiment.",
      "Your logbook needs one more recorded milestone."
    ]
    flavour_ru=[
      "Отметь находку на карте мастерской.",
      "Даже небольшая находка может изменить целую экспедицию.",
      "Подготовь ресурсы перед следующим испытанием.",
      "Исследуй ещё одну ветку этой главы.",
      "Используй открытие в собственном проекте.",
      "Сохрани результат для коллекции исследователя.",
      "Этот этап открывает следующий маршрут.",
      "Преврати знание в небольшой практический опыт.",
      "В летописи не хватает ещё одной важной отметки."
    ]
    if raw=="check":
        note_en="A creative milestone: confirm when your own project is ready."
        note_ru="Творческая цель: отметь выполнение вручную, когда собственный проект готов."
    elif raw.startswith("xp:"):
        note_en="Gain experience through any activities you enjoy."
        note_ru="Накопи опыт любым удобным способом."
    elif raw.startswith(("biome:","dim:","structure:")):
        note_en="Exploration objective. Visit this location to complete the task."
        note_ru="Задание на исследование. Посети нужное место."
    elif raw.startswith("adv:"):
        note_en="Complete the corresponding vanilla Minecraft advancement."
        note_ru="Получи указанное ванильное достижение Minecraft."
    else:
        note_en="Obtain this item at least once; FTB Quests will not consume it."
        note_ru="Получи указанный предмет; FTB Quests не будет его расходовать."
    return [story_en,note_en,flavour_en[k]],[story_ru,note_ru,flavour_ru[k]]

def generate():
    ART.mkdir(parents=True,exist_ok=True)
    ITEM_ART.mkdir(parents=True,exist_ok=True)
    SERVER_SCRIPTS.mkdir(parents=True,exist_ok=True)
    (ROOT/"kubejs/startup_scripts").mkdir(parents=True,exist_ok=True)
    (QROOT/"chapters").mkdir(parents=True,exist_ok=True)
    (QROOT/"lang").mkdir(parents=True,exist_ok=True)
    # Clean only generated files, so removed chapters don't linger in the index.
    for path in (QROOT/"chapters").glob("*.snbt"):path.unlink()
    for path in ART.glob("*.png"):path.unlink()
    (QROOT/"data.snbt").write_text(snbt({
        "default_consume_items":Byte(0),"default_quest_shape":"circle",
        "fallback_locale":"en_us","version":13})+"\n",encoding="utf-8")
    (QROOT/"chapter_groups.snbt").write_text(snbt({"chapter_groups":[]})+"\n",encoding="utf-8")
    old_keys={c[0] for c in BASE}
    extended=[]
    for b in BASE:
        key,en,ru,desc_en,desc_ru,icon,color,goals=b
        extras=EXP["extras"].get(key)
        if extras is None or len(extras)!=8:raise ValueError("8 additional objectives required for "+key)
        extended.append(dict(key=key,en=en,ru=ru,introEn=desc_en,introRu=desc_ru,
            icon=icon,color=color,layout=LAYOUTS[len(extended)%len(LAYOUTS)],
            goals=[parse_entry(v) for v in goals+extras],base=True))
    for obj in EXP["new_chapters"]:
        if obj["key"] in old_keys:raise ValueError("Duplicate key "+obj["key"])
        extended.append({**obj,"goals":[parse_entry(v) for v in obj["goals"]],"base":False})
    chapter_index={v["key"]:i for i,v in enumerate(extended)}
    assert len(extended)==24,(len(extended))
    en_lang={};ru_lang={};events=[]
    allids=set();custom_rewards=0;custom_tasks=0
    with (ROOT/"docs/QUEST_MAP.md").open("w",encoding="utf-8") as report:
        report.write("# Chronicles — interactive quest maps\n\n")
        report.write("A unique graph layout for each book chapter, not identical three lanes.\n\n")
        for ci,obj in enumerate(extended):
            key=obj["key"];rootid=uid(1,ci,1)
            basename=obj["en"];ru_name=obj["ru"];motive=obj["layout"]
            make_badge(obj["color"],key,ci)
            cid=uid(0,ci)
            chapter={"filename":key,"group":"","icon":itemstack(obj["icon"]),
                     "id":cid,"order_index":ci,"default_hide_dependency_lines":Byte(0),
                     "default_quest_shape":"circle","images":[],"quest_links":[],"quests":[]}
            en_lang["chapter."+cid+".title"]=basename
            ru_lang["chapter."+cid+".title"]=ru_name
            en_lang["chapter."+cid+".chapter_subtitle"]=[
                obj["introEn"],f"{motive.title()} layout: explore multiple routes, then claim the chapter seal."]
            ru_lang["chapter."+cid+".chapter_subtitle"]=[
                obj["introRu"],"Разветвлённая карта заданий: изучай маршруты в любом порядке и открывай финальную печать."]
            goals=obj["goals"]
            if len(goals)!=24:raise ValueError("Exactly 24 goals required: "+key)
            # Preserve 14 original chapter IDs, original first 16 goals, original finale ID.
            goal_js=list(range(1,17))+list(range(19,27)) if obj["base"] else list(range(1,25))
            finale_j=17 if obj["base"] else 25
            assert len(goal_js)==24
            goalids=[uid(1,ci,j+1) for j in goal_js]
            coords,rxy,fxy,deps,ends=graph_for(motive,rootid,goalids)
            # For all existing chapters use thematic early unlocks, never force endgame to start Create.
            unlocks={
               "awakening":None,"homestead":"awakening","mines":"awakening",
               "fields":"homestead","builder":"homestead","wilderness":"awakening",
               "redstone":"mines","ocean":"wilderness","alchemy":"nether",
               "nether":"mines","end":"nether","create_first":"mines",
               "create_motion":"create_first","create_factory":"create_motion"
            }
            unlock=obj.get("unlock") if not obj["base"] else unlocks.get(key)
            if unlock and unlock not in chapter_index:raise ValueError("Bad unlock: "+key)
            entrydep=[uid(1,chapter_index[unlock],
                       18 if extended[chapter_index[unlock]]["base"] else 26)] if unlock else []
            decorated=[
              (key+"_banner.png",(0,-21), (22.0,4.8),True),
              (key+"_seal.png",(fxy[0]+2.4,fxy[1]-2.4),(2.6,2.6),False),
              (key+"_divider.png",(0,-14), (22.0,1.1),False),
              (key+"_divider.png",(0,24), (22.0,1.1),False)]
            for n,(name,xy,wh,with_title) in enumerate(decorated):
                iid=uid(4,ci,n+1)
                # Decorative art must not obscure the quest icons. Render behind.
                chapter["images"].append({
                    "id":iid,"image":f"kubejs:textures/gui/quests/{name}",
                    "x":Double(xy[0]),"y":Double(xy[1]),
                    "width":Double(wh[0]),"height":Double(wh[1]),
                    "rotation":Double(0),"order":-150 if n==0 else -200,
                    "position_locked":Byte(1), **({"text_on_image":Byte(1),
                        "text_shadow":Byte(1),"text_inset":8} if with_title else {})})
                if with_title:
                    en_lang[f"image.{iid}.title"]=basename
                    ru_lang[f"image.{iid}.title"]=ru_name
            def put(j,raw,ru_title,en_title,parents,xy,kind="regular"):
                nonlocal custom_rewards,custom_tasks
                qid=uid(1,ci,j+1);tid=uid(2,ci,j+1)
                reward_id=uid(3,ci,j+1)
                rewards=[{"id":reward_id,"type":"xp","xp":30+ci*7+(j%7)*12}]
                if j%7==0 and kind=="regular":
                    gift=["minecraft:bread","minecraft:torch","minecraft:paper","minecraft:cooked_porkchop"][ci%4]
                    rewards.append({"id":uid(3,ci,512+j),"type":"item",
                                    "item":itemstack(gift),"count":3+(ci%4)})
                if j>0 and j%9==0:
                    rewards.append({"id":uid(3,ci,640+j),"type":"xp_levels","xp_levels":1+(ci//8)})
                if kind=="final":
                    rewards.append({"id":uid(3,ci,800+j),"type":"item",
                                    "item":itemstack("kubejs:chronicle_page")})
                    custom_id=uid(3,ci,900+j)
                    rewards.append({"id":custom_id,"type":"custom"})
                    gifts=["4x minecraft:iron_ingot","2x minecraft:emerald",
                           "6x minecraft:golden_carrot","8x minecraft:redstone"]
                    gift=gifts[ci%4]
                    events.append(
                        f"FTBQuestsEvents.customReward('{custom_id}', event => {{\n"
                        "  const p = event.player\n"
                        f"  p.give('{gift}')\n"
                        f"  p.persistentData.putBoolean('myneoforge_{key}', true)\n"
                        f"  p.tell('§6[Chronicles] §f{basename} — complete!')\n"
                        "})\n")
                    custom_rewards+=1
                obj_id=(raw if re.fullmatch(r"[a-z0-9_]+:[a-z0-9_]+",raw) else chapter["icon"]["id"])
                node={"id":qid,"icon":itemstack(obj_id),
                      "x":Double(xy[0]),"y":Double(xy[1]),
                      "tasks":[task(raw,tid)],"rewards":rewards}
                if parents:node["dependencies"]=parents
                if kind in ("final","root"):node["shape"]="hexagon";node["size"]=Double(1.5)
                elif raw=="check":node["shape"]="diamond";node["size"]=Double(1.2)
                elif raw.startswith(("biome:","adv:","dim:","structure:")):
                    node["shape"]="pentagon";node["size"]=Double(1.25)
                elif ci>=11 and raw.startswith("create:"):
                    node["shape"]="gear";node["size"]=Double(1.2)
                elif j%5==0:node["shape"]="square"
                elif j%3==0:node["shape"]="octagon"
                else:node["shape"]="circle"
                chapter["quests"].append(node)
                desc_en,desc_ru=objective_text({"raw":raw},obj["introEn"],obj["introRu"],ci,j)
                en_lang["quest."+qid+".title"]=en_title
                ru_lang["quest."+qid+".title"]=ru_title
                en_lang["quest."+qid+".quest_desc"]=desc_en
                ru_lang["quest."+qid+".quest_desc"]=desc_ru
                if qid in allids:raise ValueError("Quest ID collision "+qid)
                allids.add(qid)
                return qid,tid
            put(0,"check","Начало главы","Chapter briefing",entrydep,rxy,kind="root")
            for n,(entry,j,coord,qid) in enumerate(zip(goals,goal_js,coords,goalids)):
                put(j,entry["raw"],entry["ru"],entry["en"],deps[qid],coord[:2])
            put(finale_j,"check","Финальная печать","The chapter seal",
                ends,fxy,kind="final")
            if key=="wilderness":
                extra,taskid=put(18,"custom:storm","Дозор под грозой","Stormwatch",
                                  [rootid],(rxy[0],rxy[1]+4.5))
                en_lang["quest."+extra+".quest_desc"]=[
                    "Optional: stay near your base during three thunderstorm observation checks.",
                    "KubeJS advances this task automatically while thunder is active."]
                ru_lang["quest."+extra+".quest_desc"]=[
                    "Дополнительно: проведи три цикла наблюдения во время грозы.",
                    "KubeJS автоматически засчитывает время во время грозы."]
                events.append(f"FTBQuestsEvents.customTask('{taskid}', event => {{\n"
                    "  event.maxProgress = 3\n"
                    "  event.setCheckTimer(100)\n"
                    "  event.setCheck((task, player) => {\n"
                    "    if (player.level.thundering) task.progress++\n"
                    "  })\n"
                    "})\n")
                custom_tasks+=1
            if key=="create_mastery":
                extra,tid=put(26,"custom:archive","Архив мастерства",
                      "The Master Archivist",[rootid],(rxy[0],rxy[1]+4.8))
                en_lang["quest."+extra+".quest_desc"]=[
                    "Bonus: claim the chapter seal rewards in three Create chapters.",
                    "KubeJS reads your persistent achievement flags from the rewards."]
                ru_lang["quest."+extra+".quest_desc"]=[
                    "Бонус: забери награды за три главы Create.",
                    "KubeJS проверит сохранённые отметки о прохождении."]
                events.append(f"FTBQuestsEvents.customTask('{tid}', event => {{\n"
                    "  event.maxProgress = 1\n"
                    "  event.setCheckTimer(40)\n"
                    "  event.setCheck((task, player) => {\n"
                    "    const d = player.persistentData\n"
                    "    if (d.getBoolean('myneoforge_create_first') &&\n"
                    "        d.getBoolean('myneoforge_create_motion') &&\n"
                    "        d.getBoolean('myneoforge_create_factory')) task.progress = 1\n"
                    "  })\n"
                    "})\n")
                custom_tasks+=1
            out=QROOT/"chapters"/(key+".snbt")
            out.write_text(snbt(chapter)+"\n",encoding="utf-8")
            report.write(f"- **{obj['ru']}** / {basename}: {len(chapter['quests'])} quests; "
                         f"topology {motive}; unlocked by {unlock or 'start'}\n")
    (QROOT/"lang/en_us.snbt").write_text(snbt(dict(sorted(en_lang.items())))+"\n",encoding="utf-8")
    (QROOT/"lang/ru_ru.snbt").write_text(snbt(dict(sorted(ru_lang.items())))+"\n",encoding="utf-8")
    (SERVER_SCRIPTS/"chronicles.js").write_text(
        "// Generated, requires FTB XMod Compat 21.1.11 and KubeJS.\n\n"+
        "\n".join(events),encoding="utf-8")
    (ROOT/"kubejs/startup_scripts/chronicle_items.js").write_text(
        "StartupEvents.registry('item', event => {\n"
        "  event.create('chronicle_page').displayName('Chronicle Page').texture('kubejs:item/chronicle_page')\n"
        "})\n",encoding="utf-8")
    img=Image.new("RGBA",(32,32),(0,0,0,0));dr=ImageDraw.Draw(img,"RGBA")
    dr.polygon([(16,1),(29,9),(27,25),(16,31),(5,25),(3,9)],
               fill=(207,173,111,255),outline=(95,75,57,255))
    dr.ellipse((8,9,24,25),fill=(40,84,100,255),outline=(239,222,163,255),width=2)
    dr.line((16,8,16,26),fill=(242,219,150,255),width=2)
    img.save(ITEM_ART/"chronicle_page.png")
    # Update welcome message without flooding returning players.
    (SERVER_SCRIPTS/"player_welcome.js").write_text(
        "PlayerEvents.loggedIn(event => {\n"
        "  const d = event.player.persistentData\n"
        "  if (!d.getBoolean('myneoforge_chronicles_04')) {\n"
        "    d.putBoolean('myneoforge_chronicles_04', true)\n"
        "    event.player.tell('§6[Chronicles] §f24 illustrated chapters are available in FTB Quests!')\n"
        "  }\n"
        "})\n",encoding="utf-8")
    print(f"Chronicles v0.4: {len(extended)} chapters, {len(allids)} quests, "
          f"{custom_rewards} custom rewards, {custom_tasks} custom tasks, {len(list(ART.glob('*.png')))} artworks")

if __name__=="__main__":
    generate()
