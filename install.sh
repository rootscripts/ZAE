#!/usr/bin/env bash

set -e

echo "[ZAE] Installing ZaeTerminal on Linux..."

mkdir -p ~/.local/bin ~/.config/arch-greet/fonts

if ! command -v python3 &> /dev/null; then
    echo "[!] Error: python3 is not installed. Please install Python 3."
    exit 1
fi

python3 -c "import PyQt6" 2>/dev/null || {
    echo "[ZAE] Installing PyQt6 dependency..."
    python3 -m pip install --break-system-packages PyQt6 2>/dev/null || python3 -m pip install PyQt6
}

# ВАЖНО: Первой строчкой идет шебанг #!/usr/bin/env python3
cat << 'EOF' > ~/.local/bin/zae
#!/usr/bin/env python3
import sys, os, time, subprocess, json, urllib.request, urllib.error, re, ssl
from PyQt6.QtWidgets import QApplication, QPlainTextEdit
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QEventLoop
from PyQt6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QFontDatabase

CFG = os.path.expanduser("~/.config/arch-greet")
F_DIR = os.path.join(CFG, "fonts")
F_PATH = os.path.join(F_DIR, "PxPlus_IBM_VGA_8x16.ttf")
K_FILE = os.path.join(CFG, "groq_key")
os.makedirs(CFG, exist_ok=True)
os.makedirs(F_DIR, exist_ok=True)

CLR = "#b0b0b0"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 ZaeTerminal/2.0"

MODELS = [
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "llama-3.1-8b-instant"
]

def get_k():
    if os.environ.get("GROQ_API_KEY"): return os.environ.get("GROQ_API_KEY").strip()
    if os.path.exists(K_FILE):
        with open(K_FILE, "r") as f:
            k = f.read().strip()
            if k: return k
    return ""

def get_m(k):
    if not k: return MODELS
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        url = "https://api.groq.com/openai/v1/models"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {k}", "User-Agent": UA})
        with urllib.request.urlopen(req, timeout=3.0, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            live = [m["id"] for m in data.get("data", []) if not any(x in m["id"] for x in ("whisper", "guard", "embedding", "vision", "tool"))]
            if live:
                return [m for m in MODELS if m in live] + [m for m in live if m not in MODELS]
    except Exception: pass
    return MODELS

def get_font():
    if not os.path.exists(F_PATH) or os.path.getsize(F_PATH) < 1000:
        urls = [
            "https://raw.githubusercontent.com/WheeledCord/tbwm/master/PxPlus_IBM_VGA_8x16.ttf",
            "https://raw.githubusercontent.com/industry-advance/industry-advance/master/Fonts/Px437_IBM_BIOS.ttf"
        ]
        for url in urls:
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=3, context=ctx) as resp:
                    if resp.status == 200:
                        data = resp.read()
                        if len(data) > 1000:
                            with open(F_PATH, "wb") as f: f.write(data)
                            break
            except Exception: pass
    if os.path.exists(F_PATH):
        try:
            fid = QFontDatabase.addApplicationFont(F_PATH)
            if fid != -1:
                fams = QFontDatabase.applicationFontFamilies(fid)
                if fams: return fams[0]
        except Exception: pass
    return None

def mk_font(sz=12):
    f = QFont()
    f.setStyleHint(QFont.StyleHint.Monospace)
    f.setFixedPitch(True)
    f.setFamilies(["PxPlus IBM VGA 8x16", "Px437 IBM BIOS", "IBM Plex Mono", "JetBrains Mono", "Courier New", "monospace"])
    f.setPointSize(sz)
    return f

