#!/usr/bin/env python3
"""Chronicles v0.4: validate SNBT, RU/EN, original art, quest DAG, exact IDs."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from nbtlib import parse_nbt

ROOT=Path(__file__).resolve().parent.parent
Q=ROOT/"config/ftbquests/quests"
SOURCE=ROOT/"scripts/quest_chapters.json"
EXP=ROOT/"scripts/quest_expansion.json"
EN=parse_nbt((Q/"lang/en_us.snbt").read_text(encoding="utf-8"))
RU=parse_nbt((Q/"lang/ru_ru.snbt").read_text(encoding="utf-8"))
REG=json.loads((ROOT/"scripts/registry/mc_registry_1.21.1.json").read_text(encoding="utf-8"))
EVENTS=(ROOT/"kubejs/server_scripts/chronicles.js").read_text(encoding="utf-8")
orig=json.loads(SOURCE.read_text(encoding="utf-8"))
expand=json.loads(EXP.read_text(encoding="utf-8"))
EXPECTED=[x[0] for x in orig]+[x["key"] for x in expand["new_chapters"]]
assert len(EXPECTED)==24 and len(set(EXPECTED))==24
assert len(orig)==14 and len(expand["new_chapters"])==10
for name in ("data.snbt","chapter_groups.snbt"):
    parse_nbt((Q/name).read_text(encoding="utf-8"))

allowed={"item","checkmark","custom","xp","dimension","advancement","biome","structure"}
types=Counter()
ids=set();deps=[];rewards=[];tasks=[];total=0
for ci,key in enumerate(EXPECTED):
    path=Q/"chapters"/(key+".snbt")
    assert path.is_file(),path
    chapter=parse_nbt(path.read_text(encoding="utf-8"))
    cid=str(chapter["id"])
    assert cid==f"{(0x71<<56)|((ci+1)<<32):016X}",(path,cid)
    assert f"chapter.{cid}.title" in EN and f"chapter.{cid}.title" in RU
    qs=chapter["quests"]
    assert 26<=len(qs)<=28,(key,len(qs))
    assert len(chapter["images"])==4,(key,len(chapter["images"]))
    for img in chapter["images"]:
        name=str(img["image"])
        assert name.startswith("kubejs:textures/"),name
        art=ROOT/"kubejs/assets/kubejs/textures"/name.removeprefix("kubejs:textures/")
        assert art.is_file() and art.stat().st_size>200,(key,art)
        if "text_on_image" in img:
            iid=str(img["id"])
            assert f"image.{iid}.title" in EN and f"image.{iid}.title" in RU
    for q in qs:
        qid=str(q["id"])
        assert re.fullmatch("[0-9A-F]{16}",qid) and qid not in ids,qid
        ids.add(qid)
        assert f"quest.{qid}.title" in EN and f"quest.{qid}.title" in RU,qid
        assert f"quest.{qid}.quest_desc" in EN and f"quest.{qid}.quest_desc" in RU,qid
        assert len(q["rewards"])>0 and len(q["tasks"])>0
        assert -30<=float(q["x"])<=65 and -30<=float(q["y"])<=30,(key,qid)
        for d in q.get("dependencies",[]):
            deps.append((qid,str(d)))
        for t in q["tasks"]:
            kind=str(t["type"])
            assert kind in allowed,(key,kind)
            types[kind]+=1
            if kind=="custom":
                tasks.append(str(t["id"]))
            if kind=="item":
                raw=str(t["item"]["id"])
                if raw.startswith("minecraft:"):
                    assert raw.removeprefix("minecraft:") in REG["items"],raw
            if kind=="advancement":
                assert str(t["advancement"]) in REG["advancements"],t
            if kind=="biome":
                assert str(t["biome"]) in REG["biomes"],t
            if kind=="structure":
                assert str(t["structure"]) in REG["structures"],t
            if kind=="dimension":
                assert str(t["dimension"]) in REG["dimensions"],t
            if kind=="xp":
                assert int(t["value"])>0,t
        for r in q["rewards"]:
            if str(r["type"])=="custom":
                rewards.append(str(r["id"]))
    total+=len(qs)
assert total==626,total
assert len(ids)==total
assert len(rewards)==24,len(rewards)
assert len(tasks)==2,len(tasks)
assert len(deps)>500,len(deps)
assert len(list((Q/"chapters").glob("*.snbt")))==24
for _,d in deps:
    assert d in ids,"Missing dependency "+d
for reward in rewards:
    assert f"FTBQuestsEvents.customReward('{reward}'" in EVENTS,reward
for task in tasks:
    assert f"FTBQuestsEvents.customTask('{task}'" in EVENTS,task
assert types["item"]>400,types
assert types["checkmark"]>40,types
assert types["biome"]>=10,types
# Confirm quest dependencies form a DAG, including inter-chapter gates.
graph={node:[] for node in ids}
for node,parent in deps:
    graph[node].append(parent)
visiting=set();done=set()
def visit(node):
    if node in done:return
    if node in visiting:raise AssertionError("Dependency cycle at "+node)
    visiting.add(node)
    for parent in graph[node]:visit(parent)
    visiting.remove(node)
    done.add(node)
for node in ids:visit(node)
# Existing quest IDs are intentionally unchanged to preserve progress.
for ci in range(14):
    prefix=f"{(0x72<<56)|((ci+1)<<32):016X}"
    assert f"{((0x72<<56)|((ci+1)<<32)|1):016X}" in ids
    assert f"{((0x72<<56)|((ci+1)<<32)|18):016X}" in ids
# New main menu has custom action-bound controls, not default vanilla buttons.
layout=(ROOT/"config/fancymenu/customization/chronicles_title_layout.txt").read_text(encoding="utf-8")
assert "chronicles_background.png" in layout
assert layout.count("action_type:mimicbutton")==5
assert layout.count("element_type = custom_button")>=6
for name in ("chronicles_background.png","chronicles_button.png","chronicles_button_hover.png"):
    art=ROOT/"config/fancymenu/assets"/name
    assert art.is_file() and art.stat().st_size>175,art
print(f"Validated {len(EXPECTED)} chapters, {total} quests, {len(deps)} dependency edges, {len(rewards)} custom rewards, {len(tasks)} custom tasks")
print("Tasks:",dict(types))
print("Checked: exact vanilla IDs, original quest IDs, dependency DAG, menu buttons, images and both languages.")
