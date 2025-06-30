import requests

BASE = "https://aes.cryptohack.org/symmetry"

def encrypt(plaintext: bytes, iv: bytes) -> bytes:
    r = requests.get(f"{BASE}/encrypt/{plaintext.hex()}/{iv.hex()}/")
    return bytes.fromhex(r.json()['ciphertext'])

def get_flag_cipher():
    r = requests.get(f"{BASE}/encrypt_flag/")
    data = r.json()['ciphertext']
    return bytes.fromhex(data[:32]), bytes.fromhex(data[32:])  # IV, ciphertext

def main():
    iv, flag_ct = get_flag_cipher()
    # Symmetry in OFB: ciphertext = keystream XOR plaintext
    # Re-applying keystream (via encrypt) on ciphertext gives back plaintext
    flag_pt = encrypt(flag_ct, iv)
    print("FLAG:", flag_pt.decode())

if __name__ == "__main__":
    main()

# 0fb_15_5ymm37r1c4l_!!!11!
