TARGET_BLOCK_TIME = 60 # segons
DIFFICULTY_ADJUSTMENT_INTERVAL = 10 # blocs

import logging
from utils import hash_block

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
)
logger = logging.getLogger(__name__)

INITIAL_TARGET = 0x000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff  # nivell inicial


current_target = INITIAL_TARGET

def get_current_target():
    return current_target

def target_to_hex(target):
    return hex(target)[2:].zfill(64)

def should_adjust_difficulty(blockchain):
    return len(blockchain) % DIFFICULTY_ADJUSTMENT_INTERVAL == 0

def adjust_difficulty(blockchain):
    global current_target

    if len(blockchain) < DIFFICULTY_ADJUSTMENT_INTERVAL + 1:
        return

    start_block = blockchain[-DIFFICULTY_ADJUSTMENT_INTERVAL - 1]
    end_block = blockchain[-1]

    start_time = parse_iso8601(start_block["timestamp"])
    end_time = parse_iso8601(end_block["timestamp"])

    actual_time = end_time - start_time
    expected_time = TARGET_BLOCK_TIME * DIFFICULTY_ADJUSTMENT_INTERVAL
    
    ratio = actual_time / expected_time
    ratio = max(0.25, min(4.0, ratio))

    new_target = int(current_target * ratio)
    current_target = new_target
    logger.info(f"Nova dificultat ajustada: {new_target}")

def parse_iso8601(timestamp):
    from datetime import datetime
    return int(datetime.fromisoformat(timestamp.replace("Z", "")).timestamp())