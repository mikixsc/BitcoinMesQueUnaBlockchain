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
    "A": "d4b05f718fdee7468bd769105636b8b606ceb8d508a626d5334972d4f40b9dd47f6169b861fd6221b4f10b0171d6abd5ecce1cca51faf0808646ea14000d0425",
    "B": "1b96700904b9131d19a400d0e5b88a1832b07abd9e06632f900c127a108028fb58e440976840dcb7345039c2911856f0790db677fb1961d138fc78068da6dbac",
    "C": "3dcfe0d564bc6d72c7dbfbef3dee7c2296d14404aa458cd8810d2852d8d0bf794f85040e60868be3fe944897adf7e64d75fc4aa8c077346a950e47c091b5414f"
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