<p align="center">
  <img src="data/zae.png" alt="ZAE" width="100%">
</p>

# ZAE

Virtual machine emulator in a terminal window. Type Linux commands, get realistic output. Runs on Groq LLM inference.

ZAE renders a fake Arch Linux TTY with a boot sequence, prompt, command history, colored output. Commands are sent to Groq API which returns simulated terminal output. Supports custom tags for colors, timeouts, screen clear.

Works on Linux (X11, Wayland, Hyprland) and Windows.

## What it does

You type a command like `ls`, `ping google.com`, `fastfetch`, `cowsay hello`. ZAE sends it to Groq, gets back what a real terminal would print, and renders it in the window with color support and a retro IBM VGA font.

Not a real shell. No actual commands are executed on your machine.

## Requirements

- Python 3.10+
- PyQt6 (`pip install PyQt6`)
- Groq API key (free at [console.groq.com](https://console.groq.com))
- `certifi` on Windows (`pip install certifi`)

## Install

### Linux (native)

```bash
curl -fsSL https://raw.githubusercontent.com/rootscripts/ZAE/main/install.sh | bash
```

This downloads `zae.py` to `~/.local/bin/`, creates a `zae` launcher, and adds it to PATH. Works on any distro.

After install, restart your shell (or run `export PATH="$HOME/.local/bin:$PATH"`) and type:

```
zae
```

### Windows (unstable!!)

Open Command Prompt (cmd) as admin and run:

```cmd
curl -fsSL https://raw.githubusercontent.com/rootscripts/ZAE/main/install.bat -o %TEMP%\install_zae.bat && %TEMP%\install_zae.bat
```

The script finds your Python install automatically, downloads `zae.py` to `%USERPROFILE%\.zae\`, creates `zae.bat`, and adds it to PATH.

After install, open a new cmd window and type:

```
zae
```

### Manual install (any OS)

```bash
pip install PyQt6 certifi
curl -fsSL https://raw.githubusercontent.com/rootscripts/ZAE/main/zae.py -o zae.py
python3 zae.py
```

## First launch

On first run ZAE will ask for your Groq API key. Paste it (starts with `gsk_`) and press Enter. The key is saved to `~/.config/zae/groq_key` (Linux) or `%USERPROFILE%\.config\zae\groq_key` (Windows).

You can also set it as an environment variable:

```bash
export GROQ_API_KEY=gsk_your_key_here
```

## Controls

| Key | Action |
|---|---|
| Enter | Execute command |
| Ctrl+C | Cancel current request / interrupt |
| Esc | Exit (or cancel if busy) |
| F11 | Toggle fullscreen |
| Ctrl+D | Exit (on empty prompt) |
| Up/Down | Command history |

## Built-in commands

- `clear` — clear screen
- `reboot` — replay boot sequence
- `exit` / `poweroff` — close ZAE
- `>zae show` — debug info (last model used, raw response)

## FAQ

**Q: SSL errors on Windows / `CERTIFICATE_VERIFY_FAILED`**

ZAE disables strict SSL verification on Windows by default. If you still get errors, install certifi:
```
pip install certifi
```
If that doesn't help, your network might be blocking Groq API. Try a VPN.

**Q: `zae` command not found after install**

Linux: restart your shell or run `source ~/.bashrc`. Make sure `~/.local/bin` is in your PATH.

Windows: open a new cmd window. The installer adds the path via `setx` which only applies to new sessions.

**Q: Python not found (Windows)**

Install Python from [python.org](https://python.org). During install, check "Add Python to PATH". If already installed but the installer can't find it, run `where python` to check.

**Q: Window won't close / freezes (Windows)**

Fixed in current version. ZAE now uses standard window decorations on Windows (title bar with close button). Click the X or press Esc.

**Q: 403 Forbidden from Groq**

Your IP might be blocked. Use a VPN. Or your API key is wrong — regenerate it at console.groq.com.

**Q: Rate limit errors**

Groq free tier has rate limits. Wait the time shown in the error message. ZAE automatically tries multiple models if one is rate-limited.

**Q: Model is hallucinating / giving weird output**

Fixed in current version. Temperature is set to 0.0 and the system prompt is strict. If you still see odd output, type `clear` to reset context and try again.

**Q: PyQt6 import error**

```
pip install PyQt6
```

On some Linux distros you might need the system package instead:
```
sudo pacman -S python-pyqt6        # Arch
sudo apt install python3-pyqt6     # Debian/Ubuntu
sudo dnf install python3-qt6       # Fedora
```

## License

MIT
