from flask import Flask, request, jsonify
import requests
from core import ledger
from datetime import datetime

app = Flask(__name__)

MY_NODE_ADDRESS = "http://localhost:5000"
MY_ID = "A"  # Identificador del node

known_nodes = [
    "http://localhost:5001",
    "http://localhost:5002"
]

@app.route('/version', methods=['POST'])
def version():
    data = request.get_json()
    print(f"Rebut /version: {data}")
    sender_address = data.get("node_address")
    if sender_address:
        try:
            print(f"Enviant /verack a {sender_address}")
            requests.post(f"{sender_address}/verack")
        except Exception as e:
            print(f"Error enviant /verack: {e}")
    
    return jsonify({"message": "version received"}), 200


@app.route('/verack', methods=['POST'])
def verack():
    print(f"Rebut /verack")
    data = request.get_json()
    sender_address = data.get("node_address")

    if sender_address not in known_nodes:
        known_nodes.append(sender_address)
        print(f"Node afegit: {sender_address}")

    return jsonify({"message": "verack received"}), 200

# Demanar les adreces d'altres nodes
@app.route('/getaddr', methods=['POST'])
def get_addr():
    print(f"Rebut /getaddr")
    data = request.get_json()
    sender_address = data.get("node_address")

    if sender_address:
        try:
            payload = {"nodes": known_nodes}
            print(f"Enviant /addr a {sender_address}")
            requests.post(f"{sender_address}/addr", json=payload)
        except Exception as e:
            print(f"Error enviant /addr: {e}")
    
    return jsonify({"message": "getaddr received"}), 200

# Reposta amb la llista d'adreces conegudes:
@app.route('/addr', methods=['POST'])
def post_addr():
    data = request.get_json()
    new_nodes = data.get("nodes", [])
    
    # Afegir només nodes nous que no teníem
    for node in new_nodes:
        if node not in known_nodes:
            try:
                payload = {
                    "node_id": MY_ID,
                    "node_address": MY_NODE_ADDRESS,
                    "timestamp": datetime.utcnow().isoformat(),
                    "known_height": ledger.get_last_transaction_index()
                }
                requests.post(f"{node}/version", json=payload)
            except Exception as e:
                print(f"Error enviant /version a {node}: {e}")
    
    return jsonify({"message": "addr received"}), 200

@app.route('/inventory', methods=['POST'])
def inventory():
    data = request.get_json()
    print(f"Rebut /inventory: {data}")

    indexes_other_node  = data.get("indexes", [])
    node_address = data.get("node_address")

    if not indexes_other_node or not node_address:
        return jsonify({"error": "No indexes or node_address provided"}), 400
    
    missing_indexes = ledger.get_missing_transactions(indexes_other_node)

    if missing_indexes:
        payload = {
            "indexes": missing_indexes,
            "node_address": MY_NODE_ADDRESS
        }
        try:
            response = requests.post(f"{node_address}/getdata", json=payload)
            if response.status_code == 200:
                return jsonify({"message": "Requested missing transactions"}), 200
            else:
                return jsonify({"error": "Failed to request missing transactions"}), 500
        except requests.exceptions.RequestException as e:
            print(f"Error demanant transaccions: {e}")
            return jsonify({"error": "Connection error"}), 500
    else:
        return jsonify({"message": "No missing transactions"}), 200

@app.route('/getdata', methods=['POST'])
def getdata():
    data = request.get_json()
    print(f"Rebut /getdata: {data}")

    indexes = data.get("indexes", [])
    node_address = data.get("node_address") 

    if not indexes:
        return jsonify({"error": "No indexes provided"}), 400

    transactions_to_send = ledger.get_transactions_by_indexes(indexes)

    if transactions_to_send:
        url = f"{node_address}/transactions"
        try:
            response = requests.post(url, json=transactions_to_send)
            if response.status_code == 200:
                return jsonify({"message": "Transactions sent"}), 200
            else:
                return jsonify({"error": f"Failed to send transactions. Status code: {response.status_code}"}), 500
        except requests.exceptions.RequestException as e:
            print(f"Error enviant transactions: {e}")
            return jsonify({"error": "Connection error"}), 500
    else:
        return jsonify({"message": "No transactions found for given indexes"}), 404

@app.route('/transactions', methods=['POST'])
def transactions():
    data = request.get_json()
    ledger.process_transactions(data)
    print(f"Rebut /transactions: {data}")
    return jsonify({"message": "transactions received"}), 200
