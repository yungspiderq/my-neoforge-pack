#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_textures.py — рисует текстуры для кастомных предметов KubeJS и для
оформления глав FTB Quests.

Всё рисуется программно (Pillow), а не скачивается: картинки детерминированы
(одни и те же байты при каждом запуске), весят килобайты и их можно
перепроверять в CI через --check.

Куда кладутся:
  kubejs/assets/kubejs/textures/item/<имя>.png   — предметы KubeJS (16x16)
  kubejs/assets/kubejs/textures/gui/<имя>.png    — картинки глав FTB Quests
      в SNBT главы: image: "kubejs:textures/gui/<имя>.png"

Что за картинки gui/:
  banner_<глава>.png  — широкий баннер над деревом квестов (256x64, 4:1);
  plate.png           — пластинка для подписей секций (красится полем color,
                        текст рисуется поверх шрифтом игры и переводится);
  panel_soft.png      — мягкая подложка под блок секции (красится color);
  halo.png            — ореол позади иконки вехи (красится color);
  portal.png,
  portal_end.png      — кликабельные «порталы» между главами.

Все gui-текстуры, кроме баннеров, рисуются белыми/серыми: FTB Quests умножает
цвет текстуры на поле color картинки (ChapterImageButton.draw →
image.withColor(color.withAlpha(alpha))), поэтому одна текстура даёт любой
цвет оформления.

Запуск:  python scripts/gen_textures.py [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import io
import math
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


# --------------------------------------------------------------------------- #
#  Примитивы
# --------------------------------------------------------------------------- #

def px(img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((int(x), int(y)), c)


def rect(img, x0, y0, w, h, c):
    for y in range(int(y0), int(y0 + h)):
        for x in range(int(x0), int(x0 + w)):
            px(img, x, y, c)


def circle(img, cx, cy, r, c, fill=True):
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d2 = (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2
            if fill and d2 <= r * r:
                px(img, x, y, c)
            elif not fill and abs(math.sqrt(d2) - r) < 0.75:
                px(img, x, y, c)


def star(img, cx, cy, r, c):
    """Пятиконечная звезда попиксельно."""
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))

    def inside(x, y):
        n = len(pts)
        s = 0
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
                s += 1
        return s % 2 == 1

    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            if inside(x + 0.5, y + 0.5):
                px(img, x, y, c)


def rnd(seed):
    """Детерминированный псевдослучай в [0, 1): без него баннеры не были бы
    воспроизводимы, а --check в CI начал бы падать."""
    x = math.sin(seed * 127.1 + 311.7) * 43758.5453
    return x - math.floor(x)


def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))


def mix(a, b, t):
    return tuple(clamp(a[i] * (1 - t) + b[i] * t) for i in range(3))


def vgrad(img, top, bottom, y0=0, y1=None):
    """Вертикальный градиент по всей ширине."""
    y1 = img.height if y1 is None else y1
    for y in range(y0, y1):
        t = (y - y0) / max(1, (y1 - y0 - 1))
        c = mix(top, bottom, t)
        for x in range(img.width):
            px(img, x, y, c + (255,))


def frame(img, light, dark):
    """Тонкая рамка: светлая сверху/слева, тёмная снизу/справа."""
    W, H = img.width, img.height
    for x in range(W):
        px(img, x, 0, light + (255,))
        px(img, x, H - 1, dark + (255,))
    for y in range(H):
        px(img, 0, y, light + (255,))
        px(img, W - 1, y, dark + (255,))


def hills(img, base_y, amp, color, seed, step=0.021):
    """Силуэт холмов синусоидой: заполняет всё, что ниже линии."""
    for x in range(img.width):
        h = base_y + amp * math.sin(x * step * 6.283 + seed) \
                   + amp * 0.5 * math.sin(x * step * 15.7 + seed * 2.3)
        for y in range(int(h), img.height):
            px(img, x, y, color + (255,))


def stars(img, count, seed, ymax=None, bright=(255, 255, 255)):
    ymax = img.height if ymax is None else ymax
    for i in range(count):
        x = int(rnd(seed + i) * img.width)
        y = int(rnd(seed + i + 99.5) * ymax)
        a = int(120 + rnd(seed + i + 7.25) * 135)
        px(img, x, y, bright + (a,))


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
    rect(img, 7, 0, 2, 2, (120, 78, 12, 255))             # ушко для ленты
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
    for i in range(7):                                    # ленты
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
#  Баннеры глав (256x64, соотношение 4:1 — как width/height картинки главы)
# --------------------------------------------------------------------------- #

