from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from wakeonlan import send_magic_packet
from typing import List, Optional
from pathlib import Path

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

@app.post("/api/wake/{mac_address}")
async def wake_device(mac_address: str):
    devices = load_devices()
    device = next((d for d in devices if d.mac_address == mac_address), None)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    try:
        send_magic_packet(
            device.mac_address,
            ip_address=device.broadcast_ip,
            port=device.port
        )
        return {"message": f"Wake-on-LAN packet sent to {device.name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 