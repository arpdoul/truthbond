import requests, json, time

CONTRACT = "0x46897Ff821DfD1925FecE13D35492359A5F22a50"
RPC = "https://rpc-asimov.genlayer.com"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Accept-Encoding": "identity",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
    "Origin": "https://studio.genlayer.com",
    "Referer": "https://studio.genlayer.com/",
}

def call(method, params=[]):
    r = requests.post(RPC,
        json={"jsonrpc":"2.0","id":1,"method":method,"params":params},
        headers=HEADERS, timeout=30)
    try:
        return r.json()
    except:
        return {"raw": r.text[:300]}

def gen_read(method, args=[]):
    return call("gen_call",[{
        "to": CONTRACT,
        "data": {"method": method, "args": args}
    }])

def gen_write(method, args=[], private_key=None):
    # For write methods we need to send via eth_sendRawTransaction
    # But first let's try gen_call in write mode
    return call("gen_call",[{
        "to": CONTRACT,
        "data": {"method": method, "args": args},
        "from": "0x0000000000000000000000000000000000000001"
    }])

print("="*44)
print(" TruthBond — Post & Read Claims")
print("="*44)

# Check current count
res = gen_read("get_count")
count = res.get("result", "0") if res else "0"
print(f"\n📊 Current claims: {count}")

print("""
To post a claim you need your private key.
This signs the transaction on-chain.

Your private key is the one from your
GenLayer Studio wallet (the wallet showing
0x05...ea51 in Studio top bar).

""")

pk = input("Paste your private key (0x...): ").strip()
if not pk:
    print("No key entered. Showing read-only mode.")
else:
    print("\n📝 Enter claim details:")
    headline = input("Headline: ").strip()
    url = input("Source URL (https://...): ").strip()
    category = input("Category (crypto/politics/tech): ").strip()

    print(f"\n⏳ Posting claim to GenLayer testnet...")
    print(f"   Headline: {headline}")
    print(f"   URL: {url}")
    print(f"   Category: {category}")

    # Build the write transaction
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_sendRawTransaction",
        "params": [{
            "to": CONTRACT,
            "data": json.dumps({
                "method": "post_claim",
                "args": [headline, url, category]
            }),
            "privateKey": pk
        }]
    }

    res = call("eth_sendRawTransaction", body["params"])
    print(f"\nResponse: {json.dumps(res, indent=2)}")

print("\n" + "="*44)
print("Reading contract state...")
res = gen_read("get_count")
print(f"Total claims: {res.get('result','?') if res else '?'}")
