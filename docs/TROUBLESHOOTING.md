# Решение проблем

## Настройка репозитория / CI

### Workflow «1. Publish pack» падает на шаге *Configure GitHub Pages*
Зайдите в **Settings → Pages → Build and deployment** и поставьте
**Source: GitHub Actions** вручную. Автоматическое включение требует прав,
которых может не хватить при первом запуске.

### Страница `https://<ник>.github.io/<репо>/pack.toml` отдаёт 404
1. Репозиторий приватный, а тариф бесплатный → Pages недоступны.
   Сделайте репозиторий публичным (в нём нет файлов модов, только ссылки)
   или смените хостинг на Cloudflare Pages / Netlify — они умеют собирать
   из приватного репозитория и дают публичный URL.
2. Первый деплой занимает 1–3 минуты. Просто подождите.
3. Имя владельца в URL **должно быть в нижнем регистре**.
   Проверьте содержимое `packsync/pack-url.txt`.

### Workflow «0. Validate pack» падает с «index.toml устарел»
Вы добавили/изменили файлы, но не пересобрали индекс. Локально:

```bash
python scripts/pw.py refresh
git add index.toml pack.toml
git commit -m "chore: refresh index"
git push
```

*(Это не критично: `pages.yml` всё равно пересобирает индекс перед публикацией.
Проверка существует, чтобы в git лежала актуальная картина.)*

### `go install github.com/packwiz/packwiz@latest` падает
Обычно это значит, что packwiz требует более свежий Go. В workflow стоит
`go-version: stable` — если и это не помогло, зафиксируйте конкретную версию:

```yaml
- uses: actions/setup-go@v5
  with:
    go-version: '1.25'
```

---

## Установка у игрока

### Freesm/Prism: инстанс импортировался, но модов нет
1. ПКМ по инстансу → **Edit** → **Settings** → **Custom commands**.
   Убедитесь, что галка **Custom Commands** включена, а в *Pre-launch command*
   стоит строка с `packwiz-installer-bootstrap.jar`.
2. Запустите инстанс с открытой консолью (**Settings → Console → Show console
   while game is running**) и прочитайте вывод.
3. Откройте `packsync/pack-url.txt` внутри папки игры — адрес должен быть
   рабочим и начинаться с `https://`.

### Freesm/Prism: `Error: Could not find or load main class`
Путь к jar-у неверный. Проверьте, что в папке инстанса реально существует
`minecraft/packsync/packwiz-installer-bootstrap.jar`. Если нет — распакуйте
`…-instance.zip` заново или скопируйте папку `packsync/` из репозитория в
`<папка инстанса>/minecraft/`.

### AstralRinth: hook не срабатывает, моды не появляются
Частые причины:

| Симптом | Причина | Решение |
|---|---|---|
| Игра запускается мгновенно, ничего не качается | Hook не сохранён | Перепроверьте поле **Pre-launch** в Options профиля |
| Ошибка «Не является внутренней или внешней командой» | Написали `packsync/sync.cmd` (прямой слэш) | Windows: ровно `cmd /c packsync\sync.cmd` |
| Ошибка с разбивкой пути | В команде есть пробелы или кавычки | AstralRinth режет строку по пробелам — кавычки использовать нельзя |
| Linux: `Permission denied` | Запустили `./packsync/sync.sh` без exec-бита | Используйте `sh packsync/sync.sh` |

Проверить вручную, что синхронизация вообще работает:

```bat
cd "%APPDATA%\AstralRinth\profiles\<имя профиля>"
packsync\sync.cmd
```

*(точную папку профилей смотрите в настройках AstralRinth → Storage)*

### `[packsync] java.exe not found`
Скрипт не нашёл Java. Варианты:
- установите [Temurin JDK 21](https://adoptium.net/) — он попадёт в `PATH`;
- или задайте переменную окружения `JAVA_HOME` (например,
  `C:\Program Files\Eclipse Adoptium\jdk-21.0.5.11-hotspot`);
- или отредактируйте `packsync/sync.cmd` и впишите полный путь к `java.exe`
  в самое начало блока поиска.

### Игра не запускается после обновления пака
1. Удалите из папки игры `packwiz.json` — это заставит installer
   перепроверить все файлы заново.
2. Если не помогло: удалите папку `mods/` целиком и запустите снова —
   синхронизация скачает всё начисто.
3. Совсем тяжёлый случай — переустановите инстанс из свежего `…-instance.zip`
   (мир и `saves/` при этом сохранятся, если лежат отдельно).

---

## Содержимое пака

### Мод не добавляется: «не нашлось ни одной версии»
Под вашу версию MC/загрузчик нет сборки. Проверьте страницу мода на Modrinth →
вкладка **Versions** → фильтры. Если сборка есть, но под другой загрузчик:

```bash
python scripts/pw.py add <мод> --loader neoforge --mc 1.21.1
```

### Мод скачался для Forge вместо NeoForge
`pw.py` сначала ищет строго под основной загрузчик из `pack.toml`,
но у некоторых модов один и тот же релиз помечен и `forge`, и `neoforge`.
Проверьте `python scripts/pw.py list` — в колонке «ФАЙЛ В mods/» должно быть
`…-neoforge-…`. Если нет, пересоздайте мод явно:

```bash
python scripts/pw.py remove <мод>
python scripts/pw.py add <мод> --loader neoforge
```

### Хочу, чтобы игрок сам выбирал, ставить мод или нет
```bash
python scripts/pw.py add <мод> --optional
```

packwiz-installer покажет список опциональных модов с галочками.
**Внимание:** официальный Modrinth App опциональные моды не понимает и ставит
все подряд — это ограничение самого Modrinth App, а не пака.
Во Freesm/Prism всё работает как надо.

### Конфиг игрока затирается каждым обновлением
Поставьте файлу флаг `preserve = true` в `index.toml`:

```toml
[[files]]
file = "config/mymod.toml"
hash = "…"
preserve = true
```

`pw.py refresh` флаг сохраняет. Либо официальным packwiz:
`packwiz manual add config/mymod.toml --preserve`.

### В пак игрокам попал лишний файл (README, скрипт…)
Значит, он не исключён в `.packwizignore`. Добавьте туда путь, выполните
`python scripts/pw.py refresh` и `python scripts/pw.py check`.

> Напоминалка: packwiz считает частью пака **всё** в корне репозитория,
> кроме `pack.toml`, `index.toml`, `*.pw.toml` и исключённого в `.packwizignore`.

### Файлы в репозитории весят слишком много
`.jar` модов в git быть не должно — только `.pw.toml`. Тяжёлое обычно приносят
ресурспаки и шейдеры. Решения:

```bash
# 1. Git LFS
git lfs install
git lfs track "shaderpacks/*.zip" "resourcepacks/*.zip"

# 2. Или выложить в GitHub Releases и подключить ссылкой
python scripts/pw.py add-url "Complementary Reimagined" \
  https://github.com/<ник>/<репо>/releases/download/assets/Complementary.zip \
  --side client --hash
```

---

## Синхронизация тормозит при каждом запуске

Installer сверяет хэши всех файлов, поэтому на очень больших паках
(500+ файлов) проверка занимает несколько секунд. Ускорить:

- уберите из пака лишние мелкие файлы;
- убедитесь, что окончания строк не «прыгают»: `.gitattributes` в этом
  репозитории форсирует `eol=lf` для всех текстовых файлов. Если вы его
  удалили или правили файлы в редакторе с CRLF — хэши будут постоянно
  не совпадать и файлы будут перекачиваться заново каждый раз.

Проверить, что именно перекачивается, можно в консоли лаунчера —
installer печатает имя каждого файла.
