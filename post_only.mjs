import { createClient, createAccount } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';

const CONTRACT = "0x80b506EA79ab7f1eBcB6582A36d850bc0968379b";
const client = createClient({ 
  chain: testnetBradbury, 
  account: createAccount(process.env.GL_KEY) 
});

// Read first to confirm contract exists
console.log('Reading contract...');
const count = await client.readContract({
  address: CONTRACT,
  functionName: 'get_count',
  args: [],
});
console.log('Claim count:', count);
