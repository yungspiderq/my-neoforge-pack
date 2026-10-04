#!/usr/bin/env bash
# =====================================================================
#  Однокнопочный установщик модпака (Linux / macOS)
#
#  Запуск:
#      curl -fsSL https://<user>.github.io/<repo>/install.sh | bash
#  или с флагами:
#      curl -fsSL .../install.sh | bash -s -- --launcher astralrinth
#
#  Флаги:
#      --launcher NAME   freesm | prism | multimc | astralrinth | modrinth | auto
#      --base-url URL    переопределить адрес пака
#      -h, --help
# =====================================================================

set -euo pipefail

BASE_URL='@@BASE_URL@@'
LAUNCHER='auto'

while [ $# -gt 0 ]; do
    case "$1" in
        --launcher) LAUNCHER="${2:-auto}"; shift 2 ;;
        --base-url) BASE_URL="${2:-}";     shift 2 ;;
        -h|--help)  sed -n '2,17p' "$0";   exit 0 ;;
        *) echo "неизвестный флаг: $1" >&2; exit 2 ;;
    esac
done

C_G=$'\033[32m'; C_Y=$'\033[33m'; C_C=$'\033[36m'; C_R=$'\033[31m'; C_0=$'\033[0m'
ok()   { printf '     %s[OK]%s   %s\n' "$C_G" "$C_0" "$1"; }
info() { printf '     %s[..]%s   %s\n' "$C_C" "$C_0" "$1"; }
step() { printf '\n  %s->%s %s\n' "$C_Y" "$C_0" "$1"; }
bad()  { printf '     %s[X]%s    %s\n' "$C_R" "$C_0" "$1" >&2; }

download() {  # download URL DEST
    if command -v curl >/dev/null 2>&1; then curl -fsSL "$1" -o "$2"
    elif command -v wget >/dev/null 2>&1; then wget -q "$1" -O "$2"
    else bad 'нужен curl или wget'; exit 1; fi
}

echo
printf '  %s=============================================================%s\n' "$C_C" "$C_0"
printf '  %s  Установка модпака%s\n' "$C_C" "$C_0"
printf '  %s=============================================================%s\n' "$C_C" "$C_0"

case "$BASE_URL" in
    *'@@BASE'*)
        bad 'адрес пака не задан: скачайте скрипт со страницы GitHub Pages'
        bad 'или передайте --base-url https://<user>.github.io/<repo>'
        exit 1 ;;
esac
info "адрес пака: $BASE_URL"

# --------------------------------------------------------------------- #
#  Поиск лаунчеров
# --------------------------------------------------------------------- #

FLATPAK_IDS="org.prismlauncher.PrismLauncher com.modrinth.theseus su.astralium.AstralRinth"

