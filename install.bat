@echo off
setlocal enabledelayedexpansion

echo [ZAE] Installing ZaeTerminal on Windows...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Error: Python is not installed or not added to PATH.
    echo Please install Python 3.10+ from python.org and check "Add Python to PATH".
    pause
    exit /b 1
)

python -c "import PyQt6" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ZAE] Installing PyQt6 dependency...
    python -m pip install PyQt6
)

set "TARGET_DIR=%USERPROFILE%\.local\bin"
set "CONFIG_DIR=%USERPROFILE%\.config\arch-greet\fonts"
set "APPS_DIR=%USERPROFILE%\AppData\Local\Microsoft\WindowsApps"

if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

(
echo import sys, os, time, subprocess, json, urllib.request, urllib.error, re
echo from PyQt6.QtWidgets import QApplication, QPlainTextEdit
echo from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QEventLoop
echo from PyQt6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QFontDatabase
echo.
echo CFG = os.path.expanduser("~/.config/arch-greet")
echo F_DIR = os.path.join(CFG, "fonts")
echo F_PATH = os.path.join(F_DIR, "PxPlus_IBM_VGA_8x16.ttf")
echo K_FILE = os.path.join(CFG, "groq_key")
echo os.makedirs(CFG, exist_ok=True)
echo os.makedirs(F_DIR, exist_ok=True)
echo.
echo CLR = "#b0b0b0"
echo UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 ZaeTerminal/2.0"
echo.
echo MODELS = [
echo     "llama-3.3-70b-versatile",
echo     "openai/gpt-oss-120b",
echo     "openai/gpt-oss-20b",
echo     "qwen/qwen3.8-27b",
echo     "llama-3.1-8b-instant"
echo ]
echo.
echo def get_k():
echo     if os.environ.get("GROQ_API_KEY"): return os.environ.get("GROQ_API_KEY").strip()
echo     if os.path.exists(K_FILE):
echo         with open(K_FILE, "r") as f:
echo             k = f.read().strip()
echo             if k: return k
echo     return ""
echo.
echo def get_m(k):
echo     if not k: return MODELS
echo     try:
echo         url = "https://api.groq.com/openai/v1/models"
echo         req = urllib.request.Request(url, headers={"Authorization": f"Bearer {k}", "User-Agent": UA})
echo         with urllib.request.urlopen(req, timeout=3.0) as resp:
echo             data = json.loads(resp.read().decode("utf-8"))
echo             live = [m["id"] for m in data.get("data", []) if not any(x in m["id"] for x in ("whisper", "guard", "embedding", "vision", "tool"))]
echo             if live:
echo                 return [m for m in MODELS if m in live] + [m for m in live if m not in MODELS]
echo     except Exception: pass
echo     return MODELS
echo.
echo def get_font():
echo     if not os.path.exists(F_PATH) or os.path.getsize(F_PATH) < 1000:
echo         urls = [
echo             "https://raw.githubusercontent.com/WheeledCord/tbwm/master/PxPlus_IBM_VGA_8x16.ttf",
echo             "https://raw.githubusercontent.com/industry-advance/industry-advance/master/Fonts/Px437_IBM_BIOS.ttf"
echo         ]
echo         for url in urls:
echo             try:
echo                 req = urllib.request.Request(url, headers={"User-Agent": UA})
echo                 with urllib.request.urlopen(req, timeout=3) as resp:
echo                     if resp.status == 200:
echo                         data = resp.read()
echo                         if len(data) > 1000:
echo                             with open(F_PATH, "wb") as f: f.write(data)
echo                             break
echo             except Exception: pass
echo     if os.path.exists(F_PATH):
echo         try:
echo             fid = QFontDatabase.addApplicationFont(F_PATH)
echo             if fid != -1:
echo                 fams = QFontDatabase.applicationFontFamilies(fid)
echo                 if fams: return fams[0]
echo         except Exception: pass
echo     return None
echo.
echo def mk_font(sz=12):
echo     f = QFont()
echo     f.setStyleHint(QFont.StyleHint.Monospace)
echo     f.setFixedPitch(True)
echo     f.setFamilies(["PxPlus IBM VGA 8x16", "Px437 IBM BIOS", "IBM Plex Mono", "JetBrains Mono", "Courier New", "monospace"])
echo     f.setPointSize(sz)
echo     return f
echo.
echo BOOT = r"""<<clear:zae_term>>
echo <<color:#ff1744>>███████╗ <<color:#ff9100>>█████╗  <<color:#ffea00>>███████╗
echo <<color:#ff007f>>╚══███╔╝<<color:#ffab00>>██╔══██╗<<color:#ffff00>>██╔════╝
echo <<color:#d500f9>>  ███╔╝ <<color:#00e676>>███████║<<color:#00e5ff>>█████╗  
echo <<color:#aa00ff>> ███╔╝  <<color:#00c853>>██╔══██║<<color:#00b0ff>>██╔══╝  
echo <<color:#651fff>>███████╗<<color:#1de9b6>>██║  ██║<<color:#2979ff>>███████╗
echo <<color:#3d5afe>>╚══════╝<<color:#00bfa5>>╚═╝  ╚═╝<<color:#304ffe>>╚══════╝<<color:reset>>
echo.
echo <<color:#ff007f>>:3<<color:reset>> <<color:#6272a4>>a virtual machine that can run any OS. Powered by Groq. github: @rootlesszen<<color:reset>>
echo <<timeout:0.18>>
echo BIOS Version 4.10-ZAE (CP437 IBM VGA text mode)
echo Memory Test: 16384KB OK<<timeout:0.10>>
echo Booting from Live Media (archiso_x86_64)...<<timeout:0.15>>
echo.
echo <<color:#55ff55>>[  OK  ]<<color:reset>> Started D-Bus System Message Bus.<<timeout:0.02>>
echo <<color:#55ff55>>[  OK  ]<<color:reset>> Started Network Time Synchronization.<<timeout:0.02>>
echo <<color:#55ff55>>[  OK  ]<<color:reset>> Reached target Multi-User System.<<timeout:0.05>>
echo.
echo Arch Linux 6.10.8-arch1 (tty1)
echo Type 'archinstall' to install. Press F11 for Fullscreen, Esc to exit.
echo """
echo.
echo class State:
echo     def __init__(self):
echo         self.os_name = "Arch Linux x86_64"
echo         self.hostname = "archiso"
echo         self.user = "root"
echo         self.cwd = "/root"
echo         self.files = {
echo             "/root/install.txt": "Guide: 1. fdisk /dev/sda 2. pacstrap /mnt base linux"
echo         }
echo.
echo     def parse_cmd(self, txt):
echo         t_pad = txt + "\n"
echo         for m in re.finditer(r'^cd\s+(.+)$', t_pad, re.MULTILINE):
echo             tgt = m.group(1).strip()
echo             if tgt in ("~", ""): self.cwd = "/root" if self.user == "root" else f"/home/{self.user}"
echo             elif tgt.startswith("/"): self.cwd = tgt
echo             elif tgt == "..":
echo                 pts = self.cwd.rstrip("/").split("/")
echo                 self.cwd = "/".join(pts[:-1]) if len(pts) > 1 else "/"
echo             else: self.cwd = f"{self.cwd.rstrip('/')}/{tgt}"
echo         
echo         for m in re.finditer(r'(?:hostnamectl\s+set-hostname|hostname)\s+([a-zA-Z0-9_\-]+)', t_pad):
echo             self.hostname = m.group(1)
echo             
echo         for m in re.finditer(r'cat\s*<<\s*[\'"]?(\w+)[\'"]?\s*>\s*(\S+)\n(.*?)\n\1', t_pad, re.DOTALL):
echo             self.write_f(m.group(2), m.group(3).strip())
echo             
echo         for m in re.finditer(r'echo\s+[\'"]?(.*?)[\'"]?\s*>\s*(\S+)', t_pad):
echo             self.write_f(m.group(2), m.group(1))
echo.
echo     def write_f(self, raw_path, content):
echo         if raw_path.startswith("~/"):
echo             home = "/root" if self.user == "root" else f"/home/{self.user}"
echo             raw_path = home + "/" + raw_path[2:]
echo             
echo         path = raw_path if raw_path.startswith("/") else f"{self.cwd.rstrip('/')}/{raw_path}"
echo         if "os-release" in path:
echo             m = re.search(r'(?:PRETTY_NAME|NAME)\s*=\s*["\']?([^"\']+)["\']?', content)
echo             if m: self.os_name = m.group(1).strip()
echo         self.files[path] = content
echo.
echo     def header(self):
echo         compact_files = []
echo         for k, v in list(self.files.items())[-8:]:
echo             c_val = v[:3000]
echo             display_k = k.replace("/root/", "~/") if self.user == "root" else k
echo             compact_files.append(f"File: {display_k}\n{c_val}\n")
echo         f_str = "\n".join(compact_files)
echo         return f"[STATE: OS='{self.os_name}' HOST='{self.hostname}' USER='{self.user}' CWD='{self.cwd}']\n{f_str}\n"
echo.
echo PROMPT = r"""You are a strict, authentic command-line terminal simulation. You are NOT an AI assistant. Do NOT converse.
echo.
echo TAGS YOU CAN USE:
echo 1. <<color:#HEX>> : Set text color.
echo 2. <<color:reset>> : Reset color to default gray.
echo 3. <<timeout:X>> : Pause output for X seconds.
echo 4. <<clear:zae_term>> : Clear screen.
echo.
echo CRITICAL RULES:
echo - NEVER reply with conversational text.
echo - Output ONLY raw terminal text. NEVER use markdown codeblocks.
echo - If a command produces no stdout (like successful 'mkdir', 'touch', 'cd', 'cat >'), OUTPUT NOTHING.
echo - If a command naturally produces output (e.g., 'python3', 'echo', 'curl', 'tree', 'dir', 'dmesg', 'ls'), YOU MUST OUTPUT THE RESULT. DO NOT BE SILENT.
echo - If the user types 'cmd', 'windows', or 'cmd.exe', instantly switch your context to simulate a Microsoft Windows Command Prompt (C:\>).
echo - If the user types a Windows `color` command (e.g. `color 0a`, `color 5`), YOU MUST ACTUALLY APPLY the corresponding `<<color:#HEX>>` tag.
echo.
echo FASTFETCH INSTRUCTIONS:
echo When the user runs 'fastfetch' or 'neofetch':
echo 1. If ~/.config/fastfetch/logo.txt exists in [STATE], output the FULL custom logo EXACTLY as written. Output specs directly BELOW the logo.
echo 2. If NO custom logo exists, use this exact side-by-side Arch template:
echo <<color:#1793d1>>       /\         <<color:reset>> {USER}@{HOST}
echo <<color:#1793d1>>      /  \        <<color:reset>> --------------
echo <<color:#1793d1>>     /\   \       <<color:reset>> OS: {OS}
echo <<color:#1793d1>>    /      \      <<color:reset>> Host: {HOST}
echo <<color:#1793d1>>   /   ,,   \     <<color:reset>> Kernel: Linux 6.10.8
echo <<color:#1793d1>>  /   |  |  -\    <<color:reset>> Shell: bash
echo <<color:#1793d1>> /_-''    ''-_\  <<color:reset>> Memory: 1.2GiB / 16.0GiB
echo """
echo.
echo class Worker(QThread):
echo     chunk = pyqtSignal(str)
echo     status = pyqtSignal(str)
echo     done = pyqtSignal(str)
echo     m_used = pyqtSignal(str)
echo.
echo     def __init__(self, k, msgs):
echo         super().__init__()
echo         self.k = k
echo         self.msgs = msgs
echo         self.cancelled = False
echo         self.models = get_m(k)
echo.
echo     def cancel(self):
echo         self.cancelled = True
echo.
echo     def run(self):
echo         w_time = "a few seconds"
echo         err_code = None
echo         
echo         for m in self.models:
echo             if self.cancelled: return
echo             url = "https://api.groq.com/openai/v1/chat/completions"
echo             payload = {
echo                 "model": m,
echo                 "messages": self.msgs,
echo                 "temperature": 0.2,
echo                 "max_completion_tokens": 1400,
echo                 "stream": True
echo             }
echo             try:
echo                 self.m_used.emit(m)
echo                 req = urllib.request.Request(
echo                     url,
echo                     data=json.dumps(payload).encode("utf-8"),
echo                     headers={"Authorization": f"Bearer {self.k}", "Content-Type": "application/json", "User-Agent": UA}
echo                 )
echo                 buf_txt = []
echo                 with urllib.request.urlopen(req, timeout=6) as resp:
echo                     for raw_line in resp:
echo                         if self.cancelled: return
echo                         line = raw_line.decode("utf-8", errors="ignore").strip()
echo                         if not line or not line.startswith("data:"): continue
echo                         d_str = line[5:].strip()
echo                         if d_str == "[DONE]": break
echo                         try:
echo                             chunk = json.loads(d_str)
echo                             delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
echo                             if delta:
echo                                 buf_txt.append(delta)
echo                                 self.chunk.emit(delta)
echo                         except Exception: continue
echo.
echo                 ans = "".join(buf_txt)
echo                 self.done.emit(ans.rstrip())
echo                 return
echo                 
echo             except urllib.error.HTTPError as e:
echo                 if self.cancelled: return
echo                 err_code = e.code
echo                 if e.code == 401:
echo                     self.chunk.emit("<<color:#ff5555>>groq api key invalid<<color:reset>>\n")
echo                     self.done.emit("")
echo                     return
echo                 elif e.code == 403:
echo                     self.chunk.emit("<<color:#ff5555>>groq: HTTP 403 Forbidden :( Turn on VPN or check key.<<color:reset>>\n")
echo                     self.done.emit("")
echo                     return
echo                     
echo                 rt = e.headers.get('x-ratelimit-reset-tokens')
echo                 rr = e.headers.get('x-ratelimit-reset-requests')
echo                 ra = e.headers.get('retry-after')
echo                 
echo                 if rt: w_time = f"{rt}s"
echo                 elif rr: w_time = f"{rr}s"
echo                 elif ra: w_time = f"{ra}s"
echo                 else:
echo                     try:
echo                         body = e.read().decode("utf-8", errors="ignore")
echo                         match = re.search(r'try again in ([\w\.]+)', body, re.IGNORECASE)
echo                         if match: w_time = match.group(1).rstrip('.')
echo                     except: pass
echo                 
echo                 time.sleep(0.2)
echo                 continue
echo             except Exception:
echo                 if self.cancelled: return
echo                 time.sleep(0.2)
echo                 continue
echo.
echo         if not self.cancelled:
echo             if err_code == 429:
echo                 self.chunk.emit(f"<<color:#ff5555>>groq: rate limit cooldown active :( Please wait {w_time}.<<color:reset>>\n")
echo             elif err_code == 400:
echo                 self.chunk.emit("<<color:#ff5555>>groq: context window full :( Type 'clear'.<<color:reset>>\n")
echo             elif err_code != 403:
echo                 self.chunk.emit(f"<<color:#ff5555>>groq: API error {err_code} :( Please try again.<<color:reset>>\n")
echo             self.done.emit("")
echo.
echo class Term(QPlainTextEdit):
echo     def __init__(self):
echo         super().__init__()
echo         self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
echo         self.setWindowTitle("ArchTTY")
echo         self.resize(920, 580)
echo         
echo         self.k = get_k()
echo         self.is_fs = False
echo         
echo         self.setFont(mk_font(12))
echo         self.setCursorWidth(9)
echo         self.setStyleSheet("""
echo             QPlainTextEdit {
echo                 background-color: #000000;
echo                 color: #b0b0b0;
echo                 selection-background-color: #2e3440;
echo                 selection-color: #ffffff;
echo                 border: none;
echo                 padding: 4px;
echo                 margin: 0px;
echo                 line-height: 1.22;
echo             }
echo             QScrollBar:vertical { width: 0px; height: 0px; background: transparent; }
echo             QScrollBar:horizontal { width: 0px; height: 0px; background: transparent; }
echo         """)
echo         self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
echo         self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
echo         
echo         self.state = State()
echo         self.msgs = []
echo         self.prompt = "root@archiso ~ # "
echo         self.prompt_pos = 0
echo         self.is_busy = False
echo         
echo         self.cur_clr = CLR
echo         self.buf = ""
echo         self.hist = []; self.hist_idx = 0
echo         
echo         self.last_m = "None"
echo         self.last_resp = "None"
echo         
echo         self.spinning = False
echo         self.spin_pos = 0
echo         self.spin_i = 0
echo         self.spin_f = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
echo         self.spin_clrs = ["#ff1744", "#ff9100", "#ffea00", "#00e676", "#00e5ff", "#2979ff", "#d500f9"]
echo         self.spin_t = QTimer(self)
echo         self.spin_t.timeout.connect(self.spin_tick)
echo.
echo         self.on_chunk(BOOT)
echo         self.new_prompt()
echo.
echo     def spin_on(self):
echo         self.spinning = True
echo         self.spin_i = 0
echo         c = self.textCursor()
echo         c.movePosition(QTextCursor.MoveOperation.End)
echo         self.spin_pos = c.position()
echo         
echo         fmt = QTextCharFormat()
echo         fmt.setForeground(QColor(self.spin_clrs[0]))
echo         c.insertText(self.spin_f[0], fmt)
echo         self.setTextCursor(c)
echo         self.spin_t.start(80)
echo.
echo     def spin_tick(self):
echo         if not self.spinning: return
echo         self.spin_i += 1
echo         f = self.spin_f[self.spin_i %% len(self.spin_f)]
echo         col = self.spin_clrs[self.spin_i %% len(self.spin_clrs)]
echo         
echo         c = self.textCursor()
echo         c.setPosition(self.spin_pos)
echo         c.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 1)
echo         
echo         fmt = QTextCharFormat()
echo         fmt.setForeground(QColor(col))
echo         c.insertText(f, fmt)
echo.
echo     def spin_off(self):
echo         if self.spinning:
echo             self.spin_t.stop()
echo             self.spinning = False
echo             c = self.textCursor()
echo             c.setPosition(self.spin_pos)
echo             c.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 1)
echo             c.removeSelectedText()
echo.
echo     def on_status(self, txt):
echo         if self.spinning:
echo             self.spin_off()
echo             self.write_txt(txt, "#6272a4")
echo             self.spin_on()
echo         else:
echo             self.write_txt(txt, "#6272a4")
echo.
echo     def write_txt(self, txt, col):
echo         c = self.textCursor()
echo         c.movePosition(QTextCursor.MoveOperation.End)
echo         fmt = QTextCharFormat(); fmt.setForeground(QColor(col))
echo         c.insertText(txt, fmt); self.setTextCursor(c)
echo         self.ensureCursorVisible()
echo.
echo     def new_prompt(self):
echo         c = self.textCursor(); c.movePosition(QTextCursor.MoveOperation.End)
echo         fmt = QTextCharFormat(); fmt.setForeground(QColor("#ffffff"))
echo         c.insertText(self.prompt, fmt)
echo         fmt_t = QTextCharFormat(); fmt_t.setForeground(QColor(CLR))
echo         self.setCurrentCharFormat(fmt_t)
echo         self.setTextCursor(c); self.prompt_pos = self.textCursor().position()
echo         self.ensureCursorVisible()
echo.
echo     def stop_action(self):
echo         self.spin_off()
echo         if hasattr(self, 'worker') and self.worker.isRunning():
echo             self.worker.cancel(); self.worker.terminate(); self.worker.wait(100)
echo         self.buf = ""; self.cur_clr = CLR
echo         self.is_busy = False; self.setReadOnly(False)
echo         self.write_txt("^C\n", CLR); self.new_prompt()
echo.
echo     def replace_input(self, txt):
echo         c = self.textCursor(); c.setPosition(self.prompt_pos)
echo         c.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
echo         c.removeSelectedText()
echo         fmt = QTextCharFormat(); fmt.setForeground(QColor(CLR))
echo         c.insertText(txt, fmt); self.setTextCursor(c)
echo.
echo     def keyPressEvent(self, e):
echo         if e.modifiers() == Qt.KeyboardModifier.ControlModifier and e.key() == Qt.Key.Key_C:
echo             self.stop_action(); return
echo         if e.key() == Qt.Key.Key_Escape:
echo             if self.is_busy: self.stop_action(); return
echo             else: self.close(); return
echo         if self.is_busy: e.ignore(); return
echo.
echo         c = self.textCursor(); pos = c.position()
echo         if e.key() == Qt.Key.Key_F11:
echo             self.is_fs = not self.is_fs
echo             if self.is_fs: self.showFullScreen()
echo             else: self.showNormal()
echo             return
echo.
echo         if e.modifiers() == Qt.KeyboardModifier.ControlModifier and e.key() == Qt.Key.Key_D:
echo             if not self.toPlainText()[self.prompt_pos:]: self.close(); return
echo.
echo         if e.key() == Qt.Key.Key_Backspace and pos <= self.prompt_pos: return
echo         if e.key() == Qt.Key.Key_Left and pos <= self.prompt_pos: return
echo         if e.key() == Qt.Key.Key_Home:
echo             c.setPosition(self.prompt_pos); self.setTextCursor(c); return
echo             
echo         if e.key() == Qt.Key.Key_Up:
echo             if self.hist and self.hist_idx > 0:
echo                 self.hist_idx -= 1; self.replace_input(self.hist[self.hist_idx])
echo             return
echo             
echo         if e.key() == Qt.Key.Key_Down:
echo             if self.hist and self.hist_idx < len(self.hist) - 1:
echo                 self.hist_idx += 1; self.replace_input(self.hist[self.hist_idx])
echo             else:
echo                 self.hist_idx = len(self.hist); self.replace_input("")
echo             return
echo.
echo         if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
echo             c.movePosition(QTextCursor.MoveOperation.End)
echo             self.setTextCursor(c)
echo             cmd = self.toPlainText()[self.prompt_pos:].strip()
echo             
echo             if cmd:
echo                 self.hist.append(cmd)
echo                 self.hist_idx = len(self.hist)
echo                 
echo             fmt = QTextCharFormat(); fmt.setForeground(QColor(CLR))
echo             c.insertText("\n", fmt); self.setTextCursor(c)
echo             
echo             self.run_cmd(cmd)
echo             return
echo.
echo         super().keyPressEvent(e)
echo.
echo     def run_cmd(self, cmd):
echo         if not cmd:
echo             self.new_prompt()
echo             return
echo             
echo         if cmd == ">zae show":
echo             d_txt = f"zae: model: {self.last_m}\nresponse:\n{self.last_resp}\n"
echo             self.write_txt(d_txt, "#ffff55")
echo             self.new_prompt()
echo             return
echo             
echo         self.state.parse_cmd(cmd)
echo         p_cwd = "~" if self.state.cwd == "/root" else self.state.cwd
echo         self.prompt = f"{self.state.user}@{self.state.hostname} {p_cwd} # "
echo.
echo         if cmd == "clear":
echo             self.clear(); self.new_prompt(); return
echo         elif cmd in ("exit", "poweroff", "shutdown now"):
echo             self.close(); return
echo         elif cmd == "reboot":
echo             self.clear(); self.on_chunk(BOOT); self.new_prompt(); return
echo.
echo         if not self.k:
echo             if cmd.startswith("gsk_"):
echo                 with open(K_FILE, "w") as f: f.write(cmd)
echo                 self.k = cmd
echo                 self.write_txt("groq api key saved successfully\n", "#55ff55")
echo             else:
echo                 self.write_txt("enter your groq api key (gsk_...):\n", "#ffff55")
echo             self.new_prompt()
echo             return
echo.
echo         self.is_busy = True; self.setReadOnly(True)
echo         self.msgs.append({"role": "user", "content": cmd})
echo         
echo         sys_cnt = PROMPT + "\n" + self.state.header()
echo         p_msgs = [{"role": "system", "content": sys_cnt}]
echo         
echo         for i, m in enumerate(self.msgs[-6:]):
echo             cnt = m["content"][-2000:]
echo             if i == len(self.msgs[-6:]) - 1 and m["role"] == "user":
echo                 cnt = f"Simulate the terminal output for this command:\n{cnt}"
echo             p_msgs.append({"role": m["role"], "content": cnt})
echo.
echo         self.worker = Worker(self.k, p_msgs)
echo         self.worker.chunk.connect(self.on_chunk)
echo         self.worker.status.connect(self.on_status)
echo         self.worker.done.connect(self.on_done)
echo         self.worker.m_used.connect(lambda m: setattr(self, 'last_m', m))
echo         
echo         self.spin_on()
echo         self.worker.start()
echo.
echo     def on_chunk(self, chk):
echo         if self.spinning:
echo             self.spin_off()
echo.
echo         chk = chk.replace("```bash", "").replace("```text", "").replace("```", "")
echo         if not chk: return
echo.
echo         self.buf += chk
echo         while self.buf:
echo             tag_start = self.buf.find("<<")
echo             if tag_start == -1:
echo                 self.write_txt(self.buf, self.cur_clr)
echo                 self.buf = ""; break
echo             
echo             if tag_start > 0:
echo                 txt_pre = self.buf[:tag_start]
echo                 self.write_txt(txt_pre, self.cur_clr)
echo                 self.buf = self.buf[tag_start:]
echo                 continue
echo             
echo             tag_end = self.buf.find(">>")
echo             if tag_end == -1:
echo                 if len(self.buf) > 60:
echo                     self.write_txt(self.buf, self.cur_clr)
echo                     self.buf = ""
echo                 break
echo             
echo             tag_body = self.buf[2:tag_end].strip()
echo             self.buf = self.buf[tag_end+2:]
echo             self.apply_tag(tag_body)
echo.
echo     def apply_tag(self, tag):
echo         low = tag.lower()
echo         if low.startswith("color:"):
echo             v = low[6:].strip()
echo             if v == "reset": self.cur_clr = CLR
echo             elif v.startswith("#"): self.cur_clr = v
echo         elif low == "clear:zae_term":
echo             self.clear(); self.prompt_pos = 0
echo         elif low.startswith("timeout"):
echo             m = re.search(r'[\d\.]+', low)
echo             if m:
echo                 ms = int(float(m.group(0)) * 1000)
echo                 if ms > 0:
echo                     loop = QEventLoop(); QTimer.singleShot(min(ms, 1000), loop.quit); loop.exec()
echo.
echo     def on_done(self, raw_out):
echo         self.spin_off()
echo         self.last_resp = raw_out
echo.
echo         if self.buf:
echo             self.write_txt(self.buf, self.cur_clr)
echo             self.buf = ""
echo.
echo         if raw_out and not raw_out.endswith("\n"):
echo             self.write_txt("\n", CLR)
echo.
echo         if len(self.msgs) > 50:
echo             self.msgs = self.msgs[-20:]
echo             
echo         self.msgs.append({"role": "assistant", "content": raw_out[:1000]})
echo         self.is_busy = False; self.setReadOnly(False)
echo         self.new_prompt()
echo.
echo     def closeEvent(self, e):
echo         self.spin_off()
echo         if hasattr(self, 'worker') and self.worker.isRunning():
echo             self.worker.cancel(); self.worker.terminate()
echo         e.accept()
echo.
echo if __name__ == "__main__":
echo     app = QApplication(sys.argv)
echo     get_font()
echo     
echo     if sys.platform != "win32":
echo         for r in ["float", "center", "pin", "noborder", "bordersize 0", "noshadow", "noblur", "nodim", "opaque"]:
echo             subprocess.run(f"hyprctl keyword windowrulev2 '{r},title:^(ArchTTY)$' >/dev/null 2>&1", shell=True)
echo         
echo     win = Term(); win.show(); sys.exit(app.exec())
) > "%TARGET_DIR%\zae.py"

(
echo @echo off
echo python "%%USERPROFILE%%\.local\bin\zae.py" %%*
) > "%APPS_DIR%\zae.bat"

echo [ZAE] Installation finished! Open CMD or PowerShell and type 'zae' to start.
pause
