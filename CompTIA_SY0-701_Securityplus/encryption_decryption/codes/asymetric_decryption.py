from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# key pair
key = RSA.generate(1024)
public_key = key.publickey()

# Encrypt with public key
cipher = PKCS1_OAEP.new(public_key)
plaintext = b"Hello Security+ RSA!"
ciphertext = cipher.encrypt(plaintext)

# Decrypt with private key
decryptor = PKCS1_OAEP.new(key)
decrypted = decryptor.decrypt(ciphertext)

print("Ciphertext:", ciphertext.hex())
print("Decrypted:", decrypted.decode())
