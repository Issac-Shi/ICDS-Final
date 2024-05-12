# Implementation of Diffie-Hellman key exchange algorithm

import cryptography.hazmat.primitives.asymmetric.x25519 as x25519

def generate_key_pair():
    # Generate a private key
    private_key = x25519.X25519PrivateKey.generate()
    # Get the public key
    public_key = private_key.public_key()
    return private_key, public_key

def generate_shared_key(private_key, public_key):
    # Generate the shared key
    shared_key = private_key.exchange(public_key)
    return shared_key

# Sample case
if __name__ == "__main__":
    private_key1, public_key1 = generate_key_pair()
    private_key2, public_key2 = generate_key_pair()
    shared_key1 = generate_shared_key(private_key1, public_key2)
    shared_key2 = generate_shared_key(private_key2, public_key1)
    print(shared_key1 == shared_key2)