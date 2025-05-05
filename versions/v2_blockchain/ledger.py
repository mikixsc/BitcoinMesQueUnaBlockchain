import json
import logging
import os
import digital_signature
import utils

LEDGER_FILE = "data/ledger.json"
UTXO_FILE = "data/utxos.json"
MEMPOOL_FILE = "data/mempool.json"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
)
logger = logging.getLogger(__name__)

def load_mempool():
    if not os.path.exists(MEMPOOL_FILE):
        return []
    
    with open(MEMPOOL_FILE, "r") as f:
        try:
            return json.load(f)
        
        except json.JSONDecodeError:
            return []

def load_balances():
    if not os.path.exists(UTXO_FILE):
        return {}
    
    with open(UTXO_FILE, "r") as f:
        try:
            return json.load(f)
        
        except json.JSONDecodeError:
            return {}
        
temp_balances = load_balances()

def load_ledger():
    if not os.path.exists(LEDGER_FILE):
        return []
    
    with open(LEDGER_FILE, "r") as f:
        try:
            return json.load(f)
        
        except json.JSONDecodeError:
            return []
        
def save_ledger(transactions):
    with open(LEDGER_FILE, "w") as f:
        json.dump(transactions, f, indent=4)


def save_balances(balances):
    with open(UTXO_FILE, "w") as f:
        json.dump(balances, f, indent=2)


def update_balance(utxo, new_balance):
    balances = load_balances()
    balances[utxo] = new_balance
    save_balances(balances)

def get_balance(utxo):
    balances = load_balances()
    return balances.get(utxo, 0)

def update_balance(utxo, new_balance):
    balances = load_balances()
    balances[utxo] = new_balance
    save_balances(balances)


def process_transaction(tx):
    sender = tx["sender"]
    receiver = tx["receiver"]
    amount = tx["amount"]
    pk = tx["public_key"]

    if(pk != sender):
        logger.error(f"\n\nTransacció FALLIDA: la clau pública no coincideix amb el sender ({pk} != {sender})")
        return False

    # Agafar el saldo temporal
    balance = temp_balances.get(sender, 0)
    # Verificar que el sender existeix i té saldo suficient
    if balance < amount:
        logger.error(f"\n\nTransacció FALLIDA: saldo insuficient per {sender} (saldo: {balance}, amount: {amount})")
        return False

    # Mirar que l'hagi fet el propietari de la clau privada
    proto_tx = utils.get_proto_transaction(tx)
    proto_tx_str = json.dumps(proto_tx, sort_keys=True)
    message_hash = digital_signature.hash_message(proto_tx_str)
    if(not digital_signature.verify_signature(pk, tx["signature"], message_hash)):
        logger.error(f"\n\nTransacció FALLIDA: la firma no es vàlida")
        return False

    # Actualitzar els saldos temporals
    temp_balances[sender] = balance - amount
    temp_balances[sender] = temp_balances.get(receiver, 0) + amount

    # Posar-ho a la mempool
    transactions = load_mempool()
    if(already_have_it("tx", tx["txid"])):
        logger.error(f"\n\nTransacció FALLIDA: ja la tenia")
        return False
    transactions.append(tx)
    save_ledger(transactions)

    logger.info(f"\n\nTransacció OK: {sender} -> {receiver} ({amount}) | Ledger height: {len(transactions)}")
    return True

def process_transactions(tx_list):
    # Haurian de estar ordenades per index.
    last_index = get_last_transaction_index()
    for tx in tx_list:
        if tx["index"] != last_index + 1:
            break

        # Es la seguent que toca
        result = process_transaction(tx)
        
        if not(result):
            # No ha sigut valida
            break
        last_index = tx["index"]

def get_last_transaction_index():
    transactions = load_ledger()
    if not transactions:
        return 0
    last_index = max(tx["index"] for tx in transactions)
    return last_index

def get_transactions_by_indexes(indexes):
    transactions = load_ledger()  # Funció que carrega ledger.json
    found = [tx for tx in transactions if tx["index"] in indexes]
    return found

def get_missing_transactions(indexes_other_node):
    last_index = get_last_transaction_index()
    last_index_other = max(indexes_other_node) if indexes_other_node else 0
    if last_index==0 and last_index_other!=0:
        return list(range(1, last_index_other + 1))
    elif last_index_other>last_index:
        return list(range(last_index + 1, last_index_other + 1))
    else:
        return []
    

def already_have_it(type, hash):
    if(type == "tx"):
        data = load_mempool()
        return any(hash == tx["txid"] for tx in data)
    elif(type == "block"):
        data = load_ledger()
        return any(hash == block["hash"] for block in data)