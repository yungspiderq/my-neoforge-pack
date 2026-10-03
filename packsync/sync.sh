#!/bin/sh
# =====================================================================
#  packsync — автосинхронизация модпака (Linux / macOS)
# ---------------------------------------------------------------------
#  Запускается лаунчером ПЕРЕД стартом игры.
#  Никогда не валит старт игры: при любой ошибке возвращаем 0.
#
#  В AstralRinth / Modrinth App hook прописывается так:
#      sh packsync/sync.sh
#  (hook там режет строку по пробелам и НЕ подставляет переменные,
#   поэтому именно так — три токена без пробелов)
# =====================================================================

DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || exit 0
GAME_DIR=$(CDPATH= cd -- "$DIR/.." && pwd) || exit 0

BOOT_JAR="$DIR/packwiz-installer-bootstrap.jar"
MAIN_JAR="$DIR/packwiz-installer.jar"
URL_FILE="$DIR/pack-url.txt"

[ -f "$BOOT_JAR" ] || exit 0
[ -f "$MAIN_JAR" ] || exit 0
[ -f "$URL_FILE" ] || exit 0

PACK_URL=$(head -n 1 "$URL_FILE" | tr -d '\r' | sed 's/[[:space:]]*$//')
[ -n "$PACK_URL" ] || exit 0

find_java() {
    if [ -n "$JAVA_HOME" ] && [ -x "$JAVA_HOME/bin/java" ]; then
        echo "$JAVA_HOME/bin/java"; return 0
    fi
    if command -v java >/dev/null 2>&1; then
        command -v java; return 0
    fi
    for root in \
        "$HOME/.local/share/astralrinth/java_runtimes" \
        "$HOME/.var/app/su.astralium.AstralRinth/data/astralrinth/java_runtimes" \
        "$HOME/.local/share/ModrinthApp/java_runtimes" \
        "$HOME/.local/share/PrismLauncher/java" \
        "$HOME/.local/share/freesmlauncher/java" \
        "$HOME/.jdks" \
        "/usr/lib/jvm" \
        "/Library/Java/JavaVirtualMachines"
    do
        [ -d "$root" ] || continue
        hit=$(find "$root" -type f -name java -perm -u+x 2>/dev/null | sort | tail -n 1)
        if [ -n "$hit" ]; then echo "$hit"; return 0; fi
    done
    return 1
}

JAVA_BIN=$(find_java) || exit 0

echo "[packsync] $JAVA_BIN"
echo "[packsync] $PACK_URL"

"$JAVA_BIN" -jar "$BOOT_JAR" \
    --bootstrap-no-update \
    --bootstrap-main-jar "$MAIN_JAR" \
    --pack-folder "$GAME_DIR" \
    -g "$PACK_URL"

echo "[packsync] exit code $?"
exit 0
