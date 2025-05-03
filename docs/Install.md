# Installation / Productive setup / Deployment

## Hardware & system setup
Current standard and tested setup is:
- Raspberry Pi 4 Model B Raspberry Pi OS Bookworm
- Official 7" touchscreen
- HiFiBerry MiniAmp
- ICY BOX Dual Raspberry Pi GPIO Header
- Visaton FRS 8M speakers
- ATX Power On Off Switch with Power LED for ATX mainboards (4 cables)

- User & group name `raspifm`

If not mentioned otherwise, setup instructions refer to this setup.

NO WARRANTIES AT ALL, BUT ESPECIALLY NOT ON ANY HARDWARE SETUP/CONNECTION/MODIFCATION!

## Update your package repository
Do a `sudo apt update` first.

## Set up HifiBerry MiniAmp
- 1. Mount the MiniAmp on the GPIO header and the header to the Raspberry board, so that that unused GPIO Pins still can be used
- 1. Make a backup of config.txt file to your current directory: `cp /boot/config.txt ./`
- 2. Edit config.txt: `sudo nano /boot/config.txt`
- 3. Disable the line `dtparam=audio=on` to `# dtparam=audio=on`
- 4. Edit the line `dtoverlay=vc4-kms-v3d` to `dtoverlay=vc4-kms-v3d,noaudio`
- 5. Add lines `dtoverlay=hifiberry-dac` and `force_eeprom_read=0` before the first filter section (cm4)

## Set up touchscreen
- 1. Connect DSI and power cables (to the GPIO header), official documentation on [www.raspberrypi.com](https://www.raspberrypi.com/documentation/accessories/display.html)
- 2. I connected 5V to Pin 2/5V and Ground to Pin 14/Ground as I took Pin 6/Ground for the Power Switch (see next section)

## Setup Power Switch/LED
- 1. Connect Power LED + to Pin 7/GPIO 4, Power LED - to Pin 9/Ground and the Power Switch cables over Pin 5/GPIO 3 and Pin 6/Ground
- 2. Edit config.txt: `sudo nano /boot/config.txt` (backup done in MiniAmp setup, if not do it now!)
- 3. Add lines `dtoverlay=gpio-shutdown,gpio_pin=3` and `gpio=4=op,dh` before the first filter section (cm4)

## Download the repository from github
- 1. Create a new directory for the repository: `mkdir ~/raspifm_repo` and switch to the directory: `cd ~/raspifm_repo`.
- 2. Clone the repository: `git clone https://github.com/Drexel2k/raspiFM .`
- 3. If you do not want to use the latest commit, but the latest release, look up the latest release tag: https://github.com/Drexel2k/raspiFM/releases or https://github.com/Drexel2k/raspiFM/tags and do: `git checkout tags/v1.0`

## Setup Spotify Connect / spotifyd
- 1. Copy spotifyd binary to /usr/bin: `sudo cp ~/raspifm_repo/libs/spotifyd-0.4.1-dbus-pulse_aarch64 /usr/bin/spotifyd`
- 2. Copy the spotifyd config file from [configs](/configs/spotifyd.conf) to /etc: `sudo cp ~/raspifm_repo/configs/spotifyd.conf /etc`
- 3. Set up daemon: Copy the file from [configs](/configs/spotifyd.service) to /etc/systemd/system: `sudo cp ~/raspifm_repo/configs/spotifyd.service /etc/systemd/user`
- 4. Enable the daemon/autostart: `systemctl --user enable spotifyd.service`
- 5. Allow the spotifyd daemon to register services on the system DBus: Copy the file from [configs](/configs/spotifyd-dbus.conf) to /usr/share/dbus-1/system.d: `sudo cp ~/raspifm_repo/configs/spotifyd-dbus.conf /usr/share/dbus-1/system.d`
- 6. Reboot

## Setup raspiFM
- 1. Install gui libraries and nginx for web interface: `sudo apt install qt6-base-dev libqt6svg6-dev qt6-wayland nginx`
- 2. Create directory for raspiFM files and set permissions: `sudo mkdir -p /usr/bin/local/raspifm` and set permissions: `sudo chown raspifm:raspifm /usr/bin/local/raspifm`
- 3. Add www-data user to raspifm group: `sudo usermod -a -G raspifm www-data`
- 3. Copy the raspiFM files to the directory: `cp -r ~/raspifm_repo/src/. /usr/bin/local/raspifm`
- 4. Setup python environment/dependencies:
  - `python3 -m venv /usr/bin/local/raspifm/.venv`
  - `/usr/bin/local/raspifm/.venv/bin/python3 -m pip install -r ~/raspifm_repo/piprequirements.txt`
  - `/usr/bin/local/raspifm/.venv/bin/python3 -m pip install ~/raspifm_repo/libs/PyQt6-6.8.3-cp39-abi3-manylinux_2_28_aarch64.whl`
- 5. Setup nginx: 
  - `sudo cp ~/raspifm_repo/configs/raspifm.nginx /etc/nginx/sites-available/raspifm`
  - `sudo ln -s /etc/nginx/sites-available/raspifm /etc/nginx/sites-enabled/`
- 6. To password protect the web interface see the comment in `/etc/nginx/sites-available/raspifm`, edit it with `sudo nano /etc/nginx/sites-available/raspifm`
- 7. Setup autostart for raspiFM:
  - Create the autostart directory: `mkdir -p ~/.config/autostart`
  - Copy the desktop file to the autostart directory: `cp ~/raspifm_repo/configs/raspifm.desktop ~/.config/autostart`

  Reboot.