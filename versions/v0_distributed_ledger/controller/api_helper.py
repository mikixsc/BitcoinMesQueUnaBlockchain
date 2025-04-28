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

def create_transaction(sender, receiver, amount):
    payload = {
        "sender": sender,
        "receiver": receiver,
        "amount": amount
    }
    try:
        response = requests.post(f"{nodes_outside[sender]}/create_transaction", json=payload)
        print(f"Resposta de /create_transaction: {response.json()}")
    except Exception as e:
        print(f"Error enviant /create_transaction: {e}")