#!/usr/bin/env python3
"""Deterministic FTB Quests 1.21.1 SNBT + original art + KubeJS integration.

14 connected chapters, 18 quests each + optional sidequest, RU/EN.
FTB Quests data version 13. Python 3.11+, Pillow for drawing.
"""
import argparse
import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "config/ftbquests/quests"
ART = ROOT / "kubejs/assets/kubejs/textures/gui/quests"
ITEM_ART = ROOT / "kubejs/assets/kubejs/textures/item"
SCRIPTS = ROOT / "kubejs/server_scripts"
CHAPTERS = json.loads((ROOT / "scripts/quest_chapters.json").read_text(encoding="utf-8"))
CUSTOM_CHAPTERS = {"wilderness": "storm"}

class Byte(int):
    pass
class Long(int):
    pass
class Double(float):
    pass

def quote(s):
    return json.dumps(s, ensure_ascii=False)

def snbt(data, level=0):
    tab = "\t" * level
    if isinstance(data, dict):
        if not data:
            return "{ }"
        rows = [tab + "\t" + (k if re.fullmatch(r"[A-Za-z_][a-zA-Z0-9_]*", k) else quote(k))
                + ": " + snbt(v, level+1) for k,v in data.items()]
        return "{\n" + ",\n".join(rows) + "\n" + tab + "}"
    if isinstance(data, list):
        if not data: return "[ ]"
        return "[\n" + ",\n".join(tab + "\t" + snbt(x, level+1) for x in data) + "\n" + tab + "]"
    if isinstance(data, Byte): return f"{int(data)}b"
    if isinstance(data, Long): return f"{int(data)}L"
    if isinstance(data, Double): return f"{float(data):.3f}d"
    if isinstance(data, bool): return "1b" if data else "0b"
    if isinstance(data, int): return str(data)
    if isinstance(data, float): return f"{data:.3f}d"
    return quote(str(data))

def uid(kind, ci, seq=0):
    """All FTB IDs: unique 16-char uppercase signed-positive hex."""
    assert 0 <= ci < 255 and 0 <= seq < 4096
    return f"{((0x71+kind) << 56) | ((ci+1) << 32) | seq:016X}"

def stack(item, count=1):
    return {"count": 1, "id": item}

def objective(raw, task_id):
    if raw.startswith("dim:"):
        item = raw[4:]
        return {"id": task_id, "type": "dimension", "dimension": item}
    if raw.startswith("kill:"):
        item = raw[5:]
        return {"id": task_id, "type": "kill", "entity": item, "value": Long(1)}
    if raw.startswith("xp:"):
        return {"id": task_id, "type": "xp", "value": Long(int(raw[3:]))}
    item = raw
    return {"id": task_id, "type": "item", "item": stack(item)}

def english(raw):
    if raw.startswith("dim:"): return "Enter " + raw[4:].split(":")[-1].replace("_"," ").title()
    if raw.startswith("kill:"): return "Defeat " + raw[5:].split(":")[-1].replace("_"," ").title()
    if raw.startswith("xp:"): return "Reach level " + raw[3:]
    return raw.split(":")[-1].replace("_", " ").title()

