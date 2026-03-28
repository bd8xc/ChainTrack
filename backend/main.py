from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from web3 import Web3
from fastapi.responses import StreamingResponse
import qrcode
import io
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

# PASTE YOUR REMIX CONTRACT ADDRESS HERE:
CONTRACT_ADDRESS = "0x90353e2716D71C8CE67d41601Ebf42b0796D9E37"

with open("contract_abi.json", "r") as f:
    CONTRACT_ABI = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

class StatusUpdate(BaseModel):
    shipmentId: str
    status: str
    location: str

class Shipment(BaseModel):
    shipmentId: str
    productName: str
    manufacturer: str
    weight: int
    dimensions: str
    material: str
    origin: str
    destination: str

@app.post("/create-shipment")
async def create_shipment(data: Shipment):
    try:
        tx_hash = contract.functions.createShipment(
            data.shipmentId, data.productName, data.manufacturer,
            data.weight, data.dimensions, data.material,
            data.origin, data.destination
        ).transact({'from': w3.eth.accounts[0]})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return {"status": "Created", "tx_hash": receipt.transactionHash.hex()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/update-status")
async def update_status(data: StatusUpdate):
    try:
        # Notice we use accounts[1] here to simulate the Delivery Carrier updating it!
        tx_hash = contract.functions.updateStatus(
            data.shipmentId, data.status, data.location
        ).transact({'from': w3.eth.accounts[1]})
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return {"status": "Updated", "tx_hash": receipt.transactionHash.hex()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/track/{shipment_id}")
async def track_shipment(shipment_id: str):
    try:
        details = contract.functions.trackShipment(shipment_id).call()
        return {
            "id": details[0], "name": details[1], "manufacturer": details[2],
            "weight": details[3], "material": details[5], "status": details[8],
            "location": details[9]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
@app.get("/qr/{shipment_id}")
async def generate_qr(shipment_id: str):
    # Now the QR code will point to your computer's actual Wi-Fi IP!
    # Change it back to localhost
    tracking_url = f"http://127.0.0.1:8000/track/{shipment_id}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(tracking_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    return StreamingResponse(buf, media_type="image/png")