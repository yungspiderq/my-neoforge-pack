#!/usr/bin/env python3
"""Pin Modrinth mods, resource packs and shaders for Minecraft 1.21.1.

Only Modrinth CDN links + hashes are recorded; no JAR/ZIP is redistributed.
"""
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://api.modrinth.com/v2/"
MC = "1.21.1"
HEADERS = {"User-Agent": "MyNeoForgePack/0.2 (github.com/yungspiderq/my-neoforge-pack)"}
TARGETS = json.loads((ROOT / "pack-selection.json").read_text(encoding="utf-8"))
FOLDERS = {"mod": "mods", "resourcepack": "resourcepacks", "shader": "shaderpacks"}


def fetch(endpoint, query=None):
    url = BASE + endpoint
    if query:
        url += "?" + urllib.parse.urlencode(query)
    last = None
    for retry in range(5):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=35) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            last = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code not in (429, 500, 502, 503, 504):
                raise
            time.sleep(min(2 ** retry, 16))
    raise RuntimeError(f"Modrinth API request failed: {url}: {last}")


def versions(project, exact=True):
    kind = project["project_type"]
    params = {"game_versions": json.dumps([MC if exact else "1.21"])}
    if kind == "mod":
        params["loaders"] = json.dumps(["neoforge"])
    return fetch(f'project/{project["id"]}/version', params)


def preferred(versions_list):
    stable = [v for v in versions_list if v.get("version_type") == "release"]
    choices = stable or versions_list
    return sorted(choices, key=lambda v: v.get("date_published", ""), reverse=True)[0]


def quote(value):
    return json.dumps(value, ensure_ascii=False)


def write_project(project, version):
    kind = project["project_type"]
    slug = project["slug"]
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", slug):
        raise ValueError("Unsafe project slug " + slug)
    extension = ".jar" if kind == "mod" else ".zip"
    files = [f for f in version.get("files", []) if f.get("filename", "").lower().endswith(extension)]
    if not files:
        raise ValueError(f"No {extension} for {slug}")
    entry = next((f for f in files if f.get("primary")), files[0])
    hashes = entry.get("hashes", {})
    alg = "sha512" if hashes.get("sha512") else "sha1"
    if not hashes.get(alg):
        raise ValueError(f"Missing checksum for {slug}")
    filename = entry["filename"]
    if Path(filename).name != filename or "/" in filename or "\\" in filename:
        raise ValueError("Unsafe filename " + filename)
    output = ROOT / FOLDERS[kind] / (slug + ".pw.toml")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Replaced at each resolver run; the version is pinned to its real download hash.
    contents = [
        "name = " + quote(project["title"]),
        "filename = " + quote(filename),
        "side = " + quote("client" if kind != "mod" or project.get("client_side") == "required" and project.get("server_side") == "unsupported" else "both"),
        "",
        "[download]",
        "url = " + quote(entry["url"]),
        "hash-format = " + quote(alg),
        "hash = " + quote(hashes[alg]),
        "",
        "[update.modrinth]",
        "mod-id = " + quote(project["id"]),
        "version = " + quote(version["id"]),
        "",
    ]
    data = "\n".join(contents)
    if not output.exists() or output.read_text(encoding="utf-8") != data:
        output.write_text(data, encoding="utf-8")
        print(f"Updated {output.relative_to(ROOT)}: {version.get('version_number')}")
    else:
        print(f"Pinned {output.relative_to(ROOT)}: {version.get('version_number')}")


def run():
    queue = [(t["slug"], t["type"], bool(t.get("optional", False)), None) for t in TARGETS]
    seen = set()
    resolved = set()
    wanted = {"mod": set(), "resourcepack": set(), "shader": set()}
    errors = []
    while queue:
        slug, expected_type, optional, specific_version_id = queue.pop(0)
        key = (slug, expected_type)
        if key in seen:
            continue
        seen.add(key)
        try:
            proj = fetch("project/" + urllib.parse.quote(slug, safe=""))
            if proj["project_type"] != expected_type:
                raise ValueError(f"Expected {expected_type}, found {proj['project_type']} for {slug}")
            if specific_version_id:
                vs = [fetch("version/" + specific_version_id)]
            else:
                vs = versions(proj)
                if not vs and expected_type != "mod":
                    vs = versions(proj, exact=False)
            if not vs:
                raise ValueError(f"No compatible Minecraft {MC} / NeoForge version for {slug}")
            picked = preferred(vs)
            if expected_type == "mod" and not ("neoforge" in picked.get("loaders", []) and MC in picked.get("game_versions", [])):
                raise ValueError(f"Version is not exact NeoForge {MC}: {slug}")
            write_project(proj, picked)
            resolved.add((proj["id"], expected_type))
            wanted[expected_type].add(proj["slug"])
            for dep in picked.get("dependencies") or []:
                if expected_type != "mod" or dep.get("dependency_type") != "required":
                    continue
                pid = dep.get("project_id")
                vid = dep.get("version_id")
                if not pid and vid:
                    pid = fetch("version/" + vid).get("project_id")
                if pid and (pid, "mod") not in resolved:
                    queue.append((pid, "mod", False, vid))
        except Exception as exc:
            if optional:
                errors.append(f"Optional {slug} skipped: {exc}")
                print(errors[-1])
            else:
                raise RuntimeError(f"Required component {slug} failed: {exc}") from exc
    for kind, folder in FOLDERS.items():
        path = ROOT / folder
        if not path.exists():
            continue
        for file in path.glob("*.pw.toml"):
            # Keep manually pinned FTB modules (Maven) and discard dropped Modrinth selections.
            if kind == "mod" and file.stem in ("ftb-quests.pw", "ftb-library.pw", "ftb-teams.pw", "ftb-filter-system.pw", "ftb-xmod-compat.pw"):
                continue
            if file.name[:-len(".pw.toml")] not in wanted[kind]:
                print("Removing no longer selected:", file)
                file.unlink()
    print(f"Resolved {len(wanted['mod'])} Modrinth mods + {len(wanted['resourcepack'])} resource packs + {len(wanted['shader'])} shaders")
    for item in errors:
        print(item)


if __name__ == "__main__":
    run()
