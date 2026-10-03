# Первичная настройка

Пошаговый чек-лист: от пустой папки до работающей раздачи.

---

## ⚡ Автоматически — одной командой

Всё, что описано ниже в разделах 1–5, умеет делать `scripts/setup-github.py`:

```bash
export GITHUB_TOKEN=github_pat_xxxxxxxxxxxx

python scripts/setup-github.py \
    --repo my-neoforge-pack \
    --public \
    --pack-name "Наш Пак" \
    --mc 1.21.1 --neoforge 21.1.252

unset GITHUB_TOKEN
```

Скрипт по шагам:

| # | Действие | API |
|---|---|---|
| 1 | Проверяет токен, узнаёт ваш логин и тариф | `GET /user` |
| 2 | Создаёт репозиторий (или берёт существующий) | `POST /user/repos` |
| 3 | Включает Pages с `source = GitHub Actions` | `POST /repos/{o}/{r}/pages` |
| 4 | Проставляет `name` / `author` / `version` / `minecraft` / `neoforge` в `pack.toml` | — |
| 5 | Пишет `packsync/pack-url.txt` | — |
| 6 | `git init` → `commit` → `push -u origin main` | git + Bearer-заголовок |
| 7 | Ставит и пушит тег `v<version>` → стартует сборка релиза | git |
| 8 | Ждёт завершения workflow «1. Publish pack» | `GET /repos/{o}/{r}/actions/runs` |
| 9 | Проверяет, что `pack.toml` реально отдаётся по HTTP | — |

### Безопасность токена

Скрипт спроектирован так, чтобы токен **не мог** никуда утечь:

- читается из `GITHUB_TOKEN` / `--token-file` / скрытого ввода (`getpass`);
- **никогда не печатается** и не пишется в лог;
- в git передаётся через переменные окружения `GIT_CONFIG_KEY_0` /
  `GIT_CONFIG_VALUE_0` как HTTP-заголовок `Authorization: Bearer …`.
  Это значит, что токен **не попадает** ни в `.git/config`
  (в `remote.origin.url` лежит чистый `https://github.com/…`),
  ни в аргументы процесса, ни в историю shell;
- `credential.helper` принудительно отключён (`-c credential.helper=`),
  поэтому git не попытается сохранить токен в системное хранилище.

**Всё равно отзовите токен сразу после настройки** —
<https://github.com/settings/personal-access-tokens>. Он нужен ровно один раз.

### Полезные флаги

| Флаг | Что делает |
|---|---|
| `--dry-run` | печатает план и все команды, ничего не меняя (токен не нужен, используйте `GITHUB_OWNER=ваш-ник`) |
| `--private` | приватный репозиторий (Pages — только на платном тарифе) |
| `--org NAME` | создать репозиторий в организации |
| `--no-release` | не ставить тег, только запушить main |
| `--no-wait` | не ждать завершения Actions |
| `--force` | перезаписать удалённую `main`, если там уже есть коммиты |
| `--yes` / `-y` | не спрашивать подтверждение |

### Если хотите руками

Разделы ниже описывают ровно те же действия по шагам.

---

## 0. Требования

| Что | Зачем |
|---|---|
| Аккаунт GitHub | Хостинг репозитория, Pages, Actions, Releases |
| Python 3.8+ | Локальный инструмент `scripts/pw.py` (без зависимостей) |
| Git | Версионирование пака |
| *(опционально)* Go 1.24+ | Официальный `packwiz` локально. **Не обязателен** — CI ставит его сам |

Установка официального packwiz (если хочется):

```bash
go install github.com/packwiz/packwiz@latest
```

Или готовый бинарник: <https://nightly.link/packwiz/packwiz/workflows/go/main>
→ выберите архив под свою ОС.

---

## 1. Настроить pack.toml

Откройте `pack.toml` и впишите своё:

```toml
name = "Наш Серверный Пак"        # имя, которое увидят игроки
author = "ваш-ник-на-github"
version = "1.0.0"                  # поднимайте при каждом релизе
description = "Короткое описание"

[versions]
minecraft = "1.21.1"
neoforge = "21.1.252"

[options]
acceptable-game-versions = ["1.21", "1.21.1"]
```

Как узнать актуальную версию NeoForge для вашей версии MC:
`https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml`
— ищите последнюю версию с нужным префиксом (`21.1.x` для MC 1.21.1).

