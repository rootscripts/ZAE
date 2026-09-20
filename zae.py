#!/usr/bin/env python3
import sys, os, time, subprocess, json, re, platform, math
import urllib.request, urllib.error

_W = platform.system() == "Windows"

if _W:
    import ssl
    _ctx = ssl.create_default_context()
    try:
        import certifi
        _ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        pass
    _ctx.check_hostname = False
    _ctx.verify_mode = ssl.CERT_NONE
    _old_urlopen = urllib.request.urlopen
    def _urlopen(*a, **kw):
        kw.setdefault("context", _ctx)
        return _old_urlopen(*a, **kw)
    urllib.request.urlopen = _urlopen

from PyQt6.QtWidgets import QApplication, QPlainTextEdit
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QEventLoop
from PyQt6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QFontDatabase, QKeyEvent

_D = os.path.expanduser("~/.config/zae")
_FD = os.path.join(_D, "fonts")
_FP = os.path.join(_FD, "PxPlus_IBM_VGA_8x16.ttf")
_KF = os.path.join(_D, "groq_key")
os.makedirs(_FD, exist_ok=True)

_TC = "#b0b0b0"
_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36 ZAE/3.0"

_FM = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "llama-3.2-3b-preview",
    "llama-3.2-1b-preview",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "qwen-2.5-32b",
    "qwen-2.5-coder-32b",
    "qwen/qwen3-32b",
    "qwen/qwen3.8-27b",
    "deepseek-r1-distill-llama-70b",
    "deepseek-r1-distill-qwen-32b",
    "mistral-saba-24b",
    "mistral-small-24b-instruct-2501",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
]

_REASON_MODELS = ("gpt-oss", "qwen3", "qwen-2.5", "deepseek", "r1")

_SKIP = ("whisper", "guard", "embed", "vision", "tool", "tts", "image",
         "compound", "orpheus", "safeguard", "allam")

_mi = 0

_CMD_COLORS = {
    "0": "#000000", "1": "#000080", "2": "#008000", "3": "#008080",
    "4": "#800000", "5": "#800080", "6": "#808000", "7": "#c0c0c0",
    "8": "#808080", "9": "#5555ff", "a": "#55ff55", "b": "#55ffff",
    "c": "#ff5555", "d": "#ff55ff", "e": "#ffff55", "f": "#ffffff",
}

_ANSI_FG = {
    30: "#000000", 31: "#ff5555", 32: "#50fa7b", 33: "#f1fa8c",
    34: "#bd93f9", 35: "#ff79c6", 36: "#8be9fd", 37: "#f8f8f2",
    39: _TC,
    90: "#6272a4", 91: "#ff6e6e", 92: "#77dd77", 93: "#ffffa5",
    94: "#d6acff", 95: "#ff92df", 96: "#a4ffff", 97: "#ffffff",
}

_ANSI_BG = {
    40: "#000000", 41: "#800000", 42: "#008000", 43: "#808000",
    44: "#000080", 45: "#800080", 46: "#008080", 47: "#c0c0c0",
    49: "#000000",
    100: "#6272a4", 101: "#ff6e6e", 102: "#77dd77", 103: "#ffffa5",
    104: "#d6acff", 105: "#ff92df", 106: "#a4ffff", 107: "#ffffff",
}

def _compress_for_history(txt):
    if not txt or not txt.strip():
        return "[ok]"
    lines = txt.strip().splitlines()
    if len(lines) <= 5:
        return txt.strip()
    return "\n".join(lines[:2] + ["[...output truncated...]"] + lines[-2:])

def _256_to_hex(n):
    if n < 8:
        return ["#000000", "#cc0000", "#4e9a06", "#c4a000", "#3465a4", "#75507b", "#06989a", "#d3d7cf"][n]
    elif n < 16:
        return ["#555753", "#ef2929", "#8ae234", "#fce94f", "#729fcf", "#ad7fa8", "#34e2e2", "#eeeeec"][n - 8]
    elif n < 232:
        n -= 16
        r = (n // 36)
        g = (n % 36) // 6
        b = n % 6
        r = 0 if r == 0 else 55 + r * 40
        g = 0 if g == 0 else 55 + g * 40
        b = 0 if b == 0 else 55 + b * 40
        return f"#{r:02x}{g:02x}{b:02x}"
    elif n < 256:
        gray = 8 + (n - 232) * 10
        return f"#{gray:02x}{gray:02x}{gray:02x}"
    return _TC

def tags_to_ansi(txt):
    if not txt:
        return ""
    def _sub_color(m):
        tag = m.group(1).lower()
        val = m.group(2).strip().lower()
        if tag == "color":
            if val == "reset":
                return "\033[0m"
            if val.startswith("#"):
                h = val[1:]
                if len(h) == 3:
                    h = "".join(c * 2 for c in h)
                if len(h) == 6:
                    try:
                        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
                        return f"\033[38;2;{r};{g};{b}m"
                    except ValueError:
                        pass
        elif tag == "bgcolor":
            if val == "reset":
                return "\033[49m"
            if val.startswith("#"):
                h = val[1:]
                if len(h) == 3:
                    h = "".join(c * 2 for c in h)
                if len(h) == 6:
                    try:
                        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
                        return f"\033[48;2;{r};{g};{b}m"
                    except ValueError:
                        pass
        return m.group(0)

    res = re.sub(r'<{1,2}(color|bgcolor):([^<>]+)>{1,2}', _sub_color, txt, flags=re.IGNORECASE)
    res = re.sub(r'<{1,2}clear:zae_term>{1,2}', '\033[2J\033[H', res, flags=re.IGNORECASE)
    return res

def _lk():
    e = os.environ.get("GROQ_API_KEY", "").strip()
    if e: return e
    if os.path.exists(_KF):
        with open(_KF, "r") as f:
            v = f.read().strip()
            if v: return v
    return ""

def _gm(k):
    if not k: return list(_FM)
    try:
        r = urllib.request.Request("https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {k}", "User-Agent": _UA})
        with urllib.request.urlopen(r, timeout=4) as resp:
            d = json.loads(resp.read().decode())
            live = [m["id"] for m in d.get("data", [])
                    if not any(x in m["id"] for x in _SKIP)]
            if live:
                p = [m for m in _FM if m in live] + [m for m in live if m not in _FM]
                return p
    except Exception:
        pass
    return list(_FM)

