import requests
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES

URL = "https://aes.cryptohack.org/ecbcbcwtf"

def encrypt_cbc(plaintext: bytes) -> bytes:
    response = requests.get(f"{URL}/encrypt/{plaintext.hex()}/")
    return bytes.fromhex(response.json()["ciphertext"])

def decrypt_ecb(ciphertext: bytes) -> bytes:
    response = requests.get(f"{URL}/decrypt/{ciphertext.hex()}/")
    return bytes.fromhex(response.json()["plaintext"])

def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    BLOCK_SIZE = 16

    # Step 1: Build CBC plaintext: 2 blocks of null bytes
    pt = pad(b"\x00" * 32, BLOCK_SIZE)
    ct = encrypt_cbc(pt)

    # ct contains 2 ciphertext blocks: C1, C2
    C1, C2 = ct[:16], ct[16:32]

    # Step 2: Send (C1 || C1) to ECB decryption oracle
    payload = C1 + C1
    decrypted = decrypt_ecb(payload)

    # ECB decrypt gives: D1 || D2
    D1, D2 = decrypted[:16], decrypted[16:32]

    # Step 3: Key = D1 ⊕ D2
    key = xor(D1, D2)
    print(f"[+] Recovered key (IV): {key.hex()}")

    # Step 4: Get encrypted flag
    response = requests.get(f"{URL}/get_flag/")
    ct_flag = bytes.fromhex(response.json()["ciphertext"])
    C1_flag, C2_flag = ct_flag[:16], ct_flag[16:32]

    # Step 5: Decrypt CBC manually using the key = IV
    cipher = AES.new(key, AES.MODE_ECB)
    P2 = xor(cipher.decrypt(C2_flag), C1_flag)
    P1 = xor(cipher.decrypt(C1_flag), key)
    flag = (P1 + P2).rstrip(b"\x00")
    print(f"[+] Flag: {flag.decode()}")

if __name__ == "__main__":
    main()
