# Setup development environment / IDE

## Hardware & system setup
Current standard and tested setup is:
- Raspberry Pi 4 Model B
- Official 7" touchscreen
- HiFiBerry MiniAmp
- ICY BOX Dual Raspberry Pi Gpio Header
- Visaton FRS 8M speakers
- ATX Power On Off Switch

- User name `raspifm`

If not mentioned otherwise, setup instructions refer to this setup.

## Update your package repository
Do a `sudo apt update` first.

## Set up HifiBerry MiniAmp for Raspberry Pi OS (Bookworm, Raspberry Pi 4)
- 1. Make a backup of config.txt file to your current directory: `cp /boot/config.txt ./`
- 2. Edit config.txt: `sudo nano /boot/config.txt`
- 3. Disable the line `dtparam=audio=on` to `# dtparam=audio=on`
- 4. Edit the line `dtoverlay=vc4-kms-v3d` to `dtoverlay=vc4-kms-v3d,noaudio`
- 5. Add lines `dtoverlay=hifiberry-dac` and `force_eeprom_read=0` before the first filter section (cm4)
- 6. Reboot

## IDE Setup / Build instructions for Raspberry Pi OS/Linux
- 1. On other Linux distributions than Raspberry Pi OS, e.g. Ubuntu you may need to install git: `sudo apt install git`
- 2. Create a new directory for the repository: `mkdir ~/raspifm_repo` and switch to the directory: `cd ~/raspifm_repo`.
- 3. Clone the repository: `git clone https://github.com/Drexel2k/raspiFM .`
- 4. Install Visual Studio Code with Python Extension,`sudo apt install code` (on Ubuntu from Ubuntu Software), Python extension in the extension manager of VSC
- 5. Install Qt (touch ui), `sudo apt install qt6-base-dev libqt6svg6-dev qt6-wayland`, on Ubuntu 22.04 `sudo apt install qt6-base-dev` is sufficient, as it uses x11
- 6. On other Linux distributions than Raspberry Pi OS, e.g. Ubuntu you may need to install build packages and VLC media player, `sudo apt install build-essential pkg-config libdbus-1-dev libglib2.0-dev python3-dev vlc`.
- 7. Install PyQt6 from apt repository (a) or if it isn't available (on Ubuntu 22.04 e.g.), if you want the latest version or if you want it as .venv package, take it from the lib directory (b) or install from source (c)
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
- 5. Open the `~/raspifm_repo` directory wioth `File -> Open Folder`.
- 7. Command Palette -> Python: Create Environment
- 8. Create venv environement, select to install requirements
- 9. Command Palette -> Python: Create Terminal
- 10. If you have chosen 4b, install the wheel from [libs](/libs):
  - x64: `pip install ~/raspifm_repo/libs/PyQt6-6.6.1-cp38-abi3-manylinux_2_28_x86_64.whl` (built with Qt 6.2.4)
  - arm64: `pip install ~/raspifm_repo/libs/PyQt6-6.6.1-cp38-abi3-manylinux_2_28_aarch64.whl` (built with Qt 6.2.4)
- 11. If you have chosen 4c:
  - Download source from https://pypi.org/project/PyQt6/#files, extract with `tar -xzf PyQt6-6.6.1.tar.gz` e.g.
  - Install sip tools: `pip install PyQt-builder`
  - Add path to qmake directory to path environment variable: `export PATH="$PATH:/usr/lib/qt6/bin"` (not required on Ubunutu)
  - Change terminal directory to the path of tthe source: `cd /path/to/extraded/archive/PyQt6-6.6.1`
  - Build wheel from the source: `sip-wheel --confirm-license --verbose --qmake-setting 'QMAKE_LIBS_LIBATOMIC = -latomic'`, this takes some hours on Raspberry
  - Install the wheel: `pip install ./PyQt6-6.6.1-cp38-abi3-manylinux_2_28_x86_64.whl` or whatever the outputfile is called

## Requirements for Spotify Connect for Raspberry Pi OS/Linux
To use the Spotify conncet feature, spotifyd needs to be installed. Unfortunetally, spotifyd delivers only 32 bit binaries,
so we have to build a 64 bit version by ourselves (or setup a 32 bit environment in the 64 bit raspberry pi OS) with step 1 to 10 or use the file from the [libs] directory (start from stepp 10).
To build a 64bit binary and set up the daemon:
- 1. Uninstall current rust compiler if one is installed, it may be to old, e.g. by: `sudo apt remove rustc` or `rustup self uninstall`
- 2. On other Linux distributions than Raspberry Pi OS, e.g. Ubuntu you may need to install curl to install the current rust tolchain: `sudo apt install curl`
- 3. Install current rust toolchain, select option 1: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- 4. Setup environment variable: `source "$HOME/.cargo/env"`
- 5. Download the spotifyd git repository in a direcory of your choice: `git clone https://github.com/Spotifyd/spotifyd.git`
- 6. Install required packages: `sudo apt install libasound2-dev libdbus-1-dev`, on other Linux distributions than Raspberry, e.g. Ubuntu you may need to install further packages to compile spotifyd, `sudo apt install build-essential pkg-config`, some of these packages may also already be installed during IDE setup.
- 7. Switch to spotifyd directory: `cd spotifyd`
- 8. If you do not want to compile the latest commit, but the latest release, look up the latest release tag: https://github.com/Spotifyd/spotifyd/releases or https://github.com/Spotifyd/spotifyd/tags and do: `git checkout tags/v0.3.5` e.g.
- 9. Build spotifyd with DBus support: `cargo build --release --features dbus_mpris,pulseaudio_backend`, this takes some minutes
- 10. Copy the compiled file to /usr/bin: `sudo cp ./target/release/spotifyd /usr/bin` or use the file from libs(spotifyd-0.3.5-dbus-pulse_aarch64): 
  - x64: `sudo cp ~/raspifm_repo/libs/spotifyd-0.3.5-dbus-pulse_x86_64 /usr/bin/spotifyd`
  - arm64: `sudo cp ~/raspifm_repo/libs/spotifyd-0.3.5-dbus-pulse_aarch64 /usr/bin/spotifyd`
- 11. Copy the spotifyd config file from [configs](/configs/spotifyd.conf) to /etc: `sudo cp ~/raspifm_repo/configs/spotifyd.conf /etc`
- 12. Set up daemon: Copy the file from [configs](/configs/spotifyd.service) to /etc/systemd/system: `sudo cp ~/raspifm_repo/configs/spotifyd.service /etc/systemd/user`
- 13. Enable the daemon/autostart: `systemctl --user enable spotifyd.service`
- 14. Allow the spotifyd daemon to register services on the system DBus: Copy the file from [configs](/configs/spotifyd-dbus.conf) to /usr/share/dbus-1/system.d: `sudo cp ~/raspifm_repo/configs/spotifyd-dbus.conf /usr/share/dbus-1/system.d`
- 15. Reboot