def banner_overworld():
    """Рассвет над холмами: небо, солнце, два слоя холмов, ёлки."""
    W, H = 256, 64
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for y in range(H):
        t = y / (H - 1)
        if t < 0.55:
            c = mix((14, 22, 52), (96, 74, 128), t / 0.55)
        else:
            c = mix((96, 74, 128), (248, 178, 96), (t - 0.55) / 0.45)
        for x in range(W):
            shade = 0 if ((x // 8) + (y // 8)) % 2 == 0 else -6
            img.putpixel((x, y), (clamp(c[0] + shade), clamp(c[1] + shade),
                                  clamp(c[2] + shade), 240))
    stars(img, 70, 3.1, ymax=26)
    circle(img, 206, 26, 11, (255, 214, 130, 235))         # солнце
    circle(img, 206, 26, 7, (255, 244, 200, 255))
    hills(img, 40, 5.0, (46, 88, 52), 1.7)                 # дальние холмы
    hills(img, 50, 4.0, (26, 58, 34), 4.2)                 # ближние холмы
    for i in range(9):                                     # ёлки на ближних
        x = 14 + i * 27 + int(rnd(i * 3.3) * 10)
        h = 8 + int(rnd(i * 7.7) * 6)
        for k in range(h):
            w = max(1, (h - k) // 3)
            rect(img, x - w, 58 - k, w * 2 + 1, 1, (16, 40, 24))
        rect(img, x, 58, 1, 4, (40, 26, 16))
    rect(img, 0, 62, W, 2, (14, 30, 18, 255))
    frame(img, (178, 226, 150), (10, 22, 12))
    return img


def banner_nether():
    """Пекло: багровое небо, силуэт крепости, озеро лавы, угли."""
    W, H = 256, 64
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for y in range(H):
        t = y / (H - 1)
        c = mix((26, 6, 8), (150, 44, 18), t) if t < 0.72 \
            else mix((150, 44, 18), (255, 150, 44), (t - 0.72) / 0.28)
        for x in range(W):
            shade = 0 if ((x // 8) + (y // 8)) % 2 == 0 else -8
            img.putpixel((x, y), (clamp(c[0] + shade), clamp(c[1] + shade),
                                  clamp(c[2] + shade), 240))
    for i in range(46):                                    # угли
        x = int(rnd(i * 2.7) * W)
        y = int(rnd(i * 5.1) * 44)
        px(img, x, y, (255, 190 + int(rnd(i) * 60), 90, 200))
    for bx, bw, bh in [(18, 26, 30), (52, 14, 20), (168, 30, 34), (206, 12, 18)]:
        rect(img, bx, 46 - bh, bw, bh, (54, 16, 14, 255))  # башни крепости
        for k in range(0, bw - 4, 6):
            rect(img, bx + 2 + k, 46 - bh + 4, 3, 6, (255, 120, 40, 220))
        rect(img, bx, 46 - bh, bw, 2, (86, 28, 20, 255))
    hills(img, 46, 3.0, (74, 22, 16), 2.2)
    for y in range(52, H):                                 # лава
        for x in range(W):
            w = math.sin(x * 0.09 + y * 0.6) * 0.5 + 0.5
            c = mix((210, 78, 18), (255, 214, 96), w * (1 - (y - 52) / 14.0))
            px(img, x, y, c + (255,))
    frame(img, (255, 168, 92), (30, 8, 6))
    return img


def banner_end():
    """Край: почти чёрное небо, звёзды, остров и обсидиановые колонны."""
    W, H = 256, 64
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for y in range(H):
        t = y / (H - 1)
        c = mix((6, 5, 16), (36, 26, 62), t)
        for x in range(W):
            shade = 0 if ((x // 8) + (y // 8)) % 2 == 0 else -4
            img.putpixel((x, y), (clamp(c[0] + shade), clamp(c[1] + shade),
                                  clamp(c[2] + shade), 240))
    stars(img, 190, 11.3)
    for i in range(9):                                     # фиолетовая дымка
        x = int(rnd(i * 4.4) * W)
        y = int(rnd(i * 9.1) * 40)
        circle(img, x, y, 3 + int(rnd(i) * 4), (120, 90, 190, 26))
    for bx, bh in [(30, 34), (54, 26), (186, 30), (214, 22)]:   # колонны
        rect(img, bx, 52 - bh, 10, bh, (18, 12, 26, 255))
        rect(img, bx, 52 - bh, 10, 2, (46, 34, 62, 255))
        if bh > 28:
            px(img, bx + 5, 52 - bh - 3, (226, 190, 255, 255))  # кристалл
            px(img, bx + 4, 52 - bh - 2, (190, 150, 240, 255))
            px(img, bx + 6, 52 - bh - 2, (190, 150, 240, 255))
    hills(img, 50, 2.5, (206, 202, 150), 3.4)              # остров Края
    for x in range(0, W, 3):
        px(img, x, 49 + int(rnd(x * 0.7) * 3), (170, 166, 120, 255))
    rect(img, 118, 40, 20, 12, (8, 6, 14, 255))            # врата
    for k in range(4):
        px(img, 121 + k * 5, 46, (150, 240, 220, 255))
    frame(img, (176, 160, 232), (4, 3, 10))
    return img


BANNERS = {
    "banner_overworld": banner_overworld,
    "banner_nether":    banner_nether,
    "banner_end":       banner_end,
}


# --------------------------------------------------------------------------- #
#  Оформление: белые/серые текстуры, которые FTB Quests красит полем color
# --------------------------------------------------------------------------- #

def tex_plate():
    """Пластинка для подписи секции (128x24).

    Рисуется светлой: цвет задаёт поле color картинки главы. Лёгкий градиент
    и светлая нижняя кромка дают объём, скруглённые углы — аккуратный вид.
    """
    W, H = 128, 24
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    r = 5
    for y in range(H):
        t = y / (H - 1)
        v = int(236 - 46 * t)                       # светлый верх, темнее низ
        for x in range(W):
            # скругление углов
            dx = max(r - x, x - (W - 1 - r), 0)
            dy = max(r - y, y - (H - 1 - r), 0)
            if dx * dx + dy * dy > r * r:
                continue
            a = 255
            if dx or dy:
                a = 200
            img.putpixel((x, y), (v, v, v, a))
    for x in range(r, W - r):                       # нижняя кромка-подсветка
        img.putpixel((x, H - 2), (255, 255, 255, 255))
        img.putpixel((x, H - 1), (180, 180, 180, 255))
    for x in range(r, W - r):                       # верхняя кромка
        img.putpixel((x, 0), (255, 255, 255, 210))
    return img


def tex_panel_soft():
    """Мягкая подложка под блок секции (64x64).

    Полностью белая внутри и прозрачная по краям: при alpha≈46 и цвете секции
    получается лёгкая «зона» позади квестов, на которой иконки читаются лучше.
    """
    S = 64
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    r = 9
    edge = 6
    for y in range(S):
        for x in range(S):
            dx = max(r - x, x - (S - 1 - r), 0)
            dy = max(r - y, y - (S - 1 - r), 0)
            if dx * dx + dy * dy > r * r:
                continue
            d = min(x, y, S - 1 - x, S - 1 - y)
            if d < edge:                              # мягкий край
                a = int(150 + 105 * (d / edge))
                v = int(228 + 27 * (d / edge))
            else:
                a, v = 255, 250
            img.putpixel((x, y), (v, v, v, a))
    return img


def tex_halo():
    """Ореол позади вехи (64x64): радиальное свечение + тонкое кольцо."""
    S = 64
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    c = S / 2.0
    for y in range(S):
        for x in range(S):
            d = math.hypot(x + 0.5 - c, y + 0.5 - c) / c
            if d > 1.0:
                continue
            a = int(255 * (1 - d) ** 2.1)             # свечение к центру
            ring = 1.0 if 0.70 <= d <= 0.76 else 0.0
            v = int(255 * (1 - 0.25 * ring))
            a = min(255, a + int(190 * ring))
            img.putpixel((x, y), (v, v, v, a))
    return img


def tex_portal():
    """Портал в Незер (32x32): обсидиановая рама и фиолетовое полотно."""
    S = 32
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    rect(img, 4, 1, 24, 30, (24, 18, 34, 255))        # рама
    for i in range(0, 24, 4):                         # блоки обсидиана
        rect(img, 4 + i, 1, 3, 3, (38, 30, 52, 255))
        rect(img, 4 + i, 28, 3, 3, (38, 30, 52, 255))
    for i in range(0, 30, 4):
        rect(img, 4, 1 + i, 3, 3, (38, 30, 52, 255))
        rect(img, 25, 1 + i, 3, 3, (38, 30, 52, 255))
    for y in range(4, 28):                              # полотно
        for x in range(7, 25):
            w = math.sin(x * 0.55 + y * 0.42) * 0.5 + 0.5
            w2 = math.sin(y * 0.31 - x * 0.19) * 0.5 + 0.5
            c = mix((70, 20, 130), (206, 130, 255), (w + w2) / 2)
            px(img, x, y, c + (255,))
    for i in range(14):                                 # блики
        x = 8 + int(rnd(i * 3.7) * 15)
        y = 5 + int(rnd(i * 8.1) * 21)
        px(img, x, y, (240, 210, 255, 235))
    return img


def tex_portal_end():
    """Портал Края (32x32): чёрная рама со звёздами внутри."""
    S = 32
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    rect(img, 3, 3, 26, 26, (10, 8, 18, 255))
    rect(img, 4, 4, 24, 24, (4, 3, 10, 255))
    for y in range(6, 26):
        for x in range(6, 26):
            w = math.sin(x * 0.7 + y * 0.5) * 0.5 + 0.5
            if w > 0.86:
                px(img, x, y, (150, 240, 220, 255))
            elif w > 0.72:
                px(img, x, y, (60, 120, 130, 255))
    for i in range(18):
        x = 6 + int(rnd(i * 2.3) * 19)
        y = 6 + int(rnd(i * 6.9) * 19)
        px(img, x, y, (226, 214, 255, 235))
    for k in range(4):                                  # зелёные «глаза» рамы
        px(img, 4 + k * 7, 4, (150, 240, 220, 255))
        px(img, 4 + k * 7, 27, (150, 240, 220, 255))
    return img


GUI_TEXTURES = {
    "plate":        tex_plate,
    "panel_soft":   tex_panel_soft,
    "halo":         tex_halo,
    "portal":       tex_portal,
    "portal_end":   tex_portal_end,
}


# --------------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="не писать, а сверить хэши существующных файлов")
    args = ap.parse_args()

    made = []
    for d in (ITEM_DIR, GUI_DIR):
        os.makedirs(d, exist_ok=True)

    for name, fn in ITEMS.items():
        img = fn()
        assert img.size == (16, 16), name
        made.append((os.path.join(ITEM_DIR, name + ".png"), img))

    for name, fn in BANNERS.items():
        img = fn()
        assert img.size == (256, 64), name
        made.append((os.path.join(GUI_DIR, name + ".png"), img))

    for name, fn in GUI_TEXTURES.items():
        img = fn()
        made.append((os.path.join(GUI_DIR, name + ".png"), img))

    if args.check:
        bad = []
        for p, img in made:
            if not os.path.isfile(p):
                bad.append(p + " (нет)")
                continue
            b = io.BytesIO()
            img.save(b, "PNG")
            if hashlib.sha256(b.getvalue()).hexdigest() != \
                    hashlib.sha256(open(p, "rb").read()).hexdigest():
                bad.append(p + " (отличается)")
        if bad:
            print("ТЕКСТУРЫ УСТАРЕЛИ:")
            for b in bad:
                print("  " + b)
            print("Запустите: python scripts/gen_textures.py")
            return 1
        print("текстур %d, все актуальны" % len(made))
        return 0

    for p, img in made:
        img.save(p, "PNG")
        print("  %-62s %4dx%-4d %6d байт"
              % (os.path.relpath(p, ROOT).replace(os.sep, "/"),
                 img.width, img.height, os.path.getsize(p)))
    print("всего текстур: %d" % len(made))
    return 0


if __name__ == "__main__":
    sys.exit(main())
