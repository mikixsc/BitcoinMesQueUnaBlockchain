import os
import logging
from network import app
from digital_signature import load_or_create_keys, print_keys

PORT = int(os.getenv("PORT", 5000))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Claus digitals
    PRIVATE_KEY, PUBLIC_KEY = load_or_create_keys()
    logger.info("Claus digitals carregades o creades correctament.")
    logger.info(f"Clau pública: {print_keys(PUBLIC_KEY)}\n")

    # Arrenca el servidor
    logger.info(f"🚀 Arrencant node al port {PORT}")
    app.run(host="0.0.0.0", port=PORT)