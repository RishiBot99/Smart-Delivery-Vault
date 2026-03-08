import os
import time
# import random  # REMOVED: No longer needed
from dotenv import load_dotenv

# Hardware Import
import hardware_manager 

# XRPL imports
import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import EscrowFinish
from xrpl.transaction import submit_and_wait

# 1. Load environment variables
load_dotenv()
SENTINEL_SEED = os.getenv("SENTINEL_SEED")
BUYER_ADDRESS = os.getenv("BUYER_ADDRESS")
# Ensure the sequence is an integer
ESCROW_SEQUENCE = int(os.getenv("ESCROW_SEQUENCE", 0))
CONDITION = os.getenv("CONDITION")
FULFILLMENT = os.getenv("FULFILLMENT")

# 2. Setup XRPL Client
client = JsonRpcClient("https://s.altnet.rippletest.net:51234")
sentinel_wallet = Wallet.from_seed(SENTINEL_SEED)

def trigger_escrow_finish():
    """Signs and submits an EscrowFinish transaction to the XRPL."""
    print(f"\n[XRPL] Logic Triggered: Attempting to finish Escrow #{ESCROW_SEQUENCE}...")
    
    try:
        finish_tx = EscrowFinish(
            account=sentinel_wallet.classic_address,
            owner=BUYER_ADDRESS,
            offer_sequence=ESCROW_SEQUENCE,
            condition=CONDITION,
            fulfillment=FULFILLMENT
        )

        response = submit_and_wait(finish_tx, client, sentinel_wallet)
        
        if response.is_successful():
            print(f"✅ Success! Escrow finished. Tx Hash: {response.result.get('hash')}")
            return True
        else:
            print(f"❌ Transaction failed: {response.result.get('engine_result_message')}")
            return False

    except Exception as e:
        print(f"⚠️ Error during XRPL transaction: {e}")
        return False

def run_sentinel_hardware_monitor():
    """
    Polls the REAL BMP180 sensor and tracks 'safe' readings.
    """
    safe_check_count = 0
    required_safe_checks = 5
    threshold = 24.0 

    print(f"--- 🛡️ HARDWARE SENTINEL ACTIVE ---")
    print(f"Sentinel Address: {sentinel_wallet.classic_address}")
    print(f"Target Escrow Owner: {BUYER_ADDRESS}")
    print(f"Target Escrow Sequence: {ESCROW_SEQUENCE}")
    print(f"Threshold: < {threshold}°C\n")

    while safe_check_count < required_safe_checks:
        try:
            # 3. GET REAL DATA FROM HARDWARE
            # We call the result() function from your partner's file
            current_temp = round(hardware_manager.result(), 2)
        except Exception as e:
            # 4. HARDWARE FAILSAFE
            # If the sensor is unplugged, we set an 'Impossible' high temp
            # to prevent the escrow from ever finishing.
            print(f"🚨 SENSOR DISCONNECTED: {e}")
            current_temp = 999.9
        
        # 5. Condition Logic
        if current_temp > threshold:
            # If 999.9 (error) or real high temp, reset the count
            print(f"🚨 ALERT: Temp Spike/Hardware Error! Current: {current_temp}°C. Resetting counter.")
            safe_check_count = 0 
        else:
            safe_check_count += 1
            print(f"✨ Safe: {current_temp}°C (Check {safe_check_count}/{required_safe_checks})")

        # Poll every 2 seconds
        time.sleep(2)

    # 6. Requirement Met: Trigger Blockchain Action
    print(f"\n📦 Verified safe environment for {required_safe_checks} cycles.")
    trigger_escrow_finish()

if __name__ == "__main__":
    if not SENTINEL_SEED or not BUYER_ADDRESS or ESCROW_SEQUENCE == 0:
        print("❌ Error: Missing configuration in .env file.")
    else:
        run_sentinel_hardware_monitor()