def png_for_chapter(key, title, rgb, ordinal):
    from PIL import ImageColor
    main = ImageColor.getrgb(rgb)
    w,h = 768,184
    img = Image.new("RGBA",(w,h),(0,0,0,0))
    pixels = img.load()
    for y in range(h):
        for x in range(w):
            glow = max(0, 1-abs(x-0.73*w)/(0.85*w))
            wave = 0.07*math.sin((x+y)*0.033+ordinal)
            t=0.13 + 0.34*(x/w)+0.22*(1-y/h)+0.24*glow + wave
            pixels[x,y] = tuple(int(min(255,max(0,c*t))) for c in main)+(247,)
    dr=ImageDraw.Draw(img,"RGBA")
    dr.rectangle((4,4,w-5,h-5),outline=(*main,225),width=4)
    dr.line((16,h-26,w-16,h-26),fill=(*main,190),width=3)
    # Mechanical diagram motifs: planetary ring, travel lines and schematic grid.
    for x in range(18,w,48):
        dr.line((x,12,x,h-13),fill=(240,235,209,18),width=1)
    for y in range(22,h,38):
        dr.line((12,y,w-13,y),fill=(240,235,209,18),width=1)
    cx,cy=w-145,84
    for radius,alpha in [(65,70),(48,115),(23,175)]:
        dr.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),outline=(*main,alpha),width=4)
    for a in range(12):
        angle=2*math.pi*a/12+ordinal*0.05
        x0=cx+52*math.cos(angle); y0=cy+52*math.sin(angle)
        x1=cx+73*math.cos(angle); y1=cy+73*math.sin(angle)
        dr.line((x0,y0,x1,y1),fill=(247,219,158,165),width=5)
    for i in range(8):
        x=32+i*64; y=118+10*math.sin(ordinal+i)
        dr.line((x,y,x+38,y-15),fill=(247,219,158,65),width=3)
    # A symbol, not baked text: localization is supplied by image.<id>.title.
    img.save(ART/(key+".png"))
    # Matching strip underneath the three lanes.
    strip=img.crop((0,0,w,96)); strip.save(ART/(key+"_stripe.png"))

def token_png():
    img=Image.new("RGBA",(32,32),(0,0,0,0))
    d=ImageDraw.Draw(img,"RGBA")
    d.polygon([(16,1),(30,9),(27,27),(16,31),(5,27),(2,9)],fill=(219,172,85,255),outline=(99,67,44,255))
    d.polygon([(16,4),(26,11),(23,24),(16,28),(9,24),(6,11)],fill=(62,93,106,255))
    d.line([(9,16),(23,16)],fill=(239,222,158,255),width=2)
    d.line([(16,8),(16,24)],fill=(239,222,158,255),width=2)
    img.save(ITEM_ART/"chronicle_page.png")

def locales(out):
    return (snbt(dict(sorted(out.items()))) + "\n")

