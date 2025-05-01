"""
Codi extret de https://github.com/SalvaZaraes/bitcoin-digital-signatures-article/blob/main/ecdsa-steps-hex.py
s'han aplicat certes modificacions de l'original
"""

import hashlib
import secrets
from ecdsa import SECP256k1, SigningKey, VerifyingKey, BadSignatureError
from ecdsa.ellipticcurve import Point
from ecdsa.util import sigencode_der, sigdecode_der

def generate_keys():
    """Generates a private and public key pair."""
    # Generate a random 256-bit integer as a private key
    private_key = secrets.randbits(256)
    sk = SigningKey.from_string(private_key.to_bytes(32, byteorder="big"), curve=SECP256k1)
    sk_int = int.from_bytes(sk.to_string(), byteorder="big")

    # Calculate the public key using the private key
    generator_point = Point(SECP256k1.curve, SECP256k1.generator.x(), SECP256k1.generator.y(), SECP256k1.order)
    pk = generator_point * sk_int
    public_key = VerifyingKey.from_public_point(pk, curve=SECP256k1)

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