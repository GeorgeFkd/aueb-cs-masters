import requests
import string

BASE = 'https://aes.cryptohack.org/ecb_oracle'

def encrypt(data: bytes) -> bytes:
    """Send hex data to the oracle and get back ciphertext."""
    r = requests.get(f"{BASE}/encrypt/{data.hex()}/")
    return bytes.fromhex(r.json()['ciphertext'])

def recover_flag():
    # Define the character set we expect in flags
    charset = string.ascii_lowercase + string.digits + '_{}'
    recovered = b''

    # Keep going until the flag ends with '}'
    while not recovered.endswith(b'}'):
        block_size = 16
        # Figure out which block the next unknown byte falls into
        pad_len = (block_size - (len(recovered) + 1) % block_size)
        prefix = b'A' * pad_len
        target_cipher = encrypt(prefix)

        # We only need the block containing the next byte
        block_index = (len(prefix) + len(recovered)) // block_size
        target_block = target_cipher[block_index*block_size:(block_index+1)*block_size]

        # Try each candidate character
        found = False
        for ch in charset:
            attempt = prefix + recovered + ch.encode()
            attempt_cipher = encrypt(attempt)
            guess_block = attempt_cipher[block_index*block_size:(block_index+1)*block_size]
            if guess_block == target_block:
                recovered += ch.encode()
                print("Found so far:", recovered.decode())
                found = True
                break
        if not found:
            raise Exception("No matching byte found—attack failed")

    return recovered.decode()

if __name__ == "__main__":
    flag = recover_flag()
    print("=> FLAG:", flag)

# crypto{p3n6u1n5_h473_3cb}