find_bin() {  # find_bin name...
    for n in "$@"; do
        command -v "$n" 2>/dev/null && return 0
    done
    for n in "$@"; do
        for d in /usr/bin /usr/local/bin /opt "$HOME/.local/bin" /Applications "$HOME/Applications"; do
            [ -x "$d/$n" ] && { printf '%s\n' "$d/$n"; return 0; }
        done
    done
    # AppImage
    for n in "$@"; do
        for f in "$HOME"/*"$n"*.AppImage "$HOME"/Downloads/*"$n"*.AppImage; do
            [ -x "$f" ] && { printf '%s\n' "$f"; return 0; }
        done
    done
    # flatpak
    if command -v flatpak >/dev/null 2>&1; then
        for id in $FLATPAK_IDS; do
            if flatpak info "$id" >/dev/null 2>&1; then
                case "$id" in
                    *PrismLauncher*) for n in "$@"; do case "$n" in *rismlauncher*|*reesm*) printf 'flatpak:%s\n' "$id"; return 0;; esac; done ;;
                    *theseus*|*AstralRinth*) for n in "$@"; do case "$n" in *stral*|*odrinth*) printf 'flatpak:%s\n' "$id"; return 0;; esac; done ;;
                esac
            fi
        done
    fi
    return 1
}

PRISM_EXE=''; PRISM_NAME=''
THESEUS_EXE=''; THESEUS_NAME=''

step 'Ищу установленные лаунчеры'
if E="$(find_bin freesmlauncher FreesmLauncher)"; then PRISM_EXE="$E"; PRISM_NAME='Freesm Launcher'; ok "Freesm Launcher: $E"; fi
if [ -z "$PRISM_EXE" ] && E="$(find_bin prismlauncher PrismLauncher)"; then PRISM_EXE="$E"; PRISM_NAME='Prism Launcher'; ok "Prism Launcher: $E"; fi
if [ -z "$PRISM_EXE" ] && E="$(find_bin multimc MultiMC)"; then PRISM_EXE="$E"; PRISM_NAME='MultiMC'; ok "MultiMC: $E"; fi
if E="$(find_bin astralrinth AstralRinthApp 'AstralRinth App')"; then THESEUS_EXE="$E"; THESEUS_NAME='AstralRinth'; ok "AstralRinth: $E"; fi
if [ -z "$THESEUS_EXE" ] && E="$(find_bin modrinth-app ModrinthApp 'Modrinth App')"; then THESEUS_EXE="$E"; THESEUS_NAME='Modrinth App'; ok "Modrinth App: $E"; fi
[ -n "$PRISM_EXE$THESEUS_EXE" ] || info 'ничего не нашёл'

# --------------------------------------------------------------------- #
#  Выбор лаунчера
# --------------------------------------------------------------------- #

MODE=''
case "$LAUNCHER" in
    auto)                     if [ -n "$PRISM_EXE" ]; then MODE=prism; else MODE=theseus; fi ;;
    freesm|prism|multimc)     [ -n "$PRISM_EXE" ]   || { bad 'Prism-подобный лаунчер не найден'; exit 1; }; MODE=prism ;;
    astralrinth|modrinth)     [ -n "$THESEUS_EXE" ] || { bad "$LAUNCHER не найден"; exit 1; };      MODE=theseus ;;
    *)                        bad "неизвестный --launcher: $LAUNCHER"; exit 2 ;;
esac

run_launcher() {  # run_launcher EXE args...
    local exe="$1"; shift
    case "$exe" in
        flatpak:*) flatpak run "${exe#flatpak:}" "$@" ;;
        *)         "$exe" "$@" ;;
    esac
}

copy_hook() {
    local text="$1" tool
    for tool in wl-copy xclip xsel pbcopy; do
        if command -v "$tool" >/dev/null 2>&1; then
            case "$tool" in
                wl-copy) printf '%s' "$text" | wl-copy ;;
                xclip)   printf '%s' "$text" | xclip -selection clipboard ;;
                xsel)    printf '%s' "$text" | xsel --clipboard --input ;;
                pbcopy)  printf '%s' "$text" | pbcopy ;;
            esac
            ok "строка hook'а в буфере обмена: $text"
            return 0
        fi
    done
    info "скопируйте вручную:  $text"
}

# --------------------------------------------------------------------- #
#  Установка
# --------------------------------------------------------------------- #

if [ "$MODE" = prism ]; then
    step "Передаю лаунчеру: $PRISM_NAME --import <url>"
    info 'лаунчер сам скачает инстанс, Minecraft, NeoForge и Java'
    run_launcher "$PRISM_EXE" --import "$BASE_URL/latest/instance.zip" &
    sleep 1
    ok 'команда передана — дальше лаунчер всё сделает сам'
else
    MRP="${TMPDIR:-/tmp}/modpack-latest.mrpack"
    step "Скачиваю пак: $BASE_URL/latest/pack.mrpack"
    download "$BASE_URL/latest/pack.mrpack" "$MRP"
    ok "сохранено: $MRP"

    step "Копирую строку hook'а в буфер обмена"
    copy_hook 'sh packsync/sync.sh'

    step "Запускаю $THESEUS_NAME с файлом пака (auto-import)"
    run_launcher "$THESEUS_EXE" "$MRP" &
    sleep 1

    cat <<'EOF'

  Осталось 4 действия (один раз):
    1. Дождитесь окончания импорта профиля
    2. Откройте настройки профиля: Options
    3. Раздел Hooks -> поле Pre-launch -> вставьте из буфера
       должно получиться ровно:  sh packsync/sync.sh
    4. Сохраните и запустите профиль

  Почему так: Theseus-лаунчеры выполняют hook без shell, режут строку по
  пробелам и не подставляют переменные. Вся логика (поиск Java, адрес пака)
  спрятана в packsync/sync.sh.

EOF
fi

printf '  %s=============================================================%s\n' "$C_G" "$C_0"
printf '  %s  Готово%s\n' "$C_G" "$C_0"
printf '  %s=============================================================%s\n' "$C_G" "$C_0"
echo
echo '  Дальше моды обновляются САМИ при каждом запуске игры.'
echo "  Источник истины: $BASE_URL/pack.toml"
echo
