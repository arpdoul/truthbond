import { createClient, createAccount } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';

const CONTRACT = "0x80b506EA79ab7f1eBcB6582A36d850bc0968379b";
const client = createClient({ chain: testnetBradbury, account: createAccount(process.env.GL_KEY) });

console.log('Posting claim...');
const h1 = await client.writeContract({
  address: CONTRACT,
  functionName: 'post_claim',
  args: ['https://www.theonion.com/nation-s-rich-increasingly-outsourcing-their-own-deaths-1850937933'],
  value: BigInt(0),
});
console.log('Post TX:', h1);
console.log('Waiting 90s...');
await new Promise(r => setTimeout(r, 90000));

console.log('Verifying...');
const h2 = await client.writeContract({
  address: CONTRACT,
  functionName: 'verify_claim',
  args: ['0'],
  value: BigInt(0),
});
console.log('Verify TX:', h2);
console.log('Explorer: https://explorer-bradbury.genlayer.com/tx/' + h2);
