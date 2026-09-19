#!/usr/bin/env python3
import sys, os, time, subprocess, json, re, platform
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
from PyQt6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QFontDatabase

_D = os.path.expanduser("~/.config/zae")
_FD = os.path.join(_D, "fonts")
_FP = os.path.join(_FD, "PxPlus_IBM_VGA_8x16.ttf")
_KF = os.path.join(_D, "groq_key")
os.makedirs(_FD, exist_ok=True)

_TC = "#b0b0b0"
_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36 ZAE/3.0"

_FM = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
    "mixtral-8x7b-32768",
]

_SKIP = ("whisper", "guard", "embed", "vision", "tool", "tts", "image",
         "compound", "orpheus", "safeguard", "allam")

_mi = 0

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

_BOOT = r"""<<clear:zae_term>>
<<color:#ff1744>>███████╗ <<color:#ff9100>>█████╗  <<color:#ffea00>>███████╗
<<color:#ff007f>>╚══███╔╝<<color:#ffab00>>██╔══██╗<<color:#ffff00>>██╔════╝
<<color:#d500f9>>  ███╔╝ <<color:#00e676>>███████║<<color:#00e5ff>>█████╗  
<<color:#aa00ff>> ███╔╝  <<color:#00c853>>██╔══██║<<color:#00b0ff>>██╔══╝  
<<color:#651fff>>███████╗<<color:#1de9b6>>██║  ██║<<color:#2979ff>>███████╗
<<color:#3d5afe>>╚══════╝<<color:#00bfa5>>╚═╝  ╚═╝<<color:#304ffe>>╚══════╝<<color:reset>>

<<color:#ff007f>>:3<<color:reset>> <<color:#6272a4>>a virtual machine that can run any OS. Powered by Groq. github: @rootlesszen<<color:reset>>
<<timeout:0.18>>
BIOS Version 4.10-ZAE (CP437 IBM VGA text mode)
Memory Test: 16384KB OK<<timeout:0.10>>
Booting from Live Media (archiso_x86_64)...<<timeout:0.15>>

<<color:#55ff55>>[  OK  ]<<color:reset>> Started D-Bus System Message Bus.<<timeout:0.02>>
<<color:#55ff55>>[  OK  ]<<color:reset>> Started Network Time Synchronization.<<timeout:0.02>>
<<color:#55ff55>>[  OK  ]<<color:reset>> Reached target Multi-User System.<<timeout:0.05>>

Arch Linux 6.10.8-arch1 (tty1)
Type 'archinstall' to install. Press F11 for Fullscreen, Esc to exit.
"""

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


class _St:
    def __init__(self):
        self.os = "Arch Linux x86_64"
        self.hn = "archiso"
        self.u = "root"
        self.cd = "/root"
        self.fs = {}

    def upd(self, txt):
        t = txt + "\n"
        for m in re.finditer(r'^cd\s+(.+)$', t, re.MULTILINE):
            tgt = m.group(1).strip()
            if tgt in ("~", ""): self.cd = "/root" if self.u == "root" else f"/home/{self.u}"
            elif tgt.startswith("/"): self.cd = tgt
            elif tgt == "..":
                pts = self.cd.rstrip("/").split("/")
                self.cd = "/".join(pts[:-1]) if len(pts) > 1 else "/"
            else: self.cd = f"{self.cd.rstrip('/')}/{tgt}"
        for m in re.finditer(r'(?:hostnamectl\s+set-hostname|hostname)\s+([a-zA-Z0-9_\-]+)', t):
            self.hn = m.group(1)
        for m in re.finditer(r'cat\s*<<\s*[\'\"]?(\w+)[\'\"]?\s*>\s*(\S+)\n(.*?)\n\1', t, re.DOTALL):
            self._sf(m.group(2), m.group(3).strip())
        for m in re.finditer(r'echo\s+[\'\"]?(.*?)[\'\"]?\s*>\s*(\S+)', t):
            self._sf(m.group(2), m.group(1))

    def _sf(self, rp, c):
        if rp.startswith("~/"):
            h = "/root" if self.u == "root" else f"/home/{self.u}"
            rp = h + "/" + rp[2:]
        p = rp if rp.startswith("/") else f"{self.cd.rstrip('/')}/{rp}"
        if "os-release" in p:
            m = re.search(r'(?:PRETTY_NAME|NAME)\s*=\s*["\']?([^"\']+)["\']?', c)
            if m: self.os = m.group(1).strip()
        self.fs[p] = c

    def hdr(self):
        cf = []
        for k, v in list(self.fs.items())[-4:]:
            dk = k.replace("/root/", "~/") if self.u == "root" else k
            cf.append(f"{dk}: {v[:800]}")
        fs = "; ".join(cf)
        return f"[OS={self.os} HOST={self.hn} USER={self.u} CWD={self.cd}]{' FILES: '+fs if fs else ''}"


