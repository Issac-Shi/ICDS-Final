from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

def encrypt_message(key, plaintext):
    # Ensure the plaintext is bytes, encode if it's str
    if isinstance(plaintext, str):
        plaintext = plaintext.encode()

    # Pad the plaintext to be AES block size compliant
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plaintext) + padder.finalize()

    # Create cipher object and encrypt the data
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return ciphertext

def decrypt_message(key, ciphertext):
    # Create cipher object and decrypt the data
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # Unpad the plaintext
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    # Decode to string if necessary
    try:
        return plaintext.decode()
    except UnicodeDecodeError:
        return plaintext

KEY = b'Sixteen byte key'  # Your derived encryption key, must be 16, 24, or 32 bytes

# Sample case
plaintext = "Hello, World!"
ciphertext = encrypt_message(KEY, plaintext)
decrypted = decrypt_message(KEY, ciphertext)
print(f"Plaintext: {plaintext}")
print(f"Ciphertext: {ciphertext}")
print(f"Decrypted: {decrypted}")