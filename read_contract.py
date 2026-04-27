import requests, json, sys

CONTRACT = "0x46897Ff821DfD1925FecE13D35492359A5F22a50"
RPC = "https://rpc-asimov.genlayer.com"

# Mimic a real browser to bypass Cloudflare
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Origin": "https://studio.genlayer.com",
    "Referer": "https://studio.genlayer.com/",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "identity",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
}

def call(method, params=[]):
    try:
        r = requests.post(
            RPC,
            json={"jsonrpc":"2.0","id":1,
                  "method":method,"params":params},
            headers=HEADERS,
            timeout=30
        )
        text = r.text.strip()
        print(f"HTTP {r.status_code} | {len(text)} bytes")
        if text and text[0] in ('{','['):
            return json.loads(text)
        else:
            print(f"Non-JSON: {text[:150]}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def gen_call(method, args=[]):
    return call("gen_call", [{
        "to": CONTRACT,
        "data": {"method": method, "args": args}
    }])

print("="*45)
print("TruthBond Contract Reader")
print(f"Contract: {CONTRACT[:20]}...")
print("="*45)

# Test 1: block number
print("\n[1] Testing eth_blockNumber...")
res = call("eth_blockNumber")
if res and "result" in res:
    print(f"✅ Block: #{int(res['result'],16)}")
else:
    print(f"❌ {res}")

# Test 2: claim count
print("\n[2] Getting claim count...")
res = gen_call("get_count")
if res and "result" in res:
    print(f"✅ Claims: {res['result']}")
else:
    print(f"❌ {res}")

# Test 3: claim 0
print("\n[3] Getting claim #0...")
res = gen_call("get_claim", ["0"])
if res and "result" in res:
    try:
        c = json.loads(res["result"])
        print(f"✅ Claim: {json.dumps(c, indent=2)}")
    except:
        print(f"✅ Raw: {res['result']}")
else:
    print(f"❌ {res}")
