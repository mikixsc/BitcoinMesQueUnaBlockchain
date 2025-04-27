import json
import os

LEDGER_FILE = "../ledger.json"
UTXO_FILE = "../utxos.json"

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
    if balance >= amount:
        # Actualitzar els saldos
        update_balance(sender, balance - amount)
        update_balance(receiver, get_balance(receiver) + amount)

        # Posar-ho al llibre comptable
        transactions = load_ledger()
        load_ledger.append(tx)
        save_ledger(transactions)

        print(f"Transacció OK: {sender} -> {receiver} ({amount})")
        return True
    else:
        print(f"Transacció FALLIDA: saldo insuficient per {sender}")
        return False

def process_transactions(tx_list):
    # Haurian de estar ordenades per index.
    last_index = get_last_transaction_index()
    for tx in tx_list:
        if tx["index"] == last_index + 1:
            # Es la seguent que toca
            result = process_transaction(tx)
            if not(result):
                # No ha sigut valida
                break
            last_index = tx["index"]
        else :
            break

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
        return [1..last_index_other]
    elif last_index_other>last_index:
        return [last_index+1..last_index_other]
    else:
        return []