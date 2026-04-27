import json
import requests

RPC = "https://rpc-asimov.genlayer.com"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Accept-Encoding": "identity",
    "Origin": "https://studio.genlayer.com",
    "Referer": "https://studio.genlayer.com/"
}

# Read contract code
with open("contracts/TruthBond.py", "r") as f:
    code = f.read()

PRIVATE_KEY = "0xYOUR_PRIVATE_KEY_HERE"  # replace this

# Build deploy payload
payload = {
    "jsonrpc": "2.0",
    "method": "gen_deployIntelligentContract",
    "params": [
        {
            "from": "0xYOUR_WALLET_ADDRESS_HERE",  # replace this
            "code": code,
            "args": [],
            "leaderOnly": False
        }
    ],
    "id": 1
}

resp = requests.post(RPC, json=payload, headers=HEADERS)
print(json.dumps(resp.json(), indent=2))
