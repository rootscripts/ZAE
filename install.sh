#!/bin/bash
set -e

RAW="https://raw.githubusercontent.com/rootscripts/ZAE/main/zae.py"
BIN="$HOME/.local/bin"
TARGET="$BIN/zae.py"
TEMP_FILE="$(mktemp)"

trap 'rm -f "$TEMP_FILE"' EXIT

mkdir -p "$BIN"

echo "[zae] checking for updates..."
curl -fsSL -H "Cache-Control: no-cache" "$RAW?t=$(date +%s)" -o "$TEMP_FILE"

if [ -f "$TARGET" ] && cmp -s "$TARGET" "$TEMP_FILE"; then
    echo "[zae] zae.py is already up to date. No changes made."
else
    if [ -f "$TARGET" ]; then
        echo "[zae] change detected. Removing old version..."
        rm -f "$TARGET"
    else
        echo "[zae] fresh installation detected..."
    fi

    echo "[zae] installing updated zae.py..."
    mv "$TEMP_FILE" "$TARGET"
    chmod 644 "$TARGET"

    cat > "$BIN/zae" << 'WRAPPER'
#!/bin/bash
exec python3 "$HOME/.local/bin/zae.py" "$@"
WRAPPER
    chmod +x "$BIN/zae"
    echo "[zae] updated and permissions reset."
fi

if ! echo "$PATH" | grep -q "$BIN"; then
    for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
        if [ -f "$rc" ]; then
            grep -q '.local/bin' "$rc" 2>/dev/null || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$rc"
        fi
    done
    export PATH="$BIN:$PATH"
fi

echo "[zae] ready. Run: zae"
