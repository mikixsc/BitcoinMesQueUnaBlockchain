import json
import logging
import os

LEDGER_FILE = "data/ledger.json"
UTXO_FILE = "data/utxos.json"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
)
logger = logging.getLogger(__name__)

def load_balances():
    if not os.path.exists(UTXO_FILE):
        return {}
    
    with open(UTXO_FILE, "r") as f:
        try:
            return json.load(f)
        
        except json.JSONDecodeError:
            return {}

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

def process_transaction(tx):
    sender = tx["sender"]
    receiver = tx["receiver"]
    amount = tx["amount"]

    balance = get_balance(sender)
    # Verificar que el sender existeix i té saldo suficient
    if balance < amount:
        logger.error(f"\n\nTransacció FALLIDA: saldo insuficient per {sender} (saldo: {balance}, amount: {amount})")
        return False

    # Actualitzar els saldos
    update_balance(sender, balance - amount)
    update_balance(receiver, get_balance(receiver) + amount)

    # Posar-ho al llibre comptable
    transactions = load_ledger()
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