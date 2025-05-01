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
    "A": "152207509238b8d5c0a92d4dab98148cefdb12e91009c6e9a1d95ce251477414dc9bd1436f227f99464d43e89c2eaf7dd093e0bc6f147ca1627d62a90f165dce",
    "B": "0679cab3b1b52b28c0c35c75e6c45d06529a2c8e9eee9d734b119601c34526384fd6e34e036a2fe4cdac641182719345721ed9b5b47dd4b35e39e7d2230bc86e",
    "C": "f21f5199cc89b0e0a44bf2de088ce3f036b27a854dab4a0814976deb40966523039d7de1ccb5f6edc991edab29ba1e8799327633559aab87ff13907074468ca1"
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