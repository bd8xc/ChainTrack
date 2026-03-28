# ChainLogistics: Blockchain-Powered Supply Chain Tracker

A full-stack, decentralized logistics application that provides an immutable audit trail for shipments. This project uses a private Ethereum blockchain to store shipment states, ensuring that tracking data cannot be tampered with or deleted.

---

## System Architecture & Tech Stack

The application is built as a microservices architecture orchestrated by **Docker**. 

### 1. The Blockchain Layer (The Ledger)
* **Technology:** Solidity, Ganache.
* **Role:** Acts as the "Source of Truth." Every time a shipment is created or moved, a transaction is written to the blockchain.
* **Feature:** Uses a custom Solidity `struct` and `array` to store an immutable history for every serial ID.

### 2. The Backend Layer (The Bridge)
* **Technology:** Python, FastAPI, Web3.py.
* **Role:** Converts standard Web requests (JSON) into Blockchain transactions. 
* **Automation:** Contains a custom `deploy.py` script that automatically compiles and deploys the Smart Contract to the Dockerized blockchain on startup.

### 3. The Frontend Layer (The Command Center)
* **Technology:** Tailwind CSS, JavaScript (Vanilla), Glassmorphism UI.
* **Role:** Provides a real-time dashboard to register shipments, track current status via progress steppers, and visualize the history timeline.

### 4. Orchestration
* **Technology:** Docker & Docker Compose.
* **Role:** Manages the lifecycle of the network. It ensures the Blockchain is running before the Backend attempts to deploy the contract.

---

## How to Run the Project

### **Prerequisites**
* **Docker Desktop** installed and running.
* **VS Code** (recommended) with the **Live Server** extension.

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/YOUR_USERNAME/shipment-tracker.git
cd shipment-tracker
```

### **Step 2: Launch the Infrastructure**
Open your terminal in the root folder and run:
```bash
docker-compose up --build
```
* **Wait for it:** Look for the message `INFO: Uvicorn running on http://0.0.0.0:8000`. 
* **Note:** The backend is configured to wait 10 seconds for the blockchain to initialize before deploying the contract.

### **Step 3: Open the UI**
1.  Navigate to the `frontend/` folder.
2.  Right-click `index.html` and select **"Open with Live Server"**.
3.  Access the UI at `http://127.0.0.1:5500` (or the port provided by your server).

---

## Operating the Application

1.  **Register:** Enter a unique Shipment Serial ID (e.g., `SHP_001`) and Product Name. Click **Broadcast to Blockchain**.
2.  **Track:** Type your ID into the search bar and hit **Track**. You will see the "CREATED" status and a QR code.
3.  **Update:** Enter a new city (e.g., "Dubai") and change the status to "In Transit". Click **Sign & Update Ledger**.
4.  **Audit Trail:** Scroll down to the **Immutable Audit Trail** to see the time-stamped history of every change made on the blockchain.

---

## Important Developer Notes

### **Blockchain Reset**
Since we are using a local Ganache instance in Docker, **the blockchain is cleared every time you run `docker-compose down`.** * If you restart the containers, you must register a new shipment ID before you can track it.

### **Contract Modifications**
If you decide to modify the Smart Contract (`.sol` file):
1.  Recompile in **Remix**.
2.  **Crucial:** Set the **EVM Version** to `London` under "Advanced Configurations" in the Compiler tab.
3.  Update the **ABI** in `backend/contract_abi.json`.
4.  Update the **Bytecode** string in `backend/deploy.py`.
5.  Rebuild: `docker-compose up --build`.

---

## Project Structure
```text
shipment-tracker/
├── backend/
│   ├── main.py            # FastAPI API logic
│   ├── deploy.py          # Automated contract deployer
│   ├── contract_abi.json  # Compiled contract ABI
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Backend container config
├── frontend/
│   └── index.html         # Tailwind UI & JS Logic
├── docker-compose.yml     # Orchestration file
└── .gitignore             # Files to exclude from Git
```

