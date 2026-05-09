import { createClient, createAccount } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';
import { readFileSync } from 'fs';

const key = process.argv[2];
const client = createClient({ chain: testnetBradbury, account: createAccount(key) });
const code = readFileSync(process.env.HOME + '/truthbond/contracts/TruthBond.py', 'utf-8');

console.log('Deploying...');
const hash = await client.deployContract({ code, args: [], leaderOnly: false });
console.log('TX:', hash);

const r = await client.waitForTransactionReceipt({
  hash, status: 'ACCEPTED', retries: 60, interval: 8000
});
console.log('ADDRESS:', r?.recipient);
console.log('STATUS:', r?.txExecutionResultName);
