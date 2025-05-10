import os
import json
from ecdsa import VerifyingKey
from digital_signature import print_keys

# Configuració
DATA_DIR = "data"
NODES = ["node1", "node2", "node3"]
LEDGER_CONTENT = []



def get_public_key_hex(node_name):
    public_key_path = os.path.join(DATA_DIR, node_name, "keys", "public_key.pem")
    with open(public_key_path, "rb") as f:
        vk = VerifyingKey.from_pem(f.read())
        return print_keys(vk)


def build_utxos():
    utxos = {}
    for node in NODES:
        pub_key_hex = get_public_key_hex(node)
        utxos[pub_key_hex] = 10
    return utxos


def create_node_data(node_name):
    node_path = os.path.join(DATA_DIR, node_name)
    os.makedirs(node_path, exist_ok=True)
    
    utxos_path = os.path.join(node_path, "utxos.json")
    ledger_path = os.path.join(node_path, "ledger.json")
    
    with open(utxos_path, "w") as f:
        json.dump(build_utxos(), f, indent=2)
        
    with open(ledger_path, "w") as f:
        json.dump(LEDGER_CONTENT, f, indent=2)

    print(f"[OK] Creats fitxers per {node_name}")

def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    for node in NODES:
        create_node_data(node)

if __name__ == "__main__":
    main()
