"""
gen_resourcepack.py — собирает ресурс-пак с русским переводом Galosphere
(GalosphereRU.zip) из того же файла, что лежит в
kubejs/assets/galosphere/lang/ru_ru.json (единый источник перевода).

Две копии одного zip (байт-в-байт идентичны):
  * resourcepacks/GalosphereRU.zip — УПАКОВАННАЯ копия: входит в пак
    (index.toml) и скачивается игрокам АВТОМАТИЧЕСКИ в
    .minecraft/resourcepacks/ при установке/обновлении любым способом
    (packwiz-установщик, Modpack Manager, .mrpack через overrides/);
  * <корень workspace>/GalosphereRU.zip — запасная копия «для рук»:
    раздать вручную, положить в чужой клиент/instance 1.21.1 без KubeJS.

Включать ресурспак в настройках НЕ требуется: в сборке перевод и так
применяется автоматически через kubejs/assets/ (KubeJS монтирует её как
ресурс-пак поверх jar'ов модов). Упакованный zip — видимая в меню
«Наборы ресурсов» портативная копия того же перевода (на случай клиента
без KubeJS или желания унести перевод с собой).

Детерминированность: zip собирается в памяти, времена файлов фиксированы,
содержимое байт-в-байт повторяемо между запусками (важно для CI и хэшей).

Запуск:
  python scripts/gen_resourcepack.py            # записать обе копии
  python scripts/gen_resourcepack.py out.zip    # записать только out.zip
  python scripts/gen_resourcepack.py --check    # CI: упакованная копия
                                                # в resourcepacks/ должна
                                                # байт-в-байт совпадать
                                                # с пересобранной
"""

from __future__ import annotations

import io
import json
import struct
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # modpack/
SRC = ROOT / "kubejs" / "assets" / "galosphere" / "lang" / "ru_ru.json"
SNAPSHOT = ROOT / "scripts" / "lang" / "galosphere_en_us.json"

PACK_FORMAT = 34  # MC 1.21 / 1.21.1
DESC = "§dGalosphere RU §8| §fполный русский перевод мода §7(297 ключей, MC 1.21.1)"
ZIP_DATE = (2026, 10, 4, 12, 0, 0)  # фиксированная метка времени для детерминированности


# --------------------------------------------------------------------------
# мини-энкодер PNG (RGBA, 8 бит) без зависимостей
# --------------------------------------------------------------------------
def _png_chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def make_icon(size: int = 128) -> bytes:
    """Пиксель-арт: кристалл розовой соли с гранями и искрами на тёмном фоне."""
    cx = cy = size // 2
    radius = 44
    bg = (24, 10, 22, 255)
    edge = (255, 227, 236, 255)
    spark = (255, 240, 246, 255)
    facets = {
        (False, False): (247, 205, 217, 255),
        (True, False): (238, 174, 194, 255),
        (False, True): (226, 149, 176, 255),
        (True, True): (207, 125, 156, 255),
    }
    sparks = {(30, 26), (98, 40), (24, 92), (100, 100), (64, 12)}
    near_spark = set()
    for sx, sy in sparks:
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            near_spark.add((sx + dx, sy + dy))

    rows = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            d = abs(x - cx) + abs(y - cy)
            if d <= radius:
                if d >= radius - 2:
                    col = edge
                else:
                    col = facets[(x >= cx, y >= cy)]
                    if d <= radius // 2:  # внутренняя грань светлее
                        col = (min(255, col[0] + 12), min(255, col[1] + 12),
                               min(255, col[2] + 12), 255)
            elif (x, y) in near_spark:
                col = spark
            else:
                col = bg
            row += bytes(col)
        rows.append(bytes(row))

    raw = b"".join(b"\x00" + r for r in rows)
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(raw, 9))
        + _png_chunk(b"IEND", b"")
    )


# --------------------------------------------------------------------------
#  Сборка zip в памяти (детерминированно)
# --------------------------------------------------------------------------
PACKAGED = ROOT / "resourcepacks" / "GalosphereRU.zip"   # входит в пак
STANDALONE = ROOT.parent / "GalosphereRU.zip"            # запасная копия


def build_zip_bytes() -> tuple[bytes, str]:
    """Возвращает (байты zip, отчёт о покрытии перевода)."""
    ru = json.loads(SRC.read_text(encoding="utf-8"))
    report = f"ключей ru_ru: {len(ru)}"
    if SNAPSHOT.exists():
        en = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        missing = sorted(set(en) - set(ru))
        if missing:
            raise SystemExit(
                f"ОШИБКА: не переведено ключей: {len(missing)} -> {missing[:5]}...\n"
                "Сначала dopeреведите kubejs/assets/galosphere/lang/ru_ru.json."
            )
        report += f", покрытие en_us: {len(ru)}/{len(en)}"

    mcmeta = json.dumps(
        {"pack": {"pack_format": PACK_FORMAT, "description": DESC}},
        ensure_ascii=False,
        indent=2,
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for arcname, data in (
            ("pack.mcmeta", (mcmeta + "\n").encode("utf-8")),
            ("pack.png", make_icon()),
            ("assets/galosphere/lang/ru_ru.json", SRC.read_bytes()),
        ):
            zi = zipfile.ZipInfo(arcname, date_time=ZIP_DATE)
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, data)
    return buf.getvalue(), report


def main() -> int:
    args = sys.argv[1:]
    check = "--check" in args
    outs = [a for a in args if not a.startswith("--")]
    data, report = build_zip_bytes()

    if check:
        if not PACKAGED.exists():
            print(f"ОШИБКА: {PACKAGED} отсутствует — соберите: "
                  "python scripts/gen_resourcepack.py")
            return 1
        cur = PACKAGED.read_bytes()
        if cur != data:
            print(f"ОШИБКА: {PACKAGED} устарел (не совпадает с пересобранным "
                  f"из текущего ru_ru.json). Пересоберите: "
                  "python scripts/gen_resourcepack.py")
            return 1
        print(f"OK: resourcepacks/GalosphereRU.zip актуален "
              f"({len(data)} байт), {report}")
        return 0

    targets = [Path(outs[0])] if outs else [PACKAGED, STANDALONE]
    for out in targets:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        rel = out.relative_to(ROOT) if out.is_relative_to(ROOT) else out
        print(f"OK: {rel} ({len(data)} байт), {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
