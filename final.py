import requests, json, hashlib
from Crypto.Hash import keccak as _keccak

CONTRACT = "0x46897Ff821DfD1925FecE13D35492359A5F22a50"
RPC = "https://rpc-asimov.genlayer.com"
CHAIN_ID = 4221
HEADERS = {
    "Content-Type":"application/json",
    "Accept":"application/json",
    "Accept-Encoding":"identity",
    "User-Agent":"Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
    "Origin":"https://studio.genlayer.com",
    "Referer":"https://studio.genlayer.com/",
}

def keccak256(data):
    h = _keccak.new(digest_bits=256)
    h.update(data)
    return h.digest()

def rpc_call(method, params=[]):
    r = requests.post(RPC,
        json={"jsonrpc":"2.0","id":1,"method":method,"params":params},
        headers=HEADERS, timeout=30)
    return r.json()

def gen_read(method, args=[]):
    return rpc_call("gen_call",[{"to":CONTRACT,"data":{"method":method,"args":args}}])

# secp256k1
P=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy=0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

def inv(a): return pow(a,P-2,P)
def add(A,B):
    if A is None: return B
    if B is None: return A
    if A[0]==B[0] and A[1]!=B[1]: return None
    l=(3*A[0]**2*inv(2*A[1]))%P if A==B else ((B[1]-A[1])*inv(B[0]-A[0]))%P
    x=(l*l-A[0]-B[0])%P
    return(x,(l*(A[0]-x)-A[1])%P)
def mul(k,pt):
    R=None;Q=pt
    while k:
        if k&1:R=add(R,Q)
        Q=add(Q,Q);k>>=1
    return R

def i2b(n,l=32): return (n).to_bytes(l,'big') if n else b'\x00'*l

def rlp_enc(items):
    def enc(x):
        if isinstance(x,bytes):
            if len(x)==0:return b'\x80'
            if len(x)==1 and x[0]<0x80:return x
            return(bytes([0x80+len(x)])+x if len(x)<56 else bytes([0xb7+len(len(x).to_bytes((len(x).bit_length()+7)//8,'big'))])+len(x).to_bytes((len(x).bit_length()+7)//8,'big')+x)
        body=b''.join(enc(i) for i in x)
        return(bytes([0xc0+len(body)])+body if len(body)<56 else bytes([0xf7+len(len(body).to_bytes((len(body).bit_length()+7)//8,'big'))])+len(body).to_bytes((len(body).bit_length()+7)//8,'big')+body)
    return enc(items)

def n2b(n):
    if n==0:return b''
    return n.to_bytes((n.bit_length()+7)//8,'big')

def sign_tx(pk_hex, to, data_bytes, nonce, gas_price, gas=800000, value=0):
    pk=int(pk_hex.replace("0x",""),16)
    pub=mul(pk,(Gx,Gy))
    addr="0x"+keccak256(i2b(pub[0])+i2b(pub[1]))[-20:].hex()

    to_b=bytes.fromhex(to[2:])
    raw=rlp_enc([n2b(nonce),n2b(gas_price),n2b(gas),to_b,n2b(value),data_bytes,n2b(CHAIN_ID),b'',b''])
    z=int.from_bytes(keccak256(raw),'big')

    # RFC6979 deterministic k
    import hmac
    pk_b=i2b(pk);z_b=i2b(z)
    V=b'\x01'*32;K=b'\x00'*32
    K=hmac.new(K,V+b'\x00'+pk_b+z_b,hashlib.sha256).digest()
    V=hmac.new(K,V,hashlib.sha256).digest()
    K=hmac.new(K,V+b'\x01'+pk_b+z_b,hashlib.sha256).digest()
    V=hmac.new(K,V,hashlib.sha256).digest()
    k_val=int.from_bytes(hmac.new(K,V,hashlib.sha256).digest(),'big')%N

    R=mul(k_val,(Gx,Gy))
    r=R[0]%N
    s=(pow(k_val,N-2,N)*(z+r*pk))%N
    if s>N//2:s=N-s
    v=35+2*CHAIN_ID+(R[1]%2)

    signed=rlp_enc([n2b(nonce),n2b(gas_price),n2b(gas),to_b,n2b(value),data_bytes,n2b(v),n2b(r),n2b(s)])
    return addr, "0x"+signed.hex()

def post_claim(pk_hex, headline, source_url, category):
    print("\n📍 Getting wallet info...")
    res=rpc_call("eth_getTransactionCount",["0x0000000000000000000000000000000000000001","latest"])
    pk=int(pk_hex.replace("0x",""),16)
    pub=mul(pk,(Gx,Gy))
    addr="0x"+keccak256(i2b(pub[0])+i2b(pub[1]))[-20:].hex()
    print(f"Wallet: {addr}")

    res=rpc_call("eth_getTransactionCount",[addr,"latest"])
    nonce=int(res.get("result","0x0"),16)
    print(f"Nonce: {nonce}")

    res2=rpc_call("eth_gasPrice")
    gp=int(res2.get("result","0x3b9aca00"),16)
    print(f"Gas: {gp}")

    data=json.dumps({"method":"post_claim","args":[headline,source_url,category]}).encode()
    addr2,raw=sign_tx(pk_hex,CONTRACT,data,nonce,gp)

    print(f"📦 Sending ({len(raw)//2} bytes)...")
    res3=rpc_call("eth_sendRawTransaction",[raw])
    return res3

def view_claims():
    for i in range(10):
        r=gen_read("get_claim",[str(i)])
        raw=r.get("result") if r else None
        if not raw or raw=="None":break
        try:
            c=json.loads(raw)
            v=c.get("verdict","")
            icon={"TRUE":"✅","FALSE":"❌","UNVERIFIABLE":"⚠️"}.get(v,"🔍")
            print(f"\n{icon} Claim #{i}")
            print(f"   {c.get('headline','')}")
            print(f"   Status: {c.get('status','')} | Verdict: {v or 'pending'}")
        except:
            print(f"Claim {i}: {raw[:80]}")

def menu():
    print("""
╔══════════════════════════════════════╗
║  ⚖️  TruthBond v4.0 — FULL MODE     ║
║  pycryptodome ✅ Signing enabled     ║
╠══════════════════════════════════════╣
║  1. Post New Claim (signs tx)        ║
║  2. View All Claims                  ║
║  3. Check Connection & Count         ║
║  4. Exit                             ║
╚══════════════════════════════════════╝
""")

print("✅ pycryptodome loaded — FULL signing mode!")
res=gen_read("get_count")
c=res.get("result") if res else "?"
print(f"📊 Claims on chain: {0 if not c or c=='None' else c}")

while True:
    menu()
    ch=input("Choice (1-4): ").strip()
    if ch=="1":
        pk=input("Private key (0x...): ").strip()
        h=input("Headline: ").strip()
        u=input("Source URL (https://...): ").strip()
        cat=input("Category (crypto/tech/politics): ").strip()
        res=post_claim(pk,h,u,cat)
        print(f"\n📨 Response: {json.dumps(res,indent=2)}")
        if res.get("result"):
            print(f"\n✅ SUCCESS! TX: {res['result']}")
            print("⏳ Wait 30-60 secs then choose 2 to verify")
    elif ch=="2":
        print("\n📋 All claims:")
        view_claims()
    elif ch=="3":
        r=rpc_call("eth_blockNumber")
        if r and "result" in r:
            print(f"✅ Block #{int(r['result'],16)}")
        r2=gen_read("get_count")
        print(f"📊 Claims: {r2.get('result','?') if r2 else '?'}")
    elif ch=="4":
        print("👋 Bye!"); break