BOOT = r"""<<clear:zae_term>>
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

class State:
    def __init__(self):
        self.os_name = "Arch Linux x86_64"
        self.hostname = "archiso"
        self.user = "root"
        self.cwd = "/root"
        self.files = {
            "/root/install.txt": "Guide: 1. fdisk /dev/sda 2. pacstrap /mnt base linux"
        }

    def parse_cmd(self, txt):
        t_pad = txt + "\n"
        for m in re.finditer(r'^cd\s+(.+)$', t_pad, re.MULTILINE):
            tgt = m.group(1).strip()
            if tgt in ("~", ""): self.cwd = "/root" if self.user == "root" else f"/home/{self.user}"
            elif tgt.startswith("/"): self.cwd = tgt
            elif tgt == "..":
                pts = self.cwd.rstrip("/").split("/")
                self.cwd = "/".join(pts[:-1]) if len(pts) > 1 else "/"
            else: self.cwd = f"{self.cwd.rstrip('/')}/{tgt}"
        
        for m in re.finditer(r'(?:hostnamectl\s+set-hostname|hostname)\s+([a-zA-Z0-9_\-]+)', t_pad):
            self.hostname = m.group(1)
            
        for m in re.finditer(r'cat\s*<<\s*[\'"]?(\w+)[\'"]?\s*>\s*(\S+)\n(.*?)\n\1', t_pad, re.DOTALL):
            self.write_f(m.group(2), m.group(3).strip())
            
        for m in re.finditer(r'echo\s+[\'"]?(.*?)[\'"]?\s*>\s*(\S+)', t_pad):
            self.write_f(m.group(2), m.group(1))

    def write_f(self, raw_path, content):
        if raw_path.startswith("~/"):
            home = "/root" if self.user == "root" else f"/home/{self.user}"
            raw_path = home + "/" + raw_path[2:]
            
        path = raw_path if raw_path.startswith("/") else f"{self.cwd.rstrip('/')}/{raw_path}"
        if "os-release" in path:
            m = re.search(r'(?:PRETTY_NAME|NAME)\s*=\s*["\']?([^"\']+)["\']?', content)
            if m: self.os_name = m.group(1).strip()
        self.files[path] = content

    def header(self):
        compact_files = []
        for k, v in list(self.files.items())[-8:]:
            c_val = v[:3000]
            display_k = k.replace("/root/", "~/") if self.user == "root" else k
            compact_files.append(f"File: {display_k}\n{c_val}\n")
        f_str = "\n".join(compact_files)
        return f"[STATE: OS='{self.os_name}' HOST='{self.hostname}' USER='{self.user}' CWD='{self.cwd}']\n{f_str}\n"

PROMPT = r"""You are a strict, authentic command-line terminal simulation. You are NOT an AI assistant. Do NOT converse.

TAGS YOU CAN USE:
1. <<color:#HEX>> : Set text color.
2. <<color:reset>> : Reset color to default gray.
3. <<timeout:X>> : Pause output for X seconds.
4. <<clear:zae_term>> : Clear screen.

CRITICAL RULES:
- NEVER reply with conversational text.
- Output ONLY raw terminal text. NEVER use markdown codeblocks.
- If a command produces no stdout (like successful 'mkdir', 'touch', 'cd', 'cat >'), OUTPUT NOTHING.
- If a command naturally produces output (e.g., 'python3', 'echo', 'curl', 'tree', 'dir', 'dmesg', 'ls'), YOU MUST OUTPUT THE RESULT. DO NOT BE SILENT.
- If the user types 'cmd', 'windows', or 'cmd.exe', instantly switch your context to simulate a Microsoft Windows Command Prompt (C:\>).
- If the user types a Windows `color` command (e.g. `color 0a`, `color 5`), YOU MUST ACTUALLY APPLY the corresponding `<<color:#HEX>>` tag.

