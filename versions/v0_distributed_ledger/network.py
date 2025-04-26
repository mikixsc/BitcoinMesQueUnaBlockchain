from flask import Flask, request, jsonify
import requests
from core import ledger

app = Flask(__name__)

@app.route('/version', methods=['POST'])
def version():
    data = request.get_json()
    print(f"Rebut /version: {data}")
    return jsonify({"message": "version received"}), 200

@app.route('/verack', methods=['POST'])
def verack():
    print(f"Rebut /verack")
    return jsonify({"message": "verack received"}), 200

@app.route('/addr', methods=['GET'])
def get_addr():
    # De moment tornem una resposta dummy
    nodes = ["http://localhost:5001", "http://localhost:5002"]
    return jsonify({"nodes": nodes}), 200

@app.route('/addr', methods=['POST'])
def post_addr():
    data = request.get_json()
    print(f"Rebut /addr: {data}")
    return jsonify({"message": "addr received"}), 200

@app.route('/inventory', methods=['POST'])
def inventory():
    data = request.get_json()
    print(f"Rebut /inventory: {data}")
    return jsonify({"message": "inventory received"}), 200

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
