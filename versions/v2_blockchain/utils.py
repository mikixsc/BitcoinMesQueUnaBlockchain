
import ledger
from datetime import datetime

import json
import hashlib

from digital_signature import load_or_create_keys, print_keys


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