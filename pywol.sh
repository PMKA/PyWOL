#!/usr/bin/env bash

# Copyright (c) 2024 PMKA
# Author: PMKA
# License: MIT
# https://github.com/PMKA/PyWOL/raw/master/LICENSE

header_info() {
  clear
  cat <<"EOF"
 ____    ____    _    ____    _     ____    _      ____    _     ____    _     _ 
|  _ \  |  _ \  / \  | __ )  / \   | __ )  / \    | __ )  / \   | __ )  / \   | |
| |_) | | |_) |/ _ \ |  _ \ / _ \  |  _ \ / _ \   |  _ \ / _ \  |  _ \ / _ \  | |
|  __/  |  _ </ ___ \| |_) / ___ \ | |_) / ___ \  | |_) / ___ \ | |_) / ___ \ | |
|_|     |_| \_\/   \_\____/_/   \_\____/_/   \_\ |____/_/   \_\|____/_/   \_\|_|
                                                                                 
EOF
}

RD=$(echo "\033[01;31m")
YW=$(echo "\033[33m")
GN=$(echo "\033[1;92m")
CL=$(echo "\033[m")
BFR="\\r\\033[K"
HOLD="-"
CM="${GN}✓${CL}"
CROSS="${RD}✗${CL}"

set -euo pipefail
shopt -s inherit_errexit nullglob

msg_info() {
  local msg="$1"
  echo -ne " ${HOLD} ${YW}${msg}..."
}

msg_ok() {
  local msg="$1"
  echo -e "${BFR} ${CM} ${GN}${msg}${CL}"
}

msg_error() {
  local msg="$1"
  echo -e "${BFR} ${CROSS} ${RD}${msg}${CL}"
}

start_routines() {
  header_info

  CHOICE=$(whiptail --backtitle "Proxmox VE Helper Scripts" --title "PYWOL INSTALLATION" --menu "This will create a container and install PyWOL.\n\nProceed with installation?" 14 58 2 \
    "yes" " " \
    "no" " " 3>&2 2>&1 1>&3)
  case $CHOICE in
  yes)
    msg_info "Creating container"
    pct create 100 local:vztmpl/debian-12-standard_12.0-1_amd64.tar.gz --hostname pywol --memory 512 --swap 512 --cores 1 --net0 name=eth0,bridge=vmbr0,ip=dhcp --features nesting=1,keyctl=1 --start 1
    msg_ok "Created container"

    msg_info "Installing dependencies"
    pct exec 100 -- apt-get update
    pct exec 100 -- apt-get install -y python3-pip git
    msg_ok "Installed dependencies"

    msg_info "Cloning PyWOL repository"
    pct exec 100 -- git clone https://github.com/PMKA/PyWOL.git /opt/pywol
    msg_ok "Cloned repository"

    msg_info "Installing Python dependencies"
    pct exec 100 -- bash -c "cd /opt/pywol && pip3 install -r requirements.txt"
    msg_ok "Installed Python dependencies"

    msg_info "Creating systemd service"
    pct exec 100 -- bash -c 'cat <<EOF > /etc/systemd/system/pywol.service
[Unit]
Description=PyWOL Wake-on-LAN Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/pywol
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF'
    msg_ok "Created systemd service"

    msg_info "Starting PyWOL service"
    pct exec 100 -- systemctl enable pywol
    pct exec 100 -- systemctl start pywol
    msg_ok "Started PyWOL service"

    IP=$(pct exec 100 -- hostname -I | awk '{print $1}')
    echo -e "\n${GN}PyWOL has been successfully installed!${CL}"
    echo -e "${YW}Access it using the following URL:${CL}"
    echo -e "${GN}http://${IP}:8000${CL}\n"
    ;;
  no)
    msg_error "Selected no to PyWOL installation"
    ;;
  esac
}

header_info
echo -e "\nThis script will create a container and install PyWOL.\n"
while true; do
  read -p "Start the PyWOL Installation Script (y/n)?" yn
  case $yn in
  [Yy]*) break ;;
  [Nn]*) clear; exit ;;
  *) echo "Please answer yes or no." ;;
  esac
done

if ! pveversion | grep -Eq "pve-manager/8\.[0-3](\.[0-9]+)*"; then
  msg_error "This version of Proxmox Virtual Environment is not supported"
  echo -e "Requires Proxmox Virtual Environment Version 8.0 or later."
  echo -e "Exiting..."
  sleep 2
  exit
fi

start_routines 