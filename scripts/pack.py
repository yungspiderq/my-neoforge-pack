#!/usr/bin/env python3
"""Build and validate the clean NeoForge pack, Python 3.11+."""
import argparse
import hashlib
import json
import re
import shutil
import sys
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK_DIRS = ("mods", "config", "defaultconfigs", "kubejs", "resourcepacks", "shaderpacks")
SYNC_FILES = ("sync.cmd", "sync.sh", "pack-url.txt",
              "packwiz-installer-bootstrap.jar", "packwiz-installer.jar",
              "LICENSE-packwiz-installer.txt")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def toml(path):
    return tomllib.loads((ROOT / path).read_text(encoding="utf-8"))


def tracked():
    found = []
    for folder in PACK_DIRS:
        if not (ROOT / folder).exists():
            continue
        for f in (ROOT / folder).rglob("*"):
            if not f.is_file() or f.name.startswith(".") or f.name == "README.md":
                continue
            if folder == "mods" and not f.name.endswith(".pw.toml"):
                raise ValueError("Use packwiz *.pw.toml references, not mod binaries: " + str(f))
            found.append(f.relative_to(ROOT))
    return sorted(found)


def refresh():
    lines = ['hash-format = "sha256"']
    for p in tracked():
        lines += ["", "[[files]]", 'file = "' + p.as_posix() + '"',
                  'hash = "' + digest((ROOT / p).read_bytes()) + '"']
        if p.name.endswith(".pw.toml"):
            lines.append("metafile = true")
    content = ("\n".join(lines) + "\n").encode("utf-8")
    (ROOT / "index.toml").write_bytes(content)
    packfile = ROOT / "pack.toml"
    old = packfile.read_text(encoding="utf-8")
    new, n = re.subn(r'(?m)^hash = "[0-9a-f]{64}"$',
                     'hash = "' + digest(content) + '"', old)
    if n != 1:
        raise ValueError("Expected one hash line in pack.toml")
    packfile.write_text(new, encoding="utf-8")
    print("Refreshed manifest", len(tracked()))


def validate():
    pack = toml("pack.toml")
    contents = (ROOT / "index.toml").read_bytes()
    assert pack["index"]["file"] == "index.toml"
    assert pack["index"]["hash-format"] == "sha256"
    if pack["index"]["hash"] != digest(contents):
        raise ValueError("index hash mismatch: run python scripts/pack.py refresh")
    entries = tomllib.loads(contents.decode("utf-8")).get("files", [])
    wanted = {p.as_posix() for p in tracked()}
    found = {x["file"] for x in entries}
    if wanted != found or len(entries) != len(found):
        raise ValueError("Index file list is stale: run refresh")
    for x in entries:
        name = x["file"]
        if digest((ROOT / name).read_bytes()) != x["hash"]:
            raise ValueError("Hash mismatch in " + name)
        is_mod = name.startswith("mods/") and name.endswith(".pw.toml")
        if bool(x.get("metafile", False)) != is_mod:
            raise ValueError("Incorrect metafile flag: " + name)
        if is_mod:
            mod = toml(name)
            dl = mod.get("download", {})
            fmt = dl.get("hash-format", "")
            fn = mod.get("filename", "")
            if not mod.get("name") or not fn.endswith(".jar") or Path(fn).name != fn:
                raise ValueError("Invalid mod metadata: " + name)
            if not dl.get("url", "").startswith("https://") or fmt not in ("sha1", "sha512"):
                raise ValueError("Invalid download URL or hash format: " + name)
            if len(dl.get("hash", "")) != {"sha1": 40, "sha512": 128}[fmt]:
                raise ValueError("Invalid download checksum: " + name)
    for filename in SYNC_FILES:
        if not (ROOT / "packsync" / filename).is_file():
            raise ValueError("Missing updater: " + filename)
    print("Validated", len(entries), "pack files")
    return pack, entries


def sync_to_zip(z, prefix):
    for filename in SYNC_FILES:
        z.write(ROOT / "packsync" / filename, prefix + filename)


def instance(out, pack):
    out.parent.mkdir(parents=True, exist_ok=True)
    versions = pack["versions"]
    mc, neo = versions["minecraft"], versions["neoforge"]
    template = (ROOT / "instance-template/instance.cfg").read_text(encoding="utf-8")
    cfg = template.replace("@@NAME@@", pack["name"]).replace(
        "@@PRELAUNCH@@", 'cmd /c "$INST_DIR/sync.cmd"')
    mmc = {"formatVersion": 1, "components": [
        {"uid": "net.minecraft", "version": mc, "cachedName": "Minecraft",
         "cachedVersion": mc, "important": True,
         "cachedRequires": [{"uid": "java-runtime-delta", "equals": "21", "suggests": "21.0.1"}]},
        {"uid": "net.neoforged", "version": neo, "cachedName": "NeoForge",
         "cachedVersion": neo, "cachedVolatile": True, "important": True,
         "cachedRequires": [{"uid": "net.minecraft", "equals": mc}]}]}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("instance.cfg", cfg)
        z.writestr("mmc-pack.json", json.dumps(mmc, indent=2))
        sync_to_zip(z, "minecraft/packsync/")
        z.write(ROOT / "packsync/sync.cmd", "sync.cmd")
    print("Built", out)


def mrpack(out, pack, index):
    entries, overrides = [], []
    for x in index:
        path = x["file"]
        if not x.get("metafile"):
            overrides.append(path)
            continue
        mod = toml(path)
        dl = mod["download"]
        side = mod.get("side", "both")
        if side not in ("both", "client", "server"):
            raise ValueError("Invalid side: " + path)
        entries.append({"path": "mods/" + mod["filename"],
                        "hashes": {dl["hash-format"]: dl["hash"]},
                        "downloads": [dl["url"]],
                        "env": {"client": "unsupported" if side == "server" else "required",
                                "server": "unsupported" if side == "client" else "required"}})
    manifest = {"formatVersion": 1, "game": "minecraft", "versionId": pack["version"],
                "name": pack["name"], "summary": pack.get("description", ""),
                "files": entries, "dependencies": pack["versions"]}
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modrinth.index.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        for rel in overrides:
            z.write(ROOT / rel, "overrides/" + rel)
        sync_to_zip(z, "overrides/packsync/")
    print("Built", out)


def site(out, pack, entries):
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for rel in ["pack.toml", "index.toml"] + [e["file"] for e in entries]:
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, target)
    for name in SYNC_FILES:
        target = out / "packsync" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "packsync" / name, target)
    (out / ".nojekyll").touch()
    instance(out / "latest/instance.zip", pack)
    mrpack(out / "latest/pack.mrpack", pack, entries)
    print("Pages payload ready:", out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["refresh", "validate", "site", "instance", "mrpack"])
    p.add_argument("--out", default=None)
    args = p.parse_args()
    if args.command == "refresh":
        refresh()
        return
    pack, index = validate()
    if args.command == "site":
        site(ROOT / (args.out or "site"), pack, index)
    elif args.command == "instance":
        instance(ROOT / (args.out or "dist/instance.zip"), pack)
    elif args.command == "mrpack":
        mrpack(ROOT / (args.out or "dist/pack.mrpack"), pack, index)


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, ValueError, KeyError, OSError, tomllib.TOMLDecodeError) as err:
        print("ERROR:", err, file=sys.stderr)
        sys.exit(1)
