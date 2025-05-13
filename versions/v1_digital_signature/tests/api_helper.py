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
    "A": "4914968b82a328b1b5337239653df1fd3afcc7e5a82d22d247f1f3169d92e9474088e09cc55b7841543ea4694f764cc6dfd04c88cdcade6f30826423a12b91dd",
    "B": "366541f8af34fe12e67e4da8d21ae7157160b40696e1ba21e9ec821d516a0ad75551d5a85db17c2720e9469227ca2fbec758b73671fc5d04d9764f5a28857706",
    "C": "b81f731e80bd2959f45f65f9e9c3562881be9f8d21ac61801993f7ab46ee877ce678d8c38189636100187de03e4c317a3e7f6419162268c495059b6307b41464"
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