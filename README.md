![ZAE Banner](data/zae.png)

# ZAE.

A terminal OS simulator that runs entirely inside an LLM context on Groq LPUs. It boots into an Arch Linux live ISO by default, but can simulate any Linux distro, BSD, or switch into a Windows CMD/DOS prompt on the fly.

It is written in Python (PyQt6) with real-time SSE streaming, custom CP437 IBM VGA font rendering, and a state tracker so the AI does not forget created files or hostname changes.

IT IS FOR FUN and not production. Made entirely for fun and joy. 
The AI can only access ZAE terminal, and cannot go into your PC.
## How it works

ZAE sends shell inputs to Groq's open-weights models (`llama-3.3-70b` / `gpt-oss`) over SSE streams at ~500 tokens/second. Instead of executing local binaries, the model predicts terminal stdout, error codes, and formatting in real-time.

A lightweight client-side state tracker watches your inputs (`cat << EOF`, `hostnamectl`, `cd`, `mkdir`) and injects a ~30-token header before each request. This keeps file paths, custom fastfetch configs, and hostnames persistent across sessions without blowing up token limits.

## Installation

### Linux

Run the installer script:

```
curl -sSL https://raw.githubusercontent.com/rootscripts/ZAE/main/install.sh -o install.sh && chmod +x install.sh && ./install.sh && rm install.sh
```
The installer places the executable in ~/.local/bin/zae and ensures it is in your $PATH.

### Windows

Ensure Python 3.10+ is installed and added to PATH.

Open PowerShell, not cmd:

```
iwr -useb https://raw.githubusercontent.com/rootscripts/ZAE/main/install.bat -OutFile install.bat; .\install.bat; Remove-Item install.bat
```
The installer configures PyQt6 and creates a zae launcher in your WindowsApps directory.
Usage

Run the terminal from any console:
```
zae
```
On first launch, enter your Groq API key (starts with gsk_). 
You can get a free key at https://console.groq.com.
It's completely free and possible to do in 1 minute.

### Keybinds & commands

F11: Toggle fullscreen

Ctrl+C: Interrupt current command / stream immediately

Ctrl+D: Exit if input line is empty

Esc: Stop active command or exit

`>zae show` : Debug command that displays the raw LLM response and active model

### Fun things to try
`fastfetch`

`alias windows="cmd.exe"` then `color 0e & echo I'm yellow`

`fortune | cowsay`

`sudo rm -rf / --no-preserve-root` Deletes your entire TTY and then `reboot` to make it like nothing happened

Making your own OS or distro

### FAQ

## "Rate limit, try again in ...s"

This means you were rate limited by Groq. 

You should try waiting the time said. If the rate limit doesn't dissapear, wait a day to reset your quota.

Normally the quota is very big so u can do alot of things but if u got rate limited, it's probably ur executing 1000+ commands

## "404/403/400 error on groq"

This means the ZAE terminal AI isn't working. Try posting it on Issues, i'll resolve the problem.

## "5** error on groq"

This means Groq AI isn't working and you should wait, ZAE has nothing to do with it.
