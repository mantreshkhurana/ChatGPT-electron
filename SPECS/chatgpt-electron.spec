%global debug_package %{nil}
%undefine _debugsource_packages

Name:           chatgpt-electron
Version:        1.0
Release:        1%{?dist}
Summary:        ChatGPT Desktop (Electron, offline gebündelt)
License:        MIT
URL:            https://github.com/mantreshkhurana/ChatGPT-electron
BuildArch:      x86_64
Requires:       libX11, libXcomposite, libXdamage, libXfixes, libXrandr, libXi, libXScrnSaver, at-spi2-core, mesa-libEGL, mesa-libgbm, gstreamer1, gstreamer1-plugins-base

Source0:        chatgpt-electron.tar.gz

%description
In Electron gebündelter ChatGPT-Client. Läuft ohne weitere npm-Downloads.

%prep
%setup -q -n ChatGPT

%build
# nichts zu bauen

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/chatgpt-electron
cp -a . %{buildroot}/opt/chatgpt-electron

# Desktop-Datei
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
