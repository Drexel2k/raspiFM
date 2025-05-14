# Setup development environment / IDE

## Development system
- Raspberry Pi 4 Model B  With Raspberry OS Bookworm or Ubuntu 24.04 LTS VM on Hyper-V/Windows 11
- User name `raspifm`

If not mentioned otherwise, setup instructions refer to this setup.

## Update your package repository
Do a `sudo apt update` first.

## Hardware setup
- If you develop on the Raspberry and want to attach parts of the full hardware setup, e.g. the MiniAmp with speakers, see [installation documentation](Install.md) for hardware installation

## IDE Setup / Build instructions for Raspberry Pi OS/Linux
- 1. On other Linux distributions than Raspberry Pi OS, e.g. Ubuntu you may need to install git: `sudo apt install git`.
- 2. Create a new directory for the repository: `mkdir ~/raspifm_repo` and switch to the directory: `cd ~/raspifm_repo`.
- 3. Clone the repository: `git clone https://github.com/Drexel2k/raspiFM .`
- 4. Install Visual Studio Code with Python Extension,`sudo apt install code` (on Ubuntu from Ubuntu Software), Python extension in the extension manager of VSC
- 5. Install Qt (touch ui), `sudo apt install qt6-base-dev libqt6svg6-dev qt6-wayland`, on Ubuntu 22.04 `sudo apt install qt6-base-dev` is sufficient, as it uses x11
- 6. On other Linux distributions than Raspberry Pi OS, e.g. Ubuntu you may need to install build packages and VLC media player, `sudo apt install build-essential pkg-config libdbus-1-dev libglib2.0-dev python3-dev vlc`.
- 7. Install PyQt6 from apt repository (a) or if it isn't available (on Ubuntu 22.04 e.g.), if you want the latest version or if you want it as .venv package, take it from the lib directory (b) or install from source (c)
  - a) `sudo apt install python3-pyqt6`
  - b) Further steps follow on stepp 12
  - c) Install further libs needed on Ubuntu `sudo apt install mesa-common-dev`
    - On Ubuntu install Qt with the desired version with the Qt Online Installer (https://www.qt.io/download-qt-installer-oss), currently tested and used in the delivered libs is v6.8.3 (LTS). - On Raspberry Pi newer Qt versions from the Online installer doesn't work, because they were built on Ubuntu with a newer glibc version as on Raspberry Pi OS. So we have also to build Qt from the source, here with version 6.8.3 (LTS) and wayland support only e.g.:
      - Install dependencies (not tested if really all are needed/are not available/installed with other previous packages) `sudo apt install cmake libfontconfig1-dev libdbus-1-dev libfreetype6-dev libicu-dev libinput-dev libxkbcommon-dev libsqlite3-dev libssl-dev libpng-dev libjpeg-dev libglib2.0-dev libgles2-mesa-dev libgbm-dev libdrm-dev libvulkan-dev vulkan-tools` 
      -Install wayland libs `sudo apt install libwayland-dev libwayland-egl1-mesa libwayland-server0`
      - Download and extract https://download.qt.io/official_releases/qt/6.8/6.8.3/submodules/qtbase-everywhere-src-6.8.3.tar.xz, `tar -xf qtbase-everywhere-src-6.8.3.tar.xz`
      - Switch to the directory where the file is extracted, make a directory for the build inside, switch into the build directory `cd /path/to/qtbase-extract`, `mkdir ./build`, `cd ./build`
      - Build: `cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/home/raspifm/Qt/6.8.3-aarch64 -DQT_FEATURE_opengles2=ON -DQT_FEATURE_opengles3=ON -DQT_FEATURE_kms=ON -DQT_AVOID_CMAKE_ARCHIVING_API=ON ..`, DCMAKE_INSTALL_PREFIX parameter is where the build is installed in the next step, then `cmake --build . --parallel 4`
      - Install: `cmake --install .`
      - Build required modules: qtsvg, qtimageformats, qtwayland
      - Download and extract https://download.qt.io/official_releases/qt/6.8/6.8.3/submodules/qt....tar.xz, `tar -xf qt....tar.xz`
      - Switch to the directory where the file is extracted, make a directory for the build inside, switch into the build directory `cd /path/to/qt...-extract`, `mkdir ./build`, `cd ./build`
      - Build: `/home/raspifm/Qt/6.8.3-aarch64/bin/qt-configure-module  ..`, then `cmake --build . --parallel 4`
      - Install: `cmake --install .`
    - Further steps follow on stepp 12

In Visual Studio Code:
- 8. Open the `~/raspifm_repo` directory wioth `File -> Open Folder`.
- 9. Command Palette -> Python: Create Environment
- 10. Create venv environement, select to install requirements
- 11. Command Palette -> Python: Create Terminal
- 12. Take PyQt6 from the lib (see 7b) or install from source (see 7c)
  - from 7b) If you have chosen 7b, install the wheel from [libs](/libs):
    - x64: `pip install ~/raspifm_repo/libs/PyQt6-6.8.1-cp39-abi3-manylinux_2_28_x86_64.whl` (built with Qt 6.8.3)
    - arm64: `pip install ~/raspifm_repo/libs/PyQt6-6.8.1-cp39-abi3-manylinux_2_28_aarch64.whl` (built with Qt 6.8.3)
  - from 7c) If you have chosen 7c:
    - Download source with same or higher version from https://pypi.org/project/PyQt6/#files, extract with `tar -xzf pyqt6-6.8.1.tar.gz`, change to directory: `cd /path/to/pyqt6-6.8.1` e.g.
    - Install sip tools: `pip install PyQt-builder`
    - Add path to qmake directory from the Qt installation to path environment variable: `export PATH="$PATH:/home/raspifm/Qt/6.8.3-aarch64/bin"` e.g., make sure that the qmake in this path is used and not another from a system path e.g., remove the directory from the path if required. But this shouldn't be the case in an active venv.
    - Build wheel from the source: `sip-wheel --confirm-license --verbose`, this takes some hours on Raspberry
    - Install the wheel: `pip install ./PyQt6-6.8.3-cp39-abi3-manylinux_2_28_aarch64.whl` e.g.

