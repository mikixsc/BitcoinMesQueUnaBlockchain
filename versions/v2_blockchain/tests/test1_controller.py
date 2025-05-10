import time
from api_helper import send_version, create_transaction


time.sleep(5)  # Esperem que els nodes estiguin a punt

# Enviar un /version de A a B
send_version("A", "B", 0)

# A i B connectats

send_version("A", "C", 0)

# A i C connectats

send_version("B", "C", 0)

# B i C connectats