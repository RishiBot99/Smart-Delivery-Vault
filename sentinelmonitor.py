import os
import time
from dotenv import load_dotenv

# Hardware Import
import hardware_manager #for talking to the temp sensor

# XRPL imports
import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import EscrowFinish
from xrpl.transaction import submit_and_wait

# 1. Load environment variables to pull the secrets and IDs from the env file
load_dotenv()
SENTINEL_SEED = os.getenv("SENTINEL_SEED")
BUYER_ADDRESS = os.getenv("BUYER_ADDRESS")
ESCROW_SEQUENCE = int(os.getenv("ESCROW_SEQUENCE", 0)) #making sure escrow sequence is int
CONDITION = os.getenv("CONDITION") #lock
FULFILLMENT = os.getenv("FULFILLMENT") #key

# 2. Setup XRPL Client and Connection
client = JsonRpcClient("https://s.altnet.rippletest.net:51234")
sentinel_wallet = Wallet.from_seed(SENTINEL_SEED)

def trigger_escrow_finish():
    """Signs and submits an EscrowFinish transaction to the XRPL."""
    print(f"\n[XRPL] Logic Triggered: Attempting to finish Escrow #{ESCROW_SEQUENCE}...")
    
    try:
        finish_tx = EscrowFinish(
            account=sentinel_wallet.classic_address,
            owner=BUYER_ADDRESS, #account that created escrow
            offer_sequence=ESCROW_SEQUENCE,
            condition=CONDITION,
            fulfillment=FULFILLMENT
        )
        #waiting for ledger to validate the submitted transaction
        response = submit_and_wait(finish_tx, client, sentinel_wallet)
        
        if response.is_successful():
            print(f"✅ Success! Escrow finished. Tx Hash: {response.result.get('hash')}")
            return True
        else:
            print(f"❌ Transaction failed: {response.result.get('engine_result_message')}") #incase of failure 
            return False

    except Exception as e:
        print(f"⚠️ Error during XRPL transaction: {e}")
        return False

def run_sentinel_hardware_monitor():
    """Polls the REAL BMP180 sensor and tracks 'safe' readings."""
    safe_check_count = 0
    overheat_strikes = 0
    required_safe_checks = 5
    # configured using the environmental variables to consider for perishables; food/medicine
    max_strikes = int(os.getenv("MAX_OVERHEAT_STRIKES", 10))
    threshold = float(os.getenv("SAFE_TEMP_THRESHOLD", 25.0)) 

    print(f"--- 🛡️ HARDWARE SENTINEL ACTIVE ---")
    print(f"Sentinel Address: {sentinel_wallet.classic_address}")
    print(f"Threshold: < {threshold}°C | Max Overheat Strikes: {max_strikes}\n")

    while safe_check_count < required_safe_checks:
        try:
            current_temp = round(hardware_manager.result(), 2)
        except Exception as e:
            print(f"🚨 SENSOR DISCONNECTED: {e}") #failsafe if sensor is unplugged or broken using temp to force critical failure
            current_temp = 999.9
        
        if current_temp > threshold:
            overheat_strikes += 1
            safe_check_count = 0 
            print(f"🚨 ALERT: Overheat! Strike {overheat_strikes}/{max_strikes} (Current: {current_temp}°C)")
            
            if overheat_strikes >= max_strikes: #means the assets are ruined and cannot be used
                print("\n❌ CRITICAL FAILURE: The goods are ruined. Transaction aborted.")
                return # Exit without settling
        else:
            overheat_strikes = 0 # Reset strikes if it returns to safe levels
            safe_check_count += 1
            print(f"✨ Safe: {current_temp}°C (Check {safe_check_count}/{required_safe_checks})")
            
        time.sleep(2)
    #success the 5 check requirement was met and assets are safe.
    print(f"\n📦 Verified safe environment. Proceeding to settlement...")
    trigger_escrow_finish()

if __name__ == "__main__":
    #checking for basic confirguration prior to start
    if not SENTINEL_SEED or not BUYER_ADDRESS or ESCROW_SEQUENCE == 0:
        print("❌ Error: Missing configuration in .env file.")
    else:
        run_sentinel_hardware_monitor()