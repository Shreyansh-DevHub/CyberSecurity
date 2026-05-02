from cryptography.fernet import Fernet

# Generate a key
key = Fernet.generate_key() 
cipher = Fernet(key)

plaintext = b"This is a secret message."
cipher_text = cipher.encrypt(plaintext)

#decrypting the cipher text
decrypted = cipher.decrypt(cipher_text)

print("key", key)
print("cipher text", cipher_text.decode())
print("decrypted text", decrypted.decode())
