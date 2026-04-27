#!/usr/bin/env python3
import requests, json, sys, os

CONTRACT = "0x46897Ff821DfD1925FecE13D35492359A5F22a50"

# All known GenLayer RPC endpoints to try
RPCS = [
    "https://rpc-asimov.genlayer.com",
    "https://rpc.testnet-chain.genlayer.com",
    "https://rpc-bradbury.genlayer.com",
]
ACTIVE_RPC = None

def try_rpc(url, method, params=[]):
    try:
        r = requests.post(
            url,
            json={"jsonrpc":"2.0","id":1,"method":method,"params":params},
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "TruthBond/1.0"
            },
            timeout=20
        )
        # Check content type before parsing
        ct = r.headers.get("Content-Type","")
        if "json" not in ct and r.text.strip().startswith("<"):
            return None, "HTML response (not JSON endpoint)"
        data = r.json()
        return data, None
    except requests.exceptions.ConnectionError:
        return None, "Connection refused"
    except requests.exceptions.Timeout:
        return None, "Timeout"
    except Exception as e:
        return None, str(e)

def find_working_rpc():
    global ACTIVE_RPC
    print("\n🔍 Finding working RPC endpoint...")
    for url in RPCS:
        print(f"   Trying {url} ...", end=" ", flush=True)
        data, err = try_rpc(url, "eth_blockNumber")
        if data and "result" in data:
            block = int(data["result"], 16)
            print(f"✅ Block #{block}")
            ACTIVE_RPC = url
            return True
        elif data and "error" in data:
            # Server responded with JSON error — endpoint works!
            print(f"⚠️  RPC error: {data['error']}")
            ACTIVE_RPC = url
            return True
        else:
            print(f"❌ {err}")
    return False

def rpc(method, params=[]):
    global ACTIVE_RPC
    if not ACTIVE_RPC:
        if not find_working_rpc():
            print("❌ No RPC available. Check internet.")
            return None
    data, err = try_rpc(ACTIVE_RPC, method, params)
    if err:
        print(f"❌ RPC error: {err}")
        return None
    return data

def test_connection():
    print("\n🔌 Testing GenLayer Testnet connection...")
    if find_working_rpc():
        print(f"\n✅ Active RPC: {ACTIVE_RPC}")
        # Also test contract
        print(f"📄 Contract:   {CONTRACT}")
        res = rpc("gen_call", [{
            "to": CONTRACT,
            "data": {"method": "get_count", "args": []}
        }])
        if res and "result" in res:
            print(f"✅ Contract live! Total claims: {res['result']}")
        else:
            print(f"⚠️  Contract check: {res}")
    else:
        print("\n❌ Cannot connect. Troubleshoot:")
        print("  1. Switch WiFi ↔ Mobile data")
        print("  2. Try a VPN app")
        print("  3. Use Studio browser instead")

def get_claim():
    cid = input("\nEnter claim ID (e.g. 0): ").strip()
    res = rpc("gen_call", [{
        "to": CONTRACT,
        "data": {"method": "get_claim", "args": [cid]}
    }])
    if not res or "result" not in res:
        print(f"❌ Failed: {res}")
        return
    try:
        c = json.loads(res["result"])
        if "error" in c:
            print(f"⚠️  {c['error']}")
            return
        v = c.get("verdict","")
        icon = {"TRUE":"✅","FALSE":"❌","UNVERIFIABLE":"⚠️"}.get(v,"🔍")
        print(f"""
{'='*42}
📰  CLAIM #{c.get('id','?')}
{'='*42}
Headline : {c.get('headline','')}
Category : {c.get('category','')}
Source   : {c.get('source_url','')}
Status   : {c.get('status','')}
Poster   : {c.get('poster','')[:14]}...
{'─'*42}""")
        if v:
            print(f"{icon} VERDICT  : {v}")
            print(f"Reason   : {c.get('reason','')}")
        else:
            print("⏳ Not yet verified")
        print('='*42)
    except Exception as e:
        print(f"Parse error: {e}\nRaw: {res['result']}")

def get_count():
    res = rpc("gen_call", [{
        "to": CONTRACT,
        "data": {"method": "get_count", "args": []}
    }])
    if res and "result" in res:
        print(f"\n📊 Total claims on chain: {res['result']}")
    else:
        print(f"❌ {res}")

def post_guide():
    print("""
┌─────────────────────────────────────┐
│  📋 HOW TO POST A CLAIM             │
├─────────────────────────────────────┤
│ 1. Open studio.genlayer.com         │
│ 2. Load contract:                   │
│    0x46897Ff821...22a50             │
│ 3. Go to WRITE tab                  │
│ 4. Select: post_claim               │
│ 5. Fill:                            │
│    headline →                       │
│      "Trump signs crypto bill 2025" │
│    source_url →                     │
│      "https://reuters.com"          │
│    category → "politics"            │
│ 6. Click Execute                    │
│ 7. Wait for green ✅ in logs        │
│ 8. Note the claim ID returned       │
└─────────────────────────────────────┘
""")

def verify_guide():
    print("""
┌─────────────────────────────────────┐
│  ⚖️  HOW TO VERIFY A CLAIM          │
├─────────────────────────────────────┤
│ 1. Open studio.genlayer.com         │
│ 2. Load your contract               │
│ 3. Go to WRITE tab                  │
│ 4. Select: verify_claim             │
│ 5. Fill:                            │
│    claim_id → "0"                   │
│ 6. Click Execute                    │
│ 7. Wait 30-60 secs for AI consensus │
│ 8. Check logs for TRUE/FALSE result │
│ 9. Come back here → option 2        │
└─────────────────────────────────────┘
""")

def explorer_link():
    print(f"""
🔍 View your contract on explorer:
https://explorer-asimov.genlayer.com/contracts/{CONTRACT}

📋 Submit this URL to portal for points:
https://portal.genlayer.foundation
""")

def menu():
    print(f"""
╔══════════════════════════════════════╗
║   ⚖️  TruthBond CLI  v2.0            ║
║   AI Fake News Bounty — GenLayer     ║
╠══════════════════════════════════════╣
║  Contract: {CONTRACT[:14]}...  ║
╠══════════════════════════════════════╣
║  1. Test Connection                  ║
║  2. View a Claim by ID               ║
║  3. Get Total Claims Count           ║
║  4. How to Post a Claim (Studio)     ║
║  5. How to Verify a Claim (Studio)   ║
║  6. View Contract on Explorer        ║
║  7. Exit                             ║
╚══════════════════════════════════════╝
Enter choice:""", end=" ")

def main():
    print("🚀 TruthBond — GenLayer Testnet Asimov")
    print(f"📄 Contract: {CONTRACT}")
    while True:
        menu()
        try:
            c = input().strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Bye!")
            break
        if   c == "1": test_connection()
        elif c == "2": get_claim()
        elif c == "3": get_count()
        elif c == "4": post_guide()
        elif c == "5": verify_guide()
        elif c == "6": explorer_link()
        elif c == "7": print("👋 Bye!"); break
        else: print("❌ Invalid. Enter 1-7")

if __name__ == "__main__":
    main()
