import { createClient, createAccount } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';
import { readFileSync, writeFileSync } from 'fs';

const key = process.env.GL_KEY;
const client = createClient({ chain: testnetBradbury, account: createAccount(key) });

console.log('Deploying fixed contract...');
const code = readFileSync('./contracts/TruthBond.py', 'utf8');

const hash = await client.deployContract({ code, args: [] });
console.log('TX:', hash);

// Wait for receipt to get contract address
console.log('Waiting for contract address...');
await new Promise(r => setTimeout(r, 15000));

const receipt = await client.getTransactionReceipt({ hash });
const addr = receipt.contractAddress;
console.log('====================');
console.log('NEW CONTRACT:', addr);
console.log('====================');

// Auto-update .env
let env = readFileSync('./.env', 'utf8');
env = env.replace(/CONTRACT=0x[a-fA-F0-9]+/, `CONTRACT=${addr}`);
writeFileSync('./.env', env);
console.log('✅ .env updated');

// Auto-update verify_claim.mjs
let vc = readFileSync('./verify_claim.mjs', 'utf8');
vc = vc.replace(/const CONTRACT = process\.env\.CONTRACT \|\| '0x[a-fA-F0-9]+'/, 
  `const CONTRACT = process.env.CONTRACT || '${addr}'`);
writeFileSync('./verify_claim.mjs', vc);
console.log('✅ verify_claim.mjs updated');

console.log(`\nExplorer: https://explorer-bradbury.genlayer.com/tx/${hash}`);
console.log('\nNow run: node verify_claim.mjs $GL_KEY');
