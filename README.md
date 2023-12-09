# raspiFM
Internetradio on Raspberry Pi

## Prepare dev environment
Do a "sudo apt update" first.

### Requirements (for Spotify connect, Raspberry Pi OS/Linux only)
To use the Spotify conncet feature, spotifyd needs to be installed. Unfortunetally, spotifyd delivers only 32 bit binaries,
so we have to build a 64 bit verion by ourselves (or setup a 32 bit environment in the 64 bit raspberry pi os).
To build a 64bit binary and set up the daemon:
1. Uninstall current rust compiler, it may be to old: "sudo apt remove rustc" (may not be needed on other Linux distributions than Raspberry Pi OS like Ubunto when they have no rust compiler preinstalled)
2. On other Linux distributions than Raspberry Pi OS, e.g. Ubuntu you may need to install curl to install the current rust tolchain: "sudo apt install curl"
3. Install current rust toolchain, select option 1: "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
4. Setup environement: source "$HOME/.cargo/env"
5. On other Linux distributions than Raspberry Pi OS, e.g. Ubuntu you may need to install git: "sudo apt install git"
4. Download the spotifyd git repository in a direcory of your choice: git clone https://github.com/Spotifyd/spotifyd.git
2. On other Linux distributions than Raspberry, e.g. Ubuntu you may need to install further packages to compile spotifyd, "sudo apt install build-essential pkg-config libasound2-dev libdbus-1-dev"
5. Build spotifyd with DBus support: cd spotifyd, then cargo build --release --features dbus_mpris
6. Copy the compiled file to /usr/bin: cp ./target/release/spotifyd /usr/bin
7. Copy the spotifyd config file from [configs](/configs/spotifyd.conf) to /etc: "sudo cp ./spotifyd.conf /etc"
8. Set up daemon: Copy the file from [configs](/configs/spotifyd.service) to /etc/systemd/system: sudo cp ./spotifyd.service /etc/systemd/system
9. Enable the daemon/autostart: "sudo systemctl enable spotifyd.service"
10. Allow the spotifyd daemon to register services on the system DBus: Copy the file from [configs](/configs/spotifyd-dbus.conf) to /usr/share/dbus-1/system.d: "sudo cp ./spotifyd-dbus.conf /usr/share/dbus-1/system.d"
11. Reboot

### IDE Setup / Build instructions for Raspberry Pi OS/Linux
1. Install Visual Studio Code with Python Extension,"sudo apt install code", Python extension in the extension manager of VSC
2. Install Qt for touch ui, "sudo apt install qt6-base-dev"
3. On other Linux distributions than Raspberry Pi OS, e.g. Ubuntu you may need to install VLC media player and PIP, "sudo apt install vlc python3-pip"

In Visual Studio Code:

4. Command Palette -> Git: Clone -> Clone from Github -> Enter Url -> Enter
5. After clone, in the dialog confirm to open the folder
6. Command Palette -> Python: Create Environment
7. Create venv environement, select to install requirements
8. Command Palette -> Python: Create Terminal

With PySide 6 I had the error message on Raspberry Pi OS

  Could not load the Qt platform plugin "xcb" in ""

on touchUI launch. It seems somehow to be well known, but solutions are a little
bit differ a little bit, the reason is a package missing or needed to be reinstalled, but different packages are the cause:
Here is a big thread about it: https://forum.qt.io/topic/93247/qt-qpa-plugin-could-not-load-the-qt-platform-plugin-xcb-in-even-though-it-was-found
But googling will also bring up other communities and threads. This was my solution:
https://forum.qt.io/topic/93247/qt-qpa-plugin-could-not-load-the-qt-platform-plugin-xcb-in-even-though-it-was-found/165


### IDE Setup / Build instructions for Windows
1. Install Visual Studio Code with Python Extension (https://code.visualstudio.com/download) and Git (https://git-scm.com/download/win)
2. Install Qt for touch ui: https://www.qt.io/download-qt-installer-oss (you need an account for download), installl design tools and Qt for desktop development
3. Install VLC MediaPlayer (https://www.videolan.org/vlc/)

In Visual Studio Code:

4. Command Palette -> Git: Clone -> Clone from Github -> Enter Url -> Enter
5. After clone, in the dialog confirm to open the folder
6. Command Palette -> Python: Create Environment
7. Create venv environement, select to install requirements
8. Command Palette -> Python: Create Terminal