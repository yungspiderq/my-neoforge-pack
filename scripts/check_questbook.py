#!/usr/bin/env python3
"""Cross-reference generated SNBT chapters, assets and localizations."""
import re
import sys
from pathlib import Path
from nbtlib import parse_nbt

ROOT = Path(__file__).resolve().parent.parent
QUESTS = ROOT / "config/ftbquests/quests"
script = (ROOT / "kubejs/server_scripts/chronicles.js").read_text(encoding="utf-8")
chapters = sorted((QUESTS / "chapters").glob("*.snbt"))
assert len(chapters) == 14, f"expected 14 chapters, got {len(chapters)}"
en = parse_nbt((QUESTS / "lang/en_us.snbt").read_text(encoding="utf-8"))
ru = parse_nbt((QUESTS / "lang/ru_ru.snbt").read_text(encoding="utf-8"))
parse_nbt((QUESTS / "data.snbt").read_text(encoding="utf-8"))
parse_nbt((QUESTS / "chapter_groups.snbt").read_text(encoding="utf-8"))
ids, deps, rewards, custom_tasks, count = set(), [], [], [], 0
for file in chapters:
    c = parse_nbt(file.read_text(encoding="utf-8"))
    cid = str(c["id"])
    assert re.fullmatch("[0-9A-F]{16}", cid)
    assert f"chapter.{cid}.title" in en and f"chapter.{cid}.title" in ru
    assert len(c["images"]) >= 4
    for graphic in c["images"]:
        rel = str(graphic["image"]).removeprefix("kubejs:textures/")
        assert (ROOT / "kubejs/assets/kubejs/textures" / rel).exists(), (file, rel)
    qs = c["quests"]
    assert 18 <= len(qs) <= 30, (file,len(qs))
    count += len(qs)
    for q in qs:
        qid = str(q["id"])
        assert re.fullmatch("[0-9A-F]{16}", qid) and qid not in ids
        ids.add(qid)
        assert f"quest.{qid}.title" in en and f"quest.{qid}.title" in ru
        assert len(q["tasks"]) > 0 and len(q["rewards"]) > 0
        for d in q.get("dependencies", []):
            deps.append(str(d))
        for t in q["tasks"]:
            if str(t["type"]) == "custom":
                custom_tasks.append(str(t["id"]))
        for r in q["rewards"]:
            if str(r["type"]) == "custom":
                rewards.append(str(r["id"]))
for dep in deps:
    assert dep in ids, f"dangling dependency: {dep}"
for reward in rewards:
    assert f"FTBQuestsEvents.customReward('{reward}'" in script, reward
for task in custom_tasks:
    assert f"FTBQuestsEvents.customTask('{task}'" in script, task
assert count == 253, count
assert len(rewards) == 14, rewards
print(f"Validated {len(chapters)} chapters, {count} quests, {len(rewards)} custom rewards, {len(custom_tasks)} custom tasks, {len(deps)} dependencies")
