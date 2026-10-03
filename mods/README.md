# mods/

Здесь лежат **`*.pw.toml` — метаданные модов**, а не сами `.jar` файлы.
Один файл = один мод:

```toml
name = "Just Enough Items (JEI)"
filename = "jei-1.21.1-neoforge-19.57.0.450.jar"   # куда положить в .minecraft/mods/
side = "both"                                       # both | client | server

[download]
url = "https://cdn.modrinth.com/data/u6dRKJwZ/versions/Tn0dgwL0/jei-….jar"
hash-format = "sha1"
hash = "129a0aa982cd520ef8a35abddf592dc4d5655bd9"

[update]
[update.modrinth]
mod-id  = "u6dRKJwZ"      # по нему pw.py update находит новые версии
version = "Tn0dgwL0"
```

Игрок никогда не видит эти файлы: `packwiz-installer` читает их по HTTP,
достаёт `url` и скачивает `.jar` напрямую с Modrinth в `.minecraft/mods/`.

## Как добавлять

```bash
python scripts/pw.py add jei jade journeymap
```

Slug берётся из адреса `https://modrinth.com/mod/<slug>`. Скрипт сам подберёт
версию под загрузчик и MC из `pack.toml`, подтянет обязательные зависимости,
определит `side` и пересоберёт `index.toml`.

То же самое официальным packwiz (если он установлен):

```bash
packwiz modrinth install jei
```

## Дополнительно

| Хочу | Что сделать |
|---|---|
| Мод только для клиента (миникарта, шейдеры) | `--side client` |
| Мод только для сервера (spark, профайлеры) | `--side server` |
| Игрок сам решает, ставить ли мод | `--optional` |
| Зафиксировать версию и не обновлять | `pin = true` в `.pw.toml` |
| Мод, которого нет на Modrinth | `pw.py add-url "<имя>" <ссылка>` или положить `.jar` прямо сюда |

> Про `.jar` в этой папке: packwiz отправит его игрокам как обычный файл в
> `.minecraft/mods/`. Пользуйтесь этим **только** если лицензия мода разрешает
> распространение — иначе выложите файл в GitHub Releases и подключите ссылкой.

*Этот README не входит в пак — он исключён в `.packwizignore`.*
