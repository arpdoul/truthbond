import { createClient, createAccount } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';
import { readFileSync } from 'fs';

const key = process.argv[2];
const client = createClient({ chain: testnetBradbury, account: createAccount(key) });
const code = readFileSync('./contracts/TruthBond.py', 'utf-8');

console.log('Deploying...');
const hash = await client.deployContract({ code, args: [], leaderOnly: false });
console.log('===================');
console.log('TX HASH:', hash);
console.log('===================');
console.log('Check address at:');
console.log('https://explorer-bradbury.genlayer.com/tx/' + hash);
console.log('===================');
