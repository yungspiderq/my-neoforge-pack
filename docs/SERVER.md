# Выделенный сервер с тем же паком

Сервер использует **ровно тот же пак** — просто скачивает только
серверную часть модов (`side = "server"` и `side = "both"`).

## Быстрый вариант: вручную

```bash
mkdir my-server && cd my-server

# 1. Качаем NeoForge-сервер нужной версии
#    https://neoforged.net/  ->  Download  ->  Server
#    либо через установщик:
java -jar neoforge-21.1.252-installer.jar --installServer

# 2. Берём packsync из репозитория (или из любого установленного инстанса)
cp -r /путь/к/репо/packsync .

# 3. Синхронизируем ТОЛЬКО серверные моды
java -jar packsync/packwiz-installer-bootstrap.jar \
     --bootstrap-no-update \
     --bootstrap-main-jar packsync/packwiz-installer.jar \
     --pack-folder . \
     -g -s server \
     https://<ваш-ник>.github.io/<имя-репо>/pack.toml

# 4. Принимаем EULA и стартуем
echo "eula=true" > eula.txt
java -Xmx6G @libraries/net/neoforged/neoforge/21.1.252/unix_args.txt nogui
```

Флаг `-s server` — ключевой: без него скачаются и клиентские моды,
которые на сервере не нужны (а иногда и вредны).

## Автообновление при каждом старте

Создайте `start.sh`:

```bash
#!/bin/sh
cd "$(dirname "$0")"

java -jar packsync/packwiz-installer-bootstrap.jar \
     --bootstrap-no-update \
     --bootstrap-main-jar packsync/packwiz-installer.jar \
     --pack-folder . \
     -g -s server \
     "$(head -n 1 packsync/pack-url.txt | tr -d '\r')"

exec java -Xmx6G -XX:+UseG1GC \
     @libraries/net/neoforged/neoforge/21.1.252/unix_args.txt nogui
```

И `start.bat` для Windows:

```bat
@echo off
cd /d "%~dp0"
set /p PACK_URL=<packsync\pack-url.txt
java -jar packsync\packwiz-installer-bootstrap.jar --bootstrap-no-update ^
     --bootstrap-main-jar packsync\packwiz-installer.jar ^
     --pack-folder . -g -s server "%PACK_URL%"
java -Xmx6G -XX:+UseG1GC @libraries\net\neoforged\neoforge\21.1.252\win_args.txt nogui
pause
```

Теперь сервер подхватывает новые моды сам — так же, как клиенты.

## Docker (самый простой способ)

Образ [`itzg/minecraft-server`](https://github.com/itzg/docker-minecraft-server)
умеет packwiz из коробки:

```yaml
services:
  mc:
    image: itzg/minecraft-server
    ports: ["25565:25565"]
    environment:
      EULA: "TRUE"
      TYPE: "PACKWIZ"
      PACKWIZ_URL: "https://<ваш-ник>.github.io/<имя-репо>/pack.toml"
      VERSION: "1.21.1"
      MODS: ""
      MEMORY: "6G"
    volumes:
      - ./data:/data
    restart: unless-stopped
```

Контейнер сам запускает `packwiz-installer` при старте и при каждом рестарте
подтягивает обновления.

## Как помечать моды «только сервер» / «только клиент»

`scripts/pw.py` определяет `side` автоматически по данным Modrinth.
Переопределить можно флагом при добавлении:

```bash
python scripts/pw.py add spark --side server       # профайлер, нужен только серверу
python scripts/pw.py add journeymap --side client  # миникарта — только клиенту
```

Или отредактируйте уже созданный `mods/<имя>.pw.toml`:

```toml
side = "client"     # both | client | server
```

После изменения обязательно `python scripts/pw.py refresh`.

| `side` | Попадёт клиенту | Попадёт на сервер |
|---|---|---|
| `both` | ✅ | ✅ |
| `client` | ✅ | ❌ |
| `server` | ❌ | ✅ |

## Важно про совместимость

Если на сервере стоит мод, которого нет у клиента (или наоборот), игрок
**не сможет подключиться** — NeoForge сверяет списки модов при входе.
Правило простое: всё, что влияет на геймплей, помечайте `both`;
чисто визуальное — `client`; чисто серверную диагностику — `server`.
