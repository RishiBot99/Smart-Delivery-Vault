from cryptoconditions import PreimageSha256
import binascii

# This is a secret password only your RP5 knows
secret = b"hackathon_sentinel_2024_secure_key"
fulfillment_obj = PreimageSha256(preimage=secret)

fulfillment_hex = binascii.hexlify(fulfillment_obj.serialize_binary()).upper().decode()
condition_hex = binascii.hexlify(fulfillment_obj.condition_binary).upper().decode()

print(f"--- ADD THESE TO YOUR .env ---")
print(f"CONDITION={condition_hex}")
print(f"FULFILLMENT={fulfillment_hex}")