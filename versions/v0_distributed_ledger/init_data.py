import os
import json

# Configuració
DATA_DIR = "data"
NODES = ["node1", "node2", "node3"]
UTXO_CONTENT = {
    "A": 10,
    "B": 10,
    "C": 10
}
LEDGER_CONTENT = []

def create_node_data(node_name):
    node_path = os.path.join(DATA_DIR, node_name)
    os.makedirs(node_path, exist_ok=True)
    
    utxos_path = os.path.join(node_path, "utxos.json")
    ledger_path = os.path.join(node_path, "ledger.json")
    
    with open(utxos_path, "w") as f:
        json.dump(UTXO_CONTENT, f, indent=2)
        
    with open(ledger_path, "w") as f:
        json.dump(LEDGER_CONTENT, f, indent=2)

    print(f"[OK] Creats fitxers per {node_name}")

def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    for node in NODES:
        create_node_data(node)

    print("\nTot preparat! Ara pots fer 'docker-compose up --build'.")

if __name__ == "__main__":
    main()