def _ef():
    if not os.path.exists(_FP) or os.path.getsize(_FP) < 1000:
        for u in [
            "https://raw.githubusercontent.com/WheeledCord/tbwm/master/PxPlus_IBM_VGA_8x16.ttf",
            "https://raw.githubusercontent.com/industry-advance/industry-advance/master/Fonts/Px437_IBM_BIOS.ttf"
        ]:
            try:
                rq = urllib.request.Request(u, headers={"User-Agent": _UA})
                with urllib.request.urlopen(rq, timeout=5) as rsp:
                    if rsp.status == 200:
                        d = rsp.read()
                        if len(d) > 1000:
                            with open(_FP, "wb") as f: f.write(d)
                            break
            except Exception:
                pass
    if os.path.exists(_FP):
        try:
            fid = QFontDatabase.addApplicationFont(_FP)
            if fid != -1:
                fams = QFontDatabase.applicationFontFamilies(fid)
                if fams: return fams[0]
        except Exception:
            pass
    return None

def _gf(sz=12):
    f = QFont()
    f.setStyleHint(QFont.StyleHint.Monospace)
    f.setFixedPitch(True)
    f.setFamilies(["PxPlus IBM VGA 8x16", "Px437 IBM BIOS", "IBM Plex Mono",
                    "JetBrains Mono", "Consolas", "Courier New", "monospace"])
    f.setPointSize(sz)
    return f

_STRIP_PATTERNS = [
    re.compile(r"^```[\w]*\n?", re.MULTILINE),
    re.compile(r"\n?```$", re.MULTILINE),
    re.compile(r"^(Here is|Here's|Sure|I'll|I will|I can|I'm|Okay|OK|Let me|Of course|Certainly)[^\n]*\n?", re.IGNORECASE),
    re.compile(r"^(The output|This would|This will|This shows|Note:|Note that|As you|In this)[^\n]*\n?", re.IGNORECASE),
    re.compile(r"^\s*\*\*[^\n]*\*\*\s*\n?"),
]

def _clean(txt):
    for p in _STRIP_PATTERNS:
        txt = p.sub("", txt)
    txt = txt.replace("```bash", "").replace("```text", "").replace("```", "")
    txt = txt.strip("\n")
    return txt


_PLATFORMS = {
    "linux":   {"os": "Arch Linux x86_64", "cd": "/root"},
    "windows": {"os": "Windows 11 Pro 23H2", "cd": r"C:\Users\root"},
    "macos":   {"os": "macOS Sonoma 14.5", "cd": "/Users/root"},
}


