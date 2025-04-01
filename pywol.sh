#!/usr/bin/env bash

# Copyright (c) 2024 PMKA
# Author: PMKA
# License: MIT
# https://github.com/PMKA/PyWOL/raw/master/LICENSE

# Download functions file if not present
if [ ! -f "pywol-functions.sh" ]; then
    echo "Downloading functions file..."
    wget -q https://github.com/PMKA/PyWOL/raw/master/pywol-functions.sh
    if [ ! -f "pywol-functions.sh" ]; then
        echo "Failed to download functions file"
        exit 1
    fi
fi

# Source our functions
source pywol-functions.sh

# Check requirements
check_root
check_pve_version

# Container settings
CONTAINER_ID=100
HOSTNAME="pywol"
MEMORY=512
SWAP=512
CORES=1
REPO="https://github.com/PMKA/PyWOL.git"
INSTALL_PATH="/opt/pywol"

# Service configuration
SERVICE_NAME="pywol"
SERVICE_CONTENT="[Unit]
Description=PyWOL Wake-on-LAN Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/pywol
ExecStart=/usr/bin/python3 main.py
StandardOutput=inherit
StandardError=inherit
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target"

# Main installation process
create_container "$CONTAINER_ID" "$HOSTNAME" "$MEMORY" "$SWAP" "$CORES"
install_dependencies "$CONTAINER_ID"
clone_repo "$CONTAINER_ID" "$REPO" "$INSTALL_PATH"
install_python_deps "$CONTAINER_ID" "$INSTALL_PATH"
create_service "$CONTAINER_ID" "$SERVICE_NAME" "$SERVICE_CONTENT"
start_service "$CONTAINER_ID" "$SERVICE_NAME"

# Get IP and show success message
IP=$(get_container_ip "$CONTAINER_ID")
show_success "$IP" 