FASTFETCH INSTRUCTIONS:
When the user runs 'fastfetch' or 'neofetch':
1. If ~/.config/fastfetch/logo.txt exists in [STATE], output the FULL custom logo EXACTLY as written. Output specs directly BELOW the logo.
2. If NO custom logo exists, use this exact side-by-side Arch template:
<<color:#1793d1>>       /\         <<color:reset>> {USER}@{HOST}
<<color:#1793d1>>      /  \        <<color:reset>> --------------
<<color:#1793d1>>     /\   \       <<color:reset>> OS: {OS}
<<color:#1793d1>>    /      \      <<color:reset>> Host: {HOST}
<<color:#1793d1>>   /   ,,   \     <<color:reset>> Kernel: Linux 6.10.8
<<color:#1793d1>>  /   |  |  -\    <<color:reset>> Shell: bash
<<color:#1793d1>> /_-''    ''-_\  <<color:reset>> Memory: 1.2GiB / 16.0GiB
"""

class Worker(QThread):
    chunk = pyqtSignal(str)
    status = pyqtSignal(str)
    done = pyqtSignal(str)
    m_used = pyqtSignal(str)

    def __init__(self, k, msgs):
        super().__init__()
        self.k = k
        self.msgs = msgs
        self.cancelled = False
        self.models = get_m(k)

    def cancel(self):
        self.cancelled = True

    def run(self):
        w_time = "a few seconds"
        err_code = None
        err_detail = ""
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        for m in self.models:
            if self.cancelled: return
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {
                "model": m,
                "messages": self.msgs,
                "temperature": 0.2,
                "max_completion_tokens": 1400,
                "stream": True
            }
            try:
                self.m_used.emit(m)
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Authorization": f"Bearer {self.k}", "Content-Type": "application/json", "User-Agent": UA}
                )
                buf_txt = []
                with urllib.request.urlopen(req, timeout=6, context=ctx) as resp:
                    for raw_line in resp:
                        if self.cancelled: return
                        line = raw_line.decode("utf-8", errors="ignore").strip()
                        if not line or not line.startswith("data:"): continue
                        d_str = line[5:].strip()
                        if d_str == "[DONE]": break
                        try:
                            chunk = json.loads(d_str)
                            delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if delta:
                                buf_txt.append(delta)
                                self.chunk.emit(delta)
                        except Exception: continue

                ans = "".join(buf_txt)
                self.done.emit(ans.rstrip())
                return
                
            except urllib.error.HTTPError as e:
                if self.cancelled: return
                err_code = e.code
                if e.code == 401:
                    self.chunk.emit("<<color:#ff5555>>groq api key invalid<<color:reset>>\n")
                    self.done.emit("")
                    return
                elif e.code == 403:
                    self.chunk.emit("<<color:#ff5555>>groq: HTTP 403 Forbidden :( Turn on VPN or check key.<<color:reset>>\n")
                    self.done.emit("")
                    return
                    
                rt = e.headers.get('x-ratelimit-reset-tokens')
                rr = e.headers.get('x-ratelimit-reset-requests')
                ra = e.headers.get('retry-after')
                
                if rt: w_time = f"{rt}s"
                elif rr: w_time = f"{rr}s"
                elif ra: w_time = f"{ra}s"
                else:
                    try:
                        body = e.read().decode("utf-8", errors="ignore")
                        match = re.search(r'try again in ([\w\.]+)', body, re.IGNORECASE)
                        if match: w_time = match.group(1).rstrip('.')
                    except: pass
                
                time.sleep(0.2)
                continue
            except Exception as e:
                if self.cancelled: return
                err_detail = str(e)
                time.sleep(0.2)
                continue

        if not self.cancelled:
            if err_code == 429:
                self.chunk.emit(f"<<color:#ff5555>>groq: rate limit cooldown active :( Please wait {w_time}.<<color:reset>>\n")
            elif err_code == 400:
                self.chunk.emit("<<color:#ff5555>>groq: context window full :( Type 'clear'.<<color:reset>>\n")
            elif err_code is not None:
                self.chunk.emit(f"<<color:#ff5555>>groq: API error {err_code} :( Please try again.<<color:reset>>\n")
            else:
                self.chunk.emit(f"<<color:#ff5555>>groq: network error ({err_detail or 'Connection failed'}) :( Check internet or API key.<<color:reset>>\n")
            self.done.emit("")

class Term(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("ArchTTY")
        self.resize(920, 580)
        
        self.k = get_k()
        self.is_fs = False
        
        self.setFont(mk_font(12))
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
        
        self.state = State()
        self.msgs = []
        self.prompt = "root@archiso ~ # "
        self.prompt_pos = 0
        self.is_busy = False
        
        self.cur_clr = CLR
        self.buf = ""
        self.hist = []; self.hist_idx = 0
        
        self.last_m = "None"
        self.last_resp = "None"
        
        self.spinning = False
        self.spin_pos = 0
        self.spin_i = 0
        self.spin_f = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spin_clrs = ["#ff1744", "#ff9100", "#ffea00", "#00e676", "#00e5ff", "#2979ff", "#d500f9"]
        self.spin_t = QTimer(self)
        self.spin_t.timeout.connect(self.spin_tick)

        self.on_chunk(BOOT)
        self.new_prompt()

    def spin_on(self):
        self.spinning = True
        self.spin_i = 0
        c = self.textCursor()
        c.movePosition(QTextCursor.MoveOperation.End)
        self.spin_pos = c.position()
        
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(self.spin_clrs[0]))
        c.insertText(self.spin_f[0], fmt)
        self.setTextCursor(c)
        self.spin_t.start(80)

    def spin_tick(self):
        if not self.spinning: return
        self.spin_i += 1
        f = self.spin_f[self.spin_i % len(self.spin_f)]
        col = self.spin_clrs[self.spin_i % len(self.spin_clrs)]
        
        c = self.textCursor()
        c.setPosition(self.spin_pos)
        c.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 1)
        
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(col))
        c.insertText(f, fmt)

    def spin_off(self):
        if self.spinning:
            self.spin_t.stop()
            self.spinning = False
            c = self.textCursor()
            c.setPosition(self.spin_pos)
            c.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 1)
            c.removeSelectedText()

    def on_status(self, txt):
        if self.spinning:
            self.spin_off()
            self.write_txt(txt, "#6272a4")
            self.spin_on()
        else:
            self.write_txt(txt, "#6272a4")

    def write_txt(self, txt, col):
        c = self.textCursor()
        c.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat(); fmt.setForeground(QColor(col))
        c.insertText(txt, fmt); self.setTextCursor(c)
        self.ensureCursorVisible()

    def new_prompt(self):
        c = self.textCursor(); c.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat(); fmt.setForeground(QColor("#ffffff"))
        c.insertText(self.prompt, fmt)
        fmt_t = QTextCharFormat(); fmt_t.setForeground(QColor(CLR))
        self.setCurrentCharFormat(fmt_t)
        self.setTextCursor(c); self.prompt_pos = self.textCursor().position()
        self.ensureCursorVisible()

    def stop_action(self):
        self.spin_off()
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.cancel(); self.worker.terminate(); self.worker.wait(100)
        self.buf = ""; self.cur_clr = CLR
        self.is_busy = False; self.setReadOnly(False)
        self.write_txt("^C\n", CLR); self.new_prompt()

    def replace_input(self, txt):
        c = self.textCursor(); c.setPosition(self.prompt_pos)
        c.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        c.removeSelectedText()
        fmt = QTextCharFormat(); fmt.setForeground(QColor(CLR))
        c.insertText(txt, fmt); self.setTextCursor(c)

    def keyPressEvent(self, e):
        if e.modifiers() == Qt.KeyboardModifier.ControlModifier and e.key() == Qt.Key.Key_C:
            self.stop_action(); return
        if e.key() == Qt.Key.Key_Escape:
            if self.is_busy: self.stop_action(); return
            else: self.close(); return
        if self.is_busy: e.ignore(); return

        c = self.textCursor(); pos = c.position()
        if e.key() == Qt.Key.Key_F11:
            self.is_fs = not self.is_fs
            if self.is_fs: self.showFullScreen()
            else: self.showNormal()
            return

        if e.modifiers() == Qt.KeyboardModifier.ControlModifier and e.key() == Qt.Key.Key_D:
            if not self.toPlainText()[self.prompt_pos:]: self.close(); return

        if e.key() == Qt.Key.Key_Backspace and pos <= self.prompt_pos: return
        if e.key() == Qt.Key.Key_Left and pos <= self.prompt_pos: return
        if e.key() == Qt.Key.Key_Home:
            c.setPosition(self.prompt_pos); self.setTextCursor(c); return
            
        if e.key() == Qt.Key.Key_Up:
            if self.hist and self.hist_idx > 0:
                self.hist_idx -= 1; self.replace_input(self.hist[self.hist_idx])
            return
            
        if e.key() == Qt.Key.Key_Down:
            if self.hist and self.hist_idx < len(self.hist) - 1:
                self.hist_idx += 1; self.replace_input(self.hist[self.hist_idx])
            else:
                self.hist_idx = len(self.hist); self.replace_input("")
            return

        if e.key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            c.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(c)
            cmd = self.toPlainText()[self.prompt_pos:].strip()
            
            if cmd:
                self.hist.append(cmd)
                self.hist_idx = len(self.hist)
                
            fmt = QTextCharFormat(); fmt.setForeground(QColor(CLR))
            c.insertText("\n", fmt); self.setTextCursor(c)
            
            self.run_cmd(cmd)
            return

        super().keyPressEvent(e)

    def run_cmd(self, cmd):
        if not cmd:
            self.new_prompt()
            return
            
        if cmd == ">zae show":
            d_txt = f"zae: model: {self.last_m}\nresponse:\n{self.last_resp}\n"
            self.write_txt(d_txt, "#ffff55")
            self.new_prompt()
            return
            
        self.state.parse_cmd(cmd)
        p_cwd = "~" if self.state.cwd == "/root" else self.state.cwd
        self.prompt = f"{self.state.user}@{self.state.hostname} {p_cwd} # "

        if cmd == "clear":
            self.clear(); self.new_prompt(); return
        elif cmd in ("exit", "poweroff", "shutdown now"):
            self.close(); return
        elif cmd == "reboot":
            self.clear(); self.on_chunk(BOOT); self.new_prompt(); return

        if not self.k:
            if cmd.startswith("gsk_"):
                with open(K_FILE, "w") as f: f.write(cmd)
                self.k = cmd
                self.write_txt("groq api key saved successfully\n", "#55ff55")
            else:
                self.write_txt("enter your groq api key (gsk_...):\n", "#ffff55")
            self.new_prompt()
            return

        self.is_busy = True; self.setReadOnly(True)
        self.msgs.append({"role": "user", "content": cmd})
        
        sys_cnt = PROMPT + "\n" + self.state.header()
        p_msgs = [{"role": "system", "content": sys_cnt}]
        
        for i, m in enumerate(self.msgs[-6:]):
            cnt = m["content"][-2000:]
            if i == len(self.msgs[-6:]) - 1 and m["role"] == "user":
                cnt = f"Simulate the terminal output for this command:\n{cnt}"
            p_msgs.append({"role": m["role"], "content": cnt})

        self.worker = Worker(self.k, p_msgs)
        self.worker.chunk.connect(self.on_chunk)
        self.worker.status.connect(self.on_status)
        self.worker.done.connect(self.on_done)
        self.worker.m_used.connect(lambda m: setattr(self, 'last_m', m))
        
        self.spin_on()
        self.worker.start()

    def on_chunk(self, chk):
        if self.spinning:
            self.spin_off()

        chk = chk.replace("```bash", "").replace("```text", "").replace("```", "")
        if not chk: return

        self.buf += chk
        while self.buf:
            tag_start = self.buf.find("<<")
            if tag_start == -1:
                self.write_txt(self.buf, self.cur_clr)
                self.buf = ""; break
            
            if tag_start > 0:
                txt_pre = self.buf[:tag_start]
                self.write_txt(txt_pre, self.cur_clr)
                self.buf = self.buf[tag_start:]
                continue
            
            tag_end = self.buf.find(">>")
            if tag_end == -1:
                if len(self.buf) > 60:
                    self.write_txt(self.buf, self.cur_clr)
                    self.buf = ""
                break
            
            tag_body = self.buf[2:tag_end].strip()
            self.buf = self.buf[tag_end+2:]
            self.apply_tag(tag_body)

    def apply_tag(self, tag):
        low = tag.lower()
        if low.startswith("color:"):
            v = low[6:].strip()
            if v == "reset": self.cur_clr = CLR
            elif v.startswith("#"): self.cur_clr = v
        elif low == "clear:zae_term":
            self.clear(); self.prompt_pos = 0
        elif low.startswith("timeout"):
            m = re.search(r'[\d\.]+', low)
            if m:
                ms = int(float(m.group(0)) * 1000)
                if ms > 0:
                    loop = QEventLoop(); QTimer.singleShot(min(ms, 1000), loop.quit); loop.exec()

    def on_done(self, raw_out):
        self.spin_off()
        self.last_resp = raw_out

        if self.buf:
            self.write_txt(self.buf, self.cur_clr)
            self.buf = ""

        if raw_out and not raw_out.endswith("\n"):
            self.write_txt("\n", CLR)

        if len(self.msgs) > 50:
            self.msgs = self.msgs[-20:]
            
        self.msgs.append({"role": "assistant", "content": raw_out[:1000]})
        self.is_busy = False; self.setReadOnly(False)
        self.new_prompt()

    def closeEvent(self, e):
        self.spin_off()
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.cancel(); self.worker.terminate()
        e.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    get_font()
    
    if sys.platform != "win32":
        for r in ["float", "center", "pin", "noborder", "bordersize 0", "noshadow", "noblur", "nodim", "opaque"]:
            subprocess.run(f"hyprctl keyword windowrulev2 '{r},title:^(ArchTTY)$' >/dev/null 2>&1", shell=True)
        
    win = Term(); win.show(); sys.exit(app.exec())
EOF
chmod +x ~/.local/bin/zae
