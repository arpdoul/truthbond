#!/data/data/com.termux/files/usr/bin/bash
source ~/truthbond/.env

ESCAPED=$(python3 -c "
import json
code = open('$HOME/truthbond/contracts/TruthBond.py').read()
print(json.dumps(code))
")

echo "Deploying TruthBond to Asimov..."

curl -s https://rpc-asimov.genlayer.com \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0" \
  -H "Accept-Encoding: identity" \
  -H "Origin: https://studio.genlayer.com" \
  -H "Referer: https://studio.genlayer.com/" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"gen_deployIntelligentContract\",
    \"params\": [{
      \"from\": \"$WALLET\",
      \"code\": $ESCAPED,
      \"args\": [],
      \"leaderOnly\": false
    }],
    \"id\": 1
  }" | python3 -m json.tool

