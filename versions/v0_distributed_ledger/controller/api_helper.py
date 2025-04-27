import requests
from datetime import datetime

nodes = {
    "A": "http://localhost:5000",
    "B": "http://localhost:5001",
    "C": "http://localhost:5002"
}

def send_version(from_node_id, to_node_id, known_height=0):
    payload = {
        "node_id": from_node_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "known_height": known_height,
        "node_address": nodes[from_node_id],
    }
    try:
        response = requests.post(f"{nodes[to_node_id]}/version", json=payload)
        print(f"Resposta de /version: {response.json()}")
    except Exception as e:
        print(f"Error enviant /version: {e}")
