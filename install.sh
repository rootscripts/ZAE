#!/bin/bash
set -e

RAW="https://raw.githubusercontent.com/rootscripts/ZAE/main/zae.py"
BIN="$HOME/.local/bin"

mkdir -p "$BIN"

echo "[zae] downloading zae.py ..."
curl -fsSL "$RAW" -o "$BIN/zae.py"

cat > "$BIN/zae" << 'WRAPPER'
#!/bin/bash
exec python3 "$HOME/.local/bin/zae.py" "$@"
WRAPPER
chmod +x "$BIN/zae"

if ! echo "$PATH" | grep -q "$BIN"; then
    for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
        if [ -f "$rc" ]; then
            grep -q '.local/bin' "$rc" 2>/dev/null || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$rc"
        fi
    done
    export PATH="$BIN:$PATH"
fi

echo "[zae] installed. run: zae"
echo "[zae] if 'zae' is not found, restart your shell or run:"
echo "      export PATH=\"\$HOME/.local/bin:\$PATH\""
