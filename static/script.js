document.addEventListener('DOMContentLoaded', () => {
    const deviceList = document.getElementById('deviceList');
    const addDeviceForm = document.getElementById('addDeviceForm');

    // Load devices on page load
    loadDevices();

    // Handle form submission
    addDeviceForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const device = {
            name: document.getElementById('name').value,
            mac_address: document.getElementById('mac').value,
            ip_address: document.getElementById('ip').value || null,
            port: document.getElementById('port').value || null
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
                addDeviceForm.reset();
                loadDevices();
            } else {
                const error = await response.json();
                alert(`Error: ${error.detail}`);
            }
        } catch (error) {
            alert('Error adding device');
        }
    });

    // Load devices from API
    async function loadDevices() {
        try {
            const response = await fetch('/api/devices');
            const devices = await response.json();
            displayDevices(devices);
        } catch (error) {
            deviceList.innerHTML = '<div class="error">Error loading devices</div>';
        }
    }

    // Display devices in the UI
    function displayDevices(devices) {
        if (devices.length === 0) {
            deviceList.innerHTML = '<div class="no-devices">No devices added yet</div>';
            return;
        }

        deviceList.innerHTML = devices.map(device => `
            <div class="device-card" data-id="${device.name}">
                <div class="device-header">
                    <h3 class="device-name">${device.name}</h3>
                    <span class="device-status">${device.ip_address ? 'Online' : 'Offline'}</span>
                </div>
                <div class="device-details">
                    <p><strong>MAC:</strong> ${device.mac_address}</p>
                    ${device.ip_address ? `<p><strong>IP:</strong> ${device.ip_address}</p>` : ''}
                    ${device.port ? `<p><strong>Port:</strong> ${device.port}</p>` : ''}
                </div>
                <div class="device-actions">
                    <button class="wake-button" onclick="wakeDevice('${device.name}')">Wake Device</button>
                    <button class="delete-button" onclick="deleteDevice('${device.name}')">Delete</button>
                </div>
            </div>
        `).join('');
    }

    // Wake device function
    window.wakeDevice = async (deviceName) => {
        try {
            const response = await fetch(`/api/wake/${deviceName}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                const result = await response.json();
                alert(result.message);
            } else {
                const error = await response.json();
                alert(`Error: ${error.detail}`);
            }
        } catch (error) {
            alert('Error waking device');
        }
    };

    // Delete device function
    window.deleteDevice = async (deviceName) => {
        if (!confirm(`Are you sure you want to delete ${deviceName}?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/devices/${deviceName}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                loadDevices();
            } else {
                const error = await response.json();
                alert(`Error: ${error.detail}`);
            }
        } catch (error) {
            alert('Error deleting device');
        }
    };
}); 