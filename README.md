# raspiFM
Internetradio on Raspberry Pi

# Setup environment / IDE
## Update your package repository
Do a "sudo apt update" first.

## Set up HifiBerry MiniAmp
- tbd

## Requirements for Spotify connect for Raspberry Pi OS/Linux
To use the Spotify conncet feature, spotifyd needs to be installed. Unfortunetally, spotifyd delivers only 32 bit binaries,
so we have to build a 64 bit verion by ourselves (or setup a 32 bit environment in the 64 bit raspberry pi OS).
To build a 64bit binary and set up the daemon:
- 1. Uninstall current rust compiler, it may be to old: "sudo apt remove rustc" (may not be needed on other Linux distributions than Raspberry Pi OS like Ubunto when they have no rust compiler preinstalled)
- 2. On other Linux distributions than Raspberry Pi OS, e.g. Ubuntu you may need to install curl to install the current rust tolchain: "sudo apt install curl"
- 3. Install current rust toolchain, select option 1: "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
- 4. Setup environement: "source "$HOME/.cargo/env""
- 5. On other Linux distributions than Raspberry Pi OS, e.g. Ubuntu you may need to install git: "sudo apt install git"
- 6. Download the spotifyd git repository in a direcory of your choice: "git clone https://github.com/Spotifyd/spotifyd.git"
- 7. On other Linux distributions than Raspberry, e.g. Ubuntu you may need to install further packages to compile spotifyd, "sudo apt install build-essential pkg-config libasound2-dev libdbus-1-dev"
- 8. Build spotifyd with DBus support: cd spotifyd, then "cargo build --release --features dbus_mpris"
- 9. Copy the compiled file to /usr/bin: "sudo cp ./target/release/spotifyd /usr/bin"
- 10. Copy the spotifyd config file from [configs](/configs/spotifyd.conf) to /etc: "sudo cp path-to-configs/spotifyd.conf /etc"
- 11. Set up daemon: Copy the file from [configs](/configs/spotifyd.service) to /etc/systemd/system: "sudo cp path-to-configs/spotifyd.service /etc/systemd/system"
- 12. Enable the daemon/autostart: "sudo systemctl enable spotifyd.service"
- 13. Allow the spotifyd daemon to register services on the system DBus: Copy the file from [configs](/configs/spotifyd-dbus.conf) to /usr/share/dbus-1/system.d: "sudo cp path-to-configs/spotifyd-dbus.conf /usr/share/dbus-1/system.d"
- 14. Reboot

## IDE Setup / Build instructions for Raspberry Pi OS/Linux
- 1. Install Visual Studio Code with Python Extension,"sudo apt install code", Python extension in the extension manager of VSC
- 2. Install Qt (touch ui), "sudo apt install qt6-base-dev"
- 3. On other Linux distributions than Raspberry Pi OS, e.g. Ubuntu you may need to install build packages and VLC media player, "sudo apt install build-essential pkg-config libdbus-1-dev libglib2.0-dev python3-dev vlc"
- 4. Install PyQt6 from apt repository (a) or if it isn't available (on Ubuntu 22.04 e.g.), if you want the latest version or if you want it as .venv package, take it from the lib folder (b) or install from source (c)
  - a) "sudo apt install python3-pyqt6"
  - b) Further steps follow on stepp 10
  - c) "sudo apt install qt6-base-dev libqt6svg6-dev mesa-common-dev"
    - On Ubunutu 22.04 you need to set up a workaround for Qt6 to be found by QtChooser an make it the default Qt version:
    - qtchooser -install qt6 $(which qmake6)
    - sudo mv ~/.config/qtchooser/qt6.conf /usr/share/qtchooser/qt6.conf
    - sudo mkdir -p /usr/lib/$(uname -p)-linux-gnu/qt-default/qtchooser
    - sudo rm /usr/lib/$(uname -p)-linux-gnu/qt-default/qtchooser/default.conf
    - sudo ln -s /usr/share/qtchooser/qt6.conf /usr/lib/$(uname -p)-linux-gnu/qt-default/qtchooser/default.conf
    - Further steps follow on stepp 11

In Visual Studio Code:
- 5. Command Palette -> Git: Clone -> Clone from Github -> Enter Url -> Enter
- 6. After clone, in the dialog confirm to open the folder
- 7. Command Palette -> Python: Create Environment
- 8. Create venv environement, select to install requirements
- 9. Command Palette -> Python: Create Terminal
- 10. If you have chosen 4b:
  - x64: pip install /path/to/Lib-folder/PyQt6-6.6.1-cp38-abi3-manylinux_2_28_armv7l.whl (built with Qt 6.2.4)
  - arm:
- 11. If you have chosen 4c:
  - Download source from https://pypi.org/project/PyQt6/#files, extract with "tar -xzf PyQt6-6.6.1.tar.gz" e.g.
  - install sip tools: "pip install PyQt-builder"
  - "cd /path/to/extraded/archive/PyQt6-6.6.1"
  - sip-wheel --confirm-license --verbose --qmake-setting 'QMAKE_LIBS_LIBATOMIC = -latomic'
  - pip install ./PyQt6-6.6.1-cp38-abi3-manylinux_2_28_armv7l.whl or whatever the outputfile is called
