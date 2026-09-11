from __future__ import annotations

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
    if marker in s:
        return
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
    # ReShade has native zh-CN localization. Ensure generated configs request it.
    if "Language=zh-CN" not in s:
        # Add a helper constant without touching functional code paths. Future overlay-specific
        # writing can import/use this; current ReShade versions also follow Windows UI language.
        s += "\n\n# Chinese edition preference\nDEFAULT_LANGUAGE = \"zh-CN\"\n"
    p.write_text(s, encoding="utf-8")


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply_localization.py <upstream-tree>")
    dst = Path(sys.argv[1]).resolve()
    copy_overlay(dst)
    patch_gui(dst)
    patch_reshade(dst)


if __name__ == "__main__":
    main()
