import { createClient, createAccount } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';
import { writeFileSync, readFileSync } from 'fs';

const TX = "0x8c6258c2f75d5d4b186307bd8c86f2157bae1cafb01f7bf12208e0a956193ec1";
const key = process.env.GL_KEY;
const client = createClient({ chain: testnetBradbury, account: createAccount(key) });

console.log('Fetching receipt...');
const receipt = await client.waitForTransactionReceipt({ hash: TX, timeout: 120000 });

// BigInt-safe print
const addr = receipt.contractAddress || receipt.contract_address;
console.log('contractAddress:', addr);
console.log('All keys:', Object.keys(receipt));

if (addr) {
  let env = readFileSync('./.env', 'utf8');
  env = env.replace(/CONTRACT=0x[a-fA-F0-9]+/, `CONTRACT=${addr}`);
  writeFileSync('./.env', env);

  let vc = readFileSync('./verify_claim.mjs', 'utf8');
  vc = vc.replace(/0x[a-fA-F0-9]{40}/, addr);
  writeFileSync('./verify_claim.mjs', vc);

  console.log('✅ NEW CONTRACT:', addr);
  console.log('✅ Files updated! Run: node verify_claim.mjs $GL_KEY');
} else {
  // Print each key safely
  for (const [k, v] of Object.entries(receipt)) {
    try { console.log(k, ':', String(v)); } catch(e) {}
  }
}
