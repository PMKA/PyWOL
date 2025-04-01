#!/usr/bin/env bash

# Color codes for output
RD=$(echo "\033[01;31m")
YW=$(echo "\033[33m")
GN=$(echo "\033[1;92m")
CL=$(echo "\033[m")
BFR="\\r\\033[K"
HOLD="-"
CM="${GN}✓${CL}"
CROSS="${RD}✗${CL}"

# Error handling
set -euo pipefail
shopt -s inherit_errexit nullglob

# Message functions
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

# Check if running as root
check_root() {
  if [ "$EUID" -ne 0 ]; then 
    msg_error "Please run as root"
    exit 1
  fi
}

# Check Proxmox version
check_pve_version() {
  if ! pveversion | grep -Eq "pve-manager/8\.[0-3](\.[0-9]+)*"; then
    msg_error "This version of Proxmox Virtual Environment is not supported"
    echo -e "Requires Proxmox Virtual Environment Version 8.0 or later."
    echo -e "Exiting..."
    sleep 2
    exit 1
  fi
}

# Create container
create_container() {
  local container_id="$1"
  local hostname="$2"
  local memory="$3"
  local swap="$4"
  local cores="$5"
  
  msg_info "Creating container ${container_id}"
  pct create ${container_id} local:vztmpl/debian-12-standard_12.0-1_amd64.tar.gz \
    --hostname ${hostname} \
    --memory ${memory} \
    --swap ${swap} \
    --cores ${cores} \
    --net0 name=eth0,bridge=vmbr0,ip=dhcp \
    --features nesting=1,keyctl=1 \
    --start 1
  msg_ok "Created container ${container_id}"
}

# Install dependencies
install_dependencies() {
  local container_id="$1"
  msg_info "Installing dependencies"
  pct exec ${container_id} -- apt-get update
  pct exec ${container_id} -- apt-get install -y python3-pip git
  msg_ok "Installed dependencies"
}

# Clone repository
clone_repo() {
  local container_id="$1"
  local repo="$2"
  local path="$3"
  
  msg_info "Cloning repository"
  pct exec ${container_id} -- git clone ${repo} ${path}
  msg_ok "Cloned repository"
}

# Install Python dependencies
install_python_deps() {
  local container_id="$1"
  local path="$2"
  
  msg_info "Installing Python dependencies"
  pct exec ${container_id} -- bash -c "cd ${path} && pip3 install -r requirements.txt"
  msg_ok "Installed Python dependencies"
}

# Create systemd service
create_service() {
  local container_id="$1"
  local service_name="$2"
  local service_content="$3"
  
  msg_info "Creating systemd service"
  pct exec ${container_id} -- bash -c "cat <<EOF > /etc/systemd/system/${service_name}.service
${service_content}
EOF"
  msg_ok "Created systemd service"
}

# Start service
start_service() {
  local container_id="$1"
  local service_name="$2"
  
  msg_info "Starting service"
  pct exec ${container_id} -- systemctl enable ${service_name}
  pct exec ${container_id} -- systemctl start ${service_name}
  msg_ok "Started service"
}

# Get container IP
get_container_ip() {
  local container_id="$1"
  pct exec ${container_id} -- hostname -I | awk '{print $1}'
}

# Show success message
show_success() {
  local ip="$1"
  msg_ok "Completed Successfully!\n"
  echo -e "${CREATING}${GN}PyWOL setup has been successfully initialized!${CL}"
  echo -e "${INFO}${YW} Access it using the following URL:${CL}"
  echo -e "${TAB}${GATEWAY}${BGN}http://${ip}:8000${CL}"
} 