# Vital_Ledger
The VitaLEdger is a hardware-oracle system designed to secure the transport of vital medicine and perishables. By leveraging the Raspberry Pi 5 and the XRP Ledger, we ensure that financial settlement only occurs if the temperature of the goods is maintained throughout transit.
Overview:
A buyer can create a conditional escrow on the XRP Ledger and the Sentinel (Raspberry Pi 5). Uses the escrow logic so the Sentinel (middleman) holds zero funds). There is a cold failsafe so if the goods are ruined the contract is voided. 

TechStack: Python 3.13 Blockchain (XRPL) using xrpl-py, Hardware: Raspberry Pi 5 + BMP180 Temperature Sensor (Via I2C), Dashboard Streamlit, DevTools: VsCode (SSH), Raspberry Pi Connect.

Setup: 
Hardware: Connect BMP180 to Pi 5 (VCC, GND, SDA, SCL).
Environment:
Bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Configuration: Create a .env file with your SENTINEL_SEED, SAFE_TEMP_THRESHOLD, and MAX_OVERHEAT_STRIKES.
Launch:
streamlit run app.py
Direct Command: 
./.venv/bin/python3 -m streamlit run app.py
