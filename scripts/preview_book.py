#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preview_book.py — карта глав квестовой книги в SVG, БЕЗ запуска Minecraft.

Зачем: книга FTB Quests — это холст с иконками, и «как это будет выглядеть»
дешевле увидеть на схеме, чем запускать игру. Схема рисуется из тех же
данных, из которых gen_quests.py собирает SNBT: позиции квестов, секции,
подложки, ореолы, баннеры и стрелки зависимостей.

В SVG текст остаётся текстом (кириллица отрисуется шрифтом системы),
а баннеры глав вставляются как base64-PNG — те самые файлы, которые
положит в пак gen_textures.py.

Запуск:  python scripts/preview_book.py [--out КАТАЛОГ]
Результат: preview_book/<файл_главы>.svg
"""

from __future__ import annotations

import argparse
import base64
import html
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scripts", "quests"))

S = 46.0                 # пикселей на одну единицу сетки квестов
PAD = 70.0               # отступ холста
NODE_R = 15.0

FONT = "system-ui, 'Segoe UI', 'DejaVu Sans', sans-serif"


def esc(t):
    return html.escape(str(t), quote=True)


def rgb(n):
    return "#%06X" % (int(n) & 0xFFFFFF)


def load():
    spec = importlib.util.spec_from_file_location(
        "gen_quests", os.path.join(ROOT, "scripts", "gen_quests.py"))
    gq = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gq)
    import questline as Q
    return gq, Q


def render(gq, Q, ch, translations, out_dir):
    nbt = MAIN_NBT[ch["filename"]]
    pairs = list(zip(ch["quests"], nbt["quests"]))
    n = len(pairs)
    pts = [(float(qn["x"]), float(qn["y"])) for _qa, qn in pairs]
    minx = min(p[0] for p in pts)
    miny = min(p[1] for p in pts)
    maxx = max(p[0] for p in pts)
    maxy = max(p[1] for p in pts)
    # сверху оставляем место под баннер главы и заголовки секций
    topy = miny - 6.6

    def X(x):
        return PAD + (x - minx) * S

    def Y(y):
        return PAD + (y - topy) * S

    W = int(PAD * 2 + (maxx - minx) * S + 40)
    H = int(PAD * 2 + (maxy - topy) * S + 40)

    ru = translations["ru_ru"]
    en = translations["en_us"]

    def title_of(obj, oid, default=""):
        return ru.get("%s.%s.title" % (obj, oid),
                      en.get("%s.%s.title" % (obj, oid), default))

    parts = []
    parts.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
                 'viewBox="0 0 %d %d" font-family="%s">'
                 % (W, H, W, H, FONT))
    parts.append('<rect width="%d" height="%d" fill="#141419"/>' % (W, H))

    # --- подложки и заголовки секций ---
    boxes = {}
    for sec in ch.get("sections", []):
        mem = [(X(p[0]), Y(p[1])) for (qa, _qn), p in zip(pairs, pts)
               if qa.get("section") == sec["key"]]
        if not mem:
            continue
        pad = 1.05 * S
        x0 = min(m[0] for m in mem) - pad - NODE_R
        x1 = max(m[0] for m in mem) + pad + NODE_R
        y0 = min(m[1] for m in mem) - pad - NODE_R
        y1 = max(m[1] for m in mem) + pad + NODE_R
        boxes[sec["key"]] = (x0, y0, x1, y1)
        col = rgb(sec.get("color", 0x3E7A3A))
        parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="22" '
                     'fill="%s" fill-opacity="0.16" stroke="%s" '
                     'stroke-opacity="0.35"/>'
                     % (x0, y0, x1 - x0, y1 - y0, col, col))
        t = title_of("image", sec_image_id(ch, sec, gq), sec["title"][1])
        parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="30" rx="8" '
                     'fill="%s" fill-opacity="0.92"/>'
                     % (x0 + 10, y0 - 22, min(max(x1 - x0 - 20, 150), 420), col))
        parts.append('<text x="%.1f" y="%.1f" fill="#fff" font-size="17" '
                     'font-weight="600">%s</text>'
                     % (x0 + 22, y0 - 1, esc(t)))

    # --- картинки главы: баннер, ореолы, плашки, порталы ---
    for img in ch_nbt_images(ch, gq, Q):
        ix, iy = X(img["x"]), Y(img["y"])
        iw, ih = img["width"] * S, img["height"] * S
        path = img["image"]
        if path.endswith("panel_soft.png"):
            continue                      # подложки секций уже нарисованы
        if path.endswith("halo.png"):
            parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" '
                         'stroke="%s" stroke-opacity="0.75" stroke-width="3"/>'
                         % (ix, iy, iw / 2, rgb(img.get("color", 0xFFFFFF))))
        elif path.endswith("plate.png"):
            t = title_of("image", img["id"], "")
            parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                         'rx="7" fill="%s" fill-opacity="0.95"/>'
                         % (ix - iw / 2, iy - ih / 2, iw, ih,
                            rgb(img.get("color", 0x202028))))
            if t:
                parts.append('<text x="%.1f" y="%.1f" fill="#fff" font-size="13" '
                             'text-anchor="middle">%s</text>'
                             % (ix, iy + 4, esc(t)))
        elif "portal" in path:
            parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                         'rx="6" fill="#5A2A8A" stroke="#C9A0FF"/>'
                         % (ix - iw / 2, iy - ih / 2, iw, ih))
            parts.append('<text x="%.1f" y="%.1f" fill="#fff" font-size="12" '
                         'text-anchor="middle">⇄</text>' % (ix, iy + 4))
        elif "banner" in path:
            fp = os.path.join(ROOT, "kubejs", "assets", "kubejs",
                              path.split(":", 1)[1])
            if os.path.isfile(fp):
                b64 = base64.b64encode(open(fp, "rb").read()).decode()
                parts.append('<image x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                             'href="data:image/png;base64,%s"/>'
                             % (ix - iw / 2, iy - ih / 2, iw, ih, b64))

    # --- стрелки зависимостей ---
    by_id = {qn["id"]: (X(p[0]), Y(p[1])) for (_qa, qn), p in zip(pairs, pts)}
    for _qa, qn in pairs:
        for d in qn.get("dependencies", []):
            if d in by_id:
                x0, y0 = by_id[d]
                x1, y1 = by_id[qn["id"]]
                parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                             'stroke="#8a8aa0" stroke-width="1.6" '
                             'marker-end="url(#arr)"/>' % (x0, y0, x1, y1))
    parts.append('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
                 'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
                 '<path d="M 0 0 L 10 5 L 0 10 z" fill="#8a8aa0"/></marker></defs>')

    # --- квесты ---
    sec_color = {s["key"]: s.get("color", 0x3E7A3A)
                 for s in ch.get("sections", [])}
    for qa, qn in pairs:
        x, y = by_id[qn["id"]]
        size = float(qa.get("size", 1.0))
        r = NODE_R * (0.8 + 0.45 * size)
        col = rgb(sec_color.get(qa.get("section"), 0x3E7A3A))
        shape = qa.get("shape", ch.get("shape", "circle"))
        if shape in ("gear", "hexagon", "octagon", "pentagon"):
            parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                         'rx="6" transform="rotate(45 %.1f %.1f)" fill="%s" '
                         'stroke="#fff" stroke-opacity="0.75" stroke-width="2"/>'
                         % (x - r, y - r, r * 2, r * 2, x, y, col))
        else:
            parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" '
                         'stroke="#fff" stroke-opacity="0.75" stroke-width="2"/>'
                         % (x, y, r, col))
        if qa.get("optional"):
            parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" '
                         'stroke="#ffd75e" stroke-dasharray="4 3"/>'
                         % (x, y, r + 4))
        t = title_of("quest", qn["id"], qa["key"])
        parts.append('<text x="%.1f" y="%.1f" fill="#e8e8f0" font-size="11" '
                     'text-anchor="middle">%s</text>'
                     % (x, y + r + 14, esc(t)))

    parts.append('<text x="14" y="26" fill="#cfcfe0" font-size="20" '
                 'font-weight="700">%s — %s</text>'
                 % (esc(ch["filename"]),
                    esc(title_of("chapter", ch_id_of(ch, gq, Q), ch["title"][1]))))
    parts.append('<text x="14" y="%d" fill="#8f8fa5" font-size="12">квестов: %d '
                 '· схема из scripts/quests/chapters/%s.py · стрелка = '
                 '«открывает»</text>' % (H - 14, n, ch["filename"]))
    parts.append('</svg>')

    os.makedirs(out_dir, exist_ok=True)
    fp = os.path.join(out_dir, ch["filename"] + ".svg")
    with open(fp, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    return fp, W, H


def ch_id_of(ch, gq, Q):
    ci = [i for i, c in enumerate(Q.QUESTLINE, 1) if c is ch][0]
    return gq.code_string(ch["id"])


def sec_image_id(ch, sec, gq):
    """ID картинки-заголовка секции: баннер(1?) … считаем так же, как генератор:
    картинки нумеруются по порядку объявления в списке images главы, а секции
    идут первыми (подложка, заголовок) — заголовок = 2*номер_секции."""
    idx = [i for i, s in enumerate(ch.get("sections", []), 1)
           if s["key"] == sec["key"]][0]
    ci = ch["id"] - 0xC000
    return gq.code_string(gq.image_id_of(ci, idx * 2))


def ch_nbt_images(ch, gq, Q):
    """Картинки главы из уже собранного NBT (генератор вызывается в main)."""
    return MAIN_NBT[ch["filename"]]["images"]


MAIN_NBT = {}
MAIN_TR = {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(
        os.path.dirname(ROOT), "preview_book"))
    args = ap.parse_args()

    gq, Q = load()
    chapters, _data, translations, _used = gq.build(
        Q.QUESTLINE, Q.FILE_VERSION, Q.FILE_SETTINGS)
    for ch, ch_id, nbt, _cqs in chapters:
        MAIN_NBT[ch["filename"]] = nbt
    MAIN_TR.update(translations)

    made = []
    for ch, ch_id, nbt, _cqs in chapters:
        fp, w, h = render(gq, Q, ch, translations, args.out)
        made.append((fp, w, h))
    for fp, w, h in made:
        print("  %-46s %5dx%d" % (os.path.relpath(fp, ROOT), w, h))
    print("карт глав: %d -> %s" % (len(made), args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