> **Про выбор версии MC.** Чем старше и стабильнее ветка, тем больше модов
> под неё существует. На момент сборки этого шаблона картина по Modrinth
> (количество NeoForge-модов) была такой:
>
> | Minecraft | NeoForge-модов |
> |---|---|
> | 1.21.1 | ~21 000 ← самый богатый выбор |
> | 1.21.4 | ~9 300 |
> | 1.21.8 | ~9 000 |
> | 1.21.11 | ~8 000 |
> | 26.1.2 | ~7 800 |
> | 26.2 | ~6 400 |
>
> Перепроверьте цифры сами — они меняются каждый месяц.

---

## 2. Создать репозиторий на GitHub

1. <https://github.com/new> → имя, например `my-neoforge-pack`.
2. **Private или Public?**

   | | Репозиторий Public | Репозиторий Private |
   |---|---|---|
   | GitHub Pages | ✅ бесплатно | ⚠️ только на GitHub Pro / Team / Enterprise |
   | Кто видит код | Все | Только вы |
   | Что внутри | Только **ссылки** на моды + ваши конфиги | То же |

   Репозиторий **не содержит файлов модов** — только ссылки и ваши конфиги,
   так что публичный репозиторий обычно не проблема.

   > 📌 Даже у приватного репозитория страница на GitHub Pages доступна
   > всем по прямой ссылке (это особенность Pages, а не дыра в настройках).
   > То есть «приватный пак на приватном репо» = недоступный для поиска,
   > но доступный по ссылке. Для раздачи друзьям этого достаточно.

3. **НЕ** инициализируйте репозиторий README/`.gitignore`/лицензией — они у нас уже есть.

---

## 3. Запушить пак

```bash
cd modpack

git init
git add -A
git commit -m "init: modpack scaffold"
git branch -M main
git remote add origin https://github.com/<ваш-ник>/<имя-репо>.git

# Адрес пака — из него sync-скрипты узнают, куда ходить
python scripts/pw.py set-url https://<ваш-ник>.github.io/<имя-репо>/pack.toml
git add packsync/pack-url.txt
git commit -m "chore: set pack url"

git push -u origin main
```

> Адрес **обязательно** в нижнем регистре — GitHub Pages чувствителен к этому.
> В CI он вычисляется автоматически (`${GITHUB_REPOSITORY_OWNER,,}`), так что
> даже если вы ошиблись локально, опубликованные артефакты будут корректными.

---

## 4. Включить GitHub Pages

Перейдите в **Settings → Pages → Build and deployment**:

- **Source:** `GitHub Actions`

Workflow `pages.yml` пытается включить это сам (`configure-pages` с
`enablement: true`), но при первом запуске у репозитория может не хватить
прав — проверьте вручную.

Дальше:

1. Откройте вкладку **Actions**.
2. Дождитесь завершения workflow **«1. Publish pack (GitHub Pages)»**.
3. Откройте `https://<ваш-ник>.github.io/<имя-репо>/pack.toml` в браузере.
   Должен показаться TOML-текст.
4. Проверьте `https://<ваш-ник>.github.io/<имя-репо>/index.toml`.

Если вместо этого 404 — подождите пару минут (первый деплой Pages медленный)
и обновите страницу.

---

## 5. Собрать первый релиз

```bash
# убедитесь, что version в pack.toml = "1.0.0"
git tag v1.0.0
git push origin v1.0.0
```

Workflow **«2. Build release»** соберёт и приложит к релизу:

| Файл | Для кого |
|---|---|
| `<pack>-1.0.0-instance.zip` | Freesm / Prism / MultiMC — **полный авто-синк** |
| `<pack>-1.0.0.mrpack` | AstralRinth / Modrinth App — импорт + hook |

Ссылку на страницу релизов (`https://github.com/<ник>/<репо>/releases`)
и [`INSTALL.md`](../INSTALL.md) отдаёте игрокам.

---

## 6. Проверить на себе

**Способ 1 — через Pages (как у игроков):**
создайте новый инстанс в Freesm/Prism, импортируйте `…-instance.zip`
из релиза и запустите.

**Способ 2 — локально, без GitHub:**

```bash
python scripts/pw.py serve --port 8080
# в другом терминале:
python scripts/pw.py set-url http://localhost:8080/pack.toml
```

Временно подставьте `http://localhost:8080/pack.toml` в Pre-Launch Command
тестового инстанса. Так можно отлаживать пак, ничего не публикуя.
**Не забудьте вернуть боевой URL и закоммитить.**

---

## Дальнейший цикл работы

```bash
python scripts/pw.py add <мод>      # добавить
python scripts/pw.py update --all   # обновить всё
python scripts/pw.py check          # проверить
git add -A && git commit -m "feat: add <мод>"
git push                            # ← игроки получат при следующем запуске
```

Релиз с новыми установочными файлами нужен **только** когда меняются
`minecraft`/`neoforge`/`packsync` — обычные добавления модов доезжают
до уже установленных инстансов сами.
