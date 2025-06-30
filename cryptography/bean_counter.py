import requests
import os

BASE = "https://aes.cryptohack.org/bean_counter"

def get_ciphertext_png():
    resp = requests.get(f"{BASE}/encrypt/")
    # The server replies with JSON: { "ciphertext": [...] } (hex strings per block)
    print(resp.json())
    return bytes.fromhex(resp.json()['encrypted'])

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def recover_plaintext(encrypted_png: bytes):
    # Re-run through the same "encrypt" endpoint to XOR keystream again
    # This cancels it out: CT xor keystream xor keystream = PT
    resp = requests.post(f"{BASE}/encrypt/", data=encrypted_png)
    return resp.content  # Returns the original PNG

def main():
    # Step 1: Fetch the encrypted PNG
    encrypted = get_ciphertext_png()
    print("[+] Downloaded encrypted PNG ({} bytes)".format(len(encrypted)))

    # Step 2: Send it back to the same endpoint to decrypt
    original_png = recover_plaintext(encrypted)
    print("[+] Recovered decrypted PNG ({} bytes)".format(len(original_png)))

    # Step 3: Save to file
    with open("flag.png", "wb") as f:
        f.write(original_png)
    print("[+] Saved the flag image to flag.png")

if __name__ == "__main__":
    main()

# 
