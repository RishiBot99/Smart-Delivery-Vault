import os
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import EscrowFinish, TrustSet
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.transaction import submit_and_wait
from xrpl.models.transactions import Memo
from xrpl.account import get_balance

# connecting to the XRPL testnet
CLIENT = JsonRpcClient("https://s.altnet.rippletest.net:51234")

def get_sentinel_wallet():
    return Wallet.from_seed(os.getenv("SENTINEL_SEED")) #retrieves the Sentinel's private key from the .env file

def check_balance(address): #convert drops or the ledger units into XRP
    try:
        # returns balance in XRP
        return get_balance(address, CLIENT) / 1_000_000
    except:
        return 0

def setup_rlusd_trustline():
    
    wallet = get_sentinel_wallet()          ## due to the nature of this project using escrow the use of rlusd is not actually applicable 
    # Official Testnet RLUSD Issuer
    RLUSD_ISSUER = "rMx9U3mG... (Get current from Ripple Docs)" 
    
    trust_set_tx = TrustSet(
        account=wallet.classic_address,
        limit_amount=IssuedCurrencyAmount(      ##however this method is built in place to show its possible functionality 
            currency="RLUSD",                   ##the sentinel uses XRP to settle payments because it is the most efficient manner
            issuer=RLUSD_ISSUER,                ##in this case the use of the escrow is safer since the sentinel doesn't hold the money and only transfers it securely
            value="1000000" 
        )
    )
    return submit_and_wait(trust_set_tx, CLIENT, wallet)

def release_escrow(verified_temp=None):
    """Signs and submits based on .env values"""
    wallet = get_sentinel_wallet()
    raw_seq = os.getenv("ESCROW_SEQUENCE")
    #CHECK for escrow #: If it's missing or literally the string "None"
    if not raw_seq or raw_seq == "None":
        return False, "No Escrow Sequence found in .env. Please create an escrow first!"

    #encoding the data into memos that is put on the temperature on-chain permanently
    memo_text = f"Sentinel Verified: Temp {verified_temp}C" if verified_temp else "Sentinel Verified"
    memo_hex = memo_text.encode("utf-8").hex().upper()

    # Inside release_escrow() in blockchainutil.py
    finish_tx = EscrowFinish(
        account=wallet.classic_address,
        owner=os.getenv("BUYER_ADDRESS").strip(), #person who created escrow
        offer_sequence=int(os.getenv("ESCROW_SEQUENCE")), #id of escrow
        condition=os.getenv("CONDITION").strip(), #lock
        fulfillment=os.getenv("FULFILLMENT").strip() #key
    
    )
    
    #signing & sending the final transaction
    response = submit_and_wait(finish_tx, CLIENT, wallet)
    return response.is_successful(), response.result.get("hash")