import streamlit as st
import os
import time
from dotenv import load_dotenv

# Import your logic files
from blockchainutil import check_balance, release_escrow
from sensors import get_sensor_data
import buyer_creates_escrow as creator 

if 'settled_escrows' not in st.session_state:
    st.session_state.settled_escrows = []
# 1. Force reload .env to get the LATEST Sequence/Buyer Address
load_dotenv(override=True)

st.set_page_config(page_title="Smart Delivery Vault", layout="wide")

# --- SIDEBAR: MANAGEMENT ---
st.sidebar.title("🛠️ Sentinel Admin")
sentinel_addr = os.getenv('SENTINEL_ADDRESS')

if sentinel_addr:
    st.sidebar.metric("Sentinel Balance", f"{check_balance(sentinel_addr)} XRP")

st.sidebar.divider()
st.sidebar.subheader("Escrow Management")

# BUTTON TO GENERATE NEW ESCROW
if st.sidebar.button("🆕 Create New Escrow (Buyer Side)"):
    with st.sidebar.status("Creating Escrow on Ledger...", expanded=True) as status:
        st.write("Generating temporary buyer wallet...")
        # This function runs your script logic and updates .env
        creator.create_escrow() 
        status.update(label="Escrow Created!", state="complete")
    
    # Refresh the UI to show the new BUYER_ADDRESS and ESCROW_SEQUENCE
    st.rerun()

st.sidebar.info(f"**Monitoring Escrow:** {os.getenv('ESCROW_SEQUENCE')}")
st.sidebar.caption(f"Buyer: {os.getenv('BUYER_ADDRESS')}")


# --- MAIN UI: MONITORING ---
st.title("🛡️ Smart Delivery Vault")
st.write("This vault releases payment only if temperature and security parameters are met.")

col1, col2 = st.columns(2)

if st.button("🚀 Start Sentinel Guard", use_container_width=True):
    current_seq = os.getenv('ESCROW_SEQUENCE')
    verified_steps = 0
    progress_bar = st.progress(0)

    # FAILSAFE CHECK
    if current_seq in st.session_state.settled_escrows:
        st.error(f"⚠️ ESCROW ALERT: Sequence {current_seq} has already been settled!")
        st.info("Please go to the sidebar and click 'Create New Escrow' to start a new delivery.")
        st.stop() # Stops the code from running further
    
    # Loop for 5 "Success" readings
    while verified_steps < 5:
        # GET FAKE DATA FROM sensors.py
        temp, distance, tampered, location = get_sensor_data()
        
        with col1:
            st.metric("Temperature", f"{temp}°C", delta="-0.2" if temp < 25 else "HIGH")
        with col2:
            st.metric("Lidar Distance", f"{distance}cm", delta="Locked" if not tampered else "TAMPERED")

        if temp < 25.0 and not tampered:
            verified_steps += 1
            st.toast(f"Condition Met ({verified_steps}/5)")
        else:
            verified_steps = 0 # Reset if it gets too hot/tampered
            st.error("CONDITIONS VIOLATED")
            
        progress_bar.progress(verified_steps * 20)
        time.sleep(1) # Simulated interval
    
    st.success("⚖️ All conditions met. Releasing payment...")
    
    # 2. TRIGGER THE SETTLEMENT
    success, result = release_escrow()
    
    if success:
        st.session_state.settled_escrows.append(current_seq) # Mark as finished
        st.balloons()
        st.success(f"✅ Payment Released! Hash: {result}")
        st.link_button("View on Ledger", f"https://testnet.xrpl.org/transactions/{result}")
    else:
        st.error(f"❌ Settlement Failed: {result}")