import hashlib
import binascii

def generate_lock_and_key(secret_passphrase):
    # 1. Generate the Preimage (The Key)
    preimage = secret_passphrase.encode('utf-8')
    if len(preimage) > 32:
        preimage = preimage[:32]
    else:
        preimage = preimage.ljust(32, b'\0')

    # 2. Create the Fulfillment (The Key - for the Sentinel)
    # Binary format: [Prefix A0][Length 22][Tag 80][Length 20][Data...]
    fulfillment_bin = b'\xA0\x22\x80\x20' + preimage
    fulfillment_hex = binascii.hexlify(fulfillment_bin).upper().decode()

    # 3. Create the Condition (The Lock - for the Buyer)
    fingerprint = hashlib.sha256(preimage).digest()
    # Binary format: [Prefix A0][Length 25][Tag 80][Length 20][Hash][Cost 81 01 20]
    condition_bin = b'\xA0\x25\x80\x20' + fingerprint + b'\x81\x01\x20'
    condition_hex = binascii.hexlify(condition_bin).upper().decode()

    return condition_hex, fulfillment_hex

# CHOOSE A SECRET PHRASE (Keep this secret in real life!)
# For the hackathon, just use something like:
my_secret = "sentinel_pi_5_monitor_active"

cond, full = generate_lock_and_key(my_secret)

print("--- COPY THESE INTO YOUR .env FILE ---")
print(f"CONDITION={cond}")
print(f"FULFILLMENT={full}")