#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modpack Manager — приложение для проверки и починки сборки.

Python 3.8+ и Tkinter (входит в стандартную поставку Python). Никаких
сторонних зависимостей, поэтому собирается в один .exe через PyInstaller.

Запуск:
    python app/modpack_app.py
    python app/modpack_app.py --game-dir "C:\\...\\profiles\\MyPack"
    python app/modpack_app.py --base-url https://user.github.io/repo

Что умеет:
  • выбрать папку сборки вручную или найти её у AstralRinth / Modrinth App /
    Freesm / Prism / MultiMC / .minecraft
  • сверить с сервером ВСЁ содержимое пака по хэшам: mods, config,
    resourcepacks, shaderpacks, defaultconfigs, kubejs
  • починить: докачать отсутствующее и заменить несовпавшее — собственным
    загрузчиком, БЕЗ Java
  • создать инстанс Prism/Freesm прямо на диске — без zip и без диалога импорта
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import re
import subprocess
import sys
import threading
import time
import traceback
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk                                      # noqa: E402
from tkinter import ttk, filedialog, messagebox           # noqa: E402

import packlib as P                                       # noqa: E402

APP_NAME = "Modpack Manager"
APP_VERSION = "3.0.0"
FALLBACK_BASE = "https://yungspiderq.github.io/my-neoforge-pack"

COLORS = {
    P.OK:           "#1a7f1a",
    P.MISSING:      "#c00000",
    P.MISMATCH:     "#c00000",
    P.BROKEN_REMOTE:"#c00000",
    P.DISABLED:     "#b06000",
    P.PRESERVED:    "#707070",
    P.OTHER_SIDE:   "#707070",
    P.EXTRA:        "#8a5a00",
}


def settings_dir() -> str:
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(base, "ModpackManager")
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, "modpack-manager")


