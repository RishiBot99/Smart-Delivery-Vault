print("--- Checkpoint 0: Script is starting... ---")

import os
import datetime
from dotenv import load_dotenv

# XRPL Imports
from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet, Wallet
from xrpl.models.transactions import EscrowCreate, Payment
from xrpl.transaction import submit_and_wait
from xrpl.utils import datetime_to_ripple_time

print("--- Checkpoint 1: Libraries imported... ---")

load_dotenv()
# I'm adding a 30-second timeout so it doesn't hang forever
client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

def create_escrow():
    print("--- Checkpoint 2: Entering create_escrow function... ---")
    
    sentinel_addr = os.getenv("SENTINEL_ADDRESS")
    condition = os.getenv("CONDITION")
    
    if not sentinel_addr or not condition:
        print("❌ ERROR: Your .env file is missing SENTINEL_ADDRESS or CONDITION.")
        print(f"Current SENTINEL_ADDRESS: {sentinel_addr}")
        print(f"Current CONDITION: {condition}")
        return

    sentinel_addr = sentinel_addr.strip()
    condition = condition.strip()

    print("--- Checkpoint 3: Requesting funds from Faucet (This can take 20 seconds)... ---")
    try:
        buyer_wallet = generate_faucet_wallet(client)
        print(f"✅ Buyer Created: {buyer_wallet.classic_address}")
    except Exception as e:
        print(f"❌ Faucet Error: {e}")
        return

    print("--- Checkpoint 4: Activating Sentinel account... ---")
    activation_tx = Payment(
        account=buyer_wallet.classic_address,
        amount="20000000", 
        destination=sentinel_addr
    )
    submit_and_wait(activation_tx, client, buyer_wallet)

    print("--- Checkpoint 5: Building Escrow transaction... ---")
    now = datetime.datetime.now(datetime.timezone.utc)
    cancel_time = now + datetime.timedelta(hours=24)
    ripple_cancel_time = datetime_to_ripple_time(cancel_time)

    escrow_tx = EscrowCreate(
        account=buyer_wallet.classic_address,
        amount="10000000",
        destination=sentinel_addr, 
        condition=condition,
        cancel_after=ripple_cancel_time
    )

    print("--- Checkpoint 6: Submitting Escrow to Ledger... ---")
    try:
        response = submit_and_wait(escrow_tx, client, buyer_wallet)
        if response.is_successful():
            res_data = response.result
            # Try to find Sequence in multiple places
            seq = res_data.get("Sequence") or res_data.get("tx_json", {}).get("Sequence")
            print(f"🚀 SUCCESS! ESCROW_SEQUENCE: {seq}")
        else:
            print(f"❌ Ledger Error: {response.result}")
    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    print("--- Checkpoint: __main__ block triggered... ---")
    create_escrow()