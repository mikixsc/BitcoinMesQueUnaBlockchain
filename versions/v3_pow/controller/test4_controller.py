import time
from api_helper import send_version, create_transaction, create_malicious_transaction


time.sleep(5)  # Esperem que els nodes estiguin a punt

# Enviar un /version de A a B
send_version("A", "B", 0)

# A i B connectats

send_version("B", "C", 0)

# B i C connectats

create_transaction("A", "A", "B", 5)
create_transaction("C", "C", "A", 3)

# Pel node A: A te 5, B te 15, C te 10
# El node B la que primer li arribi, lo mes normal es que sigui: A te 5, B te 15, C te 10
# Pel node C: A te 13, B te 10, C te 7

time.sleep(2)

create_transaction("C", "C", "B", 3)
create_transaction("A", "A", "C", 5)

# Pel node A: A te 0, B te 15, C te 15
# El node B la que primer li arribi, lo mes normal es que sigui:  A te 5, B te 18, C te 7
# Pel node C: A te 13, B te 13, C te 4


# Com podem veure no ens possem d'acrod en quina es la historia correcta
# Quan tot son transaccions valides i correctes i en veritat els saldos haurien de ser aquets:
# A te 3, B te 18, C te 9