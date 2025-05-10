import os
import logging
from digital_signature import load_or_create_keys, print_keys
import threading
import random
import ledger

from shared import block_timer_event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


logger.info(f"[{os.getenv('MY_ID')}] block_timer_event en app: {id(block_timer_event)}")

PORT = int(os.getenv("PORT", 5000))


if __name__ == "__main__":
    # Claus digitals
    PRIVATE_KEY, PUBLIC_KEY = load_or_create_keys()
    logger.info("Claus digitals carregades o creades correctament.")
    logger.info(f"Clau pública: {print_keys(PUBLIC_KEY)[:30]}...")

    # Arrenca el servidor
    logger.info(f"🚀 Arrencant node al port {PORT}")
    minar()
    from network import app
    app.run(host="0.0.0.0", port=PORT)