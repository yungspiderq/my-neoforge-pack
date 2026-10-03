#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup-github.py — полная автоматическая публикация модпака на GitHub.

Делает за один запуск:
  1. проверяет токен (GET /user)
  2. создаёт репозиторий (или использует существующий)
  3. включает GitHub Pages с source = GitHub Actions
  4. проставляет имя пака / автора / версии MC в pack.toml
  5. записывает packsync/pack-url.txt
  6. git init → commit → push (токен НЕ попадает ни в .git/config, ни на диск)
  7. ставит тег и пушит его → GitHub Actions собирает релиз
  8. ждёт завершения workflow и проверяет, что pack.toml реально отдаётся
  9. печатает все ссылки

ТОКЕН НИКОГДА НЕ ПЕЧАТАЕТСЯ И НЕ СОХРАНЯЕТСЯ.
Способы передать (в порядке предпочтения):
  • переменная окружения GITHUB_TOKEN          ← рекомендуется
  • --token-file /path/to/file                ← файл вне репозитория, chmod 600
  • интерактивный ввод (символы не отображаются)

Какие права нужны токену:
  Fine-grained PAT, только на этот репозиторий:
      Contents:      Read and write
      Administration: Read and write   (нужно для включения Pages)
      Metadata:      Read-only          (выдаётся автоматически)
  Срок действия — 1 день. После настройки отозвать:
      https://github.com/settings/personal-access-tokens

Примеры:
  # всё полностью автоматически
  GITHUB_TOKEN=github_pat_xxx python scripts/setup-github.py \
      --repo my-neoforge-pack --public \
      --pack-name "Наш Пак" --author my-nick

  # только посмотреть, что будет сделано
  GITHUB_TOKEN=github_pat_xxx python scripts/setup-github.py --repo my-pack --dry-run

  # без релиза (только создать репо и запушить)
  GITHUB_TOKEN=github_pat_xxx python scripts/setup-github.py --repo my-pack --no-release
