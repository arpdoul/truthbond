import { createClient, createAccount } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';
import { readFileSync } from 'fs';
import { TransactionStatus } from 'genlayer-js/types';

const PRIVATE_KEY = '0x1828b0d235188dfafee745939881681767ef4933cedd6eb19dec9e567674af0f';

const account = createAccount(PRIVATE_KEY);

const client = createClient({
  chain: testnetBradbury,
  account: account,
});

const contractCode = readFileSync('./contracts/TruthBond.py', 'utf-8');

console.log('Deploying TruthBond to Testnet Bradbury...');
console.log('Chain:', testnetBradbury.name);
console.log('RPC:', testnetBradbury.rpcUrls?.default?.http?.[0]);

try {
  const txHash = await client.deployContract({
    code: contractCode,
    args: [],
    leaderOnly: false,
  });

  console.log('TX Hash:', txHash);
  console.log('Waiting for confirmation (this takes 3-8 mins)...');

  const receipt = await client.waitForTransactionReceipt({
    hash: txHash,
    status: TransactionStatus.ACCEPTED,
    retries: 120,
    interval: 10000,
  });

  console.log('\n✅ TruthBond DEPLOYED!');
  console.log('Contract Address:', receipt.data?.contract_address);
  console.log('\nSave this address NOW!\n');

} catch (err) {
  console.error('Error:', err.message);
  if (err.message.includes('status')) {
    console.log('\nTX was sent but timed out. Check explorer:');
    console.log('https://explorer.genlayer.com');
  }
}
