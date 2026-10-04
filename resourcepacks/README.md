# resourcepacks/

**Всё, что лежит здесь, скачивается игрокам в `.minecraft/resourcepacks/`.**

Кладите сюда `.zip`-архивы текстур-паков (не распакованные папки — packwiz
работает с файлами, а не с директориями внутри пака).

> ⚠️ Текстуры — это обычные файлы, поэтому они попадают в git целиком.
> При большом паке (>100 МБ) включите [Git LFS](https://git-lfs.com/)
> или раздавайте пак через `pw.py add-url` со ссылкой на GitHub Releases.

После добавления файла выполните:

```bash
python scripts/pw.py refresh
```

Активируется ресурспак у игроков автоматически, если прописать его
в `options.txt` (см. `config/README.md` про флаг `preserve`).

---

**`GalosphereRU.zip`** — не редактировать руками: файл детерминированно
генерируется из `kubejs/assets/galosphere/lang/ru_ru.json` скриптом
`python scripts/gen_resourcepack.py` (после правки перевода — перезапустить,
иначе CI-проверка `--check` упадёт). См. `kubejs/README.md`.
