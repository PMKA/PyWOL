from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
import json
import os
from wakeonlan import send_magic_packet
from typing import List, Optional
from pathlib import Path
import re

app = FastAPI(title="PyWOL", description="Wake-on-LAN Application")

# Get the current directory
BASE_DIR = Path(__file__).resolve().parent

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Data model
class Device(BaseModel):
    name: str
    mac_address: str
    ip_address: Optional[str] = None
    broadcast_ip: str = "255.255.255.255"
    port: Optional[int] = 9

    @validator('mac_address')
    def validate_mac_address(cls, v):
        # Remove any separators
        v = re.sub(r'[-:]', '', v)
        # Convert to lowercase
        v = v.lower()
        # Check if it's a valid MAC address
        if not re.match(r'^[0-9a-f]{12}$', v):
            raise ValueError('Invalid MAC address format')
        # Format with colons
        return ':'.join(v[i:i+2] for i in range(0, 12, 2))

# File paths
DEVICES_FILE = Path("/app/data/devices.json")

# Ensure data directory exists
os.makedirs(Path("/app/data"), exist_ok=True)

def load_devices() -> List[Device]:
    if DEVICES_FILE.exists():
        with open(DEVICES_FILE, "r") as f:
            return [Device(**device) for device in json.load(f)]
    return []

def save_devices(devices: List[Device]):
    with open(DEVICES_FILE, "w") as f:
        json.dump([device.dict() for device in devices], f, indent=4)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return FileResponse(str(BASE_DIR / "static" / "index.html"))

@app.get("/api/devices")
async def get_devices():
    devices = load_devices()
    return devices

@app.post("/api/devices")
async def add_device(device: Device):
    devices = load_devices()
    devices.append(device)
    save_devices(devices)
    return device

@app.delete("/api/devices/{mac_address}")
async def delete_device(mac_address: str):
    devices = load_devices()
    devices = [d for d in devices if d.mac_address != mac_address]
    save_devices(devices)
    return {"message": "Device deleted"}

@app.post("/api/wake/{device_name}")
async def wake_device(device_name: str):
    devices = load_devices()
    # Normalize the input device name
    normalized_input = device_name.lower().strip()
    
    # Find device with case-insensitive comparison
    device = next((d for d in devices if d.name.lower().strip() == normalized_input), None)
    
    if not device:
        print(f"Device not found. Input: '{device_name}', Normalized: '{normalized_input}'")
        print(f"Available devices: {[d.name for d in devices]}")
        raise HTTPException(status_code=404, detail="Device not found")
    
    try:
        print(f"Attempting to wake device: {device.name}")
        print(f"MAC address: {device.mac_address}")
        
        # Calculate broadcast IP from device IP
        if device.ip_address:
            ip_parts = device.ip_address.split('.')
            broadcast_ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.255"
        else:
            broadcast_ip = "255.255.255.255"
            
        print(f"Broadcast IP: {broadcast_ip}")
        
        # Ensure port is set
        port = device.port if device.port else 9
        print(f"Port: {port}")
        
        # Ensure MAC address is properly formatted
        mac_address = re.sub(r'[-:]', '', device.mac_address)
        mac_address = ':'.join(mac_address[i:i+2] for i in range(0, 12, 2))
        
        # Try sending multiple times with different broadcast addresses
        try:
            send_magic_packet(
                mac_address,
                ip_address=broadcast_ip,
                port=port
            )
            print(f"Magic packet sent successfully to {broadcast_ip}")
        except Exception as e:
            print(f"Failed to send to {broadcast_ip}, trying 255.255.255.255: {str(e)}")
            send_magic_packet(
                mac_address,
                ip_address="255.255.255.255",
                port=port
            )
            print("Magic packet sent successfully to 255.255.255.255")
            
        return {"message": f"Wake-on-LAN packet sent to {device.name}"}
    except Exception as e:
        print(f"Error sending magic packet: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 