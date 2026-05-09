import { createClient, createAccount } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';

const CONTRACT = "0x01f1A46B9D58Fd0Be7A17Ab695069a985c1b1Bc5";
const key = process.env.GL_KEY;
const client = createClient({ chain: testnetBradbury, account: createAccount(key) });

// Step 1: Post claim
console.log('Posting claim...');
const postHash = await client.writeContract({
  address: CONTRACT,
  functionName: 'post_claim',
  args: ["https://www.theonion.com/nation-s-rich-increasingly-outsourcing-their-own-deaths-1850937933"],
  value: BigInt(0),
});
console.log('Post TX:', postHash);
await new Promise(r => setTimeout(r, 30000));

// Step 2: Verify claim 0
console.log('Verifying claim 0...');
const verifyHash = await client.writeContract({
  address: CONTRACT,
  functionName: 'verify_claim',
  args: ["0"],
  value: BigInt(0),
});
console.log('Verify TX:', verifyHash);
console.log('Explorer:', 'https://explorer-bradbury.genlayer.com/tx/' + verifyHash);
console.log('Wait 5-10 mins then read contract state');
