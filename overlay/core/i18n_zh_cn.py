# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import re
import tkinter as tk
from tkinter import ttk, messagebox

_ENABLED = os.environ.get("DLSS5_AUTOPILOT_LANG", "zh_CN").lower() not in {"en", "en_us", "english", "0", "false", "off"}
_INSTALLED = False

EXACT = {
    # Primary navigation / page names
    "start": "开始",
    "find your games": "查找游戏",
    "games": "游戏",
    "your library": "游戏库",
    "install": "安装",
    "settings and go": "设置并安装",
    "video and youtube": "视频和 YouTube",
    "any file or a youtube link": "任意视频文件或 YouTube 链接",
    "rtx remix": "RTX Remix",
    "path-traced classics": "路径追踪经典游戏",
    "dlss 5 for the games you have": "让你已有的游戏用上 DLSS 5",
    "dlss5 for the games you have": "让你已有的游戏用上 DLSS 5",
    "neural rendering, one click": "神经渲染，一键完成",

    # Main-page prose
    "[ scan games ] (bottom right) finds the games your stores know about and the usual game folders, reads each executable for its architecture and renderer, and picks the route that fits it. for one game, use [ choose folder ] on the games page. video and rtx remix are on the left.":
        "右下角的 [ 扫描游戏 ] 会查找游戏平台已知的游戏和常用游戏目录，读取每个可执行文件的架构与渲染 API，并自动选择适合的安装路线。只处理单个游戏时，可在“游戏”页面使用 [ 选择文件夹 ]。视频和 RTX Remix 功能在左侧。",
    "!! before you get your hopes up": "!! 使用前先说明",
    "dlss5 works reliably on 64-bit directx 11/12. directx 9, opengl, vulkan and every 32-bit game go through extra translation, a layer or a helper process, and the dlss feature fails to create there far more often. directx 10 goes through the feeder only (build 0.13.1 and later). each game is labelled - do not expect the long shots to work.\n\nnever use any of this online: anti-cheat flags reshade add-ons.":
        "DLSS 5 在 64 位 DirectX 11/12 游戏中最可靠。DirectX 9、OpenGL、Vulkan 以及所有 32 位游戏都需要额外的转换层、兼容层或辅助进程，因此 DLSS 功能更容易初始化失败。DirectX 10 仅通过 Feeder 路线支持（0.13.1 及以上版本）。程序会给每个游戏标注兼容情况，不要对高风险路线抱过高预期。\n\n不要在联网游戏中使用这些功能：反作弊系统可能会将 ReShade 插件判定为异常。",

    # Common controls
    "all": "全部",
    "every architecture": "所有架构",
    "64-bit only": "仅 64 位",
    "32-bit only (experimental)": "仅 32 位（实验性）",
    "stable - newest release": "稳定版 - 最新正式版本",
    "newest pre-release": "最新预发布版本",
    "keep the game's own": "保留游戏自带版本",
    "scan": "扫描", "scan again": "重新扫描", "rescan": "重新扫描",
    "scan games": "扫描游戏", "[ scan games ]": "[ 扫描游戏 ]",
    "choose folder": "选择文件夹", "[ choose folder ]": "[ 选择文件夹 ]",
    "browse": "浏览", "browse...": "浏览...", "back": "返回", "next": "下一步",
    "continue": "继续", "cancel": "取消", "close": "关闭", "done": "完成",
    "ok": "确定", "yes": "是", "no": "否", "save": "保存", "apply": "应用",
    "refresh": "刷新", "retry": "重试", "open": "打开", "remove": "移除",
    "uninstall": "卸载", "restore": "恢复", "reset": "重置", "copy": "复制",
    "copy report": "复制报告", "open folder": "打开文件夹", "open game folder": "打开游戏目录",
    "launch game": "启动游戏", "run diagnosis": "运行诊断", "diagnose": "诊断",
    "install now": "立即安装", "install / update": "安装 / 更新",
    "ready": "就绪",

    # Sidebar links / update UI
    "[ open log file ]": "[ 打开日志文件 ]",
    "[ report a bug ]": "[ 报告问题 ]",
    "[ suggest a feature ]": "[ 建议新功能 ]",
    "[ how it works ]": "[ 工作原理 ]",
    "[ update now ]": "[ 立即更新 ]",
    "[ restart into it ]": "[ 重启并使用新版 ]",

    # Status / fields
    "game": "游戏", "games found": "已找到游戏", "no games found": "未找到游戏",
    "selected game": "已选择游戏", "game folder": "游戏目录", "executable": "可执行文件",
    "architecture": "架构", "renderer": "渲染 API", "status": "状态",
    "installed": "已安装", "not installed": "未安装", "compatible": "兼容",
    "incompatible": "不兼容", "unknown": "未知",
    "route": "安装路线", "recommended": "推荐", "automatic": "自动", "manual": "手动",
    "native": "原生", "native dlss": "原生 DLSS", "driver": "驱动", "nvidia driver": "NVIDIA 驱动",
    "graphics api": "图形 API", "quality": "质量", "performance": "性能", "balanced": "平衡",
    "ultra performance": "超级性能", "frame generation": "帧生成", "ray reconstruction": "光线重建",
    "preset": "预设", "version": "版本", "latest": "最新", "default": "默认",
    "experimental": "实验性", "advanced": "高级", "settings": "设置",
    "checking...": "正在检查...", "scanning...": "正在扫描...", "downloading...": "正在下载...",
    "installing...": "正在安装...", "verifying...": "正在验证...", "working...": "处理中...",
    "please wait...": "请稍候...", "complete": "完成", "failed": "失败",
    "warning": "警告", "error": "错误", "success": "成功",
    "before / after": "前 / 后对比", "report": "报告", "share report": "分享报告",
    "community": "社区", "comparison": "对比", "before": "之前", "after": "之后",
    "video": "视频", "youtube": "YouTube", "select a video": "选择视频",
    "video file": "视频文件", "youtube link": "YouTube 链接", "play": "播放", "stop": "停止",
    "Are you sure?": "确定吗？", "Confirm": "确认", "Information": "提示", "Warning": "警告", "Error": "错误",
}

