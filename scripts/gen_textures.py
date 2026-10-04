#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_textures.py — рисует текстуры для кастомных предметов KubeJS и баннеры глав.

Текстуры рисуются программно (Pillow), а не скачиваются: они детерминированы,
весят байты и их можно перегенерировать в CI. Пиксель-арт 16x16 для предметов,
баннеры глав — 256x64.

Куда кладутся:
  kubejs/assets/kubejs/textures/item/<имя>.png   — предметы KubeJS
  kubejs/assets/kubejs/textures/gui/<имя>.png    — баннеры глав FTB Quests
                                                   (в главе: image: "kubejs:textures/gui/<имя>.png")

Запуск:  python scripts/gen_textures.py [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys

try:
    from PIL import Image
except ImportError:
    print("нужен Pillow:  pip install Pillow", file=sys.stderr)
    raise SystemExit(2)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEM_DIR = os.path.join(ROOT, "kubejs", "assets", "kubejs", "textures", "item")
GUI_DIR = os.path.join(ROOT, "kubejs", "assets", "kubejs", "textures", "gui")

T = None            # полностью прозрачный


def px(img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), c)


def rect(img, x0, y0, w, h, c):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            px(img, x, y, c)


def circle(img, cx, cy, r, c, fill=True):
    for y in range(img.height):
        for x in range(img.width):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if fill and d2 <= r * r:
                px(img, x, y, c)
            elif not fill and abs((d2 ** 0.5) - r) < 0.75:
                px(img, x, y, c)


def star(img, cx, cy, r, c):
    """Пятиконечная звезда попиксельно."""
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    def inside(x, y):
        n = len(pts); s = 0
        for i in range(n):
            x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % n]
            if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
                s += 1
        return s % 2 == 1
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            if inside(x + 0.5, y + 0.5):
                px(img, x, y, c)


# --------------------------------------------------------------------------- #
#  Предметы (16x16)
# --------------------------------------------------------------------------- #

def tex_quest_token():
    """Золотая медаль: диск с тёмным ободком и звездой."""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    circle(img, 7.5, 7.5, 6.4, (120, 78, 12, 255))       # тёмный ободок
    circle(img, 7.5, 7.5, 5.2, (250, 200, 60, 255))       # золото
    circle(img, 6.0, 6.0, 2.0, (255, 236, 150, 255))      # блик
    star(img, 8, 8, 3.0, (150, 92, 10, 255))              # звезда-гравировка
    # ушко для ленты
    rect(img, 7, 0, 2, 2, (120, 78, 12, 255))
    return img


def tex_quest_token_premium():
    """Незеритовая медаль: тёмный диск, фиолетовый ободок, яркая звезда."""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    circle(img, 7.5, 7.5, 6.6, (86, 44, 130, 255))        # фиолетовый ободок
    circle(img, 7.5, 7.5, 5.3, (58, 52, 60, 255))         # незерит
    circle(img, 7.5, 7.5, 4.2, (72, 65, 74, 255))         # грань
    circle(img, 5.8, 5.6, 1.6, (150, 110, 200, 255))      # блик
    star(img, 8, 8, 3.2, (226, 170, 255, 255))            # звезда
    rect(img, 7, 0, 2, 2, (86, 44, 130, 255))
    return img