class App:
    # ------------------------------------------------------------------ #
    #  Каркас
    # ------------------------------------------------------------------ #

    def __init__(self, root: tk.Tk, args):
        self.root = root
        self.model = None
        self.rows = []
        self._row_by_id = {}
        self.args = args
        self.busy = False
        self.q: "queue.Queue" = queue.Queue()
        self.cfg = self._load_cfg()

        root.title("%s %s" % (APP_NAME, APP_VERSION))
        root.geometry("1180x720")
        root.minsize(880, 520)

        self._build_menu()
        self._build_toolbar()
        self._build_tabs()
        self._build_status()

        root.protocol("WM_DELETE_WINDOW", self._on_close)
        root.after(60, self._drain)
        root.after(120, self._startup)

    # --- настройки ---

    def _cfg_path(self):
        return os.path.join(settings_dir(), "settings.json")

    def _load_cfg(self):
        d = {"game_dir": "", "base_url": "", "side": "client", "recent": []}
        try:
            with open(self._cfg_path(), encoding="utf-8") as fh:
                j = json.load(fh)
            for k in d:
                if k in j and j[k] is not None:
                    d[k] = j[k]
        except Exception:
            pass
        return d

    def _save_cfg(self):
        try:
            os.makedirs(settings_dir(), exist_ok=True)
            self.cfg["game_dir"] = self.game_dir()
            self.cfg["base_url"] = self.base_url()
            with open(self._cfg_path(), "w", encoding="utf-8") as fh:
                json.dump(self.cfg, fh, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # --- меню ---

    def _build_menu(self):
        m = tk.Menu(self.root)
        self.root.config(menu=m)

        f = tk.Menu(m, tearoff=0)
        f.add_command(label="Выбрать папку сборки…", command=self.pick_dir, accelerator="Ctrl+O")
        self.recent_menu = tk.Menu(f, tearoff=0)
        f.add_cascade(label="Недавние", menu=self.recent_menu)
        f.add_separator()
        f.add_command(label="Установить пак с нуля (инстанс Prism/Freesm)…",
                      command=self.install_dialog)
        f.add_separator()
        f.add_command(label="Сохранить отчёт…", command=self.save_report)
        f.add_separator()
        f.add_command(label="Выход", command=self._on_close)
        m.add_cascade(label="Файл", menu=f)

        c = tk.Menu(m, tearoff=0)
        c.add_command(label="Проверить сейчас", command=self.check, accelerator="F5")
        c.add_command(label="Проверить все стороны (both)", command=lambda: self.check(side="both"))
        c.add_separator()
        c.add_command(label="Только отсутствующие и несовпавшие", command=self.filter_bad)
        c.add_command(label="Показать все", command=lambda: self.render(self.rows))
        m.add_cascade(label="Проверка", menu=c)

        s = tk.Menu(m, tearoff=0)
        s.add_command(label="Починить всё (скачать недостающее и несовпавшее)",
                      command=self.fix_all, accelerator="Ctrl+R")
        s.add_command(label="Починить только выбранное", command=self.fix_selected)
        s.add_separator()
        s.add_command(label="Убрать лишние файлы…", command=self.remove_extras)
        s.add_separator()
        s.add_command(label="Включить .disabled у выбранных модов", command=self.disable_selected)
        s.add_command(label="Снять .disabled у выбранных модов", command=self.enable_selected)
        s.add_separator()
        s.add_command(label="Запустить packwiz-installer (через Java)…", command=self.run_legacy)
        m.add_cascade(label="Синхронизация", menu=s)

        t = tk.Menu(m, tearoff=0)
        t.add_command(label="Открыть папку mods/", command=lambda: self.open_sub("mods"))
        t.add_command(label="Открыть папку config/", command=lambda: self.open_sub("config"))
        t.add_command(label="Открыть папку сборки", command=lambda: self.open_sub(""))
        t.add_command(label="Открыть папку бэкапов (.modpack-backup)",
                      command=lambda: self.open_sub(P.BACKUP_DIR))
        t.add_separator()
        t.add_command(label="Открыть packsync/sync.log", command=self.open_synclog)
        self.gui_var = tk.BooleanVar(value=False)
        t.add_checkbutton(label="Показывать окно прогресса при запуске игры (SHOW_GUI)",
                          variable=self.gui_var, command=self.toggle_show_gui)
        m.add_cascade(label="Инструменты", menu=t)

        h = tk.Menu(m, tearoff=0)
        h.add_command(label="Как это работает", command=self.show_help)
        h.add_command(label="Показать адрес пака", command=self.show_urls)
        h.add_command(label="Открыть репозиторий пака", command=self.open_repo)
        h.add_separator()
        h.add_command(label="О программе", command=self.show_about)
        m.add_cascade(label="Справка", menu=h)

        self.root.bind_all("<Control-o>", lambda e: self.pick_dir())
        self.root.bind_all("<F5>", lambda e: self.check())
        self.root.bind_all("<Control-r>", lambda e: self.fix_all())

    # --- тулбар ---

    def _build_toolbar(self):
        top = ttk.Frame(self.root, padding=(8, 6))
        top.pack(side="top", fill="x")

        ttk.Label(top, text="Папка сборки:").grid(row=0, column=0, sticky="w")
        self.dir_var = tk.StringVar()
        self.dir_cb = ttk.Combobox(top, textvariable=self.dir_var, width=74)
        self.dir_cb.grid(row=0, column=1, padx=6, sticky="we")
        ttk.Button(top, text="Обзор…", command=self.pick_dir).grid(row=0, column=2, padx=2)
        self.btn_check = ttk.Button(top, text="Проверить", command=self.check)
        self.btn_check.grid(row=0, column=3, padx=2)
        self.btn_fix = ttk.Button(top, text="Починить всё", command=self.fix_all)
        self.btn_fix.grid(row=0, column=4, padx=2)
        top.columnconfigure(1, weight=1)

        ttk.Label(top, text="Адрес пака:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.base_var = tk.StringVar(value=self.cfg.get("base_url") or "")
        ttk.Entry(top, textvariable=self.base_var).grid(
            row=1, column=1, padx=6, pady=(6, 0), sticky="we")
        ttk.Label(top, text="Сторона:").grid(row=1, column=2, sticky="e", pady=(6, 0))
        self.side_var = tk.StringVar(value=self.cfg.get("side") or "client")
        side = ttk.Combobox(top, textvariable=self.side_var, width=9, state="readonly",
                            values=["client", "server", "both"])
        side.grid(row=1, column=3, padx=2, pady=(6, 0), sticky="w")
        side.bind("<<ComboboxSelected>>", lambda e: self.check(silent=True))

        self.info_var = tk.StringVar(value="Папка не выбрана")
        ttk.Label(self.root, textvariable=self.info_var, padding=(10, 0),
                  foreground="#444444").pack(side="top", fill="x")

    # --- вкладки ---

    def _build_tabs(self):
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(side="top", fill="both", expand=True, padx=8, pady=6)
        self.trees = {}
        for key in ("mods", "files", "extra"):
            fr = ttk.Frame(self.nb)
            self.nb.add(fr, text=key)
            cols = ("name", "dest", "status", "detail")
            tv = ttk.Treeview(fr, columns=cols, show="headings", selectmode="extended")
            for cid, txt, w, anc in (("name", "Название", 290, "w"),
                                     ("dest", "Файл в папке", 320, "w"),
                                     ("status", "Статус", 140, "w"),
                                     ("detail", "Подробности", 340, "w")):
                tv.heading(cid, text=txt)
                tv.column(cid, width=w, anchor=anc, stretch=(cid in ("name", "dest", "detail")))
            vsb = ttk.Scrollbar(fr, orient="vertical", command=tv.yview)
            hsb = ttk.Scrollbar(fr, orient="horizontal", command=tv.xview)
            tv.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            tv.grid(row=0, column=0, sticky="nsew")
            vsb.grid(row=0, column=1, sticky="ns")
            hsb.grid(row=1, column=0, sticky="we")
            fr.rowconfigure(0, weight=1)
            fr.columnconfigure(0, weight=1)
            for st, col in COLORS.items():
                tv.tag_configure(st, foreground=col)
            self.trees[key] = tv

        logfr = ttk.Frame(self.nb)
        self.nb.add(logfr, text="Журнал")
        self.log = tk.Text(logfr, wrap="none", height=8, font=("Consolas", 9),
                           background="#fbfbfb", state="disabled")
        lsb = ttk.Scrollbar(logfr, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=lsb.set)
        self.log.grid(row=0, column=0, sticky="nsew")
        lsb.grid(row=0, column=1, sticky="ns")
        logfr.rowconfigure(0, weight=1)
        logfr.columnconfigure(0, weight=1)
        self.log.tag_configure("error", foreground="#c00000")

        self.nb.tab(0, text="Моды")
        self.nb.tab(1, text="Конфиги и файлы")
        self.nb.tab(2, text="Лишние")
        self.nb.tab(3, text="Журнал")

    def _build_status(self):
        bar = ttk.Frame(self.root, padding=(8, 3))
        bar.pack(side="bottom", fill="x")
        self.status_var = tk.StringVar(value="Готово")
        ttk.Label(bar, textvariable=self.status_var, anchor="w").pack(
            side="left", fill="x", expand=True)
        self.progress = ttk.Progressbar(bar, length=240, mode="determinate", maximum=100)
        self.progress.pack(side="right")

    # ------------------------------------------------------------------ #
    #  Логика вывода
    # ------------------------------------------------------------------ #

    def log_line(self, msg, error=False):
        def do():
            self.log.configure(state="normal")
            self.log.insert("end", msg + "\n", ("error",) if error else ())
            if int(self.log.index("end-1c").split(".")[0]) > 4000:
                self.log.delete("1.0", "500.0")
            self.log.see("end")
            self.log.configure(state="disabled")
        self.q.put(("log", do))

    def set_status(self, text):
        self.q.put(("status", text))

    def set_progress(self, pct, msg=None):
        self.q.put(("progress", (pct, msg)))

    def _drain(self):
        try:
            while True:
                kind, payload = self.q.get_nowait()
                if kind == "log":
                    payload()
                elif kind == "status":
                    self.status_var.set(payload)
                elif kind == "progress":
                    pct, msg = payload
                    if pct is None:
                        self.progress.configure(mode="indeterminate")
                        self.progress.start(12)
                    else:
                        self.progress.stop()
                        self.progress.configure(mode="determinate")
                        self.progress["value"] = max(0, min(100, pct))
                    if msg:
                        self.status_var.set(msg)
                elif kind == "render":
                    self._render(payload)
                elif kind == "guivar":
                    self.gui_var.set(bool(payload))
                elif kind == "info":
                    messagebox.showinfo(APP_NAME, payload)
                elif kind == "recheck":
                    self.busy = False
                    self._set_buttons(True)
                    self.check(silent=True)
                elif kind == "reloaddirs":
                    self._reload_dirs()
                elif kind == "done":
                    self.busy = False
                    self._set_buttons(True)
                elif kind == "error":
                    self.busy = False
                    self._set_buttons(True)
                    messagebox.showerror(APP_NAME, payload)
        except queue.Empty:
            pass
        self.root.after(60, self._drain)

    def _set_buttons(self, on):
        state = "normal" if on else "disabled"
        for b in (self.btn_check, self.btn_fix):
            b.configure(state=state)

    def render(self, rows):
        self.q.put(("render", rows))

    def _render(self, rows):
        for tv in self.trees.values():
            tv.delete(*tv.get_children())
        counts = {}
        for r in rows:
            key = {"Моды": "mods", "Лишние": "extra"}.get(r.category, "files")
            tv = self.trees[key]
            tv.insert("", "end", values=(r.name, r.dest_rel, r.status, r.detail),
                      tags=(r.status,), iid=str(id(r)))
            counts[r.status] = counts.get(r.status, 0) + 1
        self._row_by_id = {str(id(r)): r for r in rows}
        self.nb.tab(0, text="Моды (%d)" % len(self.trees["mods"].get_children()))
        self.nb.tab(1, text="Конфиги и файлы (%d)" % len(self.trees["files"].get_children()))
        self.nb.tab(2, text="Лишние (%d)" % len(self.trees["extra"].get_children()))

        bad = sum(counts.get(s, 0) for s in P.BAD_STATUSES)
        good = counts.get(P.OK, 0)
        if bad:
            self.status_var.set("Требуется починка: %d не в порядке, %d на месте" % (bad, good))
        elif good:
            self.status_var.set("Всё в порядке: %d файлов на месте, хэши сходятся" % good)
        else:
            self.status_var.set("Нет данных")

    def filter_bad(self):
        self.render([r for r in self.rows if r.status in P.BAD_STATUSES or r.removable])

    # ------------------------------------------------------------------ #
    #  Доступы
    # ------------------------------------------------------------------ #

    def game_dir(self) -> str:
        t = self.dir_var.get().strip()
        if "|" in t:
            t = t.split("|", 1)[1].strip()
        return t

    def base_url(self) -> str:
        u = self.base_var.get().strip().rstrip("/")
        u = re.sub(r"/pack\.toml$", "", u) if u else ""
        return u

    # ------------------------------------------------------------------ #
    #  Действия
    # ------------------------------------------------------------------ #

    def _startup(self):
        self._reload_dirs()
        d = self.args.game_dir or self.cfg.get("game_dir") or ""
        if d and os.path.isdir(d):
            self.dir_var.set("(выбрана)  |  " + d)
        elif self.dir_cb["values"]:
            self.dir_cb.current(0)
        b = self.args.base_url or self.cfg.get("base_url") or ""
        if b:
            self.base_var.set(b)
        self._build_recent()
        if self.game_dir():
            self.log_line("папка сборки: " + self.game_dir())
            self.check(silent=True)
        else:
            self.log_line("лаунчеры не найдены — укажите папку сборки кнопкой «Обзор…»")
            self.log_line("обычно это:")
            self.log_line("  AstralRinth  : %APPDATA%\\AstralRinthApp\\profiles\\<имя>")
            self.log_line("  Modrinth App : %APPDATA%\\ModrinthApp\\profiles\\<имя>")
            self.log_line("  Freesm/Prism : %APPDATA%\\FreesmLauncher\\instances\\<имя>\\.minecraft")

    def _reload_dirs(self):
        found = P.detect_game_dirs()
        vals = ["%s  |  %s" % (d.label, d.path) for d in found]
        cur = self.dir_var.get()
        self.dir_cb["values"] = vals
        if cur and cur not in vals:
            self.dir_cb["values"] = vals + [cur]
        self.log_line("найдено папок игры: %d" % len(found))

    def _build_recent(self):
        self.recent_menu.delete(0, "end")
        rec = self.cfg.get("recent") or []
        if not rec:
            self.recent_menu.add_command(label="(пусто)", state="disabled")
            return
        for p in rec[:8]:
            self.recent_menu.add_command(
                label=p, command=lambda v=p: self._use_dir(v))

    def _use_dir(self, path):
        self.dir_var.set("(вручную)  |  " + path)
        self.check()

    def _remember(self, path):
        rec = [r for r in (self.cfg.get("recent") or []) if r != path]
        rec.insert(0, path)
        self.cfg["recent"] = rec[:8]
        self._build_recent()

    def pick_dir(self):
        d = filedialog.askdirectory(title="Папка сборки (профиль лаунчера или .minecraft)",
                                    initialdir=self.game_dir() or os.path.expanduser("~"))
        if d:
            self.dir_var.set("(вручную)  |  " + os.path.normpath(d))
            self.check()

    def check(self, silent=False, side=None):
        if self.busy:
            return
        gd = self.game_dir()
        if not gd:
            if not silent:
                messagebox.showinfo(APP_NAME, "Сначала выберите папку сборки.")
            return
        if not os.path.isdir(gd):
            self.status_var.set("Папка не существует")
            self.log_line("папка не существует: " + gd, error=True)
            return
        base = self.base_url() or P.read_pack_url(gd) or FALLBACK_BASE
        self.base_var.set(base)
        sd = side or self.side_var.get() or "client"
        self.busy = True
        self._set_buttons(False)
        threading.Thread(target=self._check_worker, args=(gd, base, sd), daemon=True).start()

    def _check_worker(self, gd, base, side):
        try:
            self.set_progress(None, "Читаю пак с сервера…")
            self.model = P.load_pack(base, progress=self.set_progress)
            self.log_line("пак: " + self.model.summary)
            if self.model.integrity == "РАССИНХРОН":
                self.log_line("ВНИМАНИЕ: sha256 index.toml не совпадает с pack.toml — "
                              "пак на сервере рассинхронизирован", error=True)
            self.set_progress(None, "Сверяю с диском…")
            self.rows = P.scan_local(gd, self.model, side, progress=self.set_progress)
            self.q.put(("render", self.rows))
            self.info_var.set(self.model.summary)
            self._remember(gd)
            self._save_cfg()

            pwj = os.path.join(gd, "packwiz.json")
            if os.path.isfile(pwj):
                age = (time.time() - os.path.getmtime(pwj)) / 60
                self.log_line("packwiz.json есть, обновлён %.0f мин назад — "
                              "packwiz-installer отрабатывал" % age)
            else:
                self.log_line("packwiz.json НЕТ — packwiz-installer ни разу не отработал "
                              "(hook не прописан?)", error=True)
            sl = os.path.join(gd, "packsync", "sync.log")
            if os.path.isfile(sl):
                self.log_line("packsync/sync.log: изменён %s" % time.ctime(os.path.getmtime(sl)))
            else:
                self.log_line("packsync/sync.log нет — hook, скорее всего, не запускался")
            f = os.path.join(gd, "packsync", "SHOW_GUI")
            self.q.put(("guivar", os.path.isfile(f)))
            self.set_progress(100, None)
        except Exception as e:                              # noqa: BLE001
            self.log_line("ОШИБКА: %s" % e, error=True)
            self.log_line(traceback.format_exc(limit=3), error=True)
            self.q.put(("error", str(e)))
        finally:
            self.q.put(("done", None))

    def _selected_rows(self):
        out = []
        for tv in self.trees.values():
            for iid in tv.selection():
                r = self._row_by_id.get(iid)
                if r:
                    out.append(r)
        return out

    def fix_all(self):
        self._fix(self.rows)

    def fix_selected(self):
        rows = self._selected_rows()
        if not rows:
            messagebox.showinfo(APP_NAME, "Выделите строки в таблице.")
            return
        self._fix(rows)

    def _fix(self, rows):
        if self.busy:
            return
        todo = [r for r in rows if r.actionable]
        if not todo:
            messagebox.showinfo(APP_NAME, "Чинить нечего: все файлы на месте и хэши сходятся.")
            return
        gd = self.game_dir()
        total = sum(P.http_size(r.item.url) or 0 for r in todo[:50])
        msg = "Будет скачано/заменено файлов: %d\n\nПапка: %s\nИсточник: %s" % (
            len(todo), gd, self.model.base_url if self.model else self.base_url())
        if total:
            msg += "\nПримерный объём: %.1f МБ" % (total / 1048576)
        msg += "\n\nЗаменяемые файлы будут скопированы в %s\n\nПродолжить?" % P.BACKUP_DIR
        if not messagebox.askyesno(APP_NAME, msg):
            return
        self.busy = True
        self._set_buttons(False)
        threading.Thread(target=self._fix_worker, args=(gd, todo), daemon=True).start()

    def _fix_worker(self, gd, todo):
        try:
            res = P.sync_rows(gd, todo, progress=self.set_progress,
                              on_log=lambda s: self.log_line(s))
            self.log_line("итог: %d скачано, %d заменено, %d ошибок, %.1f МБ"
                          % (res.downloaded, res.replaced, res.failed, res.bytes / 1048576))
            if res.failed:
                self.q.put(("error", "Скачано: %d\nС ошибками: %d\n\nПодробности во вкладке «Журнал»."
                            % (res.downloaded + res.replaced, res.failed)))
            self.q.put(("recheck", None))
        except Exception as e:                              # noqa: BLE001
            self.log_line("ОШИБКА: %s" % e, error=True)
            self.q.put(("error", str(e)))
        finally:
            self.q.put(("done", None))

    def remove_extras(self):
        if self.busy:
            return
        rows = [r for r in self.rows if r.removable]
        if not rows:
            messagebox.showinfo(APP_NAME, "Лишних файлов нет.")
            return
        names = "\n".join(r.dest_rel for r in rows[:20])
        more = "\n…и ещё %d" % (len(rows) - 20) if len(rows) > 20 else ""
        if not messagebox.askyesno(
                APP_NAME, "Удалить файлов, которых нет в паке: %d?\n\n%s%s\n\n"
                          "Файлы будут перемещены в %s, а не удалены навсегда."
                % (len(rows), names, more, P.BACKUP_DIR)):
            return
        moved = P.remove_extras(self.game_dir(), rows, on_log=lambda s: self.log_line(s))
        self.log_line("перенесено в бэкап: %d" % moved)
        self.check(silent=True)

    def _toggle_disabled(self, on):
        rows = self._selected_rows()
        if not rows:
            messagebox.showinfo(APP_NAME, "Выделите строки в таблице.")
            return
        n = 0
        for r in rows:
            if r.item is None or r.item.kind != "mod":
                continue
            base = r.path[:-len(".disabled")] if r.path.endswith(".disabled") else r.path
            try:
                if on and os.path.isfile(base):
                    os.rename(base, base + ".disabled")
                    self.log_line("отключён: " + r.dest_rel)
                    n += 1
                elif not on and os.path.isfile(base + ".disabled"):
                    os.rename(base + ".disabled", base)
                    self.log_line("включён: " + r.dest_rel)
                    n += 1
            except OSError as e:
                self.log_line("не удалось %s: %s" % (r.dest_rel, e), error=True)
        self.log_line("%s модов: %d" % ("отключено" if on else "включено", n))
        self.check(silent=True)

    def disable_selected(self):
        self._toggle_disabled(True)

    def enable_selected(self):
        self._toggle_disabled(False)

    def run_legacy(self):
        gd = self.game_dir()
        if not gd:
            return
        cmd = os.path.join(gd, "packsync", "sync.cmd" if os.name == "nt" else "sync.sh")
        if not os.path.isfile(cmd):
            messagebox.showwarning(APP_NAME, "Нет %s\nЗначит packsync не установлен в эту папку." % cmd)
            return
        self.log_line("запускаю " + cmd + " (нужна Java)")
        try:
            if os.name == "nt":
                out = subprocess.run(["cmd.exe", "/c", cmd], capture_output=True,
                                     text=True, cwd=gd, timeout=1800)
            else:
                out = subprocess.run(["sh", cmd], capture_output=True, text=True,
                                     cwd=gd, timeout=1800)
            self.log_line((out.stdout or "") + (out.stderr or ""))
            self.log_line("код возврата: %s" % out.returncode)
        except Exception as e:                              # noqa: BLE001
            self.log_line("ОШИБКА: %s" % e, error=True)
        self.check(silent=True)

    def toggle_show_gui(self):
        gd = self.game_dir()
        if not gd:
            self.gui_var.set(False)
            messagebox.showinfo(APP_NAME, "Сначала выберите папку сборки.")
            return
        f = os.path.join(gd, "packsync", "SHOW_GUI")
        try:
            os.makedirs(os.path.dirname(f), exist_ok=True)
            if self.gui_var.get():
                open(f, "w").close()
                self.log_line("SHOW_GUI создан — при запуске игры откроется окно "
                              "packwiz-installer с прогрессом")
            elif os.path.isfile(f):
                os.remove(f)
                self.log_line("SHOW_GUI удалён — синхронизация при запуске снова тихая")
        except OSError as e:
            self.log_line("ОШИБКА: %s" % e, error=True)

    def open_sub(self, sub):
        gd = self.game_dir()
        if not gd:
            return
        p = os.path.join(gd, sub) if sub else gd
        if not os.path.isdir(p):
            messagebox.showwarning(APP_NAME, "Нет такого пути:\n" + p)
            return
        try:
            if sys.platform == "win32":
                os.startfile(p)                             # noqa: S606
            elif sys.platform == "darwin":
                subprocess.Popen(["open", p])
            else:
                subprocess.Popen(["xdg-open", p])
        except Exception as e:                              # noqa: BLE001
            self.log_line("не удалось открыть: %s" % e, error=True)

    def open_synclog(self):
        p = os.path.join(self.game_dir(), "packsync", "sync.log")
        if not os.path.isfile(p):
            messagebox.showinfo(APP_NAME, "sync.log ещё нет:\n" + p)
            return
        try:
            if sys.platform == "win32":
                os.startfile(p)                             # noqa: S606
            elif sys.platform == "darwin":
                subprocess.Popen(["open", p])
            else:
                subprocess.Popen(["xdg-open", p])
        except Exception:
            with open(p, encoding="utf-8", errors="replace") as fh:
                self.log.configure(state="normal")
                self.log.insert("end", fh.read())
                self.log.configure(state="disabled")
            self.nb.select(3)

    # --- установка с нуля ---

    def install_dialog(self):
        dirs = P.prism_instances_dirs()
        if not dirs:
            messagebox.showwarning(
                APP_NAME,
                "Не нашёл ни Freesm Launcher, ни Prism Launcher, ни MultiMC.\n\n"
                "Создание инстанса на диске работает только для Prism-семейства.\n"
                "Для AstralRinth используйте импорт .mrpack (см. INSTALL.md).")
            return
        win = tk.Toplevel(self.root)
        win.title("Установить пак с нуля")
        win.geometry("720x300")
        win.transient(self.root)
        fr = ttk.Frame(win, padding=12)
        fr.pack(fill="both", expand=True)

        ttk.Label(fr, text="Лаунчер:").grid(row=0, column=0, sticky="w", pady=3)
        lvar = tk.StringVar()
        lcb = ttk.Combobox(fr, textvariable=lvar, state="readonly", width=60,
                           values=["%s  |  %s" % (l, b) for l, b in dirs])
        lcb.grid(row=0, column=1, sticky="we", pady=3)
        lcb.current(0)

        ttk.Label(fr, text="Имя инстанса:").grid(row=1, column=0, sticky="w", pady=3)
        nvar = tk.StringVar(value=(self.model.name if self.model else "My NeoForge Pack"))
        ttk.Entry(fr, textvariable=nvar).grid(row=1, column=1, sticky="we", pady=3)

        ttk.Label(fr, text="Адрес пака:").grid(row=2, column=0, sticky="w", pady=3)
        bvar = tk.StringVar(value=self.base_url() or FALLBACK_BASE)
        ttk.Entry(fr, textvariable=bvar).grid(row=2, column=1, sticky="we", pady=3)

        txt = tk.Text(fr, height=7, font=("Consolas", 9), background="#fbfbfb")
        txt.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=8)
        txt.insert("end",
                   "Будет создан инстанс прямо на диске — zip и диалог импорта не нужны.\n"
                   "Лаунчер подхватит его сам при следующем запуске.\n\n"
                   "Создаётся:\n"
                   "  <instances>/<имя>/instance.cfg        с Pre-Launch Command\n"
                   "  <instances>/<имя>/mmc-pack.json       Minecraft + загрузчик\n"
                   "  <instances>/<имя>/.minecraft/packsync/  синхронизатор\n\n"
                   "Моды докачаются при первом запуске игры.")
        txt.configure(state="disabled")
        fr.rowconfigure(3, weight=1)
        fr.columnconfigure(1, weight=1)

        def do():
            if self.busy:
                return
            sel = lcb.get()
            inst_dir = sel.split("|", 1)[1].strip()
            base = bvar.get().strip().rstrip("/")
            self.busy = True
            self._set_buttons(False)
            win.destroy()

            def work():
                try:
                    mdl = self.model or P.load_pack(base, progress=self.set_progress)
                    path = P.install_prism_instance(
                        inst_dir, nvar.get().strip() or "Modpack", base,
                        mdl.mc, mdl.loader, mdl.loader_version,
                        progress=self.set_progress, on_log=lambda s: self.log_line(s))
                    self.log_line("инстанс создан: " + path)
                    self.q.put(("reloaddirs", None))
                    self.q.put(("info", "Инстанс создан:\n%s\n\nПерезапустите лаунчер — "
                                        "он появится в списке.\nПри первом запуске "
                                        "игры моды скачаются сами." % path))
                except Exception as e:                      # noqa: BLE001
                    self.log_line("ОШИБКА: %s" % e, error=True)
                    self.q.put(("error", str(e)))
                finally:
                    self.q.put(("done", None))
            threading.Thread(target=work, daemon=True).start()

        bb = ttk.Frame(fr)
        bb.grid(row=4, column=0, columnspan=2, sticky="e")
        ttk.Button(bb, text="Создать инстанс", command=do).pack(side="left", padx=4)
        ttk.Button(bb, text="Отмена", command=win.destroy).pack(side="left", padx=4)

    # --- справка и отчёты ---

    def save_report(self):
        if not self.rows:
            messagebox.showinfo(APP_NAME, "Сначала выполните проверку.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile="modpack-report.txt",
            filetypes=[("Текст", "*.txt"), ("CSV", "*.csv")])
        if not path:
            return
        csv = path.lower().endswith(".csv")
        lines = []
        if csv:
            lines.append("Категория;Название;Файл;Статус;Подробности")
            for r in self.rows:
                lines.append('"%s";"%s";"%s";"%s";"%s"'
                             % (r.category, r.name, r.dest_rel, r.status, r.detail))
        else:
            lines.append("%s %s — %s" % (APP_NAME, APP_VERSION, time.strftime("%Y-%m-%d %H:%M:%S")))
            lines.append("Папка : " + self.game_dir())
            lines.append("Адрес : " + (self.model.base_url if self.model else self.base_url()))
            if self.model:
                lines.append("Пак   : " + self.model.summary)
            lines.append("")
            for r in self.rows:
                lines.append("[%-10s] %-16s %-34s -> %-42s %s"
                             % (r.category, r.status, r.name[:34], r.dest_rel[:42], r.detail))
            lines.append("")
            lines.append("--- журнал ---")
            self.log.configure(state="normal")
            lines.append(self.log.get("1.0", "end-1c"))
            self.log.configure(state="disabled")
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("\n".join(lines))
            self.log_line("отчёт сохранён: " + path)
        except OSError as e:
            messagebox.showerror(APP_NAME, str(e))

    def show_help(self):
        messagebox.showinfo(APP_NAME + " — как это работает", HELP_TEXT)

    def show_urls(self):
        b = (self.model.base_url if self.model else self.base_url()) or FALLBACK_BASE
        messagebox.showinfo(APP_NAME, (
            "Адрес пака:\n%s/pack.toml\n\nИндекс:\n%s/index.toml\n\n"
            "Установщик:\n%s/install.ps1\n\nАртефакты:\n%s/latest/pack.mrpack\n"
            "%s/latest/instance.zip" % (b, b, b, b, b)))

    def open_repo(self):
        b = (self.model.base_url if self.model else self.base_url()) or FALLBACK_BASE
        m = re.match(r"https://([^.]+)\.github\.io/([^/]+)", b)
        webbrowser.open("https://github.com/%s/%s" % (m.group(1), m.group(2)) if m else b)

    def show_about(self):
        messagebox.showinfo(APP_NAME, (
            "%s %s\n\nОбслуживание модпака на packwiz: проверка и починка\n"
            "без запуска игры и без Java.\n\nPython %s\nНастройки: %s"
            % (APP_NAME, APP_VERSION, sys.version.split()[0], self._cfg_path())))

    def _on_close(self):
        self._save_cfg()
        self.root.destroy()


HELP_TEXT = """\
Приложение сравнивает содержимое папки сборки с тем, что опубликовано на сервере.

Цепочка ровно та же, что у packwiz-installer при запуске игры:
  1. pack.toml        — имя пака, версия Minecraft и загрузчика, sha256 индекса
  2. index.toml       — список всех файлов пака с хэшами
  3. mods/*.pw.toml   — для каждого мода: URL на Modrinth и sha1 файла
  4. каждый файл      — сравнивается с диском ПО ХЭШУ

Починка качает файлы напрямую (urllib), поэтому Java не нужна.
Скачивание идёт во временный файл, хэш проверяется ДО подмены, а заменяемый
файл копируется в .modpack-backup.

Статусы:
  НА МЕСТЕ        файл есть и хэш совпал
  ОТСУТСТВУЕТ     файла нет — будет скачан
  НЕ СОВПАДАЕТ    файл есть, но хэш другой (битый или старый) — будет заменён
  ОТКЛЮЧЁН        лежит как <имя>.disabled; синхронизатор его не трогает
  НЕТ (preserve)  в index.toml стоит preserve=true — файл намеренно не
                  перезаписывается, чтобы не затирать личные настройки
  ДРУГАЯ СТОРОНА  мод только серверный, а выбрана сторона client (или наоборот)
  ЛИШНИЙ          файл в mods/config/…, которого нет в паке

«Установить пак с нуля» создаёт инстанс Prism/Freesm прямо на диске:
instance.cfg с Pre-Launch Command, mmc-pack.json с Minecraft и загрузчиком,
и папку .minecraft/packsync. Диалог импорта и zip-файл при этом не нужны.
"""


def main():
    ap = argparse.ArgumentParser(prog="modpack_app.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game-dir", default="", help="папка сборки")
    ap.add_argument("--base-url", default="", help="адрес пака (без /pack.toml)")
    args = ap.parse_args()

    root = tk.Tk()
    try:
        style = ttk.Style(root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Treeview", rowheight=22)
    except Exception:
        pass
    App(root, args)
    root.mainloop()


if __name__ == "__main__":
    main()
