from flask import Flask, request, jsonify
import requests
import logging
from core import ledger
from datetime import datetime
import os

# Configuració del logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

PORT = int(os.getenv("PORT", 5000))
MY_NODE_ADDRESS = "http://" + os.getenv("MY_HOSTNAME", "localhost") + ":" + str(PORT)
MY_ID = os.getenv("MY_ID", "A")  # Identificador del node

known_nodes = []



# ENDPOINTS per controlar el node

@app.route('/ledger', methods=['GET'])
def get_ledger():
    try:
        current_ledger = ledger.load_ledger()
        logger.info(f"[{MY_ID}] Ledger demanat, {len(current_ledger)} transaccions retornades.")
        return jsonify(current_ledger), 200
    
    except Exception as e:
        logger.error(f"[{MY_ID}] Error carregant el ledger: {e}")
        return jsonify({"error": "No s'ha pogut carregar el ledger."}), 500

@app.route('/create_transaction', methods=['POST'])
def create_transaction():
    data = request.get_json()

    tx = {
        "index": ledger.get_last_transaction_index() + 1,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sender": data.get("sender"),
        "receiver": data.get("receiver"),
        "amount": data.get("amount")
    }
    
    if not ledger.process_transaction(tx):
        return jsonify({"error": "Transaction failed: insufficient balance"}), 400
    
    # Transacció vàlida -> anunciem-la
    payload = {
        "indexes": [ledger.get_last_transaction_index()],
        "node_address": MY_NODE_ADDRESS,
        "node_id": MY_ID,
    }
    for node_address in known_nodes:
        try:
            logger.info("\n" + "="*33)
            logger.info(f"[{MY_ID}] Inventory enviat a {node_address}")
            requests.post(f"{node_address}/inventory", json=payload)
            
        except Exception as e:
            logger.error(f"[{MY_ID}] Error enviant inventory a {node_address}: {e}")

    return jsonify({"message": "Transaction created and announced"}), 201    




# ENDPOINTS per la comunicació entre nodes

@app.route('/version', methods=['POST'])
def version():
    data = request.get_json()
    logger.info(f"[{MY_ID}] Rebut /version: {data}")
    sender_address = data.get("node_address")
    
    if sender_address:
        try:
            if sender_address not in known_nodes:
                known_nodes.append(sender_address)
                logger.info(f"[{MY_ID}] Node afegit a known_nodes: {sender_address}")
            logger.info(f"[{MY_ID}] Enviant /verack a {sender_address}")
            payload = {
                "node_id": MY_ID,
                "node_address": MY_NODE_ADDRESS,
            }
            requests.post(f"{sender_address}/verack", json=payload)
        
        except Exception as e:
            logger.error(f"[{MY_ID}] Error enviant /verack: {e}")
    
    return jsonify({"message": "version received"}), 200

@app.route('/verack', methods=['POST'])
def verack():
    logger.info(f"[{MY_ID}] Rebut /verack")
    data = request.get_json()
    sender_address = data.get("node_address")

    if sender_address and sender_address not in known_nodes:
        known_nodes.append(sender_address)
        logger.info(f"[{MY_ID}] Node afegit a known_nodes: {sender_address}")

    return jsonify({"message": "verack received"}), 200

@app.route('/getaddr', methods=['POST'])
def get_addr():
    logger.info(f"[{MY_ID}] Rebut /getaddr")
    data = request.get_json()
    sender_address = data.get("node_address")

    if sender_address:
        try:
            payload = {"nodes": known_nodes}
            logger.info(f"[{MY_ID}] Enviant /addr a {sender_address} amb nodes: {known_nodes}")
            requests.post(f"{sender_address}/addr", json=payload)
        
        except Exception as e:
            logger.error(f"[{MY_ID}] Error enviant /addr: {e}")
    
    return jsonify({"message": "getaddr received"}), 200

@app.route('/addr', methods=['POST'])
def post_addr():
    data = request.get_json()
    new_nodes = data.get("nodes", [])
    logger.info(f"[{MY_ID}] Rebut /addr amb nous nodes: {new_nodes}")
    
    for node in new_nodes:
        if node not in known_nodes:
            try:
                payload = {
                    "node_id": MY_ID,
                    "node_address": MY_NODE_ADDRESS,
                    "timestamp": datetime.utcnow().isoformat(),
                    "known_height": ledger.get_last_transaction_index()
                }
                logger.info(f"[{MY_ID}] Enviant /version a nou node {node}")
                requests.post(f"{node}/version", json=payload)
            
            except Exception as e:
                logger.error(f"[{MY_ID}] Error enviant /version a {node}: {e}")
    
    return jsonify({"message": "addr received"}), 200

@app.route('/inventory', methods=['POST'])
def inventory():
    data = request.get_json()
    logger.info(f"[{MY_ID}] Rebut /inventory: {data}")

    indexes_other_node = data.get("indexes", [])
    node_address = data.get("node_address")

    if not indexes_other_node or not node_address:
        return jsonify({"error": "No indexes or node_address provided"}), 400
    
    missing_indexes = ledger.get_missing_transactions(indexes_other_node)
    logger.info(f"[{MY_ID}] Missing transactions: {missing_indexes}")

    if not missing_indexes:
        return jsonify({"message": "No missing transactions"}), 200
    
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
        logger.error(f"[{MY_ID}] Error demanant transaccions: {e}")
        return jsonify({"error": "Connection error"}), 500


@app.route('/getdata', methods=['POST'])
def getdata():
    data = request.get_json()
    logger.info(f"[{MY_ID}] Rebut /getdata: {data}")

    indexes = data.get("indexes", [])
    node_address = data.get("node_address")

    if not indexes:
        return jsonify({"error": "No indexes provided"}), 400

    transactions_to_send = ledger.get_transactions_by_indexes(indexes)
    logger.info(f"[{MY_ID}] Transactions a enviar: {transactions_to_send}")

    if not transactions_to_send:
        return jsonify({"message": "No transactions found for given indexes"}), 404

    url = f"{node_address}/transactions"
    try:
        response = requests.post(url, json=transactions_to_send)
        if response.status_code == 200:
            return jsonify({"message": "Transactions sent"}), 200
        else:
            return jsonify({"error": f"Failed to send transactions. Status code: {response.status_code}"}), 500
    
    except requests.exceptions.RequestException as e:
        logger.error(f"[{MY_ID}] Error enviant transactions: {e}")
        return jsonify({"error": "Connection error"}), 500


@app.route('/transactions', methods=['POST'])
def transactions():
    data = request.get_json()
    logger.info(f"[{MY_ID}] Rebut /transactions: {data}")
    ledger.process_transactions(data)
    return jsonify({"message": "transactions received"}), 200