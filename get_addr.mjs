import { createClient, createAccount } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';
import { writeFileSync, readFileSync } from 'fs';

const TX = "0x98a71c67b7653bc5f56635aed2513fe47852a9d29814da1a9a38f4ea47750c77";
const client = createClient({ chain: testnetBradbury, account: createAccount(process.env.GL_KEY) });

const receipt = await client.waitForTransactionReceipt({ hash: TX, timeout: 120000 });
const addr = receipt.recipient;
console.log('NEW CONTRACT:', addr);

let env = readFileSync('./.env', 'utf8');
env = env.replace(/CONTRACT=0x[a-fA-F0-9]+/, `CONTRACT=${addr}`);
writeFileSync('./.env', env);
writeFileSync('./current_contract.txt', addr);
console.log('Saved to current_contract.txt');
