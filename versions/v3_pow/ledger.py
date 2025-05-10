import json
import logging
import os
import digital_signature
import utils
from datetime import datetime
from network import announce_block, announce_tx, send_getdata, coinbase_transaction
from init_data import build_utxos

from difficulty import should_adjust_difficulty, adjust_difficulty, get_current_target

LEDGER_FILE = "data/ledger.json"
UTXO_FILE = "data/utxos.json"
MEMPOOL_FILE = "data/mempool.json"

MAX_MEMPOOL = 5

GENESIS_BLOCK_PREV_HASH = "0" * 64

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
)
logger = logging.getLogger(__name__)

blocks_to_validate = []

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
        return GENESIS_BLOCK_PREV_HASH  # Genesis block case
    return ledger[-1]["hash"]

def try_block(nounce):
    transactions = load_mempool()
    
    coinbase = coinbase_transaction()

    transactions.append(coinbase)

    block = {
        "index": get_last_index()+1,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "prev_hash": get_prev_hash(),
        "transactions": transactions,
        "nounce": nounce
    }
    # fer el hash del bloc
    block["hash"] = utils.hash_block(block)

    if block["hash"] < get_current_target():
        add_block(block)
        announce_block(get_prev_hash())
        logger.info(f"Bloc creat amb hash {block['hash']} i {len(transactions)} transaccions.")


def create_block():
    transactions = load_mempool()

    block = {
        "index": get_last_index()+1,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "prev_hash": get_prev_hash(),
        "transactions": transactions
    }
    # fer el hash del bloc
    block["hash"] = utils.hash_block(block)

    add_block(block)
    announce_block(get_prev_hash())

    logger.info(f"Bloc creat amb hash {block['hash']} i {len(transactions)} transaccions.")


def validate_block(block, validate_index):
    global temp_balances
    # Aqui ja prev_hash es l'ultim bloc que tinc anterior
    block_copy = block.copy()
    received_hash = block_copy.pop("hash")

    # Mirar que el hash estigui per sota de l'objectiu
    if(received_hash > get_current_target()):
        logger.error("Hash del bloc no es vàlid es més gran que l'objectiu")
        return False

    #Mirar que el hash sigui el correcte
    calculated_hash = utils.hash_block(block_copy)
    if received_hash != calculated_hash:
        logger.error("Hash del bloc no coincideix")
        return False
    

    # Validar l'index
    if validate_index and block["index"] != get_last_index() + 1:
        logger.error("Index incorrecte pel bloc")
        return False

    # Fer un recorregut per les transaccions i cridant a process_transaction
    # # Només he de reutilizar si no estic reconstruint, per tant he de tenir en compte les que tinc fetes si blocs_to_validate es buit, si no no.
    
    # Restart balances
    # # Mirar que en el bloc només hi hagi com a maxim una transaccio coinbase
    temp_balances = load_balances()
    coinbase_count = 0
    for tx in block["transactions"]:
        valida, coinbase = process_transaction(tx, False, False)
        if not valida:
            logger.error("Transacció invàlida en el bloc")
            return False
        if coinbase:
            coinbase_count += 1
            if coinbase_count > 1:
                logger.error("Més d'una transacció coinbase en el bloc")
                return False
    return True



def add_block(block):
    global temp_balances
    # Guardar-lo al ledger
    ledger = load_ledger()
    ledger.append(block)
    save_ledger(ledger)

    # Actualitzar els saldos definitius
    save_balances(temp_balances)
    temp_balances = load_balances()
    
    from shared import block_timer_event
    block_timer_event.set()

    if should_adjust_difficulty(ledger):
        adjust_difficulty(ledger)

    # Netejar la mempool
    save_mempool([])
    


def reconstructing_blockchain():
    return len(blocks_to_validate)>0


def substract_tx(tx):
    sender = tx["sender"]
    receiver = tx["receiver"]
    amount = tx["amount"]

    temp_balances[sender] = temp_balances.get(sender, 0) + amount
    temp_balances[receiver] = temp_balances.get(receiver, 0) - amount


def balances_in(hash):
    global temp_balances
    temp_balances = load_balances()
    block_hash = get_prev_hash()
    while(block_hash!=hash):
        block = get_block(block_hash)
        for tx in block["transactions"]:
            substract_tx(tx)
        block_hash = block["prev_hash"]
        

