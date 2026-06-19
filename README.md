<img src="./assets/icons/png/favicon.png" width="50" height="50" />

# ChatGPT Desktop (Electron Wrapper)

[![Stars](https://img.shields.io/github/stars/mantreshkhurana/ChatGPT-electron?style=social)](https://github.com/mantreshkhurana/ChatGPT-electron)

Leichte Desktop-Hülle für die **ChatGPT Web-App** (`https://chat.openai.com`). Keine API-Keys nötig. Läuft mit lokaler Electron-Runtime, optional als RPM paketiert.

> Hinweis: Google-/Microsoft-Login kann eingebettete WebViews blockieren. Empfehlung: Anmeldung im **Systembrowser** oder E-Mail/Passwort verwenden.

---

## Inhalte

- [Voraussetzungen](#voraussetzungen)
- [Schnellstart (lokale Electron-Runtime)](#schnellstart-lokale-electron-runtime)
- [Build ohne Internetzugriff](#build-ohne-internetzugriff)
- [RPM für Fedora bauen](#rpm-für-fedora-bauen)
- [Startoptionen (Wayland/X11, GPU)](#startoptionen-waylandx11-gpu)
- [Proxy-Hinweise](#proxy-hinweise)
- [Downloads / Releases](#downloads--releases)
- [Credits & Lizenz](#credits--lizenz)

---

## Voraussetzungen

- Node.js ≥ 18 (nur für Entwicklungs-Tasks, **nicht** zur Laufzeit nötig)
- Linux x86_64
- Für Media: `gstreamer1`, `gstreamer1-plugins-base`
- Für EGL/GLX: Mesa-Stack (`mesa-libEGL`, `mesa-libgbm`, `mesa-dri-drivers`)
- Optional (RPM): `rpmbuild`

Fedora:
```bash
sudo dnf install -y   gstreamer1 gstreamer1-plugins-base   mesa-libEGL mesa-libgbm mesa-dri-drivers   libX11 libXcomposite libXdamage libXfixes libXrandr libXi libXScrnSaver at-spi2-core   rpm-build
```

---

## Schnellstart (lokale Electron-Runtime)

1) Repo klonen:
```bash
git clone https://github.com/<DEIN-FORK>/ChatGPT-electron.git
cd ChatGPT-electron
```

2) Passende Electron-Version bestimmen:
```bash
VER=$(node -p "let p=require('./package.json');(p.devDependencies?.electron||p.dependencies?.electron||'').replace(/^[^0-9]*/,'')")
echo "$VER"
```

3) Electron **ohne npm** bereitstellen:
```bash
mkdir -p ~/.cache/electron/v$VER
cd ~/.cache/electron/v$VER

# ZIP laden (Proxy siehe unten)
curl -fL -o electron-v$VER-linux-x64.zip   https://github.com/electron/electron/releases/download/v$VER/electron-v$VER-linux-x64.zip

# Prüfsumme lokal erzeugen (optional)
sha256sum electron-v$VER-linux-x64.zip | awk '{print $1"  electron-v'"$VER"'-linux-x64.zip"}' > SHASUMS256.txt

# entpacken
mkdir -p ~/.local/opt/electron-$VER
unzip -o electron-v$VER-linux-x64.zip -d ~/.local/opt/electron-$VER

# bequemer Symlink
mkdir -p ~/.local/bin
ln -sf ~/.local/opt/electron-$VER/electron ~/.local/bin/electron-$VER
```

4) Starten:
```bash
~/.local/bin/electron-$VER . --disable-gpu --use-gl=desktop
```

---

## Build **ohne Internetzugriff**

Wenn `npm install` am Proxy/SSL scheitert, starte die App direkt mit der **lokalen Electron-Runtime** (siehe oben). Für ein Bundle:

```bash
# App in Electron-Runtime bündeln
BUILDROOT="$HOME/build/chatgpt-electron"
rm -rf "$BUILDROOT" && mkdir -p "$BUILDROOT"

VER=$(node -p "let p=require('./package.json');(p.devDependencies?.electron||p.dependencies?.electron||'').replace(/^[^0-9]*/,'')")

cp -a ~/.local/opt/electron-$VER "$BUILDROOT/ChatGPT"
rm -f  "$BUILDROOT/ChatGPT/resources/app.asar"
mkdir -p "$BUILDROOT/ChatGPT/resources/app"
cp -a package.json main.js preload.js index.html assets src "$BUILDROOT/ChatGPT/resources/app/"

# Startskript
install -Dm755 /dev/stdin "$BUILDROOT/ChatGPT/ChatGPT.sh" <<'EOF'
#!/usr/bin/env bash
BASEDIR="$(cd "$(dirname "$0")" && pwd)"
exec "$BASEDIR/electron" "$BASEDIR/resources/app" --disable-gpu --use-gl=desktop "$@"
EOF
```

Danach liegt eine lauffähige Portabel-Version unter `~/build/chatgpt-electron/ChatGPT`.

---

## RPM für Fedora bauen

1) rpmbuild-Baum:
```bash
mkdir -p ~/rpmbuild/{SPECS,BUILD,RPMS,SOURCES,SRPMS}
tar -C "$BUILDROOT" -czf ~/rpmbuild/SOURCES/chatgpt-electron.tar.gz ChatGPT
```

2) SPEC nutzen:
```spec
%global debug_package %{nil}
%undefine _debugsource_packages

Name:           chatgpt-electron
Version:        1.0
Release:        1%{?dist}
Summary:        ChatGPT Desktop (Electron, offline gebündelt)
License:        MIT
URL:            https://github.com/<DEIN-FORK>/ChatGPT-electron
BuildArch:      x86_64
Requires:       libX11, libXcomposite, libXdamage, libXfixes, libXrandr, libXi, libXScrnSaver, at-spi2-core, mesa-libEGL, mesa-libgbm, gstreamer1, gstreamer1-plugins-base

Source0:        chatgpt-electron.tar.gz

%description
Electron-basierter Wrapper für die ChatGPT Web-App. Keine API-Schlüssel erforderlich.

%prep
%setup -q -n ChatGPT

%build
# nichts zu bauen

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

3) Bauen und installieren:
```bash
rpmbuild -bb ~/rpmbuild/SPECS/chatgpt-electron.spec
sudo dnf install -y ~/rpmbuild/RPMS/x86_64/chatgpt-electron-1.0-1*.rpm
```

Start: **Anwendungsmenü** oder `/opt/chatgpt-electron/ChatGPT.sh`.

---

## Startoptionen (Wayland/X11, GPU)

- X11 mit GLX (robust):
  ```bash
  --disable-gpu --use-gl=desktop
  ```
- Wayland (nur falls Session wirklich Wayland ist):
  ```bash
  --enable-features=UseOzonePlatform --ozone-platform=wayland --disable-gpu
  ```
- Software-Rendering als Notnagel:
  ```bash
  env LIBGL_ALWAYS_SOFTWARE=1 --disable-gpu --use-gl=swiftshader
  ```

---

## Proxy-Hinweise

Downloads über Proxy:
```bash
export http_proxy=http://<proxy>:3128
export https_proxy=http://<proxy>:3128
curl -fL -o electron-v$VER-linux-x64.zip https://github.com/electron/electron/releases/download/v$VER/electron-v$VER-linux-x64.zip
unset http_proxy https_proxy
```

`npm install` wird **nicht** benötigt, wenn du die App mit lokaler Electron-Runtime startest oder über RPM/Bundle betreibst.

---

## Downloads / Releases

Dieses Repo enthält **keine** Binärartefakte.  
Erstelle eigene Releases (AppImage/RPM) in deinem Fork unter **GitHub Releases** und verlinke sie hier.

---

## Credits & Lizenz

- **Upstream-Code**: [mantreshkhurana/ChatGPT-electron](https://github.com/mantreshkhurana/ChatGPT-electron)  
- **OpenAI ChatGPT**: <https://chat.openai.com>  
- Lizenz: MIT (siehe `LICENSE`)
