import json
from datetime import datetime

class Transaction:
    def __init__(self, index, sender, receiver, amount, timestamp=None):
        self.index = index
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = timestamp or datetime.utcnow().isoformat()

    def to_dict(self):
        tx = {
            "index": self.index,
            "timestamp": self.timestamp,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount
        }
        return tx
    
    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            index=data["index"],
            sender=data["sender"],
            receiver=data["receiver"],
            amount=data["amount"],
            timestamp=data.get("timestamp"),
        )