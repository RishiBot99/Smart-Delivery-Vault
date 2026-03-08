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

st.set_page_config(page_title="Smart Delivery Vault", layout="wide")

# --- SIDEBAR: MANAGEMENT ---
st.sidebar.title("🛠️ Sentinel Admin")
sentinel_addr = os.getenv('SENTINEL_ADDRESS')

if sentinel_addr:
    st.sidebar.metric("Sentinel Balance", f"{check_balance(sentinel_addr)} XRP")

st.sidebar.divider()
st.sidebar.subheader("Escrow Management")

if st.sidebar.button("🆕 Create New Escrow (Buyer Side)"):
    with st.sidebar.status("Creating Escrow on Ledger...", expanded=True) as status:
        st.write("Generating temporary buyer wallet...")
        creator.create_escrow() 
        status.update(label="Escrow Created!", state="complete")
    st.rerun()

st.sidebar.info(f"**Monitoring Escrow:** {os.getenv('ESCROW_SEQUENCE')}")
st.sidebar.caption(f"Buyer: {os.getenv('BUYER_ADDRESS')}")

# --- MAIN UI: MONITORING ---
st.title("🛡️ Smart Delivery Vault")
st.write("This vault releases payment only if temperature and security parameters are met.")

# Placeholders for metrics (prevents the "waterfall" effect)
col1, col2 = st.columns(2)
temp_stat = col1.empty()
dist_stat = col2.empty()

if st.button("🚀 Start Sentinel Guard", use_container_width=True):
    current_seq = os.getenv('ESCROW_SEQUENCE')
    verified_steps = 0
    progress_bar = st.progress(0)

    # FAILSAFE CHECK
    if current_seq in st.session_state.settled_escrows:
        st.error(f"⚠️ ESCROW ALERT: Sequence {current_seq} has already been settled!")
        st.stop() 
    
    # Loop for 5 "Success" readings
    with st.status("🕵️ Sentinel Monitoring Active...", expanded=True) as status:
        while verified_steps < 5:
            temp, distance, tampered, location = get_sensor_data()
            
            # Update metrics in the fixed placeholders
            temp_stat.metric("Temperature", f"{temp}°C", delta="-0.2" if temp < 25 else "HIGH")
            dist_stat.metric("Lidar Distance", f"{distance}cm", delta="Locked" if not tampered else "TAMPERED")

            if temp < 25.0 and not tampered:
                verified_steps += 1
                st.toast(f"Condition Met ({verified_steps}/5)")
            else:
                verified_steps = 0 
                st.error("CONDITIONS VIOLATED")
                
            progress_bar.progress(verified_steps * 20)
            time.sleep(1) 

        status.update(label="✅ All Conditions Verified!", state="complete", expanded=False)
    
    st.warning("⚖️ Conditions met. Submitting Fulfillment to XRPL...")
    
    # 2. TRIGGER THE SETTLEMENT
    success, result = release_escrow()
    
    if success:
        # COMBINED SUCCESS LOGIC
        st.session_state.settled_escrows.append(current_seq) 
        st.session_state.history.append({
            "Time": time.strftime("%H:%M:%S"),
            "Escrow Seq": current_seq,
            "Result": "Success (Released)",
            "Tx Hash": result[:12] + "..." 
        })
        
        st.balloons()
        st.success(f"✅ Payment Released! Hash: {result}")
        st.link_button("View on Ledger", f"https://testnet.xrpl.org/transactions/{result}")
    else:
        st.error(f"❌ Settlement Failed: {result}")

# --- HISTORY TABLE ---
st.divider()
st.subheader("📜 Delivery Audit Log")
if st.session_state.history:
    st.table(st.session_state.history)
else:
    st.info("No deliveries processed yet.")