_SYS = r"""Raw Linux TTY emulator. Output ONLY what a real terminal prints. No chat. No markdown. No explanations.
Rules: silent commands (cd,mkdir,touch,export)=empty output. All packages installed. Simulate 1 run only, never loop.
Tags: <<color:#HEX>> <<color:reset>> <<timeout:X>> <<clear:zae_term>>
ping=4 packets+stats then stop. fastfetch=arch logo+specs side by side. cmd/cmd.exe=switch to Windows C:\> prompt."""


class _W_Thread(QThread):
    chunk = pyqtSignal(str)
    stat = pyqtSignal(str)
    done = pyqtSignal(str)
    mused = pyqtSignal(str)

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
        for mdl in order:
            if self._stop: return
            is_reason = "gpt-oss" in mdl
            maxt = 2048 if is_reason else 800
            pl = {
                "model": mdl,
                "messages": self._msgs,
                "temperature": 0.0,
                "max_completion_tokens": maxt,
                "stream": True,
                "top_p": 0.9,
            }
            try:
                self.mused.emit(mdl)
                rq = urllib.request.Request(
                    "https://api.groq.com/openai/v1/chat/completions",
                    data=json.dumps(pl).encode(),
                    headers={"Authorization": f"Bearer {self._k}",
                             "Content-Type": "application/json",
                             "User-Agent": _UA})
                ft = []
                with urllib.request.urlopen(rq, timeout=10) as rsp:
                    for rl in rsp:
                        if self._stop: return
                        ln = rl.decode("utf-8", errors="ignore").strip()
                        if not ln or not ln.startswith("data:"): continue
                        ds = ln[5:].strip()
                        if ds == "[DONE]": break
                        try:
                            c = json.loads(ds)
                            dt = c.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if dt:
                                ft.append(dt)
                                self.chunk.emit(dt)
                        except Exception:
                            continue
                ans = "".join(ft)
                ans = _clean(ans)
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
                    self.chunk.emit("<<color:#ff5555>>groq: api key invalid<<color:reset>>\n")
                    self.done.emit(""); return
                elif e.code == 403:
                    self.chunk.emit("<<color:#ff5555>>groq: 403 forbidden. enable VPN or check key<<color:reset>>\n")
                    self.done.emit(""); return
                rt = e.headers.get('x-ratelimit-reset-tokens') or e.headers.get('x-ratelimit-reset-requests') or e.headers.get('retry-after')
                if rt: wt = f"{rt}s"
                else:
                    try:
                        eb = e.read().decode("utf-8", errors="ignore")
                        mx = re.search(r'try again in ([\w\.]+)', eb, re.IGNORECASE)
                        if mx: wt = mx.group(1).rstrip('.')
                    except Exception:
                        pass
                time.sleep(0.3)
                continue
            except Exception:
                if self._stop: return
                time.sleep(0.3)
                continue
        if not self._stop:
            if lec == 429:
                self.chunk.emit(f"<<color:#ff5555>>groq: rate limit. wait {wt}<<color:reset>>\n")
            elif lec == 400:
                self.chunk.emit("<<color:#ff5555>>groq: context full. type 'clear'<<color:reset>>\n")
            elif lec:
                self.chunk.emit(f"<<color:#ff5555>>groq: error {lec}<<color:reset>>\n")
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
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000000;
                color: #b0b0b0;
                selection-background-color: #2e3440;
                selection-color: #ffffff;
                border: none;
                padding: 4px;
                margin: 0px;
                line-height: 1.22;
            }
            QScrollBar:vertical { width: 0px; height: 0px; background: transparent; }
            QScrollBar:horizontal { width: 0px; height: 0px; background: transparent; }
        """)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._st = _St()
        self._msgs = []
        self._pr = "root@archiso ~ # "
        self._pp = 0
        self._busy = False
        self._cc = _TC
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
        self._otc(_BOOT)
        self._np()

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
        c.insertText(self._sfr[0], fmt)
        self.setTextCursor(c)
        self._stm.start(80)

    def _utk(self):
        if not self._spin: return
        self._stk += 1
        fr = self._sfr[self._stk % len(self._sfr)]
        cl = self._scl[self._stk % len(self._scl)]
        c = self.textCursor()
        c.setPosition(self._sp)
        c.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 1)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(cl))
        c.insertText(fr, fmt)

    def _xs(self):
        if self._spin:
            self._stm.stop()
            self._spin = False
            c = self.textCursor()
            c.setPosition(self._sp)
            c.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 1)
            c.removeSelectedText()

    def _ic(self, txt, clr):
        c = self.textCursor()
        c.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat(); fmt.setForeground(QColor(clr))
        c.insertText(txt, fmt); self.setTextCursor(c)
        self.ensureCursorVisible()

    def _np(self):
        c = self.textCursor(); c.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat(); fmt.setForeground(QColor("#ffffff"))
        c.insertText(self._pr, fmt)
        tf = QTextCharFormat(); tf.setForeground(QColor(_TC))
        self.setCurrentCharFormat(tf)
        self.setTextCursor(c); self._pp = self.textCursor().position()
        self.ensureCursorVisible()

    def _stop(self):
        self._xs()
        if hasattr(self, '_wk') and self._wk.isRunning():
            self._wk.cancel(); self._wk.terminate(); self._wk.wait(100)
        self._sb = ""; self._cc = _TC
        self._busy = False; self.setReadOnly(False)
        self._ic("^C\n", _TC); self._np()

    def _ri(self, txt):
        c = self.textCursor(); c.setPosition(self._pp)
        c.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        c.removeSelectedText()
        fmt = QTextCharFormat(); fmt.setForeground(QColor(_TC))
        c.insertText(txt, fmt); self.setTextCursor(c)

    def keyPressEvent(self, e):
        if e.modifiers() == Qt.KeyboardModifier.ControlModifier and e.key() == Qt.Key.Key_C:
            self._stop(); return
        if e.key() == Qt.Key.Key_Escape:
            if self._busy: self._stop(); return
            else: self.close(); return
        if self._busy: e.ignore(); return
        c = self.textCursor(); pos = c.position()
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
            if self._hist and self._hi > 0:
                self._hi -= 1; self._ri(self._hist[self._hi])
            return
        if e.key() == Qt.Key.Key_Down:
            if self._hist and self._hi < len(self._hist) - 1:
                self._hi += 1; self._ri(self._hist[self._hi])
            else:
                self._hi = len(self._hist); self._ri("")
            return
        if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            c.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(c)
            cmd = self.toPlainText()[self._pp:].strip()
            if cmd:
                self._hist.append(cmd)
                self._hi = len(self._hist)
            fmt = QTextCharFormat(); fmt.setForeground(QColor(_TC))
            c.insertText("\n", fmt); self.setTextCursor(c)
            self._hc(cmd)
            return
        super().keyPressEvent(e)

    def _hc(self, cmd):
        if not cmd:
            self._np(); return
        if cmd == ">zae show":
            self._ic(f"zae: model: {self._lm}\nresponse:\n{self._lr}\n", "#ffff55")
            self._np(); return
        self._st.upd(cmd)
        pc = "~" if self._st.cd == "/root" else self._st.cd
        self._pr = f"{self._st.u}@{self._st.hn} {pc} # "
        if cmd == "clear":
            self.clear(); self._np(); return
        elif cmd in ("exit", "poweroff", "shutdown now"):
            self.close(); return
        elif cmd == "reboot":
            self.clear(); self._otc(_BOOT); self._np(); return
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
        self._msgs.append({"role": "user", "content": cmd})
        sc = _SYS + "\n" + self._st.hdr()
        pm = [{"role": "system", "content": sc}]
        tail = self._msgs[-4:]
        for i, m in enumerate(tail):
            ct = m["content"][-600:]
            if i == len(tail) - 1 and m["role"] == "user":
                ct = f"$ {ct}"
            pm.append({"role": m["role"], "content": ct})
        _sc = cmd.split()[0] if cmd.split() else ""
        _silent = _sc in ("cd", "mkdir", "touch", "export", "alias", "unset", "source", "chmod", "chown", "mv", "cp", "rm")
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
        if self._spin:
            self._xs()
            self._ic(txt, "#6272a4")
            self._ss()
        else:
            self._ic(txt, "#6272a4")

    def _otc(self, ch):
        if self._spin:
            self._xs()
        ch = ch.replace("```bash", "").replace("```text", "").replace("```", "")
        if not ch: return
        self._sb += ch
        while self._sb:
            ts = self._sb.find("<<")
            if ts == -1:
                self._ic(self._sb, self._cc)
                self._sb = ""; break
            if ts > 0:
                self._ic(self._sb[:ts], self._cc)
                self._sb = self._sb[ts:]
                continue
            te = self._sb.find(">>")
            if te == -1:
                if len(self._sb) > 60:
                    self._ic(self._sb, self._cc)
                    self._sb = ""
                break
            tb = self._sb[2:te].strip()
            self._sb = self._sb[te+2:]
            self._at(tb)

    def _at(self, tag):
        lo = tag.lower()
        if lo.startswith("color:"):
            v = lo[6:].strip()
            if v == "reset": self._cc = _TC
            elif v.startswith("#"): self._cc = v
        elif lo == "clear:zae_term":
            self.clear(); self._pp = 0
        elif lo.startswith("timeout"):
            m = re.search(r'[\d\.]+', lo)
            if m:
                ms = int(float(m.group(0)) * 1000)
                if ms > 0:
                    lp = QEventLoop(); QTimer.singleShot(min(ms, 1000), lp.quit); lp.exec()

    def _odf(self, raw):
        self._xs()
        self._lr = raw
        if self._sb:
            self._ic(self._sb, self._cc)
            self._sb = ""
        if raw and not raw.endswith("\n"):
            self._ic("\n", _TC)
        if len(self._msgs) > 30:
            self._msgs = self._msgs[-10:]
        self._msgs.append({"role": "assistant", "content": raw[:400]})
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
