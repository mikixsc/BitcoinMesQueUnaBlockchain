from flask import Flask, request, jsonify
import requests
import logging
import ledger
import digital_signature
import utils
from datetime import datetime
import os
import json
import hashlib


TYPE_TRANSACTION = "tx"
TYPE_BLOCK = "block"

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
    
    proto_tx = utils.create_proto_transaction(data.get("sender"), data.get("receiver"), data.get("amount"))
    proto_tx_str = json.dumps(proto_tx, sort_keys=True)
    proto_tx_hash = digital_signature.hash_message(proto_tx_str)

    signature = digital_signature.sign_message(proto_tx_hash)

    tx = utils.create_transaction(proto_tx, signature)

    canonical = json.dumps(tx, sort_keys=True, separators=(',', ':')).encode()
    tx["txid"] = hashlib.sha256(canonical).hexdigest()

    if not ledger.process_transaction(tx, True, True):
        return jsonify({"error": "Transaction failed"}), 400
    
    # Transacció vàlida -> anunciem-la
    for node_address in known_nodes:
        try:
            send_inventory(node_address, TYPE_TRANSACTION, tx["txid"])
            
        except Exception as e:
            logger.error(f"[{MY_ID}] Error enviant inventory a {node_address}: {e}")

    return jsonify({"message": "Transaction created and announced"}), 201    

@app.route('/create_malicious_transaction', methods=['POST'])
def create_malicious_transaction():
    data = request.get_json()
    
    proto_tx = utils.create_proto_transaction(data.get("sender"), data.get("receiver"), data.get("amount"))
    proto_tx_str = json.dumps(proto_tx, sort_keys=True)
    proto_tx_hash = digital_signature.hash_message(proto_tx_str)

    signature = digital_signature.sign_message(proto_tx_hash)

    tx = utils.create_malicious_transaction(proto_tx, signature, data.get("public_key"))

    if not ledger.process_transaction(tx):
        return jsonify({"error": "Transaction failed"}), 400
    
    # Transacció vàlida -> anunciem-la
    payload = {
        "indexes": [ledger.get_last_index()],
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

    hash = data.get("hash")
    info_type = data.get("type")
    if(ledger.already_have_it(info_type, hash)):
        return jsonify({"message": "Already have it"}), 200

    send_getdata(data.get("node_address"), info_type, hash)
    return jsonify({"message": "Asked"}), 200


@app.route('/getdata', methods=['POST'])
def getdata():
    data = request.get_json()
    logger.info(f"[{MY_ID}] Rebut /getdata: {data}")

    info_type = data.get("type")
    hash = data.get("hash")
    destination = data.get("node_address")
    if(info_type==TYPE_BLOCK):
        block = ledger.get_block(hash)
        if(block):
            if(ledger.reconstructing_blockchain()):
                return jsonify({"message": "Doing reconstruction"}), 201
            send_block(destination, block)
    elif(info_type==TYPE_TRANSACTION):
        tx = ledger.get_transaction(hash)
        if(tx):
            send_transaction(destination, tx)
    else:
        return jsonify({"error": "Error in getdata, type not known"}), 400
    
    return jsonify({"message": "Asked data"}), 200


@app.route('/transaction', methods=['POST'])
def transaction():
    data = request.get_json()
    logger.info(f"[{MY_ID}] Rebut /transaction")
    ledger.process_transaction(data, True, True)
    return jsonify({"message": "transaction received"}), 200


@app.route('/block', methods=['POST'])
def block():
    data = request.get_json()
    logger.info(f"[{MY_ID}] Rebut /block")
    ledger.process_block(data.get("node_address"),data.get("block"))
    return jsonify({"message": "block received"}), 200


# Auxiliars

def announce_block(hash):
    for node_address in known_nodes:
        send_inventory(node_address, "block", hash)

def announce_tx(txid):
    for node_address in known_nodes:
        send_inventory(node_address, "tx", txid)

def send_inventory(destination, type, hash):
    payload = {
        "type": type,
        "hash": hash,
        "node_address": MY_NODE_ADDRESS,
        "node_id": MY_ID
    }
    try:
        logger.info(f"[{MY_ID}] Sending inventory")
        requests.post(f"{destination}/inventory", json=payload)
    except requests.exceptions.RequestException as e:
        logger.error(f"[{MY_ID}] Error sending inventory: {e}")

def send_getdata(destination, type, hash):
    payload = {
        "type": type,
        "hash": hash,
        "node_address": MY_NODE_ADDRESS,
        "node_id": MY_ID
    }
    try:
        logger.info(f"[{MY_ID}] Sending getdata")
        requests.post(f"{destination}/getdata", json=payload)
    except requests.exceptions.RequestException as e:
        logger.error(f"[{MY_ID}] Error sending getdata: {e}")


def send_transaction(destination, transaction):
    try:
        requests.post(f"{destination}/transaction", json=transaction)
    except requests.exceptions.RequestException as e:
        logger.error(f"[{MY_ID}] Error sending transaction: {e}")



def send_block(destination, block):
    payload = {
        "block": block,
        "node_address": MY_NODE_ADDRESS,
    }
    try:
        requests.post(f"{destination}/block", json=payload)
    except requests.exceptions.RequestException as e:
        logger.error(f"[{MY_ID}] Error sending block: {e}")