import requests

URL = "https://aes.cryptohack.org/flipping_cookie"

def xor_bytes(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

def get_cookie():
    response = requests.get(f"{URL}/get_cookie/")
    data = response.json()
    cookie_hex = data["cookie"]
    iv = bytes.fromhex(cookie_hex[:32])
    ciphertext = bytes.fromhex(cookie_hex[32:])
    return ciphertext, iv

def forge_iv(original_iv, original_plain, target_plain):
    return xor_bytes(original_iv, xor_bytes(original_plain, target_plain))

def main():
    ciphertext, iv = get_cookie()

    # Modify the first block to flip "admin=False" to "admin=True;"
    original_plain = b"admin=False;expi"
    target_plain = b"admin=True;\x05\x05\x05\x05\x05"

    forged_iv = forge_iv(iv, original_plain, target_plain)

    forged_iv_hex = forged_iv.hex()
    ciphertext_hex = ciphertext.hex()

    response = requests.get(f"{URL}/check_admin/{ciphertext_hex}/{forged_iv_hex}/")
    print(response.json())

main()

# crypto{4u7h3n71c4710n_15_3553n714l}
