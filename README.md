# raspiFM
Internetradio on Raspberry Pi

# Requirements (for Spotify connect)
To use the Spotify conncet feature, spotifyd needs to be installed. Unfortunetally, spotifyd delivers only 32 bit binaries,
so we have to build a 64 bit verion by ourselves (or setup a 32 bit environment in the 64 bit raspberry pi os).
To build a 64bit binary and set up the daemon:
1. Uninstall current rust compiler, it may be to old: sudo apt remove rustc
2. Install current rust version, select option 1: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
3. Setup environement: source "$HOME/.cargo/env"
4. Download the spotifyd git repsoitory: git clone https://github.com/Spotifyd/spotifyd.git
5. Build spotifyd with DBus support: cd spotifyd, then cargo build --release --features dbus_mpris
6. Copy the compiled file to /usr/bin: cp ./target/release/spotifyd /usr/bin
7. Set up daemon: Copy the file from [configs](/configs/spotifyd.service) to /etc/systemd/system: sudo cp ./spotifyd.service /etc/systemd/system
8. Enable the daemon/autostart: sudo systemctl enable spotifyd.service
8. Allow the spotifyd daemon to register services on the system DBus: Copy the file from [configs](/configs/spotifyd-dbus.conf) to /usr/share/dbus-1/system.d: sudo cp ./spotifyd-dbus.conf /usr/share/dbus-1/system.d
9. Reboot

# IDE Setup / Build instructions for Raspberry Pi OS/Linux
1. Install Visual Studio Code with Python Extension (sudo apt install code)
2. Install Qt for touch ui (sudo apt install qt6-base-dev)

In Visual Studio Code:

3. Command Palette -> Git: Clone -> Clone from Github -> Enter Url -> Enter
4. After clone, in the dialog confirm to open the folder
5. Command Palette -> Python: Create Environment
6. Create venv environement, select to install requirements
7. Command Palette -> Python: Create Terminal

With PySide 6 I had the error message

  Could not load the Qt platform plugin "xcb" in ""

even though it was found on touchUI launch. It seems somehow to be well known, but solutions are a little
bit differ a little bit, the reason is a package missing or needed to be reinstalled, but different packages are the cause:
Here is a big thread about it: https://forum.qt.io/topic/93247/qt-qpa-plugin-could-not-load-the-qt-platform-plugin-xcb-in-even-though-it-was-found
But googling will also bring up other communities and threads. This was my solution:
https://forum.qt.io/topic/93247/qt-qpa-plugin-could-not-load-the-qt-platform-plugin-xcb-in-even-though-it-was-found/165


# IDE Setup / Build instructions for Windows
1. Install Visual Studio Code with Python Extension (https://code.visualstudio.com/download) and Git (https://git-scm.com/download/win)
2. Install Qt for touch ui: https://www.qt.io/download-qt-installer-oss (you need an account for download), installl design tools and Qt for desktop development
3. Install VLC MediaPlayer (https://www.videolan.org/vlc/)

In Visual Studio Code:

4. Command Palette -> Git: Clone -> Clone from Github -> Enter Url -> Enter
5. After clone, in the dialog confirm to open the folder
6. Command Palette -> Python: Create Environment
7. Create venv environement, select to install requirements
8. Command Palette -> Python: Create Terminal