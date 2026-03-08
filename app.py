import streamlit as st
from dotenv import load_dotenv
import os
import time
from blockchainutil import check_balance, release_escrow
from sensors import get_sensor_data  # Import our updated function

load_dotenv(override=True)

st.set_page_config(page_title="Smart Delivery Vault", page_icon="🛡️")
st.title("🛡️ Smart Delivery Vault")

# Sidebar - Real-time stats
addr = os.getenv('SENTINEL_ADDRESS')
if addr:
    st.sidebar.subheader("Sentinel Status")
    st.sidebar.metric("Balance", f"{check_balance(addr)} XRP")
    st.sidebar.info(f"Escrow ID: {os.getenv('ESCROW_SEQUENCE')}")

# Main UI
st.write("### Live Telemetry")
col1, col2, col3 = st.columns(3)
temp_stat = col1.empty()
dist_stat = col2.empty()
loc_stat = col3.empty()

if st.button("Start Sentinel Guard", use_container_width=True):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    verified_steps = 0
    target_steps = 5 
    
    while verified_steps < target_steps:
        # GET DATA FROM OUR HARDWARE LAYER
        temp, dist, tampered, loc = get_sensor_data()
        
        # Update Dashboard
        temp_stat.metric("Temperature", f"{temp} °C")
        dist_stat.metric("Lidar Distance", f"{dist} cm")
        loc_stat.write(f"**Location:** \n {loc}")
        
        # VALIDATION LOGIC
        # 1. Temp must be safe (< 25)
        # 2. Must not be tampered (Lidar detects box is closed)
        if temp < 25.0 and not tampered:
            verified_steps += 1
            status_text.success(f"Step {verified_steps}/{target_steps}: Conditions Optimal.")
        else:
            verified_steps = 0 # Reset progress if conditions fail
            status_text.error("🚨 SECURITY BREACH: Conditions Out of Bounds!")
            
        progress_bar.progress(verified_steps / target_steps)
        time.sleep(1.5)
    
    st.warning("⚖️ Threshold Reached. Validating Cryptographic Fulfillment...")
    
    # Trigger XRPL Release
    with st.spinner("Submitting to XRPL Ledger..."):
        success, tx_hash = release_escrow()
    
    if success:
        st.balloons()
        st.success("✅ Payment Released Successfully!")
        st.write(f"**Transaction Hash:** `{tx_hash}`")
        st.link_button("View on XRPL Explorer", f"https://testnet.xrpl.org/transactions/{tx_hash}")
    else:
        st.error(f"❌ Release Failed: {tx_hash}")