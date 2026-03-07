import os
from dotenv import load_dotenv
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet, generate_faucet_wallet
from xrpl.models.transactions import EscrowFinish
from xrpl.transaction import submit_and_wait

load_dotenv()
CLIENT = JsonRpcClient("https://s.altnet.rippletest.net:51234")

# --- SETUP PHASE (Use this once to get a wallet) ---
def create_new_faucet_wallet():
    """Generates a new wallet and funds it with 1,000 Test XRP"""
    wallet = generate_faucet_wallet(CLIENT)
    return wallet

# --- OPERATIONAL PHASE (The Sentinel's Daily Job) ---
def get_sentinel_wallet():
    """Loads your existing wallet from the .env file"""
    seed = os.getenv("SENTINEL_SEED")
    if not seed:
        raise ValueError("No SENTINEL_SEED found in .env file!")
    return Wallet.from_seed(seed)

def check_balance(address):
    """Returns current XRP balance of any address"""
    try:
        # We use a specific XRPL method to get the balance accurately
        return CLIENT.get_balance(address)
    except Exception:
        return 0

def release_escrow(owner_address, sequence_number):
    """Signs and submits the transaction to release locked funds"""
    wallet = get_sentinel_wallet()
    
    finish_tx = EscrowFinish(
        account=wallet.classic_address,
        owner=owner_address,
        offer_sequence=sequence_number,
    )
    
    response = submit_and_wait(finish_tx, CLIENT, wallet)
    return response.result

from xrpl.models.requests import AccountObjects

def get_active_escrows(address):
    """Checks the ledger to see if there are any locked payments for this address"""
    request = AccountObjects(account=address, type="escrow")
    response = CLIENT.request(request)
    return response.result.get("account_objects", [])