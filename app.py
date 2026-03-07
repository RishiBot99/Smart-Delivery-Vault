import streamlit as st
import pandas as pd
from blockchainutil import check_balance, CLIENT
from sentinelmonitor import get_temperature
import os

st.title("🛡️ XRPL Hardware Sentinel")
st.write(f"Monitoring Wallet: `{os.getenv('SENTINEL_ADDRESS')}`")

# 1. Sidebar Stats
with st.sidebar:
    st.header("Ledger Status")
    balance = check_balance(os.getenv('SENTINEL_ADDRESS'))
    st.metric(label="Sentinel Balance", value=f"{balance} XRP")

# 2. Live Sensor Feed
st.subheader("Live Temperature Feed")
current_temp = get_temperature()
st.info(f"Current Temperature: {current_temp}°C")

# 3. Escrow Control
st.subheader("Active Escrows")
escrow_seq = st.text_input("Enter Escrow Sequence Number to Monitor")

if st.button("Start Sentinel Guard"):
    st.warning("Sentinel is now active. Monitoring   conditions...")
    # Where Sentinel Monitor logic code runs