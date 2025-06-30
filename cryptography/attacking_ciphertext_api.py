import requests
import hashlib
from Crypto.Cipher import AES

URL = "https://aes.cryptohack.org/passwords_as_keys"

def get_ciphertext():
    response = requests.get(f"{URL}/get_flag/")

    if response.status_code != 200:
        raise Exception(f"Failed to fetch ciphertext! HTTP {response.status_code}: {response.text}")

    try:
        return bytes.fromhex(response.json()["ciphertext"])
    except Exception as e:
        print("[!] Failed to decode JSON or hex:", e)
        print("Raw response text:", response.text)
        raise


def try_password(pw, ciphertext):
    # Derive AES key from SHA-256 hash of password
    key = hashlib.sha256(pw.encode()).digest()
    # AES uses a fixed IV = 16 zero bytes in this challenge
    iv = b"\x00" * 16
    cipher = AES.new(key, AES.MODE_CBC, iv)

    try:
        pt = cipher.decrypt(ciphertext)
        # Remove PKCS#7 padding
        pad_len = pt[-1]
        if pad_len < 1 or pad_len > 16:
            return None
        if any(pt[-i] != pad_len for i in range(1, pad_len + 1)):
            return None
        return pt[:-pad_len]
    except Exception:
        return None

def main():
    ciphertext = get_ciphertext()
    print("[*] Ciphertext fetched.")

    # Replace this list with your password guesses or dictionary
    passwords = ["password", "hunter2", "letmein", "qwerty", "correcthorsebatterystaple"]

    for pw in passwords:
        pt = try_password(pw, ciphertext)
        if pt and pt.startswith(b"crypto{") and pt.endswith(b"}"):
            print(f"[+] SUCCESS: password='{pw}' -> flag = {pt.decode()}")
            break
    else:
        print("[!] No password in list succeeded. Try adding more guesses!")

if __name__ == "__main__":
    main()
