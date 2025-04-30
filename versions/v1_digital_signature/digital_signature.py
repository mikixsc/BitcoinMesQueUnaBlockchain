"""
Codi extret de https://github.com/SalvaZaraes/bitcoin-digital-signatures-article/blob/main/ecdsa-steps-hex.py
s'han aplicat certes modificacions de l'original
"""

import hashlib
import secrets
import ecdsa #0.18.0/0.19.0
from ecdsa.util import sigencode_der
from ecdsa import SECP256k1, ellipticcurve, VerifyingKey, BadSignatureError
from ecdsa.ellipticcurve import Point
from ecdsa.util import sigdecode_der

def generate_keys():
    """Generates a private and public key pair."""
    # Generate a random 256-bit integer as a private key
    private_key = secrets.randbits(256)
    sk = ecdsa.SigningKey.from_string(private_key.to_bytes(32, byteorder="big"), curve=SECP256k1)
    sk_int = int.from_bytes(sk.to_string(), byteorder="big")

    # Calculate the public key using the private key
    generator_point = ellipticcurve.Point(SECP256k1.curve, SECP256k1.generator.x(), SECP256k1.generator.y(), SECP256k1.order)
    pk = generator_point * sk_int
    public_key = ecdsa.VerifyingKey.from_public_point(pk, curve=SECP256k1)

    return sk, public_key

PRIVATE_KEY, PUBLIC_KEY = generate_keys()


def hash_message(message):
    """Hashes a message using double SHA-256."""
    return hashlib.sha256(hashlib.sha256(message.encode('utf-8')).digest()).digest()

def print_keys(key):
    """Changes the format of a key to print it in Hexadecimal"""
    printable_key = key.to_string().hex()
    return printable_key


def sign_message(private_key, message_hash, generator_point, random_key):
    """Signs a message."""
    R = random_key * generator_point
    r = R.x() % SECP256k1.order
    sk_int = int.from_bytes(private_key.to_string(), byteorder="big")
    message_hash_int = int.from_bytes(message_hash, byteorder="big")
    s = (pow(random_key, -1, SECP256k1.order) * (message_hash_int + sk_int * r)) % SECP256k1.order

    # DER encode the signature
    signature_bytes = sigencode_der(r, s, SECP256k1.order)
    signature_hex = signature_bytes.hex()

    return signature_hex


def verify_signature(public_key_hex, signature_hex, message_hash):
    x = int(public_key_hex[:64], 16)
    y = int(public_key_hex[64:], 16)
    curve = SECP256k1.curve
    order = SECP256k1.order
    P = Point(curve, x, y, order)
    vk = VerifyingKey.from_public_point(P, curve=SECP256k1)

    # 2) Convertir la firma a bytes
    sig_bytes = bytes.fromhex(signature_hex)

    # 3) Intentar verificar
    try:
        # verify_digest lanza BadSignatureError si falla
        vk.verify_digest(sig_bytes, message_hash, sigdecode=sigdecode_der)
        return True
    except BadSignatureError:
        return False

"""
if __name__ == "__main__":
    print("\nProcess: Generating Keys\n")
    sk, public_key, g = generate_keys()
    print(f"Keys:\nPrivateKey= {print_keys(sk)}\nPublicKey= {print_keys(public_key)}\n\n")

    print("\nProcess: Signing\n")
    message = input("Enter the message to sign: ")
    message_hash = hash_message(message)
    random_key = secrets.randbelow(SECP256k1.order)
    r, s = sign_message(sk, message_hash, g, random_key)
    print(f"\nSignature: (r= {hex(r)[2:]}, s= {hex(s)[2:]})\n\n")

    print("\nProcess: Verifying\n")
    public_key_input = input("Enter the public key: ")
    r_input = int(input("Enter the value of r: "), base=16)
    s_input = int(input("Enter the value of s: "), base=16)
    verification_message = input("Enter the message for verification: ")

    v = verify_signature(public_key_input, r_input, s_input, g, verification_message)
    print(f'\nThe value of v= {hex(v)[2:]}')

    # Print verification result
    print("\nThe signature is valid, v is equal to r. Therefore, the private key used to derive the public key is the same one that was used to sign the message." if v == r_input else "\nThe signature is not valid, v is not equal to r")
"""