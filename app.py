import streamlit as st
from dotenv import load_dotenv
import os
import time
from blockchainutil import check_balance, release_escrow # Keep your name!
# import sensors # Your partner's file

load_dotenv(override=True)

st.title("🛡️ Smart Delivery Vault")

# Sidebar
addr = os.getenv('SENTINEL_ADDRESS')
if addr:
    st.sidebar.metric("Sentinel Balance", f"{check_balance(addr)} XRP")
    st.sidebar.write(f"Monitoring: `{os.getenv('ESCROW_SEQUENCE')}`")


# THE CORE FUNCTIONALITY:
if st.button("Start Sentinel Guard"):
    # 1. Start the loop
    placeholder = st.empty()
    
    # We loop until the conditions are met
    verified_steps = 0
    while verified_steps < 5:
        # Get data from your partner's code
        # temp = sensors.get_temp() 
        # is_open = sensors.check_lidar()
        temp = 22.0 # Placeholder until partner finishes
        
        
        placeholder.write(f"🔍 Monitoring... Current Temp: {temp}°C | Progress: {verified_steps}/5")
        
        if temp < 25.0:
            verified_steps += 1
        else:
            verified_steps = 0
            
        time.sleep(1) # Sped up to 1 second for demo purposes
    
    st.warning("⚖️ Conditions Met! Submitting Fulfillment to XRPL...")
    
    # Note: Make sure your release_escrow function in blockchainutil.py 
    # accepts the sequence from the .env!
    success, tx_hash = release_escrow()
    
    if success:
        st.balloons()
        st.success("✅ Payment Released!")
        st.code(f"Tx Hash: {tx_hash}")
        st.link_button("View on Ledger", f"https://testnet.xrpl.org/transactions/{tx_hash}")
    else:
        st.error(f"❌ Release Failed: {tx_hash}")