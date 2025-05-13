import os
import logging
from digital_signature import load_or_create_keys, print_keys
import threading
import random
import time
from  ledger import try_block

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("PORT", 5000))


def minar():
    logger.info(f"Mineria iniciada")
    while True:
        nonce = random.randint(0, 2**32 - 1)
        try_block(nonce)
        time.sleep(0.1) 

if __name__ == "__main__":
    # Claus digitals
    PRIVATE_KEY, PUBLIC_KEY = load_or_create_keys()
    logger.info("Claus digitals carregades o creades correctament.")
    logger.info(f"Clau pública: {print_keys(PUBLIC_KEY)}\n")

    # Inicia el procés de mineria en un thread separat
    threading.Thread(target=minar, daemon=True).start()

    # Arrenca el servidor
    logger.info(f"🚀 Arrencant node al port {PORT}")
    from network import app
    app.run(host="0.0.0.0", port=PORT)