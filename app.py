import streamlit as st
import os
import time
from dotenv import load_dotenv

# Import logic files; blockchain interaction, for sensor reading, and generation for escrows
from blockchainutil import check_balance, release_escrow
from sensors import get_sensor_data
import buyer_creates_escrow as creator 

load_dotenv(override=True)

# configured from envrionmental variables
THRESHOLD = float(os.getenv("SAFE_TEMP_THRESHOLD", 25.0))
MAX_STRIKES = int(os.getenv("MAX_OVERHEAT_STRIKES", 10))

# preserves data across browswer refreshes
if 'history' not in st.session_state:
    st.session_state.history = []
if 'settled_escrows' not in st.session_state: 
    st.session_state.settled_escrows = []

st.set_page_config(page_title="Smart Delivery Vault", layout="centered")

# sentinel admin controls (sidebar)
st.sidebar.title("🛡️ Sentinel Admin (RP5)")
sentinel_addr = os.getenv('SENTINEL_ADDRESS')

if sentinel_addr:
    st.sidebar.metric("Sentinel Balance", f"{check_balance(sentinel_addr)} XRP")
# the button used to create new escrows including their escrow sequence
st.sidebar.divider()
if st.sidebar.button("🆕 Create New Escrow"):
    with st.sidebar.status("Creating Escrow...", expanded=True) as status:
        creator.create_escrow() 
        status.update(label="Escrow Created!", state="complete")
    st.rerun()

st.sidebar.info(f"**Escrow ID:** {os.getenv('ESCROW_SEQUENCE')}")

# main dashboard to monitor the escrow (high-value assets)
st.title("💊 VitaLedger")
st.write("Ensuring safe transit via real-time environmental monitoring.")

# placeholders for live temp and location updates
temp_stat = st.empty()
loc_info = st.empty()

#button that begins the sentinel guard
if st.button("🚀 Start Sentinel Guard", use_container_width=True): #using raspberry pi 5 as sentinel monitors the assets
    current_seq = os.getenv('ESCROW_SEQUENCE')
    
    # Failsafe to prevent resubmission of an already processed escrow
    if current_seq in st.session_state.settled_escrows:
        st.error(f"⚠️ Escrow {current_seq} already settled.")
        st.stop() 

    verified_steps = 0
    overheat_strikes = 0 
    progress_bar = st.progress(0)
    ruined = False
    temp, location = 0.0, "Unknown" # Initialize to prevent crash if loop fails immediately

    with st.status("🕵️ Monitoring Environment...", expanded=True) as status:
        while verified_steps < 5 and overheat_strikes < MAX_STRIKES: # loop will run when 5 safe checks occur or MAX strikes is achieved
            temp, location = get_sensor_data()
            
            # updating the display so user understands what is going on
            temp_stat.metric("Current Temperature", f"{temp} °C", 
                             delta=None if temp <= THRESHOLD else "OVERHEAT", 
                             delta_color="inverse")
            loc_info.markdown(f"📍 **Verified Location:** {location}")

            if temp > THRESHOLD:
                overheat_strikes += 1
                verified_steps = 0 # Reset safety progress (it's no longer at safe temp)
                st.warning(f"🚨 ALERT: Overheat Strike {overheat_strikes}/{MAX_STRIKES}")
            else:
                overheat_strikes = 0 # Reset strikes if it cools back down
                verified_steps += 1
                st.write(f"✅ Check {verified_steps}/5: Environment Safe")
                
            progress_bar.progress(verified_steps * 20)
            time.sleep(1) #pausing for rest rather than screaming at raspberry pi

        if overheat_strikes >= MAX_STRIKES:
            ruined = True
            status.update(label="❌ MONITORING HALTED: Goods Ruined", state="error", expanded=True)
        else:
            status.update(label="✅ Environment Verified!", state="complete", expanded=False)

    # ACTION LOGIC: deciding whether or not to abort transaction and completing the transaction
    if ruined:
        st.error(f"❌ TRANSACTION ABORTED: The goods reached {temp}°C for {MAX_STRIKES} cycles. The Sentinel will not settle this escrow.")
        st.session_state.history.append({
            "Time": time.strftime("%H:%M:%S"),
            "Sequence": current_seq,
            "Temp": f"{temp}°C",
            "Location": location,
            "Result": "FAILED: RUINED" ##failed code happens when the temperature is not within the desired range typically when overheated
        })
    else:
        st.info("⚖️ Conditions met. Submitting Fulfillment to XRPL...")
        success, result = release_escrow(temp)
        if success:
            st.session_state.settled_escrows.append(current_seq) 
            st.session_state.history.append({
                "Time": time.strftime("%H:%M:%S"),
                "Sequence": current_seq,
                "Temp": f"{temp}°C",
                "Location": location,
                "Result": "Success" ##success code for when the temperature stays within the desired frame for the basis of the project
            })
            st.balloons()
            st.success(f"✅ Payment Released! Tx: {result[:15]}...")
            st.link_button("View on Ledger", f"https://testnet.xrpl.org/transactions/{result}") #animation for balloons when success occurs
        else:
            st.error(f"❌ XRPL Error: {result}")

#History Table: a permanent log of the session
st.divider() #creates a log of all transactions based on specific escrow sequence #s and displays whether or not it is a success.
st.subheader("📜 Delivery Audit Log")
if st.session_state.history:
    st.table(st.session_state.history)
else:
    st.info("No logs available.")