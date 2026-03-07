import os
import time
import random
from dotenv import load_dotenv

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
ESCROW_SEQUENCE = int(os.getenv("ESCROW_SEQUENCE", 0))
# Optional: Condition/Fulfillment if using conditional escrows
CONDITION = os.getenv("CONDITION")
FULFILLMENT = os.getenv("FULFILLMENT")

# 2. Setup XRPL Client
# Using the public Testnet JSON-RPC endpoint
client = JsonRpcClient("https://s.altnet.rippletest.net:51234")
sentinel_wallet = Wallet.from_seed(SENTINEL_SEED)

def trigger_escrow_finish():
    """
    Signs and submits an EscrowFinish transaction to the XRPL.
    """
    print(f"\n[XRPL] Logic Triggered: Attempting to finish Escrow #{ESCROW_SEQUENCE}...")
    
    try:
        # Construct the EscrowFinish transaction
        # The 'account' is the Sentinel (who is sending the tx)
        # The 'owner' is the Buyer (who created the escrow)
        finish_tx = EscrowFinish(
            account=sentinel_wallet.classic_address,
            owner=BUYER_ADDRESS,
            offer_sequence=ESCROW_SEQUENCE,
            condition=CONDITION,      # Include if condition was set
            fulfillment=FULFILLMENT    # Include if condition was set
        )

        # Sign and submit
        response = submit_and_wait(finish_tx, client, sentinel_wallet)
        
        if response.is_successful():
            print(f"✅ Success! Escrow finished. Tx Hash: {response.result['hash']}")
            return True
        else:
            print(f"❌ Transaction failed: {response.result['meta']['TransactionResult']}")
            return False

    except Exception as e:
        print(f"⚠️ Error during XRPL transaction: {e}")
        return False

def run_sentinel_simulation():
    """
    Simulates a temperature sensor and tracks 'safe' readings.
    """
    safe_check_count = 0
    required_safe_checks = 5
    threshold = 24.0 

    print(f"--- XRPL-Sentinel Monitoring Started ---")
    print(f"Sentinel Address: {sentinel_wallet.classic_address}")
    print(f"Target Escrow Owner: {BUYER_ADDRESS}")
    print(f"Target Escrow Sequence: {ESCROW_SEQUENCE}")
    print(f"Threshold: < {threshold}°C\n")

    while safe_check_count < required_safe_checks:
        # 3. Simulate Temperature Sensor (18°C to 25°C)
        current_temp = round(random.uniform(18.0, 25.5), 2)
        
        # 4. Condition Logic
        if current_temp > threshold:
            print(f"🚨 ALERT: Temperature Spike! Current: {current_temp}°C. Resetting safe counter.")
            safe_check_count = 0 # Optional: Reset if damage is irreversible
        else:
            safe_check_count += 1
            print(f"✨ Safe: {current_temp}°C (Check {safe_check_count}/{required_safe_checks})")

        # Wait 2 seconds between "sensor readings"
        time.sleep(2)

    # 5. Requirement Met: Trigger Blockchain Action
    print(f"\n📦 Safe shipping range verified for {required_safe_checks} consecutive checks.")
    trigger_escrow_finish()

if __name__ == "__main__":
    if not SENTINEL_SEED or not BUYER_ADDRESS or ESCROW_SEQUENCE == 0:
        print("❌ Error: Missing configuration in .env file.")
    else:
        run_sentinel_simulation()