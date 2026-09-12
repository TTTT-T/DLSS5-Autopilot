from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "overlay"
OPTISCALER_ZH_API = "https://api.github.com/repos/TTTT-T/DLSS5-Autopilot/releases/tags/optiscaler-zh-CN-latest"


def copy_overlay(dst: Path):
    for src in OVERLAY.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(OVERLAY)
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)


def patch_gui(dst: Path):
    p = dst / "core" / "gui.py"
    s = p.read_text(encoding="utf-8")
    marker = "from .i18n_zh_cn import install as _install_zh_cn; _install_zh_cn()"
    s = re.sub(r"(?:\n\s*" + re.escape(marker) + r")+", "", s)
    needle = "from tkinter import filedialog, messagebox, ttk"
    if needle not in s:
        raise RuntimeError("upstream gui.py changed: tkinter import marker not found")
    s = s.replace(needle, needle + "\n\n" + marker, 1)
    p.write_text(s, encoding="utf-8")


def patch_reshade(dst: Path):
    p = dst / "core" / "reshade_ini.py"
    if not p.exists():
        return
    s = p.read_text(encoding="utf-8")
    s = re.sub(
        r"\n*# Chinese edition preference\nDEFAULT_LANGUAGE = \"zh-CN\"\n?",
        "\n",
        s,
    )
    needle = 'ini = Ini.load(p)'
    out = []
    lines = s.splitlines()
    for i, line in enumerate(lines):
        out.append(line)
        if line.strip() == needle:
            lookahead = "\n".join(lines[i + 1:i + 5])
            if 'set_default("OVERLAY", "Language", "zh-CN")' not in lookahead:
                indent = line[: len(line) - len(line.lstrip())]
                out.append(indent + 'ini.set_default("OVERLAY", "Language", "zh-CN")')
    s = "\n".join(out) + ("\n" if s.endswith("\n") else "")
    p.write_text(s, encoding="utf-8")


def patch_optiscaler(dst: Path):
    p = dst / "core" / "optiscaler.py"
    if not p.exists():
        return
    s = p.read_text(encoding="utf-8")
    pattern = r'^API\s*=\s*"https://api\.github\.com/repos/[^\"]+/releases(?:/latest|/tags/[^\"]+)"\s*$'
    repl = f'API = "{OPTISCALER_ZH_API}"'
    s2, n = re.subn(pattern, repl, s, count=1, flags=re.M)
    if n != 1:
        raise RuntimeError("upstream optiscaler.py changed: default API marker not found")

    old = '''    rel = sources._json(API)\n    for a in rel.get("assets", []):\n        if a["name"].lower().endswith((".zip", ".7z")):\n            return rel.get("tag_name", "?"), a["browser_download_url"]\n    raise RuntimeError("The OptiScaler DLSS-NR release has no .zip asset.")'''
    new = '''    rel = sources._json(API)\n    assets = [a for a in rel.get("assets", [])\n              if a.get("name", "").lower().endswith((".zip", ".7z"))\n              and "source" not in a.get("name", "").lower()]\n    assets.sort(key=lambda a: a.get("updated_at") or a.get("created_at") or "",\n                reverse=True)\n    for a in assets:\n        tag = rel.get("tag_name", "?")\n        # Rolling releases replace the asset under the same tag/name. Include\n        # GitHub's asset id in the cache key so an updated runtime cannot reuse\n        # a stale archive already downloaded by an older build.\n        if "TTTT-T/DLSS5-Autopilot" in API and a.get("id"):\n            tag = f"{tag}-{a['id']}"\n        return tag, a["browser_download_url"]\n    raise RuntimeError("The OptiScaler DLSS-NR release has no runtime .zip/.7z asset.")'''
    if old not in s2:
        if 'and "source" not in a.get("name", "").lower()' not in s2:
            raise RuntimeError("upstream optiscaler.py changed: default release resolver marker not found")
    else:
        s2 = s2.replace(old, new, 1)

    p.write_text(s2, encoding="utf-8")


def verify(dst: Path):
    gui = (dst / "core" / "gui.py").read_text(encoding="utf-8")
    marker = "from .i18n_zh_cn import install as _install_zh_cn; _install_zh_cn()"
    if gui.count(marker) != 1:
        raise RuntimeError(f"expected exactly one zh-CN GUI hook, found {gui.count(marker)}")

    i18n = (dst / "core" / "i18n_zh_cn.py").read_text(encoding="utf-8")
    if "def wrapped(self, *args, **kw):" not in i18n:
        raise RuntimeError("zh-CN Tkinter wrapper lost variadic positional-argument support")

    reshade = (dst / "core" / "reshade_ini.py").read_text(encoding="utf-8")
    if "DEFAULT_LANGUAGE" in reshade:
        raise RuntimeError("legacy duplicate ReShade language constant still present")
    if 'set_default("OVERLAY", "Language", "zh-CN")' not in reshade:
        raise RuntimeError("ReShade zh-CN language default was not applied")

    opti = (dst / "core" / "optiscaler.py").read_text(encoding="utf-8")
    if f'API = "{OPTISCALER_ZH_API}"' not in opti:
        raise RuntimeError("default OptiScaler source is not the localized rolling release")
    if 'and "source" not in a.get("name", "").lower()' not in opti:
        raise RuntimeError("localized OptiScaler resolver can still select source archives")
    if "a.get(\"id\")" not in opti:
        raise RuntimeError("localized OptiScaler resolver is missing cache busting")


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply_localization.py <upstream-tree>")
    dst = Path(sys.argv[1]).resolve()
    copy_overlay(dst)
    patch_gui(dst)
    patch_reshade(dst)
    patch_optiscaler(dst)
    verify(dst)


if __name__ == "__main__":
    main()
