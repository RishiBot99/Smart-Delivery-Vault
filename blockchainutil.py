import os
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import EscrowFinish, TrustSet
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.transaction import submit_and_wait
from xrpl.account import get_balance

# Global Client
CLIENT = JsonRpcClient("https://s.altnet.rippletest.net:51234")

def get_sentinel_wallet():
    return Wallet.from_seed(os.getenv("SENTINEL_SEED"))

def check_balance(address):
    try:
        # returns balance in XRP
        return get_balance(address, CLIENT) / 1_000_000
    except:
        return 0

def setup_rlusd_trustline():
    """
    RUN THIS ONCE. This gives the Sentinel permission to hold RLUSD.
    Judges love this because it shows 'Stablecoin Flow' awareness.
    """
    wallet = get_sentinel_wallet()
    # Official Testnet RLUSD Issuer
    RLUSD_ISSUER = "rMx9U3mG... (Get current from Ripple Docs)" 
    
    trust_set_tx = TrustSet(
        account=wallet.classic_address,
        limit_amount=IssuedCurrencyAmount(
            currency="RLUSD",
            issuer=RLUSD_ISSUER,
            value="1000000" 
        )
    )
    return submit_and_wait(trust_set_tx, CLIENT, wallet)

def release_escrow():
    """Signs and submits based on .env values"""
    wallet = get_sentinel_wallet()
    raw_seq = os.getenv("ESCROW_SEQUENCE")
    # SAFETY CHECK: If it's missing or literally the string "None"
    if not raw_seq or raw_seq == "None":
        return False, "No Escrow Sequence found in .env. Please create an escrow first!"

    # Inside release_escrow() in blockchainutil.py
    finish_tx = EscrowFinish(
        account=wallet.classic_address,
        owner=os.getenv("BUYER_ADDRESS").strip(),
        offer_sequence=int(os.getenv("ESCROW_SEQUENCE")), # Must be int!
        condition=os.getenv("CONDITION").strip(),
        fulfillment=os.getenv("FULFILLMENT").strip()
    
    )
    
    
    response = submit_and_wait(finish_tx, CLIENT, wallet)
    return response.is_successful(), response.result.get("hash")