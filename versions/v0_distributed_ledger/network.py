from flask import Flask, request, jsonify
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
    return jsonify({"message": "getdata received"}), 200

@app.route('/transactions', methods=['POST'])
def transactions():
    data = request.get_json()
    ledger.process_transactions(data)
    print(f"Rebut /transactions: {data}")
    return jsonify({"message": "transactions received"}), 200