def reconstruct(initial_hash):
    global temp_balances
    # He de mirar si tots els blocs que estan a blocks_to_validate son valids
    # Si ho son crear la blockchain amb tots aquests blocs afegits despres del inital hash
    # Si no deixar-ho com esta
    # fer que temp_balances es possi en l'estat en el que estavem en el bloc inital_hash
    if(initial_hash==GENESIS_BLOCK_PREV_HASH):
        # Obtenir l'init # Quan es fagui pow inicialitzar a per defecte
        temp_balances = build_utxos()
    else: 
        temp_balances = balances_in(initial_hash)

    
    for block in blocks_to_validate:
        if(not validate_block(block, False)):
            temp_balances = load_balances()
            blocks_to_validate.clear()
            return

    for block in blocks_to_validate:
        add_block(block)
        announce_block(get_prev_hash())

    blocks_to_validate.clear()


def process_block(sender, block):

    hash = block["hash"]
    prev = block["prev_hash"]
    index = block["index"]
    

    # Es el seguent bloc 
    if(get_prev_hash() == prev):
        if(reconstructing_blockchain()):
            blocks_to_validate.append(block)
            reconstruct(prev)
        else:
            if index != get_last_index() + 1:
                logger.warning("Index incorrecte pel bloc consecutiu")
                return
            if(validate_block(block, True)):
                add_block(block)
                announce_block(get_prev_hash())
    
    # bloc amb index més petit o igual 
    elif(not reconstructing_blockchain() and index <= get_last_index()):
        logger.info(f"Es un bloc anterior")
        return
    
    else:
        # Es un bloc que ja tinc
        if(already_have_it("block", hash)):
            logger.info(f"Ja tinc el bloc")
            if(reconstructing_blockchain()):
                reconstruct(hash)
            return

        # Es un bloc més alt, pero no es el seguent
        blocks_to_validate.insert(0, block)
        if(index==1 and prev==GENESIS_BLOCK_PREV_HASH):
            reconstruct(GENESIS_BLOCK_PREV_HASH)
        send_getdata(sender, "block", prev)

def process_transaction(tx, addToMempool, lookInMempool):
    sender = tx["sender"]
    receiver = tx["receiver"]
    amount = tx["amount"]
    pk = tx["public_key"]
    coinbase = False
    # Mirar si el sender es null -> tx coinbase

    
    if sender == None:
        coinbase = True

    if(not coinbase and pk != sender):
        logger.error(f"\n\nTransacció FALLIDA: la clau pública no coincideix amb el sender ({pk} != {sender})")
        return False, coinbase

    # Agafar el saldo temporal
    if not coinbase:
        balance = temp_balances.get(sender, 0)
        # Verificar que el sender existeix i té saldo suficient
        if balance < amount:
            logger.error(f"\n\nTransacció FALLIDA: saldo insuficient per {sender} (saldo: {balance}, amount: {amount})")
            return False, coinbase
    
    if(lookInMempool and already_have_it("tx", tx["txid"])):
        logger.info(f"\n\nTransacció: ja la tenia")
        return True, coinbase

    # Mirar que l'hagi fet el propietari de la clau privada
    if not coinbase:
        proto_tx = utils.get_proto_transaction(tx)
        proto_tx_str = json.dumps(proto_tx, sort_keys=True)
        message_hash = digital_signature.hash_message(proto_tx_str)
        if(not coinbase and not digital_signature.verify_signature(pk, tx["signature"], message_hash)):
            logger.error(f"\n\nTransacció FALLIDA: la firma no es vàlida")
            return False, coinbase

    # Actualitzar els saldos temporals
    if not coinbase:
        temp_balances[sender] = balance - amount
    temp_balances[receiver] = temp_balances.get(receiver, 0) + amount

    # Posar-ho a la mempool
    if(addToMempool):
        transactions = load_mempool()
        transactions.append(tx)
        save_mempool(transactions)
        announce_tx(tx["txid"])

    return True, coinbase

def get_last_index():
    blockchain = load_ledger()
    if not blockchain:
        return 0
    return blockchain[-1]["index"]
    

def already_have_it(type, hash):
    if(type == "tx"):
        data = load_mempool()
        return any(hash == tx["txid"] for tx in data)
    elif(type == "block"):
        data = load_ledger()
        return any(hash == block["hash"] for block in data)