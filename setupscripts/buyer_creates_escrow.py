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


def update_env_variable(key, value):
    """
    Finds a key in the .env file and updates its value.
    If the key doesn't exist, it adds it to the end.
    """
    env_file = ".env"
    
    # 1. Read the existing lines
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # 2. Update the line if it exists
    found = False
    new_lines = []
    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            found = True
        else:
            new_lines.append(line)
            
    # 3. If the key wasn't there, add it
    if not found:
        new_lines.append(f"{key}={value}\n")

    # 4. Write everything back
    with open(env_file, "w") as f:
        f.writelines(new_lines)
print("--- Checkpoint 1: Libraries imported... ---")


def create_escrow():
    load_dotenv()
    # I'm adding a 30-second timeout so it doesn't hang forever
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234")
    
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
        # ... inside your create_escrow() function ...

    if response.is_successful():
        seq = response.result['Sequence']
        buyer_addr = buyer_wallet.classic_address
    
        # AUTOMATICALLY UPDATE THE .ENV
        print("Writing new values to .env...")
        update_env_variable("BUYER_ADDRESS", buyer_addr)
        update_env_variable("ESCROW_SEQUENCE", seq)
    
        print("\n" + "🚀 SUCCESS!" + "="*30)
        print(f"NEW BUYER_ADDRESS: {buyer_addr}")
        print(f"NEW ESCROW_SEQUENCE: {seq}")
        print("= (The .env file has been updated automatically) =")


if __name__ == "__main__":
    print("--- Checkpoint: __main__ block triggered... ---")
    create_escrow()