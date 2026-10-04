#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Headless-тесты ядра Modpack Manager (packlib) — запускаются в CI.

Проверяют сценарий, из-за которого появился v1.3.2: лаунчеры Theseus-семейства
(AstralRinth, Modrinth App) при обновлении пака НИЧЕГО не удаляют, поэтому
устаревшие файлы (исключённый из пака мод, главы квестов прошлой версии)
выживают и крашат игру. Лечение — чистая переустановка `clean_reinstall`.

Сервер поднимается локальный (http.server) с фейковым паком на 4 записи,
никаких внешних скачиваний. Запуск:  python3 app/test_packlib.py
"""

import hashlib
import http.server
import os
import shutil
import sys
import tempfile
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import packlib as P  # noqa: E402

FAILS = []
CHECKS = [0]


def ok(cond, msg):
    CHECKS[0] += 1
    print(("  OK  " if cond else " FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def sha(data, alg="sha256"):
    return hashlib.new(alg, data).hexdigest()


def main():
    orig_cwd = os.getcwd()
    root = tempfile.mkdtemp(prefix="packlib-test-")
    srv_root = os.path.join(root, "server")
    game = os.path.join(root, "game")

    # ---------------- фейковый пак ----------------
    overworld = b'{ chapter_id: "1111111111111111", quests: [ ], images: [ ] }\n'
    info = b"My NeoForge Pack test info\n"
    personal = b"options personalized by player\n"
    foojar = b"FAKE-MOD-JAR-CONTENT" * 100

    def w(rel, data):
        p = os.path.join(srv_root, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as fh:
            fh.write(data)

    w("config/ftbquests/quests/chapters/overworld.snbt", overworld)
    w("config/modpack-info.txt", info)
    w("config/personal.cfg", personal)          # preserve-файл (внутри config/)
    w("mods/foo.jar", foojar)                   # «мод» с локального сервера

    pwtoml_body = (
        'name = "Foo Mod"\nfilename = "foo.jar"\nside = "both"\n\n'
        '[download]\nurl = "__BASE__/mods/foo.jar"\nhash-format = "sha1"\nhash = "%s"\n\n'
        '[update]\n[update.modrinth]\nmod-id = "foo"\nversion = "1.0.0"\n'
    ) % sha(foojar, "sha1")

    # ---------------- фейковая папка игры со СТАРЫМ мусором ----------------
    def g(rel, data):
        p = os.path.join(game, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as fh:
            fh.write(data)

    g("mods/certain-questing-additions-1.2.0.4.jar", b"STALE CQA JAR" * 50)  # выпущен из пака
    g("mods/foo.jar", b"BROKEN OLD JAR")                                      # битая версия
    g("config/ftbquests/quests/chapters/start.snbt", b"OLD CHAPTER v2")       # старая глава
    g("config/ftbquests/quests/chapters/overworld.snbt", b"OLD overworld")    # устаревшая копия
    g("config/ftbquests/quests/data.snbt", b"OLD data")                       # в индексе больше нет
    g("config/modpack-info.txt", b"old info")
    g("config/personal.cfg", personal)                                        # preserve — личная версия
    g("saves/My World/level.dat", b"WORLD PROGRESS")
    g("local/ftbquests/user.snbt", b"QUEST PROGRESS")
    g("journeymap/data/point.dat", b"WAYPOINTS")
    g("options.txt", b"KEYBINDS")
    g("packsync/pack-url.txt", b"http://example.invalid/pack.toml\n")
    g("packwiz.json", b'{"files":{}}')
    g("logs/latest.log", b"log")

    # ---------------- локальный сервер ----------------
    os.chdir(srv_root)
    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda *a: None
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % port

    w("mods/foo.pw.toml", pwtoml_body.replace("__BASE__", base).encode())
    with open(os.path.join(srv_root, "mods", "foo.pw.toml"), "rb") as fh:
        pw_hash = sha(fh.read())
    idx = (
        'hash-format = "sha256"\n\n'
        '[[files]]\nfile = "config/ftbquests/quests/chapters/overworld.snbt"\nhash = "%s"\n\n'
        '[[files]]\nfile = "config/modpack-info.txt"\nhash = "%s"\n\n'
        '[[files]]\nfile = "config/personal.cfg"\nhash = "%s"\npreserve = true\n\n'
        '[[files]]\nfile = "mods/foo.pw.toml"\nhash = "%s"\n'
    ) % (sha(overworld), sha(info), sha(personal), pw_hash)
    w("index.toml", idx.encode())

    pack_toml = (
        'name = "Test Pack"\nauthor = "test"\nversion = "9.9.9"\n'
        'description = "t"\npack-format = "packwiz:1.1.0"\n\n'
        '[index]\nfile = "index.toml"\nhash-format = "sha256"\nhash = "%s"\n\n'
        '[versions]\nminecraft = "1.21.1"\nneoforge = "21.1.252"\n'
    ) % sha(idx.encode("utf-8"))
    w("pack.toml", pack_toml.encode())

    # ---------------- 1. чтение пака ----------------
    print("== load_pack ==")
    model = P.load_pack(base)
    ok(model.integrity == "OK", "integrity index.toml: " + model.integrity)
    ok(len(model.items) == 4, "в модели 4 записи, есть %d" % len(model.items))
    by_rel = {i.dest_rel: i for i in model.items}
    ok("mods/foo.jar" in by_rel, "мод foo.jar разобран из pw.toml")
    ok(by_rel.get("config/personal.cfg").preserve is True, "preserve=true прочитан")

    # ---------------- 2. скан: устаревшее видно как ЛИШНЕЕ ----------------
    print("== scan_local (до чистки) ==")
    rows = P.scan_local(game, model, "client")
    extras = {r.dest_rel.replace(os.sep, "/") for r in rows if r.status == P.EXTRA}
    ok("mods/certain-questing-additions-1.2.0.4.jar" in extras,
       "устаревший CQA-jar виден как ЛИШНИЙ")
    ok("config/ftbquests/quests/chapters/start.snbt" in extras,
       "старая глава start.snbt видна как ЛИШНИЙ (рекурсивный скан)")
    ok("config/ftbquests/quests/data.snbt" in extras,
       "вложенный data.snbt не из индекса виден как ЛИШНИЙ")
    st = {r.dest_rel.replace(os.sep, "/"): r.status for r in rows}
    ok(st.get("mods/foo.jar") == P.MISMATCH, "битый foo.jar — НЕ СОВПАДАЕТ")
    ok(st.get("config/ftbquests/quests/chapters/overworld.snbt") == P.MISMATCH,
       "старый overworld.snbt — НЕ СОВПАДАЕТ")
    ok(st.get("config/personal.cfg") == P.OK, "личный preserve-файл — НА МЕСТЕ")
    ok("saves/My World/level.dat" not in st, "saves/ не сканируется вовсе")

    # ---------------- 3. чистая переустановка ----------------
    print("== clean_reinstall ==")
    logs = []
    res = P.clean_reinstall(game, model, "client", on_log=logs.append)
    ok(res.ok, "чистая переустановка без ошибок: wipe=%s sync_err=%s"
       % (res.wipe.errors, res.sync.errors))
    ok(set(res.wipe.moved_dirs) == {"mods", "config"},
       "унесены в бэкап именно существующие каталоги: %s" % res.wipe.moved_dirs)
    ok(res.wipe.files >= 7, "в бэкапе учтено файлов: %d" % res.wipe.files)

    ok(os.path.isfile(os.path.join(game, "mods", "foo.jar")), "mods/foo.jar скачан заново")
    with open(os.path.join(game, "mods", "foo.jar"), "rb") as fh:
        ok(fh.read() == foojar, "содержимое foo.jar верное")
    ok(not os.path.exists(os.path.join(game, "mods", "certain-questing-additions-1.2.0.4.jar")),
       "СТАРЫЙ CQA-JAR ИСЧЕЗ из mods/")
    ch = os.path.join(game, "config", "ftbquests", "quests", "chapters")
    ok(sorted(os.listdir(ch)) == ["overworld.snbt"],
       "в chapters/ только overworld.snbt: %s" % sorted(os.listdir(ch)))
    with open(os.path.join(ch, "overworld.snbt"), "rb") as fh:
        ok(fh.read() == overworld, "overworld.snbt — свежий с сервера")
    ok(not os.path.exists(os.path.join(game, "config", "ftbquests", "quests", "data.snbt")),
       "старый data.snbt исчез")

    with open(os.path.join(game, "config", "personal.cfg"), "rb") as fh:
        ok(fh.read() == personal, "preserve-файл восстановлен из бэкапа")
    ok(res.preserved == 1, "restore_preserved вернул 1 файл (%d)" % res.preserved)

    for rel, want in (("saves/My World/level.dat", b"WORLD PROGRESS"),
                      ("local/ftbquests/user.snbt", b"QUEST PROGRESS"),
                      ("journeymap/data/point.dat", b"WAYPOINTS"),
                      ("options.txt", b"KEYBINDS"),
                      ("packsync/pack-url.txt", b"http://example.invalid/pack.toml\n"),
                      ("packwiz.json", b'{"files":{}}'),
                      ("logs/latest.log", b"log")):
        p = os.path.join(game, rel.replace("/", os.sep))
        got = open(p, "rb").read() if os.path.isfile(p) else None
        ok(got == want, "не тронут: " + rel)

    bak = res.wipe.backup_dir
    ok(os.path.isdir(bak) and os.path.basename(bak).startswith("clean-"),
       "бэкап-каталог создан: %s" % os.path.basename(bak))
    ok(os.path.isfile(os.path.join(bak, "mods", "certain-questing-additions-1.2.0.4.jar")),
       "старый CQA-jar лежит в бэкапе")
    ok(os.path.isfile(os.path.join(bak, "config", "ftbquests", "quests", "chapters", "start.snbt")),
       "старая глава лежит в бэкапе")

    # ---------------- 4. повторный скан — всё чисто ----------------
    print("== scan_local (после чистки) ==")
    rows2 = P.scan_local(game, model, "client")
    bad = [r for r in rows2 if r.status in P.BAD_STATUSES]
    extras2 = [r for r in rows2 if r.status == P.EXTRA]
    ok(not bad, "проблемных файлов нет: %s" % [(r.dest_rel, r.status) for r in bad])
    ok(not extras2, "лишних файлов нет: %s" % [r.dest_rel for r in extras2])

    httpd.shutdown()
    os.chdir(orig_cwd)
    shutil.rmtree(root, ignore_errors=True)
    print()
    if FAILS:
        print("ПРОВАЛЕНО: %d" % len(FAILS))
        sys.exit(1)
    print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ (%d проверок)" % CHECKS[0])


if __name__ == "__main__":
    main()
