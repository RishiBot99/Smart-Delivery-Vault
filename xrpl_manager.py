import os
from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet
from dotenv import load_dotenv

# 1. Setup Environment
load_dotenv()
client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

def setup_wallets():
    print("Connecting to XRPL Testnet...")
    # This generates a wallet with 1,000 FREE test XRP
    test_wallet = generate_faucet_wallet(client)
    print(f"Address: {test_wallet.classic_address}")
    print(f"Seed: {test_wallet.seed}")
    return test_wallet

if __name__ == "__main__":
    wallet = setup_wallets()