import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet

# Connect to the Testnet
client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

print("Generating your Sentinel Wallet...")
wallet = generate_faucet_wallet(client)

print("-" * 30)
print(f"ADDRESS: {wallet.classic_address}")
print(f"SEED:    {wallet.seed}")
print("-" * 30)
print(f"VIEW ON LEDGER: https://testnet.xrpl.org/accounts/{wallet.classic_address}")