class _St:
    def __init__(self):
        self.plat = "linux"
        self.os = "Arch Linux x86_64"
        self.hn = "archiso"
        self.u = "root"
        self.cd = "/root"
        self.shell = "bash"
        self.fs = {}
        self.dirs = set()
        self._dirstack = []
        self._initial_plat = "linux"

    def switch(self, plat):
        p = _PLATFORMS.get(plat, _PLATFORMS["linux"])
        self.plat = plat
        self.os = p["os"]
        self.cd = p["cd"]
        self.hn = "archiso" if plat == "linux" else ("DESKTOP-ZAE" if plat == "windows" else "zae-mac")
        self.shell = {"linux": "bash", "windows": "cmd", "macos": "zsh"}.get(plat, "bash")
        self._initial_plat = plat
        self.fs = {}
        self.dirs = set()
        self._dirstack = []

    def switch_custom(self, os_name):
        self.os = os_name
        lo = os_name.lower()
        if "windows" in lo or "win" in lo:
            self.plat = "windows"
            self.shell = "cmd"
            self.cd = r"C:\Users\root"
            self.hn = "DESKTOP-ZAE"
        elif "mac" in lo or "darwin" in lo:
            self.plat = "macos"
            self.shell = "zsh"
            self.cd = "/Users/root"
            self.hn = "zae-mac"
        elif "ubuntu" in lo:
            self.plat = "linux"
            self.shell = "bash"
            self.cd = "/root"
            self.hn = "ubuntu"
        elif "fedora" in lo:
            self.plat = "linux"
            self.shell = "bash"
            self.cd = "/root"
            self.hn = "fedora"
        elif "debian" in lo:
            self.plat = "linux"
            self.shell = "bash"
            self.cd = "/root"
            self.hn = "debian"
        else:
            self.plat = "linux"
            self.shell = "bash"
            self.cd = "/root"
            self.hn = re.sub(r'[^a-zA-Z0-9]', '', os_name.split()[0].lower())[:12] or "zae"
        self._initial_plat = self.plat
        self.fs = {}
        self.dirs = set()
        self._dirstack = []

    def prompt(self):
        if self.plat == "windows":
            return self.cd.rstrip("\\") + ">" if self.cd != "C:\\" else "C:\\>"
        pc = "~" if self.cd in ("/root", "/Users/root") else self.cd
        return f"{self.u}@{self.hn} {pc} # "

    def _abs_path(self, p):
        p = p.strip().strip('"').strip("'")
        if self.plat == "windows":
            p = p.replace("/", "\\")
            if re.match(r'^[a-zA-Z]:', p):
                return p
            if p.startswith("\\"):
                drive = self.cd[:2].upper() if len(self.cd) >= 2 and self.cd[1] == ":" else "C:"
                return drive + p
            base = self.cd.rstrip("\\")
            return (base + "\\" + p) if base else ("C:\\" + p)
        else:
            if p.startswith("~"):
                h = "/root" if self.u == "root" else f"/home/{self.u}"
                p = h + p[1:]
            if p.startswith("/"):
                return p
            base = self.cd.rstrip("/")
            return (base + "/" + p) if base else ("/" + p)

    def _resolve_cd(self, tgt):
        tgt = tgt.strip().strip('"').strip("'")
        if not tgt:
            if self.plat == "windows":
                return
            else:
                self.cd = "/root" if self.u == "root" else f"/home/{self.u}"
                return

        if tgt in ("/?", "--help", "-h"):
            return

        if self.plat == "windows":
            if tgt.lower().startswith("/d "):
                tgt = tgt[3:].strip().strip('"').strip("'")
            tgt = tgt.replace("/", "\\")
            if tgt == ".":
                return

            if re.match(r'^[a-zA-Z]:', tgt):
                drive = tgt[:2].upper()
                rest = tgt[2:].lstrip("\\")
                if not rest:
                    self.cd = drive + "\\"
                    return
                parts = [p for p in rest.split("\\") if p and p != "."]
                resolved = []
                for p in parts:
                    if p == "..":
                        if resolved: resolved.pop()
                    else:
                        resolved.append(p)
                self.cd = drive + "\\" + "\\".join(resolved) if resolved else drive + "\\"
                return
            elif tgt.startswith("\\"):
                drive = self.cd[:2].upper() if len(self.cd) >= 2 and self.cd[1] == ":" else "C:"
                parts = [p for p in tgt.lstrip("\\").split("\\") if p and p != "."]
                resolved = []
                for p in parts:
                    if p == "..":
                        if resolved: resolved.pop()
                    else:
                        resolved.append(p)
                self.cd = drive + "\\" + "\\".join(resolved) if resolved else drive + "\\"
                return
            else:
                curr = self.cd
                drive = curr[:2].upper() if len(curr) >= 2 and curr[1] == ":" else "C:"
                body = curr[2:].strip("\\")
                parts = [p for p in body.split("\\") if p]
                for seg in tgt.split("\\"):
                    seg = seg.strip()
                    if not seg or seg == ".":
                        continue
                    elif seg == "..":
                        if parts: parts.pop()
                    else:
                        parts.append(seg)
                self.cd = drive + "\\" + "\\".join(parts) if parts else drive + "\\"
                return
        else:
            if tgt == "~":
                self.cd = "/root" if self.u == "root" else f"/home/{self.u}"
                return
            if tgt.startswith("~/"):
                h = "/root" if self.u == "root" else f"/home/{self.u}"
                tgt = h + tgt[1:]
            if tgt.startswith("/"):
                parts = [p for p in tgt.split("/") if p and p != "."]
                resolved = []
                for p in parts:
                    if p == "..":
                        if resolved: resolved.pop()
                    else:
                        resolved.append(p)
                self.cd = "/" + "/".join(resolved) if resolved else "/"
                return
            else:
                parts = [p for p in self.cd.split("/") if p]
                for seg in tgt.split("/"):
                    seg = seg.strip()
                    if not seg or seg == ".":
                        continue
                    elif seg == "..":
                        if parts: parts.pop()
                    else:
                        parts.append(seg)
                self.cd = "/" + "/".join(parts) if parts else "/"
                return

    def _add_file(self, path, content=""):
        ap = self._abs_path(path)
        if "os-release" in ap:
            m = re.search(r'(?:PRETTY_NAME|NAME)\s*=\s*["\'"]?([^"\']+)["\'"]?', content)
            if m: self.os = m.group(1).strip()
        self.fs[ap] = content

    def _add_dir(self, path):
        ap = self._abs_path(path)
        self.dirs.add(ap)

    def _remove_path(self, path):
        ap = self._abs_path(path)
        if ap in self.fs:
            del self.fs[ap]
        if ap in self.dirs:
            self.dirs.discard(ap)
        prefix = ap.rstrip("\\/") + ("\\" if self.plat == "windows" else "/")
        for k in list(self.fs.keys()):
            if k.startswith(prefix):
                del self.fs[k]
        for d in list(self.dirs):
            if d.startswith(prefix):
                self.dirs.discard(d)

    def upd(self, txt):
        t = txt + "\n"

        for m in re.finditer(r'(?:hostnamectl\s+set-hostname|hostname)\s+([a-zA-Z0-9_\-]+)', t):
            self.hn = m.group(1)

        for m in re.finditer(r'cat\s*<<\s*[\'\"]?(\w+)[\'\"]?\s*>\s*(\S+)\n(.*?)\n\1', t, re.DOTALL):
            self._add_file(m.group(2), m.group(3).strip())

        subcmds = re.split(r'[;&|\n]+', txt)
        for sub in subcmds:
            sub = sub.strip()
            if not sub:
                continue

            m_cd = re.match(r'^cd(?:\s+(.+)|(\.\.|\.|\/|\\.*))$', sub, re.IGNORECASE)
            if m_cd:
                tgt = m_cd.group(1) or m_cd.group(2) or ""
                self._resolve_cd(tgt.strip())
                continue

            if re.match(r'^pushd\s+(.+)$', sub, re.IGNORECASE):
                p_tgt = sub[5:].strip().strip('"').strip("'")
                self._dirstack.append(self.cd)
                self._resolve_cd(p_tgt)
                continue

            if re.match(r'^popd$', sub, re.IGNORECASE):
                if self._dirstack:
                    self.cd = self._dirstack.pop()
                continue

            m_mk = re.match(r'^(?:mkdir|md)(?:\s+-[a-zA-Z]+)*\s+(.+)$', sub, re.IGNORECASE)
            if m_mk:
                d_tgt = m_mk.group(1).strip().strip('"').strip("'")
                self._add_dir(d_tgt)
                continue

            m_tch = re.match(r'^touch\s+(.+)$', sub, re.IGNORECASE)
            if m_tch:
                for f_item in m_tch.group(1).split():
                    if not f_item.startswith("-"):
                        self._add_file(f_item.strip('"').strip("'"), "")
                continue

            m_rm = re.match(r'^(?:rm|del|erase|rmdir|rd)(?:\s+-[a-zA-Z]+|\s+/[a-zA-Z]+)*\s+(.+)$', sub, re.IGNORECASE)
            if m_rm:
                r_tgt = m_rm.group(1).strip().strip('"').strip("'")
                self._remove_path(r_tgt)
                continue

            m_red = re.search(r'(?:>>|>)\s*([^\s;&|<>]+)$', sub)
            if m_red:
                out_file = m_red.group(1).strip().strip('"').strip("'")
                m_echo = re.match(r'^echo\s+(.*?)\s*(?:>>|>)', sub, re.IGNORECASE)
                c = m_echo.group(1).strip().strip('\'"') if m_echo else ""
                self._add_file(out_file, c)
                continue

    def hdr(self):
        cf = []
        for k, v in list(self.fs.items())[-15:]:
            preview = f'="{v[:50]}"' if v else ""
            cf.append(f"{k}{preview}")
        df = list(self.dirs)[-10:]
        info = [f"OS={self.os}", f"CWD={self.cd}"]
        if cf: info.append(f"VFS_FILES: {', '.join(cf)}")
        if df: info.append(f"VFS_DIRS: {', '.join(df)}")
        return "[" + " | ".join(info) + "]"


