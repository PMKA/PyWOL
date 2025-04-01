document.addEventListener('DOMContentLoaded', () => {
    const deviceForm = document.getElementById('deviceForm');
    const devicesList = document.getElementById('devicesList');
    let isLoading = false;

    // Load devices on page load
    loadDevices();

    // Handle form submission
    deviceForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (isLoading) return;

        const submitButton = deviceForm.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
        submitButton.disabled = true;
        isLoading = true;

        const device = {
            name: document.getElementById('name').value,
            mac_address: document.getElementById('macAddress').value,
            ip_address: document.getElementById('ipAddress').value || null,
            broadcast_ip: document.getElementById('broadcastIp').value || "255.255.255.255",
            port: parseInt(document.getElementById('port').value) || 9
        };

        try {
            const response = await fetch('/api/devices', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(device)
            });

            if (response.ok) {
                showNotification('Device added successfully!', 'success');
                deviceForm.reset();
                await loadDevices();
            } else {
                const error = await response.json();
                showNotification(error.detail || 'Failed to add device', 'error');
            }
        } catch (error) {
            showNotification('Error adding device', 'error');
            console.error(error);
        } finally {
            submitButton.innerHTML = originalButtonText;
            submitButton.disabled = false;
            isLoading = false;
        }
    });

    // Load devices from API
    async function loadDevices() {
        if (isLoading) return;
        isLoading = true;

        try {
            const response = await fetch('/api/devices');
            if (!response.ok) {
                throw new Error('Failed to fetch devices');
            }
            const devices = await response.json();
            displayDevices(devices);
        } catch (error) {
            console.error('Error loading devices:', error);
            showNotification('Error loading devices', 'error');
        } finally {
            isLoading = false;
        }
    }

    // Display devices in the UI
    function displayDevices(devices) {
        if (!Array.isArray(devices)) {
            console.error('Invalid devices data:', devices);
            return;
        }

        if (devices.length === 0) {
            devicesList.innerHTML = `
                <div class="no-devices">
                    <i class="fas fa-desktop"></i>
                    <p>No devices added yet. Add your first device above!</p>
                </div>
            `;
            return;
        }

        // Create a temporary container
        const tempContainer = document.createElement('div');
        
        // Add new devices to the temporary container
        devices.forEach((device, index) => {
            const deviceCard = document.createElement('div');
            deviceCard.className = 'device-card';
            deviceCard.style.animation = `fadeIn 0.5s ease ${index * 0.1}s`;
            deviceCard.innerHTML = `
                <div class="device-info">
                    <div class="device-name">${device.name}</div>
                    <div class="device-mac"><i class="fas fa-network-wired"></i> MAC: ${device.mac_address}</div>
                    ${device.ip_address ? `<div class="device-ip"><i class="fas fa-globe"></i> IP: ${device.ip_address}</div>` : ''}
                </div>
                <div class="device-actions">
                    <button class="btn-wake" onclick="wakeDevice('${device.name}')">
                        <i class="fas fa-power-off"></i> Wake
                    </button>
                    <button class="btn-delete" onclick="deleteDevice('${device.mac_address}')">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            `;
            tempContainer.appendChild(deviceCard);
        });

        // Replace the content of the devices list
        devicesList.innerHTML = '';
        devicesList.appendChild(tempContainer);
    }

    // Wake device function
    window.wakeDevice = async (deviceName) => {
        if (isLoading) return;
        const button = event.currentTarget;
        const originalButtonText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Waking...';
        button.disabled = true;
        isLoading = true;

        try {
            const response = await fetch(`/api/wake/${encodeURIComponent(deviceName)}`, {
                method: 'POST'
            });

            if (response.ok) {
                const result = await response.json();
                showNotification(result.message, 'success');
            } else {
                const error = await response.json();
                showNotification(error.detail || 'Failed to wake device', 'error');
            }
        } catch (error) {
            showNotification('Error waking device', 'error');
            console.error(error);
        } finally {
            button.innerHTML = originalButtonText;
            button.disabled = false;
            isLoading = false;
        }
    };

    // Delete device function
    window.deleteDevice = async (macAddress) => {
        if (isLoading) return;
        if (!confirm('Are you sure you want to delete this device?')) {
            return;
        }

        const button = event.currentTarget;
        const originalButtonText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';
        button.disabled = true;
        isLoading = true;

        try {
            const response = await fetch(`/api/devices/${macAddress}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                showNotification('Device deleted successfully!', 'success');
                await loadDevices();
            } else {
                const error = await response.json();
                showNotification(error.detail || 'Failed to delete device', 'error');
            }
        } catch (error) {
            showNotification('Error deleting device', 'error');
            console.error(error);
        } finally {
            button.innerHTML = originalButtonText;
            button.disabled = false;
            isLoading = false;
        }
    };

    // Show notification function
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            ${message}
        `;
        
        document.body.appendChild(notification);
        
        // Trigger reflow
        notification.offsetHeight;
        
        notification.classList.add('show');
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}); 