from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from web3 import Web3
from fastapi.responses import StreamingResponse
import qrcode
import io
import json
import os

app = FastAPI()

# FULLY OPEN CORS FOR DOCKER
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BLOCKCHAIN_URL = os.getenv("BLOCKCHAIN_URL", "http://127.0.0.1:7545")
w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))

try:
    with open("address.txt", "r") as f:
        CONTRACT_ADDRESS = f.read().strip()
except FileNotFoundError:
    print("Warning: address.txt not found.")
    CONTRACT_ADDRESS = "0x0000000000000000000000000000000000000000"

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
        # Use the first account available in the node
        account = w3.eth.accounts[0]
        tx_hash = contract.functions.createShipment(
            data.shipmentId, data.productName, data.manufacturer,
            data.weight, data.dimensions, data.material,
            data.origin, data.destination
        ).transact({'from': account})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return {"status": "Created", "tx_hash": receipt.transactionHash.hex()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/update-status")
async def update_status(data: StatusUpdate):
    try:
        account = w3.eth.accounts[0] # Changed to accounts[0] to ensure success
        tx_hash = contract.functions.updateStatus(
            data.shipmentId, data.status, data.location
        ).transact({'from': account})
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return {"status": "Updated", "tx_hash": receipt.transactionHash.hex()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/track/{shipment_id}")
async def track_shipment(shipment_id: str):
    try:
        details = contract.functions.trackShipment(shipment_id).call()
        # Returning a cleaner dictionary
        return {
            "id": details[0], 
            "name": details[1], 
            "status": details[8],
            "location": details[9]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
@app.get("/qr/{shipment_id}")
async def generate_qr(shipment_id: str):
    # Points to the tracking endpoint
    tracking_url = f"http://localhost:8000/track/{shipment_id}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(tracking_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

@app.get("/history/{shipment_id}")
async def get_shipment_history(shipment_id: str):
    try:
        raw_history = contract.functions.getShipmentHistory(shipment_id).call()
        formatted_history = []
        for update in raw_history:
            formatted_history.append({
                "status": update[0],
                "location": update[1],
                "timestamp": update[2],
                "updater": update[3]
            })
        return {"history": formatted_history}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))