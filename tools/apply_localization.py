from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "overlay"


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
    # Collapse accidental duplicate injections, then keep exactly one copy.
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

    # Remove the old localization helper block no matter how many times an
    # earlier non-idempotent version appended it.
    s = re.sub(
        r"\n*# Chinese edition preference\nDEFAULT_LANGUAGE = \"zh-CN\"\n?",
        "\n",
        s,
    )

    # ReShade supports native localization through [OVERLAY] Language.
    # Set it as a default in every helper that creates/updates ReShade.ini,
    # so existing user choices are preserved while fresh installs use zh-CN.
    needle = 'ini = Ini.load(p)'
    language_line = '    ini.set_default("OVERLAY", "Language", "zh-CN")'
    out = []
    lines = s.splitlines()
    for i, line in enumerate(lines):
        out.append(line)
        if line.strip() == needle:
            # Do not add a duplicate if the next functional line already sets it.
            lookahead = "\n".join(lines[i + 1:i + 5])
            if 'set_default("OVERLAY", "Language", "zh-CN")' not in lookahead:
                indent = line[: len(line) - len(line.lstrip())]
                out.append(indent + 'ini.set_default("OVERLAY", "Language", "zh-CN")')
    s = "\n".join(out) + ("\n" if s.endswith("\n") else "")
    p.write_text(s, encoding="utf-8")


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


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply_localization.py <upstream-tree>")
    dst = Path(sys.argv[1]).resolve()
    copy_overlay(dst)
    patch_gui(dst)
    patch_reshade(dst)
    verify(dst)


if __name__ == "__main__":
    main()
