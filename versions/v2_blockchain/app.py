import os
import logging
from digital_signature import load_or_create_keys, print_keys
import threading
import random
import ledger

from threading import Event

block_timer_event = Event()


PORT = int(os.getenv("PORT", 5000))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_block_timer():
    while True:
        interval = random.randint(50, 70)
        logger.info(f"[{os.getenv('MY_ID')}] Esperant {interval} segons abans de crear bloc...")
        block_timer_event.clear()
        interrupted = block_timer_event.wait(timeout=interval)

        if interrupted:
            logger.info(f"[{os.getenv('MY_ID')}] Temporitzador reiniciat")
            continue  # Reset timer

        logger.info(f"[{os.getenv('MY_ID')}] Temps esgotat: creant bloc")
        ledger.create_block()


if __name__ == "__main__":
    # Claus digitals
    PRIVATE_KEY, PUBLIC_KEY = load_or_create_keys()
    logger.info("Claus digitals carregades o creades correctament.")
    logger.info(f"Clau pública: {print_keys(PUBLIC_KEY)[:30]}...")

    # Arrenca el servidor
    logger.info(f"🚀 Arrencant node al port {PORT}")
    threading.Thread(target=start_block_timer, daemon=True).start()
    from network import app
    app.run(host="0.0.0.0", port=PORT)