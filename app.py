import streamlit as st
import os
import time
from dotenv import load_dotenv

# Import your logic files
from blockchainutil import check_balance, release_escrow
from sensors import get_sensor_data
import buyer_creates_escrow as creator 

# Initialize Session States
if 'history' not in st.session_state:
    st.session_state.history = []
if 'settled_escrows' not in st.session_state: 
    st.session_state.settled_escrows = []

load_dotenv(override=True)

st.set_page_config(page_title="Smart Delivery Vault", layout="centered")

# --- SIDEBAR: MANAGEMENT ---
st.sidebar.title("🛡️ Sentinel Admin")
sentinel_addr = os.getenv('SENTINEL_ADDRESS')

if sentinel_addr:
    st.sidebar.metric("Sentinel Balance", f"{check_balance(sentinel_addr)} XRP")

st.sidebar.divider()
if st.sidebar.button("🆕 Create New Escrow"):
    with st.sidebar.status("Creating Escrow...", expanded=True) as status:
        creator.create_escrow() 
        status.update(label="Escrow Created!", state="complete")
    st.rerun()

st.sidebar.info(f"**Escrow ID:** {os.getenv('ESCROW_SEQUENCE')}")

# --- MAIN UI ---
st.title("🛡️ Smart Delivery Vault")
st.write("Ensuring safe transit via real-time environmental monitoring.")

# UI Placeholders
temp_stat = st.empty()
loc_info = st.empty()

if st.button("🚀 Start Sentinel Guard", use_container_width=True):
    current_seq = os.getenv('ESCROW_SEQUENCE')
    
    # FAILSAFE
    if current_seq in st.session_state.settled_escrows:
        st.error(f"⚠️ Escrow {current_seq} already settled.")
        st.stop() 

    verified_steps = 0
    progress_bar = st.progress(0)

    with st.status("🕵️ Monitoring Environment...", expanded=True) as status:
        while verified_steps < 5:
            # UNPACKING ONLY 2 VALUES
            temp, location = get_sensor_data()
            
            # Update Display
            temp_stat.metric("Current Temperature", f"{temp} °C", delta=None if temp < 25 else "OVERHEAT")
            loc_area_text = f"📍 **Verified Location:** {location}"
            loc_info.markdown(loc_area_text)

            if temp < 25.0:
                verified_steps += 1
                st.write(f"✅ Check {verified_steps}/5: Stable")
            else:
                verified_steps = 0 
                st.write("🚨 ALERT: TEMPERATURE EXCEEDED THRESHOLD")
                
            progress_bar.progress(verified_steps * 20)
            time.sleep(1) 

        status.update(label="✅ Environment Verified!", state="complete", expanded=False)
    
    st.warning("⚖️ Conditions met. Submitting Fulfillment to XRPL...")
    
    success, result = release_escrow()
    
    if success:
        st.session_state.settled_escrows.append(current_seq) 
        st.session_state.history.append({
            "Time": time.strftime("%H:%M:%S"),
            "Sequence": current_seq,
            "Temp": f"{temp}°C",
            "Location": location,
            "Result": "Success"
        })
        st.balloons()
        st.success(f"✅ Payment Released! Tx: {result[:15]}...")
        st.link_button("View on Ledger", f"https://testnet.xrpl.org/transactions/{result}")
    else:
        st.error(f"❌ Settlement Failed: {result}")

# --- HISTORY ---
st.divider()
st.subheader("📜 Delivery Audit Log")
if st.session_state.history:
    st.table(st.session_state.history)
else:
    st.info("No logs available.")