PHRASES = [
    # High-value phrases used in composed/dynamic strings. Keep technical names intact.
    ("new DLSS5 driver detected", "检测到新的 DLSS5 驱动"),
    ("available for download", "可下载"),
    ("downloaded and verified", "已下载并验证"),
    ("restarting into the new build", "正在重启并切换到新版本"),
    ("downloading update", "正在下载更新"),
    ("scan games", "扫描游戏"),
    ("choose folder", "选择文件夹"),
    ("your library", "游戏库"),
    ("settings and go", "设置并安装"),
    ("find your games", "查找游戏"),
    ("any file or a youtube link", "任意视频文件或 YouTube 链接"),
    ("path-traced classics", "路径追踪经典游戏"),
    ("open log file", "打开日志文件"),
    ("report a bug", "报告问题"),
    ("suggest a feature", "建议新功能"),
    ("how it works", "工作原理"),
    ("update now", "立即更新"),
    ("checking compatibility", "正在检查兼容性"), ("compatibility check", "兼容性检查"),
    ("game folder", "游戏目录"), ("selected game", "已选择游戏"), ("games found", "已找到游戏"),
    ("choose a game", "选择游戏"), ("select folder", "选择文件夹"),
    ("select file", "选择文件"), ("scan for games", "扫描游戏"), ("scan again", "重新扫描"),
    ("recommended route", "推荐路线"), ("install route", "安装路线"), ("current route", "当前路线"),
    ("NVIDIA driver", "NVIDIA 驱动"), ("driver version", "驱动版本"), ("graphics card", "显卡"),
    ("graphics API", "图形 API"), ("frame generation", "帧生成"), ("ray reconstruction", "光线重建"),
    ("newest release", "最新正式版本"), ("pre-release", "预发布版本"),
    ("download failed", "下载失败"), ("install failed", "安装失败"), ("installation failed", "安装失败"),
    ("download complete", "下载完成"), ("installation complete", "安装完成"),
    ("downloading", "正在下载"), ("installing", "正在安装"), ("verifying", "正在验证"),
    ("scanning", "正在扫描"), ("checking", "正在检查"), ("diagnosis", "诊断"),
    ("warning", "警告"), ("error", "错误"), ("success", "成功"), ("failed", "失败"),
    ("compatible", "兼容"), ("incompatible", "不兼容"), ("experimental", "实验性"),
    ("recommended", "推荐"), ("automatic", "自动"), ("advanced", "高级"), ("settings", "设置"),
]