## Requirements for Spotify Connect for Raspberry Pi OS/Linux
To use the Spotify conncet feature, spotifyd needs to be installed. Unfortunetally, spotifyd delivers only 32 bit binaries,
so we have to build a 64 bit version by ourselves or use the binary from [libs](/libs) directory (or setup a 32 bit environment in the 64 bit raspberry pi OS). 

If you want to build your spotifyd 64 bit binary, follow start with step 1.  
If you want to use the file from the [libs](/libs) directory skip step 1 to 9 and start from step 10.

To build a 64 bit spotifyd binary:
- 1. Uninstall current rust compiler if one is installed, it may be to old, e.g. by: `sudo apt remove rustc` or `rustup self uninstall`
- 2. On other Linux distributions than Raspberry Pi OS, e.g. Ubuntu you may need to install curl to install the current rust tolchain: `sudo apt install curl`
- 3. Install current rust toolchain, select option 1: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- 4. Setup environment variable: `source "$HOME/.cargo/env"`
- 5. Create a new directory for the repository: `mkdir ~/spotifyd_repo` and switch to the directory: `cd ~/spotifyd_repo`.
- 6. Clone the repository: `git clone https://github.com/Spotifyd/spotifyd.git .`
- 7. Install required packages: `sudo apt install libasound2-dev libdbus-1-dev`, on other Linux distributions than Raspberry, e.g. Ubuntu you may need to install further packages to compile spotifyd, `sudo apt install build-essential pkg-config`, some of these packages may also already be installed during IDE setup.
- 8. If you do not want to compile the latest commit, but the latest release, look up the latest release tag: https://github.com/Spotifyd/spotifyd/releases or https://github.com/Spotifyd/spotifyd/tags and do: `git checkout tags/v0.4.1` e.g.
- 9. Build spotifyd with DBus support: `cargo build --release --locked --features dbus_mpris,pulseaudio_backend`, this takes some minutes

Install spotifiyd and set up the daemon:
- 10. Copy the compiled file to /usr/bin: `sudo cp ./target/release/spoetifyd /usr/bin` or use the file from libs(spotifyd-0.3.5-dbus-pulse_aarch64): 
  - x64: `sudo cp ~/raspifm_repo/libs/spotifyd-0.3.5-dbus-pulse_aarch64 /usr/bin/spotifyd`
  -   - Care! Current spotifyd stable release hase some issues due to Spotify backend changes. Use the latest build instead: `sudo cp ~/raspifm_repo/libs/spotifyd-commit-e280d84124d854af3c2f9509ba496b1c2ba6a1ae-librespot-0.4.2-dbus-pulse_aarch64 /usr/bin/spotifyd`
  - arm64: `sudo cp ~/raspifm_repo/libs/spotifyd-0.3.5-dbus-pulse_aarch64 /usr/bin/spotifyd`
- 11. Copy the spotifyd config file from [configs](/configs/spotifyd.conf) to /etc: `sudo cp ~/raspifm_repo/configs/spotifyd.conf /etc`
- 12. Set up daemon: Copy the file from [configs](/configs/spotifyd.service) to /etc/systemd/system: `sudo cp ~/raspifm_repo/configs/spotifyd.service /etc/systemd/user`
- 13. Enable the daemon/autostart: `systemctl --user enable spotifyd.service`
- 14. Allow the spotifyd daemon to register services on the system DBus: Copy the file from [configs](/configs/spotifyd-dbus.conf) to /usr/share/dbus-1/system.d: `sudo cp ~/raspifm_repo/configs/spotifyd-dbus.conf /usr/share/dbus-1/system.d`
- 15. Reboot