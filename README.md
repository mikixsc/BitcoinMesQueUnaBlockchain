# BitcoinMesQueUnaBlockchain

## Introducció
Avui en dia la majoria dels diners són digitals, la funció més funamental d’un banc és mantenir i gestionar la base de dades dels comptes bancaris. Sobretot s’ha d’assegurar que una persona no pugui utilitzar diners que ja s’ha gastat. Això per ells es relativament fàcil ja que són els unics que tenen capacitat de modificar el llibre de comptabilitat.

![Sistema centralitzat](https://github.com/user-attachments/assets/11564406-6ecc-4e29-85a2-ab832fb972ca)


Aquest sistema té certs inconvenients, com la subjecció a les seves normes, la possiblitat de censura, el potencial control i és vulnerable.

A continuació mirarem de distribuir aquest llibre de comptabilitat desde cero.

## Distribuïm el llibre de comptabilitat

![Sistema distribuït](https://github.com/user-attachments/assets/bbc7c279-8a84-4d9a-b012-afb4c66cd31d)

Ara cada persona/node gestionarà el llibre de comptabilitat. Ara quan una persona vulgui gastar diners, ho comunicaran als altres, i els altres s'asseguraran que és una transacció vàlida.

### Format del llibre de comptabilitat
El llibre de comptabilitat serà un fitxer json on cada entrada sera una transacció. El format inicial d'una transacció serà aquesta:

```json
{
  "index": 1,
  "timestamp": "2025-04-14T10:00:00Z",
  "sender": "A"
  "receiver": "B"
  "amount": 10
}
```

- index: Posició de la transacció.
- timestamp: Quan s'ha creat.
- sender: Persona que envia.
- receiver: Persona que rep.
- amount: Quantitat que envia.

Per tant el llibre de comptabilitat amb 3 transaccions tindra aquest format: 

```json
[
  {
    "index": 1,
    "timestamp": "2025-04-14T10:00:00Z",
    "sender": "A",
    "receiver": "B",
    "amount": 10
  },
  {
    "index": 2,
    "timestamp": "2025-04-14T10:05:00Z",
    "sender": "B",
    "receiver": "C",
    "amount": 5
  },
  {
    "index": 3,
    "timestamp": "2025-04-14T10:10:00Z",
    "sender": "A",
    "receiver": "C",
    "amount": 3
  }
]
```

### Comunicació

La comunicació mirarem de fer-la a través de una API sobre HTTP.

#### POST /version
Un node informa que es vol connectar.
```json
{
  "node_id": "A",
  "timestamp": "2025-04-14T17:00:00Z"
  "known_height": 3
}
```
#### POST /verack
Resposta al version. Simplement acceptem la connexió

#### GET /addr
Demanar les adreces d'altres nodes

#### POST /addr
Reposta amb la llista d'adreces conegudes:
```json
{
  "nodes": ["http://localhost:5001", "http://localhost:5002"]
}
```

#### POST /inventory
Té una nova transacció

```json
{
  "indexes": [3, 4, 5]
}
```

#### POST /getdata
El node demana les dades reals corresponents a un inventory.
```json
{
  "indexes": [3, 4, 5],
  "node_address": "http://localhost:5001"
}
```

#### POST /transactions
Resposta amb la transaccins
```json
[
  {
    "index": 3,
    "timestamp": "2025-04-14T10:10:00Z",
    "sender": "A",
    "receiver": "C",
    "amount": 3
  }
]
```
