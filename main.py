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
    broadcast_ip: Optional[str] = "255.255.255.255"
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
DEVICES_FILE = BASE_DIR / "data" / "devices.json"

# Ensure data directory exists
os.makedirs(BASE_DIR / "data", exist_ok=True)

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
    device = next((d for d in devices if d.name.lower() == device_name.lower()), None)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    try:
        print(f"Attempting to wake device: {device.name}")
        print(f"MAC address: {device.mac_address}")
        print(f"Broadcast IP: {device.broadcast_ip}")
        print(f"Port: {device.port}")
        
        # Ensure MAC address is properly formatted
        mac_address = re.sub(r'[-:]', '', device.mac_address)
        mac_address = ':'.join(mac_address[i:i+2] for i in range(0, 12, 2))
        
        send_magic_packet(
            mac_address,
            ip_address=device.broadcast_ip,
            port=device.port
        )
        print("Magic packet sent successfully")
        return {"message": f"Wake-on-LAN packet sent to {device.name}"}
    except Exception as e:
        print(f"Error sending magic packet: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 