# COURSE="CRYPTO ON THE WEB"
# def print_flag_for(course,challenge,flag):
#     print("In course: ",course," Challenge:",challenge," Result: ",flag)
# import jwt
# import requests
# import json 
# import base64
# token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmbGFnIjoiY3J5cHRve2p3dF9jb250ZW50c19jYW5fYmVfZWFzaWx5X3ZpZXdlZH0iLCJ1c2VyIjoiQ3J5cHRvIE1jSGFjayIsImV4cCI6MjAwNTAzMzQ5M30.shKSmZfgGVvd2OSB2CGezzJ3N6WAULo3w9zCl_T47KQ"
#
# # Decode without verifying signature (useful for challenges)
# payload = jwt.decode(token, options={"verify_signature": False})
#
# print("Decoded payload:", payload)
# flag = payload.get("flag")
# print_flag_for(COURSE,"Token Appreciation",flag)
#
#
# BASE_URL = "https://web.cryptohack.org/jwt-secrets"
# SECRET_KEY = "secret"  # guessed or known secret key
#
# def get_token(username):
#     resp = requests.get(f"{BASE_URL}/create_session/{username}/")
#     return resp.json()["session"]
#
# def decode_payload(token):
#     payload_b64 = token.split('.')[1]
#     padding = '=' * (-len(payload_b64) % 4)
#     decoded_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
#     return json.loads(decoded_bytes)
#
# def forge_admin_token(payload):
#     payload['admin'] = True
#     return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
#
# def check_admin(token):
#     resp = requests.get(f"{BASE_URL}/authorise/{token}/")
#     return resp.json()
#
# # Usage
# username = "attacker"
#
# token = get_token(username)
# print("Original token:", token)
#
# payload = decode_payload(token)
# print("Original payload:", payload)
#
# forged_token = forge_admin_token(payload)
# print("Forged admin token:", forged_token)
#
# response = check_admin(forged_token)
# print("Server response:", response)

print(pow(101,17) % 22663)

# Given values
p = 17
q = 23
e = 65537
m = 12

# Compute modulus
N = p * q

# RSA encryption: ciphertext = m^e mod N
ciphertext = pow(m, e, N)

print(ciphertext)

p = 857504083339712752489993810777
q = 1029224947942998075080348647219

phi = (p - 1) * (q - 1)
print(phi)

from Crypto.Util.number import inverse,long_to_bytes

p = 857504083339712752489993810777
q = 1029224947942998075080348647219
e = 65537

phi = (p - 1) * (q - 1)

d = inverse(e, phi)
print(d)



N = 882564595536224140639625987659416029426239230804614613279163
d = 121832886702415731577073962957377780195510499965398469843281  # private key from previous step
c = 77578995801157823671636298847186723593814843845525223303932

m = pow(c, d, N)
plaintext_bytes = long_to_bytes(m)

print(plaintext_bytes.decode('ascii'))

