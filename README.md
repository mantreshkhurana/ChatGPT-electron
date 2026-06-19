<img src="./assets/icons/png/favicon.png" width="50" height="50" />

# ChatGPT Desktop (Electron Wrapper)

[![Stars](https://img.shields.io/github/stars/mantreshkhurana/ChatGPT-electron?style=social)](https://github.com/mantreshkhurana/ChatGPT-electron)

Lightweight desktop wrapper for the **ChatGPT web app** (`https://chat.openai.com`). No API keys required. Runs with a local Electron runtime and can optionally be packaged as an RPM.

> Note: Google/Microsoft login can block embedded web views. Recommended: sign in using the **system browser** or use email/password.

---

## Contents

- [Prerequisites](#prerequisites)
- [Quick start (local Electron runtime)](#quick-start-local-electron-runtime)
- [Build without internet access](#build-without-internet-access)
- [Build RPM for Fedora](#build-rpm-for-fedora)
- [Startup options (Wayland/X11, GPU)](#startup-options-waylandx11-gpu)
- [Proxy notes](#proxy-notes)
- [Downloads / Releases](#downloads--releases)
- [Credits & License](#credits--license)

---

## Prerequisites

- Node.js ≥ 18 (only for development tasks, **not** required at runtime)
- Linux x86_64
- For media: `gstreamer1`, `gstreamer1-plugins-base`
- For EGL/GLX: Mesa stack (`mesa-libEGL`, `mesa-libgbm`, `mesa-dri-drivers`)
- Optional (RPM): `rpmbuild`

Fedora:
```bash
sudo dnf install -y   gstreamer1 gstreamer1-plugins-base   mesa-libEGL mesa-libgbm mesa-dri-drivers   libX11 libXcomposite libXdamage libXfixes libXrandr libXi libXScrnSaver at-spi2-core   rpm-build
```

---

## Quick start (local Electron runtime)

1) Clone the repository:
```bash
git clone https://github.com/mantreshkhurana/ChatGPT-electron.git
cd ChatGPT-electron
```

2) Determine the required Electron version:
```bash
VER=$(node -p "let p=require('./package.json');(p.devDependencies?.electron||p.dependencies?.electron||'').replace(/^[^0-9]*/,'')")
echo "$VER"
```

3) Provide Electron **without npm**:
```bash
mkdir -p ~/.cache/electron/v$VER
cd ~/.cache/electron/v$VER

# Download ZIP (proxy notes below)
curl -fL -o electron-v$VER-linux-x64.zip   https://github.com/electron/electron/releases/download/v$VER/electron-v$VER-linux-x64.zip

# Generate checksum locally (optional)
sha256sum electron-v$VER-linux-x64.zip | awk '{print $1"  electron-v'"$VER"'-linux-x64.zip"}' > SHASUMS256.txt

# Unpack
mkdir -p ~/.local/opt/electron-$VER
unzip -o electron-v$VER-linux-x64.zip -d ~/.local/opt/electron-$VER

# Convenient symlink
mkdir -p ~/.local/bin
ln -sf ~/.local/opt/electron-$VER/electron ~/.local/bin/electron-$VER
```

4) Start:
```bash
~/.local/bin/electron-$VER . --disable-gpu --use-gl=desktop
```

---

## Build **without internet access**

If `npm install` fails because of proxy/SSL restrictions, start the app directly with the **local Electron runtime** (see above). For a bundle:

```bash
# Bundle app into Electron runtime
BUILDROOT="$HOME/build/chatgpt-electron"
rm -rf "$BUILDROOT" && mkdir -p "$BUILDROOT"

VER=$(node -p "let p=require('./package.json');(p.devDependencies?.electron||p.dependencies?.electron||'').replace(/^[^0-9]*/,'')")

cp -a ~/.local/opt/electron-$VER "$BUILDROOT/ChatGPT"
rm -f  "$BUILDROOT/ChatGPT/resources/app.asar"
mkdir -p "$BUILDROOT/ChatGPT/resources/app"
cp -a package.json main.js preload.js index.html assets src "$BUILDROOT/ChatGPT/resources/app/"

# Start script
install -Dm755 /dev/stdin "$BUILDROOT/ChatGPT/ChatGPT.sh" <<'EOF'
#!/usr/bin/env bash
BASEDIR="$(cd "$(dirname "$0")" && pwd)"
exec "$BASEDIR/electron" "$BASEDIR/resources/app" --disable-gpu --use-gl=desktop "$@"
EOF
```

Afterward, a runnable portable version is available at `~/build/chatgpt-electron/ChatGPT`.

---

## Build RPM for Fedora

1) Create rpmbuild tree:
```bash
mkdir -p ~/rpmbuild/{SPECS,BUILD,RPMS,SOURCES,SRPMS}
tar -C "$BUILDROOT" -czf ~/rpmbuild/SOURCES/chatgpt-electron.tar.gz ChatGPT
```

2) Use SPEC:
```spec
%global debug_package %{nil}
%undefine _debugsource_packages

Name:           chatgpt-electron
Version:        1.0
Release:        1%{?dist}
Summary:        ChatGPT Desktop (Electron, bundled offline)
License:        MIT
URL:            https://github.com/mantreshkhurana/ChatGPT-electron
BuildArch:      x86_64
Requires:       libX11, libXcomposite, libXdamage, libXfixes, libXrandr, libXi, libXScrnSaver, at-spi2-core, mesa-libEGL, mesa-libgbm, gstreamer1, gstreamer1-plugins-base

Source0:        chatgpt-electron.tar.gz

%description
Electron-based wrapper for the ChatGPT web app. No API keys required.

%prep
%setup -q -n ChatGPT

%build
# nothing to build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/chatgpt-electron
cp -a . %{buildroot}/opt/chatgpt-electron

mkdir -p %{buildroot}/usr/share/applications
cat > %{buildroot}/usr/share/applications/chatgpt-electron.desktop <<'EOF2'
[Desktop Entry]
Name=ChatGPT (Electron)
Exec=/opt/chatgpt-electron/ChatGPT.sh
Icon=/opt/chatgpt-electron/resources/app/assets/icons/png/favicon.png
Type=Application
Categories=Utility;
EOF2

%files
/opt/chatgpt-electron
/usr/share/applications/chatgpt-electron.desktop

%changelog
* Mon Sep 29 2025 Packager <you@example.com> - 1.0-1
- Initial package
```

3) Build and install:
```bash
rpmbuild -bb ~/rpmbuild/SPECS/chatgpt-electron.spec
sudo dnf install -y ~/rpmbuild/RPMS/x86_64/chatgpt-electron-1.0-1*.rpm
```

Start: **application menu** or `/opt/chatgpt-electron/ChatGPT.sh`.

---

## Startup options (Wayland/X11, GPU)

- X11 with GLX (robust):
  ```bash
  --disable-gpu --use-gl=desktop
  ```
- Wayland (only if your session is actually Wayland):
  ```bash
  --enable-features=UseOzonePlatform --ozone-platform=wayland --disable-gpu
  ```
- Software rendering as a fallback:
  ```bash
  env LIBGL_ALWAYS_SOFTWARE=1 --disable-gpu --use-gl=swiftshader
  ```

---

## Proxy notes

Downloads through proxy:
```bash
export http_proxy=http://<proxy>:3128
export https_proxy=http://<proxy>:3128
curl -fL -o electron-v$VER-linux-x64.zip https://github.com/electron/electron/releases/download/v$VER/electron-v$VER-linux-x64.zip
unset http_proxy https_proxy
```

`npm install` is **not** required if you start the app with a local Electron runtime or run it via RPM/bundle.

---

## Downloads / Releases

This repository contains **no** binary artifacts.  
Create your own releases (AppImage/RPM) in your fork under **GitHub Releases** and link them here.

---

## Credits & License

- **Upstream code**: [mantreshkhurana/ChatGPT-electron](https://github.com/mantreshkhurana/ChatGPT-electron)  
- **OpenAI ChatGPT**: <https://chat.openai.com>  
- License: MIT (see `LICENSE`)
