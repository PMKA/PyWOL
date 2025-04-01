# PyWOL - Wake-on-LAN Manager

A modern web application for managing and waking up devices using Wake-on-LAN (WOL) technology. Built with FastAPI and a responsive frontend.

## Features

- Add and manage WOL-enabled devices
- Wake up devices with a single click
- Modern, responsive web interface
- JSON-based device storage
- RESTful API
- Error handling and notifications
- Mobile-friendly design

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A WOL-enabled device on your network

## Installation

### Standard Installation

1. Clone the repository:
```bash
git clone https://github.com/PMKA/pywol.git
cd pywol
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Alpine Linux LXC Deployment

1. Create a new Alpine Linux LXC container in Proxmox

2. SSH into your Alpine container and run:
```bash
# Make the deployment script executable
chmod +x deploy_alpine.sh

# Run the deployment script
./deploy_alpine.sh
```

3. The application will be available at:
```
http://<container-ip>:8000
```

## Usage

1. Start the application:
```bash
python main.py
```

2. Open your web browser and navigate to:
```
http://localhost:8000
```

3. Add your WOL-enabled devices using the web interface:
   - Enter the device name
   - Enter the MAC address (format: XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX)
   - Optionally enter the IP address and broadcast IP
   - Click "Add Device"

4. To wake a device:
   - Find the device in the list
   - Click the "Wake" button

## Project Structure

```
pywol/
├── main.py              # FastAPI backend
├── requirements.txt     # Python dependencies
├── Dockerfile          # Standard Dockerfile
├── Dockerfile.alpine   # Alpine-specific Dockerfile
├── docker-compose.yml  # Docker Compose configuration
├── deploy_alpine.sh    # Alpine deployment script
├── static/             # Static files
│   ├── index.html      # Main HTML file
│   ├── styles.css      # CSS styles
│   └── script.js       # Frontend JavaScript
└── data/               # Data storage
    └── devices.json    # Device configuration
```

## API Endpoints

- `GET /api/devices` - List all devices
- `POST /api/devices` - Add a new device
- `DELETE /api/devices/{mac_address}` - Delete a device
- `POST /api/wake/{mac_address}` - Wake a device

## Frontend Features

- works on all devices
- Smooth animations for device cards
- Real-time notifications for actions
- Form validation for MAC addresses
- Loading states and error handling
- Modern UI with hover effects and transitions

## Docker Deployment

### Standard Docker Deployment

To deploy using standard Docker:

1. Build the Docker image:
```bash
docker build -t pywol .
```

2. Run the container:
```bash
docker run -d -p 8000:8000 --name pywol pywol
```

### Alpine Linux Docker Deployment

To deploy using Docker Compose (recommended for Alpine):

1. Build and start the container:
```bash
docker-compose up -d --build
```

2. View logs:
```bash
docker-compose logs -f
```

3. Stop the container:
```bash
docker-compose down
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