"""

from __future__ import annotations

import argparse
import base64
import getpass
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://api.github.com"
UA = "modpack-setup/1.0"

TOKEN: str = ""
DRY = False
FORCE_PUSH = False


# --------------------------------------------------------------------------- #
#  Вывод
# --------------------------------------------------------------------------- #

def red(s):    return "\033[31m%s\033[0m" % s
def green(s):  return "\033[32m%s\033[0m" % s
def cyan(s):   return "\033[36m%s\033[0m" % s
def yellow(s): return "\033[33m%s\033[0m" % s
def bold(s):   return "\033[1m%s\033[0m" % s


def step(n, msg):  print("\n" + bold(cyan("[%d] " % n)) + bold(msg))
def ok(msg):       print("    " + green("✔ ") + msg)
def note(msg):     print("    " + cyan("· ") + msg)
def warn(msg):     print("    " + yellow("! ") + msg)


def die(msg):
    print("\n" + red("ОШИБКА: ") + msg, file=sys.stderr)
    raise SystemExit(1)


# --------------------------------------------------------------------------- #
#  GitHub API
# --------------------------------------------------------------------------- #

def api(method: str, path: str, body=None, accept_errors=()):
    url = path if path.startswith("http") else API + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", UA)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "ignore")
        if e.code in accept_errors:
            try:
                return e.code, json.loads(raw)
            except Exception:
                return e.code, {"message": raw[:400]}
        try:
            msg = json.loads(raw).get("message", raw[:400])
        except Exception:
            msg = raw[:400]
        die("GitHub API %s %s → HTTP %s\n    %s" % (method, path, e.code, msg))
    except Exception as e:
        die("GitHub API %s %s недоступен: %s" % (method, path, e))


# --------------------------------------------------------------------------- #
#  Токен
# --------------------------------------------------------------------------- #

def get_token(args) -> str:
    if args.token_file:
        p = os.path.expanduser(args.token_file)
        if not os.path.isfile(p):
            die("файл токена не найден: " + p)
        t = open(p, encoding="utf-8").read().strip()
        note("токен прочитан из " + p)
        return t
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        note("токен взят из переменной окружения")
        return t.strip()
    if not sys.stdin.isatty():
        die("токен не передан. Используйте GITHUB_TOKEN=... или --token-file")
    print("\nВставьте токен (символы не отображаются и не сохраняются):")
    t = getpass.getpass("  GITHUB_TOKEN: ").strip()
    if not t:
        die("пустой токен")
    return t


# --------------------------------------------------------------------------- #
#  Git (токен передаётся через окружение, а не через URL и не через файлы)
# --------------------------------------------------------------------------- #

def git(*a, check=True, capture=False):
    cmd = ["git", "-c", "credential.helper=", *a]
    if DRY:
        print("    $ git " + " ".join(a))
        return ""
    r = subprocess.run(cmd, cwd=ROOT, capture_output=capture, text=True, env=git_env())
    if check and r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip()
        die("git %s не удался:\n%s" % (" ".join(a), err))
    return (r.stdout or "") if capture else ""


def git_env():
    """Токен инжектим как HTTP-заголовок через GIT_CONFIG_* — так он не
    попадает ни в .git/config, ни в аргументы процесса, ни в историю."""
    e = os.environ.copy()
    e["GIT_TERMINAL_PROMPT"] = "0"
    e["GIT_CONFIG_COUNT"] = "2"
    e["GIT_CONFIG_KEY_0"] = "http.https://github.com/.extraHeader"
    e["GIT_CONFIG_VALUE_0"] = "Authorization: Bearer " + TOKEN
    e["GIT_CONFIG_KEY_1"] = "credential.helper"
    e["GIT_CONFIG_VALUE_1"] = ""
    return e


def git_out(*a):
    return git(*a, capture=True).strip()


def git_has_repo():
    return os.path.isdir(os.path.join(ROOT, ".git"))


# --------------------------------------------------------------------------- #
#  Правка pack.toml
# --------------------------------------------------------------------------- #

def patch_pack_toml(args, owner_login: str):
    path = os.path.join(ROOT, "pack.toml")
    text = open(path, encoding="utf-8").read()
    changed = []

    def sub(key, value):
        nonlocal text
        new = '%s = "%s"' % (key, value)
        pat = r'^%s\s*=\s*".*"$' % key
        if re.search(pat, text, re.M):
            if re.search(pat, text, re.M).group(0) != new:
                text = re.sub(pat, new, text, count=1, flags=re.M)
                changed.append("%s = %s" % (key, value))
        else:
            text = text.rstrip("\n") + "\n" + new + "\n"
            changed.append("%s = %s (добавлено)" % (key, value))

    def sub_in(section, key, value):
        nonlocal text
        m = re.search(r'^\[%s\]\s*$(.*?)(?=^\[|\Z)' % section, text, re.M | re.S)
        if not m:
            warn("в pack.toml нет секции [%s]" % section)
            return
        block = m.group(1)
        new = '%s = "%s"' % (key, value)
        if re.search(r'^%s\s*=\s*".*"$' % key, block, re.M):
            nb = re.sub(r'^%s\s*=\s*".*"$' % key, new, block, count=1, flags=re.M)
        else:
            nb = block.rstrip("\n") + "\n" + new + "\n"
        text = text[:m.start(1)] + nb + text[m.end(1):]
        changed.append("[%s] %s = %s" % (section, key, value))

    if args.pack_name:
        sub("name", args.pack_name)
    if args.author:
        sub("author", args.author)
    else:
        sub("author", owner_login)
    if args.version:
        sub("version", args.version)
    if args.mc:
        sub_in("versions", "minecraft", args.mc)
        gv = [args.mc]
        parts = args.mc.split(".")
        if len(parts) >= 2:
            gv.insert(0, ".".join(parts[:2]))
        text = re.sub(r'^acceptable-game-versions\s*=\s*\[.*\]$',
                      'acceptable-game-versions = [%s]' % ", ".join('"%s"' % v for v in gv),
                      text, count=1, flags=re.M)
        changed.append("acceptable-game-versions = " + ", ".join(gv))
    if args.neoforge:
        sub_in("versions", "neoforge", args.neoforge)

    if changed:
        if DRY:
            for c in changed:
                print("    ~ pack.toml: " + c)
        else:
            open(path, "w", encoding="utf-8", newline="\n").write(text)
            for c in changed:
                note("pack.toml: " + c)
    else:
        note("pack.toml: менять нечего")


def write_pack_url(url: str):
    p = os.path.join(ROOT, "packsync", "pack-url.txt")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if DRY:
        print("    ~ packsync/pack-url.txt = " + url)
        return
    open(p, "w", encoding="utf-8", newline="\n").write(url + "\n")
    ok("packsync/pack-url.txt = " + url)


# --------------------------------------------------------------------------- #
#  Шаги
# --------------------------------------------------------------------------- #

def step_token(n):
    step(n, "Проверяю токен")
    if DRY:
        note("(dry-run: проверка токена пропущена)")
        return os.environ.get("GITHUB_OWNER", "<ваш-ник>"), True
    st, me = api("GET", "/user")
    login = me.get("login")
    plan = me.get("plan", {}) if isinstance(me.get("plan"), dict) else {}
    ok("токен валиден, пользователь: %s (тариф: %s)" % (bold(login), plan.get("name", "?")))
    private_pages = (plan.get("name") or "").lower() in ("pro", "team", "enterprise", "one", "business")
    if not private_pages:
        note("тариф бесплатный → GitHub Pages работает только для ПУБЛИЧНЫХ репозиториев")
    return login, private_pages


def step_repo(n, owner, repo, private, paid_pages, org=None):
    step(n, "Репозиторий %s/%s" % (owner, repo))
    if DRY:
        print("    $ POST /user/repos {name: %s, private: %s}" % (repo, private))
        return "https://github.com/%s/%s" % (owner, repo), "main"
    st, info = api("GET", "/repos/%s/%s" % (owner, repo), accept_errors=(404,))
    if st == 200:
        ok("уже существует: " + info["html_url"])
        if info.get("private") and not paid_pages:
            die("репозиторий приватный, а тариф бесплатный — GitHub Pages не включится.\n"
                "    Сделайте репозиторий публичным или используйте --org/другое имя.")
        return info["html_url"], info.get("default_branch", "main")

    if DRY:
        print("    $ POST /user/repos {name: %s, private: %s}" % (repo, private))
        return "https://github.com/%s/%s" % (owner, repo), "main"

    if private and not paid_pages:
        warn("приватный репозиторий на бесплатном тарифе: Pages не заработают, "
             "используйте Cloudflare Pages / Netlify (см. docs/SETUP.md)")

    body = {"name": repo, "private": private, "auto_init": False,
            "description": "Minecraft modpack (packwiz) with auto-sync via GitHub Pages"}
    path = "/orgs/%s/repos" % org if org else "/user/repos"
    st, created = api("POST", path, body, accept_errors=(422,))
    if st == 422:
        die("не удалось создать репозиторий: %s" % created.get("message"))
    ok("создан: " + created["html_url"] + (" (private)" if private else " (public)"))
    return created["html_url"], "main"


def step_pages(n, owner, repo):
    step(n, "Включаю GitHub Pages (source = GitHub Actions)")
    if DRY:
        print("    $ POST /repos/%s/%s/pages {build_type: workflow}" % (owner, repo))
        return "https://%s.github.io/%s/" % (owner.lower(), repo)
    st, res = api("GET", "/repos/%s/%s/pages" % (owner, repo), accept_errors=(404,))
    if st == 200:
        if (res or {}).get("build_type") == "workflow":
            ok("уже включены: " + res.get("html_url", ""))
            return res.get("html_url", "")
        api("PUT", "/repos/%s/%s/pages" % (owner, repo), {"build_type": "workflow"})
        ok("переключены на GitHub Actions")
        return res.get("html_url", "")
    if DRY:
        print("    $ POST /repos/%s/%s/pages {build_type: workflow}" % (owner, repo))
        return "https://%s.github.io/%s/" % (owner.lower(), repo)
    st, res = api("POST", "/repos/%s/%s/pages" % (owner, repo),
                  {"source": {"branch": "main", "path": "/"}, "build_type": "workflow"},
                  accept_errors=(403, 404, 409))
    if st in (200, 201):
        ok("включены: " + (res or {}).get("html_url", ""))
        return (res or {}).get("html_url", "")
    if st == 409:
        ok("уже включены")
        return "https://%s.github.io/%s/" % (owner.lower(), repo)
    warn("не удалось включить Pages через API (HTTP %s) — сделайте вручную:\n"
         "        Settings → Pages → Build and deployment → Source: GitHub Actions" % st)
    return "https://%s.github.io/%s/" % (owner.lower(), repo)


def _cfg(key):
    if DRY:
        return ""
    r = subprocess.run(["git", "config", "--get", key], cwd=ROOT,
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def ensure_identity(owner, repo):
    """Без user.name/user.email git commit падает — проставляем локально."""
    if _cfg("user.email"):
        return
    email = "%s@users.noreply.github.com" % owner
    git("config", "user.name", owner, check=False)
    git("config", "user.email", email, check=False)
    ok("git identity (локально для этого репо): %s <%s>" % (owner, email))


def step_git(n, clone_url, pages_base, version, owner):
    step(n, "Локальный git: init → commit → push")
    if not git_has_repo():
        git("init", "-q")
        ok("git init")
    else:
        note("git-репозиторий уже инициализирован")
    ensure_identity(owner, version)

    branch = git_out("rev-parse", "--abbrev-ref", "HEAD") if _has_commits() else ""
    if branch in ("", "master"):
        git("symbolic-ref", "HEAD", "refs/heads/main")
    ok("ветка: main")

    remote = git_out("remote") if not DRY else ""
    if "origin" in remote.split():
        git("remote", "set-url", "origin", clone_url)
        note("origin обновлён: " + clone_url)
    else:
        git("remote", "add", "origin", clone_url)
        ok("origin = " + clone_url)

    git("add", "-A")
    if _has_commits():
        git("commit", "-q", "-m", "chore: configure pack publishing", "--allow-empty", check=False)
    else:
        git("commit", "-q", "-m", "init: modpack with auto-sync via packwiz + GitHub Pages")
    ok("коммит создан")

    push_args = ["push", "-u", "origin", "main"]
    if FORCE_PUSH:
        push_args.append("--force")
    r = subprocess.run(["git", "-c", "credential.helper="] + push_args,
                       cwd=ROOT, capture_output=True, text=True, env=git_env())
    if r.returncode != 0 and not DRY:
        err = (r.stderr or r.stdout or "").strip()
        if "non-fast-forward" in err or "fetch first" in err:
            warn("в удалённом репозитории уже есть коммиты. Варианты:")
            warn("  • повторите с --force (удалённая история будет перезаписана)")
            warn("  • или сначала git pull --rebase origin main")
            die("push отклонён")
        die("git push не удался:\n" + err)
    ok("запушено в main")


def _has_commits():
    if DRY:
        return False
    r = subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"],
                       cwd=ROOT, capture_output=True, text=True)
    return r.returncode == 0


def step_tag(n, owner, repo, version):
    step(n, "Создаю тег v%s и запускаю сборку релиза" % version)
    tag = "v" + version
    if DRY:
        print("    $ git tag %s && git push origin %s" % (tag, tag))
        return tag
    if git_out("tag", "-l", tag):
        note("тег %s уже существует — пересоздаю на текущий коммит" % tag)
        git("tag", "-d", tag)
    git("tag", tag)
    git("push", "origin", tag, "-f")
    ok("тег %s запушен → workflow «2. Build release» стартовал" % tag)
    return tag


def step_wait(n, owner, repo):
    step(n, "Жду завершения GitHub Actions")
    if DRY:
        note("(в dry-run пропускаю)")
        return
    deadline = time.time() + 600
    last = {}
    while time.time() < deadline:
        st, runs = api("GET", "/repos/%s/%s/actions/runs?per_page=10" % (owner, repo))
        items = (runs or {}).get("workflow_runs", [])
        if not items:
            time.sleep(5)
            continue
        cur = {}
        for r in items[:6]:
            cur[r["name"]] = (r["status"], r.get("conclusion"))
        if cur != last:
            for name, (status, concl) in cur.items():
                mark = green("✔") if concl == "success" else (
                    red("✘") if concl in ("failure", "cancelled") else cyan("…"))
                print("    %s %-45s %s%s" % (mark, name[:45], status,
                                             "" if not concl else " / " + str(concl)))
            last = cur
        publish = [r for r in items if "Publish pack" in r["name"]]
        if publish and publish[0]["status"] == "completed":
            if publish[0].get("conclusion") == "success":
                ok("пак опубликован на GitHub Pages")
            else:
                warn("workflow публикации завершился с ошибкой: " + publish[0]["html_url"])
            return
        time.sleep(10)
    warn("не дождался завершения за 10 минут — проверьте вкладку Actions вручную")


def step_verify(n, pack_url):
    step(n, "Проверяю, что пак реально отдаётся")
    if DRY:
        note("(в dry-run пропускаю)")
        return
    for attempt in range(12):
        try:
            req = urllib.request.Request(pack_url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode("utf-8", "ignore")
            if "pack-format" in body:
                ok("%s → HTTP 200, pack.toml валиден" % pack_url)
                return
            warn("по адресу pack.toml отдаётся что-то unexpected")
            return
        except Exception as e:
            if attempt < 11:
                note("ещё не готово (%s), жду 15 с…" % type(e).__name__)
                time.sleep(15)
    warn("pack.toml так и не появился. Первый деплой Pages может занять до 5 минут — "
         "проверьте позже вручную.")


# --------------------------------------------------------------------------- #
#  main
# --------------------------------------------------------------------------- #

def main():
    global TOKEN, DRY, FORCE_PUSH

    ap = argparse.ArgumentParser(
        prog="setup-github.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", help="имя репозитория на GitHub")
    ap.add_argument("--org", help="создать репозиторий в организации, а не в личном аккаунте")
    ap.add_argument("--owner", help="владелец репозитория (нужен только для --dry-run без токена)")
    ap.add_argument("--public", dest="private", action="store_false", default=None,
                    help="публичный репозиторий (рекомендуется: внутри только ссылки)")
    ap.add_argument("--private", dest="private", action="store_true",
                    help="приватный репозиторий (Pages — только на платном тарифе)")
    ap.add_argument("--token-file", help="файл с токеном (вне репозитория, chmod 600)")

    ap.add_argument("--pack-name", help="имя пака (поле name в pack.toml)")
    ap.add_argument("--author", help="автор (поле author в pack.toml)")
    ap.add_argument("--version", default=None, help="версия пака (по умолчанию — из pack.toml)")
    ap.add_argument("--mc", help="версия Minecraft, например 1.21.4")
    ap.add_argument("--neoforge", help="версия NeoForge, например 21.4.158")

    ap.add_argument("--no-release", action="store_true", help="не создавать тег/релиз")
    ap.add_argument("--no-wait", action="store_true", help="не ждать завершения Actions")
    ap.add_argument("--force", action="store_true",
                    help="перезаписать удалённую ветку main (если там уже есть коммиты)")
    ap.add_argument("--yes", "-y", action="store_true", help="не спрашивать подтверждение")
    ap.add_argument("--dry-run", action="store_true", help="только показать план действий")
    args = ap.parse_args()
    DRY = args.dry_run
    FORCE_PUSH = args.force

    print(bold("\n=== Публикация модпака на GitHub ===") +
          (yellow("   [DRY RUN — ничего не меняю]\n") if DRY else "\n"))

    TOKEN = get_token(args) if not args.dry_run else (
        os.environ.get("GITHUB_TOKEN") or "dry-run-placeholder")

    # --- токен ---
    login, paid_pages = step_token(1)
    if args.owner:
        login = args.owner
    owner = args.org or login

    # --- имя репозитория ---
    pack_path = os.path.join(ROOT, "pack.toml")
    if not os.path.isfile(pack_path):
        die("pack.toml не найден в " + ROOT)
    pack_text = open(pack_path, encoding="utf-8").read()
    cur_name = (re.search(r'^name\s*=\s*"(.*)"$', pack_text, re.M) or [None, "modpack"])[1]
    cur_ver = (re.search(r'^version\s*=\s*"(.*)"$', pack_text, re.M) or [None, "1.0.0"])[1]

    def slug(s):
        s = re.sub(r"\(.*\)", "", s.lower())
        return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-") or "modpack"

    repo = args.repo or slug(args.pack_name or cur_name)
    version = args.version or cur_ver

    # --- план ---
    print(bold("\nПлан:"))
    print("    репозиторий : %s/%s  (%s)" % (owner, repo, "private" if args.private else "public"))
    print("    пак         : %s %s" % (args.pack_name or cur_name, version))
    if args.mc:
        print("    Minecraft   : %s / NeoForge %s" % (args.mc, args.neoforge or "(как в pack.toml)"))
    print("    Pages       : https://%s.github.io/%s/pack.toml" % (owner.lower(), repo))
    print("    релиз       : %s" % ("пропускаю" if args.no_release else "v" + version))
    if not DRY and not args.yes:
        try:
            if input("\nПродолжить? [д/Н] ").strip().lower() not in ("д", "y", "yes", "да"):
                die("отменено пользователем")
        except EOFError:
            pass

    # --- выполнение ---
    pack_url = "https://%s.github.io/%s/pack.toml" % (owner.lower(), repo)
    html_url, _ = step_repo(2, owner, repo, bool(args.private), paid_pages, args.org)
    pages_url = step_pages(3, owner, repo)

    patch_pack_toml(args, login)
    step(4, "Записываю адрес пака")
    write_pack_url(pack_url)

    clone_url = "https://github.com/%s/%s.git" % (owner, repo)
    step_git(5, clone_url, pages_url, version, owner)

    if not args.no_release:
        step_tag(6, owner, repo, version)
        n = 7
    else:
        n = 6

    if not args.no_wait:
        step_wait(n, owner, repo)
        step_verify(n + 1, pack_url)

    # --- итог ---
    print("\n" + bold(green("=== ГОТОВО ===")))
    print("  Репозиторий : %s" % html_url)
    print("  Actions     : %s/actions" % html_url)
    print("  pack.toml   : %s" % pack_url)
    if not args.no_release:
        print("  Релизы      : %s/releases   ← эти файлы раздаёте игрокам" % html_url)
    print("  Страница    : %s" % (pages_url or ""))
    print()
    print(bold("  Дальше:"))
    print("   1. Откройте Releases, скачайте *-instance.zip и проверьте на себе")
    print("   2. Отдайте друзьям ссылку на Releases и INSTALL.md")
    print("   3. ОТОЗВИТЕ токен: https://github.com/settings/personal-access-tokens")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nпрервано")
        raise SystemExit(130)