def tr(value):
    if not _ENABLED or not isinstance(value, str) or not value:
        return value
    if value in EXACT:
        return EXACT[value]
    low = value.lower()
    for k, v in EXACT.items():
        if k.lower() == low:
            return v
    out = value
    for en, zh in PHRASES:
        out = re.sub(re.escape(en), zh, out, flags=re.I)
    return out


def _tx_kwargs(kwargs):
    d = dict(kwargs or {})
    for key in ("text", "label", "title", "message"):
        if key in d:
            d[key] = tr(d[key])
    if "values" in d and isinstance(d["values"], (tuple, list)):
        d["values"] = type(d["values"])(tr(x) for x in d["values"])
    return d


def _patch(cls, name, factory):
    old = getattr(cls, name, None)
    if not callable(old) or getattr(old, "_dlss5_zh_patched", False):
        return
    new = factory(old)
    new._dlss5_zh_patched = True
    setattr(cls, name, new)


def _wrap_init(old):
    def wrapped(self, *args, **kw):
        translated_args = tuple(_tx_kwargs(arg) if isinstance(arg, dict) else arg for arg in args)
        return old(self, *translated_args, **_tx_kwargs(kw))
    return wrapped


def _wrap_config(old):
    def wrapped(self, cnf=None, **kw):
        if isinstance(cnf, dict): cnf = _tx_kwargs(cnf)
        if cnf is None: return old(self, **_tx_kwargs(kw))
        return old(self, cnf, **_tx_kwargs(kw))
    return wrapped


def _wrap_menu(old):
    def wrapped(self, *args, **kw):
        return old(self, *args, **_tx_kwargs(kw))
    return wrapped


def _wrap_title(old):
    def wrapped(self, string=None):
        return old(self) if string is None else old(self, tr(string))
    return wrapped


def _wrap_var(old):
    def wrapped(self, value):
        return old(self, tr(value) if isinstance(value, str) else value)
    return wrapped


def _wrap_tree_heading(old):
    def wrapped(self, column, option=None, **kw):
        if "text" in kw:
            kw["text"] = tr(kw["text"])
        return old(self, column, option, **kw)
    return wrapped


def install():
    global _INSTALLED
    if _INSTALLED or not _ENABLED:
        return
    _INSTALLED = True
    for cls in (tk.Label, tk.Button, tk.Checkbutton, tk.Radiobutton, tk.LabelFrame, tk.Message, tk.Entry, tk.Spinbox, tk.Menubutton, tk.Scale):
        _patch(cls, "__init__", _wrap_init)
        _patch(cls, "configure", _wrap_config)
        try: cls.config = cls.configure
        except Exception: pass
    _patch(ttk.Widget, "__init__", _wrap_init)
    _patch(ttk.Widget, "configure", _wrap_config)
    try: ttk.Widget.config = ttk.Widget.configure
    except Exception: pass
    _patch(ttk.Treeview, "heading", _wrap_tree_heading)
    _patch(tk.Menu, "add_command", _wrap_menu)
    _patch(tk.Menu, "add_checkbutton", _wrap_menu)
    _patch(tk.Menu, "add_radiobutton", _wrap_menu)
    _patch(tk.Wm, "title", _wrap_title)
    _patch(tk.Variable, "set", _wrap_var)
    for name in ("showinfo", "showwarning", "showerror", "askquestion", "askokcancel", "askyesno", "askyesnocancel", "askretrycancel"):
        old = getattr(messagebox, name, None)
        if not callable(old): continue
        def make(fn):
            def wrapped(title=None, message=None, **options):
                return fn(tr(title) if title is not None else title, tr(message) if message is not None else message, **_tx_kwargs(options))
            return wrapped
        setattr(messagebox, name, make(old))
