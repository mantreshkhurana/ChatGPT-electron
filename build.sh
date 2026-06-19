#!/usr/bin/env bash
set -euo pipefail
VER=${VER:-"local"}
BUILDROOT="$HOME/build/chatgpt-electron"
rm -rf "$BUILDROOT" && mkdir -p "$BUILDROOT"
cp -a "$HOME/.local/opt/electron-$VER" "$BUILDROOT/ChatGPT"
rm -f  "$BUILDROOT/ChatGPT/resources/app.asar"
mkdir -p "$BUILDROOT/ChatGPT/resources/app"
cp -a package.json main.js preload.js index.html assets src "$BUILDROOT/ChatGPT/resources/app/"
tar -C "$BUILDROOT" -czf "$HOME/rpmbuild/SOURCES/chatgpt-electron.tar.gz" ChatGPT
echo "OK: $HOME/rpmbuild/SOURCES/chatgpt-electron.tar.gz"

