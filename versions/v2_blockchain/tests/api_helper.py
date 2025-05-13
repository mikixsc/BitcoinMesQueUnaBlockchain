import requests
from datetime import datetime

nodes_outside = {
    "A": "http://localhost:5000",
    "B": "http://localhost:5001",
    "C": "http://localhost:5002"
}

nodes_inside = {
    "A": "http://node1:5000",
    "B": "http://node2:5001",
    "C": "http://node3:5002"
}

nodes_key = {
    "A": "c42bad0eebc145bbfca7c03f40647e36803f6acdfde14b3aec12c0b264d27a9134a699e7206f7ce9af0585812245dc75b6da24b1118f04029306e32c599660e1",
    "B": "ec8e838f49796b0ca77c224826bdeb11a4b9230288fd0ce86b058763cf45c8bbb684e4295861089c384104ab32af58bec704c13630e34eab58c017baaea4434f",
    "C": "ec58f3e90461366fa00adf25edda8a384ab41242c4c20751cb9ad0032492be1dc49f7db646f522a1a24153663b4c85fca410133b47262eadb2ab18c41f5bd437"
}

def send_version(from_node_id, to_node_id, known_height=0):
    payload = {
        "node_id": from_node_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "known_height": known_height,
        "node_address": nodes_inside[from_node_id],
    }
    try:
        response = requests.post(f"{nodes_outside[to_node_id]}/version", json=payload)
        print(f"Resposta de /version: {response.json()}")
    except Exception as e:
        print(f"Error enviant /version: {e}")

def create_transaction(initial_node, sender, receiver, amount):
    payload = {
        "sender": nodes_key[sender],
        "receiver": nodes_key[receiver],
        "amount": amount
    }
    try:
        response = requests.post(f"{nodes_outside[initial_node]}/create_transaction", json=payload)
        print(f"Resposta de /create_transaction: {response.json()}")
    except Exception as e:
        print(f"Error enviant /create_transaction: {e}")

def create_malicious_transaction(initial_node, sender, receiver, amount):
    payload = {
        "sender": nodes_key[sender],
        "receiver": nodes_key[receiver],
        "amount": amount,
        "public_key": nodes_key[sender]
    }
    try:
        response = requests.post(f"{nodes_outside[initial_node]}/create_malicious_transaction", json=payload)
        print(f"Resposta de /create_transaction: {response.json()}")
    except Exception as e:
        print(f"Error enviant /create_transaction: {e}")


def remove_history(node):
    try:
        response = requests.delete(f"{nodes_outside[node]}/remove_history")
        print(f"Resposta de /remove_history: {response.json()}")
    except Exception as e:
        print(f"Error enviant /remove_history: {e}")