_SYS = r"""Raw TTY/console emulator. Output ONLY exact command stdout/stderr bytes. No markdown, no commentary, no prompt (app draws prompt).

RULES:
1. Valid commands must print realistic output. Silent commands (cd, mkdir, touch, rm, del) = empty output.
2. Short inputs (y/n, 1, 2) continue previous interactive prompts. For input prompts, end with <request>.
3. Stop immediately when realistic output ends. Never loop/repeat lines. Max 25 output lines.
4. Colors: <color:#HEX>, <color:reset>, <bgcolor:#HEX>, <bgcolor:reset>, or ANSI \033[...m. CMD `color 0a`: silent, emit <bgcolor:#000000><color:#55ff55>.

CRITICAL CWD TRACKING: You must accurately track the Current Working Directory across commands. Whenever the directory changes via 'cd', the resulting shell prompt MUST reflect the new absolute path (e.g. 'cd ..' from C:\Users\root must change prompt to 'C:\Users>'). Relative paths and listings MUST match active CWD.

PERSISTENCE: Maintain a persistent virtual filesystem state in memory for the active session. If a file or directory is created with echo, touch, mkdir, or redirected output, it MUST continue to exist in subsequent 'dir', 'ls', and 'type' calls until explicitly deleted. Never reset filesystem state to default during the session. Reflect all files/dirs from [VFS_FILES: ...] and [VFS_DIRS: ...].

FASTFETCH (2 parallel columns side-by-side, art on left, info on right):
Windows 10/11:
<color:#0078d4>████████   ████████<color:reset>   root@DESKTOP-ZAE
<color:#0078d4>████████   ████████<color:reset>   ----------------
<color:#0078d4>████████   ████████<color:reset>   <color:#0078d4>OS<color:reset>: Windows 11 Pro 23H2 x86_64
<color:#0078d4>████████   ████████<color:reset>   <color:#0078d4>Host<color:reset>: Virtual Machine
<color:#0078d4>                   <color:reset>   <color:#0078d4>Kernel<color:reset>: 10.0.22631
<color:#0078d4>████████   ████████<color:reset>   <color:#0078d4>Uptime<color:reset>: 2 mins
<color:#0078d4>████████   ████████<color:reset>   <color:#0078d4>Shell<color:reset>: cmd
<color:#0078d4>████████   ████████<color:reset>   <color:#0078d4>CPU<color:reset>: AMD EPYC 7763 (4) @ 2.45 GHz
<color:#0078d4>████████   ████████<color:reset>   <color:#0078d4>Memory<color:reset>: 1024 MiB / 16384 MiB
Arch Linux:
<color:#1793d1>         /\          <color:reset>   root@archiso
<color:#1793d1>        /  \         <color:reset>   ------------
<color:#1793d1>       /\   \        <color:reset>   <color:#1793d1>OS<color:reset>: Arch Linux x86_64
<color:#1793d1>      /      \       <color:reset>   <color:#1793d1>Host<color:reset>: QEMU Virtual Machine
<color:#1793d1>     /   ,,   \      <color:reset>   <color:#1793d1>Kernel<color:reset>: 6.10.8-arch1
<color:#1793d1>    /   |  |  -\     <color:reset>   <color:#1793d1>Uptime<color:reset>: 3 mins
<color:#1793d1>   /_-''    ''-_\    <color:reset>   <color:#1793d1>Shell<color:reset>: bash 5.2.32
<color:#1793d1>  (____      ____)   <color:reset>   <color:#1793d1>CPU<color:reset>: AMD EPYC 7763 (4) @ 2.45 GHz
<color:#1793d1>       `----'        <color:reset>   <color:#1793d1>Memory<color:reset>: 247 MiB / 16384 MiB
Ubuntu:
<color:#e95420>          _          <color:reset>   root@ubuntu
<color:#e95420>      ---(_)         <color:reset>   -----------
<color:#e95420>  _/  ---  \         <color:reset>   <color:#e95420>OS<color:reset>: Ubuntu 24.04 LTS x86_64
<color:#e95420> (_) |   |           <color:reset>   <color:#e95420>Host<color:reset>: Virtual Machine
<color:#e95420>   \  --- _/         <color:reset>   <color:#e95420>Kernel<color:reset>: 6.8.0-41-generic
<color:#e95420>      ---(_)         <color:reset>   <color:#e95420>Uptime<color:reset>: 5 mins
<color:#e95420>                     <color:reset>   <color:#e95420>Shell<color:reset>: bash 5.2.21
<color:#e95420>                     <color:reset>   <color:#e95420>CPU<color:reset>: AMD EPYC 7763 (4) @ 2.45 GHz
<color:#e95420>                     <color:reset>   <color:#e95420>Memory<color:reset>: 312 MiB / 16384 MiB"""


_BOOT = r"""<clear:zae_term>
<color:#ff1744>███████╗ <color:#ff9100>█████╗  <color:#ffea00>███████╗
<color:#ff007f>╚══███╔╝<color:#ffab00>██╔══██╗<color:#ffff00>██╔════╝
<color:#d500f9>  ███╔╝ <color:#00e676>███████║<color:#00e5ff>█████╗
<color:#aa00ff> ███╔╝  <color:#00c853>██╔══██║<color:#00b0ff>██╔══╝
<color:#651fff>███████╗<color:#1de9b6>██║  ██║<color:#2979ff>███████╗
<color:#3d5afe>╚══════╝<color:#00bfa5>╚═╝  ╚═╝<color:#304ffe>╚══════╝<color:reset>

<color:#ff007f>:3<color:reset> <color:#6272a4>a virtual machine that can run any OS. v3.2. Powered by Groq. github: @rootlesszen<color:reset>
<timeout:0.18>
Press F11 for Fullscreen, Esc to exit.
"""


