# raspiFM
Internetradio on Raspberry Pi

# Setup environment / IDE
## Update your package repository
Do a `sudo apt update` first.

## Set up HifiBerry MiniAmp for Raspberry Pi OS (Bookworm, Raspberry Pi 4)
- 1. Make a backup of config.txt file to your current folder: `cp /boot/config.txt ./`
- 2. Edit config.txt: `sudo nano /boot/config.txt`
- 3. Disable the line `dtparam=audio=on` to `# dtparam=audio=on`
- 4. Edit the line `dtoverlay=vc4-kms-v3d` to `dtoverlay=vc4-kms-v3d,noaudio`
- 5. Add lines `dtoverlay=hifiberry-dac` and `force_eeprom_read=0` before the first filter section (cm4)
- 6. Reboot

## Requirements for Spotify connect for Raspberry Pi OS/Linux
To use the Spotify conncet feature, spotifyd needs to be installed. Unfortunetally, spotifyd delivers only 32 bit binaries,
so we have to build a 64 bit verion by ourselves (or setup a 32 bit environment in the 64 bit raspberry pi OS) with step 1 to 10 or use the file from the [libs] folder (start from stepp 11).
To build a 64bit binary and set up the daemon:
- 1. Uninstall current rust compiler if one is installed, it may be to old, e.g. by: `sudo apt remove rustc` or `rustup self uninstall`
- 2. On other Linux distributions than Raspberry Pi OS, e.g. Ubuntu you may need to install curl to install the current rust tolchain: `sudo apt install curl`
- 3. Install current rust toolchain, select option 1: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- 4. Setup environment variable: `source "$HOME/.cargo/env"`
- 5. On other Linux distributions than Raspberry Pi OS, e.g. Ubuntu you may need to install git: `sudo apt install git`
- 6. Download the spotifyd git repository in a direcory of your choice: `git clone https://github.com/Spotifyd/spotifyd.git`
- 7. Install required packages: `sudo apt install libasound2-dev libdbus-1-dev`, on other Linux distributions than Raspberry, e.g. Ubuntu you may need to install further packages to compile spotifyd, `sudo apt install build-essential pkg-config`
- 8. Switch to spotifyd folder: `cd spotifyd`
- 9. If you do not want to compile the latest commit, but the latest release, look up the latest release tag: https://github.com/Spotifyd/spotifyd/releases or https://github.com/Spotifyd/spotifyd/tags and do: `git checkout tags/v0.3.5` e.g.
- 10. Build spotifyd with DBus support: `cargo build --release --features dbus_mpris,pulseaudio_backend`, this takes some minutes
- 11. Copy the compiled file to /usr/bin: `sudo cp ./target/release/spotifyd /usr/bin` or use the file from libs(spotifyd-0.3.5-dbus-pulse_aarch64): 
  - x64:
  - arm64: `sudo cp /path/to/raspifm-folder/libs/spotifyd-0.3.5-dbus-pulse_aarch64 /usr/bin/spotifyd`
- 12. Copy the spotifyd config file from [configs](/configs/spotifyd.conf) to /etc: `sudo cp /path/to/raspifm-folder/configs/spotifyd.conf /etc`
- 13. Set up daemon: Copy the file from [configs](/configs/spotifyd.service) to /etc/systemd/system: `sudo cp /path/to/raspifm-folder/configs/spotifyd.service /etc/systemd/user`
- 14. Enable the daemon/autostart: `systemctl --user enable spotifyd.service`
- 15. Allow the spotifyd daemon to register services on the system DBus: Copy the file from [configs](/configs/spotifyd-dbus.conf) to /usr/share/dbus-1/system.d: `sudo cp /path/to/raspifm-folder/configs/spotifyd-dbus.conf /usr/share/dbus-1/system.d`
- 16. Reboot

## IDE Setup / Build instructions for Raspberry Pi OS/Linux
- 1. Install Visual Studio Code with Python Extension,`sudo apt install code` (on Ubuntu from Ubuntu Software), Python extension in the extension manager of VSC
- 2. Install Qt (touch ui), `sudo apt install qt6-base-dev libqt6svg6-dev qt6-wayland`, on Ubuntu 22.04 `sudo apt install qt6-base-dev` is sufficient, as it uses x11
- 3. On other Linux distributions than Raspberry Pi OS, e.g. Ubuntu you may need to install build packages and VLC media player, `sudo apt install build-essential pkg-config libdbus-1-dev libglib2.0-dev python3-dev vlc`, some of these packages may also already be installed during spotifyd build.
- 4. Install PyQt6 from apt repository (a) or if it isn't available (on Ubuntu 22.04 e.g.), if you want the latest version or if you want it as .venv package, take it from the lib folder (b) or install from source (c)
  - a) `sudo apt install python3-pyqt6`
  - b) Further steps follow on stepp 10
  - c) Install further libs needed on Ubuntu `sudo apt install mesa-common-dev`
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
- 10. If you have chosen 4b, install the wheel from [libs](/libs):
  - x64: `pip install /path/to/raspifm-folder/libs/PyQt6-6.6.1-cp38-abi3-manylinux_2_28_x86_64.whl` (built with Qt 6.2.4)
  - arm64: `pip install /path/to/raspifm-folder/libs/PyQt6-6.6.1-cp38-abi3-manylinux_2_28_aarch64.whl` (built with Qt 6.2.4)
- 11. If you have chosen 4c:
  - Download source from https://pypi.org/project/PyQt6/#files, extract with `tar -xzf PyQt6-6.6.1.tar.gz` e.g.
  - Install sip tools: `pip install PyQt-builder`
  - Add path to qmake folder to path environment variable: `export PATH="$PATH:/usr/lib/qt6/bin"` (not required on Ubunutu)
  - Change terminal directory to the path of tthe source: `cd /path/to/extraded/archive/PyQt6-6.6.1`
  - Build wheel from the source: `sip-wheel --confirm-license --verbose --qmake-setting 'QMAKE_LIBS_LIBATOMIC = -latomic'`, this takes some hours on Raspberry
  - Install the wheel: `pip install ./PyQt6-6.6.1-cp38-abi3-manylinux_2_28_x86_64.whl` or whatever the outputfile is called
