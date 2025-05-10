
import ledger
from datetime import datetime

import json
import hashlib

from digital_signature import load_or_create_keys, print_keys, hash_message, sign_message


def create_proto_transaction(sender, receiver, amount):
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sender": sender,
        "receiver": receiver,
        "amount": amount
    }

def create_transaction(proto_tx, signature):
    """Crea la transacció final afegint la signatura i la clau pública."""
    transaction = proto_tx.copy()
    transaction["signature"] = signature
    _, PUBLIC_KEY = load_or_create_keys()
    transaction["public_key"] = print_keys(PUBLIC_KEY)
    return transaction

def create_new_transaction(sender, receiver, amount):
    proto_tx = create_proto_transaction(sender, receiver, amount)
    proto_tx_str = json.dumps(proto_tx, sort_keys=True)
    proto_tx_hash = hash_message(proto_tx_str)

    signature = sign_message(proto_tx_hash)

    tx = create_transaction(proto_tx, signature)

    canonical = json.dumps(tx, sort_keys=True, separators=(',', ':')).encode()
    tx["txid"] = hashlib.sha256(canonical).hexdigest()

    return tx

def create_malicious_transaction(proto_tx, signature, public_key):
    """Crea la transacció final afegint la signatura i la clau pública."""
    transaction = proto_tx.copy()
    transaction["signature"] = signature
    transaction["public_key"] = public_key
    return transaction

def get_proto_transaction(tx):
    """Recupera la transacció provisional a partir d'una transacció signada."""
    proto_tx = {
        "timestamp": tx["timestamp"],
        "sender": tx["sender"],
        "receiver": tx["receiver"],
        "amount": tx["amount"]
    }
    return proto_tx

def hash_block(block):
    block_serialized = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_serialized).hexdigest()