class _W_Thread(QThread):
    chunk = pyqtSignal(str)
    stat = pyqtSignal(str)
    done = pyqtSignal(str)
    mused = pyqtSignal(str)
    request_input = pyqtSignal()

    def __init__(self, k, msgs, ml, silent=False):
        super().__init__()
        self._k = k
        self._msgs = msgs
        self._stop = False
        self._ml = ml
        self._silent = silent

    def cancel(self):
        self._stop = True

    def run(self):
        global _mi
        wt = "a few seconds"
        lec = None
        ml = self._ml
        order = ml[_mi:] + ml[:_mi]
        order = order[:3]
        rate_hit_count = 0
        for attempt, mdl in enumerate(order):
            if self._stop: return
            is_reason = any(r in mdl for r in _REASON_MODELS)
            maxt = 500 if is_reason else 600
            pl = {
                "model": mdl,
                "messages": self._msgs,
                "temperature": 0.1,
                "max_completion_tokens": maxt,
                "stream": True,
                "top_p": 0.85,
                "presence_penalty": 0.3,
                "frequency_penalty": 0.5,
            }
            if is_reason:
                pl["reasoning_effort"] = "low"
                pl["include_reasoning"] = False
            try:
                self.stat.emit("api request")
                self.mused.emit(mdl)
                rq = urllib.request.Request(
                    "https://api.groq.com/openai/v1/chat/completions",
                    data=json.dumps(pl).encode(),
                    headers={"Authorization": f"Bearer {self._k}",
                             "Content-Type": "application/json",
                             "User-Agent": _UA})
                ft = []
                _rep_word = None
                _rep_count = 0
                _looped = False
                _line_buf = ""
                _line_count = 0
                self.stat.emit("waiting")
                with urllib.request.urlopen(rq, timeout=15) as rsp:
                    for rl in rsp:
                        if self._stop: return
                        ln = rl.decode("utf-8", errors="ignore").strip()
                        if not ln or not ln.startswith("data:"): continue
                        ds = ln[5:].strip()
                        if ds == "[DONE]": break
                        try:
                            c = json.loads(ds)
                            delta = c.get("choices", [{}])[0].get("delta", {})
                            dt = delta.get("content", "") or delta.get("reasoning_content", "") or delta.get("reasoning", "") or ""
                            if dt:
                                combined = _line_buf + dt
                                if "<request>" in combined or "<<request>>" in combined:
                                    tag = "<<request>>" if "<<request>>" in combined else "<request>"
                                    pre = combined.split(tag)[0]
                                    if pre:
                                        remaining = pre[len(_line_buf):]
                                        if remaining:
                                            ft.append(remaining)
                                            self.chunk.emit(remaining)
                                    ft.append("<request>")
                                    _line_buf = ""
                                    break
                                ft.append(dt)
                                self.chunk.emit(dt)
                                _line_buf += dt
                                newlines = _line_buf.count("\n")
                                if newlines > 0:
                                    _line_count += newlines
                                    last_nl = _line_buf.rfind("\n")
                                    _line_buf = _line_buf[last_nl+1:]
                                w = dt.strip()
                                if w and w == _rep_word:
                                    _rep_count += 1
                                    if _rep_count >= 6:
                                        _looped = True
                                        break
                                elif w:
                                    _rep_word = w; _rep_count = 1
                                if len(ft) > 3000 or _line_count > 40:
                                    _looped = True
                                    break
                        except Exception:
                            continue
                ans = "".join(ft)
                ans = _clean(ans)
                if _looped:
                    ans = re.sub(r'(\S+)(\s*\1){3,}\s*$', r'\1', ans).rstrip()
                if not ans.strip() and not self._silent:
                    time.sleep(0.2)
                    continue
                if ans.strip():
                    _mi = ml.index(mdl) + 1 if mdl in ml else 0
                    if _mi >= len(ml): _mi = 0
                self.done.emit(ans.rstrip())
                return
            except urllib.error.HTTPError as e:
                if self._stop: return
                lec = e.code
                if e.code == 401:
                    self.chunk.emit("<color:#ff5555>groq: api key invalid<color:reset>\n")
                    self.done.emit(""); return
                elif e.code == 403:
                    self.chunk.emit("<color:#ff5555>groq: 403 forbidden. enable VPN or check key<color:reset>\n")
                    self.done.emit(""); return
                rt = e.headers.get('x-ratelimit-reset-tokens') or e.headers.get('x-ratelimit-reset-requests') or e.headers.get('retry-after')
                if rt:
                    rt = rt.strip()
                    wt = rt if re.search(r'[a-zA-Z]$', rt) else f"{rt}s"
                else:
                    try:
                        eb = e.read().decode("utf-8", errors="ignore")
                        mx = re.search(r'try again in ([\w\.]+)', eb, re.IGNORECASE)
                        if mx: wt = mx.group(1).rstrip('.')
                    except Exception:
                        pass
                if e.code == 429:
                    rate_hit_count += 1
                    if rate_hit_count >= 2:
                        secs = re.search(r'(\d+)', str(wt))
                        sw = secs.group(1) if secs else wt
                        self.chunk.emit(f"<color:#808080>rate limit for ~{sw}s.<color:reset>\n")
                        self.done.emit(""); return
                    self.stat.emit("rate limited, switching...")
                    time.sleep(0.3)
                    continue
                time.sleep(0.3)
                continue
            except Exception:
                if self._stop: return
                time.sleep(0.3)
                continue
        if not self._stop:
            if lec == 429:
                secs = re.search(r'(\d+)', str(wt))
                sw = secs.group(1) if secs else wt
                self.chunk.emit(f"<color:#808080>rate limit for ~{sw}s.<color:reset>\n")
            elif lec == 400:
                self.chunk.emit("<color:#ff5555>groq: context full. type 'clear'<color:reset>\n")
            elif lec:
                self.chunk.emit(f"<color:#ff5555>groq: error {lec}<color:reset>\n")
            self.done.emit("")


