import { createClient, createAccount } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';

const CONTRACT = "0x80b506EA79ab7f1eBcB6582A36d850bc0968379b";
const client = createClient({ chain: testnetBradbury, account: createAccount(process.env.GL_KEY) });

console.log('Verifying claim 0...');
const hash = await client.writeContract({
  address: CONTRACT,
  functionName: 'verify_claim',
  args: ["0"],
  value: BigInt(0),
});
console.log('TX:', hash);
console.log('Explorer: https://explorer-bradbury.genlayer.com/tx/' + hash);
