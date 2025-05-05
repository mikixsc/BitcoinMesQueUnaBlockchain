import json
import logging
import os
import digital_signature
import utils
from datetime import datetime
import hashlib
from network import announce_block

LEDGER_FILE = "data/ledger.json"
UTXO_FILE = "data/utxos.json"
MEMPOOL_FILE = "data/mempool.json"

MAX_MEMPOOL = 5


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
        
def save_mempool(transactions):
    with open(MEMPOOL_FILE, "w") as f:
        json.dump(transactions, f, indent=4)

        
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

def get_transaction(txid):
    mempool = load_mempool()
    for tx in mempool:
        if tx["txid"] == txid:
            return tx
    
    return None

def get_block(hash):
    blockchain = load_ledger() 
    for block in blockchain:
        if block["hash"] == hash:
            return block
    return None


def get_prev_hash():
    ledger = load_ledger()
    if not ledger:
        return "0" * 64  # Genesis block case
    return ledger[-1]["hash"]


def create_block():
    transactions = load_mempool()

    block = {
        "index": get_last_index()+1,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "prev_hash": get_prev_hash(),
        "transactions": transactions
    }
    # fer el hash del bloc
    block_serialized = json.dumps(block, sort_keys=True).encode()
    block_hash = hashlib.sha256(block_serialized).hexdigest()
    block["hash"] = block_hash

    add_block(block)

    logger.info(f"Bloc creat amb hash {block_hash} i {len(transactions)} transaccions.")


def validate_block(block):


def add_block(block):
    # Guardar-lo al ledger
    ledger = load_ledger()
    ledger.append(block)
    save_ledger(ledger)

    # Netejar la mempool
    save_mempool([])

    # Actualitzar els saldos definitius
    save_balances(temp_balances)

def process_block(block):

    hash = block["hash"]
    prev = block["prev_hash"]
    index = block["index"]

    # Es un bloc que ja tinc --> comprovar que es el mateix index (te sentit aixo de comprovar lindex?)
    if(already_have_it("block", hash)):
        logger.info(f"Ja tinc el bloc")
        return
    
    # Es un bloc que no tinc
    
    # bloc amb index més petit o igual 
    if(index <= get_last_index()):
        logger.info(f"Es un bloc anterior")
        return

    # Es el seguent bloc 
    if(get_prev_hash() == prev):
        # cal que miri l'index que també sigui igual a l'ultim?
        if(validate_block(block)):
            add_block(block)

    # Es un bloc més alt, pero no es el seguent
    # Entenc que he de mirar quin es l'ultim block en el que estem d'acord, validar la part nova i si es valida afegirla, sino quedarme amb el que tinc
    


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
    
    if(already_have_it("tx", tx["txid"])):
        logger.error(f"\n\nTransacció FALLIDA: ja la tenia")
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
    transactions.append(tx)
    save_mempool(transactions)

    if(len(transactions) >= MAX_MEMPOOL):
        create_block()
        announce_block(get_prev_hash())

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

def get_last_index():
    blockchain = load_ledger()
    if not blockchain:
        return 0
    return blockchain[-1]["index"]


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