class _Term(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        if _W:
            self.setWindowFlags(Qt.WindowType.Window)
        else:
            self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("ZAE")
        self.resize(920, 580)
        self._k = _lk()
        self._fs = False
        self._models = _gm(self._k)
        self.setFont(_gf(12))
        self.setCursorWidth(9)
        self._cc = _TC
        self._bg_cc = "#000000"
        self._update_style()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._st = _St()
        self._msgs = []
        self._pr = "root@archiso ~ # "
        self._pp = 0
        self._busy = False
        self._sb = ""
        self._hist = []; self._hi = 0
        self._lm = "None"; self._lr = "None"
        self._spin = False; self._sp = 0; self._stk = 0
        self._sfr = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self._scl = ["#ff1744", "#ff9100", "#ffea00", "#00e676", "#00e5ff", "#2979ff", "#d500f9"]
        self._stm = QTimer(self)
        self._stm.timeout.connect(self._utk)
        self._drg = False
        self._doff = None
        self._waiting_input = False
        self._spin_status = ""
        self._model_menu_active = False
        self._model_menu_idx = 0
        self._model_menu_start_pos = 0
        self._sys_override = None
        self._otc(_BOOT)
        self._np()

    def _update_style(self):
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {self._bg_cc};
                color: {self._cc};
                selection-background-color: #2e3440;
                selection-color: #ffffff;
                border: none;
                padding: 4px;
                margin: 0px;
                line-height: 1.22;
            }}
            QScrollBar:vertical {{ width: 0px; height: 0px; background: transparent; }}
            QScrollBar:horizontal {{ width: 0px; height: 0px; background: transparent; }}
        """)

    def mousePressEvent(self, e):
        if not _W and e.button() == Qt.MouseButton.LeftButton and e.position().y() < 30:
            self._drg = True
            self._doff = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
            e.accept()
        else:
            super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self._drg and self._doff is not None:
            self.move((e.globalPosition().toPoint() - self._doff))
            e.accept()
        else:
            super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        self._drg = False
        super().mouseReleaseEvent(e)

    def _ss(self):
        self._spin = True; self._stk = 0
        c = self.textCursor()
        c.movePosition(QTextCursor.MoveOperation.End)
        self._sp = c.position()
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(self._scl[0]))
        status_text = self._sfr[0] + " " + self._spin_status
        c.insertText(status_text, fmt)
        self.setTextCursor(c)
        self._stm.start(80)

    def _utk(self):
        if not self._spin: return
        self._stk += 1
        fr = self._sfr[self._stk % len(self._sfr)]
        cl = self._scl[self._stk % len(self._scl)]
        c = self.textCursor()
        c.setPosition(self._sp)
        c.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(cl))
        status_text = fr + " " + self._spin_status
        c.insertText(status_text, fmt)

    def _xs(self):
        if self._spin:
            self._stm.stop()
            self._spin = False
            c = self.textCursor()
            c.setPosition(self._sp)
            c.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
            c.removeSelectedText()

    def _raw_insert(self, txt, clr):
        if not txt:
            return
        c = self.textCursor()
        c.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(clr))
        c.insertText(txt, fmt)
        self.setTextCursor(c)
        self.ensureCursorVisible()

    def _parse_and_insert(self, txt, default_color=None):
        if not txt:
            return
        if default_color:
            self._cc = default_color

        for tm in re.finditer(r'<{1,2}timeout:([\d\.]+)>{1,2}', txt, re.IGNORECASE):
            try:
                ms = int(float(tm.group(1)) * 1000)
                if ms > 0:
                    lp = QEventLoop()
                    QTimer.singleShot(min(ms, 1000), lp.quit)
                    lp.exec()
            except Exception:
                pass
        txt = re.sub(r'<{1,2}timeout:[\d\.]+>{1,2}', '', txt, flags=re.IGNORECASE)

        txt = tags_to_ansi(txt)
        txt = re.sub(r'<{1,2}request>{1,2}', '', txt)

        ansi_re = re.compile(r'(?:\x1b|\033|\\e)\[([0-9;]*)([a-zA-Z])')
        last_idx = 0
        for m in ansi_re.finditer(txt):
            plain = txt[last_idx:m.start()]
            if plain:
                self._raw_insert(plain, self._cc)
            last_idx = m.end()

            params_str, cmd = m.group(1), m.group(2)
            if cmd == 'm':
                codes = [int(x) for x in params_str.split(';') if x.isdigit()]
                if not codes:
                    codes = [0]
                i = 0
                while i < len(codes):
                    c = codes[i]
                    if c == 0:
                        self._cc = _TC
                    elif c in _ANSI_FG:
                        self._cc = _ANSI_FG[c]
                    elif c in _ANSI_BG:
                        self._bg_cc = _ANSI_BG[c]
                        self._update_style()
                    elif c == 38 and i + 4 < len(codes) and codes[i+1] == 2:
                        r, g, b = codes[i+2], codes[i+3], codes[i+4]
                        self._cc = f"#{r:02x}{g:02x}{b:02x}"
                        i += 4
                    elif c == 48 and i + 4 < len(codes) and codes[i+1] == 2:
                        r, g, b = codes[i+2], codes[i+3], codes[i+4]
                        self._bg_cc = f"#{r:02x}{g:02x}{b:02x}"
                        self._update_style()
                        i += 4
                    elif c == 38 and i + 2 < len(codes) and codes[i+1] == 5:
                        self._cc = _256_to_hex(codes[i+2])
                        i += 2
                    elif c == 48 and i + 2 < len(codes) and codes[i+1] == 5:
                        self._bg_cc = _256_to_hex(codes[i+2])
                        self._update_style()
                        i += 2
                    i += 1
            elif cmd in ('J', 'H'):
                self.clear()
                self._pp = 0

        rem = txt[last_idx:]
        if rem:
            self._raw_insert(rem, self._cc)

    def _ic(self, txt, clr=None):
        if not txt:
            return
        if "<" in txt or "\033" in txt or "\x1b" in txt or "\\e[" in txt:
            self._parse_and_insert(txt, clr)
        else:
            self._raw_insert(txt, clr or self._cc)

    def _np(self):
        c = self.textCursor(); c.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat(); fmt.setForeground(QColor("#ffffff"))
        c.insertText(self._pr, fmt)
        tf = QTextCharFormat(); tf.setForeground(QColor(self._cc))
        self.setCurrentCharFormat(tf)
        self.setTextCursor(c); self._pp = self.textCursor().position()
        self.ensureCursorVisible()

    def _stop(self):
        self._xs()
        if hasattr(self, '_wk') and self._wk.isRunning():
            self._wk.cancel(); self._wk.terminate(); self._wk.wait(100)
        self._sb = ""
        self._busy = False; self._waiting_input = False
        self.setReadOnly(False)
        self._raw_insert("^C\n", self._cc); self._np()

    def _ri(self, txt):
        c = self.textCursor(); c.setPosition(self._pp)
        c.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        c.removeSelectedText()
        fmt = QTextCharFormat(); fmt.setForeground(QColor(self._cc))
        c.insertText(txt, fmt); self.setTextCursor(c)

    def _draw_model_menu(self):
        c = self.textCursor()
        c.setPosition(self._model_menu_start_pos)
        c.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        c.removeSelectedText()
        self.setTextCursor(c)
        bar = "═" * 52
        self._raw_insert(f"╔{bar}╗\n", "#4444aa")
        self._raw_insert(f"║{'ZAE MODEL SELECTOR':^52}║\n", "#4444aa")
        self._raw_insert(f"╠{bar}╣\n", "#4444aa")
        max_v = 14
        total = len(self._models)
        if total <= max_v:
            start_i = 0
            end_i = total
        else:
            half = max_v // 2
            start_i = max(0, min(self._model_menu_idx - half, total - max_v))
            end_i = start_i + max_v

        for i in range(start_i, end_i):
            m = self._models[i]
            name = m[:46]
            if i == self._model_menu_idx:
                line = f" ► {name:<47} "
                self._raw_insert("║", "#4444aa")
                self._raw_insert(line, "#ff5555")
                self._raw_insert("║\n", "#4444aa")
            else:
                line = f"   {name:<47} "
                self._raw_insert("║", "#4444aa")
                self._raw_insert(line, "#808080")
                self._raw_insert("║\n", "#4444aa")
        self._raw_insert(f"╠{bar}╣\n", "#4444aa")
        footer_text = f"↑/↓ Navigate   Enter: Select ({self._model_menu_idx+1}/{total})"
        self._raw_insert(f"║{footer_text:^52}║\n", "#555555")
        self._raw_insert(f"╚{bar}╝\n", "#4444aa")

    def keyPressEvent(self, e):
        if self._model_menu_active:
            if e.key() == Qt.Key.Key_Up:
                self._model_menu_idx = max(0, self._model_menu_idx - 1)
                self._draw_model_menu()
                return
            elif e.key() == Qt.Key.Key_Down:
                self._model_menu_idx = min(len(self._models) - 1, self._model_menu_idx + 1)
                self._draw_model_menu()
                return
            elif e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self._model_menu_active = False
                chosen = self._models[self._model_menu_idx]
                c = self.textCursor()
                c.setPosition(self._model_menu_start_pos)
                c.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
                c.removeSelectedText()
                self.setTextCursor(c)
                old_idx = _FM.index(chosen) if chosen in _FM else 0
                global _mi
                _mi = old_idx
                self._models = [chosen] + [m for m in self._models if m != chosen]
                self._ic(f"model set: {chosen}\n", "#77dd77")
                self._np()
                return
            elif e.key() == Qt.Key.Key_Escape:
                self._model_menu_active = False
                c = self.textCursor()
                c.setPosition(self._model_menu_start_pos)
                c.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
                c.removeSelectedText()
                self.setTextCursor(c)
                self._ic("cancelled\n", "#808080")
                self._np()
                return
            else:
                return

        if e.modifiers() == Qt.KeyboardModifier.ControlModifier and e.key() == Qt.Key.Key_C:
            self._stop(); return
        if e.key() == Qt.Key.Key_Escape:
            if self._busy: self._stop(); return
            else: self.close(); return
        if self._busy and not self._waiting_input:
            e.ignore(); return
        c = self.textCursor(); pos = c.position()
        _nav_keys = (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Home,
                     Qt.Key.Key_F11, Qt.Key.Key_Left)
        if pos < self._pp and e.key() not in _nav_keys:
            c.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(c)
            pos = c.position()
        anchor_before_pp = c.hasSelection() and min(c.anchor(), c.position()) < self._pp
        if anchor_before_pp and e.key() not in _nav_keys:
            c.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(c)
            pos = c.position()
        if e.key() == Qt.Key.Key_F11:
            self._fs = not self._fs
            if self._fs: self.showFullScreen()
            else: self.showNormal()
            return
        if e.modifiers() == Qt.KeyboardModifier.ControlModifier and e.key() == Qt.Key.Key_D:
            if not self.toPlainText()[self._pp:]: self.close(); return
        if e.key() == Qt.Key.Key_Backspace and pos <= self._pp: return
        if e.key() == Qt.Key.Key_Left and pos <= self._pp: return
        if e.key() == Qt.Key.Key_Home:
            c.setPosition(self._pp); self.setTextCursor(c); return
        if e.key() == Qt.Key.Key_Up:
            if not self._waiting_input and self._hist and self._hi > 0:
                self._hi -= 1; self._ri(self._hist[self._hi])
            return
        if e.key() == Qt.Key.Key_Down:
            if not self._waiting_input:
                if self._hist and self._hi < len(self._hist) - 1:
                    self._hi += 1; self._ri(self._hist[self._hi])
                else:
                    self._hi = len(self._hist); self._ri("")
            return
        if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            c.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(c)
            cmd = self.toPlainText()[self._pp:].strip()
            fmt = QTextCharFormat(); fmt.setForeground(QColor(self._cc))
            c.insertText("\n", fmt); self.setTextCursor(c)
            if self._waiting_input:
                self._handle_interactive_input(cmd)
                return
            if cmd:
                self._hist.append(cmd)
                self._hi = len(self._hist)
            self._hc(cmd)
            return
        super().keyPressEvent(e)

    def _handle_interactive_input(self, answer):
        self._waiting_input = False
        self._busy = True
        self.setReadOnly(True)
        self._msgs.append({"role": "user", "content": answer.strip()[:600]})
        sc = self._get_sys_prompt() + "\n" + self._st.hdr()
        pm = [{"role": "system", "content": sc}] + self._msgs[-8:]
        self._spin_status = ""
        self._wk = _W_Thread(self._k, pm, self._models, silent=False)
        self._wk.chunk.connect(self._otc)
        self._wk.stat.connect(self._osu)
        self._wk.done.connect(self._odf)
        self._wk.mused.connect(self._omu)
        self._ss()
        self._wk.start()

    def _get_sys_prompt(self):
        if hasattr(self, '_sys_override') and self._sys_override:
            return self._sys_override
        return _SYS

    def _hc(self, cmd):
        if not cmd:
            self._np(); return

        if cmd == ">zae show":
            self._ic(f"zae: model: {self._lm}\nresponse:\n{self._lr}\n", "#ffff55")
            self._np(); return

        if cmd == ">zae reset":
            self._st = _St()
            self._msgs = []
            self._cc = _TC
            self._bg_cc = "#000000"
            self._waiting_input = False
            self._sys_override = None
            self._update_style()
            self.clear()
            self._otc(_BOOT)
            self._pr = self._st.prompt()
            self._np()
            return

        if cmd.startswith(">zae osinstall"):
            rest = cmd[len(">zae osinstall"):].strip()
            os_name = rest.strip('"').strip("'").strip()
            self._st = _St()
            self._msgs = []
            self._cc = _TC
            self._bg_cc = "#000000"
            self._waiting_input = False
            self._update_style()
            self.clear()
            if os_name:
                self._st.switch_custom(os_name)
                self._sys_override = _SYS.replace(
                    "Raw TTY/console emulator.",
                    f"Raw TTY/console emulator running {os_name}. OS is ALWAYS {os_name}."
                )
                self._otc(_BOOT)
                self._ic(f"OS set: {os_name}\n", "#77dd77")
                self._pr = self._st.prompt()
                if self._st.plat == "windows" and self._st.shell == "powershell":
                    self._pr = "PS " + self._st.prompt()
            else:
                self._st.os = "Custom OS (building)"
                self._st.plat = "linux"
                self._st.shell = "bash"
                self._st.hn = "custom"
                self._st.cd = "/root"
                self._sys_override = _SYS.replace(
                    "Raw TTY/console emulator.",
                    "Raw TTY/console emulator for custom OS built from scratch."
                )
                self._otc(_BOOT)
                self._ic("ZAE: Custom OS mode. Build your kernel and components from scratch.\n", "#ffff55")
                self._pr = self._st.prompt()
            self._np()
            return

        if cmd == ">zae model":
            self._model_menu_active = True
            self._model_menu_idx = 0
            c = self.textCursor()
            c.movePosition(QTextCursor.MoveOperation.End)
            self._model_menu_start_pos = c.position()
            self._draw_model_menu()
            return

        _lc = cmd.strip().lower()

        if self._st.plat == "windows":
            cm = re.match(r'^color\s+([0-9a-fA-F])([0-9a-fA-F])$', _lc)
            if cm:
                bg_d = cm.group(1)
                fg_d = cm.group(2)
                self._bg_cc = _CMD_COLORS.get(bg_d, "#000000")
                self._cc = _CMD_COLORS.get(fg_d, "#55ff55")
                self._update_style()
                self._np()
                return

        self._st.upd(cmd)
        self._pr = self._st.prompt()

        if _lc == "clear" or (self._st.plat == "windows" and _lc == "cls"):
            self.clear(); self._np(); return
        elif _lc in ("exit", "poweroff", "shutdown now"):
            self.close(); return

        if not self._k:
            if cmd.startswith("gsk_"):
                with open(_KF, "w") as f: f.write(cmd)
                self._k = cmd
                self._models = _gm(self._k)
                self._ic("groq api key saved\n", "#55ff55")
            else:
                self._ic("enter your groq api key (gsk_...):\n", "#ffff55")
            self._np(); return

        self._busy = True; self.setReadOnly(True)
        self._msgs.append({"role": "user", "content": cmd.strip()[:1000]})
        sc = self._get_sys_prompt() + "\n" + self._st.hdr()
        pm = [{"role": "system", "content": sc}] + self._msgs[-8:]

        _sc = cmd.split()[0] if cmd.split() else ""
        _silent = _sc.lower() in ("cd", "mkdir", "touch", "export", "alias", "unset", "source",
                                   "chmod", "chown", "mv", "cp", "rm",
                                   "md", "set", "cd.", "attrib", "cd..", "color")
        self._spin_status = ""
        self._wk = _W_Thread(self._k, pm, self._models, silent=_silent)
        self._wk.chunk.connect(self._otc)
        self._wk.stat.connect(self._osu)
        self._wk.done.connect(self._odf)
        self._wk.mused.connect(self._omu)
        self._ss()
        self._wk.start()

    def _omu(self, n):
        self._lm = n

    def _osu(self, txt):
        self._spin_status = txt
        if self._spin:
            self._xs()
            self._ss()

    def _otc(self, ch):
        if self._spin:
            self._xs()
        ch = ch.replace("```bash", "").replace("```text", "").replace("```", "")
        if not ch: return
        self._sb += ch

        to_process = self._sb
        self._sb = ""

        last_lt = to_process.rfind("<")
        if last_lt != -1 and ">" not in to_process[last_lt:]:
            tail = to_process[last_lt:]
            if len(tail) < 50 and re.match(r'^<{1,2}[a-zA-Z0-9_:#\.\-]*$', tail):
                self._sb = tail + self._sb
                to_process = to_process[:last_lt]

        m_esc = re.search(r'(?:\x1b|\033|\\e)(?:\[[0-9;]*)?$', to_process)
        if m_esc:
            self._sb = m_esc.group(0) + self._sb
            to_process = to_process[:m_esc.start()]

        if to_process:
            self._parse_and_insert(to_process)

    def _odf(self, raw):
        self._xs()
        self._lr = raw
        if self._sb:
            self._parse_and_insert(self._sb)
            self._sb = ""

        has_request = ("<request>" in raw) or ("<<request>>" in raw)
        clean_raw = re.sub(r'<{1,2}request>{1,2}', '', raw).rstrip()
        if clean_raw and not clean_raw.endswith("\n"):
            self._raw_insert("\n", self._cc)

        hist_entry = _compress_for_history(clean_raw)
        self._msgs.append({"role": "assistant", "content": hist_entry})
        if len(self._msgs) > 20:
            self._msgs = self._msgs[-16:]

        if has_request:
            self._waiting_input = True
            self._busy = False
            self.setReadOnly(False)
            c = self.textCursor(); c.movePosition(QTextCursor.MoveOperation.End)
            self._pp = c.position()
            self.setTextCursor(c)
            self.ensureCursorVisible()
        else:
            self._waiting_input = False
            self._busy = False; self.setReadOnly(False)
            self._np()

    def closeEvent(self, ev):
        self._xs()
        if hasattr(self, '_wk') and self._wk.isRunning():
            self._wk.cancel(); self._wk.terminate()
        ev.accept()
        QApplication.instance().quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    _ef()
    if not _W:
        if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
            for r in ["float", "center", "pin", "noborder", "bordersize 0", "noshadow", "noblur", "nodim", "opaque"]:
                subprocess.run(f"hyprctl keyword windowrulev2 '{r},title:^(ZAE)$' >/dev/null 2>&1", shell=True)
    w = _Term(); w.show(); sys.exit(app.exec())
