import { createClient, createAccount } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';

const PRIVATE_KEY = process.env.GL_PRIVATE_KEY;
const CONTRACT = '0x21F6D24E5b422780e6253A0F25620AC56246313A';
const url = process.argv[2];

if (!url) { console.error('Usage: node write_claim.mjs "https://article-url"'); process.exit(1); }
if (!PRIVATE_KEY) { console.error('Set GL_PRIVATE_KEY env var'); process.exit(1); }

const account = createAccount(PRIVATE_KEY);
const client = createClient({ chain: testnetBradbury, account });

console.log('Submitting claim:', url);
const txHash = await client.writeContract({
  address: CONTRACT,
  functionName: 'submit_claim',
  args: [url],
  value: BigInt(0),
});

console.log('TX Hash:', txHash);
console.log('Waiting for AI consensus...');

const receipt = await client.waitForTransactionReceipt({
  hash: txHash,
  status: 'ACCEPTED',
  retries: 24,
  interval: 5000,
});

console.log('✅ Done! Claim submitted on-chain.');
console.log('Receipt:', JSON.stringify(receipt, null, 2));
