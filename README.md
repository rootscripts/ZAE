
<p align="center">
  <img src="data/zae.png" alt="ZAE" width="100%">
</p>

# ZAE

Virtual machine and OS emulator inside a GPU-accelerated terminal window. Type commands, simulate entire platforms (Arch Linux, Windows Vista/11, macOS, Custom Kernels), build projects, and run realistic scripts. Powered by Groq LLM inference with persistent VFS (Virtual File System) tracking.

ZAE renders an authentic TTY/CMD interface complete with boot screens, prompt feedback, command history, 24-bit ANSI colors, and an embedded retro IBM VGA font. All terminal output is hallucinated in real time without executing dangerous commands on your host system.

Works seamlessly on Linux (X11, Wayland, Hyprland) and Windows.

# WARNING
This is a pure AI-driven operating system simulator.
- Output is generated on the fly by language models.
- The emulator is completely sandboxed: commands like `rm -rf /` or `format C:` will **not** affect your real computer.
- Safe environment for testing, roleplaying, scripting experiments, and custom OS concepts.

## What it does

Enter any shell command (`ls`, `pacman -S neofetch`, `dir /s`, `color 1f`, `cat << 'EOF' > run.sh`). ZAE parses the state, tracks files locally inside its Virtual File System (VFS), queries the LLM, and streams back byte-perfect terminal output with ANSI colors and realistic typing latency.

## Requirements

- Python 3.10+
- PyQt6 (`pip install PyQt6`)
- Groq API key (free at [console.groq.com](https://console.groq.com))
- `certifi` on Windows (`pip install certifi`)

## Install

### Linux (native)

```bash
curl -fsSL [https://raw.githubusercontent.com/rootscripts/ZAE/main/install.sh](https://raw.githubusercontent.com/rootscripts/ZAE/main/install.sh) | bash

```

After install, restart your shell or run `export PATH="$HOME/.local/bin:$PATH"`, then launch:

```bash
zae

```

### Windows (unstable)

Open Command Prompt (cmd) as Administrator and run:

```cmd
curl -fsSL [https://raw.githubusercontent.com/rootscripts/ZAE/main/install.bat](https://raw.githubusercontent.com/rootscripts/ZAE/main/install.bat) -o %TEMP%\install_zae.bat && %TEMP%\install_zae.bat

```

Open a new Command Prompt window and launch:

```cmd
zae

```

### Manual install (any OS)

```bash
pip install PyQt6 certifi
curl -fsSL [https://raw.githubusercontent.com/rootscripts/ZAE/main/zae.py](https://raw.githubusercontent.com/rootscripts/ZAE/main/zae.py) -o zae.py
python3 zae.py

```

## First launch

On first run, paste your Groq API key (starts with `gsk_`) directly into the prompt. The key is saved to `~/.config/zae/groq_key` (Linux) or `%USERPROFILE%\.config\zae\groq_key` (Windows).

You can also pass it via environment variable:

```bash
export GROQ_API_KEY=gsk_your_key_here

```

## Controls

| Key | Action |
| --- | --- |
| Enter | Execute command |
| Ctrl+C | Interrupt / Cancel current generation |
| Esc | Exit application (or cancel execution) |
| F11 | Toggle Fullscreen mode |
| Ctrl+D | Exit (on empty prompt) |
| Up / Down | Navigate command history |

## Built-in `>zae` Engine Commands

Control the emulator state and configuration directly through internal `>zae` directives:

* **`>zae osinstall <OS_NAME>`**
Installs/switches to any target operating system on the fly. Automatically resets memory and reconfigures prompts, shells, directory paths, and command syntax:
```bash
>zae osinstall Windows Vista
>zae osinstall Ubuntu 24.04
>zae osinstall macOS Sonoma

```


Running `>zae osinstall` without arguments switches to **Custom OS mode** (scratch environment with toolchain utilities like `gcc`, `make`, `ld`, and `fdisk`).
* **`>zae model`**
Opens the interactive terminal GUI selector to swap Groq models in real time (`llama-3.1-8b-instant`, `llama-3.3-70b-versatile`, `openai/gpt-oss-120b`). Use `Up`/`Down` arrows to navigate and `Enter` to confirm.
* **`>zae reset`**
Performs a complete cold restart: clears VFS, purges conversation context, resets colors, and redraws the boot sequence.
* **`>zae show`**
Displays debug metadata: active model name and the raw, unparsed response string from the latest generation.
* **`gsk_...`**
Update your Groq API key on the fly by pasting a new key into the prompt.

## Shell Features & Virtual Filesystem (VFS)

* **Persistent VFS:** Writing files with `echo ... > file`, appending with `>>`, or creating multiline scripts via heredocs (`cat << 'EOF' > file`) stores the file in memory. Reading them via `cat` or `type` returns accurate contents.
* **Path Resolution:** Directory changes (`cd`, `pushd`, `popd`) accurately maintain state across relative and absolute paths for both Linux (`/`) and Windows (`\`).
* **Windows CMD Emulation:** Supports authentic `color XY` palette changes, native command parsing (`dir`, `cls`, `type`), and syntax errors on foreign Unix commands.
* **Interactive Prompts (`<<request>>`):** Automatically detects commands requesting user input (e.g. `passwd`, confirmation prompts, interactive installers), suspends execution, and passes the input back into the stream.
* **Token Pruning:** Maintains rolling message history and compresses verbose command outputs to avoid rate limits and context bloat.

## FAQ

**Q: Rate limit errors (HTTP 429)**

Groq free tier enforces token-per-minute (TPM) limits. ZAE features automatic context truncation, but if a limit occurs, wait for the displayed cooldown or paste a fresh key (`gsk_...`).

**Q: 404 Model Not Found**

Run `>zae model` to pick an active model. ZAE automatically removes deprecated models and falls back to `llama-3.1-8b-instant`.

**Q: SSL errors on Windows / `CERTIFICATE_VERIFY_FAILED**`

Install certifi (`pip install certifi`). ZAE includes automatic fallback routines for Windows certificate trust stores.

## Changelog

### v3.2.0

* **Dynamic OS Installation (`>zae osinstall`):** Added live switching between guest systems (Windows Vista/7/11, Arch, Ubuntu, macOS, or Custom OS toolchains).
* **Interactive Model Picker (`>zae model`):** In-terminal TUI menu for hot-swapping models without restarting.
* **VFS Overhaul:** Native support for multiline `cat << 'EOF'` heredocs and append redirection (`>>`).
* **Context Optimizer:** Rolling window compression to prevent TPM rate limits on repetitive or verbose commands (`dir /s`, dumps).
* **Removed Fake Status Markers:** Completely eliminated synthetic `"done"` outputs, allowing authentic shell silence and raw stream rendering.

### v3.1.0

* Added Windows CMD emulation engine with real-time `color` hex switching and Windows file path resolution.
* Added support for interactive prompts via `<<request>>` token handling.
* Enhanced ANSI 256-color and 24-bit TrueColor parsing routines.

### v3.0.0

* Complete migration to Groq streaming API with sub-second response times.
* Integrated IBM VGA 8x16 retro font autoloading.
* Added initial support for Hyprland window rules.

## License

MIT

```