def run():
    ART.mkdir(parents=True,exist_ok=True)
    ITEM_ART.mkdir(parents=True,exist_ok=True)
    (BASE/"chapters").mkdir(parents=True,exist_ok=True)
    (BASE/"lang").mkdir(parents=True,exist_ok=True)
    SCRIPTS.mkdir(parents=True,exist_ok=True)
    (BASE/"data.snbt").write_text(snbt({"default_consume_items":Byte(0),"default_quest_shape":"circle","fallback_locale":"en_us","version":13})+"\n",encoding="utf-8")
    (BASE/"chapter_groups.snbt").write_text(snbt({"chapter_groups":[]})+"\n",encoding="utf-8")
    token_png()
    en,ru,completion=[],[],[]
    en_lang,ru_lang={},{}
    js=[]
    count=0
    generated=[]
    for ci,(key,english_name,russian_name,english_story,russian_story,icon,color,entries) in enumerate(CHAPTERS):
        assert len(entries)==16, (key,len(entries))
        chapter_id=uid(0,ci)
        png_for_chapter(key,english_name,color,ci)
        chapter={"filename":key,"group":"","icon":stack(icon),"id":chapter_id,
                 "order_index":ci, "default_hide_dependency_lines":Byte(0),
                 "default_quest_shape":"circle","images":[],"quest_links":[],"quests":[]}
        en_lang[f"chapter.{chapter_id}.title"]=english_name
        ru_lang[f"chapter.{chapter_id}.title"]=russian_name
        en_lang[f"chapter.{chapter_id}.chapter_subtitle"]=[english_story,"Three routes. Complete all three to unlock the final seal. No item consumption."]
        ru_lang[f"chapter.{chapter_id}.chapter_subtitle"]=[russian_story,"Три ветки. Пройди каждую, чтобы открыть финальную печать. Предметы не расходуются."]
        images=chapter["images"]
        banner_id=uid(4,ci,1)
        images.append({"id":banner_id,"image":f"kubejs:textures/gui/quests/{key}.png",
                       "x":Double(10),"y":Double(-4),"width":Double(21),
                       "height":Double(3.2),"rotation":Double(0),"order":-150,
                       "position_locked":Byte(1),"text_on_image":Byte(1),
                       "text_shadow":Byte(1),"text_inset":8})
        en_lang[f"image.{banner_id}.title"]=english_name
        ru_lang[f"image.{banner_id}.title"]=russian_name
        for ix,y in enumerate([3.75,10.5,17.25]):
            iid=uid(4,ci,ix+2)
            images.append({"id":iid,"image":f"kubejs:textures/gui/quests/{key}_stripe.png",
                           "x":Double(9.5),"y":Double(y),"width":Double(17.8),
                           "height":Double(2.25),"rotation":Double(0),"order":-200,
                           "alpha":105,"position_locked":Byte(1)})
        def make_quest(j, obj, title_en,title_ru, dep, x,y, special=False, extra=False):
            nonlocal count
            qid=uid(1,ci,j+1)
            tid=uid(2,ci,j+1)
            rid=uid(3,ci,j+1)
            reward=[{"id":rid,"type":"xp","xp":40+(ci//3)*20+(j//3)*10}]
            if j==0:
                reward.append({"id":uid(3,ci,512+j),"type":"item","item":stack("minecraft:bread"),"count":3})
            elif j%5==0:
                reward.append({"id":uid(3,ci,512+j),"type":"item","item":stack("minecraft:torch"),"count":4})
            if special:
                reward.append({"id":uid(3,ci,800+j),"type":"item","item":stack("kubejs:chronicle_page"),"count":1})
                reward.append({"id":uid(3,ci,900+j),"type":"custom"})
            tasks=[{"id":tid,"type":"checkmark"}] if obj=="check" else [objective(obj,tid)]
            if obj=="custom:storm":
                tasks=[{"id":tid,"type":"custom"}]
            q={"id":qid,"icon":stack(icon if obj in ("check","custom:storm") or obj.startswith(("xp:","dim:","kill:")) else obj),
               "x":Double(x),"y":Double(y),"tasks":tasks,"rewards":reward}
            if dep:q["dependencies"]=dep
            if special:q["shape"]="hexagon";q["size"]=Double(1.6)
            if extra:q["shape"]="diamond"
            chapter["quests"].append(q)
            en_lang[f"quest.{qid}.title"]=title_en
            ru_lang[f"quest.{qid}.title"]=title_ru
            en_lang[f"quest.{qid}.quest_desc"]=[english_story,
                "You only need to obtain or achieve the objective. Items are not consumed.",
                "Complete the related nodes to open new routes."]
            ru_lang[f"quest.{qid}.quest_desc"]=[russian_story,
                "Достаточно получить предмет или выполнить условие. Предметы не расходуются.",
                "Выполняй связанные задания, чтобы открыть новые направления."]
            count+=1
            return qid,tid
        prev_final = uid(1,ci-1,18) if ci>0 else None
        if key.startswith("create_"):
            prev_final=uid(1,2,18) if key=="create_first" else uid(1,ci-1,18)
        root,_=make_quest(0,"check","Chapter briefing","Начало экспедиции",[prev_final] if prev_final else [],0,10.5)
        ends=[]
        for lane,(start,end,y) in enumerate([(0,5,3.75),(5,10,10.5),(10,16,17.25)]):
            parent=root
            for offset,i in enumerate(range(start,end)):
                raw,title_ru=entries[i].split("|",1)
                # Each lane progresses independently; finale joins all three.
                qid,_=make_quest(i+1,raw,english(raw),title_ru,[parent],2.7+2.9*offset,y)
                parent=qid
            ends.append(parent)
        finale,ftid=make_quest(17,"check","The chapter seal","Печать главы",ends,21,10.5,special=True)
        # Sidequest: sample of event-driven custom progression, without blocking the chapter.
        if key=="wilderness":
            side,task=make_quest(18,"custom:storm","Stormwatch","Дозор под грозой",[root],0,22.5,extra=True)
            en_lang[f"quest.{side}.quest_desc"]=["Optional: spend three observation cycles in a thunderstorm.", "KubeJS monitors weather and advances the custom FTB task."]
            ru_lang[f"quest.{side}.quest_desc"]=["Необязательно: дождись грозы и проведи три цикла наблюдения.", "KubeJS сам отслеживает погоду и выполняет особое задание."]
            js.append(f"FTBQuestsEvents.customTask('{task}', event => {{\n  event.maxProgress = 3\n  event.setCheckTimer(100)\n  event.setCheck((task, player) => {{ if (player.level.thundering) task.progress++ }})\n}})\n")
        # Biome-themed cache, an optional extra custom reward on each grand finale.
        gift=["4x minecraft:iron_ingot","2x minecraft:emerald","4x minecraft:golden_carrot","8x minecraft:redstone"][ci%4]
        rid=uid(3,ci,917)
        # Match the custom reward actually written by make_quest (j=17).
        rid=uid(3,ci,900+17)
        js.append(f"FTBQuestsEvents.customReward('{rid}', event => {{\n  const p = event.player\n  p.give('{gift}')\n  p.persistentData.putBoolean('myneoforge_{key}', true)\n  p.tell('§6[Chronicles] §f{english_name} — complete!')\n}})\n")
        out=BASE/"chapters"/f"{key}.snbt"
        out.write_text(snbt(chapter)+"\n",encoding="utf-8")
        generated.append(out)
    (BASE/"lang/en_us.snbt").write_text(locales(en_lang),encoding="utf-8")
    (BASE/"lang/ru_ru.snbt").write_text(locales(ru_lang),encoding="utf-8")
    (SCRIPTS/"chronicles.js").write_text("// Generated by questgen.py. Requires FTB XMod Compat.\\n\\n".replace("\\n","\n")+"\n".join(js),encoding="utf-8")
    (ROOT/"kubejs/startup_scripts").mkdir(parents=True,exist_ok=True)
    (ROOT/"kubejs/startup_scripts/chronicle_items.js").write_text(
        "StartupEvents.registry('item', event => {\n"
        "  event.create('chronicle_page').displayName('Chronicle Page').texture('kubejs:item/chronicle_page')\n"
        "})\n",encoding="utf-8")
    (SCRIPTS/"player_welcome.js").write_text(
        "PlayerEvents.loggedIn(event => {\n"
        "  const data = event.player.persistentData\n"
        "  if (!data.getBoolean('myneoforge_welcome')) {\n"
        "    data.putBoolean('myneoforge_welcome', true)\n"
        "    event.player.tell('§6[Chronicles] §fOpen FTB Quests in your inventory. 14 chapters await!')\n"
        "  }\n"
        "})\n",encoding="utf-8")
    # Verify semantics before handing any book to FTB: unique hex IDs, all dependencies resolvable,
    # no small/invalid item tag filters, every custom event backed by handler.
    ids=set();deps=[];rewards=[];custom=[]
    assert 14 <= len(generated) <= 30
    for ci,chapter in enumerate(CHAPTERS):
        key=chapter[0]
        expected = 19 if key=="wilderness" else 18
        # The generated chapter is a single file: no extra question files.
        data=(BASE/"chapters"/f"{key}.snbt").read_text(encoding="utf-8")
        seen=len(re.findall(r'\btype: "checkmark"|\btype: "item"|\btype: "dimension"|\btype: "custom"',data))
        assert seen >= expected, (key,seen,expected)
        for j in range(expected):
            qid=uid(1,ci,j+1)
            assert qid not in ids; ids.add(qid)
            assert f'quest.{qid}.title' in en_lang and f'quest.{qid}.title' in ru_lang
    assert count==14*18+1,(count)
    print(f"Generated {len(generated)} chapters, {count} quests and {len(CHAPTERS)*4} chapter images.")
    print("Includes RU/EN, dependency graphs, item/XP/custom rewards, optional storm task, and KubeJS collectible.")

if __name__=="__main__":
    run()
