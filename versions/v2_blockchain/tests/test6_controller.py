import time
from api_helper import send_version, create_transaction, remove_history


time.sleep(5)  # Esperem que els nodes estiguin a punt

# Enviar un /version de A a B
send_version("A", "B", 0)

# A i B connectats

send_version("B", "C", 0)

# B i C connectats

send_version("A", "C", 0)

transactions = [
    ("A", "A", "B", 2),
    ("B", "B", "C", 6),
    ("C", "C", "A", 4),
    ("A", "A", "C", 8),
    ("B", "B", "A", 1),
    ("C", "C", "B", 7),
    ("A", "A", "B", 3),
    ("B", "B", "C", 9),
    ("C", "C", "A", 2),
    ("A", "A", "C", 10),
    ("A", "A", "B", 2),
    ("B", "B", "C", 6),
    ("C", "C", "A", 4),
    ("A", "A", "C", 8),
    ("B", "B", "A", 1),
    ("C", "C", "B", 7),
    ("A", "A", "B", 3),
    ("B", "B", "C", 9),
    ("C", "C", "A", 2),
    ("A", "A", "C", 10),
    ("A", "A", "B", 2),
    ("B", "B", "C", 6),
    ("C", "C", "A", 4),
    ("A", "A", "C", 8),
    ("B", "B", "A", 1),
    ("C", "C", "B", 7),
    ("A", "A", "B", 3),
    ("B", "B", "C", 9),
    ("C", "C", "A", 2),
    ("A", "A", "C", 10),
]


for tx in transactions:
    sender_node, from_user, to_user, amount = tx
    create_transaction(sender_node, from_user, to_user, amount)
    time.sleep(10)

remove_history("A")