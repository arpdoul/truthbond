import { createClient, createAccount } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';

const CONTRACT = process.env.CONTRACT || '0xDbf7602636289Fd7B845968bA7CF755C3A0e647B';
const key = process.env.GL_KEY;

const client = createClient({ chain: testnetBradbury, account: createAccount(key) });

console.log('Requesting AI verdict for claim 0...');
const hash = await client.writeContract({
  address: CONTRACT,
  functionName: 'verify_claim',
  args: [0],
  value: BigInt(0),
});
console.log('TX:', hash);
console.log('Explorer:', 'https://explorer-bradbury.genlayer.com/tx/' + hash);
console.log('Wait 5-10 mins then read the verdict...');
