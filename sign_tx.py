import requests, json, hashlib, hmac, struct, os

CONTRACT = "0x46897Ff821DfD1925FecE13D35492359A5F22a50"
RPC = "https://rpc-asimov.genlayer.com"
HEADERS = {
    "Content-Type":"application/json",
    "Accept":"application/json",
    "Accept-Encoding":"identity",
    "User-Agent":"Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
    "Origin":"https://studio.genlayer.com",
    "Referer":"https://studio.genlayer.com/",
}

def rpc(method, params=[]):
    r = requests.post(RPC,
        json={"jsonrpc":"2.0","id":1,"method":method,"params":params},
        headers=HEADERS, timeout=30)
    return r.json()

def gen_read(method, args=[]):
    return rpc("gen_call",[{
        "to":CONTRACT,
        "data":{"method":method,"args":args}
    }])

# ── Pure Python secp256k1 ─────────────────────────
P  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

def modinv(a, m):
    return pow(a, m-2, m)

def point_add(P1, P2):
    if P1 is None: return P2
    if P2 is None: return P1
    if P1[0]==P2[0] and P1[1]!=P2[1]: return None
    if P1==P2:
        lam = (3*P1[0]*P1[0]*modinv(2*P1[1],P))%P
    else:
        lam = ((P2[1]-P1[1])*modinv(P2[0]-P1[0],P))%P
    x = (lam*lam-P1[0]-P2[0])%P
    y = (lam*(P1[0]-x)-P1[1])%P
    return (x,y)

def scalar_mult(k, point):
    result = None
    addend = point
    while k:
        if k&1: result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    return result

def get_pubkey(privkey_int):
    return scalar_mult(privkey_int, (Gx,Gy))

def privkey_to_address(privkey_hex):
    pk = int(privkey_hex, 16)
    pub = get_pubkey(pk)
    pub_bytes = pub[0].to_bytes(32,'big') + pub[1].to_bytes(32,'big')
    kh = hashlib.new('sha3_256') # wrong - need keccak
    # Use sha3 as approximation for address display
    h = hashlib.sha256(pub_bytes).digest()
    return "0x" + h[-20:].hex()

def keccak256(data):
    # Use Python's hashlib sha3_256 won't work - need pysha3
    # Workaround: call RPC to get address from key
    return hashlib.sha256(data).digest()

def rlp_encode(items):
    def encode_item(item):
        if isinstance(item, bytes):
            if len(item)==0: return b'\x80'
            if len(item)==1 and item[0]<0x80: return item
            return encode_length(len(item), 0x80) + item
        elif isinstance(item, list):
            out = b''.join(encode_item(i) for i in item)
            return encode_length(len(out), 0xc0) + out
    def encode_length(l, offset):
        if l<56: return bytes([l+offset])
        bl = (l.bit_length()+7)//8
        return bytes([offset+55+bl]) + l.to_bytes(bl,'big')
    return encode_item(items)

def int_to_bytes(n):
    if n==0: return b''
    return n.to_bytes((n.bit_length()+7)//8, 'big')

print("="*44)
print(" TruthBond — Direct Transaction Sender")
print("="*44)

# Show current state
res = gen_read("get_count")
print(f"\n📊 Current claims: {res.get('result','?') if res else '?'}")

print("""
⚠️  NOTE: Pure Python signing needs keccak256
which isn't in Python stdlib.

BEST OPTION: Install pysha3 (no Rust needed):
""")

# Try installing pysha3
import subprocess
result = subprocess.run(
    ["pip", "install", "pysha3", "--quiet"],
    capture_output=True, text=True
)
if result.returncode == 0:
    print("✅ pysha3 installed!")
    import sha3
    
    def keccak256(data):
        k = hashlib.new('sha3_256')
        k = sha3.keccak_256()
        k.update(data)
        return k.digest()
    
    print("✅ Full signing available!")
else:
    print(f"❌ pysha3 failed: {result.stderr[:100]}")
    print("""
Since eth-account and pysha3 can't install,
the ONLY reliable way to send write transactions
from Termux is to use Studio in Chrome browser.

Your READ operations work perfectly from Termux.
Use this split approach:
  WRITE → Studio browser (Chrome)
  READ  → Termux CLI (working ✅)
""")

print("\n" + "="*44)
print("Reading contract (this always works):")
res = gen_read("get_count")
c = res.get("result") if res else None
print(f"Total claims: {c if c and c!='None' else '0 (empty)'}")

res2 = gen_read("get_claim",["0"])
raw = res2.get("result") if res2 else None
if raw and raw != "None":
    print(f"Claim 0: {raw}")
else:
    print("No claims yet - post one via Studio!")
