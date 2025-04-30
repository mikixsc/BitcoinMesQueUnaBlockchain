
import ledger
from datetime import datetime

from digital_signature import PUBLIC_KEY


def create_proto_transaction(sender, receiver, amount):
    return {
        "index": ledger.get_last_transaction_index() + 1,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sender": sender,
        "receiver": receiver,
        "amount": amount
    }

def create_transaction(proto_tx, signature):
    """Crea la transacció final afegint la signatura i la clau pública."""
    transaction = proto_tx.copy()
    transaction["signature"] = signature
    transaction["public_key"] = PUBLIC_KEY.to_string().hex()
    return transaction

def get_proto_transaction(tx):
    """Recupera la transacció provisional a partir d'una transacció signada."""
    proto_tx = {
        "index": tx["index"],
        "timestamp": tx["timestamp"],
        "sender": tx["sender"],
        "receiver": tx["receiver"],
        "amount": tx["amount"]
    }
    return proto_tx