def tex_quest_medal():
    """Финальная медаль: звезда на двух лентах."""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    # ленты
    for i in range(7):
        px(img, 4 + i // 2, i, (176, 28, 40, 255))
        px(img, 11 - i // 2, i, (28, 60, 176, 255))
    circle(img, 7.5, 10.0, 5.4, (120, 88, 20, 255))       # ободок
    circle(img, 7.5, 10.0, 4.4, (255, 214, 80, 255))      # золото
    star(img, 8, 10, 3.4, (255, 252, 230, 255))           # звезда
    circle(img, 6.2, 8.6, 1.0, (255, 255, 255, 210))      # блик
    return img


ITEMS = {
    "quest_token":         tex_quest_token,
    "quest_token_premium": tex_quest_token_premium,
    "quest_medal":         tex_quest_medal,
}


# --------------------------------------------------------------------------- #
#  Баннеры глав (256x64)
# --------------------------------------------------------------------------- #

def banner(base, accent, light, motif, label):
    """Полосатый градиентный фон + мотив + подпись.

    FTB Quests рисует картинку главы как прямоугольник в координатах сетки
    квестов, поэтому баннер делается широким (4:1).
    """
    W, H = 256, 64
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(base[i] * (1 - t * 0.55) + accent[i] * (t * 0.55)) for i in range(3))
        for x in range(W):
            # лёгкая «шахматная» фактура, чтобы баннер не был плоским
            shade = 0 if ((x // 8) + (y // 8)) % 2 == 0 else -14
            img.putpixel((x, y), (max(0, min(255, c[0] + shade)),
                                  max(0, min(255, c[1] + shade)),
                                  max(0, min(255, c[2] + shade)), 235))
    # рамка
    for x in range(W):
        px(img, x, 0, light + (255,)); px(img, x, H - 1, (0, 0, 0, 160))
    for y in range(H):
        px(img, 0, y, light + (255,)); px(img, W - 1, y, (0, 0, 0, 160))

    if motif == "ore":
        for i, (mx, my) in enumerate([(28, 30), (52, 20), (40, 44), (70, 36), (22, 14)]):
            for dx in range(-5, 6):
                for dy in range(-5, 6):
                    if abs(dx) + abs(dy) <= 5:
                        px(img, mx + dx, my + dy, light if (dx + dy) % 3 else accent)
    elif motif == "sword":
        for i in range(34):
            px(img, 30 + i, 48 - i, light)
            px(img, 31 + i, 48 - i, light)
        rect(img, 24, 44, 12, 4, accent)
    elif motif == "wheat":
        for sx in (26, 40, 54):
            for i in range(26):
                px(img, sx, 20 + i, accent)
            for i in range(5):
                px(img, sx - 3 + i, 14 + i * 2, light)
                px(img, sx + 3 - i, 14 + i * 2, light)
    elif motif == "gear":
        cx, cy, r = 42, 32, 16
        for y in range(H):
            for x in range(W):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if r - 4 <= d <= r:
                    import math
                    a = math.atan2(y - cy, x - cx)
                    if (int((a + math.pi) / (math.pi / 6))) % 2 == 0 or d <= r - 4:
                        px(img, x, y, light)
        circle(img, cx, cy, 6, accent)
    elif motif == "portal":
        for y in range(10, 54):
            for x in range(20, 66):
                if (x - 20) % 8 < 5 and (y - 10) % 8 < 6:
                    px(img, x, y, accent)
        rect(img, 18, 8, 50, 4, (60, 30, 20, 255))
        rect(img, 18, 52, 50, 4, (60, 30, 20, 255))
    elif motif == "star":
        star(img, 44, 32, 22, light)
        for i in range(40):
            px(img, 80 + i * 3, 12 + (i * 7) % 40, (255, 255, 255, 190))
    elif motif == "blocks":
        for i, (bx, by) in enumerate([(20, 14), (40, 14), (60, 14), (20, 34), (40, 34), (60, 34)]):
            rect(img, bx, by, 16, 16, light if i % 2 else accent)
            rect(img, bx, by, 16, 2, (255, 255, 255, 90))
    elif motif == "compass":
        cx, cy, r = 42, 32, 20
        circle(img, cx, cy, r, (0, 0, 0, 120), fill=False)
        circle(img, cx, cy, r - 3, light, fill=False)
        for i in range(-r + 4, r - 3):
            px(img, cx + i, cy + i, accent)
            px(img, cx + i, cy - i, (255, 255, 255, 220))
    elif motif == "potion":
        rect(img, 36, 10, 12, 6, (200, 200, 210, 255))
        for y in range(16, 50):
            w = min(20, 6 + (y - 16) * 2)
            rect(img, 42 - w // 2, y, w, 1, accent if y > 26 else light)
    elif motif == "cube":
        cx, cy = 42, 32
        for y in range(-18, 19):
            for x in range(-18, 19):
                if abs(x) + abs(y) <= 18:
                    px(img, cx + x, cy + y, light if x < 0 and y < 0 else (accent if x >= 0 else base))
    else:  # 'plain'
        rect(img, 18, 18, 52, 28, light)

    # подпись слева от мотива не рисуем: текст в FTB Quests берётся из lang-файла,
    # а растровые буквы выглядели бы чужеродно при смене языка.
    return img


CHAPTER_BANNERS = {
    # имя файла              базовый   акцент    светлый   мотив
    "banner_beginning":   ((58, 122, 58),  (34, 74, 34),  (150, 214, 130), "blocks"),
    "banner_mining":      ((92, 92, 104),  (48, 48, 58),  (196, 168, 96),  "ore"),
    "banner_combat":      ((150, 46, 46),  (74, 18, 18),  (236, 168, 150), "sword"),
    "banner_food":        ((176, 148, 52), (96, 148, 52), (240, 226, 150), "wheat"),
    "banner_enchanting":  ((96, 52, 156),  (44, 20, 78),  (196, 150, 240), "potion"),
    "banner_redstone":    ((140, 40, 36),  (66, 16, 16),  (240, 120, 100), "gear"),
    "banner_nether":      ((146, 62, 32),  (62, 20, 16),  (246, 168, 90),  "portal"),
    "banner_end":         ((70, 56, 110),  (24, 18, 44),  (206, 196, 246), "star"),
    "banner_exploration": ((44, 122, 132), (16, 58, 66),  (150, 224, 226), "compass"),
    "banner_building":    ((110, 122, 150),(52, 60, 80),  (196, 206, 226), "cube"),
    "banner_advancement": ((150, 122, 46),(86, 66, 18),  (246, 226, 150), "star"),
    "banner_custom":      ((176, 132, 34),(96, 66, 12),  (250, 222, 130), "gear"),
    "banner_mastery":     ((40, 40, 46),  (16, 16, 20),  (198, 176, 240), "star"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="не писать, а сверить хэши существующих файлов")
    args = ap.parse_args()

    made = []
    for d in (ITEM_DIR, GUI_DIR):
        os.makedirs(d, exist_ok=True)

    for name, fn in ITEMS.items():
        img = fn()
        assert img.size == (16, 16), name
        p = os.path.join(ITEM_DIR, name + ".png")
        made.append((p, img))

    for name, (base, accent, light, motif) in CHAPTER_BANNERS.items():
        img = banner(base, accent, light, motif, name)
        p = os.path.join(GUI_DIR, name + ".png")
        made.append((p, img))

    if args.check:
        bad = []
        for p, img in made:
            if not os.path.isfile(p):
                bad.append(p + " (нет)")
                continue
            buf = os.urandom(0)
            import io
            b = io.BytesIO(); img.save(b, "PNG")
            if hashlib.sha256(b.getvalue()).hexdigest() != hashlib.sha256(open(p, "rb").read()).hexdigest():
                bad.append(p + " (отличается)")
        if bad:
            print("ТЕКСТУРЫ УСТАРЕЛИ:")
            for b in bad:
                print("  " + b)
            print("Запустите: python scripts/gen_textures.py")
            return 1
        print("текстур %d, все актуальны" % len(made))
        return 0

    import io
    for p, img in made:
        img.save(p, "PNG")
        print("  %-64s %5d байт" % (os.path.relpath(p, ROOT).replace(os.sep, "/"),
                                     os.path.getsize(p)))
    print("всего текстур: %d" % len(made))
    return 0


if __name__ == "__main__":
    sys.exit(main())
